# Skill: Upstream CI Database Queries

## Purpose

Reference for querying CI databases that store **upstream test results** (Stateless and Integration tests).
This is separate from the regression test database (`clickhouse_regression_results`).

---

## Database Access

### Altinity CI Database

- **Host:** `github-checks.internal.tenant-a.staging.altinity.cloud`
- **Database/Table:** `` `gh-data`.checks ``
- **User:** `robot`
- **Password:** Must be provided by user
- **Web UI:** `https://github-checks.internal.tenant-a.staging.altinity.cloud:8443/play`

**Connection method: HTTP API (port 8443)** — verified working:
```bash
curl -s "https://github-checks.internal.tenant-a.staging.altinity.cloud:8443/?user=robot&password=<PASSWORD>" \
  --data-binary "SELECT * FROM \`gh-data\`.checks LIMIT 1 FORMAT Vertical"
```

**Note:** Native protocol (`clickhouse-client`) does NOT work on this host (SSL error on both ports 9440 and 8443). Always use `curl` with the HTTP API.

### Upstream ClickHouse CI Database

- **Host:** `play.clickhouse.com`
- **Database/Table:** `default.checks`
- **Web UI:** `https://play.clickhouse.com/play`

**Connection method 1: Native protocol (preferred)** — faster for large queries:
```bash
clickhouse-client --host play.clickhouse.com --port 9440 --secure \
  --user explorer --password '' \
  --query "SELECT * FROM default.checks LIMIT 1 FORMAT Vertical"
```

**Connection method 2: HTTP API** — works from any environment:
```bash
curl -s "https://play.clickhouse.com/?user=play&query=SELECT+1"
```

Both `explorer` (native) and `play` (HTTP) users work with no password.

---

## Schema: `checks` Table

| Column | Type | Description |
|--------|------|-------------|
| `pull_request_number` | UInt32 | PR number (0 for non-PR runs) |
| `commit_sha` | String | Commit hash |
| `check_name` | String | CI job name |
| `check_status` | String | Job status: `success`, `failure`, `error` |
| `check_start_time` | DateTime | When the check started |
| `test_name` | String | Full test name |
| `test_status` | String | `OK`, `FAIL`, `SKIPPED` |
| `test_duration_ms` | UInt64 | Test duration |
| `base_ref` | String | Base branch (e.g., `25.8`, `master`) |
| `head_ref` | String | Head branch/ref |
| `report_url` | String | Link to test report |
| `task_url` | String | Link to CI job |

---

## Test Type Identification

| Test Type | Check Name Pattern | Test Name Pattern | Log Files |
|-----------|-------------------|-------------------|-----------|
| **Integration** | `Integration tests (amd_*, N/M)` | `test_*/test.py::test_*` | `integration_run_parallel_N.log` |
| **Stateless** | `Stateless tests (arm_*, ...)` | `NNNNN_test_name` (5-digit prefix) | `job.log` |
| **AST fuzzer** | `AST fuzzer (amd_*)` | Error message as test_name | `fatal.log`, `stderr.log`, `job.log` |
| **Stress test** | `Stress test (amd_*)` | Meta-status (e.g., `Server died`) | `run.log`, `application_errors.txt`, `clickhouse-server.err.log` |
| **BuzzHouse** | `BuzzHouse (amd_*)` | Error message as test_name | `fatal.log`, `stderr.log` |
| **Stateful** | `Stateful tests (amd_*)` | Test name | `job.log` |

### Fuzzer/Stress Test Notes

- **AST fuzzer** randomly mutates SQL queries to find server crashes. The `test_name` in the database contains the error message, not a test file name. The `fatal.log` contains the crashing query and stack trace. The `Changed settings` line at the end of `fatal.log` lists all non-default settings needed to reproduce.
- **Stress tests** run the server under load for extended periods. If the server crashes, check `clickhouse-server.err.log` for the root cause. `application_errors.txt` lists all exceptions during the run.
- **BuzzHouse** is similar to AST fuzzer but generates more complex query sequences. Same log structure as AST fuzzer.

---

## Build Type Identification

| Pattern in `check_name` | Build Type |
|-------------------------|------------|
| `amd_debug` | Debug build (assertions enabled) |
| `amd_binary`, `arm_binary` | Release build (no assertions) |
| `tsan`, `asan`, `msan`, `ubsan` | Sanitizer build |
| `ParallelReplicas` | Parallel replicas mode |
| `AsyncInsert` | Async insert mode |
| `s3 storage` | S3 storage backend |

---

## Common Query Templates

### Get All Failures for a PR

```sql
SELECT check_name, test_name, test_status, check_start_time
FROM `gh-data`.checks
WHERE pull_request_number = <PR_NUMBER>
  AND test_status = 'FAIL'
ORDER BY check_name, check_start_time
```

### Test History (30 days)

```sql
SELECT 
    test_status,
    count() as cnt,
    max(check_start_time) as last_seen,
    min(check_start_time) as first_seen
FROM `gh-data`.checks
WHERE test_name LIKE '%<TEST_NAME>%'
  AND check_start_time > now() - INTERVAL 30 DAY
GROUP BY test_status
ORDER BY cnt DESC
```

### Check if Test is Pre-existing Flaky

```sql
SELECT test_name, pull_request_number, check_start_time, check_name
FROM `gh-data`.checks
WHERE test_name = '<TEST_NAME>'
  AND test_status = 'FAIL'
ORDER BY check_start_time DESC
LIMIT 20
```

If failures span multiple PRs over weeks/months → pre-existing flaky test.

### Failure Rate by Build Type

```sql
SELECT 
    check_name,
    sum(test_status = 'OK') as passes,
    sum(test_status = 'FAIL') as fails,
    round(100.0 * sum(test_status = 'FAIL') / count(), 2) as fail_rate
FROM `gh-data`.checks
WHERE test_name LIKE '%<TEST_NAME>%'
  AND check_start_time > now() - INTERVAL 30 DAY
GROUP BY check_name
HAVING fails > 0
ORDER BY fail_rate DESC
```

### Debug vs Release Comparison

```sql
SELECT 
    CASE 
        WHEN check_name LIKE '%debug%' THEN 'debug'
        ELSE 'release'
    END as build_type,
    test_status,
    count() as cnt
FROM `gh-data`.checks
WHERE test_name LIKE '%<TEST_NAME>%'
  AND check_start_time > now() - INTERVAL 30 DAY
GROUP BY build_type, test_status
ORDER BY build_type, test_status
```

### Sanitizer vs Non-Sanitizer

```sql
SELECT 
    CASE 
        WHEN check_name LIKE '%tsan%' OR check_name LIKE '%asan%' 
             OR check_name LIKE '%msan%' OR check_name LIKE '%ubsan%'
        THEN 'sanitizer' 
        ELSE 'non-sanitizer' 
    END as build_type,
    test_status,
    count() as cnt
FROM `gh-data`.checks
WHERE test_name LIKE '%<TEST_NAME>%'
  AND check_start_time > now() - INTERVAL 30 DAY
GROUP BY build_type, test_status
ORDER BY build_type, test_status
```

### Version-Specific Analysis

```sql
SELECT 
    multiIf(
        base_ref LIKE '%25.8%' OR head_ref LIKE '%25.8%', '25.8',
        base_ref LIKE '%25.3%' OR head_ref LIKE '%25.3%', '25.3',
        base_ref LIKE '%24.8%' OR head_ref LIKE '%24.8%', '24.8',
        'other'
    ) as version,
    test_status,
    count() as cnt
FROM `gh-data`.checks
WHERE test_name LIKE '%<TEST_NAME>%'
  AND check_start_time > now() - INTERVAL 90 DAY
GROUP BY version, test_status
ORDER BY version DESC, test_status
```

### Check Job Status Discrepancy

Compare database status with GitHub API:

```bash
gh api repos/Altinity/ClickHouse/actions/runs/<RUN_ID>/jobs \
  --jq '.jobs[] | {name: .name, conclusion: .conclusion}'
```

### Multiple Runs for Same Job (Reruns)

```sql
SELECT check_name, check_status, check_start_time, count() as tests
FROM `gh-data`.checks
WHERE pull_request_number = <PR_NUMBER>
  AND check_name LIKE '%<JOB_PATTERN>%'
GROUP BY check_name, check_status, check_start_time
ORDER BY check_start_time DESC
```

---

## Log URLs

There are two URL patterns depending on whether the CI run is for a **PR** or a **branch/REF** (e.g., `antalya-25.8`, `v25.8.16.20001.altinityantalya`).

### PR-based Runs

**JSON log browser:**
```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?PR=<PR>&sha=<SHA>&name_0=PR&name_1=<URL_ENCODED_JOB_NAME>
```

**Direct log file:**
```
https://altinity-build-artifacts.s3.amazonaws.com/PRs/<PR>/<SHA>/<job_artifact_dir>/<log_file>
```

**CI report:**
```
https://s3.amazonaws.com/altinity-build-artifacts/PRs/<PR>/<SHA>/<RUN_ID>/ci_run_report.html
```

### Branch/REF-based Runs

**JSON log browser** — note `name_0=MasterCI` instead of `name_0=PR`:
```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=<BRANCH>&sha=<SHA>&name_0=MasterCI&name_1=<URL_ENCODED_JOB_NAME>
```

**Direct log file:**
```
https://altinity-build-artifacts.s3.amazonaws.com/REFs/<BRANCH>/<SHA>//<job_artifact_dir>/<log_file>
```

**CI report:**
```
https://s3.amazonaws.com/altinity-build-artifacts/REFs/<BRANCH>/<SHA>/<RUN_ID>/ci_run_report.html
```

### Job Artifact Directory Naming

The `<job_artifact_dir>` in direct log URLs follows this pattern:

| Job Type | Directory Pattern | Example |
|----------|------------------|---------|
| Integration tests | `integration_tests_<build>_<N>_<M>` | `integration_tests_amd_binary_1_5` |
| Stateless tests | `stateless_tests_<build>_<modes>_parallel` | `stateless_tests_amd_binary_old_analyzer_s3_storage_databasereplicated_parallel` |
| AST fuzzer | `ast_fuzzer_<build>` | `ast_fuzzer_amd_msan` |
| Stress test | `stress_test_<build>` | `stress_test_amd_tsan` |

### S3 Artifact Listing

**PR artifacts:**
```bash
curl -s "https://altinity-build-artifacts.s3.amazonaws.com/?list-type=2&prefix=PRs/<PR>/<SHA>/&delimiter=/" \
  | grep -oE '<Prefix>[^<]+</Prefix>' | sed 's/<[^>]*>//g'
```

**REF artifacts:**
```bash
curl -s "https://altinity-build-artifacts.s3.amazonaws.com/?list-type=2&prefix=REFs/<BRANCH>/<SHA>/&delimiter=/" \
  | grep -oE '<Prefix>[^<]+</Prefix>' | sed 's/<[^>]*>//g'
```

---

## Cross-Referencing Altinity CI vs Upstream CI

When a failure involves upstream ClickHouse code (not Altinity-specific features), check whether the same error exists upstream to determine origin.

### When to Cross-Reference

- The failing test is an upstream test (Stateless, Integration, AST fuzzer, Stress)
- The error message is a `LOGICAL_ERROR` or server crash
- The failure doesn't involve Altinity-specific features (Hybrid engine, etc.)

### Step 1: Find the Error Signature

Extract a unique error string from the Altinity failure, e.g.:
- `std::out_of_range, e.what() = vector`
- `Logical error: 'Unexpected size of tuple element'`
- A specific assertion message

### Step 2: Query Upstream CI

```bash
clickhouse-client --host play.clickhouse.com --port 9440 --secure \
  --user explorer --password '' --query "
SELECT
    check_name,
    check_start_time,
    pull_request_number,
    test_name
FROM default.checks
WHERE check_name LIKE '%<JOB_TYPE>%'
    AND test_status = 'FAIL'
    AND test_name LIKE '%<ERROR_SIGNATURE>%'
ORDER BY check_start_time ASC
LIMIT 30
"
```

### Step 3: Interpret Results

| Finding | Conclusion |
|---------|------------|
| Same error exists upstream before our branch point | **Pre-existing upstream bug**, not caused by backport |
| Same error only appears after a specific upstream PR | Upstream regression, check if that PR was backported |
| Error does not exist upstream at all | **Altinity-specific issue**, likely from our patches |
| Error appears upstream only recently | May be a new upstream regression reaching our branch |

### Step 4: Monthly Distribution

To see the trend over time:

```bash
clickhouse-client --host play.clickhouse.com --port 9440 --secure \
  --user explorer --password '' --query "
SELECT
    toStartOfMonth(check_start_time) as month,
    count() as hits,
    groupUniqArray(pull_request_number) as prs
FROM default.checks
WHERE check_name LIKE '%<JOB_TYPE>%'
    AND test_status = 'FAIL'
    AND test_name LIKE '%<ERROR_SIGNATURE>%'
GROUP BY month
ORDER BY month
"
```

---

## Notes

- Always use `test_status = 'FAIL'` to filter actual failures
- `check_status` is job-level, `test_status` is individual test level
- PR number 0 indicates master/main branch runs
- Sanitizer builds often expose race conditions missed by regular builds
- Debug builds have assertions that cause crashes on errors release builds ignore
- For AST fuzzer failures, the `test_name` column contains the full error message (not a test file name)

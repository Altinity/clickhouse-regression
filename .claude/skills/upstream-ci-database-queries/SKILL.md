---
name: upstream-ci-database-queries
description: Query reference for the CI databases - connection details, schema, ready-made queries, log and artifact URL patterns, and how to cross-reference Altinity CI against upstream CI. A lookup table for other skills: it returns data, it does not classify failures.
---

# Skill: Upstream CI Database Queries

## Purpose

Reference for querying CI databases that store **upstream test results** (Stateless and Integration tests).
This is separate from the regression test database (`clickhouse_regression_results`).

---

## This skill does not classify failures

It returns **data**. Deciding whether a failure is a `regression`,
`pre-existing-flaky`, `infrastructure`, `cascade`, or `unknown` belongs to
`pr-ci-failure-triage`, `upstream-test-investigation`, and
`regression-test-database-investigation`, using the shared definitions in
`.claude/skills/_shared/failure-categories.md`.

Keeping verdicts out of this file is deliberate: judgment rules change, and a rule
duplicated here would silently contradict the skills that own it.

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

- **AST fuzzer** randomly mutates SQL queries from existing tests to find server crashes. The `test_name` in the database contains the error message, not a test file name. The `fatal.log` contains the crashing query and stack trace. The `Changed settings` line at the end of `fatal.log` lists all non-default settings needed to reproduce.
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

### Bisect a Regression Using Branch Runs

Branch runs (nightly, release, `antalya-*`) are stored with
**`pull_request_number = 0`**. Filtering on that removes all PR noise and turns the
history into a timeline you can bisect — the fastest way to date a regression when
no PR is implicated.

```sql
SELECT check_start_time, commit_sha, check_status, test_status
FROM `gh-data`.checks
WHERE test_name = '<TEST_NAME>'
  AND check_name = '<EXACT_JOB_NAME>'   -- pin the build type, or you mix them
  AND pull_request_number = 0           -- branch runs only
  AND check_start_time > now() - INTERVAL 60 DAY
ORDER BY check_start_time
```

Take the last-good and first-bad `commit_sha`, then list the window locally:

```bash
cd <clickhouse-clone> && git log --oneline <LAST_GOOD>..<FIRST_BAD>
```

> **Needs the ClickHouse source.** If you do not already know where a clone is,
> **ask the user** - do not guess a path and do not clone it yourself. Check the
> remotes before reading: `origin` is often the Altinity fork, whose `master` is
> frozen because work happens on release branches, while `upstream` is
> `ClickHouse/ClickHouse`. Read `upstream/master` for "what does upstream have
> today"; a `git log origin/master` that comes back ancient means the wrong remote,
> not a stale clone. Without a clone, the same questions can be answered from the
> API at one request each.


A real regression shows a **sharp** pass-then-fail boundary. A scattered mix of
pass and fail is flakiness, not a regression — do not bisect it.

---

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

### Failure Rate, Branch Baseline vs a PR

The comparison the classification skills need: how often a test fails **with** a
change against how often it fails **without** one. Return both sides, not a list of
failures - a raw list of failures cannot show a rate.

```sql
SELECT
    pull_request_number = <THIS_PR> AS on_this_pr,
    count()                          AS runs,
    countIf(test_status = 'FAIL')    AS fails,
    round(100.0 * fails / runs, 1)   AS fail_pct
FROM `gh-data`.checks
WHERE test_name = '<TEST_NAME>'
  AND check_name = '<EXACT_JOB_NAME>'          -- same build type on both sides
  AND (pull_request_number = 0 OR pull_request_number = <THIS_PR>)
  AND check_start_time > now() - INTERVAL 60 DAY
GROUP BY on_this_pr
```

To see which other PRs it fails in:

```sql
SELECT pull_request_number, count() AS fails, max(check_start_time) AS last_seen
FROM `gh-data`.checks
WHERE test_name = '<TEST_NAME>' AND test_status = 'FAIL'
  AND check_start_time > now() - INTERVAL 60 DAY
GROUP BY pull_request_number ORDER BY last_seen DESC
```

A long failure history does **not** by itself settle the verdict - the reading of
these numbers is defined in the classification skills, not here.

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

All CI report, log and artifact URL patterns live in one place:
**read `.claude/skills/_shared/ci-urls.md`**.

It covers the PR-vs-REF fork (path segment, `name_0`, and `job.log` vs `job.log.zst`),
the CI report and JSON-browser URLs, direct artifact paths and job directory naming,
S3 listing, range reads for large logs, and the rerun-overwrites-artifacts gotcha.

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

### Step 3: What the Result Tells You

This answers **where the defect comes from** - a different question from which of
the five categories it gets. Feed it into the classification, do not use it instead:

| Finding | What it establishes |
|---------|---------------------|
| Same error exists upstream before our branch point | The defect predates our branch - a backport did not introduce it |
| Same error appears upstream only after a specific upstream PR | An upstream regression; check whether that PR reached our branch |
| Error appears upstream only recently | A new upstream regression may be arriving in our branch |
| Error does not appear upstream at all | Only that **upstream CI has no record of it** - see below |

The last row is the one that gets over-read. No upstream record is consistent with
an Altinity-specific defect, but equally with upstream never running that
configuration, that sanitizer, or that test at all. Confirm upstream actually runs
the job before concluding the defect is ours:

```sql
SELECT check_name, count() AS runs, max(check_start_time) AS last_seen
FROM default.checks
WHERE test_name = '<TEST_NAME>' AND check_start_time > now() - INTERVAL 90 DAY
GROUP BY check_name ORDER BY runs DESC
```

No rows means upstream does not run it, and the absence of failures there proves
nothing.

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

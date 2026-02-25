# Skill: Upstream CI Database Queries

## Purpose

Reference for querying CI databases that store **upstream test results** (Stateless and Integration tests).
This is separate from the regression test database (`clickhouse_regression_results`).

---

## Database Access

### Altinity CI Database

- **URL:** `https://github-checks.internal.tenant-a.staging.altinity.cloud:8443`
- **Database/Table:** `` `gh-data`.checks ``
- **User:** `robot`
- **Password:** Must be provided by user
- **Web UI:** `https://github-checks.internal.tenant-a.staging.altinity.cloud:8443/play`

```bash
curl -s "https://github-checks.internal.tenant-a.staging.altinity.cloud:8443/?user=robot&password=<PASSWORD>" \
  --data-binary "SELECT * FROM \`gh-data\`.checks LIMIT 1 FORMAT Vertical"
```

### Upstream ClickHouse CI Database

- **URL:** `https://play.clickhouse.com`
- **Database/Table:** `default.checks`
- **User:** `play` (no password)
- **Web UI:** `https://play.clickhouse.com/play`

**Note:** Use WebFetch tool for upstream queries. URL encode the query:
```
https://play.clickhouse.com/?user=play&query=<URL_ENCODED_QUERY>
```

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

| Test Type | Check Name Pattern | Test Name Pattern |
|-----------|-------------------|-------------------|
| **Integration** | `Integration tests (amd_*, ...)` | `test_*/test.py::test_*` |
| **Stateless** | `Stateless tests (arm_*, ...)` | `NNNNN_test_name` (5-digit prefix) |

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

### Integration Test Logs

```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?PR=<PR>&sha=<SHA>&name_0=PR&name_1=Integration%20tests%20%28<build_type>%29
```

### Stateless Test Logs

```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?PR=<PR>&sha=<SHA>&name_0=PR&name_1=Stateless+tests+%28<build_type>%29&name_2=Tests
```

### S3 Artifact Listing

```bash
curl -s "https://altinity-build-artifacts.s3.amazonaws.com/?list-type=2&prefix=PRs/<PR>/<SHA>/&delimiter=/" \
  | grep -oE '<Prefix>[^<]+</Prefix>' | sed 's/<[^>]*>//g'
```

---

## Notes

- Always use `test_status = 'FAIL'` to filter actual failures
- `check_status` is job-level, `test_status` is individual test level
- PR number 0 indicates master/main branch runs
- Sanitizer builds often expose race conditions missed by regular builds
- Debug builds have assertions that cause crashes on errors release builds ignore

---
name: regression-test-database-investigation
description: Investigate one Altinity regression-suite (TestFlows) failure - "investigate this test", "why is this scenario failing". Handles scenario paths starting with a slash (`/swarms/...`, `/lightweight delete/...`, `/ldap/authentication`) - anything recorded in `gh-data.clickhouse_regression_results`. Uses the CI database to classify it as a regression, pre-existing flaky, infrastructure, cascade, or unknown.
---

# Skill: Database Failure Investigation (MVP)

## Purpose
Use the internal CI database to quickly determine whether a test failure is:
- Flaky
- A likely regression
- A new / unknown failure

This skill is intentionally limited to **database analysis only**.
It does not analyze logs or run tests.

---

## Database Access

- **Host:** `github-checks.internal.tenant-a.staging.altinity.cloud`
- **Database:** `gh-data`
- **Table:** `clickhouse_regression_results`
- **Full path:** `` `gh-data`.clickhouse_regression_results ``

- **Authentication:**
  - User: `robot`
  - Password: must be provided by the user when requested

The agent must not assume credentials.
If the password is not provided, explicitly ask for it before proceeding.

> **This database has no error-text column.** Unlike the upstream
> `default.checks` on play.clickhouse.com, `gh-data` tables expose **no
> `test_context_raw`** and **no runner / `instance_type`** column. You cannot search
> for an error signature or correlate with hardware from SQL here — the failure text
> has to come from the job artifact. Do not assume the two schemas match.

### Connection Example

**Connection method: HTTP API (port 8443)** — verified working:

```bash
curl -s "https://github-checks.internal.tenant-a.staging.altinity.cloud:8443/?user=robot&password=<PASSWORD>" \
  --data-binary "SELECT * FROM \`gh-data\`.clickhouse_regression_results LIMIT 1 FORMAT Vertical"
```

**Note:** Native protocol (`clickhouse-client`) does NOT work on this host (SSL error). Always use `curl` with the HTTP API on port 8443.

For interactive exploration, use the web UI at:
`https://github-checks.internal.tenant-a.staging.altinity.cloud:8443/play`

---

## Result Types

The `result` column contains these values:

| Result | Meaning | Action |
|--------|---------|--------|
| `OK` | Test passed | No action needed |
| `Fail` | Test failed unexpectedly | **Investigate these** |
| `XFail` | Expected failure (known issue) | Usually ignore |
| `XError` | Expected error | Usually ignore |
| `Skip` | Test was skipped | Usually ignore |

**Important:** When investigating failures, filter to `result = 'Fail'` to focus on actual unexpected failures. `XFail` results are expected and should not be treated as new issues.

---

## Test Path Granularity

Test paths in the database vary in depth and structure. Some are shallow suite-level results, others are deep paths with parameters.

Examples:
```
/s3                                          ← Suite level
/tiered storage/with s3gcs/background move   ← Feature level
/s3/minio/part 2/combinatoric table/engine=AggregatingMergeTree,replicated=True,n_cols=10,n_tables=3,part_type=wide  ← Full scenario with parameters
```

If the exact path returns no results, try progressively shorter parent paths until you find matching records.

---

## Build Types

There are three types of ClickHouse builds in the database, identified by the `clickhouse_package` column:

| Build Type | Source Repo | Package Pattern | Example |
|------------|-------------|-----------------|---------|
| **Altinity Release** | altinity/clickhouse-regression | `docker://altinity/clickhouse-server:...` | `docker://altinity/clickhouse-server:25.8.14.20001.altinityantalya` |
| **ClickHouse Release** | altinity/clickhouse-regression | `docker://clickhouse/clickhouse-server:...` | `docker://clickhouse/clickhouse-server:25.3.13.19-alpine` |
| **PR Build** | altinity/ClickHouse | `https://altinity-build-artifacts.s3.amazonaws.com/PRs/...` | `https://altinity-build-artifacts.s3.amazonaws.com/PRs/1360/.../clickhouse` |

**Why this matters:**
- A failure on PR builds only → likely caused by changes in that PR
- A failure on Altinity releases only → may be Altinity-specific patch or backport
- A failure on ClickHouse releases only → upstream issue
- A failure across all build types → general regression

Always check the `clickhouse_package` column to understand which build types are affected.

---

## Common Query Templates

### Get history for a specific test (30 days)

```sql
SELECT 
    result,
    count() as cnt,
    max(start_time) as last_seen,
    min(start_time) as first_seen
FROM `gh-data`.clickhouse_regression_results 
WHERE test_name = '/tiered storage/with s3gcs/background move'
  AND start_time > now() - INTERVAL 30 DAY
GROUP BY result
ORDER BY cnt DESC
FORMAT PrettyCompact
```

### Check failure concentration by version/architecture

```sql
SELECT 
    clickhouse_version,
    architecture,
    with_analyzer,
    sum(result = 'OK') as passes,
    sum(result = 'Fail') as fails,
    round(100.0 * sum(result = 'Fail') / count(), 2) as fail_rate
FROM `gh-data`.clickhouse_regression_results 
WHERE test_name = '/tiered storage/with s3gcs/background move'
  AND start_time > now() - INTERVAL 30 DAY
GROUP BY clickhouse_version, architecture, with_analyzer
HAVING fails > 0 OR passes > 5
ORDER BY clickhouse_version DESC, architecture
FORMAT PrettyCompact
```

### Get error messages for failed runs

```sql
SELECT 
    start_time,
    clickhouse_version,
    architecture,
    result_message
FROM `gh-data`.clickhouse_regression_results 
WHERE test_name = '/tiered storage/with s3gcs/background move'
  AND result = 'Fail'
  AND start_time > now() - INTERVAL 30 DAY
ORDER BY start_time DESC
FORMAT Vertical
```

For additional query patterns, see [.github/database.README.md](../../../.github/database.README.md).

---

## Expected Input (Minimum)

One of the following:
- A full **test path** (preferred)
- A suite-level path
- A commit hash + suite name

If multiple inputs are provided, always prefer the **most specific test path**.

**How to find the test path:** Check the job log for the "Failing" section:
```
Failing

✘ [ Fail ] '/s3/minio/part 2/combinatoric table/engine=AggregatingMergeTree,replicated=True,n_cols=10,n_tables=3,part_type=wide'
```

---

## Output Vocabulary

The investigation must end with **exactly one** of these five categories, spelled as
written. `pr-ci-failure-triage` consumes this result directly, so any other wording
breaks the report:

| Category | Means |
|----------|-------|
| `regression` | A change broke it - name the PR, or the merge window |
| `pre-existing-flaky` | Fails at a similar rate before and after |
| `infrastructure` | The environment failed, not the code |
| `cascade` | A consequence of another failure in the same job |
| `unknown` | Not enough evidence to place it yet |

Full definitions and the evidence each requires: read
`.claude/skills/_shared/failure-categories.md`.

Report the **mechanism** alongside the category, never instead of it - a data race,
a sanitizer slowdown, an assertion, a hardware-dependent codepath. "`pre-existing-flaky`,
sanitizer slowdown under tsan" is a complete answer; "flaky" is not.

Use `unknown` when the evidence is missing, and say what would resolve it. Do not
round an unproven case up to `pre-existing-flaky`.

---

## Step 1: Identify the Search Key

1. Use the provided test path or suite-level path directly as the search key.
2. If a commit hash + suite name is provided, use the suite name as the search key.
3. Explicitly record the selected search key before proceeding.

**Fallback:** If the exact path returns no historical results, try progressively shorter parent paths.

Example:
```
Search key: /s3/minio/part 2/combinatoric table/engine=AggregatingMergeTree,replicated=True,n_cols=10,n_tables=3,part_type=wide
```

---

## Step 2: Query Historical Data

Use SQL queries against the database to inspect recent history.

### Time Windows

Analyze results using fixed windows:

* Last **7 days**
* Last **30 days**

Collect only the following signals:

* Number of FAIL runs (exclude XFail)
* Number of PASS runs
* Last failure timestamp
* Last successful run timestamp

Do not infer root cause at this stage.

---

## Step 3: Check Concentration Patterns

Inspect whether failures are concentrated by:

* ClickHouse version
* Architecture (x86_64 vs aarch64)
* Analyzer usage (`with-analyzer` vs `without-analyzer`)
* Build type (Altinity Release vs ClickHouse Release vs PR Build)

Heuristics:

* Failures limited to one architecture → likely infra or race condition
* Failures only with analyzer → pipeline or settings-related
* Failures starting at a specific version → likely regression
* 100% fail rate on specific versions with 0% on others → strong regression signal
* Failures only on PR builds → likely caused by PR changes
* Failures only on Altinity releases → Altinity-specific patch or backport issue
* Failures only on ClickHouse releases → upstream issue not present in Altinity builds

---

## Step 4: Error Signature Consistency

If error messages or failure reasons are available in the database:

* Same error signature across runs → deterministic / regression-like
* Varying error signatures → flaky or infrastructure-related

Exact message matching is not required.
High-level consistency is sufficient (same file, same assertion, same exception type).

---

## Step 5: Classification

Classify the failure as **one** of the following:

### `pre-existing-flaky`

* Fails at a similar rate with and without the change under review - compare the
  two rates, do not judge the absolute number
* Passes after reruns
* Scattered across versions/architectures with no pattern

A low overall rate does **not** by itself mean flaky: a test that fails 0.5% of the
time historically but 10 of 10 times here is `regression`.

### `regression`

* Passed in previous versions
* Fails consistently in newer versions
* Error signature is stable
* High fail rate on specific versions

### `infrastructure`

* Error names an environment component: docker, network, DNS, disk, package
  install, object store, `Cannot start clickhouse-server`
* Passes on rerun, and unrelated suites failed at the same time
* Say **which** component failed - "infrastructure" with no named mechanism is a guess

### `cascade`

* The failure follows an earlier one in the same job - typically the server died
  and everything after it failed too
* Do not classify it on its own: find the root cause failure, classify that, and
  list these as its consequence

### `unknown`

* No meaningful historical data
* First occurrence or insufficient signal
* State what would resolve it: more runs, a specific attempt's log, a bisect, or a
  local reproduction. Do not round it up to `pre-existing-flaky`.

---

## Step 6: Recommendation

Provide a short, explicit recommendation:

* **Flaky likely**

  * Recommend rerun
  * Suggest tracking if recurring

* **Regression likely**

  * Recommend local reproduction
  * Suggest opening an issue if confirmed

* **New failure**

  * Recommend reproducing with `--only`

---

## Standard Output Format

The agent must always respond using the following format:

```
Database check for: <TEST PATH>

- History: <fails>/<runs> in last 7 days, <fails>/<runs> in last 30 days
- Last fail: <date>
- Last pass: <date>
- Concentration: <version / arch / analyzer or none>
- Error signature: <consistent / varies>

Assessment: <Flaky likely | Regression likely | New failure>
Recommendation: <next step>
```

---

## Notes

* This skill is designed as a fast triage step (2-5 minutes).
* It should not block on missing or incomplete data.
* It can be executed in parallel with local reproduction or CI reruns.
* Always filter to `result = 'Fail'` — ignore `XFail` unless specifically investigating expected failures.

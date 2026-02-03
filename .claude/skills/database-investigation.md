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

- URL:
  https://github-checks.internal.tenant-a.staging.altinity.cloud:8443/play

- Authentication:
  - User: `robot`
  - Password: must be provided by the user when requested

The agent must not assume credentials.
If the password is not provided, explicitly ask for it before proceeding.

---

## Expected Input (Minimum)

One of the following:
- A full **test path** (preferred)
- A suite-level path
- A GitHub Actions job URL
- A commit hash + suite name

If multiple inputs are provided, always prefer the **most specific test path**.

---

## Step 1: Identify the Search Key

1. Prefer the **leaf test path** (deepest failing test).
2. If unavailable, fall back to the closest suite-level path.
3. Explicitly record the selected search key before querying.

Example:
```

Search key:
/iceberg/iceberg cache/rest catalog/iceberg database engine/cache

````

---

## Step 2: Query Historical Data

Use SQL queries against the database to inspect recent history.

### Example Query

```sql
SELECT *
FROM `gh-data`.clickhouse_regression_results
WHERE test_name LIKE '%/iceberg/iceberg cache/rest catalog/iceberg database engine/cache%'
ORDER BY start_time DESC
LIMIT 300;
````

### Time Windows

Analyze results using fixed windows:

* Last **7 days**
* Last **30 days**

Collect only the following signals:

* Number of FAIL runs
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

Heuristics:

* Failures limited to one architecture → likely infra or race condition
* Failures only with analyzer → pipeline or settings-related
* Failures starting at a specific version → likely regression

---

## Step 4: Error Signature Consistency

If error messages or failure reasons are available in the database:

* Same error signature across runs → deterministic / regression-like
* Varying error signatures → flaky or infrastructure-related

Exact message matching is not required.
High-level consistency is sufficient.

---

## Step 5: Classification

Classify the failure as **one** of the following:

### Flaky (Likely)

* Failures appear intermittently
* Passes after reruns
* Error signature varies

### Regression (Likely)

* Passed in previous versions
* Fails consistently in newer versions
* Error signature is stable

### New / Unknown

* No meaningful historical data
* First occurrence or insufficient signal

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

* This skill is designed as a fast triage step (2–5 minutes).
* It should not block on missing or incomplete data.
* It can be executed in parallel with local reproduction or CI reruns.

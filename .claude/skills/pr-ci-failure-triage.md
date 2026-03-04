# Skill: PR CI Failure Triage

## Purpose

Analyze all CI failures in a Pull Request and categorize them:
- Failures **caused by the PR** (regressions)
- **Pre-existing flaky tests** (unrelated to PR)
- **Infrastructure issues** (transient, unrelated)
- **Cascade failures** (caused by earlier test crashing the server)

This skill provides a high-level triage of PR CI status and creates summary comments.

---

## Identifying CI Failures

### CI Report URL

**PR runs:**
```
https://s3.amazonaws.com/altinity-build-artifacts/PRs/<PR>/<SHA>/<RUN_ID>/ci_run_report.html
```

**Branch/REF runs** (e.g., `antalya-25.8`, `v25.8.16.20001.altinityantalya`):
```
https://s3.amazonaws.com/altinity-build-artifacts/REFs/<BRANCH>/<SHA>/<RUN_ID>/ci_run_report.html
```

### JSON Log Browser

**PR runs:**
```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?PR=<PR>&sha=<SHA>&name_0=PR&name_1=<URL_ENCODED_CHECK_NAME>
```

**Branch/REF runs** — note `name_0=MasterCI` and `REF=` instead of `PR=`:
```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?REF=<BRANCH>&sha=<SHA>&name_0=MasterCI&name_1=<URL_ENCODED_CHECK_NAME>
```

---

## Step 1: Get All Failing Tests

Query the CI database to get all failures for the PR:

```sql
SELECT check_name, test_name, test_status, check_start_time
FROM `gh-data`.checks
WHERE pull_request_number = <PR_NUMBER>
  AND test_status = 'FAIL'
ORDER BY check_name, test_name
```

---

## Step 2: Identify Cascade Failures

When a test crashes the server (SIGABRT), subsequent tests fail as cascade effects.

### Cascade Failure Indicators

These test names indicate cascade failures, not root causes:

| Test Name Pattern | Meaning |
|-------------------|---------|
| `Fatal messages (in clickhouse-server.log...)` | Server crash detected |
| `Killed by signal (in clickhouse-server.log...)` | SIGABRT/SIGSEGV detected |
| `Exception in test runner` | Test runner failed |
| `Server died` | Server process terminated |
| `Sanitizer assert (in stderr.log)` | Sanitizer detected issue |

### Identifying Root Cause

When cascade failures are present:
1. Find the **earliest failing test** in that job (by timestamp or test order)
2. Check if it's a test with actual assertions, not a meta-check
3. The root cause test typically runs **before** the cascade failures

---

## Step 3: Categorize Each Failure

For each unique failing test (excluding cascade indicators), determine category:

### Category 1: Pre-existing Flaky Test

Query historical failures:

```sql
SELECT test_name, pull_request_number, check_start_time
FROM `gh-data`.checks
WHERE test_name = '<TEST_NAME>'
  AND test_status = 'FAIL'
ORDER BY check_start_time DESC
LIMIT 20
```

**Indicators:**
- Failures exist across multiple unrelated PRs
- Failures predate the current PR by weeks/months
- Failures occur on PR=0 (master branch)

### Category 2: Infrastructure Issue

**Indicators:**
- Error messages about Docker, networking, timeouts
- `Connection refused`, `Container failed to start`
- Passes on rerun
- Affects unrelated test types

### Category 3: PR-Caused Regression

**Indicators:**
- Test was passing before this PR
- Failure pattern matches PR changes (e.g., JSON tests fail after JSON-related change)
- Consistent failure on specific build types

---

## Step 4: Debug vs Release Build Differences

Different from sanitizer builds:

| Build Type | Behavior |
|------------|----------|
| **Debug** (`amd_debug`) | Assertions enabled, `LOGICAL_ERROR` causes SIGABRT crash |
| **Release** (`amd_binary`, `arm_binary`) | No assertions, errors may be silent or return incorrect data |

### Pattern Recognition

| Observation | Likely Cause |
|-------------|--------------|
| Fails on debug, passes on release | Assertion catches bug that release ignores |
| Fails on release, passes on debug | Performance/timing issue |
| Fails on both | Fundamental bug |

---

## Step 5: Check GitHub Job Status vs Database

Jobs may show different status on GitHub vs database due to reruns:

```bash
gh api repos/Altinity/ClickHouse/actions/runs/<RUN_ID>/jobs \
  --jq '.jobs[] | select(.name | contains("<JOB_NAME>")) | {name, conclusion}'
```

**Discrepancy causes:**
- Partial rerun only ran sanity checks (not actual tests)
- GitHub shows latest run status, database has all runs

---

## Step 6: Investigate Root Cause Tests

For each test identified as potentially PR-caused, use the appropriate skill:

| Test Type | Skill to Use |
|-----------|--------------|
| **Stateless tests** (`NNNNN_test_name`) | `upstream-test-investigation.md` |
| **Integration tests** (`test_*/test.py::test_*`) | `upstream-test-investigation.md` |
| **Regression tests** (`/suite/subsuite/test`) | `regression-test-database-investigation.md` |

Then:
1. Check if test is related to PR changes
2. Verify local reproduction if needed

---

## Step 7: Create PR Summary Comment

After categorization, create a structured comment:

```markdown
## CI Failures Analysis

### Related to this PR
- `<test_name>`: <brief description of failure>
- ...

All other failures in same job (`Fatal messages`, `Killed by signal`, etc.) 
are cascade failures from server crash.

### Pre-existing Flaky Tests (Unrelated)
- `<test_name>` - flaky since <date>
- ...

### Infrastructure Issues (Unrelated)
- `<description>` - passed on rerun

### Issue/Fix References
- **Issue created:** #<NUMBER>
- **Fix PR:** #<NUMBER>
```

---

## Standard Output Format

```
## PR #<NUMBER> CI Triage

### Summary
| Category | Count | Tests |
|----------|-------|-------|
| PR-caused regression | N | test1, test2 |
| Cascade failures | N | (from server crash) |
| Pre-existing flaky | N | test3, test4 |
| Infrastructure | N | description |

### Root Cause Analysis
<For each PR-caused regression, brief analysis>

### Recommendations
1. <action item>
2. <action item>
```

---

## Related Skills

- **`upstream-test-investigation.md`** - Deep investigation of upstream test (Stateless/Integration/Fuzzer/Stress)
- **`upstream-ci-database-queries.md`** - CI database query reference (Altinity + upstream)
- **`regression-test-database-investigation.md`** - Altinity regression test database investigation
- **`github-issue-template.md`** - Templates for writing GitHub issues after investigation

---

## Notes

- Always check if failures predate the PR before attributing them to PR changes
- Server crashes (SIGABRT) on debug builds often indicate assertion failures
- A single root cause test can cause dozens of cascade failures
- Rerun data may mask original failures in GitHub UI

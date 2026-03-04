# Skill: Upstream Test Failure Investigation

## Purpose

Deep investigation of a specific **upstream ClickHouse test** (Stateless or Integration) failure:
- Query failure history across versions and build types
- Analyze logs to find root cause
- Search for existing upstream issues and fixes
- Determine if fix needs backporting
- Provide local reproduction steps

This skill focuses on **single test investigation**, not PR-wide triage.

---

## Test Type Identification

| Test Type | Check Name Pattern | Test Name Pattern | Example |
|-----------|-------------------|-------------------|---------|
| **Integration** | `Integration tests (amd_*, N/M)` | `test_*/test.py::test_*` | `test_storage_rabbitmq/test.py::test_rabbitmq_json` |
| **Stateless** | `Stateless tests (arm_*, ...)` | `NNNNN_test_name` (5-digit prefix) | `01825_type_json_in_array` |
| **AST fuzzer** | `AST fuzzer (amd_*)` | Error message (not a test name) | `Logical error: 'std::exception... out_of_range...'` |
| **Stress test** | `Stress test (amd_*)` | Meta-status | `Server died`, `Cannot start clickhouse-server` |
| **BuzzHouse** | `BuzzHouse (amd_*)` | Error message | Similar to AST fuzzer |

### Fuzzer / Stress Test Investigation Differences

These job types require a different investigation approach than Integration/Stateless tests:

**AST fuzzer:**
- Randomly mutates SQL queries from existing tests to find server crashes
- The `test_name` in the database IS the error message (e.g., `Logical error: 'std::exception. Code: 1001, type: std::out_of_range, e.what() = vector'`)
- Key log files: `fatal.log` (crashing query + stack trace), `stderr.log`, `job.log`
- The `fatal.log` ends with a `Changed settings:` line listing all non-default settings needed to reproduce
- Always check if `allow_experimental_*` settings are involved — experimental features are expected to have bugs

**Stress test:**
- Runs the server under heavy load for an extended period
- Key log files: `run.log`, `application_errors.txt`, `clickhouse-server.err.log`, `clickhouse-server.initial.log`
- If the server failed to start, check `clickhouse-server.initial.log` for the root cause
- `application_errors.txt` contains all exceptions during the run

**Reproduction from fuzzer crashes:**
1. Read `fatal.log` to extract the crashing SQL query
2. Read the `Changed settings:` line for required settings
3. Create a minimal table matching what the query expects
4. Run the query with those settings enabled

---

## Step 1: Gather Information

Collect from user or context:
1. **Test name** (full path)
2. **CI job URL or report URL**
3. **PR number** (if applicable)
4. **Database password** (for Altinity database)

---

## Step 2: Query Failure History

Use queries from `upstream-ci-database-queries.md`.

### Key Questions to Answer

1. **Is this a new failure or pre-existing?**
   - Query failures across multiple PRs
   - Check if failures predate the current PR

2. **Which build types are affected?**
   - Debug vs Release
   - Sanitizer vs Non-sanitizer
   - Specific modes (AsyncInsert, ParallelReplicas)

3. **Is it version-specific?**
   - Compare 25.8 vs 25.3 vs master

### Classification

| Pattern | Classification |
|---------|----------------|
| Failures across many PRs over months | Pre-existing flaky |
| Failures only in current PR | Potential regression |
| Failures on debug only | Assertion catching silent bug |
| Failures on specific version only | Version-specific regression |

---

## Step 3: Analyze Logs

### Finding Log URLs

**Integration tests:**
```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?PR=<PR>&sha=<SHA>&name_0=PR&name_1=Integration%20tests%20%28<build_type>%29
```

**Stateless tests:**
```
https://altinity-build-artifacts.s3.amazonaws.com/json.html?PR=<PR>&sha=<SHA>&name_0=PR&name_1=Stateless+tests+%28<build_type>%29&name_2=Tests
```

### Common Failure Patterns

| Error Pattern | Likely Cause |
|---------------|--------------|
| `LOGICAL_ERROR` + SIGABRT | Assertion failure (debug build) |
| `server died` / `ConnectionRefusedError` | Server crash |
| `result differs with reference` | Output mismatch |
| `Timeout` | Slow test or deadlock |
| `Database already exists` | Missing cleanup |
| Exit code 137 | OOM kill |
| `Container failed to start` | Infrastructure issue |

### Server Crash Analysis

If server crashed, check `clickhouse-server.err.log`:
1. Find the stack trace
2. Identify the failing assertion or error
3. Note the query that triggered the crash

---

## Step 4: Check Test Source Code

Read the test file to understand:
1. What the test does
2. What settings it uses (MergeTree settings, etc.)
3. Whether it forces specific part types (compact vs wide)

```bash
# For stateless tests
cat tests/queries/0_stateless/<TEST_NAME>.sql

# For integration tests
cat tests/integration/<TEST_DIR>/test.py
```

### Key Settings to Note

| Setting | Impact |
|---------|--------|
| `min_bytes_for_wide_part` | Forces compact or wide parts |
| `write_marks_for_substreams_in_compact_parts` | Affects compact part format |
| `allow_experimental_object_type` | Enables deprecated JSON type |

---

## Step 5: Search for Upstream Issues

### Basic Searches

```bash
# Search by test name
gh search issues --repo ClickHouse/ClickHouse "<test_name>" --limit 10

# Search by error pattern
gh search issues --repo ClickHouse/ClickHouse "<error_keyword>" --state open --limit 10

# View issue details
gh issue view <ISSUE_NUMBER> --repo ClickHouse/ClickHouse --json title,state,body,comments

# Check if fix exists
gh pr list --repo ClickHouse/ClickHouse --search "<test_name>" --state merged
```

### Advanced Search Strategies

The basic search often returns no results. Use multiple strategies systematically:

**By STID (Stack Trace ID):** The upstream CI auto-generates issues with STID identifiers (format: `XXXX-XXXX`). These appear in the `test_name` field in the CI database:
```bash
gh api search/issues --method GET \
  -f "q=repo:ClickHouse/ClickHouse is:issue \"STID: <STID>\"" \
  -f per_page=10
```

**By exact error message in title:**
```bash
gh api search/issues --method GET \
  -f "q=repo:ClickHouse/ClickHouse is:issue \"<exact_error>\" in:title" \
  -f per_page=10
```

**By stack trace function names:**
```bash
gh api search/issues --method GET \
  -f "q=repo:ClickHouse/ClickHouse is:issue \"<FunctionName>\" \"<ErrorType>\"" \
  -f per_page=10
```

**By label combinations:**
```bash
gh api search/issues --method GET \
  -f "q=repo:ClickHouse/ClickHouse is:issue label:fuzz \"<error_keyword>\"" \
  -f per_page=20
```

**By component labels:** Common labels: `fuzz`, `crash`, `bug`, `comp-joins`, `comp-analyzer`, `experimental feature`, `testing`

### Parse API Results

```bash
gh api search/issues --method GET \
  -f "q=repo:ClickHouse/ClickHouse is:issue <QUERY>" \
  -f per_page=10 | python3 -c "
import json,sys
d = json.load(sys.stdin)
print(f'Total results: {d.get(\"total_count\", 0)}')
for item in d.get('items', []):
    print(f'  #{item[\"number\"]} [{item[\"state\"]}] {item[\"title\"]}')
    print(f'    URL: {item[\"html_url\"]}')
"
```

### Search Checklist

When investigating a crash/error, try these searches in order:
1. STID (if available in CI database `test_name` field)
2. Exact error message in issue title
3. Key function name from stack trace + error type
4. Error type + `fuzz` label
5. Related feature keywords + `crash`
6. Broader error category (e.g., `out_of_range vector`)

If all searches return empty, the bug is **unreported** and should be filed.

---

## Step 6: Local Reproduction

### Download Debug Binary

```bash
wget https://altinity-build-artifacts.s3.amazonaws.com/PRs/<PR>/<SHA>/build_amd_debug/clickhouse
chmod +x clickhouse
./clickhouse server
```

### Run Specific Stateless Test

```bash
./clickhouse-test <TEST_NUMBER> --no-stateless --no-parallel
```

### Manual Reproduction

1. Start the server
2. Connect with client: `./clickhouse client`
3. Execute the failing queries from the test

---

## Step 7: Risk Assessment

| Factor | Question |
|--------|----------|
| **Data Loss** | Can this cause data loss in production? |
| **Crash** | Does it crash the server? |
| **Data Correctness** | Can it produce incorrect results silently? |
| **Scope** | What configurations are affected? |

### Bug Classification

| Type | Characteristics |
|------|-----------------|
| **Test-only issue** | Bug in test code, not in ClickHouse |
| **Flaky test** | Race condition in test, intermittent |
| **Real bug (debug only)** | Assertion catches issue, release ignores |
| **Real bug (all builds)** | Actual ClickHouse bug |
| **Experimental feature bug** | Bug in code guarded by `allow_experimental_*` settings; expected to be unstable |
| **Pre-existing upstream bug** | Bug exists in upstream CI history, not introduced by our changes |

### Experimental Feature Bugs

When the failure requires `allow_experimental_*` settings (visible in fuzzer's `Changed settings:` line):

1. The feature is explicitly marked experimental — upstream tolerates known bugs
2. On **release builds**: returns error code 1001 (`LOGICAL_ERROR` / `STD_EXCEPTION`), server stays up
3. On **debug/sanitizer builds**: triggers `abortOnFailedAssertion()` → SIGABRT, server crashes
4. These are real bugs but lower priority — still worth reporting if no upstream issue exists
5. Cross-reference with upstream CI to confirm it's not Altinity-specific (see `upstream-ci-database-queries.md`)

---

## Standard Output Format

```
## Investigation: <TEST_NAME>

### Test Information
- **Type:** Integration / Stateless
- **Test:** <full test name>
- **Check:** <CI job name>

### Failure History
| Build Type | Last 30 Days | Fail Rate |
|------------|--------------|-----------|
| debug      | X/Y          | Z%        |
| release    | X/Y          | Z%        |

- **Pre-existing:** Yes/No (first failure: <date>)
- **Version-specific:** Yes/No

### Root Cause
<Brief description of why the test fails>

### Error Details
```
<Key error message or stack trace>
```

### Upstream Status
- **Issue:** <link> or "None found"
- **Fix PR:** <link> or "None"

### Reproduction Steps
1. <step>
2. <step>

### Risk Assessment
| Factor | Assessment |
|--------|------------|
| Data Loss | No |
| Crash | Yes/No |
| Silent Corruption | Yes/No |

### Recommendations
1. <Primary recommendation>
2. <Secondary recommendation>
```

---

## Related Skills

- **`pr-ci-failure-triage.md`** - PR-wide failure analysis
- **`upstream-ci-database-queries.md`** - CI database query reference (Altinity + upstream), including cross-referencing
- **`regression-test-database-investigation.md`** - For Altinity regression tests (different from upstream)
- **`github-issue-template.md`** - Templates for writing GitHub issues after investigation

---

## Notes

- Always check if failure predates the PR before attributing to PR changes
- Debug builds crash on assertions that release builds ignore silently
- Randomized MergeTree settings in test runner can cause flakiness
- Check `min_bytes_for_wide_part` if failure is related to compact/wide parts
- Integration tests use pytest; stateless tests use numbered SQL files

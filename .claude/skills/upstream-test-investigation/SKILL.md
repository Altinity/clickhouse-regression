---
name: upstream-test-investigation
description: Investigate one upstream CI failure in depth - "investigate this test", "why is this test failing", "analyse this failure". Handles Stateless tests (`03340_projections_formatting`), Integration tests (`test_s3_cluster/test.py::test_ambiguous`), unit tests, and job-level failures with no test name (`Server died`, `Unknown error`, `Timeout`, `Cannot start clickhouse-server`) - anything recorded in `gh-data.checks`. Works from a PR or from a branch/MasterCI run: queries history, analyses logs, identifies the PR or merge window that broke it, and searches Altinity and upstream issues.
---

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

## Step 1: Gather Information

Always collect:
1. **Failure name** - a test name, or a job-level name with no test (see below)
2. **Check (job) name** - pins the build type; without it, history mixes builds
3. **CI job URL or report URL**
4. **Database password** (for the Altinity database)

Then identify **which context** you are in, because it changes what else you need
and what question you are answering:

| Context | Also collect | Question to answer |
|---------|--------------|--------------------|
| **Pull request** | PR number | Did this PR break it? |
| **Branch / MasterCI** (`pull_request_number = 0`) | branch name, the failing run, the last passing run | What broke it on this branch, and when? |

The branch context usually arrives from `release-branch-monitor`, phrased as "this
test started failing on `<branch>`, run X failed and run Y passed". Those two runs
are the merge window - keep them, Step 5 needs them.

### When the failure has no test name

Roughly 13% of failures in `gh-data.checks` are job-level: `Server died`,
`Unknown error`, `Timeout`, `Cannot start clickhouse-server`, `Check failed`,
`Some queries hung`, `Build ClickHouse`. They are rows in this table, so they belong
to this skill - but there is no test to look up.

For these:
1. **`Server died` first goes through the taxonomy** in `pr-ci-failure-triage`
   (*Server died Taxonomy*): exit 143 from a harness timeout, an actual crash, and
   an OOM all carry this same label, and only one of them is a bug.
2. **Recover the test that was actually running** - `ci-job-forensics` section 4.
   The report will not name it; the client log or the shell trace will.
3. Then continue from Step 2 using the recovered test, or - if none can be
   recovered - treat the job itself as the subject and rely on logs.

---

## Step 2: Query Failure History

Use queries from the `upstream-ci-database-queries` skill.

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

| Pattern | Category | Mechanism to note |
|---------|----------|-------------------|
| Failures across many PRs over months | `pre-existing-flaky` | - |
| Failures only in current PR, and the diff touches code the test exercises | `regression` | - |
| Failures only in current PR, but no plausible code path | `unknown` | say what would resolve it |
| Failures on debug only | category from the rate comparison | assertion catching a bug release ignores |
| Failures on a specific version only | category from the rate comparison | version-specific behaviour |
| Environment errors, passes on rerun | `infrastructure` | name the failing component |
| Follows a server death in the same job | `cascade` | classify the root cause instead |

The first two columns are the answer. "Debug only" and "version-specific" are
**mechanisms**, not categories - they still need the rate comparison to decide
whether the change is responsible.

---

## Step 3: Analyze Logs

### Finding Log URLs

All CI report, log and artifact URL patterns live in one place:
**read `.claude/skills/_shared/ci-urls.md`**.

It covers the PR-vs-REF fork (path segment, `name_0`, and `job.log` vs `job.log.zst`),
the CI report and JSON-browser URLs, direct artifact paths and job directory naming,
S3 listing, range reads for large logs, and the rerun-overwrites-artifacts gotcha.

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

## Step 5: Identify What Broke It

Only for `regression` candidates. Skip when history already says
`pre-existing-flaky`.

**In a PR context**, the culprit is the PR - confirm the mechanism: does the diff
touch code the test exercises?

**In a branch context**, find the merge window. Branch runs carry
`pull_request_number = 0`, so the history is a clean timeline:

```sql
SELECT check_start_time, commit_sha, test_status
FROM `gh-data`.checks
WHERE test_name = '<TEST_NAME>'
  AND check_name = '<EXACT_JOB_NAME>'
  AND pull_request_number = 0
  AND check_start_time > now() - INTERVAL 60 DAY
ORDER BY check_start_time
```

Take the last-good and first-bad `commit_sha` and list what landed between them:

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


Then narrow, in this order:
1. Did any PR in the window run this same job and fail it? Query
   `pull_request_number IN (...)` with the same `check_name`.
2. Does any diff in the window reach the code the test exercises?
3. If it still will not narrow, **the window is the answer**.

> **A single PR often cannot be identified, and the reason is structural.** The set
> of jobs a pull request runs is **chosen per PR** - it may match MasterCI or be much
> smaller. MasterCI always runs the full set.
>
> So **a missing row is ambiguous**: finding no result for a candidate PR does not
> mean the test passed there - the job may never have run. Confirm the job ran
> before reading anything into its absence:
>
> ```sql
> SELECT pull_request_number, check_name, countIf(test_status='FAIL') AS fails, count() AS runs
> FROM `gh-data`.checks
> WHERE pull_request_number IN (<CANDIDATES>) AND check_name = '<EXACT_JOB_NAME>'
> GROUP BY pull_request_number, check_name
> ```
>
> A PR absent from these results never ran the job, and tells you nothing. If none
> of the candidates ran it, the merge window is the answer and no further querying
> will improve on it.
>
> Report the window instead: "broke between `<SHA>` and `<SHA>`, N commits, of which
> these touch relevant code". That is a complete answer, not a partial one.

Before concluding the code broke: if the failure starts at a sharp boundary and
never recovers, check whether the **environment** changed at that boundary - runner
image tag, base image, a dependency. Persistent infrastructure breakage looks
identical to a code regression on a branch timeline.

---

## Step 6: Search for Existing Issues

Search **both** repositories. An Altinity-side issue is often the one that exists,
especially for failures on `antalya-*` and `*-altinity*` branches.

```bash
# Altinity fork - check this one too, it is frequently the only hit
gh search issues --repo Altinity/ClickHouse "<test_name>" --limit 10
gh search issues --repo Altinity/ClickHouse "<error_keyword>" --state open --limit 10

# Upstream
gh search issues --repo ClickHouse/ClickHouse "<test_name>" --limit 10
```

Report what you found on each side separately: an upstream issue with a fix that is
not in our branch is a backport candidate; an Altinity issue may already track this
exact failure.



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

## Step 7: Local Reproduction

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

## Step 8: Risk Assessment

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
5. Cross-reference with upstream CI to confirm it's not Altinity-specific (see `upstream-ci-database-queries` skill)

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

### What Broke It

- **Culprit:** PR #N, **or** merge window `<LAST_GOOD>..<FIRST_BAD>` (N commits)
- If the window could not be narrowed to one PR, say so and say why - a reduced job
  set on PRs is a normal and complete reason

### Existing Issues
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

- **`pr-ci-failure-triage`** - PR-wide failure analysis
- **`upstream-ci-database-queries`** - CI database query reference (Altinity + upstream), including cross-referencing
- **`regression-test-database-investigation`** - For Altinity regression tests (different from upstream)
- **`github-issue-template`** - Templates for writing GitHub issues after investigation

---

## Notes

- Always check if failure predates the PR before attributing to PR changes
- Debug builds crash on assertions that release builds ignore silently
- Randomized MergeTree settings in test runner can cause flakiness
- Check `min_bytes_for_wide_part` if failure is related to compact/wide parts
- Integration tests use pytest; stateless tests use numbered SQL files

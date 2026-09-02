---
name: regression-test-database-investigation
description: Investigate one Altinity regression-suite (TestFlows) failure - "investigate this test", "why is this scenario failing". Handles scenario paths starting with a slash (`/swarms/...`, `/lightweight delete/...`, `/ldap/authentication`) - anything recorded in `gh-data.clickhouse_regression_results`. Reaches a verdict - regression, pre-existing flaky, infrastructure, cascade, or unknown - using the CI database, the ClickHouse source when the error comes from the server, and this repository's own history. Works without the database password.
---

# Skill: Database Failure Investigation (MVP)

## Purpose

Investigate one failing scenario of the Altinity regression suite (TestFlows -
paths starting with `/`) and reach a verdict: which of the five categories it is,
what mechanism produced it, and what would fix it.

The CI database is the main tool but **not the only one**. Two other sources
routinely decide the case on their own:

- the **ClickHouse source at the failing version** - when the error text comes from
  the product rather than from the harness (Step 0)
- the **regression repository's own history** - when a sibling suite has already hit
  and fixed the same thing (Step 5)

Do not stop because the database is unavailable. Work through everything that does
not depend on it first.

---

## Database Access

- **Host:** `github-checks.internal.tenant-a.staging.altinity.cloud`
- **Database:** `gh-data`
- **Table:** `clickhouse_regression_results`
- **Full path:** `` `gh-data`.clickhouse_regression_results ``

- **Authentication:**
  - User: `robot`
  - Password: must be provided by the user when requested

The agent must not assume credentials - never invent or guess a password.

**A missing password does not stop the investigation.** Do everything that does not
need the database first (Step 0, reading the test source, the repository history),
then ask for the password at the point where a query is actually the next step, and
say what it would add. Often it only confirms *since when* a failure occurs, while
the cause and the fix are already settled - in that case, report the finding and
name the query as the remaining gap rather than waiting.

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

## Step 0: Does the Error Come From the Product or From the Harness?

Do this **before touching the database**, and before asking for a password. It costs
four commands and it settles a whole class of failures on its own - twice now it has
produced the complete answer while the database could only have said *when*.

**The signal:** the error text is a ClickHouse server error, not a Python or
TestFlows one. `Code: NNN. DB::Exception: ...`, `ACCESS_DENIED`, `UNKNOWN_SETTING`,
`Unknown function`, `NOT_IMPLEMENTED`, `NUMBER_OF_ARGUMENTS_DOESNT_MATCH`. The
server is refusing something it used to accept - which means the product changed,
on purpose, and our test still speaks the old dialect.

**First, check the clone covers the version under test.** Step 0 concludes from
*absence* - "this branch does not have the setting" - and absence in a clone that
predates the failing build is indistinguishable from absence in reality. This check
costs milliseconds and prevents a confidently wrong answer:

```bash
git log -1 --format='%ci' upstream/master     # is this newer than the failing run?
```

If it is older than the build under test, fetch **one branch**, not the whole remote
(`git fetch upstream master`), and expect it to take minutes on this repository. If
that is not practical, use the GitHub API for the specific file instead - and either
way, **never report "not present" from a clone that does not reach that version.**

**The recipe**, in the ClickHouse clone (ask the user where it is if you do not
know):

```bash
# 1. Find the code that produces the message
git grep -n "<distinctive phrase from the error>" upstream/master -- src/

# 2. If it names a setting, find when its default changed
git grep -n "<setting_name>" upstream/master -- src/Core/SettingsChangesHistory.cpp

# 3. Find the commit and the PR that introduced it
git log --oneline -S "<setting_name>" -- src/Core/Settings.cpp | tail -5
git log -1 --format="%H %ci%n%s%n%b" <SHA>

# 4. Establish the blast radius. List the branches that exist - do not guess names -
#    and keep "absent" distinct from "no such branch".
git branch -r --list 'origin/antalya-*' 'origin/2*.*' upstream/master

for b in <the refs the command above printed> ; do
  if ! git cat-file -e "$b:src/Core/Settings.cpp" 2>/dev/null; then
    printf "%-34s no such ref\n" "$b"
  elif git grep -q "<setting_name>" "$b" -- src/Core/Settings.cpp 2>/dev/null; then
    printf "%-34s PRESENT - affected\n" "$b"
  else
    printf "%-34s absent - not affected\n" "$b"
  fi
done
```

Step 2 of that recipe is the one that pins the version, because
`SettingsChangesHistory.cpp` records the release in which a default flipped.

A bare `0` from a count is ambiguous - it means both "the branch does not have this"
and "that branch name does not exist". The loop above separates them, because
reporting a branch as unaffected when you never actually looked at it is worse than
reporting nothing.

**What it establishes:** the mechanism, the culprit PR, and which branches are
affected - the three things a verdict needs. The rate comparison is then unnecessary
(see the deterministic-mechanism exception in Step 6), and the database is reduced
to confirming *since which run* it fails, which rarely changes the answer.

**When the verdict is "the product changed on purpose":** the fix belongs in this
repository, not in ClickHouse. Say so explicitly in the report - the reader needs to
know where the work goes.

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

## Step 5: Has a Sibling Suite Already Hit This?

Before proposing any fix, check whether someone in this repository already solved
the same thing. This is cheap and it has paid off: a sibling fix landed the same day
as an investigation and was found only by accident.

```bash
# Has anyone fixed this recently, by PR number, setting or error phrase?
git log --oneline -S "<setting_name or distinctive phrase>" -- . | head
git log --oneline --grep="<PR number>" | head

# Which other places in this repository have the same pattern?
git grep -n "<the pattern that broke, e.g. s3('http>" -- '*.py'
```

A precedent gives you three things at once: a fix already reviewed, the version
guard it needed (`check_clickhouse_version(...)`), and evidence of how wide the
problem is.

**Check whether the precedent is already pushed**, because it changes what you
recommend:

```bash
git branch -r --contains <precedent SHA> | head
```

- **Already on `main`** - someone is mid-sweep and missed these call sites. The
  recommendation is to finish the sweep, and it is worth saying who authored the
  precedent so the work is not duplicated.
- **Local or unpushed only** - nobody has addressed this yet, and the fix is a fresh
  change rather than a continuation.

**Report every other call site you find, not just the failing one.** A failure that
looks like one broken scenario is often one of five, and the others are simply not
running yet. Scope is part of the verdict.

---

## Step 6: Classification

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

**Deterministic mechanisms need no rate.** If you have read the source and the code
rejects this unconditionally - a changed setting default, a removed function, a new
refusal path - the rate is 100% by construction. Report file, line and the PR that
introduced it, and do not fall back to `unknown` for want of counts.

**Otherwise, state the counts.** Every classification carries the numbers behind it:
"fails 30% of the time on the branch, 8 of 8 here". Before claiming a correlation,
gather 5-15 samples and check whether any contradicts it; with fewer, say how many
the claim rests on. A verdict with neither counts nor a mechanism read from source
is not finished.

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

## Step 7: Recommendation

Provide a short, explicit recommendation, keyed to the verdict:

* **`pre-existing-flaky`** - rerun; suggest tracking (an xfail or an issue) if it
  recurs. Say the rate, so the reader can judge whether tracking is worth it.

* **`regression`, fix in ClickHouse** - reproduce locally, then open an issue
  against the product with the mechanism and the culprit PR.

* **`regression`, fix in this repository** - the product changed on purpose and the
  test still speaks the old dialect. Propose the change, list **every** affected call
  site, and follow the precedent's version guard if one exists. This is a PR here,
  not an issue against ClickHouse.

* **`infrastructure`** - name the component that failed and who can fix it. If it is
  persistent rather than transient, say so: it will not clear on a rerun.

* **`cascade`** - no recommendation of its own. Point at the root-cause failure and
  recommend on that.

* **`unknown`** - state exactly what would resolve it: more runs, a specific
  attempt's log, a bisect, or a local reproduction. Do not recommend a rerun as a
  way of avoiding the question.

---

## Standard Output Format

```
Investigation: <TEST PATH>

Verdict:      <regression | pre-existing-flaky | infrastructure | cascade | unknown>
Mechanism:    <one line - what actually makes it fail>
Fix goes in:  <ClickHouse | this repository | CI configuration | nothing to fix>

Evidence
  <the block that applies - see below>

Scope:        <every affected call site or scenario, not only the one that failed>
Precedent:    <sibling fix already in this repository, or none found>
Recommendation: <next step>
```

Fill **one** evidence block - the one matching how the case was settled. Omit the
other entirely rather than filling it with `N/A`.

**Settled from source** (Step 0 closed it - a deterministic mechanism):

```
  Code:         <file:line> - <what the code does>
  Introduced by: <PR #N>, <SHA>, <date>, first released in <version>
  Blast radius: <branches that have it / branches that do not>
```

**Settled from the database** (Steps 1-4 closed it):

```
  History:      <fails>/<runs> in 7 days, <fails>/<runs> in 30 days
  Last fail / last pass: <dates>
  Concentration: <version / arch / analyzer, or none>
  Error signature: <consistent / varies>
```

`Verdict` must be one of the five words above, spelled exactly. The older wording -
"Flaky likely", "Regression likely", "New failure" - is replaced; see
`.claude/skills/_shared/failure-categories.md`.

`Fix goes in` is required. "The product changed on purpose and our test is outdated"
and "the product broke" are both `regression`, and this line is what tells them
apart for whoever reads the report.

---

## Notes

* This skill is designed as a fast triage step (2-5 minutes).
* It should not block on missing or incomplete data.
* It can be executed in parallel with local reproduction or CI reruns.
* Always filter to `result = 'Fail'` — ignore `XFail` unless specifically investigating expected failures.

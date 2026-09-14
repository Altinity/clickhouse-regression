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

Do this **before touching the database**, and before asking for a password. It
settles a whole class of failures on its own - it has produced the complete answer
three times while the database could only have said *when*.

**The signal:** the error text is a ClickHouse server error, not a Python or
TestFlows one. `Code: NNN. DB::Exception: ...`, `ACCESS_DENIED`, `UNKNOWN_SETTING`,
`Unknown expression or function identifier`, `NOT_IMPLEMENTED`,
`NUMBER_OF_ARGUMENTS_DOESNT_MATCH`. Also count a message whose **wording** changed
while the behaviour did not - the test asserts on text, so a rephrasing breaks it
exactly like a behaviour change would.

Either way the product changed on purpose and our test still speaks the old dialect.

### Run the script first

`scripts/source_forensics.py` does steps 1-4 below in a single run, issuing the
independent lookups in parallel. It exists because the cost of this step is
round-trips, not requests: the calls total ~3 seconds, while doing them one turn at
a time has taken five minutes.

```bash
.claude/skills/regression-test-database-investigation/scripts/source_forensics.py \
  --token '<distinctive string from the error>' [--pr <n>] [--path src/...]
```

It returns: the source files containing the token, the merged PRs that mention it,
the culprit PR with its **merge date** and merge SHA, the changelog entry naming the
release, and the blast radius across branches.

Two limits it reports rather than hides:

- **A generic token cannot be attributed.** If the token matches more than 20 PRs it
  refuses to name a culprit and asks you to narrow it or pass `--pr`. Prefer the
  exact new wording over a common phrase - `"Maybe you meant"` matches 50 PRs and
  attributes to the wrong one; the specific setting or message name matches a handful.
- **Blast radius is only as precise as the token.** With a generic phrase it tells
  you the phrase is present on a branch, not that this change is.

Read the manual recipe below when the script comes back empty, when you need
something it does not cover, or to understand what it is doing.

### The same thing by hand - GitHub API, no local clone needed

Every question below is one request against a repository that is always current.
Measured: locating the code ~1s, reading a file at any ref ~0.7s, finding the PR
~1.5s. **Do not clone and do not `git fetch`** - a fetch on ClickHouse takes minutes
and a stale clone silently turns "I did not look" into "not present".

```bash
# 1. Which file produces the message? (searches the default branch)
gh api -X GET search/code \
  -f q='<distinctive token from the error> repo:ClickHouse/ClickHouse' \
  --jq '.items[].path'

# 2. Read that file, or SettingsChangesHistory.cpp, at any ref.
#    Use raw, NOT the contents API - contents caps at 1 MB and Settings.cpp exceeds it.
curl -sL "https://raw.githubusercontent.com/ClickHouse/ClickHouse/master/src/Core/SettingsChangesHistory.cpp" \
  | grep -n "<setting_name>"

# 3. Which PR introduced it? Search by the distinctive token, not by the test name.
gh api -X GET search/issues \
  -f q='repo:ClickHouse/ClickHouse <setting_name or exact new message> type:pr' \
  --jq '.items[] | "\(.number)  \(.closed_at[0:10])  \(.title)"'

# 3b. Which release shipped it, in the project's own words?
#     LIST the changelog files first - release filenames are not predictable and
#     guessing one costs a round. (search/code with a PR number returns nothing.)
gh api repos/ClickHouse/ClickHouse/contents/docs/changelogs --jq '.[].name' | tail -20

curl -sL "https://raw.githubusercontent.com/ClickHouse/ClickHouse/master/docs/changelogs/<the file you picked>" \
  | grep -n "<PR number>"

# 4. Blast radius: fetch the file per branch and count. One request each.
for r in ClickHouse/ClickHouse:master \
         Altinity/ClickHouse:antalya-26.6 Altinity/ClickHouse:antalya-25.8 ; do
  repo=${r%%:*}; ref=${r##*:}
  body=$(curl -sfL "https://raw.githubusercontent.com/$repo/$ref/src/Core/Settings.cpp") \
    && printf "%-42s %s\n" "$r" \
         "$(printf '%s' "$body" | grep -c '<setting_name>' | sed 's/^0$/absent - not affected/;s/^[1-9].*/PRESENT - affected/')" \
    || printf "%-42s no such ref or path\n" "$r"
done
```

Step 2 pins the **version** for a setting change: `SettingsChangesHistory.cpp`
records the release in which a default flipped. Step 3b does the same for anything
else, and is usually faster - the changelog names the release and describes the
change in the project's own words, which is quotable in the report. Step 4 must keep "absent" distinct from "no such
ref" - reporting a branch as unaffected when the request failed is worse than
reporting nothing.

> **Dates lie in both directions.** `search/commits` and `git log` report the date a
> commit was *authored on its feature branch*, which can be weeks before it reached
> master. When the date matters, take it from the **merge commit on master** or from
> the PR's `closed_at`, and say which one you used.

> **`search/code` only indexes the default branch.** It answers "where is this code",
> never "which branches have it" - that is what step 4 is for. Code search is limited
> to 30 requests per minute; the rest of the API to 5000 per hour.

### Step 0.5: When the API is not enough

The one thing the API cannot do is a **pickaxe** - `git log -S`, "when did this
string enter this file". `search/commits` matches commit *messages*, not diffs, and
has returned a follow-up PR instead of the original.

If steps 1-4 did not pin the culprit, **ask the user two questions** before going
further:

1. Do you have a local ClickHouse clone, and where?
2. Is it up to date - does it include the version under test?

Then work in the clone they name. Confirm the date yourself, since it is free:

```bash
git log -1 --format='%ci' upstream/master
```

If it does not reach the version under test, say so and stop concluding from
absence - report the window you can support instead. **Never run `git fetch`**; it
takes minutes on this repository and is the user's call, not yours.

In the clone:

```bash
git log --oneline -S '<setting_name>' <ref> -- src/Core/Settings.cpp | tail -5
git log -1 --format='%H %ci%n%s' <SHA>
```

> **Never use `--contains` on the ClickHouse clone.** `git branch -r --contains` and
> `git tag --contains` walk thousands of refs and do not finish - one run was killed
> at five minutes. To ask whether a named ref carries a commit, invert the question:
>
> ```bash
> git merge-base --is-ancestor <SHA> <ref> && echo present || echo absent
> ```
>
> One reachability check per ref, instant. (`--contains` is fine in the
> clickhouse-regression repository, where it is used in Step 5 - it is only
> unusable against ClickHouse.)

> **Always name the ref.** A bare `git grep <pattern> -- src/` reads whatever branch
> happens to be checked out, which is often a maintenance branch and not what you
> mean. Write `git grep <pattern> upstream/master -- src/`. Getting this wrong has
> produced the opposite conclusion.

### What Step 0 establishes

The mechanism, the culprit PR, and which branches are affected - the three things a
verdict needs. The rate comparison then becomes unnecessary (see the
deterministic-mechanism exception in Step 6), and the database is reduced to
confirming *since which run* it fails, which rarely changes the answer.

**When the verdict is "the product changed on purpose":** the fix belongs in this
repository, not in ClickHouse. Say so explicitly in the report - the reader needs to
know where the work goes.

### Stop here when Step 0 closed the case

If you have the mechanism, the culprit PR and the blast radius, **skip Steps 1-4
entirely and go to Step 5** (precedent), then Step 6 (classification).

Steps 1-4 query the database for *when* a failure started. That is worth having when
the cause is open, and worth nothing once the cause is read from source: the
deterministic-mechanism exception in Step 6 already accepts a source-read mechanism
without any rate. Do not ask for the database password to complete a picture that is
already complete - name the query as a remaining gap in the report and move on.

The steps below are numbered in sequence but are not a checklist to be worked
through regardless. Running them anyway has cost real time on a verdict that was
already settled.

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
# a. By string - did someone already touch this exact text?
git log --oneline -S "<setting_name or distinctive phrase>" -- . | head
git log --oneline --grep="<PR number>" | head

# b. By FORM - has this KIND of failure been fixed here before?
#    Run this even when (a) returns nothing; it usually does return nothing.
git log --oneline -i --grep='exception message' --grep='error message' \
        --grep='update.*message' --grep='for 2[0-9]\.[0-9]' | head -20

# c. Which other places in this repository have the same pattern?
git grep -n "<the pattern that broke>" -- '*.py'
```

**(b) is the one that pays.** Searching by string looks for this failure; searching
by form looks for *this class* of work. Adapting tests to upstream message changes
is recurring maintenance here - the repository carries dozens of such commits, and a
search by string finds none of them because every one used different words.

What (b) tells you that (a) cannot:

- this is routine maintenance, not a novel finding
- the guard style the repository already settled on
- **where the team centralises these** - often a suite's `helper/errors.py` rather
  than an f-string repeated across call sites. If you are about to edit the same
  literal in four places, check whether a helper already exists for it, and say so
  in the recommendation.

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

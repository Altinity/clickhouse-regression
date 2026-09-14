---
name: ci-job-forensics
description: Extract facts from a CI job - fetch logs (including previous attempts), read huge artifacts without downloading them, identify the runner hardware, bisect a regression on branch runs, and interpret broken_tests.yaml matching.
---

# Skill: CI Job Forensics

## Purpose

Low-level techniques for **extracting a specific fact from a CI job**. This is the
toolbox the triage skills call into; it does not classify failures or write reports.

Use it when you need to answer questions like:
- What was in the log of the *previous* attempt, before the rerun overwrote it?
- Which test actually hung, when the report does not name one?
- What CPU did this runner have?
- Which commit introduced this, when there is no PR to bisect?
- Why is this test not being suppressed by `broken_tests.yaml`?

Sections are ordered by how often they are actually needed.

---

## 1. Getting the Job Log

### From GitHub (works for reruns and previous attempts)

The GitHub API serves the log of the attempt you ask for. The web UI only shows
the latest one, so this is the **only** way to read a failed attempt after a rerun:

```bash
# Current attempt
gh api repos/Altinity/ClickHouse/actions/jobs/<JOB_ID>/logs > job.txt

# List all jobs of a run, with their IDs and conclusions
gh api repos/Altinity/ClickHouse/actions/runs/<RUN_ID>/jobs --paginate \
  --jq '.jobs[] | "\(.id)  \(.conclusion)  \(.name)"'

# Previous attempts of a run
gh api repos/Altinity/ClickHouse/actions/runs/<RUN_ID>/attempts/<N>/jobs --paginate \
  --jq '.jobs[] | "\(.id)  \(.conclusion)  \(.name)"'
```

The job log contains the **shell trace** (`set -x`) of the whole job, which is often
more informative than the test report: it shows the exact docker invocation, the
runner name, and every command that ran before the failure.

### From S3 artifacts

Every artifact URL pattern - the PR-vs-REF path fork, `job.log` vs `job.log.zst`,
job directory naming, S3 listing, and range reads for logs over 100 MB - is in
**`.claude/skills/_shared/ci-urls.md`**. Read it rather than reconstructing a URL from memory.

> **The forensic point:** S3 artifacts are **overwritten on rerun**, so what you
> download belongs to the *latest* attempt even when you are investigating an
> earlier one. The CPU model and server logs you read may describe a different run.
> GitHub job logs are per-attempt and immutable - when the question is about one
> specific attempt, use the API above, not the artifact.

---

## 2. Bisecting Without a PR

Branch runs (nightly, release, `antalya-*`) are recorded with
**`pull_request_number = 0`**. That makes the database a bisect tool: filter to
branch runs only, order by time, and find the first run where a passing test
started failing.

```sql
SELECT check_start_time, commit_sha, check_name, test_status
FROM `gh-data`.checks
WHERE test_name = '<TEST>'
  AND pull_request_number = 0          -- branch runs only, no PR noise
  AND check_start_time > now() - INTERVAL 60 DAY
ORDER BY check_start_time
```

Then take the last-good and first-bad `commit_sha` and list what landed between
them in the local clone:

```bash
cd <clickhouse-clone> && git log --oneline <LAST_GOOD>..<FIRST_BAD>
```

> Needs a local clone of the ClickHouse source. If you do not know where it is,
> **ask the user** - do not guess a path and do not clone one. In that clone,
> `origin` is usually the Altinity fork (its `master` is frozen; work happens on
> release branches) and `upstream` is `ClickHouse/ClickHouse`, so read
> `upstream/master` for "what does upstream have today". Without a clone, fetch the
> commit list from the API instead.

This isolates a regression to a merge window without needing to reproduce it.
It is the fastest path when a test fails on a release branch and no PR is implicated.

Two cautions:
- Filter by `check_name` too, or you will mix build types and see false transitions.
- A test that is simply flaky produces a scattered pattern, not a clean
  before/after boundary. Confirm the boundary is sharp before calling it a regression.

---

## 3. Correlating a Failure with Runner Hardware

Two facts identify the machine a job ran on. Both are worth extracting before
concluding that a failure is "random".

### CPU features

The server prints its detected instruction sets at startup, in
`clickhouse-server.log`:

```bash
curl -s -r 0-300000 "<...>/clickhouse-server.log.zst" | zstd -dc \
  | grep -i "Available CPU instruction sets"
```

This resolved a sanitizer failure that looked random: the discriminator was a
single instruction set (`AVX512VBMI`), which selects a different SIMD codepath in
a vendored library. Note it was **not** the broader family (`AVX512`) — see the
evidence rule below.

### Runner name

Present in the job log header, and it distinguishes standby / ephemeral / static
runners:

```bash
grep -m1 -iE "Runner name|Runner Image|hetzner" job.txt
```

Useful when a failure correlates with a runner class rather than with the code —
for example, integration tests that hang only on dedicated arm64 runners.

### The evidence rule

**Before claiming a correlation, gather between 5 and 15 samples of the failure
and check whether any of them contradicts the hypothesis.** If fewer than 5 exist,
work with what is available — and say explicitly in the write-up how many samples
the claim rests on.

This exists because concluding from 2 samples produced a wrong answer three
separate times in one investigation. With 2 jobs the answer looked like "AVX-512";
with 18 jobs the real discriminator turned out to be `AVX512VBMI`, a narrower
feature that the first answer would have mis-attributed.

Concretely: pull the failing jobs from the database, extract the candidate fact
from each, and tabulate. A hypothesis that survives all samples is reportable; one
that a single sample contradicts is not.

---

## 4. Finding the Test That Actually Hung

When a job dies without naming a culprit (`Server died`, timeout, killed process
group), the test list in the report is incomplete — the hung test never reported a
result. Two ways to recover it:

```bash
# 1. The last test to START in the shell trace is usually the one that hung
grep -nE "^\+ .*(clickhouse-test|pytest)" job.txt | tail -20

# 2. --client_logs_file leaks the query stream of the running test
grep -n "client_logs_file" job.txt | tail
```

The second is the reliable one: the client log keeps flowing until the process is
killed, so its **last** entries belong to the test that was still running.

---

## 5. `broken_tests.yaml` Matching Semantics

Misunderstanding this wastes time, because a wrong entry fails silently — the test
keeps failing and nothing indicates why the suppression did not apply.

- The `message` field is matched against
  **`f"Reason: {result.reason.value} {result.description}"`** — **not** against
  `job.log` and not against the server log. A phrase copied from the job log will
  usually not match.
- Matching is **substring** by default. Set `regex: true` for a pattern; it then
  applies to `name`, `message`, and `not_message`, but never to `reason` or
  `check_types`.
- `check_types` must intersect the job's `build_flags`. The sanitizer flags are the
  short names: `msan`, `tsan`, `asan`, `ubsan` (`BuildFlags.MEMORY = "msan"`).
- Regex rules are evaluated in file order — most specific first.

To verify an entry before committing it, reconstruct the string it will be matched
against from the report's reason and description, and test the pattern against
*that*, not against a log.

---

## 6. Database Column Asymmetry

The Altinity and upstream CI databases are **not** the same schema. Assuming
symmetry costs a round of failed queries:

| Column | `gh-data.checks` (Altinity) | `default.checks` (upstream, play.clickhouse.com) |
|--------|------------------------------|--------------------------------------------------|
| `test_context_raw` | absent | present — full failure text, searchable without downloading logs |
| runner / `instance_type` | absent | present |

`test_context_raw` on the upstream database lets you search for an error signature
directly:

```sql
SELECT check_start_time, check_name, pull_request_number
FROM default.checks
WHERE test_status = 'FAIL'
  AND test_context_raw LIKE '%<ERROR SIGNATURE>%'
  AND check_start_time > now() - INTERVAL 90 DAY
ORDER BY check_start_time
```

For the Altinity database there is no equivalent — the error text must come from
the artifact.

---

## Related Skills

- **`pr-ci-failure-triage`** — categorizing a PR's failures; calls into this skill for facts
- **`upstream-test-investigation`** — deep dive on one upstream test
- **`upstream-ci-database-queries`** — query reference and URL patterns for both databases
- **`regression-test-database-investigation`** — Altinity regression suite results
- **`github-issue-template`** — structure for writing the issue afterwards

---

## Notes

- Prefer the GitHub job log over S3 artifacts when investigating a specific attempt;
  artifacts are mutable, job logs are not.
- `socket.timeout is TimeoutError` in Python 3.10+, so a timeout raised inside
  `clickhouse-test` can be swallowed by an `except socket.timeout` handler. The
  visible symptom is a killed process group **without** the usual
  `Test execution timed out` line — do not rely on that string to find timeouts.
- State sample counts in write-ups. "Failed on 4 of 18 jobs, all sharing X" is a
  claim a reader can check; "it's X" is not.

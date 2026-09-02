---
name: pr-ci-failure-triage
description: Verify a Pull Request's CI before approving it - QA verification, PR verification, CI triage, "check the CI of PR #N", "is this PR green", "did this PR break anything". Analyzes every failing job in a PR and categorizes each failure as a PR-caused regression, a pre-existing flaky test, an infrastructure issue, or a cascade failure, then produces the approval comment.
---

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

All CI report, log and artifact URL patterns live in one place:
**read `.claude/skills/_shared/ci-urls.md`**.

It covers the PR-vs-REF fork (path segment, `name_0`, and `job.log` vs `job.log.zst`),
the CI report and JSON-browser URLs, direct artifact paths and job directory naming,
S3 listing, range reads for large logs, and the rerun-overwrites-artifacts gotcha.

---

## Failure Categories (shared vocabulary)

Every failure gets **exactly one** of these five, spelled as written. Other skills
emit the same five, so their results drop straight into this report with no
translation.

| Category | Means | Blocks approval? |
|----------|-------|------------------|
| `regression` | A change broke it - name the PR, or the merge window | **Yes** |
| `pre-existing-flaky` | Fails at a similar rate before and after | No |
| `infrastructure` | The environment failed, not the code | No |
| `cascade` | A consequence of another failure in the same job | No - classify the root cause instead |
| `unknown` | Not enough evidence to place it yet | **Yes, until resolved** |

Full definitions, the evidence each one requires, and the mechanism axis:
read `.claude/skills/_shared/failure-categories.md`.

`unknown` is not a soft `pre-existing-flaky`. It is the honest answer when evidence
is missing, it blocks approval, and it must say what would resolve it.

---

## Dispatching a Failure to the Right Investigation Skill

Which skill owns a failure is decided by **which table it lives in**, and the name
shape tells you the table with no ambiguity (verified against 57k failure rows):

| Failure name | Table | **Invoke** |
|--------------|-------|------------|
| Starts with `/` (`/swarms/...`, `/lightweight delete/...`) | `gh-data.clickhouse_regression_results` | `regression-test-database-investigation` |
| Anything else - `03340_projections_formatting`, `test_s3_cluster/test.py::test_x`, and job-level names with no test at all (`Server died`, `Unknown error`, `Timeout`, `Cannot start clickhouse-server`) | `gh-data.checks` | `upstream-test-investigation` |

**Invoke the skill - do not reimplement it here.** Reading its name in this table is
not the same as loading it; a skill only takes effect when it is actually invoked.

Pass along: the exact failure name, the check (job) name, the branch or PR, a sample
commit SHA, the run ID, and the database password.

Job-level names that are not tests still belong to `upstream-test-investigation` -
they are rows in the same table, and it has the job-level path for them. They are
not rare: they were **13% of all failures** in a recent 30-day window.

---

## How to Work Through the List

Triage is a **funnel, not a loop.** Do not run a deep investigation per failing
test: a PR with 40 failures would become 40 investigations, and most of them resolve
in bulk from a single query.

Work in this order, and only what survives each stage moves on:

**1. Drop the cascade failures.** Group by job. Where a job shows a server death or
a killed process group, everything after it is `cascade`. Classify the root cause,
list the rest as its consequence. This alone often removes most of the list.

**2. One bulk query for everything that is left.** Ask for the branch baseline of
all remaining tests at once, rather than one query per test:

```sql
SELECT test_name,
       countIf(pull_request_number = 0)                        AS branch_runs,
       countIf(pull_request_number = 0 AND test_status='FAIL')  AS branch_fails,
       countIf(pull_request_number = <THIS_PR>)                 AS pr_runs,
       countIf(pull_request_number = <THIS_PR> AND test_status='FAIL') AS pr_fails
FROM `gh-data`.checks
WHERE test_name IN ('<T1>','<T2>','<T3>')      -- the whole remaining list
  AND check_name = '<EXACT_JOB_NAME>'
  AND check_start_time > now() - INTERVAL 60 DAY
GROUP BY test_name
```

Apply the rate comparison to each row. Anything that fails on the branch at a
comparable rate is `pre-existing-flaky` and needs nothing further.

**3. Sort the obvious infrastructure out by error text.** Docker, DNS, package
install, `Cannot start clickhouse-server`, object-store errors - `infrastructure`,
named mechanism, done.

**4. Only now investigate individually.** What reaches this stage is usually two or
three failures: no branch history, or a rate far above baseline, or an error nobody
recognises. Dispatch each one per the table above, and **invoke** the skill.

**5. Anything still unplaced is `unknown`** - with what would resolve it. Do not
round it up to `pre-existing-flaky` to close the list.

State how many failures each stage removed. "41 failures: 28 cascade behind one
server death, 9 pre-existing flaky, 2 infrastructure, 2 investigated" is a report
someone can audit.

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
| `Server died` | Server process terminated - see *Server died taxonomy* below |
| `Sanitizer assert (in stderr.log)` | Sanitizer detected issue |

### Identifying Root Cause

When cascade failures are present:
1. Find the **earliest failing test** in that job (by timestamp or test order)
2. Check if it's a test with actual assertions, not a meta-check
3. The root cause test typically runs **before** the cascade failures
4. **If the indicator is `Server died`, stop and apply the
   [Server died taxonomy](#server-died-taxonomy) below before going further.** The
   label covers three unrelated causes, and only one of them means a real crash
   happened. Categorizing it without the taxonomy produces a wrong verdict.
5. If no test is named at all (killed process group, job timeout), recover the
   hung test with `ci-job-forensics` section 4 - the report will not name it.

---

## Step 3: Categorize Each Failure

For each unique failing test (excluding cascade indicators), determine category:

### `pre-existing-flaky`

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

### `infrastructure`

**Indicators:**
- Error messages about Docker, networking, timeouts
- `Connection refused`, `Container failed to start`
- Passes on rerun
- Affects unrelated test types

> Before settling on "flaky" or "infrastructure", check whether the failing jobs
> share a machine characteristic the passing ones do not - see
> [Correlating a failure with hardware or runner](#correlating-a-failure-with-hardware-or-runner).
> A failure that looks random across jobs is sometimes deterministic given the CPU
> or the runner class, and that changes both the verdict and the fix.

### `regression`

**Indicators:**
- Test was passing before this PR (**prove this - see below**)
- Failure pattern matches PR changes (e.g., JSON tests fail after JSON-related change)
- Consistent failure on specific build types

#### Proving the test was passing before the PR

"It was passing before" is the claim that turns a failure into a regression, so it
has to be checked, not assumed. Three queries, in order of strength:

**a. How often does it fail on the branch, compared to how often it fails on this
PR?** Branch runs carry `pull_request_number = 0`, so they give the test's normal
behaviour without the PR.

Ask for **how often**, not whether. A test that has failed before can still be
broken by a PR - what matters is whether the PR made it fail much more often:

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

Read the two rates side by side:

| Branch (no PR) | This PR | Reading |
|----------------|---------|---------|
| 5 of 1000 | 10 of 10 | **PR-caused.** Rare before, always now - the difference is not close. |
| 2 of 40 | 8 of 8 | **PR-caused.** Occasional before, consistent now. |
| 120 of 400 | 3 of 8 | **Pre-existing.** Fails at about the same rate either way. |
| 120 of 400 | 1 of 1 | **Probably pre-existing.** A test that fails ~30% of the time is expected to fail sometimes - one failure is what the baseline predicts. Not proof, but nothing points at the PR. |
| 0 of 300 | 1 of 1 | **Not yet decided.** Never fails on the branch, so this one failure is unexplained - get more runs before deciding. |

The rule in words: **a test that already fails sometimes is not automatically
pre-existing.** Compare the rates. If the PR's rate is far above the branch's, the
PR made it worse and it counts as a regression, even though the test has a failure
history. If the two rates are close, it is pre-existing and the PR is not
implicated.

There is no fixed threshold, and none is needed - the cases that matter are not
close calls. When the two rates *are* close, that is itself the answer: you do not
have evidence against the PR.

**Watch the sample size on the PR side.** One or two runs cannot establish a rate,
and that is the common situation on a fresh PR. A test that fails 8 of 8 is strong
evidence; a test that fails 1 of 1 is much weaker - and what it is worth depends on
the branch baseline:

- **Baseline already fails often** - a single failure is what that baseline
  predicts, so it most likely means nothing new. Lean pre-existing, say that the PR
  side has only one run, and move on. Reruns rarely change this verdict.
- **Baseline never fails** - a single failure has no innocent explanation yet.
  This is the case worth spending reruns on: rerun the failing job a few times and
  decide from real numbers rather than from n=1, following the same reasoning as
  the [evidence rule](#evidence-rule).

Either way, write the counts into the report. "Fails 30% of the time on the branch;
1 of 1 on this PR" lets a reader disagree with the verdict; "pre-existing flaky"
does not.

**b. Does it fail in other, unrelated PRs?**

```sql
SELECT pull_request_number, count() AS fails, max(check_start_time) AS last_seen
FROM `gh-data`.checks
WHERE test_name = '<TEST_NAME>'
  AND test_status = 'FAIL'
  AND pull_request_number != <THIS_PR>
  AND check_start_time > now() - INTERVAL 60 DAY
GROUP BY pull_request_number ORDER BY last_seen DESC
```

Failures spread across unrelated PRs point to pre-existing flakiness (`pre-existing-flaky`) -
but apply the same rate comparison: if those other PRs fail occasionally and this
one fails every time, the history does not clear this PR.

**c. Does it fail on this PR's own base commit?** Compare the PR's runs against the
merge-base SHA; if both fail, the PR is not the cause.

**Only if all three point at the PR**, confirm the mechanism: does the diff touch
code the test exercises? A regression claim needs both the timeline *and* a
plausible path from the change to the failure. If the timeline fits but no code
path does, say so explicitly rather than asserting causation.

When the boundary is sharp on the branch timeline but no PR is implicated, bisect
the merge window - `ci-job-forensics` section 2.

---

### `cascade`

Identified in Step 2, not here. Do not classify a cascade failure on its own: find
the failure that caused it, classify that one, and list the cascade failures as its
consequence. A single root cause routinely produces dozens.

### `unknown`

Use it when the evidence does not support any of the others - most often a failure
with no history and only one run, where the rate comparison cannot decide.

State what would resolve it: more runs, the log of a specific attempt, a bisect, or
a local reproduction. `unknown` blocks approval, and that is deliberate - it marks
what still needs a person instead of letting "probably flaky" close the case
silently.

---

## Step 4: Build Type Differences

The build type is evidence. A failure confined to one build type usually names its
own cause.

### Non-sanitizer builds

| Build Type | Behavior |
|------------|----------|
| **Debug** (`amd_debug`) | Assertions enabled, `LOGICAL_ERROR` causes SIGABRT crash |
| **Release** (`amd_binary`, `arm_binary`) | No assertions, errors may be silent or return incorrect data |

### Sanitizer builds

Each sanitizer catches a different defect class and has its own failure signature.
They also run **much slower** than release, which by itself causes timeout failures
that are not bugs.

| Build | Catches | Signature in logs | Slowdown |
|-------|---------|-------------------|----------|
| **asan** | out-of-bounds, use-after-free, leaks | `AddressSanitizer: heap-buffer-overflow`, `LeakSanitizer` | ~2x |
| **tsan** | data races, lock-order inversions | `WARNING: ThreadSanitizer: data race`, `lock-order-inversion` | ~5-15x |
| **msan** | reads of uninitialized memory | `MemorySanitizer: use-of-uninitialized-value` | ~3x |
| **ubsan** | undefined behaviour (overflow, misaligned, bad cast) | `runtime error: signed integer overflow`, `member call on null pointer` | ~1.5x |

### Pattern Recognition

| Observation | Likely Cause |
|-------------|--------------|
| Fails on debug, passes on release | Assertion catches bug that release ignores |
| Fails on release, passes on debug | Performance/timing issue |
| Fails on both | Fundamental bug |
| Fails only on tsan, always a timeout | Slowdown, not a race - check the message before blaming the PR |
| Fails only on tsan, with a `data race` report | Real race; it may well be pre-existing - run the rate comparison before attributing it |
| Fails only on msan | Uninitialized read, **or** a false positive from un-instrumented code |
| Fails only on asan with `LeakSanitizer` | Leak, often in test setup rather than product code |
| Fails on every sanitizer but no release build | Usually resource exhaustion (memory, time), not a code defect |

### Sanitizer false positives

msan reports uninitialized reads only if **all** code is instrumented. Hand-written
assembly, vendored SIMD libraries, and code selected at runtime by CPU feature are
common sources of false positives - and because the codepath depends on the CPU,
the same test passes on some runners and fails on others.

Before treating an msan report as a bug, check whether the failing jobs share a CPU
feature the passing ones lack (`ci-job-forensics` section 3), and whether the
program's actual output is correct despite the report. The [evidence rule](#evidence-rule) applies here: this specific mistake has been made from a 2-job sample.

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

## Step 6: Investigate What Survived the Funnel

Only the failures still unexplained after stages 1-3 of *How to Work Through the
List* reach this step - typically two or three, not the whole list.

For each one, **invoke** the owning skill from *Dispatching a Failure to the Right
Investigation Skill*, passing the failure name, the exact check name, the branch or
PR, a sample SHA, the run ID, and the database password.

The skill returns one of the five shared categories plus a mechanism. Take that
result as given and place it in the report - do not re-derive it here.

If a failure cannot be dispatched because it has no test name, that is expected:
`upstream-test-investigation` owns those too and has the job-level path.

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

## Server died Taxonomy

`Server died` is a **label, not a cause**. Three different things produce it, and
they need different conclusions. Distinguish them before categorizing the failure —
misreading the cause here turns an infrastructure problem into a false regression
report, or hides a real crash.

| Cause | Exit code | How to confirm | Category |
|-------|-----------|----------------|----------|
| Test framework killed the process group on timeout | **143** (SIGTERM) | `Terminated`/`KeyboardInterrupt` in the job log; no stack trace; no sanitizer report | Infrastructure / known upstream instability |
| Server crashed | **2**, or signal | `Fatal` or `Killed by signal` in `clickhouse-server.err.log`; stack trace present | Real bug - investigate |
| Out of memory | varies | OOM killer message in the job log or `dmesg`; memory limit exception before the death | Infrastructure, unless the PR changed memory behaviour |

Three greps separate them:

```bash
grep -cE "Terminated|KeyboardInterrupt"  job.txt   # framework kill
grep -nE "<Fatal>|Killed by signal"      clickhouse-server.err.log
grep -niE "out of memory|oom-kill|Memory limit .* exceeded" job.txt
```

The framework-kill variant comes from `clickhouse-test`'s timeout handler calling
`os.killpg(pgid, SIGTERM)`. Two important consequences:

- Every test still running in that group dies with it, so the reported failures are
  cascade, not independent.
- The handler's exception can be swallowed (`socket.timeout is TimeoutError` in
  Python 3.10+), so **the `Test execution timed out` line is sometimes absent**. Its
  absence does not rule out a timeout — use the exit code and the absence of a
  stack trace instead.

This is a known upstream problem (issue #116243). When the taxonomy lands on the
framework-kill row, the finding is "upstream test instability", and the useful
next step is identifying *which* test hung — see `ci-job-forensics`, section 4.

---

## Correlating a Failure with Hardware or Runner

A failure that looks random across jobs is sometimes deterministic given the
machine. Before filing it as flaky, check whether the failing jobs share something
the passing ones do not:

- **CPU instruction sets** — printed at server startup; selects SIMD codepaths in
  vendored libraries, and has produced sanitizer failures that occur only on
  certain hardware.
- **Runner name / class** — standby vs ephemeral vs dedicated; some failure modes
  are confined to one class.
- **Architecture** — amd vs arm, where a failure on only one is a strong signal.

Commands for extracting each are in `ci-job-forensics`, section 3.

### Evidence rule

**Gather between 5 and 15 samples before claiming a correlation, and check whether
any sample contradicts it.** If fewer than 5 samples exist, proceed with what is
available and state the sample count explicitly in the write-up.

Two samples are not enough to name a cause. In one investigation, 2 jobs pointed at
"AVX-512"; 18 jobs showed the real discriminator was `AVX512VBMI` specifically — a
narrower feature, and the two-sample answer would have been wrong. Small-sample
conclusions have also mis-attributed failures to memory compression and to a race
that did not exist.

Report the count with the claim: "failed on 4 of 18 jobs, all lacking X" is
checkable; "it's X" is not.

---

## Related Skills

- **`ci-job-forensics`** - Extracting facts from a job: logs of previous attempts, huge artifacts, runner hardware, bisect on branch runs
- **`upstream-test-investigation`** - Deep investigation of upstream test (Stateless/Integration/Fuzzer/Stress)
- **`upstream-ci-database-queries`** - CI database query reference (Altinity + upstream)
- **`regression-test-database-investigation`** - Altinity regression test database investigation
- **`github-issue-template`** - Templates for writing GitHub issues after investigation

---

## Notes

- Always check if failures predate the PR before attributing them to PR changes
- Server crashes (SIGABRT) on debug builds often indicate assertion failures
- A single root cause test can cause dozens of cascade failures
- Rerun data may mask original failures in GitHub UI

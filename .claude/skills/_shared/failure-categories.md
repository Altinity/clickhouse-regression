# Shared vocabulary: CI failure categories

This file is the single source of truth for how a CI failure is classified.
Every skill that classifies a failure must emit **exactly one** of these five names,
spelled as written here, so that results from different skills compose into one
report without translation.

This folder is not a skill (it has no `SKILL.md`). It is read by:
`pr-ci-failure-triage`, `upstream-test-investigation`,
`regression-test-database-investigation`, `release-branch-monitor`.

---

## Two contexts, one vocabulary

The same five categories apply whether you are looking at a **pull request** or at a
**branch over time** (MasterCI runs, `pull_request_number = 0`). What differs is only
the unit of blame:

| Context | Question | Unit of blame |
|---------|----------|---------------|
| Pull request | Did this PR break it? | the PR |
| Branch (MasterCI) | What broke it on this branch? | a PR, **or** a merge window |

Do not invent a separate category for "new failure on the branch" - that is
`regression`, with the culprit named as precisely as the evidence allows.

---

## The five categories

| Category | Means | Blocks approval / release? |
|----------|-------|----------------------------|
| `regression` | A change broke it | **Yes** |
| `pre-existing-flaky` | Fails at a similar rate before and after | No |
| `infrastructure` | The environment failed, not the code | No, but must be fixed if persistent |
| `cascade` | A consequence of another failure in the same job | No - classify the root cause instead |
| `unknown` | Not enough evidence to place it yet | **Yes, until resolved** |

---

## What each one requires

### `regression`

Two things must both hold:

1. **Rate.** The failure rate after the suspected change is far above the rate
   before it. Compare, do not ask yes/no - a test that already failed sometimes can
   still be broken by a change. See the rate-comparison table in
   `pr-ci-failure-triage`.
2. **Mechanism.** A change in the window touches code the test exercises.

If only the rate fits and no code path does, say so and use `unknown`. A timeline
alone is correlation, not cause.

**Name the culprit as precisely as the evidence allows**, and no further:

- **A specific PR** - when the test failed on that PR's own CI, or when only one
  change in the window can plausibly reach the failing code.
- **A merge window** - "broke between `<last good SHA>` and `<first bad SHA>`,
  N commits". This is a complete answer, not a partial one. Report the window and
  the candidate PRs in it.

> **A PR often cannot be pinned, and the reason is structural.** The set of jobs a
> pull request runs is **chosen per PR** - it may match MasterCI or be much smaller.
> MasterCI always runs the full set. So when a test fails only under msan (or any
> job a PR may skip), that PR may simply never have run it.
>
> This makes **a missing row ambiguous**: no result for a PR does not mean the test
> passed there, it may mean the job never ran. Check whether the job ran at all
> before reading anything into its absence. If it did not, the merge window is the
> best available answer and no amount of querying will improve on it.
>
> Narrowing a window further requires reading the diffs in it and reasoning about
> which one reaches the failing code, or building and reproducing at candidate
> commits. Say which of these you did.

### `pre-existing-flaky`

The failure rate is about the same before and after the suspected change. Evidence:
it fails on branch runs (`pull_request_number = 0`) across earlier runs too, or
across unrelated PRs, at a comparable rate.

Not established by "it has failed before". A test with a 0.5% history that now
fails 10 of 10 is `regression`, not this.

### `infrastructure`

The environment failed: docker, network, DNS, disk, package install, runner, object
store, a missing tool in the image. Signals: `Connection refused`, container start
failure, `Cannot start clickhouse-server`, package-manager errors, unrelated test
types failing at the same time.

A killed process group after a timeout also belongs here when the timeout came from
the harness rather than from the product - see the Server died taxonomy.

**Infrastructure breakage is not always transient.** "Passes on rerun" confirms this
category but its absence does not rule it out: a broken runner image or a changed
dependency fails every run, forever, and looks exactly like a code regression on a
branch timeline. When a failure starts at a sharp boundary and never recovers, check
whether anything in the environment changed at that boundary - image tag, base
image, runner class - before concluding the code broke.

Say **which** part of the environment failed. "Infrastructure" without a named
mechanism is a guess.

### `cascade`

The failure is downstream of something else that already failed in the same job -
typically the server died and every later test failed with it.

Do not classify a cascade failure on its own. Find the root cause failure, classify
**that**, and list the cascade ones as its consequence.

### `unknown`

The honest category. Use it when evidence is missing, not as a soft version of
`pre-existing-flaky`.

Whenever it is used, state **what would resolve it** - usually one of:
- more runs (a 1-of-1 failure is not a rate)
- the log of a specific attempt
- a bisect over a merge window
- reproducing locally at a candidate commit

`unknown` blocks approval. That is the point: it marks the failures that still
need a person, and prevents "probably flaky" from doing that job silently.

---

## Mechanism is a separate axis

These are **not** categories. They describe *how* a failure happens, and any of
them can attach to any category above:

- assertion in a debug build catching something release ignores
- data race reported by tsan
- uninitialized read reported by msan (possibly a false positive)
- sanitizer slowdown causing a timeout
- version-specific behaviour
- hardware-dependent codepath (CPU features, architecture)
- resource exhaustion (memory, disk, ports)
- job or shard instability: the same job fails every run with **different** test
  names each time - points at the job, not at any of the tests

Report the mechanism alongside the category, never instead of it.
"`pre-existing-flaky`, sanitizer slowdown under tsan" is a complete answer.

---

## Evidence bar

State the counts behind every classification. "Fails 30% of the time on the branch;
1 of 1 on this PR" is checkable; "pre-existing flaky" is not.

Before claiming a correlation, gather **between 5 and 15 samples** and check whether
any contradicts it. If fewer than 5 exist, use what is available and say how many
the claim rests on.

---

## Replaces these older names

| Old name (where it appeared) | Use instead |
|------------------------------|-------------|
| "PR-caused regression" / "Regression (Likely)" | `regression`, culprit named |
| "Flaky (Likely)" / "definitive flaky test" | `pre-existing-flaky` |
| "New / Unknown" | `unknown` |
| "Potential regression" | `regression`, or `unknown` if unproven |
| "transient infra" | `infrastructure` (transient is a property, not a category) |
| "Job/shard instability" | a mechanism, plus the right category |
| "Assertion catching silent bug" | a mechanism, not a category |
| "Version-specific regression" | a mechanism, plus the right category |

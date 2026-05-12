---
name: release-branch-monitor
description: Monitor MasterCI failures on a release branch (e.g. antalya-26.1) by cross-referencing the last N CI run reports. Use when the user asks to "check failing tests on branch X", "monitor a release branch", "see which tests are flaky on antalya-XX.X before release", or wants to know which failures are consistent vs flaky vs isolated across recent MasterCI runs.
---

# Skill: Release Branch Monitor

## Purpose

Before an Altinity ClickHouse release is cut from a release branch (e.g. `antalya-26.1`), the user needs to know which tests are failing in MasterCI and whether each failure is:

- **CONSISTENT** (failed in all analyzed runs) → likely a real bug or a job that needs fixing/xfail before release
- **FLAKY** (failed in some runs but not all) → monitor; may need xfail
- **ISOLATED** (failed once) → register for comparison with next run, no immediate action

MasterCI runs after every PR merged to a release branch. The last successful run typically becomes the release candidate, so its report is shipped to customers — making this monitoring critical.

This skill produces a markdown report cross-referencing failures across the last N MasterCI runs.

---

## Inputs

The user provides a **branch name** (required) and optionally **how many runs** to compare (default: 3).

Examples of phrasing to handle:
- "check failing tests on antalya-26.1"
- "monitor antalya-25.8 over the last 5 runs"
- "any consistent failures on antalya-26.1?"

If the user does not specify the branch, ask. If they don't specify N, use 3.

---

## Workflow

Track progress with this checklist:

```
- [ ] Step 1: Fetch the latest N MasterCI runs for the branch
- [ ] Step 2: Build the report URL for each run and parse the failures
- [ ] Step 3: Cross-reference and render the markdown report
- [ ] Step 4: Present findings to the user
- [ ] Step 5: Offer to investigate individual failures via the appropriate skill
```

### Step 1 — Fetch the latest N MasterCI runs

Use the helper script (requires `gh` authenticated to `Altinity/ClickHouse`):

```bash
.claude/skills/release-branch-monitor/scripts/fetch_runs.sh <branch> [N]
```

Output is TSV: `run_id<TAB>sha<TAB>created_at<TAB>conclusion<TAB>title`.

The first line is the most recent run.

**Skip in-progress runs** if their report does not yet exist (see Step 2). If the most recent run is `in_progress`, mention it but use the next N completed runs.

### Step 2 — Build the report URL and parse each run

For each run, the report URL follows this pattern:

```
https://s3.amazonaws.com/altinity-build-artifacts/REFs/<BRANCH>/<SHA>/<RUN_ID>/ci_run_report.html
```

Verify with `curl -sI -o /dev/null -w "%{http_code}\n" <URL>` — if 404, the run hasn't published its report yet and should be skipped.

Then parse each report:

```bash
.claude/skills/release-branch-monitor/scripts/parse_report.py <REPORT_URL>
```

This emits JSON for five sections of the report:

- `checks_errors` — `Checks Errors` table (job-level errors, e.g. timeouts, plus rows where a specific test caused the error)
- `checks_new_fails` — `Checks New Fails` table (new test failures vs known-fail baseline)
- `regression_new_fails` — `Regression New Fails` table (Altinity TestFlows regression suites)
- `cve_section_title` + `cve_high_critical` — `Docker Images CVEs` heading text (e.g. `Docker Images CVEs (0 high/critical)`) plus rows whose Severity is High or Critical
- `ci_jobs_failed` — `CI Jobs Status` rows whose status is `error` or `failure` (used as a sanity check to confirm nothing is missed by the other sections)

### Step 3 — Cross-reference and render the report

Use the cross-reference script to produce the markdown directly:

```bash
.claude/skills/release-branch-monitor/scripts/cross_reference.py \
    <branch> \
    1:<run_id_1>:<sha_1>:<report_url_1> \
    2:<run_id_2>:<sha_2>:<report_url_2> \
    3:<run_id_3>:<sha_3>:<report_url_3>
```

The first positional after `<branch>` is run #1 (most recent), and so on. The script:
- aggregates failing **jobs** from `Checks Errors` and `Checks New Fails`
- finds **specific tests** (by `(job_name, test_name)`) that fail in ≥2 runs
- aggregates **regression** failures by `(arch, job_name, test_name)`
- classifies each row as CONSISTENT / FLAKY / isolated
- reports any **High/Critical Docker Image CVE** per run (the `(0 high/critical)` summary in the section title is shown for context)
- runs a **`CI Jobs Status` sanity check**: every job marked `error`/`failure` in `CI Jobs Status` should also appear in one of the other sections; anything uncovered is flagged in its own table

### Step 4 — Present findings

Forward the script's markdown output to the user as-is, then add a short plain-text recommendation paragraph if any CONSISTENT failures exist (e.g. "Investigate <job/test> before release; if it's a known flaky test, consider xfailing it").

### Step 5 — Offer to investigate individual failures

After presenting the report, **always ask the user** if they want to investigate any of the failures individually. Example prompt:

> "Want me to investigate any of these failures individually? I can dig into any of the CONSISTENT/FLAKY items, or any other row of interest."

If the user says yes (or names a specific failure), **do not investigate inside this skill**. Instead, route to the appropriate investigation skill below, passing the context already collected (branch, sample commit SHA, run ID, full test/job name, report URL).

This skill stays focused on monitoring; investigation lives in dedicated skills.

---

## Routing failures to investigation skills

Pick the skill based on the row type in the cross-reference report:

| Failure row in report | Skill to use | Key inputs to pass |
|---|---|---|
| Job-level error in `Checks Errors` (no test name; e.g. `Timeout`, `Internal error in pytest or a plugin`) | `upstream-test-investigation` (job-level path: read `job.log`) + `upstream-ci-database-queries` for distribution across branches | job name, branch, sample commit SHA, run ID, **CI database password** |
| Specific test failure in `Checks Errors` / `Checks New Fails` (Stateless `NNNNN_*` or Integration `test_*/test.py::test_*`) | `upstream-test-investigation` | full test name, check (job) name, branch, sample SHA, password |
| Row in `Regression New Fails` (TestFlows: `/swarms/...`, `/ldap/authentication`, etc.) | `regression-test-database-investigation` | scenario path, suite (job_name), arch, branch |
| Row in `CI Jobs Status — sanity check` (uncovered failing job) | `upstream-test-investigation` (logs-first path: there are no per-test rows in the DB) | job name, branch, sample SHA, run ID |
| High/Critical CVE row in `Docker Images CVEs` | No dedicated skill yet — investigate manually (CVE database + Dockerfile diff), then file an issue using `github-issue-template` | image tag, CVE id, severity |

When the database password is needed, ask the user — never assume one. The `upstream-ci-database-queries` skill documents the connection details.

After each investigation, also recommend that the user file a tracking issue with `github-issue-template` if the failure is real (not a known flaky test).

---

## Output format

The report has these sections (in this order):

1. **Runs analyzed** — table with run id, commit, conclusion
2. **Failing jobs across runs (Checks Errors + Checks New Fails)** — every job that errored/failed in any run, with X/- markers per run and a verdict
3. **Specific tests failing in >=2 runs (Checks)** — only tests that repeated; if none, note that the same job failing with different tests usually means shard instability rather than a single test regression
4. **Regression New Fails across runs** — same shape as #2 but for TestFlows regression
5. **Docker Images CVEs (high/critical)** — one row per run with the section title (`(N high/critical)`) and any High/Critical CVEs listed
6. **CI Jobs Status — sanity check** — confirms every failing job in `CI Jobs Status` is covered by sections 2/4 above; lists any uncovered jobs per run
7. **Executive summary** — bulleted lists of CONSISTENT, FLAKY, and High/Critical-CVE items, with action recommendation

---

## Interpretation guide

| Pattern | Likely meaning |
|---|---|
| Same job fails 3/3 with **different test names** each run | Job/shard instability (timeout, infra), not a single test bug |
| Same job + same test fails 3/3 | Real regression or definitive flaky test → investigate or xfail |
| Same regression scenario (e.g. `swarms/.../initiator out of disk space`) fails on **both** x86_64 and aarch64 in all runs | Strong signal of a real bug, not arch-specific flakiness |
| Job `error` (no test name) consistently | Often a timeout or runner-level error — check the job's `json.html` |
| One run has many failures and the next two are clean | Likely transient infra; record for comparison but don't block release |

---

## Edge cases

- **Branch has fewer than N runs** — analyze whatever exists and note the count.
- **Most recent run is in_progress** — mention it (with link), then analyze the next N completed runs.
- **Report 404** — the run finished but artifacts were not uploaded; skip with a note.
- **Branch not found** — `fetch_runs.sh` returns no rows; tell the user the branch has no MasterCI runs on `Altinity/ClickHouse`.

---

## Dependencies

- `gh` CLI authenticated against `Altinity/ClickHouse`
- `python3` (stdlib only — no extra packages required)
- `curl`

---

## Related skills

This skill **monitors** failures; it deliberately does not investigate them. For root-cause analysis, route to:

- **`upstream-test-investigation`** — drill into a specific Stateless/Integration test failure or a job-level error from `Checks Errors` / sanity-check uncovered jobs. Required for: timeouts, server crashes, pytest internal errors, single-test failures.
- **`upstream-ci-database-queries`** — query reference used by the investigation skill (Altinity CI DB at `github-checks.internal.tenant-a.staging.altinity.cloud`, upstream at `play.clickhouse.com`). Needs database password from the user.
- **`regression-test-database-investigation`** — drill into a TestFlows regression scenario (rows in `Regression New Fails`) to decide flaky vs real bug.
- **`pr-ci-failure-triage`** — sibling skill for single-PR analysis (this one is for a branch over time).
- **`github-issue-template`** — file a tracking issue once a CONSISTENT failure is confirmed as a real bug.

# Skill: GitHub Issue Writing

## Purpose

Write well-formatted GitHub issues for the Altinity ClickHouse repository following team conventions.
Covers bug reports for regressions, upstream bugs, and flaky test tracking.

---

## Repository

- **Altinity repo:** `Altinity/ClickHouse` — for Altinity-specific issues
- **Upstream repo:** `ClickHouse/ClickHouse` — for upstream bugs (only if no existing issue found)

---

## Issue Template: Bug Report

Use this template for all bug reports. Adapt sections as needed based on the bug type.

```markdown
✅ *I checked [the Altinity Stable Builds lifecycle table](https://docs.altinity.com/altinitystablebuilds/#altinity-stable-builds-life-cycle-table), and the Altinity Stable Build version I'm using is still supported.*

## Type of problem
**Bug report** - something's broken

## Describe the situation
<1-3 paragraphs explaining:>
<- What the bug is>
<- When/how it was discovered (CI job, manual testing, customer report)>
<- Impact: crash, wrong results, error message, etc.>

This issue:
- <key fact 1, e.g., "Causes SIGABRT on debug/sanitizer builds">
- <key fact 2, e.g., "Returns error code 1001 on release builds">
- <key fact 3, e.g., "Is a pre-existing upstream bug dating back to July 2024">

---

## How to reproduce the behavior

### Environment
- **Version:** <exact version string>
- **Build type:** <release / debug / sanitizer>

### Steps

1. <step 1>

```sql
<SQL or commands for step 1>
```

2. <step 2>

```sql
<SQL or commands for step 2>
```

3. <step 3>

```sql
<SQL or commands for step 3>
```

---

## Expected behavior
<What should happen>

---

## Actual behavior

### On release builds
<Error message or wrong output>

```
<exact error output>
```

### On debug/sanitizer builds (if applicable)
<SIGABRT / crash details>

```
<stack trace, trimmed to relevant frames>
```

---

## Root cause analysis
<Technical explanation of why the bug occurs.>
<Include: which code paths are involved, what conditions trigger it.>

---

## Additional context

### CI failure
- **Job:** <job name>
- **Branch:** <branch>
- **Commit:** `<sha>`
- **CI report:** [ci_run_report.html](<url>)
- **Logs:** [json.html](<url>)

### <Other relevant sections>
<Related PRs, upstream history, workarounds, etc.>
```

---

## Section Guidelines

### Describe the situation
- Lead with what's broken, not how you found it
- State the severity: crash vs error vs wrong results
- If it's an upstream bug, say so explicitly and mention since when

### How to reproduce
- Minimal steps — remove anything not needed to trigger the bug
- Include exact SQL queries and settings
- For fuzzer-found bugs: extract the crashing query from `fatal.log` and the required settings from the `Changed settings:` line

### Expected vs Actual behavior
- Be specific: "should return 3 rows" not "should work"
- For crashes: show both release behavior (error message) and debug behavior (SIGABRT + stack trace)

### Root cause analysis
- Optional but highly valued by the team
- Reference specific source files and functions if known
- If from stack trace analysis, include the key frames

### Additional context
- Always include CI links
- For upstream bugs: include the upstream CI history (query results from `play.clickhouse.com`)
- For regressions: reference the PR that introduced the change
- For flaky tests: include fail rate and time range

---

## Bug Type Variations

### Upstream Bug (not Altinity-specific)

Add to "Describe the situation":
```markdown
- Is a **pre-existing upstream bug** — present in the upstream ClickHouse CI since **<date>** with <N>+ occurrences
- Was detected in **Altinity Stable Build <version>** via the <job name> CI job
- No existing GitHub issue was found upstream tracking this failure
```

Add "Upstream CI history" subsection under Additional context:
```markdown
### Upstream CI history

| Month | Upstream CI hits |
|-------|-----------------|
| <month> | <count> |
| ... | ... |
```

### Regression from Specific PR

Add to Additional context:
```markdown
### Related PR
- PR #<NUMBER>: <title> — introduced the change that caused this regression
```

### Flaky Test

Add to Additional context:
```markdown
### Flakiness data
- **Fail rate:** <X>% over the last 30 days
- **Affected build types:** <list>
- **First seen:** <date>
- **Pattern:** <consistent error vs varying>
```

---

## Creating the Issue

```bash
gh issue create --repo Altinity/ClickHouse \
  --title "<concise title>" \
  --label "bug" \
  --body "$(cat <<'EOF'
<issue body here>
EOF
)"
```

Common labels: `bug`, `stable`, `antalya`, `antalya-25.8`, `25.8`, `25.8.16`

---

## Reference Issues

Good examples of well-formatted issues in the Altinity repo:
- [#1412](https://github.com/Altinity/ClickHouse/issues/1412) — Regression with full reproduction, root cause, and workaround
- [#1437](https://github.com/Altinity/ClickHouse/issues/1437) — Bug with suggested fix in the issue body

---

## Related Skills

- **`pr-ci-failure-triage.md`** — Identifies which failures need issues filed
- **`upstream-test-investigation.md`** — Gathers the data needed for the issue body
- **`upstream-ci-database-queries.md`** — Provides upstream CI history for cross-referencing

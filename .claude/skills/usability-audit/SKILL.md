---
name: usability-audit
description: Perform a usability audit of a feature, PR, or test suite from the user/operator's point of view and produce a clean list of issues they may face in normal flow, failure modes, cancellation, retries, concurrent admin actions, diagnostics, and at scale. Use when the user asks for a usability audit, user-journey trace, operator experience review, or wants a report of issues an operator may hit when using a feature. Also use proactively after completing a feature or PR audit to append an operational readiness section.
---

# Usability Audit

## Purpose

Audit a feature, PR, or test suite from the end user's (usually the operator's) point of view and produce a **clean list of issues** the user may face. The output is a report, not a narrative.

The report has three parts and nothing else:

1. **Scope and persona** — one short paragraph.
2. **Issues** — a numbered list. Each issue is one concrete problem the user may hit.
3. **Readiness verdict and operator guidance** — short, actionable.

No filler, no narrative, no restating the code.

---

## When to use this skill

- The user asks for a usability audit, user-journey trace, operator experience review, or "what issues will the user face?".
- A correctness / code audit has just been completed and an operational readiness section should be appended.
- A new feature, command, or setting is being tested and its operator experience needs to be assessed (not just SQL correctness).

Run in addition to, not instead of, a correctness review.

---

## Personas

Pick one persona before auditing. Default is **Operator / DBA** for server-side ClickHouse features. Alternatives: **application developer**, **test / CI author**, **end user of a client app**. State the persona at the top.

---

## Always audit against the original source

Never audit from memory, from the PR description alone, or from summaries. The audit must be grounded in the real code the user runs.

**Before producing any issue, confirm you are reading the right source:**

1. Identify the exact code under audit: repository, branch or tag, PR number, and commit SHA if available.
2. Read the relevant files directly (server source, test code, config, scripts). Do not paraphrase — cite file paths.
3. If the code is not locally available, **stop and ask the user** which of the following to do before continuing:
   - Checkout the branch or PR locally (`git fetch && git checkout <branch>` or `gh pr checkout <N>`).
   - Clone the repository if it is not in the workspace.
   - Use the Cursor CLI / `gh` to fetch the needed files or PR diff.
4. If the scope spans multiple repos (e.g. `Altinity/ClickHouse` server + `Altinity/clickhouse-regression` tests), confirm the branch / commit for each.
5. When an issue is sourced from a specific file, cite `path:line` in Symptom or Trigger. When sourced from a PR, cite `#<PR> @ <sha>`.

If the user refuses to provide source access, state clearly at the top of the report:
*"Audit performed without direct source access; findings are based on <PR description / docs / prior audit> and may be incomplete."*
Do not silently proceed.

---

## Audit workflow

**First, identify the primary flows — the normal paths that real users will run most often. Everything else follows from this list.** Audit priority is set by which paths are heavily used: a minor annoyance in the top flow outweighs a severe issue in a rarely-used edge path.

Track progress:

```
- [ ] 1. Confirm source access (repo, branch/PR, commit). If missing, ask the user to checkout / clone / fetch before proceeding.
- [ ] 2. Identify the primary (heavily-used) flows. Rank them by expected usage frequency. Everything after this step is prioritized by this ranking.
- [ ] 3. State scope (feature, PR, branch, env assumptions) and persona
- [ ] 4. Enumerate user actions inside the primary flows: commands, settings, observed system tables, admin ops that may race
- [ ] 5. Walk each primary flow end-to-end and record every friction / ambiguity / unclear signal as an issue
- [ ] 6. Walk failure, cancellation, retry, concurrency, and scale variations of the primary flows using the prompt list below, and record each as an issue
- [ ] 7. For each issue: symptom, trigger, signal quality, severity, recovery (cite file:line or PR@sha); note which primary flow it affects
- [ ] 8. Write the readiness verdict, grouped by primary flow
- [ ] 9. Write operator guidance / workarounds
- [ ] 10. (Optional) Append to the existing audit doc as "Operational Readiness"
```

### How to identify primary flows (step 2)

Before producing any issue, list the normal paths real users will actually run most of the time. Infer from:

- Documented / advertised use cases in the feature's docs or PR description.
- Default settings — the flow a user gets without changing anything is almost always a primary flow.
- Existing tests marked as smoke / sanity / basic — these encode what the team considers the core path.
- The "obvious" SQL the user would write given only the feature name (e.g. for `EXPORT PARTITION` → "export one partition to Iceberg with defaults").

Produce a short ranked list (usually 2–5 flows) per feature. Examples across different feature types:

**Export Partition to Iceberg** (`s3/requirements/export_partition.md`, `iceberg/`):
1. Export one partition to Iceberg with `export_merge_tree_partition_async = 1`, single replica, default settings. *(most common)*
2. Export with `async = 0` (synchronous) for small tables.
3. Export during a running merge / mutation on the source.

**Export Part to S3** (`s3/requirements/export_part.md`):
1. `ALTER TABLE t EXPORT PART '<name>' TO <s3_table>` on a MergeTree with default storage policy. *(most common)*
2. Export every part of a partition sequentially via a loop / script.
3. Export from a table whose parts sit on multiple disks (TTL moves, tiered storage).
4. Export parts from a table with alias / materialized / default / JSON columns.

**Swarm cluster query execution** (`swarms/requirements/requirements.md`, SRS-044):
1. `SELECT` against an object-storage table function (e.g. `s3(...)`) with swarm cluster discovery enabled and default `object_storage_max_nodes`. *(most common)*
2. Same query while swarm nodes register / deregister (scale-up, scale-down).
3. Query with `object_storage_max_nodes` set to a specific non-default value.
4. Query while a swarm node fails or exhibits high latency (retry path).

**Hybrid table engine** (`ice/requirements/hybrid.md`):
1. `CREATE TABLE ... ENGINE = Hybrid(src1, date < watermark, src2, date >= watermark)` then `SELECT` across both sources, used for gradual migration. *(most common)*
2. `INSERT` into the Hybrid table (writes routed to the first source).
3. Hybrid over an S3-backed source plus a local MergeTree for tiered storage.
4. JOIN / aggregation on the Hybrid table leveraging Distributed optimisations (`skip_unused_shards`, global JOIN pushdown).

**Iceberg engine read** (`iceberg/requirements/requirements.md`, `iceberg/tests/iceberg_engine/`):
1. `SELECT` from an `Iceberg` engine table pointed at an S3 warehouse via a REST catalog, default settings. *(most common)*
2. `SELECT` while upstream writers commit new snapshots concurrently.
3. `SELECT` from an Iceberg v2 table with row-level deletes.
4. `SELECT` after schema evolution on the upstream table (column added, dropped, renamed).

If you cannot identify the primary flows from the source or existing requirements doc, **ask the user** which flows they consider primary before continuing. Do not invent them.

### Prompt list (use to find issues — do not put this list in the report)

**Normal flow**
- Ambiguous status values, unclear terminal state, missing progress signal.
- Settings that silently change semantics.
- Output / result shape surprises.

**State and lifecycle**
- Non-terminal states that can loop forever.
- Per-subtask state inconsistent with overall state.
- Missing terminal status for known failure modes.
- Retries that do not terminalize — retried work neither makes progress nor fails cleanly.

**Cancellation**
- Kill / cancel races with completion.
- Kill appears to succeed but final status ends as success.
- No way to cancel at all.

**Retries, force, re-runs**
- Force / retry while previous attempt is in flight → duplication, divergence, corruption.
- No idempotency or fencing.

**Concurrency and admin actions**
- Destination renamed / dropped / altered mid-op.
- Source detached / merged / mutated mid-op.
- Replica failover, network blip, Keeper partition, leader change.

**Diagnostics and observability**
- Errors that do not identify which part / replica / step failed.
- Warnings-only failure loops with no terminal state.
- Operator cannot distinguish "still working" from "stuck".
- Logs and `system.*` tables disagree.

**Correctness hazards surfaced to the user**
- Commit / cleanup / publish windows where partial state leaks.
- Post-publish / post-commit cleanup that can corrupt already-published state under exception timing.
- Counter narrowing, off-by-one, lost-ACK / missed-ACK paths.
- Snapshot / metadata corruption under specific timing.

**Scale**
- UX degrades at 10x / 100x parts, replicas, partitions.
- Per-item diagnostics become unusable at scale.

---

## Output template

Use this exact structure. Do not add sections.

```markdown
# Usability Audit: <feature / PR title>

**Scope:** <feature, PR #, branch, or test suite>
**Persona:** <operator / app developer / test author>
**Environment:** <single-node / replicated / cloud / destination system / etc.>

## Primary flows (ranked by expected usage)
1. <flow description — command + key settings + env assumptions>
2. <flow description>
3. <flow description>

## Issues

Issues are grouped by the primary flow they affect. Within each group, order by severity (blocker → low).

### Flow 1: <short name>

#### 1.1 <Short, specific title>
- **Symptom:** <what the user sees> (`<path:line>` or `#<PR> @ <sha>`)
- **Trigger:** <what conditions cause it — normal, failure, concurrency, scale, …>
- **Signal quality:** <clear | confusing | silent>
- **Severity:** <blocker | high | medium | low>
- **Recovery:** <self-service | runbook | engineer required>

#### 1.2 <Short, specific title>
- …

### Flow 2: <short name>

#### 2.1 <Short, specific title>
- …

### Cross-flow issues (apply to all primary flows)

#### X.1 <Short, specific title>
- …

## Readiness verdict
- **Flow 1 (<name>) in isolation:** <ready | ready with caveats | not ready>, because <issue numbers>.
- **Flow 2 (<name>) in isolation:** <ready | ready with caveats | not ready>, because <issue numbers>.
- **Overall in production (network blips, concurrent admin ops, scale):** <ready | ready with caveats (guardrails required) | not ready>, because <issue numbers>.

It is normal for individual flows to be ready in isolation while the overall production verdict is "ready with caveats (guardrails required)". In that case, the Operator guidance section below defines the required guardrails.

## Operator guidance (until fixes land)
- <concrete workaround / guardrail 1, tied to issue #N>
- <concrete workaround / guardrail 2, tied to issue #N>
- <maintenance-window or timing guardrail, tied to issue #N>
- <runbook to validate status consistency before declaring done, tied to issue #N>

## Recommended fixes
- <fix 1, tied to issue #N>
- <fix 2, tied to issue #N>
```

### Common guardrail patterns for operator guidance

When writing the Operator guidance section, consider these recurring patterns:

- **Avoid mutually unsafe combinations.** Name the combination explicitly (e.g. *"do not run `force_<op>` while any prior `<op>` for the same key may be in commit phase"*).
- **Treat long-running non-terminal state as suspect.** Alert and intervene early rather than waiting indefinitely.
- **Prefer maintenance windows** around destination rename/drop/alter and source detach/drop/mutate operations.
- **Validate multi-level state before declaring done.** If the feature exposes both an overall status and per-subtask state (e.g. `system.*` + ZK/Keeper paths), require operators to check both.

---

## Style rules

- Every issue must be something the **user** observes or suffers — not an internal code smell.
- One issue per entry. Do not bundle unrelated problems.
- Titles are specific: *"Kill appears successful but export still completes"*, not *"Kill bug"*.
- Prefer concrete names: exact status values, system tables, settings, error messages.
- If a failure is speculative, mark severity `low` and say *(unconfirmed)* in Symptom.
- If observed in a test or CI, cite the test path or PR number in Symptom.
- Every issue must be traceable to a file, commit, or PR you actually read. No findings from memory or summaries.
- Every issue must be tagged to a primary flow (or marked cross-flow). Issues that do not affect any primary flow are out of scope.
- Target length: 1–2 pages. If it is longer, it is padded.
- Do not include the prompt list, the workflow checklist, or this skill's framing in the report.
- No emojis unless the user asked for them.

---

## Anti-patterns

- Narrative walk-through of the normal flow. The normal flow only appears in the report as issues it surfaces.
- Restating the implementation or the test plan.
- Vague severities. Pick one: blocker / high / medium / low.
- Verdicts without reasons. Every verdict line must name issue numbers.
- Mixing developer-facing concerns (code structure, refactor ideas) with user-facing issues.
- Auditing from a PR description, changelog, or prior summary without reading the source. If you don't have the code, ask the user to checkout / clone / fetch it first.
- Starting the audit without ranking the primary flows. Edge-case issues in rarely-used paths must not outrank friction in the top flow.

---

## Appending to an existing audit doc

If an audit document already exists (for example `AUDIT_PR_<N>.md`), append a new top-level section titled **`## Operational Readiness`** containing the Issues / Verdict / Operator guidance / Recommended fixes structure. Do not duplicate items already covered by the correctness audit — reference them by section.

---

## Example (condensed)

```markdown
# Usability Audit: EXPORT PARTITION async to Iceberg (PR #1618)

**Scope:** `ALTER TABLE ... EXPORT PARTITION ... TO ... SETTINGS export_merge_tree_partition_async = 1` @ PR #1618
**Persona:** Operator / DBA
**Environment:** Replicated MergeTree, Keeper, Iceberg destination.

## Primary flows (ranked by expected usage)
1. Export one partition to Iceberg with `async=1` on a replicated table with default settings. *(most common)*
2. Export during normal merge / mutation churn on the source table.
3. Cancel an in-flight export with `KILL EXPORT PARTITION`.

## Issues

### Flow 1: Default async export

#### 1.1 Export can loop forever in PENDING with warnings only
- **Symptom:** Task stays `PENDING` in `system.replicated_partition_exports`; only warnings in the log (`#1618 @ <sha>`).
- **Trigger:** Missing part, missing destination, or commit precondition no-op.
- **Signal quality:** Silent (no terminal state).
- **Severity:** High.
- **Recovery:** Engineer required.

#### 1.2 force_export during commit duplicates Iceberg data
- **Symptom:** Two Iceberg transactions commit the same logical data.
- **Trigger:** `force_export` while a prior attempt is in the commit phase.
- **Signal quality:** Silent.
- **Severity:** Blocker.
- **Recovery:** Iceberg-side cleanup.

### Flow 3: Cancel in-flight export

#### 3.1 KILL EXPORT PARTITION can race with completion
- **Symptom:** `KILL` reports success; final status becomes `COMPLETED`.
- **Trigger:** Kill issued during commit phase.
- **Signal quality:** Confusing.
- **Severity:** High.
- **Recovery:** Operator must verify both kill result and final status.

### Cross-flow issues

#### X.1 Export status and per-part status disagree
- **Symptom:** Overall status `FAILED` while `processing/<part>` is still `PENDING` in ZK.
- **Trigger:** Export-level failure before per-part terminalization.
- **Signal quality:** Confusing.
- **Severity:** Medium.
- **Recovery:** Operator must read both views.

## Readiness verdict
- **Flow 1 (default async export) in isolation:** ready with caveats; normal flow completes and lands in Iceberg, but exposed to #1.1 and #1.2 under real failure modes.
- **Flow 2 (export during merges) in isolation:** ready with caveats; no flow-specific blockers, affected by X.1.
- **Flow 3 (cancel) in isolation:** not ready, because of #3.1 (kill race).
- **Overall in production (network blips, concurrent admin ops, scale):** not ready; not yet safe for broad production use without guardrails, because of #1.1 (non-terminal PENDING), #1.2 (force-export duplication), and #3.1 (kill race).

## Operator guidance (until fixes land)
- Do not use `force_export` while any export for the same key may be in commit phase (#1.2).
- Treat long-running `PENDING` as suspect; alert and intervene early (#1.1).
- After `KILL`, verify final export status before declaring cancellation (#3.1).
- Prefer explicit maintenance windows around destination rename/drop and source detach/drop; avoid concurrent admin actions during active exports.
- Add a runbook that validates both export-level status and per-part ZK state before declaring completion or failure (X.1).

## Recommended fixes
- Map all non-progressing conditions to a terminal status (#1.1).
- Add fencing / idempotency for `force_export` during active commit (#1.2).
- Fence kill against commit; make kill and final status consistent (#3.1).
- Make per-part status terminalization part of export-level failure (X.1).
```

---

## Related skills

- `pr-ci-failure-triage` — CI signal that often points to real issues worth listing.
- `github-issue-template` — file the reported issues once confirmed.

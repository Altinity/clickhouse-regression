# CAS static audit — fresh re-run 2026-08-31 (PR #2159 head)

Tracking issue: https://github.com/Altinity/ClickHouse/issues/2031
(`CAS-###` IDs are unchanged from the 2026-08-12 catalogue.)

All 39 CAS audits plus a distributed-systems audit and a usability audit, redone
**from scratch** against the latest PR #2159 code, after Filimonov's 2026-08-21
triage and the post-triage fix series that landed before merge.

Prior rounds (`cas-audit-rerun-20260812/`, #2031, Filimonov comment) are used as
**inventory of audit names/angles and as the developer-verdict ledger**. No prior
`CAS-###` finding is assumed still present. Every finding in this round is derived
from the current tree. Existing `CAS-###` IDs are **reused** when the same root
cause is re-confirmed, so Filimonov's per-id verdicts stay attachable.

## Audit target (pinned)

- Repo worktree: `/Volumes/workspace/altinity-clickhouse/cas-pr-2159-ceee42c`
- PR: https://github.com/Altinity/ClickHouse/pull/2159 (merged 2026-08-26)
- Commit: `ceee42c51a06cb05e2c9a2d811ef7e1726825552`
  (`cas: admit worker renewals only over an Active keeper`)
- Merge commit on `antalya-26.6`: `a49d9ed16df9e2ae03a22b69fed7f94c89d16ca7`
- No further CAS product commits on `antalya-26.6` after the merge
- CAS code root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
  (133 `.cpp`/`.h` files). Adjacent hooks in scope where an angle requires them:
  `src/Disks/DiskObjectStorage/**`, `src/Storages/MergeTree/DataPartsExchange.*`,
  `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp`,
  `src/Storages/System/StorageSystemContentAddressedMounts.cpp`,
  `programs/disks/Command*.cpp`, `docs/en/antalya/cas/**`.

## Post-audit (2026-08-12) product commits that must be treated as current

These landed after the previous audit pin (`842f2b37b8f`) and after / around
Filimonov's 2026-08-21 triage. Do not re-raise a finding that these close.

| Commit | What it changed |
|---|---|
| `83c03e26b18` | namespace absence proven per-row, not whole-catalog stillness |
| `b69051a2d85` | GCS generation semantics isolated to CAS requests |
| `335802a938f` | FREEZE shadow namespace scoped to `server_root_id` (closes #2212 / CAS-001) |
| `84b30f6b0d9` | `freezeRemote` CAS transaction (closes #2173 / CAS-058) |
| `2649bce42db` | undecodable manifest no longer wedges pool-wide GC (CAS-040) |
| `940b1685bf9` | blobs published unconditionally after mandatory HEAD (large write-protocol rewrite) |
| `7f932d31352` | bounded mount-lease renewal; GC meta-jobs take ownership (closes #2244) |
| `205af29c7f2` | drain detached work; survive released Context at shutdown |
| `917600b122b` | CAS settings live under `cas_` prefix (closes #2243 / CAS-106) |
| `ceee42c51a0` | worker renewals admitted only over an Active keeper |

## Method

- Static reasoning only. No build, no runtime, no fault injection.
- Intended behaviour from types, control flow, error classification, fail-open vs
  fail-closed branches, and shipped exception/setting strings.
- Comments and docs may be read as *claims to verify*, never as evidence that the
  code does what they say.
- Tests may be read to establish what CI pins, or for the test-coverage audit.
- Locate by symbol. Line numbers from the 2026-08-12 reports are stale.

## Filimonov calibration (do not repeat these failure modes)

From #2031 comment 2026-08-21:

- A real code shape with an **invented consequence** is not a finding.
- "Reported nowhere" is false if a SQL row or CLI surface reports it.
- Test-only fields and hooks are not production data.
- Do not invent arithmetic.
- Do not cite callers that have no production call site.
- Privilege claims must account for the `GLOBAL` privileges on `SYSTEM CAS *`.
- `EmulatedSingleProcess` is tests / local development only.
- Fail-closed loud failure grades below silent corruption.
- Operability / cost / scale gaps are not High on their own.

## Report contract

One file per audit in `reports/`. Format:

```markdown
# <audit> -- fresh audit 2026-08-31

## Scope
- Files/dirs examined
- Explicitly out of scope

## Findings
### <audit>-N -- <title> (High|Medium|Low)
- Anchor: path:lines (symbol) at ceee42c
- Trigger: minimal realistic trigger
- Evidence: code-backed reasoning
- Notes: optional. If this is the same root cause as an existing CAS-###, say so.

## By-design / info / non-actionable

## Closed-since-2026-08-12
- Items in this angle that the previous report raised and that HEAD no longer has,
  with the closing commit if identifiable.

## Coverage
- Reviewed / N-A / Deferred
```

Only confirmed defects. Per-audit local IDs. Global `CAS-###` assigned only in
the consolidation pass (reuse existing IDs when the root cause matches).

## The 39 audits

| Batch | Audits |
|---|---|
| B1 foundation | `codeonly-line`, `coverage-map`, `idisk-contract` |
| B2 protocols | `write-protocol`, `read-protocol`, `gc-protocol`, `gc-rebuild-feature` |
| B3 DS/safety | `jepsen-anomaly`, `security`, `concurrency`, `interleaving`, `crash-consistency`, `upgrade-compat`, `tla-fidelity` |
| B4 formats/bug-classes | `bc1-offset-overflow`, `bc2-writebuffer-spill`, `bc3-exception-safety`, `bc4-protobuf-decode`, `bc5-wide-part-read`, `bc6-mtime-semantics`, `bc7-blocking-io-locks` |
| B5 day-2/backend | `ad1-hash-determinism`, `ad2-deletion-erasure`, `ad3-day2-dr-runbook`, `ad4-migration`, `ad5-resource-exhaustion`, `ad6-s3-lifecycle-cross-region`, `ad7-protocol-skew` |
| B6 features/broad | `mergetree-part-support`, `datatype-agnosticism`, `alter-merge-mutation`, `encryption`, `performance`, `test-coverage-fuzzing`, `tier1`, `tier2`, `tier3`, `tier4`, `backfill-not-reviewed` |

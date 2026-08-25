# CAS static audit — fresh re-run 2026-08-12 (code-only)

All 39 CAS audits redone **from scratch** against the refactored CAS code.

Prior audit rounds ([`cas-audit-rerun-20260730/`](../cas-audit-rerun-20260730/),
[`cas-audit-rerun-20260811/`](../cas-audit-rerun-20260811/), the original gist, and tracking issue
[#2031](https://github.com/Altinity/ClickHouse/issues/2031)) were used **only as an inventory of audit
names and angles**. No prior `CAS-###` finding was carried forward, re-verified, or assumed.
Every finding in this round is derived independently from the current code.

## Audit target (pinned)

- Repo: `/Volumes/workspace/altinity-clickhouse/ClickHouse`
- Branch: `cas-code-only-strip`
- Base commit: `842f2b37b8f` (`842f2b37b8f8d93eef08945ab3a47b8f805635a5`)
- Tree audited: the **working tree as of 2026-08-12T09:40Z**, i.e. base commit plus the uncommitted
  comment/doc strip (~280 deletions, ~236 modifications). The strip is intentionally not committed;
  audits read the files on disk.
- CAS code root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (129 `.cpp`/`.h`
  files across `Backend/`, `Formats/`, `Gc/`, `Parts/`, `Pool/`, `Primitives/`, `Tools/`, `benchmarks/`)
- Adjacent CAS hooks in scope where an audit angle requires them: `src/Disks/DiskObjectStorage/**`,
  `src/Storages/MergeTree/DataPartsExchange.cpp`, `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp`,
  `src/Storages/System/StorageSystemContentAddressedMounts.cpp`, `programs/disks/Command*.cpp`.

## Code-only rule

The branch exists specifically so that audits cannot be misled by stale prose. Therefore:

- Intended behaviour is inferred from **types, control flow, error classification, and fail-open vs
  fail-closed branches** — not from comments, design docs, or commit messages.
- `docs/en/antalya/cas/**` is deleted on this tree. `docs/superpowers/CAS.md` still exists as an
  untracked leftover and is **excluded as evidence**.
- Tests are read only for audits whose angle is test coverage, or to establish what behaviour is
  currently pinned by CI.
- No runtime execution: static reasoning only.
- The ClickHouse tree is read-only for this exercise: no `checkout`, `reset`, or commit.

## Report contract

One file per audit in [`reports/`](reports/):

```markdown
# <audit> -- fresh audit 2026-08-12

## Scope
- Files/dirs examined
- Explicitly out of scope

## Findings
### <audit>-N -- <title> (High|Medium|Low)
- Anchor: path:lines (symbol)
- Trigger: minimal realistic trigger
- Evidence: code-backed reasoning
- Notes: optional

## By-design / info / non-actionable

## Coverage
- Reviewed / N-A / Deferred
```

Rules: only confirmed defects, each with a current-code file+line anchor; per-audit local IDs
(`write-protocol-1`, …); global `CAS-###` IDs assigned only in the consolidation pass.

## The 39 audits

| Batch | Audits |
|---|---|
| B1 foundation | `codeonly-line`, `coverage-map`, `idisk-contract` |
| B2 protocols | `write-protocol`, `read-protocol`, `gc-protocol`, `gc-rebuild-feature` |
| B3 DS/safety | `jepsen-anomaly`, `security`, `concurrency`, `interleaving`, `crash-consistency`, `upgrade-compat`, `tla-fidelity` |
| B4 formats/bug-classes | `bc1-offset-overflow`, `bc2-writebuffer-spill`, `bc3-exception-safety`, `bc4-protobuf-decode`, `bc5-wide-part-read`, `bc6-mtime-semantics`, `bc7-blocking-io-locks` |
| B5 day-2/backend | `ad1-hash-determinism`, `ad2-deletion-erasure`, `ad3-day2-dr-runbook`, `ad4-migration`, `ad5-resource-exhaustion`, `ad6-s3-lifecycle-cross-region`, `ad7-protocol-skew` |
| B6 features/broad | `mergetree-part-support`, `datatype-agnosticism`, `alter-merge-mutation`, `encryption`, `performance`, `test-coverage-fuzzing`, `tier1`, `tier2`, `tier3`, `tier4`, `backfill-not-reviewed` |

## Deliverables

- [`reports/`](reports/) — 39 fresh audit reports
- [`NEW-FINDINGS.md`](NEW-FINDINGS.md) — consolidated, deduplicated findings with global IDs
- [`RECONCILIATION-2031.md`](RECONCILIATION-2031.md) — every new finding mapped against the existing
  triage in [#2031](https://github.com/Altinity/ClickHouse/issues/2031), bucketed as already
  adjudicated / marked-fixed-but-still-found / re-confirmed / genuinely new
- [`ISSUE-DRAFT-cas-audit-2026-08-12.md`](ISSUE-DRAFT-cas-audit-2026-08-12.md) — replacement tracking
  issue superseding #2031

Note on numbering: the `CAS-###` IDs in this round are freshly assigned and do **not** correspond to
the numbering in #2031. `RECONCILIATION-2031.md` disambiguates them as `NEW-CAS-###` / `OLD-CAS-###`.

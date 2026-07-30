# CAS static audit re-run — 2026-07-30

Re-runs the 39 static audits originally captured in:
- Gist: https://gist.github.com/vzakaznikov/8b0506a495187ce3d634385544beebea
- Tracking issue: https://github.com/Altinity/ClickHouse/issues/2031 (**do NOT edit**)

Target of review: PR https://github.com/Altinity/ClickHouse/pull/2073 (`cas-gc-rebuild` → `antalya-26.6`).

## Paths for auditors

- **CAS source (current PR HEAD)**: `/Volumes/workspace/ClickHouse` — branch `cas-audit-20260730` (tracks `altinity/cas-gc-rebuild`). Do NOT edit or `git checkout` there.
- **CAS code root**: `/Volumes/workspace/ClickHouse/src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (114 files, ~2.4 MB). Subdirs: `Backend/`, `Formats/`, `Gc/`, `Parts/`, `Pool/`, `Primitives/`, `Tools/`, `benchmarks/`.
- **CAS design docs (in PR)**: `/Volumes/workspace/ClickHouse/docs/superpowers/cas/**` and `docs/superpowers/models/**` (TLA+).
- **Original audit reports**: `cas/docs/cas-audit-rerun-20260730/original-audit-gist.md` (all 39 files concatenated).
- **PR file list**: `cas/docs/cas-audit-rerun-20260730/pr2073-files.txt`.

## Focus rule (per user)

**Only CAS code**. Skip infra, CI, docs, unrelated ClickHouse files. Anchor every finding at a `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**` path (or immediately adjacent CAS integration hooks in `src/Disks/DiskObjectStorage/`).

## Skip list

None pre-determined. Every `CAS-###` in the original list is re-verified; auditor assigns a verdict per finding.

## Per-audit report shape

Each audit writes ONE markdown file into `cas/docs/cas-audit-rerun-20260730/reports/<audit-name>.md` with:

```markdown
# <audit name> — re-run 2026-07-30

## Scope in current code
- Files/dirs walked: <list>

## Findings still present
For each: `CAS-###` — one-line title
- Anchor: `src/.../File.cpp:LINE` (function / code path)
- Trigger: <minimal>
- Evidence quote (short)
- Notes

## Findings fixed / no longer reproducible
- `CAS-###` — one line + anchor for the fix

## New findings (not in original audit)
- NEW-<audit>-N: title + severity + anchor + trigger

## By-design / N/A / info

## Verdict summary table
| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
```

Static reasoning only. No runtime execution. Every "still present" claim requires a file+line anchor in the current code.

## Verdicts vocabulary

`🔴 still-present` · `✅ fixed` · `📐 by-design` · `🚫 not-a-bug` · `🛠 will-fix` · `❌ wontfix` · `🟡 needs-repro` · `↗ split-out` · `⚪ info`

## Batches (dispatched in parallel)

- **B1 foundation**: codeonly-line, coverage-map, idisk-contract
- **B2 protocols**: write-protocol, read-protocol, gc-protocol, gc-rebuild-feature
- **B3 DS/safety**: jepsen-anomaly, security, concurrency, interleaving, crash-consistency, upgrade-compat, tla-fidelity
- **B4 formats**: bc1-offset-overflow, bc2-writebuffer-spill, bc3-exception-safety, bc4-protobuf-decode, bc5-wide-part-read, bc6-mtime, bc7-blocking-io-locks
- **B5 day-2/backend**: ad1-hash-determinism, ad2-deletion-erasure, ad3-day2-dr-runbook, ad4-migration, ad5-resource-exhaustion, ad6-s3-lifecycle-cross-region, ad7-protocol-skew
- **B6 features/broad**: mergetree-part-support, datatype-agnosticism, alter-merge-mutation, encryption, performance, test-coverage-fuzzing, tier1, tier2, tier3, tier4
- **B7 (later, after B1-B6)**: consolidated summary + reconciliation table → then update #2031.

## Published gist

https://gist.github.com/alsugiliazova/7fb1441688ff428cc0e0a18918077c26

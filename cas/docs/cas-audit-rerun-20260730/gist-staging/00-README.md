# CAS static audit re-run — 2026-07-30 (vs Altinity/ClickHouse PR #2073)

Re-run of the 39 original static audits against current Content-Addressed Storage code
(`cas-gc-rebuild` / PR https://github.com/Altinity/ClickHouse/pull/2073).

Tracking issue: https://github.com/Altinity/ClickHouse/issues/2031
Original audit gist: https://gist.github.com/vzakaznikov/8b0506a495187ce3d634385544beebea

## Contents

| File | What |
|---|---|
| `RECONCILIATION.md` | Single triage table for all **131** `CAS-###` ids (zero not-reviewed) |
| `NEW-FINDINGS.md` | **70** new findings not in the original catalog |
| `ISSUE-2031-DRAFT.md` | Proposed replacement body for issue #2031 (includes New Findings section) |
| `report-*.md` | Per-audit re-run reports (39 files: 38 thematic + 1 backfill) |

## Headline

- 131 / 131 original findings re-verified
- See `RECONCILIATION.md` § Verdict counts for the breakdown
- New findings are tracked separately under `NEW-FINDINGS.md` and as a section in the issue draft

Static reasoning only. Anchors point into `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**`.

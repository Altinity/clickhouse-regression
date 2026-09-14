# Reconciliation of the 2026-08-31 re-run against #2031

Pin: PR #2159 head `ceee42c51a06cb05e2c9a2d811ef7e1726825552`.
IDs: **same** as the 2026-08-12 catalogue / Filimonov 2026-08-21 comment. Not renumbered.

Filimonov comment (2026-08-21) is the verdict ledger. k-morozov (2026-08-18) on
CAS-002 / 003 / 005 / 006 matches that ledger. alsugiliazova split CAS-021 to #2207.

## Bucket counts (135 catalogue items + 2 new)

| Bucket | Count | Meaning |
|---|---|---|
| **Fixed / obsolete on #2159** | 10 | CAS-001, 010, 031, 040, 058, 070, 088, 093, 103, 106 |
| **Still open — P2 residual** | 26 | Filimonov-accepted residuals re-confirmed at HEAD |
| **Still open — P3 residual** | 14 | Same, P3 only |
| **New this round** | 2 | CAS-136, CAS-137 |
| **Adjudicated, no action** | 31 | by-design / not-a-bug / duplicate; still true on HEAD |
| **Dropped as cosmetic P3** | ~52 | Filimonov "partly" with no production consequence left |

Full open/closed text: [`ISSUE-2031-UPDATED-BODY.md`](ISSUE-2031-UPDATED-BODY.md).

## P1s (all closed)

| ID | Closing commit | Issue |
|---|---|---|
| CAS-001 | `335802a` | #2212 |
| CAS-040 | `2649bce` | — |
| CAS-058 | `84b30f6` | #2173 |
| CAS-106 | `917600b` | #2243 |

## Do not re-open

Anything Filimonov marked 📐 / 🚫 / ❌ / duplicate, plus the 940b168 blob-protocol items
(CAS-010, 031, 088, 103). CAS-079 is **not** closed by `83c03e2` — that commit only
moved the writer path to per-row proof.

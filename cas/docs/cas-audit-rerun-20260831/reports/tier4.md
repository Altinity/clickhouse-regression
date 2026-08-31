# tier4 -- fresh audit 2026-08-31

## Scope
Tier4 in this re-run is **scale/ops remaining issues only if they produce user-visible breakage** (loud INSERT/merge refusal, stall, wrong admin effect, ENOSPC). Cost-only or by-design backpressure is not a finding here.

- Files/dirs examined: inline caps (`CasPartWriteTxn.cpp:55,533-535`), recovery epoch seals (`CasRefLedger.cpp:1097-1116`), `applyNewSettings` no-op, nested `server_root_id`, scratch path, 64 MiB snapshot ceiling (CAS-111 class), `isDirectoryEmpty` FREEZE merge.
- Explicitly out of scope: re-raising the upload-pool block-on-full as a defect; GC list-everything memory unless it surfaces as a stuck verb.

## Findings
### tier4-1 -- a legal part can fail INSERT/merge forever with LIMIT_EXCEEDED at 16 MiB inline (Medium)
- Anchor: `CasPartWriteTxn.cpp:55,533-535`. Classifier still inlines `data.cmrk4`, `primary.cidx`, skip-index files (`ContentAddressedTransaction.cpp:67-75`).
- Trigger: many sub-MiB index/projection/marks files on one part. Retry rebuilds the same set.
- Evidence: the operator sees a hard write failure on a schema a plain object-storage disk accepts. User-visible, deterministic. Same as CAS-044 / mergetree-part-support-1.
- Notes: CAS-044.

### tier4-2 -- first touch of a long-idle table can stall on O(mount-count) epoch-seal writes (Medium)
- Anchor: `CasRefLedger.cpp:1097-1116`.
- Trigger: many remounts, then SELECT/INSERT the idle table.
- Evidence: the query waits on sequential durable pairs with no operator-facing progress besides logs. User-visible stall, not corruption. Same as CAS-114 / performance-2.
- Notes: CAS-114.

### tier4-3 -- RELOAD CONFIG leaves CAS settings and a removed disk's mount lease live (Medium)
- Anchor: see tier2-3 / CAS-107.
- Trigger: `SYSTEM RELOAD CONFIG` after changing `cas_*` or deleting the disk stanza.
- Evidence: settings stay at ctor values; lease keeps renewing until restart. Operator-visible "I changed the file and nothing happened".
- Notes: CAS-107.

### tier4-4 -- DROP POOL MEMBER on a prefix `server_root_id` decommissions nested members (Medium)
- Anchor: see tier2-2 / CAS-007.
- Trigger: `SYSTEM CAS DROP POOL MEMBER` for `a` while `a/b` is a live member.
- Evidence: user-visible destructive admin effect on the wrong member.
- Notes: CAS-007.

## By-design / info / non-actionable
- Local scratch ENOSPC is loud and expected without a quota (CAS-046). Not re-raised as a separate tier4 item.
- 64 MiB encoded snapshot/removal ceiling (CAS-111) is a loud fail-closed admission refusal before objects are created. Scale limit, already tracked; not a silent break.
- Upload-pool blocking enqueue is backpressure.
- FREEZE-name merge is user-visible (wrong backup set) and is owned by tier2-1; not duplicated as a new id.

## Closed-since-2026-08-12
- CAS-106 UNKNOWN_SETTING at startup (`cas_` prefix).
- CAS-001 UNFREEZE deleting another server's freeze (ops breakage closed).
- CAS-040 pool-wide GC wedged by one bad manifest (ops unavailability closed).

## Coverage
- Reviewed: write-cap refusal, recovery stall, reload, nested decommission, scratch ENOSPC, snapshot ceiling.
- N-A: by-design backpressure and cost-only cache-weight inaccuracy (performance owns the latter; it does not break a verb).
- Deferred: measured recovery-seal latency vs mount count.

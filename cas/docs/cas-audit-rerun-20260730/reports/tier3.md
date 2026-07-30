# tier3 — re-run 2026-07-30

Scope of the original section (`cas-tier2-audit.md` §3 "Storage policy / tiered storage / TTL moves")
covers **MOVE PARTITION TO DISK/VOLUME**, **TTL moves**, **move_factor / free-space heuristics**,
and the **R1/X1 read-vs-GC dangle class as it applies to move**. Reconciliation IDs from the gist:
`CAS-041` (TIER-1), `CAS-043` (TIER-2), `CAS-103` (TIER-3/TIER-4).

## Scope in current code
- Files/dirs walked (current PR HEAD, branch `cas-audit-20260730` @ `834c9517`):
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp`
    (`createHardLink`, `moveDirectory`, `moveFile`, `replaceFile`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp`
    (`getStorageObjects`, `getObjectsFor…`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp` (reader-pin surface)
  - directory-wide grep for `IReservation` / `getAvailableSpace` / `getTotalSpace` / `move_factor`
    over the entire `.../ContentAddressed/` subtree — no matches, i.e. CAS overrides none of them.
- Anchored against generic MergeTree cross-disk move path in `Storages/MergeTree/**` only insofar as
  it calls back into CAS (`createHardLink` requires two part-file paths; cross-disk paths cannot
  reach it) — no CAS-side changes to the cross-disk move contract landed in this PR.

## Findings still present

### `CAS-041` / `TIER-1` — Cross-disk MOVE PARTITION is a full byte copy, even CAS→CAS same-pool (Med)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1119`
  (`ContentAddressedTransaction::createHardLink`) — early guard:
  `if (!src || src->file.empty() || !dst || dst->file.empty()) throw … "createHardLink requires two part-file paths"`.
- Trigger: `ALTER TABLE … MOVE PARTITION … TO DISK/VOLUME` across disks. The generic MergeTree
  clone path (`MergeTreeData::clonePartOnSameDisk` / cross-disk move) is byte-oriented; it does not
  invoke `createHardLink` on the CAS metadata layer because source and destination live under two
  different `DiskObjectStorage` instances (different metadata storages). Same-pool CAS→CAS is
  indistinguishable to the mover.
- Evidence quote:
  `"ContentAddressed: createHardLink requires two part-file paths: {} -> {}"` — refuses non-part
  shapes; there is no cross-disk relink hook anywhere in `ContentAddressedTransaction.cpp` or in
  `ContentAddressedMetadataStorage.cpp`.
- Notes: `moveDirectory` (line 1200) handles only **same-namespace** re-key + `republishRef`
  (line 1370), i.e. same-disk moves. No new API for cross-disk / cross-pool relink landed. Missed
  optimization on CAS→CAS same-pool remains; correctness of same-disk MOVE PARTITION TO TABLE
  continues to be handled via `moveDirectory` (copy-by-reference).

### `CAS-043` / `TIER-2` — TTL move off CAS transiently double-bills storage until GC reclaims (Med)
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp:1963`
  (manifest-cleanup path after ref-drop; reclaim is asynchronous and deferred to a GC round).
- Trigger: TTL move (`… TO DISK / TO VOLUME`) drops the source part ref after the destination is
  written; blobs remain until the next successful GC round. Behavior unchanged in this PR.
- Evidence quote: `"the manifest cleanups execute inline from result.mf_cleanup"` — cleanups are
  *scheduled* by the GC round, not by the ref-drop itself. This is the LC-1 deferred-reclaim shape.
- Notes: expected/by-design given the CAS reclaim model; still observably transient over-billing
  during a large TTL wave.

### `CAS-103` (part 1) / `TIER-3` — Move-vs-concurrent-GC untested; R1/X1 class applies (Low)
- Anchor: `ContentAddressedMetadataStorage.cpp:1793` and `:1830`
  (`{StoredObject(location.key, path, location.length)}` returned from `getStorageObjects` /
  per-file object accessor). The source-side read for a cross-disk move issues ranged GETs against
  these blob keys **without a reader-side pin** across the deferred blob fetch — the R1/X1 dangle
  class.
- Trigger: `MOVE PARTITION … TO DISK` reading the source while a concurrent `DROP PARTITION` +
  GC-condemn/delete runs against the same blobs. GC condemnation still uses `resolveRef` +
  ack-floor logic in `Gc/CasGc.cpp`; there is no per-reader lease/pin added in this PR
  (grep for `reader.*pin` / `readerPin` / `pin.*reader` under `.../ContentAddressed/` returns only
  the R1 heartbeat comment at `Gc/CasGc.cpp:367`, which pertains to mount-liveness, not blob
  pinning).
- Evidence quote: `Gc/CasGc.cpp:367` — `e.reason = "R1: heartbeat classification (live/terminated/fenced mounts)"`
  (the "R1" here refers to the fencing incarnation class, not to the reader-pin gap). No blob-level
  reader pin API is exposed.
- Notes: fail-loud (`NoSuchKey`) is the expected behavior; not a correctness regression, but the
  MOVE code path exercising this class is untested. Inherits directly from Tier 1 R1/X1.

### `CAS-103` (part 2) / `TIER-4` — `move_factor` / free-space heuristics inert on CAS source (Info)
- Anchor: no anchor **by absence** — grep over `.../ContentAddressed/` shows zero overrides of
  `IReservation`, `getAvailableSpace`, `getTotalSpace`, `getUnreservedSpace`, or `move_factor`
  (verified: `rg -w 'getAvailableSpace|getTotalSpace|move_factor' src/Disks/…/ContentAddressed`
  returns nothing). CAS inherits the object-storage placeholder free-space from the underlying
  `DiskObjectStorage`.
- Trigger: `move_factor`-driven background moves *from* a CAS volume: because free space on an
  object-store-backed disk is effectively unbounded, the free-space trigger never fires.
- Evidence quote: n/a (absence). The pattern still matches the original SYS-4 note ("free space is
  not a real CAS quota; reservation logic uses the object-storage number").
- Notes: informational; standard object-store behavior. Cross-references SYS-4 in the Tier 2 audit.

## Findings fixed / no longer reproducible
- None. The MOVE / TTL-move / free-space surfaces are unchanged in this PR relative to the
  original audit: no cross-disk relink hook, no reader-pin API, no CAS reservation override.

## New findings (not in original audit)

- **NEW-tier3-1** (Low, feature-gap-with-safety-note) — `moveFile` on committed non-part files
  throws `LOGICAL_ERROR` when the source is not staged in this transaction. Anchor:
  `ContentAddressedTransaction.cpp:1488` — `"ContentAddressed: moveFile source not staged: {}"`.
  Trigger: any code path that reaches `moveFile` on a committed part-file rename (e.g. a future
  MergeTree change that reintroduces the `txn_version.txt` `.tmp` + `replaceFile` rename dance) —
  the branch comment (lines 1483-1487) explicitly documents it as "no live caller … retained only
  as a fail-loud guard". Correctness-safe (fails loudly), but the guard is coupled to a MergeTree
  invariant that CAS does not enforce; a future MergeTree refactor could regress silently until
  hit by MOVE/rename-heavy workloads.

- **NEW-tier3-2** (Low, robustness) — cross-namespace `moveDirectory` (RENAME TABLE) is
  documented as **best-effort, non-atomic, idempotent-on-retry** but has **no in-call
  compensation**. Anchor: `ContentAddressedTransaction.cpp:1215-1248`. Trigger: server crash
  mid-loop during a `RENAME TABLE` that spans a CAS pool ⇒ table is "SPLIT across namespaces"
  until the same RENAME is manually re-driven. Overlaps with MOVE PARTITION when the target is
  a cross-engine move that maps to a namespace move. In-code note admits: *"there is no in-call
  compensation; true atomicity would need a durable move-journal (deliberately out of scope)."*
  Same failure mode as the DUR1 partial-commit class, at RENAME-TABLE granularity — not called
  out in the original Tier3/Tier2 sections.

- **NEW-tier3-3** (Info) — Same-pool same-disk `moveDirectory` for part-dirs is a pure metadata
  `republishRef` (`ContentAddressedTransaction.cpp:1370`), i.e. genuinely O(1) copy-by-reference.
  Original audit did not enumerate this explicitly as a positive property (only noted it in
  passing for FREEZE); it is worth calling out that same-disk `MOVE PARTITION TO TABLE` is
  already relink-free on CAS today. This bounds the gap in TIER-1 (CAS-041) precisely to the
  **cross-disk** case.

## By-design / N/A / info

- **CAS-041 (part)**: same-disk `MOVE PARTITION TO TABLE` is by-design relink-free
  (`republishRef`); TIER-1 gap is strictly the cross-disk / cross-pool subset.
- **TIER-4**: standard object-store behavior; informational only. Documenting a
  `move_factor` caveat in operator docs is the appropriate remedy — no code fix expected.
- **TIER-2**: inherent to the CAS reclaim model (LC-1 deferred reclaim); tracked as CAS-043
  in the reconciliation table.

## Verdict summary table

| CAS-id | Original ID | Old severity | Status | Evidence anchor |
|---|---|---|---|---|
| CAS-041 | TIER-1 (cross-disk MOVE = byte copy) | Med | 🔴 still-present | `ContentAddressedTransaction.cpp:1119` (`createHardLink` requires two part-file paths; no cross-disk relink hook) |
| CAS-043 | TIER-2 (TTL move double-bills until GC) | Med | 🔴 still-present | `Gc/CasGc.cpp:1963` (deferred `mf_cleanup`; LC-1 reclaim model) |
| CAS-103a | TIER-3 (move vs concurrent GC untested; R1/X1) | Low | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1793`/`:1830` (no reader pin); `Gc/CasGc.cpp` grep — no reader-pin API |
| CAS-103b | TIER-4 (`move_factor` inert on CAS source) | Info | 🔴 still-present | absence in `.../ContentAddressed/` — no `IReservation`/`getAvailableSpace` override |
| — | NEW-tier3-1 (`moveFile` unstaged guard is a coupling risk) | Low | ⚪ info / 🟡 needs-repro | `ContentAddressedTransaction.cpp:1488` |
| — | NEW-tier3-2 (cross-ns `moveDirectory` non-atomic, no compensation) | Low | 🔴 still-present | `ContentAddressedTransaction.cpp:1215-1248` |
| — | NEW-tier3-3 (same-disk part MOVE is relink-free ✅) | Info | 📐 by-design | `ContentAddressedTransaction.cpp:1370` (`republishRef`) |

## Counts
- Findings still present (original): 4/4 (CAS-041, CAS-043, CAS-103a, CAS-103b)
- Fixed since original: 0
- New findings this re-run: 3 (2 Low, 1 Info)

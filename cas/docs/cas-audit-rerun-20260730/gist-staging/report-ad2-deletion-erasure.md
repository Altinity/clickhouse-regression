# ad2-deletion-erasure — re-run 2026-07-30

Re-verification of AD-2 (Data-Deletion & Erasure-Guarantee / GDPR "right to be forgotten") against the
current PR head at `/Volumes/workspace/ClickHouse` (branch `cas-audit-20260730`, tracks
`altinity/cas-gc-rebuild`). Static reasoning only.

## Scope in current code
Files/dirs walked (CAS-only, per README focus rule):
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.{cpp,h}`
  (`removeRecursive`, `dropRefIfPresent`, `renameDirectory` sweeps)
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.{cpp,h}`
  (`shadowNamespace`, `liveNamespace`, GC / FSCK entry points)
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedSettings.{cpp,h}`
- `Parts/PartFolderAccess.{cpp,h}` (`dropRef`, `dropRefIfPresent`, `dropNamespace`)
- `Parts/PartPathParser.h` (FREEZE shadow / detached / moving classification)
- `Pool/CasPool.{cpp,h}`, `Pool/CasRefLedger.{cpp,h}`, `Pool/CasRefProtocol.h` (`dropRef`, `dropNamespace`, `gc_snap_generations_to_keep`)
- `Gc/CasGc.{cpp,h}`, `Gc/CasGcScheduler.{cpp,h}`, `Gc/CasGcShardPlan.{cpp,h}`, `Gc/CasBlobInDegree.{cpp,h}`
  (two-phase graduation, `suppress_destructive`, snap retention floor)
- `Backend/CasBackend.h`, `Backend/CasObjectStorageBackend.{cpp,h}`, `Backend/CasProbe.{cpp,h}`
  (`deleteExact`, `checkPoolPreconditions`, versioning refusal)
- `Tools/CasFsck.{cpp,h}` (reachability audit — `PendingGc` / `AwaitingGc` classifications)
- `Tools/CasDecommission.{cpp,h}` (SYSTEM CONTENT ADDRESSED FORGET — assertion, not erasure proof)
- `Tools/CasInspect.{cpp,h}`
- `Primitives/CasEvent.{cpp,h}`

## Findings still present

### CAS-018 / ERASE-1 — No bounded delete→physical-erase SLA 🔴 still-present
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1034-1036` (`removeRecursive` header)
- Trigger: any DROP/TRUNCATE/DROP PARTITION/TTL-expiry on a CAS-backed table.
- Evidence quote:
  > "Removal = pointer-unlink + deferred GC: only refs and verbatim files go; the shared blobs/trees
  > are reclaimed by Cas::Gc once unreachable. The predicate gates backing-object deletion, which CA
  > always defers, so it is intentionally ignored here."
- Notes: `ShouldRemoveObjectsPredicate` is **explicitly ignored** — the caller cannot force synchronous
  erase. Reclaim is still 100% GC-deferred; the two-phase `condemn → delete_pending → deleteExact`
  chain in `Gc/CasGc.cpp` remains gated by GC leader, mount, retention floor, and `suppress_destructive`
  clamp (`Gc/CasGc.cpp:1833, 2079, 2170`). No `deletion_sla_ms` / `max_reclaim_lag_ms` setting exists
  in `ContentAddressedSettings.cpp` (verified — only `gc_snap_generations_to_keep = 3` and
  scheduler-cadence settings). No "reclaim-now" foreground command is exposed by
  `ContentAddressedMetadataStorage.h` (only `gcStop` / `gcStart` / `gcRun` — see `:289,301` and
  `.cpp:580,939,975`; `gcRun` still returns after the round it starts and does NOT prove a specific
  ref/blob was erased).

### CAS-019 / ERASE-2 — Dedup: one owner's delete may erase nothing 🔴 still-present
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasBlobInDegree.cpp:364-448` (in-degree
  merge / condemn logic); `Pool/CasRefLedger.cpp:2801,2890` (`dropRef` / `dropNamespace` decrement one
  source-edge, not a blob).
- Trigger: DELETE a row / DROP a partition whose content is byte-identical to any other live ref
  (another partition, another table, another replica's part, a FREEZE shadow, an INSERT-block-dedup
  survivor).
- Evidence quote (`Tools/CasFsck.cpp:568`):
  > "reclaim it. The edge names its source, so the check is to ask whether that source still exists"
- Notes: The whole reachability model in `Gc/CasBlobInDegree.h/.cpp` graduates a blob to
  `delete_pending` **only** when in-degree reaches 0. No per-subject / per-tag ledger of "who else
  points at this blob" is materialised at DELETE time; `CasFsck` can compute it offline
  (`Tools/CasFsck.cpp:471,568,639`) but is read-only and post-hoc. No API in
  `ContentAddressedMetadataStorage.h` returns "list every ref that shares blob(s) belonging to <ref>".
  No per-subject-key encryption exists (see encryption audit rerun). Semantic gap unchanged.

### CAS-043 / LC-1 — DROP/TRUNCATE/TTL-move frees zero bytes synchronously 🔴 still-present
- Anchor: `ContentAddressedTransaction.cpp:1032-1074` (`removeRecursive`), particularly `:1072`
  (`dropNamespace(liveNamespace(uuid))` — a metadata-only tombstone).
- Trigger: DROP TABLE / TRUNCATE / DROP PARTITION / TTL move OFF a CAS disk.
- Evidence quote (`:1034`):
  > "Removal = pointer-unlink + deferred GC"
- Notes: still no synchronous S3 DELETE at any user-visible point. `Cas::Gc::cleanupRefObjects`
  (`Gc/CasGc.cpp:2075-2145`) is the ONLY path that removes ref-log/verbatim objects and it runs on the
  GC round; `deleteExact` on blobs is deferred through the graduation states. `ContentAddressedSettings.cpp`
  (`gc_snap_generations_to_keep = 3`, no SLA settings) confirms no bound. `suppress_destructive`
  clamp (`Gc/CasGc.cpp:1833-1957`) still latches on ANY anomaly and freezes destructive actions for
  that round, extending the leak window arbitrarily.
- Related: `CFG-4` (GC-disabled / read-only mount leaks indefinitely) still holds — `gcStop`
  (`ContentAddressedMetadataStorage.cpp:939-975`) has no back-pressure on DROP/TRUNCATE ingest, so an
  operator who stops GC before dropping a table gets a namespace-tombstoned table whose bytes will
  never leave S3 without `gcStart`.

### CAS-070 / ERASE-3, ERASE-4 — FREEZE shadow / detached / gc-snap retention silently retain deleted data 🔴 still-present
- Anchors:
  - `Parts/PartPathParser.h:17,25,44-48,87-90` (FREEZE `shadow/<backup_name>/...` and `detached/`
    classification — kept as first-class routes into ref namespaces).
  - `ContentAddressedTransaction.cpp:1044-1066` (a `removeRecursive` on a shadow path only drops the
    **shadow** namespace; a `removeRecursive` on the live table dir at `:1070-1074` drops
    `liveNamespace(uuid)` and does NOT sweep sibling `shadowNamespace(<backup>/...)` refs).
  - `ContentAddressedMetadataStorage.cpp:1239,1255,1607` (shadow namespaces are separate entities the
    live-table drop path never touches).
  - `Pool/CasPool.h:79-84` and `ContentAddressedSettings.cpp:79`
    (`gc_snap_generations_to_keep = 3` — retained metadata about reclaimed content).
- Trigger: table had a FREEZE / BACKUP taken; user then DELETEs/DROPs; blobs stay live via the
  shadow-namespace refs until an explicit `SYSTEM UNFREEZE WITH NAME <backup>` (which the shadow
  path in `removeRecursive` DOES handle at `:1058-1065`, but nothing invokes it as part of DROP).
- Evidence quote (`ContentAddressedTransaction.cpp:1068-1074`):
  > "Table dir: the table's namespace (live + folded-in detached refs) and every verbatim file go in
  > one dropNamespace." — note: **live + detached only**, no shadow sweep.
- Notes: The detached branch _is_ now folded into `liveNamespace` per parser design
  (`PartPathParser.h:44-48`), so ERASE-3 detached-refs sub-part is mitigated for the whole-table DROP
  path. But per-partition FREEZE shadows survive DROP, and the `Tools/CasDecommission.h:25-39`
  "namespaces_removed by this invocation" flow only walks the pool member's namespaces — it does not
  enumerate shadow namespaces belonging to other members. `gc_snap_generations_to_keep` still defaults
  to 3 (`ContentAddressedSettings.cpp:79`, `CasGc.cpp:762,2319`), retaining reclaim-audit metadata
  about deleted subjects.

### CAS-071 / ERASE-5 — No crypto-shred; physical erasure depends on backend DELETE semantics 🔴 still-present (mitigated for one case)
- Anchor: `Backend/CasObjectStorageBackend.cpp:52-84` (`checkPoolPreconditions`), `Backend/CasProbe.cpp:47,219-225`.
- Trigger: mount a CAS pool over a bucket whose DELETE does not synchronously destroy bytes
  (versioning-enabled S3/GCS, S3 object-lock, S3 replication / CRR, GCS soft-delete duration > 0).
- Evidence quote (`Backend/CasObjectStorageBackend.cpp:78-83`):
  > "the bucket has object VERSIONING enabled. A token-exact DELETE on a versioned bucket archives a
  > noncurrent generation instead of reclaiming storage — GC would silently stop reclaiming space.
  > Disable versioning on the bucket (and prefer soft-delete duration 0 for CAS pools) and retry the
  > mount."
- Notes: **Partial mitigation vs. original.** GC-side warning also present at `Gc/CasGc.cpp:519` (logs
  when a delete created a delete-marker). BUT:
  - The check runs only in Native + GCS-generation-token mode (`:57-58`); S3 with versioning is not
    refused at all.
  - `isBucketVersioningEnabled()` returning `nullopt` falls back to WARN + proceed (`:61-75`) — no
    fail-closed.
  - **No object-lock check**, **no cross-region-replication (CRR) check**, **no S3-soft-delete /
    MFA-delete check**, **no bucket-lifecycle-transition-to-Glacier check**. All of these still
    silently retain deleted bytes.
  - No `deleteExact`-side post-condition ("HEAD after DELETE returned 404") is asserted for any
    backend (`Backend/CasBackend.h:107-132`, `CasObjectStorageBackend.cpp:531,989-995`).
  - No `crypto-shred` primitive exists (`grep -i crypto` on the tree returns only
    `Primitives/CasBlobDigest.h:99` — "no cryptographic property is needed here"). Per-subject keys
    remain incompatible with content-addressed dedup.

### ERASE-6 — Orphaned namespaces / refs retain deleted data indefinitely (Low) 🔴 still-present
- Anchor: `Tools/CasFsck.h:31-93` (orphan classes still labeled reclaimable but rely on
  `SYSTEM CONTENT ADDRESSED GC REBUILD` for the stuck-in-degree case); `Gc/CasGc.cpp:1230,1447,1995,2007`
  (still points operators to REBUILD to recover an unreclaimable blob).
- Trigger: crash between `dropNamespace`'s Removed-snapshot durability and GC namespace-cleanup
  (`Pool/CasRefLedger.cpp:2947-2982`), or ZK/CAS divergence for a table.
- Notes: `Tools/CasFsck.cpp:667` still reports orphan blobs as "unreclaimable by the incremental GC
  (needs `ca-gc-rebuild`)". Rebuild is destructive/operator-driven; nothing runs it automatically.

### ERASE-7 — Deferred/dedup model is correct engineering; the gap is contractual ⚪ info
- Anchor: whole `Gc/` subtree; `ContentAddressedTransaction.cpp:1034` doc comment.
- Notes: unchanged. The two-phase design is safe. The audit-item is the missing compliance surface.

## Findings fixed / no longer reproducible

None of ERASE-1..ERASE-7 is fully fixed. Partial improvements:
- `Backend/CasObjectStorageBackend.cpp:55-84` — mounts on GCS with bucket-versioning ENABLED now
  fail-closed. Narrows the AWS "versioning silently retains" edge of ERASE-5/CAS-071 for one dialect.
- `ContentAddressedTransaction.cpp:1068-1074` + `Parts/PartPathParser.h:44-48` — detached refs are
  now folded into `liveNamespace`, so a whole-table DROP does reach the detached ref set (was called
  out in ERASE-3). FREEZE shadow refs are still separate.
- `ContentAddressedTransaction.cpp:1058-1065` — `SYSTEM UNFREEZE WITH NAME` (and shadow-prefix
  `removeRecursive`) will iterate every shadow namespace under the backup root and dropNamespace each.
  So an operator who UNFREEZEs BEFORE DROPping can achieve deterministic shadow cleanup — but this
  still doesn't couple to DROP semantically (ERASE-3 remains open).

## New findings (not in original audit)

- **NEW-ad2-1 (High for compliance) — `isBucketVersioningEnabled()` unknown → mount proceeds.**
  - Anchor: `Backend/CasObjectStorageBackend.cpp:61-75`.
  - Trigger: on a bucket where `GetBucketVersioning` errors (permissions denied) or the backend has
    no answer, CAS logs a WARNING and mounts. If versioning is in fact ON, every future
    `deleteExact` becomes a delete-marker (`Gc/CasGc.cpp:519`) and reclaim silently stops.
  - Rationale for elevating: for a regulated deployment the correct default is fail-closed on
    "unknown", not "assume off". The comment at `:64-68` acknowledges the design choice explicitly.

- **NEW-ad2-2 (Med) — versioning precondition is GCS-only; S3 versioning / object-lock / CRR /
  soft-delete not checked.**
  - Anchor: `Backend/CasObjectStorageBackend.cpp:57-58` (`if (mode != Mode::Native || native_token_type != TokenType::Generation) return;`).
  - Trigger: mount CAS over an S3 bucket with versioning, MFA-delete, object-lock retention,
    lifecycle rules that transition-to-Glacier before expiring, or CRR to a bucket CAS never
    deletes. `checkPoolPreconditions` returns immediately without touching any of these. The GC-side
    "delete marker created" log warning (`Gc/CasGc.cpp:519`) is the only after-the-fact signal.
  - Effect: the original AD-2 caveat "physical erasure depends on backend DELETE semantics" (ERASE-5)
    is now partly enforced for one dialect and left completely unenforced for the more common one.

- **NEW-ad2-3 (Med) — no post-`deleteExact` verification anywhere in the pipeline.**
  - Anchor: `Backend/CasBackend.h:102-132` (`DeleteOutcome`, `created_delete_marker`); no
    HEAD-after-DELETE is performed in `Gc/CasGc.cpp` around the `deleteExact` sites
    (`Tools/CasDecommission.cpp:57,81` are the only other `deleteExact` calls; neither re-heads).
  - Trigger: any object-store that acknowledges DELETE but retains the object (soft-delete window,
    replicated-copy retention). CAS marks the blob reclaimed and drops it from `blobIndegree`; no
    later fsck notices the survivor because the ref side is gone.
  - Effect: compliance-grade "prove erased" cannot be assembled from the outcomes CAS records; the
    tool asked for in the original AD-2 §3 remains impossible to build on top of the current API.

- **NEW-ad2-4 (Med) — `SYSTEM CONTENT ADDRESSED FORGET` explicitly documents "erasure NOT verified".**
  - Anchor: `Pool/CasPool.cpp:135,328-332,755,966` and `ContentAddressedMetadataStorage.cpp:926-929,1046,1140-1160`.
  - Evidence quote (`Pool/CasPool.cpp:332`):
    > "decommissioned by SYSTEM CONTENT ADDRESSED FORGET — erasure was NOT verified; if this was a"
  - Notes: The operator's only advertised "make this pool go away" verb is spec'd, in the code
    itself, as a non-erasure assertion. A compliance auditor reading these strings has no
    alternative primitive to point at. Reinforces ERASE-1/ERASE-2/ERASE-5 as a contractual gap.

- **NEW-ad2-5 (Low) — `gc_snap_generations_to_keep` retention floor is uncapped by wall-clock.**
  - Anchor: `Pool/CasPool.h:79-84`, `Gc/CasGc.cpp:762,2319`.
  - Trigger: a CAS pool with very-slow GC rounds retains the last N snap generations even if each
    generation is weeks old. The metadata about reclaimed subjects (ERASE-4) can therefore live
    much longer than "3 rounds" implies.
  - Effect: minor amplification of ERASE-4; strictly a documentation / metric gap.

## By-design / N/A / info

- The core `pointer-unlink → GC-graduation` model is unchanged and remains the right engineering
  choice (ERASE-7). New findings are all about the *contract / preconditions / observability*
  layered on top of it, not about the correctness of the deletion primitive itself.
- `Tools/CasFsck.cpp` continues to be the ONLY thing that can answer "is blob X still reachable and
  through which refs" — but is read-only, cluster-cold, and not wired to any operator-facing
  "prove erased" verb.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-018 (ERASE-1) | High (compliance) | 🔴 still-present | `ContentAddressedTransaction.cpp:1034`; no SLA setting in `ContentAddressedSettings.cpp` |
| CAS-019 (ERASE-2) | High (compliance) | 🔴 still-present | `Gc/CasBlobInDegree.cpp:364-448`; `Pool/CasRefLedger.cpp:2801,2890` |
| CAS-043 (LC-1)    | High (leak/observ) | 🔴 still-present | `ContentAddressedTransaction.cpp:1032-1074`; `Gc/CasGc.cpp:1833,2075,2170` |
| CAS-070 (ERASE-3/4) | Med           | 🔴 still-present (detached folded in; shadow still separate; snap retention unchanged) | `ContentAddressedTransaction.cpp:1044-1074`; `Pool/CasPool.h:79-84` |
| CAS-071 (ERASE-5) | Med             | 🔴 still-present (GCS-versioning-enabled now fail-closed; S3 variants + object-lock + CRR + soft-delete uncovered) | `Backend/CasObjectStorageBackend.cpp:55-84`; `Gc/CasGc.cpp:519` |
| ERASE-6           | Low             | 🔴 still-present | `Tools/CasFsck.h:41-93`, `CasFsck.cpp:667`; `Gc/CasGc.cpp:1230,1995` |
| ERASE-7           | Info            | ⚪ info | whole `Gc/` subtree |
| NEW-ad2-1         | High (compliance) new | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:61-75` |
| NEW-ad2-2         | Med new         | 🔴 still-present | `Backend/CasObjectStorageBackend.cpp:57-58` |
| NEW-ad2-3         | Med new         | 🔴 still-present | `Backend/CasBackend.h:102-132`; `Gc/CasGc.cpp` `deleteExact` sites |
| NEW-ad2-4         | Med new         | 🔴 still-present | `Pool/CasPool.cpp:332`; `ContentAddressedMetadataStorage.cpp:926-929` |
| NEW-ad2-5         | Low new         | 🔴 still-present | `Pool/CasPool.h:79-84`; `Gc/CasGc.cpp:762,2319` |

**Headline:** All 7 original AD-2 items remain. The versioning-precondition addition (`checkPoolPreconditions` refusing GCS-with-versioning) narrows one edge of ERASE-5 but is the ONLY compliance-relevant surface added; the fundamental "delete is a pointer-unlink, physical erase is unbounded / dedup-gated / backend-trust-dependent" contract is unchanged. Four new findings flag gaps in the precondition set (unknown-versioning fallback, S3-side omissions), the missing post-DELETE verification, and the code's own explicit "erasure NOT verified" text for FORGET.

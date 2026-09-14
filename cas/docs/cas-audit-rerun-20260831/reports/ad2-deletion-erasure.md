# ad2-deletion-erasure -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Gc/CasGc.cpp` (redelete, delete-marker abort); `Gc/CasBlobInDegree.cpp`; `Tools/CasDecommission.cpp`; `Pool/CasServerRoot.h` (`validateServerRootId`); `Formats/CasLayout.h` (`serverRootPrefix`, `casManifestsServerPrefix`, staging/`roots/` prefixes); `ContentAddressedTransaction.cpp` (remove / UNFREEZE / hardlink); `ContentAddressedMetadataStorage.cpp` (`shadowNamespace`, `serverPrefix`, cache wrap comment); `DiskObjectStorageCache.cpp`; `Pool/CasPartWriteTxn.cpp` (`adoptEvidence`); `Backend/CasObjectStorageBackend.cpp` (`publishBlob`, `deleteExact`).
- Explicitly out of scope: GC rebuild orphaning (gc-rebuild-feature); local scratch residue (bc2); crypto-shred policy (security).

## Findings
### ad2-1 -- nested `server_root_id` still lets DROP POOL MEMBER erase a live descendant (Medium)
- Anchor: `Pool/CasServerRoot.h:76-105` (`validateServerRootId` allows `/`); `Tools/CasDecommission.cpp:146-151` (`victim_srid + "/"` prefix on catalog ns); `:220-242` (`casManifestsServerPrefix(victim_srid)`, `staging/<srid>/`, `serverRootDataPrefix(victim_srid)` — all path prefixes).
- Trigger: two members `prod` and `prod/2` (macro `{cluster}` vs `{cluster}/{replica}`). Both mount: owner/mount keys differ. `SYSTEM CAS DROP POOL MEMBER 'prod'` selects every catalog ns that equals `prod` or starts with `prod/`, including `prod/2/<uuid>`.
- Evidence: the slash suffix stops `victim` matching `victim2`. It does not stop `prod` matching `prod/2/...`. Prefix deletes of `cas/manifests/prod/`, `staging/prod/`, and `roots/prod/` also cover the descendant. `openForDecommission` only impersonates the named victim (`CasPool.cpp:816-863`); it does not test live descendants. `validateServerRootId` rejects `.` / `..` / `_files` / `_manifests` only.
- Notes: same root cause as CAS-007.

### ad2-2 -- GC blob deletes bypass the filesystem cache wrapper (Low)
- Anchor: `DiskObjectStorageCache.cpp:21-31` (cache-wrapped CAS reuses the same `ContentAddressedMetadataStorage`; only the object-storage pointer is wrapped); GC `deleteExact` goes through the CAS backend's raw store (`Gc/CasGc.cpp:668`).
- Trigger: a `type=cache` disk in front of CAS (the documented recommended shape), SELECT a part, then DROP and let GC reclaim the blobs.
- Evidence: CAS never calls `removeCacheIfExists`. Cached segments remain until LRU. Content-addressed keys mean a stale entry cannot return foreign bytes; the cache is bounded. Residual is delayed local erasure / capacity, not wrong reads.
- Notes: same root cause as CAS-084. Consequence narrowed to cache-capacity hold.

### ad2-3 -- S3 staging residue is swept only for this mount's `server_root_id` (Low)
- Anchor: `Pool/CasServerRoot.h:546-553` (sweep lists `<pool>/staging/<own srid>/` only); `Tools/CasDecommission.cpp:232-236` (victim prefix only); fsck/GC never list `staging/`.
- Trigger: crash mid-insert with `cas_staging_backend=s3`, then the node never remounts that srid.
- Evidence: objects under `staging/<dead-srid>/` are not content-addressed and are invisible to fsck/GC. Reclaim is remount of the same srid, or DROP POOL MEMBER of that srid. Cost and diagnosability, not silent corruption.
- Notes: CAS-081 residual.

### ad2-4 -- CAS never lists or aborts incomplete multipart uploads (Low)
- Anchor: `Backend/CasObjectStorageBackend.cpp:904-934` (`publishBlob` streams via ordinary `writeObject` Rewrite, which may MPU); no `ListMultipartUploads` in the CAS tree.
- Trigger: SIGKILL / OOM while a large blob is being published.
- Evidence: abort exists only on the live buffer cancel path. After 940b168 the blob path is unconditional MPU, so leftover parts are still possible; they do not appear in `ListObjectsV2` and therefore not in GC/fsck. Bucket lifecycle `AbortIncompleteMultipartUpload` is neither required nor checked.
- Notes: CAS-082 residual. Blob create is no longer conditional MPU (CAS-031 closed).

## By-design / info / non-actionable
- Lightweight DELETE and mutation hardlinks re-reference the same `BlobRef` (`adoptEvidence`, `CasPartWriteTxn.cpp:474-488`). GC cannot reclaim masked rows. CAS-083 / ordinary MergeTree.
- Pool-wide unsalted content-hash keys: a delete frees a blob only at in-degree 0. No shred verb. CAS-028.
- `FREEZE` / shadow namespaces are now `server_root_id + "/" + shadow path` (`shadowNamespace`, `ContentAddressedMetadataStorage.cpp:1356-1362`). UNFREEZE on one server cannot delete another server's frozen parts (CAS-001 closed by `335802a938f`).
- `DROP TABLE` drops only the live namespace; frozen copies keep edges until UNFREEZE.
- Token-exact GC delete; delete-marker aborts with `LOGICAL_ERROR` (`CasGc.cpp:669-672`). A blob that regained an edge is spared.

## Closed-since-2026-08-12
- Previous ad2 High "UNFREEZE deletes another server's frozen parts" (CAS-001 / #2212): closed by `335802a938f`. Shadow ns includes `server_root_id`.
- Previous "whole-catalog stillness gates every delete": namespace absence is per-row after `83c03e26b18`. Not re-raised here.
- `putIfAbsentStream` MPU residue class is obsolete as a *conditional-create* hazard; leftover MPU parts remain as ad2-4.

## Coverage
- Reviewed: user delete → ref-log; GC condemn/graduate/redelete; UNFREEZE/shadow ns; DROP POOL MEMBER prefix; lightweight-delete adopt; cache wrap; staging sweep; MPU abort surface.
- N-A: encryption-at-rest shred (docs: store-side only).
- Deferred: measured erasure SLA vs creation rate (operability sibling).

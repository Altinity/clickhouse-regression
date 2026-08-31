# ad4-migration -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `docs/en/antalya/cas/roadmap.md` (encrypted-over-CAS); `docs/en/antalya/cas/configuration.md`; `Disks/DiskEncrypted.{h,cpp}`; `ContentAddressedMetadataStorage.{h,cpp}` (no `applyNewSettings`); `MetadataStorages/IMetadataStorage.h:365-368`; `Disks/DiskSelector.cpp:176-219`; `Storages/MergeTree/DataPartStorageOnDiskBase.cpp` (`freeze` / `freezeRemote` / BACKUP); `ContentAddressedTransaction.cpp` (`generateObjectKeyForPath`, `createMetadataFile`); `Pool/CasPool.cpp` (`skip_access_check`); `ContentAddressedSettings.cpp`.
- Explicitly out of scope: `getStorageObjects` offset drop (idisk-contract); relink trust model (write-protocol / CAS-002).

## Findings
### ad4-1 -- encrypted-over-CAS is documented as unsupported and still has no config fail-fast (Low)
- Anchor: `docs/en/antalya/cas/roadmap.md:83-87`; `DiskEncrypted.h` (no `isContentAddressed` override → `IDisk` default false); `ContentAddressedTransaction.cpp` autocommit refusal for part files.
- Trigger: `<disk>encrypted</disk>` wrapping a CAS disk, `CREATE TABLE`, first `INSERT`.
- Evidence: docs now name the combination and the INSERT error (`Autocommit writes are not supported for content part files on a content-addressed disk`). `DiskEncrypted` accepts any delegate. CREATE TABLE succeeds; the first part write fails loud. No mount-time or factory gate.
- Notes: CAS-059 residual. Docs closed the "unmentioned" half.

### ad4-2 -- `always_use_copy_instead_of_hardlinks=1` still makes same-disk CAS clones throw NOT_IMPLEMENTED (Medium)
- Anchor: `StorageMergeTree.cpp` / `StorageReplicatedMergeTree.cpp` / `MutateTask.cpp` set `copy_instead_of_hardlink` from the setting; `DataPartStorageOnDiskBase.cpp:562` passes it into `Backup`; `ContentAddressedTransaction.cpp:555-557`, `:721-723` (`generateObjectKeyForPath` / `createMetadataFile` → `notYet`).
- Trigger: `ALTER TABLE cas_tbl MODIFY SETTING always_use_copy_instead_of_hardlinks = 1`, then same-disk `ATTACH PARTITION FROM` or a mutation clone.
- Evidence: nothing rejects the setting on a CAS table. The copy path needs the generic disk-transaction surface, which CAS stubs. Failure is loud. `FREEZE` and implicit zero-copy do not take this path (`supportZeroCopyReplication` excludes CAS).
- Notes: CAS-085.

### ad4-3 -- BACKUP of a CAS table outside an Atomic database is refused (Low)
- Anchor: `DataPartStorageOnDiskBase.cpp:426-427` (`SUPPORT_IS_DISABLED`, "use an Atomic database").
- Trigger: `BACKUP TABLE ordinary_db.cas_tbl`.
- Evidence: `make_temporary_hard_links` is true unless the table has a UUID. Ordinary is deprecated. Loud, documented workaround.
- Notes: CAS-121 residual.

### ad4-4 -- no CAS `applyNewSettings`; removing the disk from config leaves the mount lease renewing (Medium)
- Anchor: `IMetadataStorage.h:365-368` (default no-op); no override on `ContentAddressedMetadataStorage`; `DiskObjectStorage.cpp` forwards to metadata storage; `DiskSelector.cpp:176-219` (existing disks only `applyNewSettings`; disappeared disks log a restart warning).
- Trigger: `SYSTEM RELOAD CONFIG` after changing `cas_gc_*` / `cas_blob_hash` / `cas_server_root_id`, or deleting the disk element.
- Evidence: reload succeeds; CAS settings stay at mount-time values with no warning. A removed CAS disk keeps its `Pool` and lease workers until restart, so a successor with the same srid fails as a live double-start.
- Notes: CAS-107.

### ad4-5 -- `skip_access_check` still skips the capability battery on ETag (AWS/S3-compatible) writable mounts (Medium)
- Anchor: `Pool/CasPool.cpp:459-486`; `Backend/CasObjectStorageBackend.cpp:92-103` (`checkSkipAccessCheckSupport` throws only for generation-token / GCS).
- Trigger: `skip_access_check=1` on an AWS/MinIO CAS disk.
- Evidence: probe I/O (versioning delete-marker, conditional create/overwrite/delete, list-after-write) is skipped. GCS writable mounts now refuse the flag. Decommission still forces `skip_access_check=true` (`CasPool.cpp:829`) and skips `checkSkipAccessCheckSupport` so GCS decommission remains possible.
- Notes: CAS-030 residual. GCS half closed.

## By-design / info / non-actionable
- `freezeRemote` now opens a CAS transaction when the destination is content-addressed (`DataPartStorageOnDiskBase.cpp:687-704`) and copies through that transaction. CAS-058 / #2173 closed by `84b30f6b0d9`.
- Two CAS disks sharing pool + `server_root_id` fail the second mount (CAS-024).
- CRR / cross-region: pool identity is `_pool_meta.pool_id` only; no endpoint/bucket bind. Operator must not write a replica prefix (CAS-032). See ad6.
- Intra-pool local MOVE still copies bytes then dedups; relink is interserver-only. Performance, not a break.

## Closed-since-2026-08-12
- Previous ad4-1 (High) cross-disk ATTACH into CAS unimplemented: `freezeRemote` has a CAS transaction branch (`84b30f6b0d9`).
- Encrypted-over-CAS is no longer undocumented (`roadmap.md`).
- `non_cas_keys` startup death (CAS-106) closed by `917600b122b` (`cas_` prefix).

## Coverage
- Reviewed: encrypted wrapper; copy-instead-of-hardlinks; Ordinary BACKUP; applyNewSettings / disk removal; skip_access_check; freezeRemote; CRR identity.
- N-A: Azure CAS dialect (roadmap: not wired).
- Deferred: measured MOVE cost vs relink.

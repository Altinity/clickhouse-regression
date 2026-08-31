# alter-merge-mutation -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `ContentAddressedTransaction.cpp` (`createHardLink`, `publishStaging` merge/repoint, `moveDirectory`, `cleanupPendingTempFiles`, `generateObjectKeyForPath`), `Parts/PartFolderAccess.cpp` (`republishRef`, `ForceFresh`), `ContentAddressedMetadataStorage.cpp` (`liveNamespace`, `shadowNamespace`, `isDirectoryEmpty`, `getStorageObjects`), `DataPartStorageOnDiskBase.cpp` (`freeze`, `freezeRemote`, `clonePart`), `MergeTreeData.cpp` (`cloneAndLoadDataPart`, `freezePartitionsByMatcher`), `Backup.cpp`, `MutateTask.cpp` (`always_use_copy_instead_of_hardlinks`), `TextIndexUtils.cpp`, `DiskObjectStorageTransaction.cpp` (`copyFile` via `getStorageObjects`).
- Explicitly out of scope: blob publish protocol internals (sibling write-protocol); GC reclamation timing; encryption.

Protocol facts re-read on HEAD: `freezeRemote` now owns a CAS transaction; FREEZE/shadow namespaces include `server_root_id`; `publishStaging` merges staged deltas into a committed dest via `repointRef`.

## Findings
### alter-merge-mutation-1 -- committed-source `createHardLink` still ForceFresh-resolves the source per file (Medium)
- Anchor: `ContentAddressedTransaction.cpp:1209-1225` (`getView(..., ForceFresh)` inside `createHardLink`); `PartFolderAccess.cpp` (`ForceFresh` + default `part_folder_validate=always` → mandatory manifest HEAD); contrast `unlinkFile` memo in `force_fresh_validated_refs` (`ContentAddressedTransaction.cpp:1620-1626`).
- Trigger: mutation / FREEZE / ATTACH/REPLACE PARTITION of a committed wide part. `MutateTask` hardlinks each unchanged file.
- Evidence: there is still no per-transaction memo on the hardlink path. A 500-column part pays hundreds of sequential HEADs of the same source manifest. Cost, not correctness. Same root cause as CAS-055.
- Notes: CAS-055.

### alter-merge-mutation-2 -- `always_use_copy_instead_of_hardlinks=1` turns mutations and same-disk clones into NOT_IMPLEMENTED (Medium)
- Anchor: `MutateTask.cpp:2567,2590,3386`; `ContentAddressedTransaction.cpp:555-557` (`generateObjectKeyForPath` → `notYet`); `DiskObjectStorageTransaction.cpp:522-524`.
- Trigger: `ALTER TABLE t MODIFY SETTING always_use_copy_instead_of_hardlinks = 1` (accepted) then UPDATE/DELETE / MATERIALIZE INDEX / ATTACH/REPLACE / FREEZE-with-copy.
- Evidence: the copy path asks the dest metadata transaction for an object key. CAS implements that as `NOT_IMPLEMENTED`. No admission gate on `isContentAddressed()`. Loud; a replicated queue entry retries. Same class as CAS-085.
- Notes: CAS-085.

### alter-merge-mutation-3 -- repeated FREEZE WITH NAME merges into the existing shadow ref (Medium)
- Anchor: `ContentAddressedMetadataStorage.cpp:1880-1888` (`isDirectoryEmpty` is true for every part dir); `Backup.cpp:146-149` (throws `DIRECTORY_ALREADY_EXISTS` only when dest exists *and is non-empty*); `ContentAddressedTransaction.cpp:362-416` (`publishStaging` sees the committed dest, merges carried entries with staged ones, `repointRef`).
- Trigger: `ALTER TABLE t FREEZE WITH NAME 'b'` twice (same or overlapping parts), or FREEZE ALL then FREEZE PARTITION under the same name.
- Evidence: on a local disk the second freeze is refused. On CAS the emptiness lie lets `Backup` proceed; commit takes the committed-ref merge/repoint path and silently unions the two snapshots into one shadow ref. `UNFREEZE` then drops the merged set. Same residual as CAS-086.
- Notes: CAS-086.

### alter-merge-mutation-4 -- `getStorageObjects` omits the blob envelope offset, so server-side copy of a CA file includes header bytes (Medium)
- Anchor: `ContentAddressedMetadataStorage.cpp:1936-1940` (`StoredObject(location.key, path, location.length)` — no offset); contrast `getBlobViewPlan` at `:2062-2064` (`payload_offset = location.offset`). `CasManifestReader.cpp:156-160` (`offset = meta.blob_header_len`). Consumer: `DiskObjectStorageTransaction.cpp:522` (`copyFile` → `copyObjectToAnotherObjectStorage`).
- Trigger: MOVE / TTL move / BACKUP that copies a CA *blob* file via `getStorageObjects` + server-side copy onto a non-CA disk on the same host. Inline files return an empty key and fail loudly (`:1903-1904`).
- Evidence: the byte-read path applies the envelope window; the storage-object path does not. A copy starts at byte 0 of the blob object. Checksums on the dest usually make this loud; the copied object is still the wrong bytes. Same root cause as CAS-020.
- Notes: CAS-020.

## By-design / info / non-actionable
- Adoption of unchanged mutation files is metadata-only (`adoptEvidence`). Write amplification tracks changed columns.
- Merge publish is one `promoteBuild` after an in-transaction tmp→final rename.
- `freezeRemote` now wraps the whole clone in one transaction (`DataPartStorageOnDiskBase.cpp:687-704`). Cross-disk `ATTACH PARTITION FROM` is no longer the one-file-per-autocommit collision.
- `metadata_version.txt` is written *inside* the freeze transaction (`:585-595`). The post-clone write in `MergeTreeData.cpp:10104-10109` is a byte-equal repoint no-op when the bytes match.
- S3 staging objects of an aborted mutation are left until `sweepOwnMountStaging` (mount/decommission). Documented as the resurrect source (`cleanupPendingTempFiles` `:188-196`). Not a correctness hole.
- Shadow namespaces are `server_root_id`-prefixed (`shadowNamespace` `:1356-1361`). UNFREEZE on one server no longer deletes another server's freeze.
- Text-index tmp refs are dropped in `moveDirectory` (`:1416-1423`).
- Lightweight DELETE / patch parts are ordinary mutations/refs.

## Closed-since-2026-08-12
- CAS-058 / `freezeRemote` without a transaction (`84b30f6b0d9`).
- CAS-001 / pool-global FREEZE namespace (`335802a938f`).
- ATTACH/REPLACE `metadata_version.txt` written only after the clone commit as a required extra repoint: now written inside the clone transaction.
- Text-index `removeRecursive` silent no-op: replaced by `dropRefIfPresent`.

## Coverage
- Reviewed: lightweight/heavy ALTER, mutation hardlink vs copy, merge publish, LWD/patch, projections, text-index tmp, DROP/DETACH/ATTACH/REPLACE/MOVE/FREEZE/UNFREEZE, TTL/MOVE via `getStorageObjects`, `always_use_copy_instead_of_hardlinks`, cancellation/staging residue.
- N-A: FETCH/relink cookie (exchange sibling).
- Deferred: runtime confirmation of HEAD counts and envelope-copy checksum behavior.

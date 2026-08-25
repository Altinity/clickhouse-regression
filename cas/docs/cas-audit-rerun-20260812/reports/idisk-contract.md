# idisk-contract -- fresh audit 2026-08-12

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is.
Method: static reading of interface definitions, CAS overrides, and generic callers. No docs or comments used as evidence of intended behavior; contracts inferred from types, control flow, and how generic callers consume each method.

## Scope

Interfaces / generic layer examined:

- `src/Disks/IDisk.h`, `src/Disks/IDisk.cpp` (`copyThroughBuffers`, `asyncCopy`, `isDirectoryEmpty`)
- `src/Disks/IDiskTransaction.h`
- `src/Disks/DiskObjectStorage/MetadataStorages/IMetadataStorage.h` (`IMetadataStorage`, `IMetadataTransaction`)
- `src/Disks/DiskObjectStorage/DiskObjectStorage.{h,cpp}`
- `src/Disks/DiskObjectStorage/DiskObjectStorageTransaction.{h,cpp}` (`dispatch`, `commit`, `tryCommit`, `undo`, `copyFileImpl`, `writeFileImpl`)
- `src/Disks/DiskType.{h,cpp}` (`DataSourceDescription::operator==`)

CAS code examined:

- `MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.{h,cpp}`
- `MetadataStorages/ContentAddressed/ContentAddressedTransaction.{h,cpp}`
- `MetadataStorages/ContentAddressed/Pool/CasManifestReader.{h,cpp}` (`locate`, `BlobLocation`), `Pool/CasPool.{h,cpp}` (`locate`, `listRefs`, namespace-file API surface)

Generic callers checked for reachability:

- `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp` (`clonePart`, `copyDirectoryContentIntoTransaction`)
- `src/Storages/MergeTree/DataPartStorageOnDiskFull.{h,cpp}` (`exists`, `getRemotePaths`, `moveFile`, `replaceFile`, `copyFileFrom`, `beginTransaction`/`commitTransaction`)
- `src/Storages/MergeTree/MergeTreeData.cpp` (`clearOldTemporaryDirectories`, `isOldPartDirectory`), `MergeTask.cpp`, `MergeTreeDataWriter.cpp`, `MutateTask.cpp`
- `src/Storages/MergeTree/UniqueKey/DeleteBitmapFileOps.cpp`, `UniqueKey/SSTIndexWriter.cpp`
- `src/Storages/System/StorageSystemRemoteDataPaths.cpp`, `src/Storages/MergeTree/Backup.cpp`, `src/Backups/BackupIO_Disk.cpp`, `src/Interpreters/InterpreterCreateQuery.cpp`

Out of scope for this audit (covered by sibling audits): GC/ref-lifecycle correctness, manifest/blob wire formats, cache freshness policy (`Freshness::CachedForLoad` staleness), lease/fence semantics, concurrency and crash-consistency, security.

## Override conformance table

| Interface method | CAS behavior | Conforms? | Anchor |
| --- | --- | --- | --- |
| `IMetadataStorage::existsFile` | routes part-file paths through the manifest view; table-verbatim and mountpoint objects otherwise | Yes | `ContentAddressedMetadataStorage.cpp:955-978` |
| `IMetadataStorage::existsDirectory` | 11-shape classifier (`classifyDirectory`) over refs/namespaces/mirrored children | Yes | `ContentAddressedMetadataStorage.cpp:980-1124` |
| `IMetadataStorage::existsFileOrDirectory` | manifest file-or-subdir check, else `existsFile \|\| existsDirectory` | Yes | `ContentAddressedMetadataStorage.cpp:1126-1143` |
| `IMetadataStorage::getFileSize` | payload size from the manifest entry (not envelope) | Yes | `ContentAddressedMetadataStorage.cpp:1145-1170` |
| `IMetadataStorage::getLastModified` | ref publish time for part paths; `Timestamp(0)` for files; **throws `FILE_DOESNT_EXIST` for existing non-part directories** | No -- see finding 6 | `ContentAddressedMetadataStorage.cpp:1172-1194` |
| `IMetadataStorage::listDirectory` / `iterateDirectory` | listing built per directory shape; iterator is a materialized `StaticDirectoryIterator` (no lifetime coupling to the storage) | Yes | `ContentAddressedMetadataStorage.cpp:1196-1291` |
| `IMetadataStorage::isDirectoryEmpty` | **returns `true` unconditionally for part dirs and projection dirs** | No -- see finding 5 | `ContentAddressedMetadataStorage.cpp:1293-1305` |
| `IMetadataStorage::getStorageObjects` / `getStorageObjectsIfExist` | returns the blob key with `bytes_size = payload`, **dropping the envelope offset**; empty `remote_path` for inline entries | No -- see finding 1 | `ContentAddressedMetadataStorage.cpp:1308-1372` |
| `IMetadataStorage::getHardlinkCount` | constant `0` while `supportsHardLinks()` is `true` | Partial -- info | `ContentAddressedMetadataStorage.h:121`, `DiskObjectStorage.cpp:755-761` |
| `IMetadataStorage::createTransaction` | read-only guard, then a staging-overlay transaction | Yes | `ContentAddressedMetadataStorage.cpp:846-850` |
| `IMetadataTransaction::commit` / `tryCommit` | publishes staged parts; `tryCommit` rejects non-`NoCommitOptions`; a failed transaction cannot be re-committed | Yes | `ContentAddressedTransaction.cpp:312-361` |
| `IMetadataTransaction::tryCreateWriteBuffer` / write path | inline or content-hashed staging buffer; rejects `Append` and autocommit on blob-class part files | Yes | `ContentAddressedTransaction.cpp:531-671` |
| `IMetadataTransaction::createDirectory` / `createDirectoryRecursive` | admission check only, no state | Yes (dirs are implicit) | `ContentAddressedTransaction.cpp:673-681` |
| `IMetadataTransaction::removeDirectory` | drops the ref durably at call time; **silent no-op for any other path shape** | No -- see findings 3, 8 | `ContentAddressedTransaction.cpp:683-703` |
| `IMetadataTransaction::removeRecursive` | drops refs/namespaces/namespace-files durably at call time; **silent no-op for unclassified shapes** | No -- see findings 3, 8 | `ContentAddressedTransaction.cpp:705-780` |
| `IMetadataTransaction::createHardLink` | adopts the staged or committed manifest entry into the destination staging | Yes | `ContentAddressedTransaction.cpp:782-829` |
| `IMetadataTransaction::moveDirectory` | staged-part merge, `republishRef`, or namespace-to-namespace migration; the last is durable and non-atomic | Partial -- see finding 3 | `ContentAddressedTransaction.cpp:846-967` |
| `IMetadataTransaction::moveFile` | **requires the source to be staged in the same transaction, else `LOGICAL_ERROR`**; durable put+delete for non-part paths | No -- see findings 2, 3 | `ContentAddressedTransaction.cpp:969-1056` |
| `IMetadataTransaction::replaceFile` | erases the destination staging entry, then delegates to `moveFile` | No -- inherits finding 2 | `ContentAddressedTransaction.cpp:1058-1067` |
| `IMetadataTransaction::unlinkFile` | staged removal for part files; **durable removal at call time** for table/mountpoint files | Partial -- see finding 3 | `ContentAddressedTransaction.cpp:1069-1128` |
| `IMetadataTransaction::truncateFile` | throws `NOT_IMPLEMENTED` loudly | Yes (loud) | `ContentAddressedTransaction.cpp:1130-1135` |
| `IMetadataTransaction::chmod` | throws `NOT_IMPLEMENTED`; `supportsChmod()` is `false` so callers gate | Yes | `ContentAddressedTransaction.cpp:836-839` |
| `IMetadataTransaction::setLastModified` / `setReadOnly` | silent no-ops (admission check only) | Acceptable -- see by-design | `ContentAddressedTransaction.cpp:831-844` |
| `IMetadataTransaction::generateObjectKeyForPath` / `createMetadataFile` | throw `NOT_IMPLEMENTED` | Loud, but disables the generic copy path -- see finding 4 | `ContentAddressedTransaction.cpp:363-366, 492-495` |
| `IMetadataTransaction::getSubmittedForRemovalBlobs` | returns `{}`; `waitBlobRemoval` becomes a no-op (GC owns deletion) | Yes (by design) | `ContentAddressedTransaction.cpp:368-371` |
| `IMetadataTransaction::tryGetInFlight*` / `listInFlightDirectory` | read-your-own-writes over the staging overlay | Yes | `ContentAddressedTransaction.cpp:384-490` |
| `IMetadataTransaction::hasInFlightDirectory` | returns `false` when the path is the part directory itself (`r->file.empty()`) | Partial -- info | `ContentAddressedTransaction.cpp:453-466` |
| `IDiskTransaction::undo` (inherited) | inherited implementation removes `written_blobs` only, which CAS never populates | No -- see finding 3 | `DiskObjectStorageTransaction.cpp:698-714` |

## Findings

### idisk-contract-1 -- `getStorageObjects` returns objects that are not the file's bytes (envelope offset dropped) (High)

- **Anchor**: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp:1336-1340` and `:1368-1371`; `Pool/CasManifestReader.cpp:133-144`; `Pool/CasManifestReader.h:14-19`.
- **Trigger**: move or copy a part off a CAS disk to another object-storage disk whose `DataSourceDescription` compares equal (`ALTER TABLE ... MOVE PART/PARTITION TO DISK`, TTL moves, `MergeTreePartsMover` -> `DataPartStorageOnDiskBase::clonePart` non-CAS-destination branch at `DataPartStorageOnDiskBase.cpp:719-732` -> `IDisk::copyDirectoryContent` -> `IDisk.cpp:154-160` `asyncCopy` -> `DiskObjectStorage::copyFile`).
- **Evidence**: `Pool::locate` returns `BlobLocation{key, offset = meta.blob_header_len, length = entry.blob_size}` (`CasManifestReader.cpp:139-143`) -- the stored object begins with an envelope header and the payload starts at `offset`. `getStorageObjects` discards `offset` and constructs `StoredObject(location.key, path, location.length)`; `StoredObject` carries no offset field, so the returned object claims that key holds exactly `blob_size` bytes of file content starting at byte 0. `DiskObjectStorage::copyFile` (`DiskObjectStorage.cpp:300-317`) takes the server-side-copy branch whenever `getDataSourceDescription() == to_disk.getDataSourceDescription()`, and `DataSourceDescription::operator==` (`DiskType.cpp:35-38`) deliberately compares only `type, object_storage_type, description, is_encrypted, zookeeper_name` -- `metadata_type` is **not** part of the comparison, so a CAS disk and a plain/S3 disk over the same endpoint compare equal. `copyFileImpl` then feeds `src_metadata_storage->getStorageObjects(from_file_path)` (`DiskObjectStorageTransaction.cpp:507`) straight into `copyObjectToAnotherObjectStorage` (`:535-537`) and records the destination metadata with the same `bytes_size` (`:509`, `:549-555`). The destination file therefore begins with `blob_header_len` bytes of CAS envelope and is truncated by the same amount -- corrupt, with no error raised. Inline entries are worse in a different way: `getStorageObjects` returns `StoredObject("", path, size)` (`:1311-1312`) and `getStorageObjectsIfExist` likewise (`:1368-1369`), i.e. an empty remote key.
- **Notes**: the CAS *read* path is safe only because `DiskObjectStorage::prepareRead` special-cases content-addressed metadata (`DiskObjectStorage.cpp:808-822`) and re-applies the offset via `pipeline.needFileView(path, payload_offset, payload_end)` (`:903-904`). Every generic consumer that bypasses `prepareRead` sees the raw, offset-less object: `DiskObjectStorage::getBlobPath` (`:930-941`), `DiskObjectStorage::getUniqueId` (`:381-388`), `DataPartStorageOnDiskFull::getRemotePaths` (`DataPartStorageOnDiskFull.cpp:174-192`), `StorageSystemRemoteDataPaths.cpp:386`. Zero-copy replication is separately disabled for CAS (`DiskObjectStorage.h:51-55`), which removes one otherwise-severe consumer.

### idisk-contract-2 -- `moveFile`/`replaceFile` of a committed part file always throws `LOGICAL_ERROR` (High)

- **Anchor**: `ContentAddressedTransaction.cpp:1030-1055` (`moveFile`, final `throw ... "moveFile source not staged"`), `:1058-1067` (`replaceFile` delegates to it).
- **Trigger**: any rename of a file inside an already-published part that is not performed inside the same disk transaction that staged the source. Concretely `writeBitmapToStorage` in `src/Storages/MergeTree/UniqueKey/DeleteBitmapFileOps.cpp:58-71`: it writes `<name>.tmp` through `IDataPartStorage::writeFile` (auto-committing when the part storage has no active transaction), then calls `storage.replaceFile(tmp_name, final_name)`. Same shape at `UniqueKey/SSTIndexWriter.cpp:283`.
- **Evidence**: `DataPartStorageOnDiskFull::replaceFile`/`moveFile` (`DataPartStorageOnDiskFull.cpp:293-309`) fall through to the disk when no part-storage transaction is active. `DiskObjectStorage::moveFile` (`DiskObjectStorage.cpp:276-281`) and `DiskObjectStorage::replaceFile` (`:325-335`) each create a **fresh** `DiskObjectStorageTransaction`, so `parts` in the new `ContentAddressedTransaction` is empty by construction. `moveFile` looks the source up only in `src_st.entries` (`:1033-1035`) and, finding nothing, throws `LOGICAL_ERROR` at `:1055` -- it never consults the committed manifest (contrast `createHardLink`, which does fall back to `partAccess()->getView(...)` at `:816-828`).
- **Notes**: two separate contract problems. (a) `IDiskTransaction::moveFile`/`replaceFile` are documented as ordinary path operations on existing files; CAS supports them only for same-transaction sources. (b) The error class is wrong: `LOGICAL_ERROR` signals an internal invariant break (it aborts builds running with `abort_on_logical_error`, and generic recovery code that catches `FILE_DOESNT_EXIST` will not match it). The non-part branch of the same method does use `FILE_DOESNT_EXIST` for a missing source (`:990`, `:1012`), so the classification is inconsistent within one method.

### idisk-contract-3 -- durable mutations happen before `commit()`, and `undo()` cannot revert them (Medium)

- **Anchor**: dispatch: `DiskObjectStorageTransaction.h:128-135`. Eager durable CAS operations: `ContentAddressedTransaction.cpp:690` and `:716,721,734,740,750,761` (`dropRefIfPresent` / `dropNamespace`), `:777` (`removeNamespaceFile`), `:862-874` (`republishRef` + `putNamespaceFile` + `dropNamespace`), `:957,961`, `:992-994`, `:1014-1015`, `:1114`, `:1127`. Rollback hook: `DiskObjectStorageTransaction.cpp:698-714`. Destructor: `ContentAddressedTransaction.cpp:101-123`.
- **Trigger**: any multi-operation disk transaction on CAS where a later operation throws, and any caller that relies on `undo()`. Two concrete ones: `DataPartStorageOnDiskBase::clonePart` catches, logs "Rolling back transaction after failed attempt to move a data part" and calls `clone_transaction->undo()` (`DataPartStorageOnDiskBase.cpp:712-717`); `DiskObjectStorage::renameExchange` (`DiskObjectStorage.cpp:337-350`) issues three `moveFile` calls in one transaction, each of which is durable at call time for non-part paths.
- **Evidence**: because `transactionIsStagingOverlay()` returns `true` (`ContentAddressedMetadataStorage.h:117`), `dispatch` invokes `operation(metadata_transaction)` immediately instead of queueing it (`DiskObjectStorageTransaction.h:131-134`). The CAS implementations listed above perform externally visible pool mutations right then, not at `commit()`. The only rollback surface the interface offers, `undo()`, removes entries from `written_blobs` -- and CAS never populates `written_blobs`, because `writeFileImpl` returns the CAS buffer at `DiskObjectStorageTransaction.cpp:270-272`, before the `written_blobs[location].push_back(object)` at `:323`. So `undo()` is a guaranteed no-op for CAS. The CAS destructor abandons in-progress builds and deletes staging temp files (`ContentAddressedTransaction.cpp:101-123`, `:148-172`) but reverts no published ref/namespace change. The RENAME-TABLE branch is explicit about the resulting split state and re-throws after logging (`:876-884`), which confirms the partial-application window is real rather than theoretical.
- **Notes**: the eager model is clearly intentional (the generic layer even asserts that a staging-overlay transaction queued nothing: `DiskObjectStorageTransaction.cpp:570-573`, `:619-622`). The contract gap is that `IDiskTransaction::undo()` remains part of the interface and callers act on it; a CAS override that at least throws or logs would stop callers from believing a rollback occurred.

### idisk-contract-4 -- `generateObjectKeyForPath` / `createMetadataFile` throw, disabling the generic copy path (Medium)

- **Anchor**: `ContentAddressedTransaction.cpp:363-366`, `:492-495` (both route into `notYet(...)` at `:83-90`, `NOT_IMPLEMENTED`).
- **Trigger**: `always_use_copy_instead_of_hardlinks = 1` on a table whose parts live on a CAS disk. `MutateTask.cpp:2490-2493` (and the projection variant at `:2513-2516`) calls `IDataPartStorage::copyFileFrom`, which goes to `DataPartStorageOnDiskFull.cpp:338-354` -> `DiskObjectStorage::copyFile` -> `copyFileImpl`, where `metadata_transaction->generateObjectKeyForPath(to_file_path)` is called eagerly at `DiskObjectStorageTransaction.cpp:509` while materializing `blobs_to_create`.
- **Evidence**: `copyFileImpl` has no alternative path -- the key generation happens before any CAS-aware branch, so every `copyFile` whose *destination* is CAS fails with `NOT_IMPLEMENTED`. `writeFileUsingBlobWritingFunction` fails the same way one line earlier (`DiskObjectStorageTransaction.cpp:388`), and would fail again at `createMetadataFile` (`:408`) if it got past that.
- **Notes**: this is a loud failure rather than corruption, so severity is Medium; the cost is that a supported MergeTree setting and the whole `IDisk::copyFile`-into-CAS surface are unusable, and the message points at the disk transaction rather than at the setting.

### idisk-contract-5 -- `isDirectoryEmpty` reports every part directory as empty, defeating non-empty guards (Medium)

- **Anchor**: `ContentAddressedMetadataStorage.cpp:1293-1305` (returns `true` for `PartDir` and projection-dir routes before consulting anything), versus `listDirectory` for the same shapes at `:1256-1265`.
- **Trigger**: `DiskObjectStorage::removeDirectory(<part dir>)` -- `DiskObjectStorage.cpp:440-448` guards the removal with `if (!isDirectoryEmpty(path)) throw CANNOT_RMDIR`. On CAS the guard never fires for a part directory, so the call proceeds to `ContentAddressedTransaction::removeDirectory`, which drops the ref (`ContentAddressedTransaction.cpp:688-702`) -- a fully populated part is deleted where every other metadata storage would have refused with `CANNOT_RMDIR`.
- **Evidence**: the base contract is spelled out by the default implementation `return !iterateDirectory(path)->isValid();` (`IMetadataStorage.h:234-237`), and `IDiskTransaction::removeDirectory` is documented as "Throws exception if it's not a directory or if directory is not empty". CAS's `listDirectory`/`iterateDirectory` do return the part's children for the same path, so the two answers contradict each other. The same guard is used as a safety check by `MergeTree/Backup.cpp:146` (`existsFileOrDirectory(dst) && !isDirectoryEmpty(dst)`) and `Backups/BackupIO_Disk.cpp:116,125`.
- **Notes**: `isDirectoryEmpty` on a table directory or intermediate path still goes through `iterateDirectory` and is consistent; only the part-dir and projection-dir short-circuits are affected.

### idisk-contract-6 -- `getLastModified` throws for directories that `existsDirectory` reports as present (Low)

- **Anchor**: `ContentAddressedMetadataStorage.cpp:1172-1194`.
- **Trigger**: `getLastModified` on `.../detached`, `.../moving`, a table directory, or any generic intermediate directory -- all of which `existsDirectory` answers `true` for (`:1096-1121`).
- **Evidence**: only routes with a non-empty `ref` reach `resolve_stamp` (`:1185-1190`); everything else falls to `existsFile(path)`, which returns `false` for directories and for part paths with an empty `file` component (`:969-971`), so the method throws `FILE_DOESNT_EXIST` at `:1193`. This makes the inherited `getLastModifiedIfExists` (`IMetadataStorage.h:210-215`), whose whole purpose is to return `nullopt` instead of throwing, throw for an existing directory.
- **Notes**: reachability in product code is thin -- `MergeTreeData::isOldPartDirectory` (`MergeTreeData.cpp:3314-3324`) only passes part directories -- so this is Low. Related but *not* CAS-specific: when the ref disappears between `iterateDirectory` and `getLastModified`, CAS raises `DB::Exception(FILE_DOESNT_EXIST)`, which the surrounding cleanup loop does not catch (it only handles `fs::filesystem_error` with `no_such_file_or_directory`, `MergeTreeData.cpp:3421-3429`) and the whole sweep aborts; `MetadataStorageFromPlainObjectStorage::getLastModified` behaves identically (`MetadataStorageFromPlainObjectStorage.cpp:92-98`), so this is a pre-existing object-storage-wide gap rather than a CAS regression.

### idisk-contract-7 -- `getHardlinkCount` is constant zero while the disk advertises hardlink support (Low)

- **Anchor**: `ContentAddressedMetadataStorage.h:121` (`uint32_t getHardlinkCount(const std::string &) const override { return 0; }`) versus `DiskObjectStorage::supportsHardLinks()` returning `true` for content-addressed storages (`DiskObjectStorage.cpp:755-761`).
- **Trigger**: any generic caller that uses the reference count to decide whether data is still shared -- `IDisk::getRefCount` -> `DataPartStorageOnDiskFull::getRefCount` (`DataPartStorageOnDiskFull.cpp:169-172`).
- **Evidence**: CAS both dedups blobs by content and implements `createHardLink` by adopting the same manifest entry into a second ref (`ContentAddressedTransaction.cpp:782-829`), so a blob is very often referenced more than once; the reported count is nevertheless always `0`, i.e. "no references at all", which is neither the true count nor a conservative one.
- **Notes**: no reachable data-loss path was confirmed, because blob deletion on CAS is owned by GC rather than by ref-count-driven callers, and zero-copy replication (the main ref-count consumer) is disabled for CAS. Recorded so a future caller does not silently inherit a wrong answer.

### idisk-contract-8 -- `removeRecursive` / `removeDirectory` silently succeed on unclassified paths (Low)

- **Anchor**: `ContentAddressedTransaction.cpp:683-703` (`removeDirectory` returns without action unless the path is a part directory) and `:705-780` (`removeRecursive` falls off the end of the function when no shape matches).
- **Trigger**: `DiskObjectStorage::removeSharedRecursive` / `removeDirectory` on a path CAS cannot classify -- e.g. an intermediate `store/<prefix>` level, or a mountpoint-namespace file path passed to `removeRecursive`.
- **Evidence**: both methods are structured as a sequence of shape matches with an implicit "do nothing" fall-through; there is no final `else` that throws or logs. `IDiskTransaction::removeRecursive` is specified as "Remove file or directory with all children ... Throws exception if file doesn't exist", so a caller that gets no exception is entitled to assume the subtree is gone.
- **Notes**: contrast the shadow branch at `:727-735`, which does log the keys it refused to touch. Low because no confirmed product caller depends on the missing removal, but it is the classic "silent no-op instead of loud unsupported" shape the audit brief asks about.

## By-design / info / non-actionable

- **Eager (non-deferred) transaction execution is intentional and enforced.** `transactionIsStagingOverlay()` (`ContentAddressedMetadataStorage.h:117`) makes `dispatch` run operations immediately, and both `commit()` and `tryCommit()` assert that a staging-overlay transaction queued nothing (`DiskObjectStorageTransaction.cpp:570-573`, `:619-622`) -- a mutating method that bypassed `dispatch` fails loudly. Only the *durability* of the eager side effects is a finding (idisk-contract-3), not the eagerness.
- **Directory creation is a no-op.** `createDirectory`/`createDirectoryRecursive` only run the admission check (`ContentAddressedTransaction.cpp:673-681`); directories exist implicitly as manifest path prefixes and are answered consistently by `existsDirectory`/`listDirectory`.
- **`setLastModified` / `setReadOnly` are silent no-ops** (`:831-844`). `supportsStat()`/`supportsChmod()` are `false` (`ContentAddressedMetadataStorage.h:108-109`) and `getLastModified` derives its answer from ref publish time, so there is no mutable attribute to store; callers gate on the capability flags.
- **`truncateFile` and `chmod` throw `NOT_IMPLEMENTED` loudly** (`:1130-1135`, `:836-839`) -- the desired behavior for unsupported operations. No MergeTree caller of `truncateFile` was found.
- **`getSubmittedForRemovalBlobs` returning `{}`** (`:368-371`) makes `waitBlobRemoval` (`DiskObjectStorageTransaction.cpp:609-610`) a no-op; deletion is GC-owned in CAS, so there is nothing for the disk layer to wait on.
- **Directory iterator lifetime is safe.** `iterateDirectory` materializes the full listing into a `StaticDirectoryIterator` (`ContentAddressedMetadataStorage.cpp:1281-1291`), so the iterator holds no reference to pool state and cannot observe a mid-iteration pool swap or shutdown.
- **Empty-enumeration answers are fail-closed.** `listDirectory` confirms pool identity before returning an empty result for table directories and detached containers (`:1236-1237`, `:1245-1246`, `:818-844`), so an erased or unreachable backing does not masquerade as "no parts".
- **`hasInFlightDirectory` ignores the part directory itself** (`ContentAddressedTransaction.cpp:453-456` requires a non-empty `file`), so `DataPartStorageOnDiskFull::exists()` (`DataPartStorageOnDiskFull.cpp:60-66`) does not see a part staged in the current transaction. Every call site inspected (`MergeTask.cpp:581`, `MergeTreeDataWriter.cpp:909`, `:1078`, `MergeTreeData.cpp:11218`, `DataPartsExchange.cpp:1010`) runs before or immediately after `beginTransaction()`, when nothing is staged yet, so no reachable defect was confirmed.
- **`tryCommit` rejects commit options other than `NoCommitOptions`** with `LOGICAL_ERROR` (`ContentAddressedTransaction.cpp:354-361`). `isTransactional()` is `false` for CAS, so `DiskObjectStorage::createDirectories` takes the plain `commit()` branch (`DiskObjectStorage.cpp:419-438`) and no Keeper-style option variant reaches the CAS transaction on the paths inspected.
- **Autocommit is refused for blob-class part files** (`ContentAddressedTransaction.cpp:539-544`), which is what forces part writes through an explicit transaction; this is a deliberate narrowing of `IDisk::writeFile`, and it fails loudly with `NOT_IMPLEMENTED`.

## Coverage

**Reviewed**

- Full `IMetadataStorage` and `IMetadataTransaction` override surface of `ContentAddressedMetadataStorage` / `ContentAddressedTransaction`, method by method, against the base declarations.
- Atomicity/deferral: `dispatch` template, `commit`, `tryCommit`, `undo`, and the staging-overlay assertions in `DiskObjectStorageTransaction`.
- Abandoned-transaction behavior: `~ContentAddressedTransaction`, `cleanupPendingTempFiles`, build `abandon()`.
- `existsFile` / `existsDirectory` / `existsFileOrDirectory` / `isDirectoryEmpty` / `listDirectory` / `iterateDirectory` consistency, including consistency with the in-flight (`*InFlight*`) overlay.
- `getFileSize` (payload vs envelope), `getLastModified`, `getStorageObjects` / `getStorageObjectsIfExist`, `getHardlinkCount`.
- `createHardLink` / `replaceFile` / `moveFile` / `moveDirectory` / `removeRecursive` / `removeDirectory` / `unlinkFile` / `truncateFile` semantics.
- Write-buffer contracts (`CaContentWriteBuffer`, `CaInlineWriteBuffer`, `tryCreateWriteBuffer`, `WriteMode::Append` rejection) and read-after-write within one transaction (`tryReadFileInFlight`, `tryGetInFlightFileSize`, `tryGetInFlightStorageObjects`).
- Error classification (`FILE_DOESNT_EXIST` vs `LOGICAL_ERROR` vs `NOT_IMPLEMENTED` vs CAS transient/lifecycle errors) against what generic callers catch.
- Reachability through `DataPartStorageOnDiskFull`/`Base`, `MergeTreeData`, `MergeTask`, `MutateTask`, `MergeTreeDataWriter`, `IDisk::copyDirectoryContent`, backup entry points, `StorageSystemRemoteDataPaths`, `InterpreterCreateQuery`.

**Not applicable**

- `IMetadataStorage` replication hooks (`getBlobsToRemove`, `recordAsRemoved`, `getBlobsToReplicate`, `recordAsReplicated`, `hasUnreplicatedBlobs`) -- CAS does not override them and the CAS disk is not configured for the multi-location cluster path.
- Zero-copy replication contract -- explicitly disabled for `MetadataStorageType::CAS` (`DiskObjectStorage.h:51-55`).
- `getSerializedMetadata`, `readFileToString`, `readInlineDataToString`, `stat`, `getLastChanged`, `updateCache*`, `dropCache` -- not overridden by CAS; the base implementations throw `NOT_IMPLEMENTED` or no-op, and `supportsStat()` is `false`.
- Cache-layer wrapper (`MetadataStorageFromCacheObjectStorage`) -- pure delegation, adds no CAS-specific contract behavior.

**Deferred to sibling audits**

- Staleness of `Freshness::CachedForLoad` in `existsFile`/`getFileSize`/`getStorageObjects` (read-protocol / concurrency audits).
- Whether an eagerly dropped ref is recoverable, and GC interaction with abandoned builds and staging keys (gc-protocol / crash-consistency audits).
- Lease/fence admission (`checkOpAdmitted`, `CasOpAdmission::TruthAbsent` turning probes and removals into silent successes) -- treated here only as an interface-shape observation; its correctness belongs to the mounts/leases audit.
- Envelope header format and blob hashing (write-protocol / formats audits); this audit only used `blob_header_len` as evidence for the offset mismatch in finding 1.

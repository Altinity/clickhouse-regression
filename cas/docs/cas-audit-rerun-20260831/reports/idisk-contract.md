# idisk-contract -- fresh audit 2026-08-31

## Scope
- Interfaces: `src/Disks/IDisk.h`, `src/Disks/IDisk.cpp` (`copyThroughBuffers`, `asyncCopy`), `src/Disks/IDiskTransaction.h`, `src/Disks/DiskObjectStorage/MetadataStorages/IMetadataStorage.h`, `DiskObjectStorage.{h,cpp}`, `DiskObjectStorageTransaction.{h,cpp}`, `DiskType.cpp` (`DataSourceDescription::operator==`)
- CAS: `ContentAddressedMetadataStorage.{h,cpp}`, `ContentAddressedTransaction.{h,cpp}`, `Pool/CasManifestReader.{h,cpp}` (`locate`)
- Generic callers: `DataPartStorageOnDiskBase.cpp` (`freezeRemote`, `clonePart`, `copyDirectoryContentIntoTransaction`), `DataPartStorageOnDiskFull.cpp`, `MergeTreeData.cpp`, `UniqueKey/DeleteBitmapFileOps.cpp`, `UniqueKey/SSTIndexWriter.cpp`, `MergeTree/Backup.cpp`, `Backups/BackupIO_Disk.cpp`
- Assigned surface: directory ops, hardlink/copy, exists/list/stat, `removeRecursive`, `getStorageObjects`, freeze/clone, atomic writes, fake transaction
- Out of scope: GC/ref-lifecycle, wire formats, lease/fence correctness, cache freshness (beyond the `getStorageObjects` offset)

## Override conformance table

| Interface method | CAS behavior | Conforms? | Anchor |
|---|---|---|---|
| `existsFile` | manifest / verbatim / mountpoint | Yes | `ContentAddressedMetadataStorage.cpp` existsFile |
| `existsDirectory` | 11-shape `classifyDirectory` | Yes | same, `classifyDirectory` |
| `existsFileOrDirectory` | file or directory | Yes | |
| `getFileSize` | payload size, not envelope | Yes | |
| `getLastModified` | ref publish time for part paths; epoch for files; **throws `FILE_DOESNT_EXIST` for existing non-part directories** | No — idisk-contract-6 | `:1715-1744` |
| `listDirectory` / `iterateDirectory` | per-shape listing; `StaticDirectoryIterator` | Yes | `:1747-1872` |
| `isDirectoryEmpty` | **`true` for every part dir and projection dir** | No — idisk-contract-5 | `:1874-1893` |
| `getStorageObjects` / `IfExist` | blob key + **payload length, envelope offset dropped**; empty remote key for inline | No — idisk-contract-1 | `:1895-1977` |
| `getHardlinkCount` | constant `0`; `supportsHardLinks()` is `true` | Partial — info | `.h:271`; `DiskObjectStorage.cpp:755-768` |
| `supportsStat` / `stat` | `false`; base throws | Yes (gated) | `.h:239` |
| `createTransaction` | staging-overlay txn after read-only check | Yes | |
| `transactionIsStagingOverlay` | `true` — eager dispatch, empty FIFO | Yes (intentional fake batch) | `.h:267` |
| `supportsAtomicFileWrites` | `true` — ref publish is the atomic name | Yes for part refs | `.h:268` |
| `commit` / `tryCommit` | publishes staged parts; `tryCommit` rejects non-`NoCommitOptions` | Yes | `ContentAddressedTransaction.cpp` commit |
| `tryCreateWriteBuffer` | hash-on-write; rejects Append on part files; autocommit refused for `partFileMustStayBlob` | Yes (narrowed, loud) | `:772-796` |
| `createDirectory*` | admission only, no state | Yes (dirs implicit) | `:1011-1014` |
| `removeDirectory` | drops part ref at **call time**; no-op for other shapes | No — idisk-contract-3, -8 | `:1016-1055` |
| `removeRecursive` | drops refs/namespaces/files at call time; **falls off the end for unclassified paths** | No — idisk-contract-3, -8 | `:1057-1165` |
| `createHardLink` | adopt staged or committed manifest entry | Yes | `:1167-1226` |
| `moveDirectory` | overlay re-key, `republishRef`, or non-atomic table-namespace migrate | Partial — idisk-contract-3 | `:1248-1436` |
| `moveFile` / `replaceFile` | staged re-key, or **`LOGICAL_ERROR` if source not staged** | No — idisk-contract-2 | `:1438-1576` |
| `unlinkFile` | staged drop or `content_removed` mark | Partial — idisk-contract-3 | `:1578+` |
| `truncateFile` / `chmod` | `NOT_IMPLEMENTED` | Yes (loud) | |
| `setLastModified` / `setReadOnly` | gated no-ops | Acceptable | `:1228-1246` |
| `generateObjectKeyForPath` / `createMetadataFile` | `NOT_IMPLEMENTED` | Loud; kills generic copy-into-CAS — idisk-contract-4 | `:555-557`, `:721-723` |
| `getSubmittedForRemovalBlobs` | `{}` | Yes (GC owns delete) | |
| `tryGetInFlight*` / `listInFlightDirectory` | staging overlay | Yes | |
| `hasInFlightDirectory` | false for the bare part dir | Partial — info | `.h:68-69` |
| `IDiskTransaction::undo` | inherited; removes `written_blobs` only; CAS never populates it | No — idisk-contract-3 | `DiskObjectStorageTransaction.cpp` undo |
| `IDisk::copyFile` (same `DataSourceDescription`) | server-side copy of `getStorageObjects` | No — idisk-contract-1 | `DiskObjectStorage.cpp:291-317` |
| `freezeRemote` / `clonePart` into CAS | one owned transaction + byte copy | Yes (CAS dest) | `DataPartStorageOnDiskBase.cpp:668-837` |
| `clonePart` / `copyDirectoryContent` **from** CAS to same-endpoint non-CAS | `copyFile` server-side path | No — idisk-contract-1 | `:815-820` + `IDisk.cpp:144-160` |

## Findings

### idisk-contract-1 -- `getStorageObjects` drops the envelope offset; same-endpoint copy then stores the wrong bytes (High)
- Anchor: `ContentAddressedMetadataStorage.cpp:1934-1940` and `:1974-1977`; `Pool/CasManifestReader` `locate` (key, `offset = blob_header_len`, `length = payload`); `DiskObjectStorage.cpp:291-317` (`copyFile`); `DiskObjectStorageTransaction.cpp:522+` (`copyFileImpl`); `DiskType.cpp:35-38`; `IDisk.cpp:144-160`; `DataPartStorageOnDiskBase.cpp:815-820` at ceee42c
- Trigger: `ALTER TABLE … MOVE PART/PARTITION TO DISK` (or any `clonePart` / `IDisk::copyDirectoryContent`) **from a CAS disk to a plain object-storage disk whose `DataSourceDescription` compares equal** — same `type`, `object_storage_type`, endpoint `description`, encryption, ZooKeeper name. `metadata_type` is not in `operator==`. Typical shape: two S3 disks on one bucket, one `metadata_type=cas`, one plain.
- Evidence: `Pool::locate` returns a payload window. `getStorageObjects` builds `StoredObject(location.key, path, location.length)` and **discards `offset`**. `StoredObject` has no range field. `DiskObjectStorage::prepareRead` is safe: it uses `getBlobViewPlan` and `pipeline.needFileView(path, payload_offset, payload_end)` (`DiskObjectStorage.cpp:824-921`). `copyFile` does not: when descriptions match it takes the server-side-copy branch, feeds `getStorageObjects` into `copyObjectToAnotherObjectStorage`, and records the destination metadata with that `bytes_size`. The destination object is the CAS envelope plus a truncated payload, with no error. Inline entries return `StoredObject("", path, size)` (`:1903-1904`, `:1974-1975`) — empty remote key. Comments at `:1937-1939` and `.h:137-139` admit the offset is only applied on the CA read branch and that a bypassing consumer "fails loudly, never reads wrong bytes". That last claim is false for this copy path: it succeeds and writes wrong bytes. `getBlobPath` (`:947-958`), `getUniqueId` (`:381-387`), and `DataPartStorageOnDiskFull::getRemotePaths` also see the offset-less object (wrong id/size, not silent user data).
- Notes: Same root cause as 2026-08-12 idisk-contract-1 / prior CAS-### on envelope-unaware copy. **CAS destination** of `freezeRemote` / `clonePart` is now a single transaction + `writeFile` byte copy (`84b30f6`, `DataPartStorageOnDiskBase.cpp:688-706`, `:790-813`) and does not use this path. The remaining High is CAS **source** → equal-description non-CAS dest. Zero-copy replication stays disabled for CAS.

### idisk-contract-2 -- `moveFile`/`replaceFile` of a committed part file throws `LOGICAL_ERROR` (Medium)
- Anchor: `ContentAddressedTransaction.cpp:1552-1557`; `replaceFile` at `:1560-1576`; `DataPartStorageOnDiskFull.cpp:339-345`; `UniqueKey/DeleteBitmapFileOps.cpp:58-71`; `UniqueKey/SSTIndexWriter.cpp:283` at ceee42c
- Trigger: UniqueKey delete-bitmap or SST index write on a CAS part: `writeFile(<name>.tmp)` (auto-commit when the part storage has no open transaction) then `replaceFile(tmp, final)`. `DiskObjectStorage::replaceFile` opens a **new** transaction, so staging is empty.
- Evidence: `moveFile` only re-keys an entry found in `src_st.entries` (`:1527-1550`). If the source is not staged it throws `LOGICAL_ERROR` ("moveFile source not staged"). `createHardLink` *does* fall back to the committed manifest (`:1209-1226`); `moveFile` does not. `tryCreateWriteBuffer` allows autocommit of inline-eligible part files (`:784-796`); delete-bitmap / SST names are not in `partFileMustStayBlob`, so the `.tmp` can publish before `replaceFile`. The error class is `LOGICAL_ERROR` (aborts under `abort_on_logical_error`); the non-part branch of the same function uses `FILE_DOESNT_EXIST` (`:1476`, `:1500`). No UniqueKey / `isContentAddressed` gate exists in MergeTree.
- Notes: Fail-closed and loud, so not High (brief). The in-file comment that this branch "has no live caller" is false — see codeonly-line-2. Same root cause as 2026-08-12 idisk-contract-2.

### idisk-contract-3 -- durable mutations run before `commit()`, and `undo()` cannot revert them (Medium)
- Anchor: `IMetadataStorage.h:326-330`; `ContentAddressedMetadataStorage.h:265-267`; `DiskObjectStorageTransaction.h` `dispatch`; eager `dropRefIfPresent` / `dropNamespace` / `republishRef` / verbatim put+delete at `ContentAddressedTransaction.cpp:1018-1024`, `:1037`, `:1075-1116`, `:1248-1308`, `:1430`, `:1478-1480`; `DiskObjectStorageTransaction` `undo`; `DataPartStorageOnDiskBase.cpp:699-702`, `:809-812` at ceee42c
- Trigger: a multi-op disk transaction that throws after `removeDirectory` / `moveDirectory` / non-part `moveFile`, then the caller invokes `undo()` — `clonePart` and `freezeRemote` both do (`DataPartStorageOnDiskBase.cpp:701`, `:749`, `:811`)
- Evidence: `transactionIsStagingOverlay()` makes `dispatch` run the metadata method immediately. Several verbs mutate the pool at call time; the comments at `:1018-1024` and `:1253-1254` call this the "everything-immediate model" and point at MergeTree compensation. `undo()` only deletes `written_blobs`. CAS writes go through `tryCreateWriteBuffer` and never populate `written_blobs`, so `undo()` is a no-op. The destructor abandons uncommitted builds and local staging; it does not un-drop a published ref or un-rename a namespace. RENAME TABLE logs the split and rethrows (`:1300-1307`). Callers that log "Rolling back transaction" (`:810`) have not rolled anything durable back.
- Notes: Eagerness is intentional (commit asserts the FIFO is empty). The contract gap is `IDiskTransaction::undo()` remaining part of the interface while CAS makes it a guaranteed no-op. Same root cause as 2026-08-12 idisk-contract-3.

### idisk-contract-4 -- `generateObjectKeyForPath` / `createMetadataFile` throw, so generic copy-into-CAS is unusable (Medium)
- Anchor: `ContentAddressedTransaction.cpp:555-557`, `:721-723`; `DiskObjectStorageTransaction.cpp` `copyFileImpl` / `writeFileUsingBlobWritingFunction` (key generation before any CA branch) at ceee42c
- Trigger: `always_use_copy_instead_of_hardlinks = 1` on a CAS table (`MutateTask` → `copyFileFrom` → `DiskObjectStorage::copyFile` → `copyFileImpl`), or any `IDiskTransaction::copyFile` whose **destination** is CAS
- Evidence: `copyFileImpl` calls `generateObjectKeyForPath(to_file_path)` while building `blobs_to_create`. CAS throws `NOT_IMPLEMENTED` (`notYet`). There is no alternative path. `freezeRemote` / `clonePart` into CAS avoid this via `writeFile` (`DataPartStorageOnDiskBase.cpp:637-663`). The generic copy-into-CAS surface and that MergeTree setting remain unusable.
- Notes: Loud, so Medium. Same as 2026-08-12 idisk-contract-4; the new freeze/clone branches shrink reachability but do not implement the generic method.

### idisk-contract-5 -- `isDirectoryEmpty` reports every part directory as empty (Medium)
- Anchor: `ContentAddressedMetadataStorage.cpp:1874-1893` vs `listDirectory` PartDir/ProjectionDir at `:1827-1840`; `DiskObjectStorage.cpp` `removeDirectory` `CANNOT_RMDIR` guard; `IDiskTransaction.h:99`; `MergeTree/Backup.cpp` and `Backups/BackupIO_Disk.cpp` non-empty checks at ceee42c
- Trigger: `removeDirectory(<part dir>)` on CAS; also any backup/generic guard `existsFileOrDirectory(dst) && !isDirectoryEmpty(dst)` on a CAS part path
- Evidence: Default contract is `!iterateDirectory(path)->isValid()` (`IMetadataStorage.h:248-251`). `IDiskTransaction::removeDirectory` "Throws exception if … directory is not empty". CAS short-circuits part and projection dirs to `true` so `removeDirectory` proceeds to `dropRefIfPresent` (comments at `:1880-1883` and `.h:346-348` state this is deliberate). `listDirectory` for the same path returns the part's children. The two answers contradict. Table / detached-container dirs still use the listing. A vanished disk also reports empty (`:1876-1879`) so DROP can finish — that part is the admission matrix, not this finding.
- Notes: Intentional for MergeTree fast-remove. Still a contract break for every caller that trusts `isDirectoryEmpty`. Same as 2026-08-12 idisk-contract-5.

### idisk-contract-6 -- `getLastModified` throws for directories that `existsDirectory` reports as present (Low)
- Anchor: `ContentAddressedMetadataStorage.cpp:1715-1744` at ceee42c
- Trigger: `getLastModified` on `…/detached`, `…/moving`, a table directory, or a generic intermediate directory
- Evidence: Only routes with a non-empty `ref` take `resolve_stamp`. Everything else falls through to `existsFile` (false for directories) and throws `FILE_DOESNT_EXIST`. Inherited `getLastModifiedIfExists` (`IMetadataStorage.h:224-228`) therefore throws for an existing directory. `MergeTreeData::isOldPartDirectory` only passes part directories (those have a stamp), so product reachability is thin.
- Notes: Same as 2026-08-12 idisk-contract-6.

### idisk-contract-7 -- `getHardlinkCount` is always 0 while the disk advertises hardlinks (Low)
- Anchor: `ContentAddressedMetadataStorage.h:271`; `DiskObjectStorage.cpp:755-768`; `createHardLink` at `ContentAddressedTransaction.cpp:1167-1226` at ceee42c
- Trigger: `IDisk::getRefCount` → `DataPartStorageOnDiskFull::getRefCount`
- Evidence: CAS implements `createHardLink` by adopting the same manifest entry and advertises `supportsHardLinks() == true` so mutations/lightweight delete stay enabled. `getHardlinkCount` is still `0`. Blob deletion is GC-owned; zero-copy replication is disabled. No data-loss path confirmed.
- Notes: `supportsHardLinks` comments now explain the capability gate. The count is still neither true nor conservative.

### idisk-contract-8 -- `removeRecursive` / `removeDirectory` silently succeed on unclassified paths (Low)
- Anchor: `ContentAddressedTransaction.cpp:1016-1055` (`removeDirectory` returns unless the path is a part dir); `:1057-1165` (`removeRecursive` has no final `else`) at ceee42c
- Trigger: `removeSharedRecursive` / `removeDirectory` on `store/<prefix>` or another shape `classifyDirectory` does not map to a drop
- Evidence: `IDiskTransaction::removeRecursive` "Throws exception if file doesn't exist". CAS is a sequence of shape matches with implicit success. Callers may assume the subtree is gone. Shadow unattributable keys are logged and left (`:1088-1104`); that branch is loud. The fall-through is not.
- Notes: Same as 2026-08-12 idisk-contract-8. No confirmed product caller depends on the missing removal.

## By-design / info / non-actionable
- **Staging-overlay / fake batch transaction is explicit.** `transactionIsStagingOverlay()` is the documented IMetadataStorage flag; `dispatch` runs immediately; commit asserts the FIFO is empty. Only undo-of-durable-side-effects is a finding.
- **Atomic part writes.** `supportsAtomicFileWrites() == true` matches "no partial content under the final name": the ref is published at `commit`. Autocommit of column blobs is refused loudly.
- **Directory create is a no-op.** Object storage has no directory objects; `existsDirectory` / `listDirectory` answer the virtual tree.
- **`setLastModified` / `setReadOnly` no-ops** after the Write gate. `supportsStat` / `supportsChmod` are false.
- **`getSubmittedForRemovalBlobs` empty** — GC deletes blobs.
- **`iterateDirectory` materializes** a `StaticDirectoryIterator`; no lifetime coupling to the pool.
- **Empty table-root listing** is fail-closed (`confirmPoolIdentityForEmptyEnumeration`).
- **`hasInFlightDirectory` ignores the bare part dir** so a dedup-rejected tmp is not a real directory. Inspected MergeTree callers run before/just after `beginTransaction`.
- **`freezeRemote` / `clonePart` into CAS** now use one transaction (`84b30f6`). That closes the old per-file autocommit collision. Their `undo()` on failure still cannot revert a durable ref drop (idisk-contract-3) but the happy path no longer publishes one-file manifests.
- **FREEZE shadow namespaces include `server_root_id`** (`shadowNamespace` / `shadowScope`). Not an IDisk defect.

## Closed-since-2026-08-12
- Per-file autocommit `freezeRemote` / `clonePart` into CAS (prior CAS-058 / #2173) — closed by the owned-transaction branch (`84b30f6`, `DataPartStorageOnDiskBase.cpp:688-706`, `:790-813`).
- No other idisk-contract finding from 2026-08-12 is gone. 1–8 are re-derived on HEAD; 3/5/7 are now commented as intentional but still violate the generic interface for non-MergeTree callers.

## Coverage
- Reviewed: full `IMetadataStorage` / `IMetadataTransaction` override set; `dispatch` / `commit` / `tryCommit` / `undo`; destructor / staging cleanup; exists/list/stat/empty consistency; `getFileSize` / `getLastModified` / `getStorageObjects*` / `getHardlinkCount`; hardlink / move / replace / removeRecursive / removeDirectory / unlink / truncate; write-buffer + autocommit rules; freeze/clone CAS vs non-CAS branches; `DataSourceDescription::operator==`; UniqueKey / SST `replaceFile`; error classes vs generic catchers.
- N/A: replication hooks (`getBlobsToRemove` …) — not overridden; zero-copy — disabled for CAS; `getSerializedMetadata` / `readFileToString` / `stat` — base `NOT_IMPLEMENTED` / `supportsStat() == false`; cache metadata wrapper — forwards.
- Deferred: `Freshness::CachedForLoad` staleness (read-protocol; `allow_stale` is discarded — codeonly-line-1); recoverability of an eagerly dropped ref (gc-protocol / crash-consistency); `TruthAbsent` admission turning Probe/Remove into success (mounts/leases).

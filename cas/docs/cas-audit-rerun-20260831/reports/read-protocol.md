# read-protocol -- fresh audit 2026-08-31

## Scope
- Read path at `ceee42c51a06cb05e2c9a2d811ef7e1726825552` (worktree `/Volumes/workspace/altinity-clickhouse/cas-pr-2159-ceee42c`).
- Files/dirs examined (read in full or in the relevant regions):
  `Pool/CasRefLedger.cpp` (`resolveRef`/`listRefs`), `Parts/PartFolderAccess.{h,cpp}`
  (view cache, single-flight, freshness), `Pool/CasManifestReader.{h,cpp}`,
  `Formats/CasPartManifestFormat.cpp` (decode, sampled),
  `Formats/CasBlobEnvelopeFormat.cpp` (header_len, sampled),
  `ContentAddressedMetadataStorage.{h,cpp}` (`existsFile`/`getFileSize`/`getStorageObjects`/
  `getStorageObjectsIfExist`/`tryGetInManifestBytes`/`prepareInManifestRead`/`getBlobViewPlan`/
  `readBlobPayload`/`physicalKey`),
  `ContentAddressedTransaction.cpp` (in-flight read/size/storage-objects),
  `DiskObjectStorage.cpp` (`prepareRead`, `copyFile`, `getUniqueId`),
  `DiskObjectStorageTransaction.cpp` (`copyFileImpl`),
  `DiskObjectStorageCache.cpp` (`wrapWithCache`),
  `Storages/MergeTree/DataPartStorageOnDiskFull.cpp` (`prepareRead`/`getRemotePaths`/`copyFileFrom`),
  `Storages/MergeTree/DataPartStorageOnDiskBase.cpp` (`backup`/`clonePart`/`freezeRemote`),
  `Storages/MergeTree/Backup.cpp`, `Disks/IDisk.cpp` (`copyThroughBuffers`/`copyFile`),
  `Backups/BackupEntryWithChecksumCalculation.cpp` (`calculateChecksumFromRemotePath`),
  `Disks/DiskType.cpp` (`DataSourceDescription::operator==`).
- Explicitly out of scope: GC condemn/graduate protocol correctness, ref-ledger recovery and
  wedge resolution, mount-lease internals, write/upload protocol, IDisk contract of
  `getStorageObjects` beyond the MOVE/TTL/BACKUP consumers named here.

Read path as implemented at HEAD:

1. `parsePartFilePath` / `route()` → `{namespace, ref, file}`.
2. `CachedPartFolderAccess::resolve` → `Pool::resolveRef` → `CasRefLedger::resolveRef`.
   `allow_stale` is unused (mounted writer is the sole writer of that namespace).
   `Resolved::manifest_size` is still hard-coded to `0`.
3. `getView`: resolve first; `CachedForLoad` serves the LRU view only if `manifestId` matches;
   `ForceFresh` may skip body re-proof per `part_folder_validate`. Misses are single-flighted
   per `ns+ref` for `CachedForLoad` only.
4. `readManifestShared`: mandatory `HEAD` → decode-cache lookup keyed by `(manifest_id, token)`
   → `GET` → `decodePartManifest` → `refMatchesBody` / `manifestNamespaceMatches`.
5. Blob locate: `{key = layout.blobKey(ref), offset = poolMeta.blob_header_len, length = entry.blob_size}`.
   The object's own envelope is not parsed on the read path.
6. `prepareRead` on a CAS disk uses `prepareInManifestRead` (inline) or `getBlobViewPlan`
   (payload window + `needFileView`). Payload GET is `object_storage->readObject`, not `Cas::Backend`.
7. `getStorageObjects` returns payload *length* and the raw blob key, with no range/offset.
   `getBlobViewPlan` is the only byte-reading plan that applies the envelope offset and `physicalKey`.

## Findings
### read-protocol-1 -- part-folder view cache accounts every retained manifest as 256 bytes (Medium)
- Anchor: `Parts/PartFolderAccess.cpp:136-141` (`estimatedBytes() { return 256 + manifest_size; }`);
  `:64-70` (`manifest_size` taken from `Resolved::manifest_size`);
  `Pool/CasRefLedger.cpp:349-353` and `:381-385` (the only two producers of `Resolved`, both set
  `.manifest_size = 0`); consumers `:224-226` (byte budget), `:226` (oversize bypass).
  Setting text: `ContentAddressedSettings.cpp:74-76`.
- Trigger: read files from N distinct parts whose manifests are large (many entries and/or inline
  payloads). Every view is retained at weight 256, so `part_folder_cache_bytes` (default 64 MiB)
  cannot bind: 64 MiB / 256 B = 262144 > `max_entries` = 10000. The effective bound is 10000
  retained decoded manifests. Write-side caps allow 16 MiB inline and 256 MiB encoded per manifest
  (`CasPartWriteTxn.cpp:52-55`). Ten thousand parts with a few MiB of inline payload is tens of
  GiB resident while `CASPartFolderCacheBytes` reports ~2.5 MB. `part_folder_cache_max_entry_bytes`
  (16 MiB) never fires.
- Evidence: `manifest_size` has exactly two writers in the tree, both literal `0`. The decode cache
  one layer down weighs correctly (`CasManifestReader.h:81-90`) and both caches hold the same
  `shared_ptr<const PartManifest>`. The decode cache can evict its accounted entry while the view
  cache keeps the body alive off-budget.
- Notes: same root cause as CAS-045. Not High: this is a memory-budget / operability defect, not
  silent wrong results. `max_entries` still caps count.

### read-protocol-2 -- `getStorageObjects` drops the envelope offset; same-description server-side copy copies envelope bytes (Medium)
- Anchor: `ContentAddressedMetadataStorage.cpp:1936-1940` (`StoredObject(location.key, path, location.length)` —
  no offset, no `physicalKey`); `:1976-1977` (`getStorageObjectsIfExist`, same);
  `ContentAddressedTransaction.cpp:597-598` (in-flight, same). Contrast `getBlobViewPlan` at
  `:2062-2064` (`physicalKey`, `payload_offset = location.offset`). Consumer:
  `DiskObjectStorage.cpp:291-317` (`copyFile` uses `copyFileImpl` when
  `getDataSourceDescription() == to_disk.getDataSourceDescription()`);
  `DiskObjectStorageTransaction.cpp:522-551` (`getStorageObjects` then `copyObjectToAnotherObjectStorage`);
  `IDisk.cpp:154-160` (`copyThroughBuffers`/`asyncCopy` calls `from_disk.copyFile`);
  `DataPartStorageOnDiskFull.cpp:375-390` (`copyFileFrom`);
  `DataPartStorageOnDiskBase.cpp:820` (MOVE/TTL `clonePart` → `copyDirectoryContent`).
  `DataSourceDescription::operator==` ignores `metadata_type` (`Disks/DiskType.cpp:35-38`).
- Trigger: copy a blob-backed part file from a CAS S3 disk to another object-storage disk whose
  `DataSourceDescription` matches (same type/endpoint/bucket; metadata type is not compared) —
  `MOVE PARTITION`/`TTL` via `clonePart` → `copyDirectoryContent` → `copyFile`, or a mutation
  `copyFileFrom`, or `BACKUP` with `copy_instead_of_hardlinks` to an S3 disk on the same host.
  `copyObject` copies the whole key. The destination file is `[envelope][payload]`.
- Evidence: `locate` returns `offset = meta.blob_header_len` (`CasManifestReader.cpp:156-160`).
  `getStorageObjects` documents that it carries no range (`:1937-1939`) and relies on
  `getBlobViewPlan` for byte reads. `prepareRead` honours that split (`DiskObjectStorage.cpp:824-831,
  918-921`), so MergeTree queries are correct. The copy path does not. Inline files return
  `StoredObject("", path, size)` (`:1903-1904`, `:1974-1975`) and fail loudly — a whole-part MOVE/BACKUP
  that hits `columns.txt`/`checksums.txt` aborts. A single-file blob copy (mutation `copyFileFrom`
  of a `.bin`) has no inline file to fail closed and writes envelope bytes to the destination.
- Notes: same root cause as CAS-020. Cross-description copies use `IDisk::copyFile` → `readFile` →
  `prepareRead` and are correct. Same-disk CAS `copyFile` hits `generateObjectKeyForPath` and throws
  `NOT_IMPLEMENTED`. Temporary-hardlink BACKUP on CAS is already refused (`DataPartStorageOnDiskBase.cpp:424-429`).
  Pointer-holding BACKUP content goes through `readFile`; `calculateChecksumFromRemotePath` hashes
  the remote_path string, not object bytes.

### read-protocol-3 -- one logical read resolves the ref several times, with no read snapshot (Low)
- Anchor: `ContentAddressedMetadataStorage.cpp:1438-1471` (`existsFile`), `:1686-1711` (`getFileSize`),
  `:2033-2067` (`getBlobViewPlan`), `:1980-2011` (`tryGetInManifestBytes`) — each independently
  `route()` → `resolve()` → `getView(CachedForLoad)`. Callers chain them
  (`DataPartStorageOnDiskFull.cpp` size then `prepareRead`).
- Trigger: a repoint of the committed ref (standalone write/remove on that part) landing between
  `getFileSize` and `readFile`. Size comes from manifest A, bytes from manifest B.
- Evidence: no token, generation, or manifest id is threaded from the size query into the read plan.
  The view LRU narrows but does not close the window: it is validated against a freshly resolved
  `manifest_id` on every call (`PartFolderAccess.cpp:173-187`). Blobs are immutable, so the failure
  is a wrong length (short read / checksum), not mixed foreign bytes.
- Notes: loud; requires a concurrent repoint of the exact ref being read.

### read-protocol-4 -- `CachedForLoad` single-flight is keyed only by `ns+ref`; a follower can take a one-repoint-lag view (Low)
- Anchor: `Parts/PartFolderAccess.cpp:264-287` (`buildView`); inflight map keyed by `key.cacheKey()`
  (`PartFolderAccess.h` `ns + '\0' + ref`). Followers return `future.get()` and ignore their own
  `resolved`.
- Trigger: two concurrent `CachedForLoad` `getView` calls on the same ref. Call A resolves manifest
  M1 and becomes the flight leader. A repoint lands. Call B resolves M2, joins the inflight, and
  is handed A's M1 view.
- Evidence: fresh modes do not coalesce (`:267-270`). Only `CachedForLoad` shares the flight.
  Every issued view is internally consistent (one manifest). The effect is a one-repoint lag, not
  two manifests mixed in one view.
- Notes: same shape as CAS-019. `ForceFresh`/`StrictValidate` are unaffected.

## By-design / info / non-actionable
- **Payload offset is taken from pool meta; the object's envelope is not parsed on read.**
  `locate` uses `meta.blob_header_len` (`CasManifestReader.cpp:156-160`). `decodeEnvelopeHeader`
  is not on the query path. `blob_header_len` is pool-global and persisted. Envelope-length
  divergence is not a structurally reachable production case (CAS-089 by-design). Truncation/bit
  rot degrade to a loud checksum failure because `ReadBufferFromFileView` reports the declared
  logical size. Not re-raised as a defect.
- **Nothing pins a blob across the GET; payload reads escape `CasRequestController`.**
  `readBlobPayload` / `prepareRead` use `object_storage->readObject` directly
  (`ContentAddressedMetadataStorage.cpp:2076-2079`). CAS inherits MergeTree's part-lifetime
  guarantee. A GC/read race surfaces as a raw object-storage `NoSuchKey`/`S3_ERROR` without
  `CasEventType::ReadMissing` (the manifest path has that event). Documented design (CAS-016);
  residual is diagnosability only and is not raised separately.
- **`allow_stale` does not select a source.** `CasRefLedger::resolveRef` always reads the recovered
  in-memory committed table (`CasRefLedger.cpp:286-290`). Namespaces are owned by one server root.
- **Manifest decode cache cannot serve stale content.** Key includes the HEAD token
  (`CasManifestReader.h:64-68`, `.cpp:83-85`). Manifest keys are write-once per `ManifestRef`.
- **Fail-closed admission.** `ContentRead` never answers silent-absent on a Vanished/uncertain disk
  (`checkOpAdmitted`).
- **Cache-wrapped CAS disk.** `wrapWithCache` reuses the same metadata storage
  (`DiskObjectStorageCache.cpp:21-31`). The CAS plan and file view survive under the cache layer.
- **In-transaction reads** go through `tryReadFileInFlight` and window S3 staging at
  `blob_header_len` (`ContentAddressedTransaction.cpp:632-646`).
- **Zero-length blob-placed files** yield `left_bound == right_bound`; gather does not issue a
  request at EOF.

## Closed-since-2026-08-12
- The previous read-protocol-2 (read-side envelope not parsed ⇒ silent wrong window) is not
  re-raised: Filimonov CAS-089 and the pool-global persisted `blob_header_len` make the integrity
  consequence unreachable. The code shape is unchanged and is recorded under by-design.
- No other finding in this angle was closed by a product commit. `Resolved::manifest_size = 0`
  and the `getStorageObjects` offset drop are still present.

## Coverage
- Reviewed: `resolveRef`, part-folder view / single-flight / freshness, manifest decode + cache,
  blob locate (envelope offset), payload path vs CAS backend, file/page cache composition,
  stale vs fresh, `getStorageObjects` consumers (MOVE/TTL/`copyFileFrom`/BACKUP).
- N-A: write/upload protocol (write-protocol audit); GC condemn correctness.
- Deferred: `ReadPipeline`/`ReadBufferFromFileView` internals beyond the CAS plan hand-off;
  distributed-cache interaction (same file-view wrap).

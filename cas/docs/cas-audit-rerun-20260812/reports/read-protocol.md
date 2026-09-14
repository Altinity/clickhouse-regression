# read-protocol -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, working tree as-is
(base `842f2b37b8f`). Read-only, code-only: no `docs/**`, no comment text used as evidence of intent. Shipped
strings used as evidence: exception messages, `DECLARE()` descriptions in
`ContentAddressedSettings.cpp`, `describeUnresolvedReason` in `Backend/CasRequestControl.h:47-69`.

Audited: the path from a MergeTree read of a part file to bytes returned — path parsing, ref resolution,
manifest read/decode/caching, blob locate and offset math, inline vs blob payload, envelope header handling,
the read plan handed to `DiskObjectStorage` (`prepareInManifestRead` / `getBlobViewPlan`), buffer construction
in `ReadPipeline`, file-cache/page-cache interaction, and `getFileSize` / `exists*` / `listDirectory` as used
by readers.

Not re-derived (per calibration): CAS tests are deleted in the working tree; transactions are eager
(`transactionIsStagingOverlay() == true`, `ContentAddressedMetadataStorage.h:117`);
`Mode::EmulatedSingleProcess` is auto-selected for local object storage; `getStorageObjects` dropping
`BlobLocation.offset` and reads escaping only because `DiskObjectStorage::prepareRead` special-cases CAS
(`DiskObjectStorage.cpp:808-822`, `903-904`) is **already reported by the idisk-contract audit** and is cited
here only as context.

## Read path as implemented

1. **Path parsing.** `Cas::parsePartFilePath` / `isPartFilePath` split the disk-relative path and anchor a part
   directory: `store/<3>/<uuid>` prefix match (`Parts/PartPathParser.cpp:88-99`), else a `detached`/`moving`
   component, else the **last** component that "looks like" a part dir (`PartPathParser.cpp:101-163`).
   Everything after the anchor is the in-part file path (`PartPathParser.cpp:194-209`). Splits are memoized in
   a `thread_local` 8-slot cache keyed by the full path (`PartPathParser.cpp:35-64`).
2. **Route + ref.** `route()` maps the parsed path to `{namespace, ref, file}`; the ref key is
   `ns + '\0' + ref` (`Parts/PartFolderAccess.h:21-29`).
3. **Ref resolution.** `CachedPartFolderAccess::resolve` → `Pool::resolveRef` (`Pool/CasPool.cpp:1135-1137`) →
   `CasRefLedger::resolveRef` (`Pool/CasRefLedger.cpp:214-259`). The `allow_stale` argument is **unused**
   (parameter is unnamed at `CasRefLedger.cpp:214`); the answer always comes from the in-memory committed ref
   table of a runtime acquired/recovered once (`CasRefLedger.cpp:388-432`, `956-...`). `Resolved.manifest_size`
   is hard-coded to `0` (`CasRefLedger.cpp:256`, and `275` for `listRefs`).
4. **Part-folder view.** `CachedPartFolderAccess::getView` (`PartFolderAccess.cpp:149-215`) resolves first,
   then serves the LRU view only if `cached->manifestId() == resolved->manifest_id`
   (`PartFolderAccess.cpp:158-170`); `ForceFresh` may skip body re-proof per `part_folder_validate`
   (`PartFolderAccess.cpp:172-188`). Misses are single-flighted per ref
   (`PartFolderAccess.cpp:231-269`).
5. **Manifest read + decode cache.** `CasManifestReader::readManifestShared`
   (`Pool/CasManifestReader.cpp:54-126`): `backend.head(manifestKey)` → decode-cache lookup keyed by
   `(manifest_id, head.token)` (`CasManifestReader.cpp:76-78`, key/hash at `CasManifestReader.h:37-52`) →
   `backend.get` → `decodePartManifest` → `refMatchesBody` and `manifestNamespaceMatches` checks
   (`CasManifestReader.cpp:88-120`). Decode itself is self-verifying: canonical ordering, trailer count,
   payload-zone banners, and a CityHash128 `payload_digest` over the re-encoded body
   (`Formats/CasPartManifestFormat.cpp:236-269`).
6. **Entry lookup.** `PartFolderView::findFile` → binary search over sorted entries
   (`PartFolderAccess.cpp:80-83`, `CasPartManifestFormat.cpp:291-298`).
7. **Blob locate / offset math.** `CasManifestReader::locate` (`CasManifestReader.cpp:133-151`) returns
   `{key = layout.blobKey(entry.ref), offset = meta.blob_header_len, length = entry.blob_size}`. `Inline`
   throws `BAD_ARGUMENTS`.
8. **Inline payload.** `prepareInManifestRead` (`ContentAddressedMetadataStorage.cpp:1402-1417`) →
   `tryGetInManifestBytes` (`1374-1400`) → `ReadBufferFromOwnMemoryFile` over the manifest's inline bytes; the
   pipeline is a `CustomSource` with `StoredObject("", path, size)` and `prepareRead` returns before any
   gather/cache stage (`DiskObjectStorage.cpp:814-815`).
9. **Blob read plan.** `getBlobViewPlan` (`ContentAddressedMetadataStorage.cpp:1419-1445`) →
   `StoredObject(physicalKey(location.key), path, location.offset + location.length)`,
   `payload_offset = offset`, `payload_end = offset + length`. `prepareRead` uses that single object
   (`DiskObjectStorage.cpp:820-822`), adds gather, the object storage's own cache stage, page cache and async
   prefetch, and finally wraps the whole chain in a file view (`DiskObjectStorage.cpp:861-904`).
10. **Buffer construction.** `ReadPipeline::build` (`IO/ReadPipeline.cpp:172-201`) →
    source (+ filesystem cache, key `FileCacheKey::fromPath(object.remote_path)` at `ReadPipeline.cpp:320`,
    `538`, `575`) → gather → page cache (`ReadPipeline.cpp:618-639`) → `AsynchronousBoundedReadBuffer` →
    `ReadBufferFromFileView(impl, path, payload_offset, payload_end)` (`ReadPipeline.cpp:687-694`). The
    experimental `use_reader_executor` path is skipped whenever a file view is present
    (`ReadPipeline.cpp:209-216`). `ReadBufferFromFileView` translates logical offsets (`IO/ReadBufferFromFileView.cpp:36-51`,
    `94-125`) and reports the logical size (`IO/ReadBufferFromFileView.h:22`).
11. **In-transaction reads.** `DataPartStorageOnDiskFull::readFile` consults
    `tx->tryReadFileInFlight` first (`Storages/MergeTree/DataPartStorageOnDiskFull.cpp:225`, `264`), which
    serves staged inline bytes, an S3 staging object through a file view over
    `poolMeta().blob_header_len` (`ContentAddressedTransaction.cpp:419-431`), a local staging file, or falls
    back to `readBlobPayload` (`ContentAddressedTransaction.cpp:434`,
    `ContentAddressedMetadataStorage.cpp:1447-1455`).
12. **Reader-facing metadata.** `existsFile` (`ContentAddressedMetadataStorage.cpp:955-978`), `getFileSize`
    (`1145-1170`), `existsFileOrDirectory` (`1126-1143`), `listDirectory`/`iterateDirectory`
    (`1196-1291`) each independently resolve the ref and obtain a `CachedForLoad` view. All read-class entry
    points first pass `checkOpAdmitted` (`785-816`).
13. **Cache-wrapped disk.** For a CAS disk, `wrapWithCache` reuses the *same* metadata storage instead of
    wrapping it (`DiskObjectStorageCache.cpp:21-23`), so the CAS plan is preserved under the cache layer.

## Findings

### read-protocol-1 -- part-folder view cache accounts every retained manifest as 256 bytes (High)

- **Anchor.** `Parts/PartFolderAccess.cpp:128-131` (`estimatedBytes() { return 256 + manifest_size; }`);
  `PartFolderAccess.cpp:45-52` and `59-66` (`manifest_size` is taken from `Resolved::manifest_size`);
  `Pool/CasRefLedger.cpp:254-258` and `273-276` (the only two producers of `Resolved`, both set
  `.manifest_size = 0`); consumers: `PartFolderAccess.cpp:180-183` (`ViewWeight`, `PartFolderAccess.h:180-184`),
  `PartFolderAccess.cpp:143-147` (byte budget + `CurrentMetrics::CASPartFolderCacheBytes`),
  `PartFolderAccess.cpp:194-206` (oversize bypass). Wiring: `ContentAddressedMetadataStorage.cpp:588-593`;
  shipped setting text: `ContentAddressedSettings.cpp:52-54`.
- **Trigger.** Read files from N distinct parts whose manifests are large — many entries and/or inline
  entries, which hold whole small files (`ContentAddressedTransaction.cpp:638-654`). Every view is retained
  with a declared weight of exactly 256 bytes, so `part_folder_cache_bytes` (default 64 MiB, described as
  "Part-folder view cache byte budget") can never bind: 64 MiB / 256 B = 262 144 > `max_entries` = 10 000.
  The effective bound is 10 000 retained decoded manifests of *unbounded declared size*; the per-manifest
  write-side caps are 16 MiB of inline payload, 256 MiB encoded and 1 048 576 entries
  (`Pool/CasPartWriteTxn.cpp:52-55`, enforced at `511-544`). Ten thousand parts each carrying a few MiB of
  inline payload is tens of GiB of resident memory while `CASPartFolderCacheBytes` reports 2.5 MB.
- **Evidence.** `manifest_size` has exactly two writers in the tree, both literal `0`
  (`rg manifest_size` over the CAS root returns only the declaration sites plus
  `CasRefLedger.cpp:256`/`275`), so `estimatedBytes()` is a compile-time-equivalent constant 256.
  Consequences visible in shipped behaviour: (a) the byte budget is inoperative;
  (b) `part_folder_cache_max_entry_bytes` (16 MiB, "Oversized part-folder views bypass retention above this
  size") can never fire, making `ProfileEvents::CASPartFolderViewOversizedBypasses`
  (`PartFolderAccess.cpp:204`) dead code; (c) both `CASPartFolderCacheBytes` and any operator sizing based on
  it under-report by orders of magnitude.
- **Notes.** The *decode* cache one layer down does weigh correctly
  (`Pool/CasManifestReader.h:49-58` counts `path`, `inline_bytes` and 96 B/entry against
  `manifest_decode_cache_bytes`, default 128 MiB), and both caches hold the same
  `shared_ptr<const PartManifest>`. That makes the leak worse rather than better: the decode cache can evict
  its properly-accounted entry while the view cache keeps the body alive off-budget. Minimal fix is to carry
  a real size into `PartFolderView` (either populate `Resolved::manifest_size` at resolve time or weigh the
  decoded body the way `PartManifestWeight` already does).

### read-protocol-2 -- payload offset is taken from pool meta; the object's own envelope is never parsed or verified on read (Medium)

- **Anchor.** `Pool/CasManifestReader.cpp:137-144` (`offset = meta.blob_header_len`);
  `ContentAddressedMetadataStorage.cpp:1437-1442` and `1447-1455`; `DiskObjectStorage.cpp:903-904`;
  `ContentAddressedTransaction.cpp:425-430` (same constant on the in-flight staging read).
  `decodeEnvelopeHeader` exists and can recover the true `header_len` by scanning the pad zone
  (`Formats/CasBlobEnvelopeFormat.cpp:214-229`), but its only caller in the tree is the inspect tool
  (`Tools/CasInspect.cpp:571`), and it ignores its `object_size` parameter entirely (unnamed parameter,
  `CasBlobEnvelopeFormat.cpp:146`).
- **Trigger.** Any object living at a blob key whose envelope is not exactly `poolMeta().blob_header_len`
  bytes is read at the wrong offset and the mismatch is never detected. `blob_header_len` is pool-global and
  persisted, and `PoolMeta::createOrValidate` returns the *persisted* value without comparing it to the
  configured one (`Pool/CasPoolMeta.cpp:100-104`; `admitOrValidate` only reconciles the hash algo,
  `CasPoolMeta.cpp:60-84`), so the normal single-pool case is self-consistent. It stops being self-consistent
  when `_pool_meta` is lost and re-minted while the configured `blob_header_len` differs
  (`CasPoolMeta.cpp:106-119`; blob keys are pure content-hash paths, `Formats/CasLayout.cpp:28-31`, so
  pre-existing blobs are still addressable and are re-adopted by key existence alone at
  `Pool/CasPartWriteTxn.cpp:153-174`), or when an object is placed at a blob key by any other route
  (hand copy, restore into the prefix, an interrupted resurrect). The read then returns a window shifted by
  the header delta with no exception.
- **Evidence.** There is no content-hash verification anywhere on the read path: no digest call exists in
  `CasManifestReader.cpp` or in the read entry points of `ContentAddressedMetadataStorage.cpp`; payload
  verification lives only in `Tools/CasFsck.cpp`. The only structural check on a blob object is on the
  *write* side, `Pool/CasPartWriteTxn.cpp:253-257` ("size ... is below the pool blob header length"), and it
  neither compares the derived logical size to the declared payload size nor reads the envelope. The
  envelope carries exactly the fields that would allow a read-side cross-check — `tag`, `bld`, `ref`
  (`CasBlobEnvelopeFormat.cpp:101-130`) — and none is consulted.
- **Notes.** Truncation/bit rot degrade to a loud failure rather than silence: `tryGetFileSize` reports the
  *declared* logical size (`IO/ReadBufferFromFileView.h:22`), so a short object ends the read early and
  MergeTree's own checksums fire. A header-length mismatch is the silent case, because every byte offset is
  still in range. Manifests are safe by contrast — they are self-verifying (finding list, item 5 above).

### read-protocol-3 -- nothing pins a blob across the GET, and the payload read escapes CAS request control and classification (Medium)

- **Anchor.** `ContentAddressedMetadataStorage.cpp:1447-1455` and `DiskObjectStorage.cpp:820-822`, `903-904`:
  the payload is read with `object_storage->readObject(...)` directly — the `Cas::Backend` wrapper is not on
  this path, so no `CasRequestBudget` attempt timeout / operation deadline / attempt cap applies
  (`Backend/CasRequestControl.h:82-94`) and no CAS classification or event is produced.
  `Parts/PartFolderAccess.cpp:190-215` hands out a plain `shared_ptr<const PartFolderView>` snapshot with no
  lease. GC deletes blob bodies token-conditionally, a generation after condemnation
  (`Gc/CasGc.cpp:605-613`).
- **Trigger.** A reader that has already obtained a view (or an open read buffer) for a ref that is
  subsequently dropped, while GC advances far enough to graduate and redelete the blob
  (`gc_interval_sec` default 60, `ContentAddressedSettings.cpp:32`). The GET then fails with a raw
  object-storage `NoSuchKey`/`S3_ERROR` surfaced to the query, with no CAS context — none of the
  `describeUnresolvedReason` vocabulary (`CasRequestControl.h:47-69`) or `CasEventType::ReadMissing`
  treatment that the *manifest* path gets (`Pool/CasManifestReader.cpp:59-74`).
- **Evidence.** The only invalidation coupling is local: `dropRef*`/`promoteBuild` call `eraseView`
  (`PartFolderAccess.cpp:271-278`, `309`, `475-516`), which removes the LRU entry but cannot revoke views
  already handed out, and there is no reader registry, lease, or refcount consulted by GC. `PreconditionFailed`
  / `InvalidObjectState` are classified only for conditional *writes*
  (`Backend/CasObjectStorageBackend.cpp:117-120`, `276-277`), never for a data read.
- **Notes.** Whether this is reachable in practice depends entirely on the caller: MergeTree normally keeps
  the ref alive for the lifetime of a part reference, so the honest statement is that CAS provides no
  read-side protection of its own and inherits the caller's guarantee. The actionable half is the diagnostics
  gap — a GC/read race is indistinguishable from a genuinely corrupt pool in the error the operator sees.

### read-protocol-4 -- one logical read resolves the ref several times, with no read snapshot (Low)

- **Anchor.** `ContentAddressedMetadataStorage.cpp:955-978` (`existsFile`), `1145-1170` (`getFileSize`),
  `1419-1445` (`getBlobViewPlan`), `1374-1400` (`tryGetInManifestBytes`) — each independently calls
  `route()` → `resolve()` → `getView(CachedForLoad)`. Callers chain them:
  `Storages/MergeTree/DataPartStorageOnDiskFull.cpp:155-167` then `225`.
- **Trigger.** A repoint of a committed ref (`PartFolderAccess.cpp:442-473`, reached by a standalone
  write/remove on a committed part) landing between a reader's `getFileSize` and its `readFile`: the size
  comes from manifest A and the bytes from manifest B. Because blobs are immutable and content-addressed the
  bytes themselves are consistent, so the outcome is a wrong length — a short read ending in "Cannot read all
  data" or a checksum failure — rather than a clean retryable error.
- **Evidence.** No token, generation, or manifest id is threaded from the size query into the read plan;
  `getBlobViewPlan` takes only a path. The view LRU narrows but does not close the window, since it is
  validated against a freshly resolved `manifest_id` on every call (`PartFolderAccess.cpp:158-170`).
- **Notes.** Low because the failure is loud and the trigger requires a concurrent repoint of the exact ref
  being read. Worth recording because the `IMetadataStorage` surface offers no way to pass a resolved
  manifest identity from one call to the next.

## By-design / info / non-actionable

- **Manifest decode cache cannot serve stale content.** The key includes the HEAD token
  (`CasManifestReader.h:37-42`, `CasManifestReader.cpp:76-78`, `123-124`) and a HEAD precedes every lookup,
  so a replaced object misses the cache. The GET body is not re-checked against the HEAD token, which is
  harmless: manifest keys are write-once per `ManifestRef` (`Pool/CasPartWriteTxn.cpp:533-551`) and the body
  self-verifies against ref, namespace and payload digest.
- **Read amplification on a view-cache miss.** `readManifestShared` issues `head()` and then `get()`, and in
  `Mode::Native` `get()` performs its own `nativeHead` first
  (`Backend/CasObjectStorageBackend.cpp:468-489`) — two HEADs plus one GET per miss. Sound, just costly.
- **Fail-closed admission.** `checkOpAdmitted` (`ContentAddressedMetadataStorage.cpp:785-816`) throws
  transient-unavailable for `TransientNotLive` and returns `TruthAbsent` only for
  `VanishedReplaced`/`VanishedForgotten` and only for `Probe`/`Remove`; `ContentRead` never fails open. The
  empty-enumeration answer is additionally gated on a pool-identity sentinel probe (`818-844`).
- **Offset/size arithmetic.** `offset + length` is `uint64` and the plan is consistent
  (`ContentAddressedMetadataStorage.cpp:1439-1441`); a wrapped sum cannot produce a silently wrong window
  because `needFileView` rejects `right < left` (`IO/ReadPipeline.cpp:161-170`), and `blob_size` is a decoded
  canonical `u64` (`CasPartManifestFormat.cpp:205`, `226`). `ReadBufferFromFileView` bounds
  `setReadUntilPosition` (`ReadBufferFromFileView.cpp:36-41`) and seeks
  (`ReadBufferFromFileView.cpp:117-119`) against the view, and reports logical size and offsets
  (`ReadBufferFromFileView.h:21-22`).
- **Zero-length blob-placed files.** `.bin`/`.mrk*`/`primary.idx` always go to a blob
  (`ContentAddressedTransaction.cpp:65-73`, `598`), so a zero-byte one yields `left_bound == right_bound`.
  Checked and sound: the gather never creates an implementation buffer at `offset == total size`
  (`Disks/IO/ReadBufferFromRemoteFSGather.cpp:78-108`), so the read ends at EOF without issuing a request.
- **File-cache keying.** The key is `FileCacheKey::fromPath(object.remote_path)` where `remote_path` is
  `physicalKey(blobKey)` (`ReadPipeline.cpp:320`, `538`, `575`). Blob keys are content-hash paths, so equal
  keys imply equal payloads; a cross-pool collision needs an identical physical prefix, i.e. the same pool.
  Note that in `EmulatedSingleProcess` the pool prefix can be trimmed to empty
  (`ContentAddressedMetadataStorage.cpp:522-535`), so two local CAS disks sharing one filesystem cache and
  one common prefix can share cache keys — benign while `blob_header_len` matches, and folded into
  read-protocol-2 when it does not. The page-cache path is pool-safe: its prefix includes disk name, storage
  type and object namespace (`DiskObjectStorage.cpp:879-886`).
- **Cache-wrapped CAS disk.** `wrapWithCache` deliberately reuses the CAS metadata storage rather than
  wrapping it in `MetadataStorageFromCacheObjectStorage` (`DiskObjectStorageCache.cpp:21-23`); the CAS plan
  and file view therefore survive under the cache layer. In-flight staging reads use the metadata storage's
  own uncached `object_storage` (`ContentAddressedTransaction.cpp:427`) and so bypass the file cache — cold
  but correct.
- **Inline reads.** `prepareInManifestRead` copies the payload into the buffer creator and returns before the
  gather/cache stages (`ContentAddressedMetadataStorage.cpp:1409-1416`, `DiskObjectStorage.cpp:814-815`), so
  an inline read is a whole-value memory read regardless of how few bytes the caller wants. Bounded by
  `INLINE_CAP` and the 16 MiB per-manifest inline total (`CasPartWriteTxn.cpp:54`).
- **Path parsing heuristic.** With no `store/<3>/<uuid>` anchor and no `detached`/`moving` component, the
  parser anchors on the *last* component that looks like a part directory
  (`PartPathParser.cpp:159-161`). No production part-internal file name matches the predicate (≥4
  underscore-separated groups with the last three numeric, `PartPathParser.cpp:101-132`), so this is
  informational, not a finding.
- **Cross-node read-after-write.** `resolveRef` ignores `allow_stale` and answers from an in-memory ref table
  recovered once per runtime (`CasRefLedger.cpp:214-221`, `388-432`), so a namespace mutated by another
  server root would not be observed. Consistent with namespaces being owned by one server root
  (`ContentAddressedMetadataStorage.cpp:1458-1463`); no cross-node reader flow in this tree contradicts it.
- **Same-transaction read-after-write** is served by the staging overlay
  (`ContentAddressedTransaction.cpp:406-438`) and is wired into MergeTree
  (`DataPartStorageOnDiskFull.cpp:71`, `159`, `225`, `264`).
- **`getStorageObjects` / `getStorageObjectsIfExist` dropping the payload offset**
  (`ContentAddressedMetadataStorage.cpp:1336-1341`, `1365-1371`, and the in-transaction variant at
  `ContentAddressedTransaction.cpp:394-401`) — already reported by the idisk-contract audit; cited here only
  because it is why the CAS special case in `prepareRead` is load-bearing. One additional detail visible from
  this path: those two sites return the raw `location.key`, while the read plan returns
  `physicalKey(location.key)` (`1439`), so with a non-empty `physical_key_prefix` the returned key is not
  resolvable either.
- **`read_hint`** reaches the object storages only as a buffer-sizing estimate
  (`Disks/IO/createReadBufferFromFileBase.cpp:48-49`, `221-224`); object length always comes from
  `StoredObject::bytes_size`, which CAS sets to `offset + length`. No header-length truncation risk here.

## Coverage

Checked and found sound: manifest decode self-verification (order, trailer, banners, payload digest, ref and
namespace binding); manifest decode cache keying and staleness; part-folder view validation against a freshly
resolved manifest id; single-flight of view misses; inline vs blob dispatch; the file-view offset translation,
seek/`setReadUntilPosition` bounding and logical size reporting; zero-length blob reads; gather/cache/page-cache
/async-prefetch stage ordering and the reader-executor fallback; `use_reader_executor` interaction with the
file view; file-cache and page-cache key derivation; `read_hint` semantics; overflow behaviour of the
offset/size arithmetic; admission (fail-closed) behaviour of read-class entry points; path-parsing anchors;
in-transaction read-after-write; the cache-wrapped CAS disk composition.

Checked and reported: view-cache weight accounting (read-protocol-1); read-side envelope/offset trust and the
absence of any payload integrity check (read-protocol-2); absence of a read-side pin plus the payload GET
escaping CAS request control and error classification (read-protocol-3); repeated independent ref resolution
within one logical read (read-protocol-4).

Not covered here (other audits): GC condemn/graduate/redelete protocol correctness, ref-ledger recovery and
wedge resolution, mount leases and fencing, write/upload protocol, `IDisk` contract conformance of
`getStorageObjects`, backup/restore and interserver relink paths.

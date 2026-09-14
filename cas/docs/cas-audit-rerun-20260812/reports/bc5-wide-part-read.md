# bc5-wide-part-read -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base
`842f2b37b8f`, working tree as-is, read-only. CAS root
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`. Paths below are relative to that
root unless prefixed with `src/`.

Question: how does a Wide-format part with hundreds/thousands of files, and how does a very large
part, behave on the read and metadata path? Specifically: file-to-entry/blob mapping and the inline
threshold, manifest growth against the hard caps, per-file resolution cost, directory iteration,
decoded-manifest memory and cache weighting, object-store round trips to open a part, projections and
secondary indexes, and rewrite amplification on mutation/merge.

Code-only rule observed: `docs/**` and comments are not treated as evidence of intent; only shipped
strings, constants and control flow. All CAS tests are deleted in this working tree, so no test is
cited as evidence of a contract.

Cited from sibling audits, not re-derived here: `PartFolderView::estimatedBytes()` is a constant 256
because `Resolved::manifest_size` is hardwired to 0, so the view cache's byte budget is inoperative
and only the 10,000-entry cap evicts; there is no pin held across the blob GET; and `locate()` takes
the payload offset from pool meta rather than from the object's own envelope.

## Wide-part representation and read cost

Mapping. One `ManifestEntry` per part file, no packing and no grouping
(`Formats/CasPartManifestFormat.h:20-39`). Placement is decided purely by file name:
`partFileMustStayBlob()` returns true only for the exact name `primary.idx` and for the suffixes
`.bin .mrk .mrk2 .mrk3 .cmrk .cmrk2 .cmrk3` (`ContentAddressedTransaction.cpp:65-73`). Everything
else goes down the inline path and is embedded in the manifest body if it is `<= INLINE_CAP`
(1 MiB, `ContentAddressedTransaction.cpp:92`, decision at `:643`); above that it spills to a local
scratch file and becomes a blob (`:655-668`). So for a Wide part with N columns the shape is roughly
N `.bin` + N `.cmrk3` blobs, plus `columns.txt`, `checksums.txt`, `count.txt`, `serialization.json`,
`partition.dat`, `metadata_version.txt`, `primary.cidx` and every `skp_idx_*.idx/.idx2` inline.

Blob layout. Each blob object is `blob_header_len` (default 256, space-padded to exactly that width)
followed by the payload (`Pool/CasPool.h:46`, `Formats/CasBlobEnvelopeFormat.cpp:133-142`), and each
fresh blob also gets its own separate freshness-meta object
(`Pool/CasPartWriteTxn.cpp:381-385`, backfill at `:287-292`).

Encode/decode. `encodePartManifest` sorts a pointer vector, checks for duplicate paths, writes one
JSON line per entry, a trailer with the count, then a payload zone with one banner + raw bytes per
inline entry (`Formats/CasPartManifestFormat.cpp:71-113`). `decodePartManifest` validates strict
ascending path order (`:236-239`) and then verifies the payload digest by calling
`computePayloadDigest`, which deep-copies the whole manifest and re-encodes it (`:263-267`,
`:272-279`).

Per-operation cost, M = entry count of the part, warm caches unless stated:

| operation | anchor | cost |
| --- | --- | --- |
| resolve ref -> manifest id | `Pool/CasRefLedger.cpp:214-258` | in-memory map lookup, 4 acquisitions of the per-namespace `state_mutex` |
| read manifest, cold | `Pool/CasManifestReader.cpp:54-126` | 1 HEAD + 1 GET + decode + full re-encode for the digest |
| read manifest, decode-cache hit | `Pool/CasManifestReader.cpp:58,76-79` | 1 HEAD unconditionally, then a hash lookup |
| `getView`, view-cache hit | `Parts/PartFolderAccess.cpp:152-170` | resolve + hash lookup, no object-store I/O |
| `getView(ForceFresh)` with default `part_folder_validate=always` | `Parts/PartFolderAccess.cpp:172-190` | shortcut disabled, always `buildView` -> `readManifestShared` -> HEAD |
| `findFile` / `fileSize` / `hasFile` | `Formats/CasPartManifestFormat.cpp:291-298` | O(log M) `lower_bound` on the sorted vector |
| `hasDirectory` / projection listing | `Formats/CasPartManifestFormat.cpp:300-311` | O(log M + range) |
| `listChildren("")` (part dir listing) | `Parts/PartFolderAccess.cpp:105-120` | O(M) with an `unordered_set` of names |
| open one column file | `ContentAddressedMetadataStorage.cpp:1419-1445` | warm view + 1 ranged GET starting at offset 256 |
| open the whole part | as above, per file | 1 HEAD + 1 GET for the manifest, then one GET per file, no CAS-level batching, coalescing, prefetch or deadline |
| stage one file into a txn | `ContentAddressedTransaction.cpp:510,652` | O(M_staged) linear scan, so O(M^2) to stage a whole part |
| publish onto an existing ref | `ContentAddressedTransaction.cpp:256-290` | O(M_committed x K_staged) merge, then a full manifest republish |

Hard caps, all in `Pool/CasPartWriteTxn.cpp:52-55` and enforced in `stageManifest` at `:511-544`:
entries `<= 1,048,576`; encoded manifest `<= 256 MiB`; total inline `<= 16 MiB`; largest single
inline entry `<= 1 MiB`. All four are checked before the manifest PUT and raise `LIMIT_EXCEEDED`, so
the cap is fail-closed at write time and cannot produce an unreadable part. `FormatId::PartManifest`
carries `object_cap = 256 MiB` and `line_cap = 64 KiB` (`Formats/CasFormat.cpp:110`), and the read
side checks the *declared decompressed* size against the same 256 MiB
(`Formats/CasTextFormat.cpp:378-392`), so write and read caps agree.

## Findings

### bc5-1 -- Secondary-index and compressed-primary-index files are inlined, so a legitimately wide part hits the 16 MiB total-inline cap and its INSERT fails permanently (High)

- Anchor: `ContentAddressedTransaction.cpp:65-73` (`partFileMustStayBlob` matches only the exact name
  `primary.idx` plus the `.bin`/`.mrk*`/`.cmrk*` suffixes); `ContentAddressedTransaction.cpp:643`
  (`bytes.size() <= INLINE_CAP` -> inline); `Pool/CasPartWriteTxn.cpp:54`
  (`kMaxManifestInlineBytesTotal = 16 MiB`) enforced at `Pool/CasPartWriteTxn.cpp:514-528`.
  Neither `skp_idx_*.idx`, `skp_idx_*.idx2` nor `primary.cidx` matches the blob predicate;
  `primary.cidx` is the default primary-index name because `compress_primary_key` defaults to true
  (`src/Storages/MergeTree/IMergeTreeDataPart.h:863`,
  `src/Storages/MergeTree/MergeTreeSettings.cpp:2121`).
- Trigger (part shape): a Wide part with 400 columns and ~100 skip indexes over ~12,000 granules.
  Each minmax `skp_idx_*.idx2` is roughly `2 values x 8 bytes x 12,000` ~ 190 KiB, all below the
  1 MiB per-entry cap so all are inlined; 100 x 190 KiB ~ 19 MiB of inline payload, over the 16 MiB
  aggregate cap. Adding `primary.cidx` and `serialization.json` only makes it worse.
- Consequence: `publishStaging` -> `stageManifest` throws
  `LIMIT_EXCEEDED: "stageManifest: total inline {} bytes exceeds cap {}"` at commit, *after* the
  ~800 column blobs were already uploaded and their meta objects written
  (`ContentAddressedTransaction.cpp:264,299` upload before the merge/publish completes). The staged
  blobs and the scratch manifest become GC debris. Because the cap is a function of the part shape,
  not of transient state, every retry and every merge producing the same shape fails identically, so
  the table is unwritable at that shape with an internal-limit error that names no user-facing knob
  (the cap is a compile-time constant, not a setting in
  `ContentAddressedSettings.cpp:29-58`).
- Evidence: constant at `Pool/CasPartWriteTxn.cpp:54`; check and message at
  `Pool/CasPartWriteTxn.cpp:526-528`; placement decision at `ContentAddressedTransaction.cpp:598,643`;
  the blob predicate's literal suffix list at `ContentAddressedTransaction.cpp:69`.

### bc5-2 -- A single-file write or unlink on a committed wide part republishes the whole manifest twice and emits one adopt event per blob entry inside the ref-log CAS lambda (High)

- Anchor: `ContentAddressedTransaction.cpp:256-290`. When the ref already resolves, the code stages a
  *scratch* manifest of just the staged entries and PUTs it (`:262`), precommits it (`:263`), uploads
  blobs (`:264`), then builds `merged` from the committed entries plus the staged ones (`:267-274`)
  and calls `repointRef` (`:280`), then `abandon()`s the scratch build (`:285`).
  `Parts/PartFolderAccess.cpp:444-457` (`repointRef`) re-reads the committed manifest with
  `ForceFresh`, then does `computePayloadDigest` + `encodePartManifest` + `decodePartManifest`
  (which itself re-runs `computePayloadDigest`) just to compare, then `publishEntries` ->
  `prepareEntries` (`:392-410`) which calls `adoptEvidence` for **every** entry and
  `stageManifest(entries)` for the full merged set -- a second full manifest PUT.
  `Pool/CasPartWriteTxn.cpp:643-647` then GETs and decodes that manifest again inside `promote`, and
  the ref-mutation lambda captures the decoded `body` **by value** (`:658`) and loops over all
  `body.entries` (`:675-695`) emitting a `BlobReuseAdopt` event for every adopted blob (`:686-694`).
  The lambda is `build_ops`, invoked at `Pool/CasRefLedger.cpp:2094` from `flushRefBatch`, which
  `runRefQueueLeader` calls in a `while (true)` loop until the item lands
  (`Pool/CasRefLedger.cpp:1508-1516`), so it re-runs from scratch on every batch retry. Event emission
  is synchronous under one per-pool mutex (`Pool/CasEventDispatcher.cpp:17-44`).
- Trigger (part shape): a committed Wide part with 1,000 columns, so M ~ 2,100 entries and a manifest
  of ~350 KB; then any standalone one-file change on it -- a mutation writing
  `metadata_version.txt`, or `unlinkFile` of a single file (`ContentAddressedTransaction.cpp:1069-1098`),
  both of which reach `publishStaging` with a non-empty `st.entries`/`content_removed` and an
  existing ref.
- Consequence: for a one-byte logical change the writer performs 2 manifest PUTs (one immediately
  orphaned), ~5 full encodes plus 2 full decodes plus 2 deep copies of the manifest, ~2,100
  `adoptEvidence` map inserts, and ~2,100 synchronous audit events -- all inside the single-threaded
  ref-queue leader for the namespace, and all repeated per retry. Write amplification is O(M) manifest
  bytes per O(1) file changed, and the adopt-event storm serializes every other ref mutation in the
  namespace behind it.
- Evidence: `ContentAddressedTransaction.cpp:262,280,285`; `Parts/PartFolderAccess.cpp:447-457,399-401`;
  `Pool/CasPartWriteTxn.cpp:643-647,658,675-695`; `Pool/CasRefLedger.cpp:2094`, `:1508-1516`;
  `Pool/CasEventDispatcher.cpp:26-42`.

### bc5-3 -- Decoding a manifest costs 2x the work and ~3x the transient memory of the manifest, because digest verification deep-copies and re-encodes it (Medium)

- Anchor: `Formats/CasPartManifestFormat.cpp:263-267` calls `computePayloadDigest(m)` at the end of
  every decode; `:272-279` implements it as `PartManifest probe = m;` (a full deep copy including all
  inline payloads) followed by `encodePartManifest(probe)` (a full re-serialization, plus another
  sort of the pointer vector at `:77-78`). The same function is also called on the write path at
  `Pool/CasPartWriteTxn.cpp:540` immediately before the real `encodePartManifest` at `:541`, so
  staging encodes twice as well.
- Trigger (part shape): a Wide part at the inline ceiling -- ~20,000 entries with ~15 MiB of inline
  payload, ~20 MiB encoded. One cold open transiently allocates the encoded bytes, the decoded
  manifest, the deep copy, and the re-encoded buffer -- roughly 60 MiB for a 20 MiB manifest, and
  two sorts of 20,000 pointers. At the 256 MiB `kMaxManifestEncodedBytes` ceiling the same pattern
  needs ~0.75 GiB transiently for one decode.
- Consequence: cold-open latency and allocation spikes scale at ~3x manifest size rather than 1x;
  `repointRef` (`Parts/PartFolderAccess.cpp:452-453`) chains three of these in a row, and `promote`
  adds a fourth (`Pool/CasPartWriteTxn.cpp:647`).
- Evidence: `Formats/CasPartManifestFormat.cpp:263-267,272-279,77-78`;
  `Pool/CasPartWriteTxn.cpp:540-541`.

### bc5-4 -- The manifest decode cache under-weights a decoded wide manifest by roughly 2x, so its byte budget over-admits (Medium)

- Anchor: `Pool/CasManifestReader.h:49-58`, `PartManifestWeight` = `256 + sum(path.size() +
  inline_bytes.size() + 96)`. The real per-entry footprint is `sizeof(ManifestEntry)` = 112 bytes
  (`Formats/CasPartManifestFormat.h:20-30`: two 32-byte `std::string`, a 1-byte placement, a
  `BlobRef` whose `BlobDigest` is a **fixed 32-byte array regardless of algorithm**
  (`Primitives/CasBlobDigest.h:39-41,145-152`), and a `uint64_t`), plus one heap block with allocator
  overhead for every path longer than the 15-byte SSO limit. On top of that
  `decodePartManifest` `push_back`s without any `reserve`
  (`Formats/CasPartManifestFormat.cpp:240`), so the vector's capacity after geometric growth is up to
  2x the entry count and stays that way in the cached object.
- Trigger (part shape): a Wide part with 20,000 entries and ~28-character paths. Weight computes
  ~20,000 x (28 + 96) ~ 2.5 MB. Actual residency is ~32,768 slots x 112 B ~ 3.7 MB for the vector
  alone plus ~20,000 x (28 + allocator header) ~ 1 MB of path heap, ~4.7-5.5 MB.
- Consequence: the default `manifest_decode_cache_bytes = 128 MiB`
  (`ContentAddressedSettings.cpp:56`) admits roughly twice the intended bytes of wide-part manifests,
  and the reported `CASManifestDecodeCacheBytes` metric understates real residency by the same
  factor, so the overshoot is invisible to an operator.
- Evidence: `Pool/CasManifestReader.h:52-57`; `Formats/CasPartManifestFormat.h:20-30`;
  `Primitives/CasBlobDigest.h:39-41`; `Formats/CasPartManifestFormat.cpp:240`;
  `ContentAddressedSettings.cpp:56`.

### bc5-5 -- Wide parts make the inoperative view-cache byte budget concretely dangerous: 10,000 retained views pin gigabytes of decoded manifests (Medium)

- Anchor: the constant-256 accounting is a sibling finding
  (`Parts/PartFolderAccess.cpp:128-131` returns `256 + manifest_size`;
  `Pool/CasRefLedger.cpp:256` and `:275` hardwire `.manifest_size = 0`). What is specific to this
  audit is the magnitude at wide-part shape and the second consequence: the same constant also
  defeats the oversized-bypass guard at `Parts/PartFolderAccess.cpp:196`
  (`view->estimatedBytes() <= params.max_entry_bytes`, default 16 MiB,
  `ContentAddressedSettings.cpp:54`), so **no** view is ever classified oversized and
  `CASPartFolderViewOversizedBypasses` can never fire. Each retained `PartFolderView` holds a
  `shared_ptr<const PartManifest>` (`Parts/PartFolderAccess.h:76`), which keeps the decoded manifest
  alive after the decode cache has evicted it.
- Trigger (part shape): a table with 10,000 live Wide parts of 1,000 columns each (~2,100 entries,
  ~0.5 MB decoded per part) read in a single scan, filling the cache to its
  `max_entries = 10,000` cap (`Parts/PartFolderAccess.h:130`, `ContentAddressedSettings.cpp:53`).
- Consequence: ~5 GB resident against a configured `part_folder_cache_bytes` of 64 MiB
  (`ContentAddressedSettings.cpp:52`); with a manifest at the 256 MiB cap a single such view is
  retained rather than bypassed, and the only bound is the entry count.
- Evidence: `Parts/PartFolderAccess.cpp:128-131,194-206`; `Pool/CasRefLedger.cpp:256,275`;
  `Parts/PartFolderAccess.h:76,127-133`; `ContentAddressedSettings.cpp:52-54`.

### bc5-6 -- Staging and publishing a wide part are quadratic in the number of files (Medium)

- Anchor: every staging mutation removes any prior entry for the same path with a linear
  `std::erase_if` over the staged vector: `ContentAddressedTransaction.cpp:510` (blob),
  `:652` (inline), `:810`, `:827` (hardlink), `:930` (moveDirectory), `:1051`, `:1064` (moveFile /
  replaceFile), `:1076-1078` (unlinkFile, which also does a preceding `std::any_of` scan).
  `findStagedEntry` (`:379-381`), `tryGetInFlightFileSize` (`:448`) and `hasInFlightDirectory`
  (`:462-464`) are linear too, and they are on the in-flight read path used while the part is being
  written. The publish-side merge is the same shape: `:268-272` runs `std::none_of` over the staged
  entries for **each** committed entry.
- Trigger (part shape): a Wide part with 20,000 columns produces ~42,000 `writeFile` completions in
  one transaction, so the staging scans alone are ~8.8e8 string comparisons; the publish merge on a
  committed part of the same width is O(M_committed x K_staged).
- Consequence: commit becomes CPU-bound and scales quadratically in file count, with no cap or
  short-circuit; the staged container is a `std::vector<ManifestEntry>` with no index
  (`ContentAddressedTransaction.h` `PartStaging::entries`), even though the manifest itself is
  canonically sorted and could be searched in O(log M).
- Evidence: the ten `erase_if`/`find_if` sites listed above; `ContentAddressedTransaction.cpp:268-272`.

### bc5-7 -- One object plus one meta object plus a 256-byte envelope per part file: a wide part with small files is dominated by per-object overhead (Medium)

- Anchor: `Pool/CasManifestReader.cpp:133-144` maps each blob entry to its own `layout.blobKey(ref)`
  with `offset = meta.blob_header_len`; there is no packing, no shared container object and no
  offset/length carve-out within a shared blob anywhere in the entry model
  (`Formats/CasPartManifestFormat.h:20-30` has only `ref` + `blob_size`). `blob_header_len` defaults
  to 256 (`Pool/CasPool.h:46`) and the envelope is **space-padded to exactly that width**
  (`Formats/CasBlobEnvelopeFormat.cpp:139`), with a hard floor of 240
  (`Formats/CasPoolMetaFormat.cpp:19-25`). Every fresh blob also writes a separate freshness-meta
  object (`Pool/CasPartWriteTxn.cpp:381-385`, plus the backfill path at `:287-292`).
- Trigger (part shape): a Wide part with 1,000 columns and 10,000 rows -- ~1,000 `.bin` files of a
  few KB and ~1,000 `.cmrk3` mark files of roughly 48 bytes each.
- Consequence: ~2,000 blob objects and ~2,000 meta objects, i.e. ~4,000 object-store PUTs for one
  INSERT of a single part; the marks contribute ~48 KB of payload inside ~512 KB of envelope padding
  (a >10x storage blow-up on those objects); and reading the part issues ~2,000 independent ranged
  GETs that each discard the first 256 bytes. The dedup HEAD-first optimisation does not apply,
  since `deduplication_head_first_min_bytes` defaults to 1 MiB (`ContentAddressedSettings.cpp:37`)
  and these files are far smaller. There is no CAS-level fan-out, coalescing, prefetch or per-part
  deadline on the read side -- `fanOutBlobUploads` (`ContentAddressedTransaction.cpp:1152`) exists
  only for the write path.
- Evidence: `Pool/CasManifestReader.cpp:137-143`; `Pool/CasPool.h:46`;
  `Formats/CasBlobEnvelopeFormat.cpp:133-142`; `Formats/CasPoolMetaFormat.cpp:19-25`;
  `Pool/CasPartWriteTxn.cpp:381-385`; `ContentAddressedMetadataStorage.cpp:1419-1445`.

### bc5-8 -- Mutating a wide part costs one manifest HEAD and one view rebuild per hardlinked file, because `part_folder_validate` defaults to `always` (Medium)

- Anchor: `ContentAddressedTransaction.cpp:816` -- `createHardLink` falls through to
  `getView(src->refKey(), Freshness::ForceFresh)` for every file that is not already staged in this
  transaction. In `getView`, the ForceFresh cache shortcut at `Parts/PartFolderAccess.cpp:172` is
  guarded by `params.validate.mode != PartFolderValidate::Mode::Always`, and the shipped default is
  `"always"` (`ContentAddressedSettings.cpp:55`, parsed into `PartFolderValidate` whose default
  member is also `Mode::Always`, `Parts/PartFolderAccess.h:87-92`). So the shortcut is dead by
  default and every call reaches `buildView` (`:231-235`) -> `readManifestShared`, which issues an
  unconditional `backend.head(key)` *before* consulting the decode cache
  (`Pool/CasManifestReader.cpp:58,76-79`), allocates a fresh `PartFolderView`, and re-inserts it into
  the view cache (`:194-198`).
- Trigger (part shape): a mutation (`ALTER ... UPDATE` on one column, or `ALTER TABLE ... MODIFY
  COMMENT`) on a Wide part with 1,000 columns, which hardlinks the ~2,100 unchanged files from the
  source part.
- Consequence: ~2,100 HEAD requests against the same manifest key, ~2,100 view allocations, ~2,100
  `resolve` round trips and ~2,100 `emitResolveEvent` audit events
  (`Parts/PartFolderAccess.cpp:213,217-229`) for one mutation. `unlinkFile` has a per-transaction
  memo for exactly this (`force_fresh_validated_refs`, `ContentAddressedTransaction.cpp:1081-1086`);
  `createHardLink` has none, so the memo's own premise is not applied on the path that needs it most.
- Evidence: `ContentAddressedTransaction.cpp:816`, `:1081-1086`;
  `Parts/PartFolderAccess.cpp:172-188,231-235,194-206,213`;
  `Pool/CasManifestReader.cpp:58,76-79`; `ContentAddressedSettings.cpp:55`;
  `Parts/PartFolderAccess.h:87-92`.

### bc5-9 -- Every per-file `existsFile`/`getFileSize` re-enters the ref-ledger runtime, so opening a wide part takes thousands of acquisitions of one per-namespace mutex (Low)

- Anchor: `ContentAddressedMetadataStorage.cpp:976` (`existsFile`), `:1164` (`getFileSize`),
  `:1333`/`:1362`/`:1396`/`:1432` (`getStorageObjects`, `getStorageObjectsIfExist`,
  `tryGetInManifestBytes`, `getBlobViewPlan`) all call `getView`, and `getView` calls `resolve` at
  `Parts/PartFolderAccess.cpp:152` **before** the view-cache lookup at `:158-170`. `resolveRef`
  runs `acquireReadableRefTableRuntime` + `ensureRefTableRecovered` + `sweepStalePrecommitsForRead` +
  `maybeScheduleSnapshotPublish` and then takes `state_mutex` again for the lookup
  (`Pool/CasRefLedger.cpp:217-232`). Each of the middle three has an early-return fast path but each
  takes `rt->state_mutex` to reach it (`:958-967`, `:3091-3098`, `:2807-2810`).
- Trigger (part shape): loading a Wide part with 1,000 columns; ClickHouse probes existence and size
  per stream, so ~2,000-4,000 metadata calls, each doing ~4 lock/unlock cycles on the single
  `state_mutex` shared with all writers to that namespace. Note also that `getStorageObjects`
  (`:1311`) calls `tryGetInManifestBytes` first, which itself does a full `poolAccess()` +
  `getView`, so that path pays two view lookups per file.
- Consequence: ~8,000-16,000 acquisitions of a namespace-global mutex per part open, contending with
  the ref-mutation leader; `getLastModified` (`:1177`) additionally uses the default
  `ResolveAudit::Emit`, so it emits one audit event per call rather than the deferred audit that
  `getView` uses.
- Evidence: `Parts/PartFolderAccess.cpp:149-170,280-284`; `Pool/CasRefLedger.cpp:214-232,958-967,3091-3098,2807-2810`;
  `ContentAddressedMetadataStorage.cpp:976,1164,1177,1311,1333`.

## Checked and sound

- The four hard caps are all enforced in `stageManifest` **before** the manifest object is PUT
  (`Pool/CasPartWriteTxn.cpp:511-544`) and raise `LIMIT_EXCEEDED` with the offending value and the
  cap in the message. There is no path that writes an over-cap manifest and then cannot read it.
- Write-side and read-side size caps agree: `kMaxManifestEncodedBytes` (256 MiB) matches
  `FormatId::PartManifest.object_cap` (`Formats/CasFormat.cpp:110`), and the reader checks both the
  raw stored size and the *declared decompressed* size against that cap
  (`Formats/CasTextFormat.cpp:378-392`), so a compressed manifest cannot expand past the budget.
- Per-file resolution on a warm view is O(log M), not a rescan: `findEntry` is a `lower_bound` over a
  canonically sorted vector (`Formats/CasPartManifestFormat.cpp:291-298`), the encoder sorts and
  rejects duplicate paths (`:77-81`), and the decoder rejects any non-ascending order
  (`:236-239`), so the binary search's precondition is enforced on the wire.
- The manifest is decoded once per part, not once per file: `PartFolderView` holds the decoded body
  and all per-file accessors read from it (`Parts/PartFolderAccess.cpp:80-126`), and the body is a
  `shared_ptr` shared between the decode cache and the view
  (`Pool/CasManifestReader.cpp:122-125`, `Parts/PartFolderAccess.h:76`), so there is one copy in
  memory, not two.
- Directory listing and `hasDirectory` use `entryRange`, an O(log M + range) prefix range rather than
  a full scan (`Formats/CasPartManifestFormat.cpp:300-311`); only `listChildren("")` on the part root
  is legitimately O(M).
- Projections and their subtrees live in the parent part's manifest under a `*.proj/` path prefix
  (`Parts/PartFolderAccess.cpp:68-78`), so opening or listing a projection costs no additional
  object-store round trip and shares the parent's cached view.
- Inline overflow is a graceful fallback, not a failure: a would-be inline file larger than 1 MiB is
  spilled and staged as a blob (`ContentAddressedTransaction.cpp:655-668`).
- Concurrent cold opens of the same part are deduplicated by the in-flight promise map, so N readers
  cause one manifest GET, not N (`Parts/PartFolderAccess.cpp:237-268`).
- The O(M) entry-ordering re-check in the `PartFolderView` constructor is a `chassert`
  (`Parts/PartFolderAccess.cpp:54-56`) and is compiled out in release builds
  (`base/base/defines.h:46`), so it is a debug/CI cost only, not a shipping per-view O(M) cost.
- There is no write-time validation that an entry record fits `line_cap` (64 KiB), but `promote`
  decodes the manifest before the ref transitions to committed
  (`Pool/CasPartWriteTxn.cpp:643-651`), so an over-long line fails closed pre-commit. It surfaces as
  `CORRUPTED_DATA` rather than a limit error, which is a poor diagnostic, but I could not construct a
  reachable trigger: it needs a single part-file name near 65 KB.
- `uploadPendingBlobs` filters staged blobs down to those still referenced by the final entry set
  before uploading (`ContentAddressedTransaction.cpp:210-220`), so an overwritten file in a wide part
  does not upload a blob that no entry names.

## Coverage

Read in full: `Formats/CasPartManifestFormat.{h,cpp}`, `Parts/PartFolderAccess.{h,cpp}`,
`Pool/CasManifestReader.{h,cpp}`, `Formats/CasFormat.{h,cpp}`, `Primitives/CasTypes.h`,
`Primitives/CasBlobDigest.h`, `ContentAddressedSettings.cpp`. Read in the relevant ranges:
`ContentAddressedTransaction.cpp` (staging, `writeFile`, `createHardLink`, `moveDirectory`,
`moveFile`, `unlinkFile`, `publishStaging`, `commit`, in-flight read helpers),
`ContentAddressedMetadataStorage.cpp` (`existsFile`, `existsDirectory`, `existsFileOrDirectory`,
`getFileSize`, `getLastModified`, `listDirectory`, `iterateDirectory`, `getStorageObjects`,
`tryGetInManifestBytes`, `getBlobViewPlan`, `startup`), `Pool/CasPartWriteTxn.cpp`
(`stageManifest`, `precommitAdd`, `promote`, `abandon`, `uploadFromSource`, `observeAndAdmit`,
`adoptEvidence`), `Pool/CasRefLedger.cpp` (`resolveRef`, `appendRefOps`, `runRefQueueLeader`,
`flushRefBatch` build-ops invocation, the recovery/sweep/publish fast paths),
`Formats/CasTextFormat.cpp` cap enforcement, `Formats/CasBlobEnvelopeFormat.cpp` header padding,
`Formats/CasPoolMetaFormat.cpp` header-length validation, `Pool/CasEventDispatcher.cpp`. Cross-checked
against `src/Storages/MergeTree` only to establish real Wide-part file names and the
`compress_primary_key` default.

Not covered here (owned by sibling audits): GC/in-degree accounting for the republished manifests and
orphaned scratch manifests; the ref-log/checkpoint encoding budgets; crash consistency of the
two-manifest publish; the missing pin across the blob GET; the envelope-vs-pool-meta offset question;
concurrency of the view cache itself. Not statically decidable and not claimed: actual wall-clock
latency, real S3 request accounting, and whether ClickHouse's own reader coalesces the per-column GETs
above the disk interface.

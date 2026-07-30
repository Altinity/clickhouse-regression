# bc5-wide-part-read-correctness — re-run 2026-07-30

CAS source: `/Volumes/workspace/ClickHouse` @ `cas-audit-20260730` (HEAD `834c9517f56`).

## Scope in current code

Wide-part read composition (per-column-file blob + inline-manifest fallback). Files walked:

- `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp` — `DiskObjectStorage::prepareRead` (813–923).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp`
  — `getStorageObjects` (1748), `getStorageObjectsIfExist` (1798), `tryGetInManifestBytes` (1833),
  `prepareInManifestRead` (1867), `getBlobViewPlan` (1886), `readBlobPayload` (1923), `getFileSize` (1536),
  `listDirectory` (1597), `iterateDirectory` (1714), `isDirectoryEmpty` (1727).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartFolderAccess.cpp`
  — `PartFolderView::findFile`/`fileSize`/`inlineBytes`/`listChildren`/`hasDirectory`,
  `projectionDirPrefix` (73–83).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.cpp`
  — `parsePartFilePath` (257–284).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasPartManifestFormat.cpp`
  — `findEntry` (329–336) + sorted-invariant enforcement (263–267), `entryRange` (339–351).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp`
  — `locate` (144–164).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.cpp`
  — `listRefs` (238–260).
- `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.cpp`
  — `listNamespaceFiles` (896–899), `listMirroredChildren` (1388+).
- `src/IO/ReadBufferFromFileView.cpp` — rebase discipline (13–177).

## Findings still present

### BC5-2 — Two size semantics; correctness depends on all reads going through `prepareRead` + FileView

- Anchor: `ContentAddressedMetadataStorage.cpp:1793` (getStorageObjects returns `StoredObject(location.key, path, location.length)` — payload only) vs `ContentAddressedMetadataStorage.cpp:1915` (getBlobViewPlan.object sized `location.offset + location.length` — envelope+payload).
- Trigger: any future/adjacent reader that constructs a buffer from `getStorageObjects` and does *not* go through `DiskObjectStorage::prepareRead`'s CA branch.
- Evidence (comment @ 1791–1792): "the header offset is applied by getBlobViewPlan's view window, the only byte-reading path."
- Notes: the in-manifest guard (empty-key placeholder @ 1757 for inline/verbatim bytes) makes a bypass **fail loudly** for in-manifest cases, but for blob-backed entries the returned StoredObject is a real physical key sized to the payload — a bypass would issue a `GET` from offset 0 for `location.length` bytes and consume the **envelope header** as the first bytes. Structural fragility unchanged; documented as invariant, not enforced. 🔴 still-present.

### BC5-3 — Inline vs blob split is decided at write finalize; a single wide part mixes two read paths

- Anchor: `DiskObjectStorage.cpp:830` (`prepareInManifestRead` short-circuits) and `ContentAddressedMetadataStorage.cpp:1867–1884` (memory-backed `ReadBufferFromOwnMemoryFile`) vs the standard blob/FileView path at 832+.
- Trigger: a part with only large columns never hits the inline branch; one with `primary.idx`/small `.mrk` inline only that branch — so a coverage matrix must exercise both.
- Notes: an inline entry that ever escapes the short-circuit and reaches `getBlobViewPlan` throws `BAD_ARGUMENTS` from `CasManifestReader::locate` (`case Inline: throw` @ CasManifestReader.cpp:162–164), not FILE_DOESNT_EXIST — see NEW-BC5-1 below. 🔴 still-present.

### BC5-4 — Mid-stream mark right-bound narrowing (setReadUntilPosition) correct but subtle

- Anchor: `src/IO/ReadBufferFromFileView.cpp:38–56` (`setReadUntilPosition`), 59–70 (`setReadUntilEnd`), 78–101 (`nextImpl`), 104–133 (`seek`), 138–162 (`executeWithOriginalBuffer` rebase helper).
- Trigger: `MergeTreeReaderStream` right-mark narrowing after the buffer has already been advanced past a previous mark — the underlying `ReadBufferFromS3` may discard its buffer on a range change, so `file_offset_of_buffer_end` must be re-anchored from `impl_buffer_end` on every op that can change the impl's position.
- Evidence: comment @ 62 "Same rebase contract as setReadUntilPosition"; @ 153 "read or seek over-reads / serves wrong bytes. `op` can throw (e.g. setReadUntilPosition ..."
- Notes: no defect found. The audit's prior recommendation — an explicit mid-stream `setReadUntilPosition` test — is **still not present** in `tests/integration/test_content_addressed_s3/test.py` (grep for `read_until_position|right.mark` yields nothing under `tests/`). Test-coverage gap unchanged. 🔴 still-present (coverage).

### BC5-5 — Projections read through the parent ref; nested-key routing branch

- Anchor: `PartFolderAccess.cpp:73–83` (`projectionDirPrefix`, matches `.proj` and `.tmp_proj`), `ContentAddressedMetadataStorage.cpp:1423–1428`, 1687–1691, 1742–1743 (`ProjectionDir` classify/list/isEmpty), `PartPathParser.cpp:264–273` (`parsePartFilePath` joins components after the part dir into `PartFilePath.file`, e.g. `col.proj/data.bin`).
- Trigger: a projection column read goes through the **same** `findFile` lookup on the parent manifest, keyed by the full nested path.
- Evidence: `PartFolderView::findFile` → `Cas::findEntry` binary search on the sorted `entries` vector (`CasPartManifestFormat.cpp:329–336`); sorted invariant enforced at decode (`:263–267`).
- Notes: correct by construction; the key-encoding parity between `parsePartFilePath` and `stageManifest` (writer side) is the load-bearing invariant. No defect. 🔴 still-present (informational; distinct-path coverage note).

### BC5-6 — Caches sit below the FileView (blob coordinates)

- Anchor: `DiskObjectStorage.cpp:876–923` — order is `needGather` → object-storage `prepareRead` (cache stage) → distributed cache → memory (page) cache → async prefetch → `needFileView`.
- Notes: unchanged; page-cache keys are blob-relative and correctly shared across parts referencing the same blob. ⚪ info.

## Findings fixed / no longer reproducible

None — every BC5-* is still structurally present. BC5-2's blast radius is partly mitigated by the empty-key placeholder for in-manifest bytes @ 1757 (bypassing reader fails loudly for that case), but the blob-backed case is not enforced, so BC5-2 remains 🔴 still-present.

## New findings (not in original audit)

### NEW-BC5-1 (Low) — inline entry reaching `getBlobViewPlan` throws BAD_ARGUMENTS, not the expected typed path

- Anchor: `Pool/CasManifestReader.cpp:144–164` — `locate(entry)` throws `BAD_ARGUMENTS` on `EntryPlacement::Inline`.
- Trigger: any call site that reaches `getBlobViewPlan` (`ContentAddressedMetadataStorage.cpp:1886`) on an inline entry without having first funneled through `prepareInManifestRead`. Under `DiskObjectStorage::prepareRead` (830) this cannot happen — `prepareInManifestRead` short-circuits — so it is currently unreachable via the primary read path. But `getBlobViewPlan` is a public method on `IContentAddressedExchange`; a future direct caller (relink offer builder, tooling, `system.remote_data_paths`-style path) would hit a raw `BAD_ARGUMENTS` where the design contract asks for either `std::nullopt` ("not blob-backed") or a typed FILE_DOESNT_EXIST.
- Note: reinforces BC5-2's structural-fragility concern — the "reads always go through prepareRead" invariant is again implicit, not enforced.

### NEW-BC5-2 (Med, cross-links STORE-2) — payload window offset is `meta.blob_header_len` (pool-wide constant), not the blob's own envelope `header_len`

- Anchor: `Pool/CasManifestReader.cpp:154–160` — `.offset = meta.blob_header_len`, propagated verbatim into `BlobLocation.offset` → `BlobViewPlan.payload_offset` (`ContentAddressedMetadataStorage.cpp:1916`) → `ReadBufferFromFileView` left-bound (DiskObjectStorage.cpp:922).
- Trigger: a blob written under a **different** `blob_header_len` than the current pool meta (config drift, mixed-version writer, or a pool meta rewrite) — the read window would start at the wrong offset and every byte returned to `MergeTreeReader` would be shifted by `Δheader_len`. This is exactly the code-only-pass STORE-2 finding surfacing on the read path: on a wide-part read, an entire column would decompress as garbage / `MergeTree` marks would point into the envelope header.
- Note: BC5-1's "one file = one blob = one payload" premise is only correctness-preserving as long as the pool-wide constant `blob_header_len` is a true invariant across every blob in the pool. There is **no per-blob header re-read** or cross-check on the read path (confirmed: `getBlobViewPlan` never touches the blob's envelope; the envelope is only validated during blob upload / GC revalidation, not on read). 🔴 latent hazard, previously missed by BC5-1's optimism.

### NEW-BC5-3 (Info) — payload integrity is NOT verified on the read path

- Anchor: `ContentAddressedMetadataStorage.cpp:1915–1922` (`getBlobViewPlan`), 1923–1933 (`readBlobPayload`) — neither the manifest `payload_digest` nor the per-entry `blob_hash` is recomputed on a normal read. This is the INT-1 / MC-1 finding (see `original-audit-gist.md` codeonly-line section) intersecting the wide-part read path: a bit-flip inside a blob's payload (or a shard-hosted mis-serve of a same-length blob with a different content) would be returned to the reader without detection.
- Note: informational — this is expected content-addressed-storage behavior once the reference is trusted (integrity trust is at the **manifest** level, not per read). But the audit is worth flagging because upstream MergeTree relies on **file-level checksums** for wide parts (`checksums.txt`) — and on CAS `checksums.txt` is itself a per-part inline/blob-backed file. If `checksums.txt` and the column blobs diverge (either bit-rot on the store, or a `blob_hash` corruption in the manifest per MC-1), the read returns silently-wrong bytes; only a subsequent `CHECK TABLE` catches it.

### NEW-BC5-4 (Low, coverage) — no test exercises FINAL / parallel-replica / patch-apply-on-read for wide parts on CAS (CAS-117 unfixed)

- Anchor: `tests/integration/test_content_addressed_s3/test.py` — grep for `FINAL` yields one occurrence (`OPTIMIZE TABLE cas_test FINAL`, not a `SELECT ... FINAL`); patch-part testing exists only for the persistence path (`test_mutations_and_patch_parts_survive_restart`), which forces a lightweight-update but does not exercise **apply-on-read** semantics against a wide part; no test uses `allow_experimental_parallel_replicas` / `parallel_replicas_for_non_replicated_merge_tree` against a CAS disk.
- Trigger: `SELECT ... FINAL` against a CAS ReplacingMergeTree wide part; parallel-replica scan across CAS-backed shards; `SELECT` after `ALTER TABLE ... UPDATE ... IN PARTITION` with `enable_lightweight_update=1` (patch apply on read).
- Note: original CAS-117 concern is still valid — the three read-path shapes above compose the FileView layer with row-level filtering / patch stream merging / cross-replica coordination, none of which are covered.

## By-design / N/A / info

- **BC5-1 (one file = one blob = one payload)** — confirmed structurally by `Pool::locate` returning exactly `.offset = meta.blob_header_len, .length = entry.blob_size` (one contiguous payload window per file). `needGather` still runs but joins a single object. ⚪ info / by-design.
- **CAS-116 read-path lookups** — `PartFolderView::findFile` and `Cas::findEntry` are **O(log N)** binary search on the sorted manifest entries (`CasPartManifestFormat.cpp:329–336`; sorted invariant enforced @ `:263–267`); `entryRange` is `lower_bound` + linear on the prefix range (`:339–351`). Not the linear-scan hazard CAS-116 called out — that concern applies to the enumeration paths (`listNamespaceFiles`, `listMirroredChildren`) which are S3-LIST-paginated and orthogonal to the wide-part read hot path. 📐 by-design on read.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| BC5-1 | Info | 📐 by-design (confirmed) | `Pool/CasManifestReader.cpp:151–160` |
| BC5-2 | Med  | 🔴 still-present (fragility, partly mitigated for in-manifest bytes) | `ContentAddressedMetadataStorage.cpp:1793` vs `:1915` |
| BC5-3 | Low  | 🔴 still-present | `DiskObjectStorage.cpp:830`, `ContentAddressedMetadataStorage.cpp:1867` |
| BC5-4 | Low  | 🔴 still-present (rebase intact; explicit mid-stream test still missing) | `src/IO/ReadBufferFromFileView.cpp:38–101` |
| BC5-5 | Low  | 🔴 still-present (info) | `PartFolderAccess.cpp:73–83`, `PartPathParser.cpp:264–273`, `CasPartManifestFormat.cpp:329–336` |
| BC5-6 | Info | ⚪ info (confirmed) | `DiskObjectStorage.cpp:876–923` |
| NEW-BC5-1 | — | 🟡 new (Low) | `Pool/CasManifestReader.cpp:162–164` |
| NEW-BC5-2 | — | 🔴 new (Med) — read-path facet of code-only STORE-2 | `Pool/CasManifestReader.cpp:154–160` |
| NEW-BC5-3 | — | ⚪ new (Info) | `ContentAddressedMetadataStorage.cpp:1923–1933` |
| NEW-BC5-4 | — | 🔴 new (Low, coverage) — CAS-117 concretion | `tests/integration/test_content_addressed_s3/test.py` |

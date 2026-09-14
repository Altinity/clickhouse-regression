# datatype-agnosticism -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: the single filename classifier `partFileMustStayBlob` and both consumers in `ContentAddressedTransaction.cpp`; inline vs blob buffers; `Formats/CasPartManifestFormat.cpp` (path validation, banner, ordering); `Formats/CasLayout.cpp` (blob keys); read path `prepareInManifestRead` / `getBlobViewPlan` / `getStorageObjects`; upstream name space `ISerialization.cpp`, `MergeTreeIndexGranularityInfo.cpp`, `IMergeTreeDataPart.h:863`, `MergeTreeIndices.h`, `MergeTreeIndexText.cpp`, `MergeTreeSettings.cpp` (`write_marks_for_substreams_in_compact_parts`, `compress_primary_key`).
- Explicitly out of scope: GC/ref protocols, exchange cookie, encryption.

Question: does CAS treat every column type / stream file equally, or does a type-specific path break?

## Findings
### datatype-agnosticism-1 -- Compact-part marks `.cmrk4` / `.mrk4` are not in the blob allowlist (Medium)
- Anchor: `ContentAddressedTransaction.cpp:67-75` (suffixes stop at `.cmrk3` / `.mrk3`) vs `MergeTreeIndexGranularityInfo.cpp:98` (`res + (with_substreams ? "4" : "3")`); defaults `write_marks_for_substreams_in_compact_parts=true` (`MergeTreeSettings.cpp:406`) and `compress_marks=true`.
- Trigger: any Compact part under default settings (`data.cmrk4`). Size grows with granules × substreams (`Tuple`/`Nested`/`Map`/`JSON`/`Dynamic`).
- Evidence: CAS never uses `MarkType::isMarkFileExtension`. Marks take `CaInlineWriteBuffer`, embed in the manifest when `<= 1 MiB`, charge the 16 MiB inline budget, skip the autocommit-blob guard, and lose content-addressed dedup. Reads are placement-agnostic, so this is cost/memory, not wrong bytes. Same class as CAS-014.
- Notes: CAS-014.

### datatype-agnosticism-2 -- `primary.idx` special case is dead under default `compress_primary_key` (Medium)
- Anchor: `ContentAddressedTransaction.cpp:69` (`file_name == "primary.idx"`) vs `IMergeTreeDataPart.h` `getIndexExtension` (`.cidx` when compressed); `MergeTreeSettings.cpp:2125` (`compress_primary_key=true`).
- Trigger: any table with a non-empty primary key under defaults. Wide `ORDER BY` on a large part produces a multi-megabyte `primary.cidx`.
- Evidence: the literal never matches the shipped name. The file is inlined or RAM-buffered-then-spilled to *local* scratch, bypassing S3 staging. Same class as finding 1.
- Notes: CAS-014.

### datatype-agnosticism-3 -- secondary-index and packed-archive files take the in-memory inline route (Medium)
- Anchor: `ContentAddressedTransaction.cpp:71-74` (no `.idx` / `.idx2` / `.packed`); `:1982` unbounded `accumulated`.
- Trigger: `INDEX … TYPE vector_similarity` (`skp_idx_*.idx` HNSW), `TYPE text` (`.dct.idx`/`.pst.idx`/`.pos.idx`), bloom/minmax/set, or `skp_idx.packed`.
- Evidence: a merge that rebuilds a gigabyte-scale vector or text index holds the whole file in a `std::string` before the 1 MiB overflow can spill. Same merge on a plain object-storage disk streams. No type-aware branch exists to fix this except expanding the suffix list.
- Notes: CAS-014.

### datatype-agnosticism-4 -- the classifier is a closed suffix allowlist with no unknown-kind diagnostic (Low)
- Anchor: `ContentAddressedTransaction.cpp:67-75` is the entire classifier; GC/fsck/inspect branch on `EntryPlacement`, never on extension.
- Trigger: a future marks/index extension (the set is documented as versioned per substream).
- Evidence: new kinds fail silently toward "small metadata": RAM buffer, manifest embed, inline-budget consumption, loss of the autocommit guard. Nothing logs or meters the misclassification.
- Notes: consequence of CAS-014, not a separate corruption path.

## By-design / info / non-actionable
- Column substreams (`.null`, `.sizeN`, `.dict`, Variant/Dynamic/JSON `object_shared_data.*`) always end in `.bin` or a marks extension and classify correctly as blobs once the marks suffix is recognized. The marks `4` gap is the leak, not the stream-name grammar.
- Blob object keys are digest-only (`CasLayout.cpp`); column names never reach a key. Entry paths are bytewise ordered and JSON-escaped.
- Per-column codecs are transparent: CAS hashes the bytes it is handed.
- Read path is placement-agnostic (`tryGetInManifestBytes` vs `getBlobViewPlan`).
- Payload-zone banners are escaped (`CasPartManifestFormat.cpp:65-79`). A raw LF in a path is no longer an undecodable manifest.

## Closed-since-2026-08-12
- Unescaped payload-zone banner / LF in path (`datatype-agnosticism-6` / CAS-040 encode half): `bannerFor` now escapes through the same `stringValue` as the record line.

## Coverage
- Reviewed: classifier and both call sites; inline/blob buffers; manifest path/banner/order; layout keys; read-path placement; upstream stream/marks/primary/index extensions.
- N-A: type-specific CAS branches besides the suffix list (none exist).
- Deferred: measured RSS / manifest sizes (static only).

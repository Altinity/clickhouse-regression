# bc5-wide-part-read -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `ContentAddressedTransaction.cpp` (`partFileMustStayBlob`, `INLINE_CAP`, `findPendingBlob`, `writeFile`), `Pool/CasPartWriteTxn.cpp` (`kMaxManifestInlineBytesTotal`, `stageManifest`), `Formats/CasPartManifestFormat.{h,cpp}`, `Pool/CasManifestReader.cpp`, `Parts/PartFolderAccess.cpp` (`buildView`, `repointRef`), `src/Storages/MergeTree/MergeTreeIndexGranularityInfo.h` (mark suffixes), `MergeTreeIndicesSerialization.h` (`skp_idx_`), `IMergeTreeDataPart` / settings for `primary.cidx`.
- Explicitly out of scope: view-cache weight (`Resolved::manifest_size`); locate offset-from-pool-meta (read-protocol); 16 MiB cap *mechanism* is shared with bc2-3 — here the question is the classifier that feeds it.

## Findings
### bc5-1 -- placement allowlist still omits `primary.cidx`, `.mrk4`/`.cmrk4`, and skip-index files (Medium)
- Anchor: `ContentAddressedTransaction.cpp:67-75` (`partFileMustStayBlob`); `:100` (`INLINE_CAP = 1 MiB`); `Pool/CasPartWriteTxn.cpp:55,533-535` at ceee42c
- Trigger: a Wide part whose primary index is `primary.cidx` (`compress_primary_key` defaults true), or whose marks are `.mrk4`/`.cmrk4` (`MergeTreeIndexGranularityInfo.h:18`), or that has `skp_idx_*.idx` / `.idx2` files (`MergeTreeIndicesSerialization.h:10-32`). None of those names match `{primary.idx, .bin, .mrk, .mrk2, .mrk3, .cmrk, .cmrk2, .cmrk3}`. Nested projection paths use the leaf name (`p->file`), so `<proj>.proj/primary.cidx` misses as well.
- Evidence: those files go through `CaInlineWriteBuffer`, which accumulates the *entire* file in a `std::string` (`:1978-1983`) and only then decides. `<= 1 MiB` is inlined; above that it spills to a local scratch file and a second write (`:976-998`). Many skip-index files just under 1 MiB are all inlined; their sum hits the 16 MiB aggregate cap and `stageManifest` throws `LIMIT_EXCEEDED` (bc2-3) after column blobs have already uploaded. Not corruption: there is a per-file cap and a blob spill. The cost is buffering the whole file plus a double write, and a loud commit failure for a part shape that is legal on a plain disk.
- Notes: same root as CAS-014. Classifier is still a closed allowlist.

### bc5-2 -- pending-blob lookup is still a linear scan of a vector (Low)
- Anchor: `ContentAddressedTransaction.cpp:214-222` (`findPendingBlob`); `ContentAddressedTransaction.h` (`pending_blobs` as `std::vector`) at ceee42c
- Trigger: a part with many blob files and any path that calls `findPendingBlob` per entry (hardlink / adopt / merge of staged blobs).
- Evidence: each lookup walks the whole vector. Staging mutations (`erase_if` on `st.entries` at `:973`, `moveDirectory` destination scans) are the same shape. Cost is string compares against one PUT per file, not a correctness break. Same residual as CAS-116.

### bc5-3 -- every blob still pays envelope + `.meta` on first publication (Low)
- Anchor: `Pool/CasPartWriteTxn.cpp:281,302,337-351`; `Formats/CasBlobEnvelopeFormat.cpp:153-158`; `Pool/CasPool.h:58` (`blob_header_len = 256`) at ceee42c
- Trigger: first publication of a blob-classified file (or an inline overflow).
- Evidence: each new blob is `blob_header_len` padded envelope plus a separate `.meta` sibling. Small eager metadata is inlined (bc5-1), so a wide part of *small* files does not multiply this cost per column metadata file. Residual is per *blob* overhead, already the packing/inline class.

## By-design / info / non-actionable
- One `ManifestEntry` per part file, no packing. Decode still re-encodes for `payload_digest` (bc4-3).
- Cold `CachedForLoad` view builds are single-flight per `ns+ref` (`PartFolderAccess.cpp:268-287`). `ForceFresh` does not coalesce (one HEAD per caller).
- `repointRef` still ForceFresh-resolves and encode/decode-compares before publishing (`PartFolderAccess.cpp:555-567`). Byte-equal path does zero pool mutations. Carry-forward `createHardLink` still ForceFresh-resolves (CAS-055 class; not re-derived as a new quadratic here).

## Closed-since-2026-08-12
- None of the classifier names were added. The previous High "wide part is unreadable / corrupt" consequence is not re-raised: the 1 MiB cap and blob spill are still there; the real cost is memory + double write + the 16 MiB aggregate (CAS-014 / CAS-044).
- Inline-path `PartWriteTxn` missing for all-inline parts: `buildFor` is now called on the inline path (`ContentAddressedTransaction.cpp:965`). Closed.

## Coverage
- Reviewed: `partFileMustStayBlob` vs current MergeTree file names; per-file inline buffer; aggregate 16 MiB cap; pending-blob scan; blob envelope/meta overhead; view single-flight.
- N-A: protobuf (bc4).
- Deferred: measured decode-cache / view-cache byte weighting (CAS-045; sibling cache audit).

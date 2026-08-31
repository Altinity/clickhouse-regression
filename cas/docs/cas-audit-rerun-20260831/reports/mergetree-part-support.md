# mergetree-part-support -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `ContentAddressedTransaction.{h,cpp}` (`partFileMustStayBlob`, write buffers, `createHardLink`/`moveFile`/`replaceFile`/`moveDirectory`, `publishStaging`), `Parts/PartPathParser.{h,cpp}`, `Parts/PartFolderAccess.{h,cpp}`, `Pool/CasPartWriteTxn.cpp` (inline caps, `stageManifest`), `Formats/CasPartManifestFormat.cpp` (path banner escaping), `ContentAddressedMetadataStorage.cpp` (routing, `isDirectoryEmpty`, `getStorageObjects`), MergeTree hooks `DataPartStorageOnDiskBase.cpp` (`freeze`/`freezeRemote`/`clonePart`), `IMergeTreeDataPart.h` (primary-index extension), `MergeTreeIndexGranularityInfo.cpp` (marks `4`), `MergeTreeIndices.h` / `MergeTreeIndexText.cpp`, `UniqueKey/DeleteBitmapFileOps.cpp` / `MergeTreeBitmapStore.cpp`.
- Explicitly out of scope: write-protocol blob publish race, GC in-degree, encryption wrapper (sibling `encryption`), concurrency of unconditional repoint.

Question: which MergeTree part shapes, file kinds, and engine features CAS actually supports on `ceee42c`.

## Findings
### mergetree-part-support-1 -- 16 MiB per-part inline budget is commit-only, with no spill fallback (Medium)
- Anchor: `ContentAddressedTransaction.cpp:67-75` (`partFileMustStayBlob`); `:100` (`INLINE_CAP = 1 MiB`); `:942-989` (per-file inline vs overflow); `Pool/CasPartWriteTxn.cpp:55,533-535` (`kMaxManifestInlineBytesTotal`, `LIMIT_EXCEEDED`).
- Trigger: a part whose inline-classified files each stay at or under 1 MiB but sum over 16 MiB. Reachable with many projections (`<name>.proj/primary.idx` fails the exact `"primary.idx"` compare), many skip-index substreams, or a wide Compact part whose `data.cmrk4` + `primary.cidx` plus metadata sit under the per-file cap.
- Evidence: placement is decided per file in `writeFile`. `stageManifest` is the first place the aggregate is seen and it throws; there is no "reclassify this inline entry as a blob because the part total overflowed" path. The failure is deterministic on retry. Loud, no silent corruption. Same root cause as CAS-044.
- Notes: CAS-044.

### mergetree-part-support-2 -- non-allowlisted part files are accumulated whole in RAM before any spill (Medium)
- Anchor: `ContentAddressedTransaction.cpp:1982` (`CaInlineWriteBuffer` `accumulated.append`); `:942-989` (overflow writes that same string to local scratch).
- Trigger: writing `skp_idx_*.idx` / `.idx2` / text `.dct.idx`/`.pst.idx`/`skp_idx.packed`, `primary.cidx`, or `data.cmrk4` larger than a few megabytes (vector_similarity / text index materialize or merge).
- Evidence: the blob path (`CaContentWriteBuffer`) streams. The inline path has no spill-while-writing; the 1 MiB overflow happens only in `finalizeImpl` after the full `std::string` is held. Peak RSS equals the file plus a second local copy. Failures are OOM or ENOSPC, not silent wrong bytes. Same class as CAS-014.
- Notes: CAS-014.

### mergetree-part-support-3 -- unique-key delete-bitmap publish is tmp+replaceFile and throws LOGICAL_ERROR on CAS (Medium)
- Anchor: `ContentAddressedTransaction.cpp:1552-1557` (`moveFile` "source not staged" `LOGICAL_ERROR`); `:1560-1575` (`replaceFile` delegates); `UniqueKey/DeleteBitmapFileOps.cpp:48-71` (`removeFileIfExists` + `writeFile(.tmp)` + `replaceFile`); sole production-shaped caller `MergeTreeBitmapStore.cpp:123`.
- Trigger: wiring unique-key/upsert so `writeBitmapToStorage` runs against a committed part on a CAS disk. Each of remove/write/replace is its own autocommit transaction (`DataPartStorageOnDiskFull` / `DiskObjectStorage`).
- Evidence: the `.tmp` write commits in transaction A; `replaceFile` in transaction B does not find the source in `src_st.entries` and throws. `VersionMetadataOnDisk` already branches on `supportsAtomicFileWrites()` to avoid this; `DeleteBitmapFileOps` does not. No non-test caller of `MergeTreeBitmapStore::install` today, so the hole is latent. Same shape as CAS-057.
- Notes: CAS-057.

### mergetree-part-support-4 -- Ordinary-layout `detached`/`moving` as a database or table name is folded as the reserved container (Low)
- Anchor: `Parts/PartPathParser.cpp:202-227` (leftmost `detached`/`moving` at index `>= 1` wins; comment and test name `DetachedNamedTableIsKnownAmbiguityFoldedAsReservedDir`).
- Trigger: a non-Atomic database or table literally named `detached` or `moving` on a CAS disk.
- Evidence: the parser is string-only and documents the ambiguity. Atomic UUID anchors still win. Failures are mis-routed refs, not a new grammar. Same accepted limitation as CAS-087; still no fail-closed refusal on a reserved name used as a table id.
- Notes: CAS-087.

## By-design / info / non-actionable
- Wide/Compact, MergeTree family engines, ReplicatedMergeTree relink, patch parts (`looksLikePartDir` accepts `patch-<hash>-<partition>_min_max_level`), `_row_exists`, `detached/`/`moving/`/`shadow/` prefixes, tmp/delete_tmp names: supported.
- `isDirectoryEmpty` returns true for a part dir (`ContentAddressedMetadataStorage.cpp:1880-1888`) so `removeDirectory` can drop the ref. That also defeats `Backup`'s `DIRECTORY_ALREADY_EXISTS` guard — owned by `alter-merge-mutation`.
- Projection `.tmp_proj`→`.proj` is an in-transaction prefix rewrite; temp projections share the parent transaction on CAS.
- `WriteMode::Append` / `truncateFile` / autocommit of blob-class files refused loudly.
- Zero-copy replication remains off for CAS (`DiskObjectStorage.h`).
- Manifest entry paths and payload-zone banners are JSON-escaped (`CasPartManifestFormat.cpp:65-79`). A projection name containing `\n` no longer produces an undecodable orphan.

## Closed-since-2026-08-12
- CAS-040 / newline-in-path wedge: `bannerFor` now uses `CasJsonWriter::stringValue` (`CasPartManifestFormat.cpp:70-78`); orphan sweep skips undecodable manifests (`CasOrphanManifestSweep.cpp:891-893`, `2649bce42db`).
- CAS-058 / `freezeRemote` without a CAS transaction: `DataPartStorageOnDiskBase.cpp:687-704` now owns one transaction and `copyDirectoryContentIntoTransaction` (`84b30f6b0d9`).
- Shadow/FREEZE namespace not scoped by `server_root_id`: `shadowNamespace` is `serverPrefix() + "/" + canonical` (`ContentAddressedMetadataStorage.cpp:1356-1361`, `335802a938f`).
- Text-index tmp dir leftover as a silent `removeRecursive` no-op: `moveDirectory` now `dropRefIfPresent` on the committed `text_index_tmp` scratch ref (`ContentAddressedTransaction.cpp:1416-1423`). Residual is an extra publish-then-drop, not a stuck ref.

## Coverage
- Reviewed: file-kind classifier and both call sites; inline/blob buffers and caps; part-path grammar (Atomic UUID, Ordinary, detached/moving/shadow, projections); unique-key bitmap write; freeze/clone/freezeRemote; patch-part names; reserved-name ambiguity.
- N-A: InMemory parts (type gone).
- Deferred: runtime RSS/manifest-size measurement; UniqueKey production wiring.

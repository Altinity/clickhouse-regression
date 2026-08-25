# mergetree-part-support -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is. CAS root `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`. Static reasoning only; shipped strings and code are the only evidence (all CAS tests are deleted in the tree; docs/comments are not treated as intent).

Question: which MergeTree part shapes, file kinds and engine features does CAS actually support? Walked the file-kind classifier (`partFileMustStayBlob`, `Parts/PartPathParser`, inline caps in `CasPartWriteTxn::stageManifest`), the write/rename/remove surface of `ContentAddressedTransaction`, and the MergeTree-side CAS hooks (`isContentAddressed()`, `supportsAtomicFileWrites()`, `supportsTransactionalMutableFiles()`).

Two structural facts frame everything below and are **not** re-derived here (see the sibling reports `codeonly-line.md`, `write-protocol.md`, `concurrency.md`):

- Placement is decided purely by filename suffix; only `.bin`, `.mrk*`, `.cmrk*` and the exact string `"primary.idx"` stay blobs.
- `getLastModified` is one publish timestamp for the whole part; `isDirectoryEmpty` is always true for part dirs.

There is **no mutable-file set in this fork**. `supportsTransactionalMutableFiles()` returns true (`ContentAddressedMetadataStorage.h:119`), but the implementation of a rewrite/removal on an already-committed part is "read the committed manifest, merge, publish a whole new manifest, repoint the ref" (`ContentAddressedTransaction.cpp:256-291` → `PartFolderAccess.cpp:442-473`). So the "mutable?" column below means only "rewritable at all", and every rewrite costs a full manifest republish. The repoint is an unconditional overwrite with no expected-old-manifest compare-and-swap (`CasPartWriteTxn.cpp:697-705`); the lost-update consequences of that are the concurrency report's subject.

## File-kind classification matrix

Anchors: blob set `ContentAddressedTransaction.cpp:65-73`; inline/blob split at write time `ContentAddressedTransaction.cpp:598-670` (`INLINE_CAP = 1 MiB`, `:92`); commit-time caps `CasPartWriteTxn.cpp:52-55, 507-544`.

| file kind | blob/inline | mutable? | anchor | risk |
| --- | --- | --- | --- | --- |
| `<col>.bin`, `data.bin` (Wide/Compact) | blob (streamed) | yes, whole-manifest republish | `ContentAddressedTransaction.cpp:69` | none |
| `_row_exists.bin` (lightweight delete) | blob | as above | `ContentAddressedTransaction.cpp:69`, `MergeTreeVirtualColumns.cpp:24` | none |
| `*.mrk`, `*.mrk2`, `*.mrk3` | blob | as above | `ContentAddressedTransaction.cpp:69` | none |
| `*.cmrk`, `*.cmrk2`, `*.cmrk3` (compressed marks) | blob | as above | `ContentAddressedTransaction.cpp:69` | none |
| `primary.idx` (top-level only, exact compare) | blob | as above | `ContentAddressedTransaction.cpp:67` | none |
| `<name>.proj/primary.idx` | **inline** (exact compare fails on the `<name>.proj/` prefix) | as above | `ContentAddressedTransaction.cpp:67` vs route file `PartPathParser.cpp:197-203` | finding 1, 2 |
| `primary.cidx` (`compress_primary_key`) | **inline** | as above | `IMergeTreeDataPart.h:863` | finding 1, 2 |
| `skp_idx_<name>.idx` / `.idx2` (all skip-index types) | **inline** | as above | `MergeTreeIndices.h:266` | finding 1, 2 |
| `skp_idx_<name>.idx` written by `vector_similarity` (HNSW) | **inline** | as above | `MergeTreeIndices.h:266`, `MergeTreeIndices.cpp:231` | finding 2 (High) |
| text/GIN substreams `skp_idx_<name>.dct.idx`, `.pst.idx`, `.pos.idx` | **inline** | as above | `MergeTreeIndexText.cpp:1741-1747` | finding 2 (High) |
| `skp_idx_<name>.mrk2` (skip-index marks) | blob | as above | `ContentAddressedTransaction.cpp:69` | asymmetric with its data file |
| `skp_idx.packed` (packed skip-index archive) | **inline** | as above | `MergeTreeSettings.cpp:1952-1959` | finding 1, 2 |
| `statistics_<col>.stats`, `statistics.packed` | **inline** | as above | `Statistics.h:13-14` | finding 1 |
| `minmax_<col>.idx` | **inline** | as above | `IMergeTreeDataPart.cpp:191, 248` | finding 1 |
| `partition.dat` | **inline** | as above | — | none |
| `columns.txt`, `checksums.txt`, `count.txt`, `default_compression_codec.txt`, `serialization.json`, `ttl.txt`, `columns_substreams.txt`, `uuid.txt`, `delete-on-destroy.txt` | **inline** | as above | `IMergeTreeDataPart.h:551-578` | finding 1 on very wide schemas |
| `metadata_version.txt` | **inline** | yes: `beginTransaction` + `removeFileIfExists` + `writeFile` + `commitTransaction` | `IMergeTreeDataPart.cpp:1666-1681` | sound (republish cost only) |
| `txn_version.txt` | **inline** | yes: CAS takes the atomic single-write branch, no rename | `VersionMetadataOnDisk.cpp:329-337` | sound |
| `txn_version.txt.tmp` | inline (only on the non-CAS branch) | — | `VersionMetadataOnDisk.cpp:22, 339-357` | finding 5 (reachable via an encrypted wrapper) |
| `delete_bitmap_<csn>.rbm` and its `.tmp` sibling | **inline** | published by tmp-write + `replaceFile` | `DeleteBitmap.cpp:29-30`, `DeleteBitmapFileOps.cpp:54-71` | finding 4 |
| any inline-classified file > 1 MiB | auto-promoted to a blob, but only after full RAM buffering | as above | `ContentAddressedTransaction.cpp:654-669` | finding 2 |
| `<name>.proj` / `<name>.tmp_proj` directory | not an entry; a path prefix inside the parent manifest | — | `PartFolderAccess.cpp:68-78` | none |

## Engine/part-shape support matrix

| shape / feature | support | anchor / behavior |
| --- | --- | --- |
| Wide parts | supported | per-column `.bin`/`.mrk*` all blobs |
| Compact parts | supported | `data.bin` + `data.cmrk3` blobs |
| InMemory parts | not applicable | the type no longer exists in this fork: `MergeTreeDataPartType.h:20-25` has only `Wide`, `Compact`, `Unknown` |
| MergeTree, ReplacingMergeTree, CollapsingMergeTree, SummingMergeTree, AggregatingMergeTree, VersionedCollapsingMergeTree, GraphiteMergeTree | supported, engine-agnostic | CAS never inspects the engine; merge modes add no new file kinds (`MergeTreeData.cpp:1893-1901`) |
| ReplicatedMergeTree | supported | manifest-relink fast path inside one pool (`DataPartsExchange.cpp:310-330`, receiver `:757-794`), byte fetch otherwise; ordering of the projection count vs manifest payload matches on both sides |
| zero-copy replication | disabled by design | `DiskObjectStorage.h:51-54` excludes `MetadataStorageType::CAS`, so the empty `remote_path` that inline entries return (`ContentAddressedMetadataStorage.cpp:1368-1369`) never reaches `getUniqueId`-based locks |
| projections | supported | temp projections are forced into the parent transaction on CAS (`IMergeTreeDataPart.cpp:1359`, `MergeTask.cpp:562`); `.tmp_proj`→`.proj` rename handled for staged entries (`ContentAddressedTransaction.cpp:893-906`) |
| secondary/skip indexes (minmax, set, bloom_filter, ngram/token bf, text/GIN, vector_similarity) | functionally supported, but every index **data** file is inline | findings 1 and 2 |
| patch parts | supported | partition id `patch-<hash>-<original>` (`PatchPartInfo.h:29`) still ends in `_min_max_level`, so `looksLikePartDir` accepts it (`PartPathParser.cpp:101-132`) |
| lightweight delete (`_row_exists`) | supported | blob file inside an ordinary mutation part |
| delete bitmaps / unique-key upsert structures | present in the tree, **breaks on CAS** | finding 4; no non-test caller of `writeBitmapToStorage` today (`MergeTreeBitmapStore.cpp:123` is the only one) |
| detached parts, all name variants | supported | refs are prefixed `detached/` (`ContentAddressedMetadataStorage.cpp:914-921`); the part component after `detached` is taken verbatim, so `broken_`, `unexpected_`, `covered-by-`, `attaching_`, `ignored_`, `_tryN` all classify |
| `moving/` parts | supported | `kMovingRefPrefix`, `ContentAddressedMetadataStorage.cpp:922-929` |
| `shadow/` (FREEZE) | supported | shadow namespace routing `PartPathParser.cpp:204-208`; `BACKUP` via temporary hard links is explicitly refused (`DataPartStorageOnDiskBase.cpp:417-422`) |
| temporary (`tmp_*`, `tmp-fetch_*`), broken, covered parts | supported | ordinary refs; names classify |
| part removal (`delete_tmp_` rename) | supported, expensive | finding 8 |
| zero-column / zero-file part dirs | cannot be represented | `createDirectory` is a no-op (`ContentAddressedTransaction.cpp:673-681`) and `existsDirectory(PartDir)` is `existsRef` (`ContentAddressedMetadataStorage.cpp:1102-1103`), so a part dir exists only once it has at least one file |
| encrypted disk over CAS | accepted by config, then fails | finding 5 |
| cache metadata wrapper / read-only wrapper over CAS | sound | both forward `isContentAddressed` (`MetadataStorageFromCacheObjectStorage.cpp:172-175`, `ReadOnlyDiskWrapper.h:88`) |
| `WriteMode::Append` on a part file | rejected loudly | `ContentAddressedTransaction.cpp:536-537` |
| `truncateFile` on a part file | rejected loudly | `ContentAddressedTransaction.cpp:1130-1135` |

## Findings

### mergetree-part-support-1 -- the 16 MiB per-part inline budget is enforced only at commit, with no fallback, and index/projection files are the ones spending it (High)

- **Anchor**: `Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:638-669` (per-file decision, `INLINE_CAP = 1 MiB` at `:92`); `.../Pool/CasPartWriteTxn.cpp:54` (`kMaxManifestInlineBytesTotal = 16 MiB`) enforced at `:514-528`, reached from `ContentAddressedTransaction.cpp:297` / `:262`; classifier `ContentAddressedTransaction.cpp:65-73`.
- **Trigger**: any part whose inline-classified files sum to more than 16 MiB while each individual file stays at or under 1 MiB. Concretely reachable with (a) many projections — each `<name>.proj/primary.idx` is inline because the classifier compares the whole route file against the literal `"primary.idx"` and the route file for a projection is `<name>.proj/primary.idx` (`PartPathParser.cpp:197-203`), plus a per-projection `checksums.txt`/`serialization.json`/`columns.txt`/`minmax_*.idx`; or (b) a few dozen sub-MiB skip-index substreams (`MergeTreeIndices.h:266`, text substreams `MergeTreeIndexText.cpp:1741-1747`, packed archive `MergeTreeSettings.cpp:1952`).
- **Consequence**: the per-file placement decision is local and cannot see the aggregate, so the overflow is discovered only when `stageManifest` runs during commit and it throws `LIMIT_EXCEEDED`. The write path has no "spill this inline entry to a blob because the part total is too big" fallback (compare `:654-669`, which spills only on the per-file 1 MiB test). The failure is deterministic: retrying the same INSERT, mutation or merge rebuilds the same entry set and fails again, so the part can never be written and — if two such parts already exist — merges over them fail permanently.
- **Evidence**: `stageManifest` computes `inline_total` over the entries it was handed and throws before any ref work; nothing between `writeFile` and `stageManifest` re-examines placement. `partFileMustStayBlob` contains no `.idx`, `.idx2`, `.cidx`, `.packed`, `.stats` or projection-aware case.

### mergetree-part-support-2 -- every non-blob-suffixed part file is materialized whole in RAM, so vector and text index files are unbounded memory (High)

- **Anchor**: `ContentAddressedTransaction.h:188-205` and `.cpp:1336-1348` (`CaInlineWriteBuffer::accumulated` is a `std::string` appended in `nextImpl`, consumed only in `finalizeImpl`); selection at `.cpp:638`; the >1 MiB overflow path at `.cpp:654-669` writes that same string to a local scratch file (`metadata_storage.scratchPath()`) and only then stages a blob.
- **Trigger**: writing any file whose name is not `.bin`/`.mrk*`/`.cmrk*`/`primary.idx`. The large kinds are `skp_idx_<name>.idx` for `vector_similarity` (HNSW graph, routinely hundreds of MB to GB), text-index postings/dictionary substreams `skp_idx_<name>.pst.idx` / `.dct.idx`, `skp_idx.packed`, `statistics.packed`, `primary.cidx`, and `checksums.txt`/`serialization.json` on very wide schemas.
- **Consequence**: peak resident memory equals the full serialized index size per file being written concurrently (INSERT, merge and mutation all build indexes), followed by a full extra copy to local scratch and then an upload — i.e. 1x RAM + 1x local disk + 1x network for data that the blob path streams. Blob-suffixed files use `CaContentWriteBuffer`, which streams to the sink and never accumulates (`.cpp:1269-1295`), so the asymmetry is purely a consequence of the suffix list.
- **Evidence**: `CaInlineWriteBuffer::nextImpl` unconditionally appends the working buffer; there is no size guard, no spill-while-writing, and no memory budget check in either the buffer or `writeFile`.

### mergetree-part-support-3 -- parts near the inline budget bypass the part-folder view cache entirely (Medium)

- **Anchor**: `.../Parts/PartFolderAccess.cpp:196-206` (retain only when `view->estimatedBytes() <= params.max_entry_bytes`), `estimatedBytes() = 256 + manifest_size` at `:128-131`, default `max_entry_bytes = 16 MiB` at `PartFolderAccess.h:131` and `ContentAddressedSettings.cpp:54`.
- **Trigger**: a part whose encoded manifest exceeds 16 MiB — which the inline budget of finding 1 permits right up to its own 16 MiB limit, since inline payloads are stored inside the manifest body (`CasPartManifestFormat.cpp:102-111`).
- **Consequence**: the two caps are numerically adjacent, so exactly the parts that are legal-but-large are never retained: every `existsFile`, `getFileSize`, `listDirectory` and read of such a part re-GETs and re-decodes the whole multi-MB manifest, including all inline payloads. Metadata probe cost per part file becomes O(manifest size) instead of O(1), with a `CASPartFolderViewOversizedBypasses` bump each time.
- **Evidence**: the oversized branch increments the bypass event and returns the view without inserting it into `view_cache`; there is no partial-retention or payload-stripped variant.

### mergetree-part-support-4 -- "write .tmp then replaceFile" against a committed part is unsupported and throws LOGICAL_ERROR (Medium)

- **Anchor**: `ContentAddressedTransaction.cpp:1026-1055` (`moveFile` only looks for the source in `src_st.entries`, i.e. entries staged in *this* transaction, and otherwise throws `LOGICAL_ERROR: moveFile source not staged`), `:1058-1067` (`replaceFile` delegates to `moveFile`); each of `removeFileIfExists`/`writeFile`/`replaceFile` on a part with no active part transaction becomes its own CAS transaction (`DataPartStorageOnDiskFull.cpp:277-319`, `DiskObjectStorage.cpp:276-281, 325-335`).
- **Trigger**: `DeleteBitmapFileOps::writeBitmapToStorage` (`DeleteBitmapFileOps.cpp:54-71`): `removeFileIfExists(tmp)`, `writeFile(tmp)`, `getDirectorySyncGuard()`, `replaceFile(tmp, delete_bitmap_<csn>.rbm)` on a part that is already committed. The `.tmp` write commits in transaction A; the `replaceFile` runs in transaction B, where the source exists only in the committed manifest, so `moveFile` throws.
- **Consequence**: publishing a delete bitmap (the unique-key/upsert structure in this fork) fails on a CAS disk, and it fails after the `.tmp` entry has already been committed into the part manifest — leaving a `delete_bitmap_<csn>.rbm.tmp` entry behind that nothing else prunes (the next attempt does `removeFileIfExists` on it, which is a second manifest republish). Today this is dormant: `MergeTreeBitmapStore::install` at `MergeTreeBitmapStore.cpp:123` is the only caller of `writeBitmapToStorage` and it has no non-test caller, so the hazard is "the moment unique-key writes are wired up, they break on CAS", plus the same trap for any future tmp+rename metadata file.
- **Evidence**: the guarded counter-example proves the pattern is known and was handled elsewhere: `VersionMetadataOnDisk::storeInfoToDataPartStorage` branches on `supportsAtomicFileWrites()` and writes `txn_version.txt` directly on CAS (`VersionMetadataOnDisk.cpp:329-337`), taking the `createFile`+tmp+`replaceFile` path only otherwise (`:339-357`). `DeleteBitmapFileOps` has no such branch.

### mergetree-part-support-5 -- an encrypted disk over CAS reports "not content-addressed", disabling every CAS hook while still routing writes into CAS (Medium)

- **Anchor**: `Disks/DiskEncrypted.h:24` (`class DiskEncrypted : public IDisk`) overrides `getRefCount` (`:395-399`) and `getDelegateDiskIfExists` (`:390-393`) but never `isContentAddressed()` or `supportsAtomicFileWrites()`, so the `IDisk` defaults apply (`IDisk.h:475-477`, both `false`); contrast `ReadOnlyDiskWrapper.h:88`, which does forward it.
- **Trigger**: a storage configuration layering `type=encrypted` over a CAS disk. Nothing in the CAS metadata storage or in `MergeTreeData` rejects it (no encryption-aware code exists anywhere under the CAS root).
- **Consequence**: every MergeTree CAS hook silently turns off — `restorePartFromBackup` stops opening a disk transaction (`MergeTreeData.cpp:7499`), `freeze` stops owning one (`DataPartStorageOnDiskBase.cpp:531`), `clonePart` takes the copy path (`:702`), temp projections stop using the parent transaction (`IMergeTreeDataPart.cpp:1359`, `MergeTask.cpp:562`), the relink fetch path disappears (`DataPartsExchange.cpp:111`), and `txn_version.txt` falls back to tmp+`replaceFile` and hits finding 4. Meanwhile writes still reach `ContentAddressedTransaction`, where the transaction-free per-file write of a `.bin`/`.mrk*` file is explicitly refused: `tryCreateWriteBuffer` throws `NOT_IMPLEMENTED` when `autocommit && partFileMustStayBlob` (`ContentAddressedTransaction.cpp:539-544`). The operator gets a "not implemented for a content-addressed disk … the disk is wrapped by a layer that bypasses the content-addressed write path" error at INSERT time instead of a configuration-time rejection.
- **Evidence**: the `NOT_IMPLEMENTED` message at `:541-544` describes exactly this wrapping scenario, and `DiskEncryptedTransaction::writeFileImpl` (`DiskEncryptedTransaction.cpp:82-118`) forwards to `delegate_transaction->writeFileWithAutoCommit` for the autocommit case, i.e. straight into the refused branch.

### mergetree-part-support-6 -- on non-UUID layouts a path component literally named `detached` or `moving` outranks part-dir detection (Medium)

- **Anchor**: `.../Parts/PartPathParser.cpp:140-162`: when no `<3hex>/<uuid>` pair is found, the parser scans from `i = 1` for **any** component equal to `detached`/`moving` and anchors the part dir there, before ever trying `looksLikePartDir`; routing then treats that component as the container (`ContentAddressedMetadataStorage.cpp:914-929`).
- **Trigger**: a non-Atomic (Ordinary-layout) data path such as `data/detached/<table>/<part>/<file>` — i.e. a database named `detached` (or `moving`), or a table so named, on a CAS disk. No CAS or MergeTree code requires an Atomic database; the only nearby guard is the BACKUP message at `DataPartStorageOnDiskBase.cpp:420-422`, which merely *recommends* Atomic.
- **Consequence**: `table_uuid` collapses to `data`, `ref` becomes `detached/<table>`, and every part of every table in that database is flattened into one ref per table with the part name folded into the entry path. The removal path then silently does nothing: `removeRecursive` on such a part hits `if (r && !r->ref.empty()) return;` (`ContentAddressedTransaction.cpp:764-765`) because `r->file` is non-empty, so dropped parts are never removed from the manifest and their blobs are never released — unbounded manifest growth and permanent blob retention with no error anywhere.
- **Evidence**: the `detached`/`moving` scan has no positional constraint (no "must be the component right after the table dir") and no interaction with `looksLikePartDir`, which is only consulted afterwards.

### mergetree-part-support-7 -- an unclassified part-dir name is silently reinterpreted as a table-level file rather than rejected (Low)

- **Anchor**: `.../Parts/PartPathParser.cpp:101-132` (`looksLikePartDir` requires at least four `_`-separated groups with the last three all numeric) is the only part-dir recognizer for non-UUID layouts; when it fails, `parseTableFilePath` falls through to its catch-all `table_uuid = <all but last component>, tail = <last component>` (`:274-277`).
- **Trigger**: any MergeTree-generated part directory under a non-UUID data path whose name does not end in `_<num>_<num>_<num>`. Present part-name formats all satisfy the heuristic (`all_1_1_0`, `all_1_1_0_5`, `20140317_20140323_2_2_0`, `tmp_insert_*`, `tmp-fetch_*`, `delete_tmp_*`, `patch-<hash>-<partition>_1_1_0`), so this is latent rather than currently broken.
- **Consequence**: a future or third-party part-naming variant is not rejected loudly — its files are written into the table's namespace-file space as verbatim objects (`ContentAddressedTransaction.cpp:562-578`), where they are invisible to ref listing, to GC's blob in-degree accounting and to part removal. Misfiled instead of failed.
- **Evidence**: neither `parsePartFilePath` nor `parseTableFilePath` ever raises on an unclassifiable shape; the only `LOGICAL_ERROR`s are raised later, by callers that need two part paths (`moveDirectory` `:889-891`, `createHardLink` `:787-789`).

### mergetree-part-support-8 -- part removal costs a full manifest republish and is not atomic across the rename (Low)

- **Anchor**: `Storages/MergeTree/DataPartStorageOnDiskBase.cpp:844-896` renames the part dir to `delete_tmp_<name>` before removing it; on CAS that rename resolves to `moveDirectory` → `republishRef` (`ContentAddressedTransaction.cpp:955-962`, `PartFolderAccess.cpp:419-440`), which reads the source manifest, **publishes a brand-new manifest** for the `delete_tmp_` ref, then drops the source ref.
- **Trigger**: any ordinary part removal (outdated-part cleanup, DROP PARTITION, post-merge cleanup).
- **Consequence**: removing a part performs a manifest PUT plus two ref-log transactions plus a second removal pass, so cleanup generates write traffic and fresh blob in-degree edges proportional to the part's file count. Because publish and drop are separate ref transactions, an interruption between them leaves the part live under both `all_1_1_0` and `delete_tmp_all_1_1_0`; recovery relies on `clearOldTemporaryDirectories` recognizing the `delete_tmp_` prefix (`MergeTreeData.cpp:3364-3378`, prefix list at `:4184`) and on `getLastModified` being old enough — but the republish just reset that timestamp to now (`ContentAddressedMetadataStorage.cpp:1172-1183`, `isOldPartDirectory` at `:3319-3321`), so the leftover survives at least one full `temporary_directories_lifetime` window while holding all of the part's blobs.
- **Evidence**: `republishRef` publishes before dropping and has no combined transaction; `dropRef` of the source is a separate `store->dropRef` call.

## Checked and sound

- **Engine independence.** CAS never looks at the merge mode; Replacing/Collapsing/Summing/Aggregating/VersionedCollapsing/Graphite introduce no new file kinds, so support follows the file-kind matrix. Patch parts and `_row_exists` classify correctly.
- **`metadata_version.txt` rewrite.** `IMergeTreeDataPart::writeMetadataVersion` (`IMergeTreeDataPart.cpp:1666-1681`) wraps remove+write in one part transaction; CAS merges the committed manifest with the staged entry and the removal mark in a single repoint (`ContentAddressedTransaction.cpp:256-291`).
- **`txn_version.txt`.** The `supportsAtomicFileWrites()` branch avoids the tmp+rename trap (`VersionMetadataOnDisk.cpp:329-337`).
- **Manifest canonical order.** The merge in `publishStaging` appends staged entries after committed ones without sorting, but `encodePartManifest` sorts and rejects duplicate paths (`CasPartManifestFormat.cpp:71-81`) and `decodePartManifest` re-checks ascending order (`:236-239`), so the binary searches in `findEntry`/`entryRange` stay valid.
- **Projection lifecycle on CAS.** `use_parent_transaction` is forced for CAS temp projections (`IMergeTreeDataPart.cpp:1359`, `MergeTask.cpp:562`), which is what makes the staged `.tmp_proj`→`.proj` rewrite in `ContentAddressedTransaction.cpp:893-906` always find its staging (the staging key is the part ref, and the projection dir is part of the entry path).
- **Replication protocol ordering.** The sender writes the projection count before the relink manifest (`DataPartsExchange.cpp:304-325`) and the receiver reads them in the same order (`:757-790`), with a cookie-value mismatch falling back to a byte fetch.
- **Zero-copy interaction.** Inline entries expose an empty `remote_path` (`ContentAddressedMetadataStorage.cpp:1368-1369`) and `getHardlinkCount` is hard-coded to 0 (`ContentAddressedMetadataStorage.h:121`), but `DiskObjectStorage::supportZeroCopyReplication()` excludes CAS (`DiskObjectStorage.h:51-54`), so the `getRefCount`/`getUniqueId` consumers in `StorageReplicatedMergeTree.cpp:10614-10621, 11586-11595` are unreachable.
- **Loud refusals rather than silent wrong behavior**: `WriteMode::Append` on part files (`:536-537`), `truncateFile` (`:1130-1135`), autocommit writes of blob-class files (`:539-544`), `createMetadataFile`/`chmod`/`generateObjectKeyForPath` (`:83-90`), BACKUP via temporary hard links (`DataPartStorageOnDiskBase.cpp:417-422`), and `republishRef` refusing a destination that already holds different content (`PartFolderAccess.cpp:426-435`).
- **`isTransactional()` is not overridden** by CAS, so `DiskObjectStorage::createDirectories`' `while (!existsFileOrDirectory(path))` loop (`DiskObjectStorage.cpp:419-429`) is not entered — which matters because `createDirectory` is a no-op on CAS and an empty part dir never becomes observable.
- **InMemory parts** cannot be reached: the part type is gone from this fork (`MergeTreeDataPartType.h:20-25`).

## Coverage

Read in full or in the relevant range: `ContentAddressedTransaction.{h,cpp}` (classifier, write buffers, all mutating verbs, commit/rollback), `Parts/PartPathParser.{h,cpp}`, `Parts/PartFolderAccess.{h,cpp}`, `Formats/CasPartManifestFormat.{h,cpp}`, `Pool/CasPartWriteTxn.cpp` (caps, `stageManifest`, `promote`), `ContentAddressedMetadataStorage.h` plus its routing/probe/list/size/mtime/storage-object sections. MergeTree side: `DataPartStorageOnDiskBase.cpp` (backup, freeze, clonePart, rename, remove), `DataPartStorageOnDiskFull.cpp`, `IMergeTreeDataPart.{h,cpp}` (metadata file constants, projections, metadata-version write), `VersionMetadataOnDisk.cpp`, `MergeTreeData.cpp` (empty parts, restore-from-backup, temporary-directory cleanup), `MergeTask.cpp`, `MutateTask.cpp` (index extensions, renames), `DataPartsExchange.cpp` (relink both sides), `MergeTreeIndices.h` / `MergeTreeIndexText.cpp` / `MergeTreeIndicesSerialization.h` (index file extensions), `MergeTreeSettings.cpp` (packed skip-index archive), `Statistics.h`, `UniqueKey/*` (delete bitmaps, SST writer), `MergeTreeDataPartType.h`, `DiskEncrypted.h` / `DiskEncryptedTransaction.cpp`, `IDisk.h`, `DiskObjectStorage.{h,cpp}`, `ReadOnlyDiskWrapper.h`, `MetadataStorageFromCacheObjectStorage.cpp`.

Not covered here (owned by siblings, deliberately not duplicated): suffix-based placement rationale and `getLastModified`/`isDirectoryEmpty` semantics (`codeonly-line.md`); lost-update and interleaving consequences of the unconditional repoint (`concurrency.md`, `interleaving.md`); wide-part read amplification (`bc5-wide-part-read.md`); crash windows in the ref protocol (`crash-consistency.md`, `write-protocol.md`); GC treatment of manifests produced by republish (`gc-protocol.md`); cross-disk/cross-pool ATTACH (`ISSUE-DRAFT-cas020-cross-disk-attach.md`). No dynamic verification was performed: all CAS tests are deleted in the working tree, so every claim above rests on the shipped code and its shipped strings.

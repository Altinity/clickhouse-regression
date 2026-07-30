# mergetree-part-support — re-run 2026-07-30

## Scope in current code
- Files/dirs walked:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/` (`PartPathParser.{h,cpp}`, `PartFolderAccess.{h,cpp}`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp` (unlinkFile, chmod, generateObjectKeyForPath, truncateFile, writeFile)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedExchange.h`
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.{h,cpp}` (isContentAddressed surface)
  - `src/Disks/DiskObjectStorage/DiskObjectStorage.{h,cpp}` — `isContentAddressed()`, `supportZeroCopyReplication()`
  - Adjacent integration hooks (CAS-only branches):
    - `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp` — BACKUP temp-hardlink CAS reject (B16/B34)
    - `src/Storages/MergeTree/MergeTreeData.cpp` — `checkContentAddressedDiskRestrictions` (ALTER allow-list, via `MetadataStorageType::ContentAddressed` case) + `choosePartFormat` + UNIQUE KEY non-local reject
    - `src/Storages/MergeTree/DataPartsExchange.cpp` — `Fetcher::relinkPartToDisk` (including `to_detached` staging)

## Findings still present

### `CAS-042` — BACKUP is Atomic-DB-only (Ordinary/non-UUID rejected)
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:422-427` (`backup(...)` — temp-hardlink CAS gate)
- Trigger: `BACKUP TABLE` on an Ordinary (or otherwise non-UUID) database whose part storage is on a CAS disk → temp-hardlink path enters CAS reject.
- Evidence quote:
  > `if (make_temporary_hard_links && disk->isContentAddressed()) throw Exception(ErrorCodes::SUPPORT_IS_DISABLED, "BACKUP via temporary hard links is not supported on a content_addressed disk yet (B16/B34); use an Atomic database (which backs up via pointer-holding) instead; disk '{}'", ...);`
- Notes: Unchanged from original B-1. Pointer-holding path (`make_temporary_hard_links=false`, Atomic DBs) unaffected. Incremental-backup dedup + RESTORE round-trip still untested by static reading (no covering fixture visible in Parts/).

### `CAS-041` (B-2) — Cross-disk `MOVE PARTITION TO DISK/VOLUME` still unverified
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:6740-6763` (`checkContentAddressedDiskRestrictions`, ALTER allow-list, `MetadataStorageType::ContentAddressed` case)
- Trigger: `ALTER TABLE ... MOVE PARTITION ... TO DISK/VOLUME` (cross-disk) — admitted by the allow-list which cannot distinguish `TO TABLE` (verified) from `TO DISK/VOLUME` (byte-copy `clonePart`).
- Evidence quote:
  > `NOTE:  MOVE_PARTITION  also admits cross-disk  MOVE ... TO DISK/VOLUME  (this check cannot distinguish the destination); that uses the byte-copy clonePart path (NOT the corrupting per-file hardlink), but only same-disk MOVE ... TO TABLE is verified here — cross-disk is a follow-up to verify.`
- Notes: Original B-2 unchanged; the comment itself acknowledges "follow-up to verify."

### `CAS-105` (B-3) — Packed storage-type parts (arriving via RESTORE/ATTACH) still untested
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:5147-5168` (`choosePartFormat` always returns `PartStorageType::Full`), and `src/Storages/MergeTree/MergeTreeData.cpp:7588-7591` (broken-part fake restore path forces `Full`/`Wide`).
- Trigger: `RESTORE` or `ATTACH` of a **Packed**-storage part produced on a non-CAS disk onto a CAS disk.
- Evidence quote:
  > `return {part_type, PartStorageType::Full};`
- Notes: CAS write path still never emits Packed; no code path in `ContentAddressed/**` models a single-file packed container, so an incoming Packed part on RESTORE/ATTACH remains outside the tested envelope. Note also `MergeTreeData.cpp:7340-7345` explicitly rejects RESTORE on UNIQUE KEY tables (`"RESTORE of data is not supported for UNIQUE KEY tables yet"`), which narrows the RESTORE surface but does not close the Packed gap.

### `CAS-055` — Non-MergeTree engines / `tmp` disks / SSD-cache dict / Distributed spool: still ungated at DDL/config on a CAS disk
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:531-534` (`generateObjectKeyForPath` → `notYet` → `NOT_IMPLEMENTED`), `:1188-1191` (`chmod` → `NOT_IMPLEMENTED`), `:756-772` (append/autocommit rejects), `:1603-1607` (`truncateFile` → `NOT_IMPLEMENTED`).
- Trigger: Attaching a non-MergeTree engine (Log/StripeLog/…), using a CAS disk as a `tmp_path` / SSD cache backing / Distributed spool. There is no engine- or purpose-level DDL/config gate in the CAS layer or in `DiskObjectStorage`; the failure surfaces mid-write as `NOT_IMPLEMENTED` from the transaction shim.
- Evidence quote (from `notYet(op)` at line 88-91):
  > `throw Exception(ErrorCodes::NOT_IMPLEMENTED, "The operation '{}' is not implemented for a content-addressed disk: it belongs to the generic disk-transaction surface that the content-addressed write path does not use. ...");`
- Notes: A fail-closed check at DDL/`registerStorageMergeTree`/`tmp_policy` setup would still be the right fix (per original G4/G5/G6/G8); no such check exists in-tree.

### `CAS-073` (B-4, adjacent) — Non-Atomic (Ordinary DB) recognition still by grammar heuristic
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.cpp:136-168` (`looksLikePartDir`), invoked at `:225-227`.
- Trigger: Any non-Atomic layout — the uuid anchor is absent, so a directory is admitted as a part iff its **last three underscore-separated groups are decimal** (`_min_max_level`).
- Evidence quote:
  > `return is_number(groups[n - 1]) && is_number(groups[n - 2]) && is_number(groups[n - 3]);`
- Notes: Unchanged shape (original B-4 / CAS-073). Coupling to MergeTree part-name grammar persists on Ordinary DBs. Reserved-directory anchors (`detached/`, `moving/`) precede this scan (`:210-212`) so those cases don't need the heuristic; the risk is only for future part-name tails that stop matching `_ _ _`.

### `CAS-007` — UniqueKey/upsert MergeTree DeleteBitmap + SSTIndex hot-rewrite mismatch with CAS
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:4523-4531` (schema-change disk check), `src/Storages/MergeTree/MergeTreeData.cpp:7340-7345` (RESTORE UNIQUE KEY reject).
- Trigger: Any attempt to place a UNIQUE KEY table on a CAS disk.
- Evidence quote:
  > `if (desc.type != DataSourceType::Local) throw Exception(ErrorCodes::SUPPORT_IS_DISABLED, "UNIQUE KEY on non-local disks is not yet supported ...");`
- Notes: Downgraded severity — UNIQUE KEY tables are now blocked from **any** non-local disk (which includes CAS as an object-storage backend), so the DeleteBitmap-triggered whole-part republish and SSTIndex hot-rewrite scenarios are unreachable **from a supported configuration**. The underlying mismatch (delete-bitmap not in the mutable-per-part set) remains untested and would resurface if the non-local guard is lifted. Not a CAS-code fix — it is an upstream fence.

## Findings fixed / no longer reproducible

### `CAS-110` (B-5) — FETCH-to-detached now relinks (source-token gated)
- Fix anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:1388-1449` (`Fetcher::relinkPartToDisk`, `bool to_detached` parameter), staged under `TABLE/detached` and folded onto the `detached/DIR` ref by the CA router.
- Evidence quote:
  > `Stage under the tmp-fetch dir OF THE TARGET PARENT — the table dir, or  TABLE/detached  when the caller asked for a detached fetch (B66b). ... a relinked part re-keys exactly as a byte-fetched one does.`
- Also `:700-704`:
  > `to_detached  is now a parameter of  relinkPartToDisk  (it stages under the  detached/  parent), and  try_zero_copy  goes back to meaning real zero-copy only.`
- Caveat: The allow-list comment at `MergeTreeData.cpp:6730-6733` is now stale — it still says "relink-into-detached is deferred, see backlog." Behaviour has changed; comment lags. Minor doc/comment drift.

### `CAS-111` (B-6) — Committed single-file `unlinkFile` no longer a fail-open no-op
- Fix anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1509-1569` (`unlinkFile` case 2 stages a `content_removed` mark, resolved by `publishStaging` into a repoint-remove; superseded by same-transaction `removeDirectory`).
- Evidence quote:
  > `A lone surgical unlink NOT followed by a ref-drop in the same transaction (ATTACH's  removeVersionMetadata , a future backfill/repair delete) resolves to one repoint-remove — this closes the file's former fail-open`
- Notes: The load-bearing "storm-then-drop = 1 ref-drop + 0 repoints" invariant is preserved (the drop supersedes marks), so no perf regression on MergeTree's fast-removal path. The latent bug flagged by original B-6 / CAS-111 is closed by construction.

## New findings (not in original audit)

### `NEW-mergetree-part-support-1` — Stale comment implying FETCH-to-detached relink is still deferred (Info)
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:6730-6733`
- Trigger: Reader (or downstream audit) trusts the comment which says "relink-into-detached is deferred, see backlog", but `Fetcher::relinkPartToDisk` now honors `to_detached` (see CAS-110 fix). Only a documentation/comment drift; no functional issue.
- Severity: `⚪ info` (documentation).

### `NEW-mergetree-part-support-2` — ALTER allow-list admits `MOVE_PARTITION` unconditionally; still no runtime split for `TO DISK/VOLUME` (Med, restated)
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:6744-6756` and the `checkPartitionCanBeDropped`/executor path that dispatches `MOVE_PARTITION` in `MergeTreeData::alterPartition` (`:7113-7134`).
- Trigger: same as CAS-041 above; noted separately because the allow-list is the DDL-gate point where a stricter split (`command.move_destination_type == TABLE` only) could be enforced now without cross-disk verification work.
- Severity: `🛠 will-fix` (call-site could differentiate `MOVE ... TO TABLE` from `MOVE ... TO DISK/VOLUME` via `command.move_destination_type` — the field is available in the executor at `:7115`).

### `NEW-mergetree-part-support-3` — No CAS-side gate for non-MergeTree engines / tmp-policy / SSD-cache dict (restated with anchor) (Low-Med)
- Anchor: absence of any storage-kind check in `ContentAddressed/**` or `DiskObjectStorage::isContentAddressed()` call sites; `DiskObjectStorage.cpp:766-777` shows only the CA cap flag, no engine gate.
- Trigger: `StorageLog`, `SET default_temporary_files_disk = <ca-disk>`, `<layout>ssd_cache</layout>` dictionary source pointing at a CA disk — surfaces as `NOT_IMPLEMENTED` from the CA transaction shim (see CAS-055).
- Severity: `🟡 needs-repro` — same shape as CAS-055 but re-anchored at the CAS layer to make the missing gate explicit.

## By-design / N/A / info
- **Wide vs Compact** — both are N-files → N-entries in the manifest; CAS is layout-agnostic. `choosePartFormat` still always emits `PartStorageType::Full` (`MergeTreeData.cpp:5167`). Verified.
- **Projections** — `PartFolderView::projectionDirPrefix` recognises `.proj`/`.tmp_proj` (`PartFolderAccess.cpp:73-80`). Nested manifest-key model unchanged. Verified.
- **Patch parts / lightweight deletes** — no special CA handling required; `looksLikePartDir` grammar covers `patch-<partition_id>_<min>_<max>_<level>` and mutation-added `_row_exists` still travels as an ordinary column file.
- **Detached** — `kDetachedRefPrefix = "detached/"` (`PartPathParser.h:49`); reserved-dir anchor at `PartPathParser.cpp:210-212`. Verified.
- **Temporary** (`tmp_insert_`, `tmp_merge_`, `delete_tmp_`) — grammar-anchored; `looksLikePartDir` covers them.
- **Frozen / shadow** — `kShadowDirName = "shadow"` (`PartPathParser.h:19`), FREEZE routing at `PartPathParser.cpp:274-282`; FREEZE/UNFREEZE now in ALTER allow-list (`MergeTreeData.cpp:6752-6755`). Verified.
- **ReplicatedMergeTree fetch-by-relink** — `DataPartsExchange.cpp:159-162, 403-406, 1388-` — supported and now also honours `to_detached`. Verified.
- **Zero-copy replication** — intentionally disabled: `DiskObjectStorage.h:54-58` returns false for `MetadataStorageType::ContentAddressed`. By design (CAS-203 supports mapping).
- **CAS-203** — "all mainstream MergeTree part types supported" — re-verified in this run for Wide, Compact, projections, patch parts, lightweight-delete artifacts, detached, temp, frozen, Replicated fetch-by-relink. Only Packed remains outside the envelope (CAS-105).

## Verdict summary table
| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-007 | FEATURE-GAP / PERF | 🚫 not-a-bug (fenced upstream: UNIQUE KEY blocked on non-local disks) | `src/Storages/MergeTree/MergeTreeData.cpp:4523-4531`, `:7340-7345` |
| CAS-041 (B-2) | FEATURE-GAP / PERF | 🔴 still-present (unverified) | `src/Storages/MergeTree/MergeTreeData.cpp:6740-6763` |
| CAS-042 (B-1) | FEATURE-GAP | 🔴 still-present | `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:422-427` |
| CAS-055 | CONFIG / FEATURE-GAP | 🔴 still-present (no engine/tmp/dict DDL gate) | `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:531-534, 1188-1191, 1603-1607` |
| CAS-073 (B-4) | DECODE / STRUCTURAL | 🔴 still-present (Ordinary-DB grammar heuristic) | `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Parts/PartPathParser.cpp:136-168` |
| CAS-105 (B-3) | TEST-GAP / FEATURE-GAP | 🔴 still-present (Packed on RESTORE/ATTACH) | `src/Storages/MergeTree/MergeTreeData.cpp:5147-5168`, `:7588-7591` |
| CAS-110 (B-5) | PERF / TEST-GAP | ✅ fixed (FETCH-to-detached now relinks) | `src/Storages/MergeTree/DataPartsExchange.cpp:700-704, 1388-1449` |
| CAS-111 (B-6) | CORRECTNESS | ✅ fixed (unlink now stages content_removed) | `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:1509-1569` |
| CAS-203 | INFO | ⚪ info — re-verified (all mainstream types still supported) | `PartPathParser.{h,cpp}`, `PartFolderAccess.cpp:73-80`, `DataPartsExchange.cpp:1388-`, `MergeTreeData.cpp:5167, 6744-6756` |
| NEW-mergetree-part-support-1 | — | ⚪ info (stale comment) | `src/Storages/MergeTree/MergeTreeData.cpp:6730-6733` |
| NEW-mergetree-part-support-2 | — | 🛠 will-fix (differentiable at ALTER dispatch) | `src/Storages/MergeTree/MergeTreeData.cpp:6744-6756`, `:7113-7134` |
| NEW-mergetree-part-support-3 | — | 🟡 needs-repro (missing CAS-side engine gate) | `src/Disks/DiskObjectStorage/DiskObjectStorage.cpp:766-777` |

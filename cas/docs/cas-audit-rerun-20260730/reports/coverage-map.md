# coverage-map — re-run 2026-07-30

Static re-verification of the original CAS coverage-map audit against the current PR #2073 code
(`altinity/cas-gc-rebuild`, worktree at `/Volumes/workspace/ClickHouse`, branch
`cas-audit-20260730`). Method: enumerate CAS-specific tests actually present in the checked-out
tree, then map each original coverage-gap finding (G1–G12, tracked as `CAS-007`, `CAS-041`,
`CAS-055`, `CAS-061`, `CAS-105`, `CAS-109`) to whether a targeted test now exists. Static reasoning
only.

## Scope in current code

Files/dirs walked:

- CAS code root — `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
  (`Backend/`, `Formats/`, `Gc/`, `Parts/`, `Pool/`, `Primitives/`, `Tools/`, `benchmarks/`,
  `ContentAddressed{MetadataStorage,Transaction,Exchange,Settings}.{h,cpp}`).
- CAS integration hooks — `src/Storages/MergeTree/{MergeTreeData,MergeTask,MergeTreeDataWriter,
  IMergeTreeDataPart,DataPartStorageOnDiskBase,DataPartsExchange}.cpp`,
  `src/Disks/{IDisk.h,ReadOnlyDiskWrapper.h,DiskObjectStorage/DiskObjectStorage.{h,cpp},
  DiskObjectStorage/DiskObjectStorageCache.cpp}`,
  `src/Disks/DiskObjectStorage/MetadataStorages/Cache/MetadataStorageFromCacheObjectStorage.{h,cpp}`.
- Test surfaces:
  - `tests/queries/0_stateless/*content_addressed*` (32 files) and `*cas*` (4 files: 05011,
    05015, 05016, 05022).
  - `tests/integration/test_content_addressed_*` (5 tests: `s3`, `shared_pool`, `gc_s3`,
    `ref_snaplog`, `drop_pool_member`) and `tests/integration/test_cas_*` (5 tests:
    `replicated_relink`, `lazy_load_recovery`, `insert_fault_recovery`, `gc_sharded`,
    `file_cache`).
  - CAS unit tests under `src/Disks/tests/gtest_cas_*.cpp` (~97 files) plus
    `src/Disks/tests/gtest_ca_*.cpp` (3 files, `cas_test_helpers.h`,
    `cas_format_test_battery.h`) and `src/Disks/tests/gtest_content_addressed_settings.cpp`.
  - clickhouse-regression `cas/` suite — only `cas/tests/sanity.py` (one
    `replicated_merge_tree_on_content_addressed_storage` scenario + a currently-disabled orphan
    sweep scenario); `jepsen-cas-scaffold/` (Clojure `cas_register` workload).
- Non-MergeTree engine sources checked for a CAS gate:
  `src/Storages/{StorageLog.cpp,StorageStripeLog.cpp,StorageDistributed.cpp,
  registerStorages.cpp}` and `src/Interpreters/**`.

Grep sweep summary (targeted keyword × `*content_addressed*` test glob) — matches counted:

| Keyword | Files matched |
|---|---|
| `DeleteBitmap` / `UniqueKey` / `SSTIndex` | 0 |
| `Text index` / `GIN` / `USearch` / `vector_similarity` / `MATERIALIZE INDEX` | 0 |
| `TO DISK` / `TO VOLUME` / `MOVE PARTITION` (cross-disk) | 0 (only same-disk `MOVE PARTITION … TO TABLE` in `04280_content_addressed_clone_partition_works.sql`) |
| `EXCHANGE TABLES` / `RENAME TABLE` | 0 |
| `StorageLog` / `StripeLog` / `TinyLog` / `StorageSet` / `StorageJoin` / `EmbeddedRocksDB` / `KeeperMap` / `StorageDistributed` / `tmp_policy` / `SSDCache` | 0 |
| `Packed` storage-type (RESTORE) | 0 |
| `clickhouse-disks` / `DiskWeb` / cache-disk-over-CAS layering | 0 |
| `system.query_log` / `system.part_log` / `system_logs` on CAS | 0 |

Grep sweep of `isContentAddressed()` in production code:

- MergeTree-side callers: `MergeTreeData.cpp` (2), `MergeTask.cpp` (1),
  `IMergeTreeDataPart.cpp` (1), `MergeTreeDataWriter.cpp` (1 comment),
  `DataPartsExchange.cpp` (2), `DataPartStorageOnDiskBase.{h,cpp}` (4).
- Disk-side wiring: `IDisk.h`, `ReadOnlyDiskWrapper.h`,
  `DiskObjectStorage/DiskObjectStorage.{h,cpp}`, `DiskObjectStorageCache.cpp`,
  `MetadataStorages/Cache/MetadataStorageFromCacheObjectStorage.{h,cpp}`,
  `MetadataStorages/IMetadataStorage.h`, `MetadataStorages/ContentAddressed/*`.
- **No matches** in `src/Storages/StorageLog.cpp`, `StorageStripeLog.cpp`,
  `StorageDistributed.cpp`, `src/Interpreters/**` — i.e. **no fail-closed CREATE-time or
  config-time guard against pointing a non-MergeTree engine, a `tmp` disk, or an SSD-cache
  dictionary at a CAS disk exists in this PR.** (The one gate in
  `ContentAddressedMetadataStorage.cpp:347` guards a NoTrashChecker path, not table
  registration.)

## Findings still present

Each CAS-### below was cited by the original coverage-map audit as a "not audited / not tested"
finding whose defect *is* the test-coverage gap. Verdict is `🔴 still-present` when no targeted
test now exists in the current PR; the anchor points at the production code the gap concerns.

### `CAS-007` — UniqueKey / DeleteBitmap + SSTIndex on CAS untested (G1)
- Anchor: `src/Storages/MergeTree/UniqueKey/UniqueKeyIndexCache.{h,cpp}`,
  `src/Storages/MergeTree/UniqueKey/DeleteBitmapFileOps.cpp` (referenced by original audit); the
  three UniqueKey gtests (`gtest_unique_key_index_cache.cpp`,
  `gtest_unique_key_sst_probe.cpp`, `gtest_unique_key_encoding.cpp`) and the DeleteBitmap
  gtests (`UniqueKey/tests/gtest_delete_bitmap*.cpp`,
  `gtest_merge_tree_bitmap_store.cpp`) contain **zero** references to `content_addressed` /
  `isContentAddressed`.
- Trigger: `CREATE TABLE … UNIQUE KEY … SETTINGS disk = <CAS>` then `INSERT` triggering
  DeleteBitmap `replaceFile` — the CA transaction / manifest churn path is un-exercised in
  any test tier.
- Evidence quote: `04294_content_addressed_patch_parts.sh:12–13` — "non-UNIQUE-KEY custom-
  partitioned table" is required by the LWU test, i.e. the CA suite explicitly excludes the
  UniqueKey path.
- Notes: Also the delete-bitmap file is **not** listed in the CA mutable-per-part set (the
  set is `{uuid.txt, txn_version.txt, metadata_version.txt}`, see
  `ContentAddressedTransaction.cpp` `mutable_file_names`); `replaceFile` on it routes through
  whole-part republish. No test exercises this.
- Verdict: 🔴 still-present.

### `CAS-061` — Full-text (GIN/Text) & vector-similarity index build/read on CAS untested (G2)
- Anchor: `src/Storages/MergeTree/MergeTreeIndexText.*`,
  `src/Storages/MergeTree/MergeTreeIndexVectorSimilarity.*` (index families in the current
  code); zero `content_addressed` cross-references.
- Trigger: `CREATE TABLE … ADD INDEX … TYPE text|vector_similarity SETTINGS disk = <CAS>`
  followed by `MATERIALIZE INDEX` / query using the index — never covered.
- Evidence: no `*content_addressed*` test file contains `text`, `GIN`, `USearch`,
  `vector_similarity`, or `MATERIALIZE INDEX`.
- Notes: The manifest schema (`Formats/CasManifestCodec.h`) is type-agnostic (see also
  `CAS-202` info), so *storage* likely works; the un-tested surface is dedup behaviour of
  wide GIN segment files and MATERIALIZE INDEX during merge.
- Verdict: 🔴 still-present.

### `CAS-041` — Cross-disk `MOVE / REPLACE / ATTACH PARTITION … TO DISK/VOLUME` unverified (G3)
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:5904` (CA branch for `new_data_part`) and
  the byte-copy `clonePart` path referenced from `DataPartStorageOnDiskBase.cpp:735`
  (`if (dst_disk->isContentAddressed())` — same-pool relink hint; the cross-disk copy
  fallback is unchecked in any test).
- Trigger: two storage policies, one plain, one CA, `ALTER TABLE t MOVE PARTITION p TO DISK
  '<other>'` in both directions.
- Evidence: `tests/queries/0_stateless/04280_content_addressed_clone_partition_works.sql`
  covers only same-disk `MOVE PARTITION … TO TABLE`, `REPLACE PARTITION`, and
  `ATTACH PARTITION FROM` on the same CA disk. Its comment (lines 5–7) explicitly notes
  history of `SUPPORT_IS_DISABLED` rejections; the cross-disk case is not exercised. No
  integration test with two disks (one CA, one non-CA) exists.
- Verdict: 🔴 still-present.

### `CAS-055` — Non-MergeTree engines / `tmp` disks / SSD-cache / Distributed spool ungated on CAS (G4, G5, G6, G8)
- Anchor: `src/Storages/StorageLog.cpp`, `StorageStripeLog.cpp`, `StorageDistributed.cpp`,
  `src/Storages/registerStorages.cpp`, `src/Interpreters/InterpreterCreateQuery.cpp`,
  `src/Interpreters/Context.cpp` (tmp-policy resolution),
  `src/Dictionaries/SSDCacheDictionaryStorage.cpp` — **no `isContentAddressed()` guard in
  any**. `IDisk.h:477` provides the vtable slot; only MergeTree checks it.
- Trigger: `CREATE TABLE … ENGINE = Log … SETTINGS disk = <CAS>` (or `StorageDistributed`,
  `SET` / `Join`, `File`, `Memory` with disk persistence, `EmbeddedRocksDB`, `KeeperMap`,
  `Dictionary … LAYOUT(SSD_CACHE(…))`, or `<tmp_policy>` pointing at a CA disk). Runtime
  `NOT_IMPLEMENTED` / no-op / misroute at first write.
- Evidence: zero test files match `StorageLog|StorageDistributed|SSDCache|tmp_policy` +
  `content_addressed`; grep of production sources confirms the guard is absent.
- Verdict: 🔴 still-present.

### `CAS-109` — System-log-on-CAS storm; `EXCHANGE TABLES` / `clickhouse-disks` / disk-layering-over-CAS untested (G7, G9, G10, G11)
- Anchor: `src/Interpreters/SystemLog.cpp` (query_log/part_log wire-up),
  `src/Interpreters/InterpreterRenameQuery.cpp` (RENAME / EXCHANGE dispatch),
  `programs/disks/*` (`clickhouse-disks` tooling),
  `src/Disks/DiskObjectStorage/DiskObjectStorageCache.cpp` (cache-over-CAS composition).
- Trigger: `<query_log><disk>cas</disk></query_log>` in server config;
  `EXCHANGE TABLES ca_a AND ca_b`; `clickhouse-disks write-file` / `copy` against a CA disk;
  layering `<cache>` or `<web>` disk on top of a CA disk.
- Evidence: no `*content_addressed*` test file references `query_log`, `part_log`,
  `EXCHANGE`, `RENAME TABLE`, `clickhouse-disks`, or `DiskWeb`. The FS-cache-over-CAS
  composition seam exists in `DiskObjectStorageCache.cpp:22–29` and
  `MetadataStorageFromCacheObjectStorage.cpp:172` but has no dedicated stateless / integration
  test.
- Notes: `04292/04293/04295/04290_content_addressed_*` cover mutation / lightweight delete
  churn but not the *system-table* placement path; `test_cas_replicated_relink` covers
  RENAME-adjacent semantics implicitly via relink, not the atomic `EXCHANGE TABLES` primitive.
- Verdict: 🔴 still-present.

### `CAS-105` — RESTORE of Packed storage-type parts + BAK-4 round-trip on CAS untested (G12)
- Anchor: `src/Storages/MergeTree/IMergeTreeDataPart.cpp` (Packed vs Full type dispatch),
  `src/Backups/BackupsWorker.cpp` and `src/Storages/MergeTree/DataPartStorageOnDiskFull.cpp`
  (CA transaction interaction on restore).
- Trigger: `BACKUP TABLE t_packed` → `RESTORE TABLE t_packed AS t_ca` where `t_ca` sits on
  a CA disk.
- Evidence: `05005_content_addressed_backup_restore.sh` and
  `04284_content_addressed_backup_pointer_holding.sh` exist but neither exercises Packed
  storage-type parts arriving via `RESTORE` (CA parts are always Full storage;
  `DataPartStorageOnDiskBase.cpp:422` `make_temporary_hard_links && isContentAddressed()`
  branch is exercised only for the Full path).
- Verdict: 🔴 still-present.

## Findings fixed / no longer reproducible

None. The 6 CAS-### items above were all *test-coverage gaps*, and each required a NEW test to
be closed. The current PR does not ship any of those tests. (Positive coverage additions in the
PR — extensive `gtest_cas_*` unit tests, the 32-file `0_stateless/*content_addressed*` suite,
integration tests `test_content_addressed_*` / `test_cas_*` — target the *safety core* and the
data-plane paths that were already deemed covered by the original audit.)

## New findings (not in original audit)

### NEW-coverage-1 (Med) — clickhouse-regression `cas/` suite is a single-scenario smoke test only
- Severity: Med (test-gap)
- Anchor: `/Volumes/workspace/clickhouse-regression/cas/tests/{feature,sanity}.py`
- Trigger: `cas/regression.py` runs `Feature(cas.tests.sanity.feature)`, which invokes
  exactly one scenario (`replicated_merge_tree_on_content_addressed_storage`) plus a
  commented-out `published_manifests_survive_orphan_sweep` scenario. The Altinity regression
  suite therefore adds **no coverage** for anything the original coverage-map audit called
  out (UniqueKey, Text/vector indexes, cross-disk MOVE, non-MergeTree engine gating,
  EXCHANGE, system-log placement, Packed RESTORE, disk layering). All actual CAS testing
  lives in upstream `tests/queries/0_stateless/*content_addressed*` and
  `tests/integration/test_(cas|content_addressed)_*`, which — as the sweep above shows —
  also leave those gaps open.
- Notes: This is a coverage-map-scoped observation about the regression harness itself.

### NEW-coverage-2 (Med) — CAS-vs-DiskEncrypted composition (E-2/3/4, CAS-113) has no test
- Severity: Med (test-gap)
- Anchor: `src/Disks/DiskEncrypted.cpp` and CAS composition path
  (`Disks/DiskObjectStorage/DiskObjectStorage.cpp:220` `isContentAddressed()` forwards).
- Trigger: `<disk_encrypted>` wrapping a `<content_addressed>` disk.
- Evidence: `gtest_disk_encrypted.cpp` never composes with CAS; no `*content_addressed*`
  stateless / integration test wraps `disk_encrypted` around CAS. Adjacent to `CAS-113` in
  the master table but originally filed under encryption-audit scope; the coverage-map audit
  did not enumerate it explicitly, so recording as a new coverage-map finding.
- Notes: Static-only observation. Composition may be structurally fine; the point is that
  it is *unverified*.

### NEW-coverage-3 (Low) — Real-S3 / real-GCS conditional-write coverage (CAS-012 backing) still test-less
- Severity: Low (already tracked as `CAS-012`; re-raising as a coverage-map observation
  because none of the new integration tests target it)
- Anchor: `src/Disks/ObjectStorages/S3/S3ObjectStorage.cpp` conditional-op codepath;
  `test_content_addressed_s3/test.py` and `test_content_addressed_gc_s3/test.py` both run
  against MinIO, not real S3/GCS.
- Trigger: 412 / `NoSuchKey` → `PreconditionFailed` mapping on real S3 / GCS.
- Notes: Static reasoning only — no way to know from the tree whether a CI job runs against
  real S3; on the code / test-file evidence, no such test exists.

## By-design / N/A / info

- **CAS-201 / CAS-202 / CAS-203 / CAS-204 / CAS-205 / CAS-206 / CAS-207 / CAS-208 / CAS-209
  / CAS-210** — retained as info per master table; the coverage-map audit did not touch
  these and re-verification would exceed scope.
- The extensive `gtest_cas_*` battery under `src/Disks/tests/` (97 files covering envelope,
  manifest, GC state, ref state-machine, mount, format battery, protocol scenarios,
  orphan-sweep, fold-seal, ack-floor, shard incarnation, blob upload pool, etc.) does
  provide deep coverage of the *safety core* the original coverage-map audit had already
  marked "effectively fully covered" (Part A #1–20). None of it addresses the six specific
  gaps re-verified here.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-007 (G1) | High | 🔴 still-present | `src/Storages/MergeTree/UniqueKey/DeleteBitmapFileOps.cpp` + `tests/queries/0_stateless/04294_content_addressed_patch_parts.sh:12` (test explicitly excludes UNIQUE KEY) |
| CAS-061 (G2) | Med (feature-gap) | 🔴 still-present | zero `content_addressed` × `text/GIN/vector` test matches in `tests/queries/0_stateless` |
| CAS-041 (G3) | Med | 🔴 still-present | `tests/queries/0_stateless/04280_content_addressed_clone_partition_works.sql` (same-disk only); `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:735` byte-copy path untested cross-disk |
| CAS-055 (G4/G5/G6/G8) | Med (config) | 🔴 still-present | no `isContentAddressed()` gate in `src/Storages/StorageLog.cpp` / `StorageStripeLog.cpp` / `StorageDistributed.cpp` / `registerStorages.cpp` / `Interpreters/**` / `Dictionaries/SSDCacheDictionaryStorage.cpp`; no test attempts these engines on CAS |
| CAS-109 (G7/G9/G10/G11) | Low–Med (perf / test-gap) | 🔴 still-present | no `*content_addressed*` test references `system.query_log` / `part_log`, `EXCHANGE TABLES`, `clickhouse-disks`, or cache/web disk over CAS |
| CAS-105 (G12) | Med (feature-gap) | 🔴 still-present | `05005_content_addressed_backup_restore.sh` / `04284_content_addressed_backup_pointer_holding.sh` do not cover Packed storage-type parts on RESTORE |
| NEW-coverage-1 | Med | 🔴 still-present | `clickhouse-regression/cas/tests/sanity.py` — single scenario suite |
| NEW-coverage-2 | Med | 🔴 still-present | no CAS × DiskEncrypted composition test in `src/Disks/tests/` or `tests/queries/0_stateless` |
| NEW-coverage-3 | Low | 🔴 still-present | `test_content_addressed_s3/` runs against MinIO; no real-S3/GCS conditional-write test |

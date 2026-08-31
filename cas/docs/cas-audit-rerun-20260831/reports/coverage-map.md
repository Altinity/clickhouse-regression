# coverage-map -- fresh audit 2026-08-31

## Scope
- Target: `/Volumes/workspace/altinity-clickhouse/cas-pr-2159-ceee42c` @ `ceee42c51a06cb05e2c9a2d811ef7e1726825552`
- Method: code-only inventory of roles, contracts, and seams from declarations and call sites. Comments/docs were treated as claims, not evidence.
- CAS root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (`CA/`), 133 `.cpp`/`.h` files, 55,180 lines (was 129 files / 36,603 lines on the 2026-08-12 strip tree). Adjacent hooks in `src/Disks/DiskObjectStorage/**`, `src/Storages/MergeTree/DataPartsExchange.*`, `DataPartStorageOnDiskBase.cpp`, `StorageSystemContentAddressedMounts.cpp`, `programs/disks/Command*.cpp`, `docs/en/antalya/cas/**`.
- Previous Scope (2026-08-12) used as the angle only: enumerate every layer, mark dead vs live symbols, list thin/unreviewed surfaces. That tree was a comment/test strip; this tree is the merged PR #2159 head with comments, tests, and the post-triage protocol commits.
- Explicitly out of scope: protocol correctness, IDisk contract defects (idisk-contract), comment/doc drift (codeonly-line).

New files vs the 2026-08-12 map (4 files, +2 Pool +2 Gc):

| File | Lines | Why it exists |
|---|---|---|
| `Pool/CasDetachedWork.{h,cpp}` | 65 / 52 | Tracked detached-work leases + stop token; drained at shutdown (`205af29c7f2`) |
| `Gc/CasGcMetaWriter.{h,cpp}` | 87 / 223 | Bounded pool for GC per-hash freshness-meta writes; jobs own their state (`7f932d3`) |

`G_BUILD` is 10 (`Formats/CasFormat.h:62`). Backend blob bodies go through `publishBlob` (`Backend/CasBackend.h:275`); `promoteStaged` / `putIfAbsentStream` are gone.

## Code surface (by subdirectory)

### `CA/` top level — 8 files, 6,385 lines

| File | Lines | Role (from code) |
|---|---|---|
| `ContentAddressedMetadataStorage.h` | 798 | `ContentAddressedMetadataStorage final : IMetadataStorage, IContentAddressedExchange`; `CasOpClass` / `CasOpAdmission`; `Route` / `DirRoute` / `DirShape`; `PoolView` / `PoolAccessSnapshot`; GC/fsck/FORGET/GC STOP-START; `*ForTest` seams |
| `ContentAddressedMetadataStorage.cpp` | 2,374 | Read + enumeration: `exists*` / `listDirectory` / `iterateDirectory` / `getFileSize` / `getLastModified` / `getStorageObjects*`; directory classifier; `liveNamespace` / `shadowNamespace` (server-root-scoped); `openPoolView` (`EmulatedSingleProcess` for `ObjectStorageType::Local`); startup/shutdown/forgetDisk/gcStop/gcStart; exchange verbs |
| `ContentAddressedTransaction.h` | 420 | `ContentAddressedTransaction : IMetadataTransaction`; `PartStaging` / `PendingBlob`; `partFileMustStayBlob`; `fanOutBlobUploads`; `CaContentWriteBuffer` / `CaInlineWriteBuffer` |
| `ContentAddressedTransaction.cpp` | 2,002 | Eager mutations: write buffers, `createDirectory*`, `moveFile` / `moveDirectory` / `replaceFile` / `createHardLink` / `unlinkFile` / `removeRecursive`, `publishStaging` |
| `ContentAddressedExchange.h` / `.cpp` | 260 / 170 | Relink / confirm / blob-view plan; token codec |
| `ContentAddressedSettings.h` / `.cpp` | 94 / 267 | `cas_`-prefixed `LIST_OF_CONTENT_ADDRESSED_SETTINGS` (unprefixed spelling still accepted with a warning); `non_cas_keys` gone |

### `CA/Backend/` — 13 files, 4,756 lines

| File | Role (from code) |
|---|---|
| `CasBackend.h` (427) | Object-store contract: get/head/putIfAbsent/putOverwrite/casPut/deleteExact/list + **`publishBlob`** (pure). No `promoteStaged` / `putIfAbsentStream` |
| `CasObjectStorageBackend.{h,cpp}` (282 / 1,179) | Only production `Backend`: Native vs `EmulatedSingleProcess`; `publishBlob` (HEAD-then-unconditional body, native copy only for first S3-staged miss) |
| `CasInstrumentedBackend.{h,cpp}` | ProfileEvents decorator |
| `CasInMemoryBackend.{h,cpp}` | In-memory `Backend` + fault-injection. **No `src/` / `programs/` caller** |
| `CasRequestControl.{h,cpp}` (635 / 912) | Conditional-write outcome algebra for **metadata/control** objects (not blob bodies) |
| `CasProbe.{h,cpp}` / `CasSentinelProbe.{h,cpp}` | Boot capability probe; sentinel / bootstrap-residual classification |

### `CA/Formats/` — 39 files, 7,383 lines

Unchanged file set vs 2026-08-12. Registry in `CasFormat.{h,cpp}` (`G_BUILD = 10`, `changePoints` tables, `currentWriterVersion` / `currentCompatibilityVersion` / `checkCompatibility`). `Layout` is the single key-naming source. One encode/decode pair per `FormatId`. `changePoints()` is called only from gtests; writers stamp `G_BUILD`.

### `CA/Gc/` — 19 files, 9,461 lines

| File | Role (from code) |
|---|---|
| `CasGc.{h,cpp}` (978 / 4,527) | Round driver. Fold writes in-memory `(snap_generation, snap_attempt)`; **one round CAS** on `gc/state`. Sharded path calls `foldDeltasIntoGeneration`, not `ShardReducer` |
| `CasGcScheduler.{h,cpp}` | Background pacer, `GcHealth`, Start/Finish/Phase log records |
| `CasGcMetaWriter.{h,cpp}` | **New.** Typed condemn-marker / meta-delete jobs; no closure capture |
| `CasBlobInDegree.{h,cpp}` | In-degree fold / `foldDeltasIntoGeneration` |
| `CasOrphanManifestSweep.{h,cpp}` | Budgeted orphan-manifest sweep; undecodable manifests skipped (2649bce) |
| `CasGcShardPlan.{h,cpp}` | `blobShard` (live). `ShardReducer` / `manifestCleanupShard` — **gtest only** |
| `CasGcMaintenanceState.{h,cpp}` | Janitor cursor codec |
| `CasNamespaceJanitor.{h,cpp}` | Paged removed-namespace cleanup |
| `CatalogLifecycleReconciler.{h,cpp}` | Catalog vs observed-evidence reconcile |
| `CasGcPhaseTimer.h` | Header-only phase timer |

### `CA/Parts/` — 4 files, 1,719 lines

`PartPathParser` (path grammar + split cache). `CachedPartFolderAccess` / `PartFolderView` / `Freshness` / `PartFolderValidate`. Every `existsFile` / `getFileSize` / `listDirectory` / read resolves through this facade.

### `CA/Pool/` — 33 files, 20,782 lines

| Cluster | Files | Role |
|---|---|---|
| Facade | `CasPool.{h,cpp}`, `CasPoolMeta.cpp` | Open/bootstrap, mount, `beginPartWrite`, namespace files, lifecycle |
| Mount / identity | `CasMountRuntime.{h,cpp}`, `CasServerRoot.{h,cpp}` | Lease + `write_attempt_id`, epoch, fence; owner/epoch/mount objects; worker renewals admitted only over Active keeper (`ceee42c`) |
| Ref engine | `CasRefLedger.{h,cpp}`, `CasRefProtocol.{h,cpp}`, `CasRefCatalog.{h,cpp}`, `CasRefCkpt.{h,cpp}`, `CasRefCowMap.{h,cpp}`, `CasRefCowManifestSet.{h,cpp}` | Ref-log / snapshot / catalog / checkpoint |
| Part write | `CasPartWriteTxn.{h,cpp}`, `CasBlobUploadPool.{h,cpp}`, `CasBlobMeta.{h,cpp}` | HEAD → adopt or `publishBlob`; precommit/promote |
| Read | `CasManifestReader.{h,cpp}` | Manifest decode cache + `locate` (key, **offset**, length) |
| Side objects | `CasPlainObjects.{h,cpp}` | Verbatim namespace / mountpoint files |
| Async | `CasDetachedWork.{h,cpp}` **new**, `CasEventDispatcher.{h,cpp}` | Tracked detached work; `system.cas_log` sink |

### `CA/Primitives/` — 10 files, 1,476 lines

Identity/hashing vocabulary: `CasTypes`, `CasBlobDigest`, hashing write buffers, `CasXxh3Streamer`, `CasCodecUtil`, `CasNamespaceLifeId`, `CasEvent`.

### `CA/Tools/` — 6 files, 2,665 lines

`runFsck`, `caInspectToJson`, `decommissionPoolMember`. Offline entry via `programs/disks/Command*.cpp`.

### `CA/benchmarks/` — 1 file, 553 lines

`benchmark_cas_ref_protocol.cpp`, `ENABLE_BENCHMARKS` default OFF.

## Subsystems and entry points

Layering (include direction): `Primitives → Formats → Backend → Pool → Gc → Tools ≈ Parts → facade`.

| Trigger | Entry point |
|---|---|
| Disk config | `registerContentAddressedMetadataStorage` → `ContentAddressedSettings::loadFromConfig` → ctor |
| Server start/stop | `startup`/`shutdown`; `Cas::initializeBlobUploadPool` / `shutdownBlobUploadPool`; detached-work drain |
| Part-file read | `DiskObjectStorage::prepareRead` → `prepareInManifestRead` / `getBlobViewPlan` (offset applied here, not in `getStorageObjects`) |
| Part-file write | `transactionIsStagingOverlay()` → eager `ContentAddressedTransaction::*` → `PartWriteTxn` |
| Replica fetch | `DataPartsExchange` relink (`getRelinkOffer` / `prepareAdoptFromManifest` / promote) |
| FREEZE / clone into CAS | `DataPartStorageOnDiskBase::freezeRemote` / `clonePart` content-addressed branch → one disk transaction + `copyDirectoryContentIntoTransaction` (`84b30f6`) |
| Background GC | `CasGcScheduler` → `Gc::runRegularRound` → `GcMetaWriter` |
| `SYSTEM CAS *` | `InterpreterSystemQuery` via `tryFromDisk` |
| `clickhouse-disks` | cas-fsck / cas-gc-dryrun / cas-gc-rebuild / cas-inspect / cas-drop-member |
| Observability | `system.cas_log`, `system.cas_gc_log`, `system.cas_mounts` |

## External integration seams (checked live)

- `IDisk::isContentAddressed`, `IMetadataStorage::{isContentAddressed,transactionIsStagingOverlay,supportsAtomicFileWrites}`, `IDataPartStorage::isContentAddressed`
- `DiskObjectStorage::{supportsHardLinks,prepareRead,copyFile,isContentAddressed,supportsAtomicFileWrites}`; cache wrapper skipped for CAS (`DiskObjectStorageCache.cpp`)
- `DiskObjectStorageTransaction::dispatch` eager when staging-overlay; `commit`/`tryCommit` assert empty queue; `undo` still only walks `written_blobs` (CAS never fills it)
- MergeTree: `DataPartStorageOnDiskBase::{freezeRemote,clonePart,Backup hardlink refuse}`, `MergeTreeData` empty-part / restore commits, `MergeTask` / `IMergeTreeDataPart` projection transaction reuse, `DataPartsExchange` relink
- Interpreters: `SYSTEM CAS *`, `ContentAddressedLog` / `ContentAddressedGarbageCollectionLog`, `ServerAsynchronousMetrics`, `AccessType` `SYSTEM_CAS_*`, `cas_blob_upload_pool_size`

Notably still absent: no `src/Backups/**` CAS branch (backup-via-temp-hardlinks refused); no `src/Storages/ObjectStorage/**` CAS branch.

## Findings

### coverage-map-1 -- production GC fold does not use `ShardReducer` / `manifestCleanupShard` (Medium)
- Anchor: `Gc/CasGc.cpp:3035-3071`; `Gc/CasGcShardPlan.h:58-86` / `.cpp:17-43`; callers only in `src/Disks/tests/gtest_cas_gc_shard_plan.cpp` at ceee42c
- Trigger: an auditor treating `ShardReducer` as the sharded fold, or a later change that updates only `ShardReducer` and assumes the round inherits it
- Evidence: `Gc::fold`'s `gc_shards > 1` arm buckets with `blobShard` and calls `foldDeltasIntoGeneration`. No production call of `ShardReducer::reduce` or `manifestCleanupShard`. The symbols are compiled into the server and covered by gtest only.
- Notes: Same dead-symbol shape as 2026-08-12 coverage-map-1; tests are back, so this is no longer "dead because tests were stripped". The fold comment that still names `ShardReducer` is codeonly-line-5.

### coverage-map-2 -- four post-2026-08-12 surfaces have no dedicated sibling angle (Medium)
- Anchor: `Pool/CasDetachedWork.{h,cpp}`; `Gc/CasGcMetaWriter.{h,cpp}`; `Backend/CasBackend.h:275` `publishBlob` + `CasObjectStorageBackend.cpp:862`; `Pool/CasMountRuntime` `write_attempt_id` / `ceee42c` Active-only renewals; pool format generation 10 (`Formats/CasFormat.h:62`)
- Trigger: the rest of this re-run scoping only the 2026-08-12 file list
- Evidence: These are the product commits the brief says must be treated as current (`205af29c`, `7f932d3`, `940b168`, `ceee42c`, generation bump to 10). None of the 39 audit names is "detached-work drain", "GC meta-writer ownership", or "`publishBlob` transport". write-protocol / gc-protocol / concurrency / crash-consistency must explicitly take them; they are not covered by "read the old Scope".
- Notes: Inventory, not a defect in the new code.

### coverage-map-3 -- `InMemoryBackend` still has no production caller (Low)
- Anchor: `Backend/CasInMemoryBackend.{h,cpp}`; repo-wide `src/` + `programs/` search at ceee42c
- Trigger: treating in-memory conditional-write behaviour as the production dialect
- Evidence: Only gtests construct it. Production `Pool::open` wraps `ObjectStorageBackend` in `InstrumentedBackend`. Same as 2026-08-12; tests being present does not make it a production backend.
- Notes: Filimonov: `EmulatedSingleProcess` is tests / local development. `InMemoryBackend` is even narrower (unit tests only).

### coverage-map-4 -- `changePoints()` is still unreachable from writers (Low)
- Anchor: `Formats/CasFormat.cpp:72-114`; gtest-only callers; writers stamp `G_BUILD` via `currentCompatibilityVersion()`
- Trigger: citing the per-format table as the rolling-upgrade window
- Evidence: `currentWriterVersion` / `changePoints` have no `src/` / `programs/` caller. `CasFormat.h:138-144` now documents the always-`G_BUILD` stamp. upgrade-compat owns the compatibility window; this map only records that the table is not on the write path.

### coverage-map-5 -- thin / unreviewed surfaces that no named audit owns by default (Low)
- Anchor: listed symbols at ceee42c
- Trigger: a consolidation pass that assumes every CA file is covered by one of the 39 names
- Evidence: surfaces that remain thin even after assigning the 39 audits:
  1. `Formats/CasByteBudget.h` admission-sizing chain (not bc1, not ad5).
  2. `Parts/PartPathParser` split cache growth / invalidation.
  3. `Mode::EmulatedSingleProcess` auto-selected for `ObjectStorageType::Local` (`ContentAddressedMetadataStorage.cpp` `openPoolView`) — most local CI is this dialect, not Native S3/GCS.
  4. Read-only / `CasOpAdmission::TruthAbsent` matrix (`checkOpAdmitted`).
  5. `forgetDisk` / `gcStop` / `gcStart` / `startup` `TSA_NO_THREAD_SAFETY_ANALYSIS`.
  6. `*ForTest` seams compiled into production classes (promote-failure, empty-proof probe, GC-admit window, detached-work, ledger carve hooks).
  7. `benchmarks/benchmark_cas_ref_protocol.cpp` (default-off).
  8. ProfileEvents increment completeness on `Unresolved` / fail-closed branches (`CasInstrumentedBackend`).
  9. Generic `getStorageObjects` consumers that bypass `prepareRead` (`DiskObjectStorage::{copyFile,getBlobPath,getUniqueId}`, `DataPartStorageOnDiskFull::getRemotePaths`) — owned by idisk-contract if that audit runs; otherwise uncovered.
  10. Encrypted-over-CAS and `DataPartsExchange` relink after the 940b168 publish change.

## By-design / info / non-actionable
- Tests and docs are present. "No gtest caller" is no longer an artifact of the 2026-08-12 strip.
- `Layout::casRefsPrefix()` aliasing `namespaceStreamRootPrefix()` is a naming redundancy, both used.
- `transactionIsStagingOverlay() == true` and `supportsAtomicFileWrites() == true` are intentional flags; contract gaps belong to idisk-contract.
- `getHardlinkCount() == 0` while `supportsHardLinks()` is true is a known interface shape (idisk-contract), not a missing file.
- Layering exception: `CasFsck` reaches into Pool + Gc helpers. Documented in `CA/README.md`.

## Closed-since-2026-08-12
- Working-tree strip consequences (deleted gtests/docs/READMEs; every `*ForTest` looking dead) — tests, `docs/en/antalya/cas/**`, and both READMEs are in this tree.
- `promoteStaged` / `resurrect` as production Backend verbs — replaced by `publishBlob` (`940b168`). Do not look for those symbols.
- `non_cas_keys` skip-list — gone (`917600b`).
- File-count baseline 129 / 36,603 — stale. Use 133 / 55,180.

## Coverage
- Reviewed: all 133 CA `.cpp`/`.h` files classified by subdirectory and role; new-vs-2026-08-12 file diff; Backend verb set; live vs gtest-only symbols (`ShardReducer`, `manifestCleanupShard`, `InMemoryBackend`, `changePoints`); external seams in Disks / MergeTree / Interpreters / programs/disks; `tryFromDisk` call sites.
- N/A: dynamic coverage measurement; template-only callers.
- Deferred: per-`*ForTest` seam audit; ProfileEvents increment matrix; encrypted-over-CAS; whether every `CAS*` ProfileEvent still has an increment (previous map claimed 156; recount not repeated).

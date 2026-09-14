# coverage-map -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base commit `842f2b37b8f`
("Merge branch 'antalya-26.6' into feature/antalya-26.6/CAS"), audited as a **working tree**, read-only.

CAS code root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
(referred to below as `CA/`).

Method: code-only. Every role, contract, and seam below is derived from declarations, control flow, and
error/branch classification in `.cpp`/`.h`. No `docs/**`, no `README.md`, no comment text was used as
evidence of intent. Where a contract could only be inferred from a comment, it is reported as unknown
rather than asserted.

**Working-tree shape matters for every other audit and is stated here once.** `git status` on this branch
reports 280 deletions, of which 277 are CAS test/doc artifacts:

- `src/Disks/tests/gtest_cas_*.cpp`, `gtest_ca_*.cpp`, plus the shared fixtures
  `src/Disks/tests/cas_test_helpers.h`, `cas_format_test_battery.h`, `cas_sweep_test_support.h` — all deleted.
- `docs/en/antalya/cas/**`, `docs/en/operations/system-tables/cas_*.md` — all deleted.
- `CA/README.md` and `CA/Formats/README.md` — deleted.

Consequences that the other 38 audits must carry:

1. Any symbol whose only caller was a gtest now looks like dead code. This report distinguishes
   *"no caller at all"* from *"no caller because the test that called it was stripped"*.
2. `test-coverage-fuzzing` cannot measure coverage on this tree; it can only inventory the 264 `*ForTest`
   seams that remain compiled into production classes (see coverage-map-3).
3. Comment-derived rationale (e.g. the B90 use-after-free note removed from `src/Common/ThreadStatus.h`)
   is gone, so exception/lifetime audits (`bc3-exception-safety`, `bc7-blocking-io-locks`) must re-derive
   those constraints from code.

Size of the surface: **129 `.cpp`/`.h` files, 36,603 lines** (plus `benchmarks/CMakeLists.txt`).

| Subdirectory | Files | Lines |
| --- | --- | --- |
| `CA/` (top level) | 8 | 4,010 |
| `CA/Backend/` | 13 | 3,207 |
| `CA/Formats/` | 39 | 5,677 |
| `CA/Gc/` | 17 | 6,352 |
| `CA/Parts/` | 4 | 1,179 |
| `CA/Pool/` | 31 | 12,604 |
| `CA/Primitives/` | 10 | 1,123 |
| `CA/Tools/` | 6 | 2,082 |
| `CA/benchmarks/` | 1 | 369 |
| **Total** | **129** | **36,603** |

## Code surface (by subdirectory)

### `CA/` top level — 8 files, 4,010 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `ContentAddressedMetadataStorage.h` | 346 | Declares `ContentAddressedMetadataStorage final : IMetadataStorage, IContentAddressedExchange`; `CasOpClass`/`CasOpAdmission` admission enums; `Route`/`DirRoute`/`DirShape` path classification types; `PoolView`/`PoolAccessSnapshot`; the GC/fsck/decommission admin verbs; 10 `*ForTest` hooks. |
| `ContentAddressedMetadataStorage.cpp` | 1,638 | Read-side + enumeration implementation: `existsFile/existsDirectory/listDirectory/iterateDirectory/getFileSize/getLastModified/getStorageObjects`, `classifyDirectory`, namespace routing (`liveNamespace`, `shadowNamespace`, `route`), `openPoolView` (chooses `ObjectStorageBackend::Mode::EmulatedSingleProcess` for `ObjectStorageType::Local`, else `Native`), `startup/shutdown/forgetDisk/gcStop/gcStart`, GC/fsck/rebuild verb entry points, `getRelinkOffer` / `prepareAdoptFromManifest`. |
| `ContentAddressedTransaction.h` | 207 | Declares `ContentAddressedTransaction : IMetadataTransaction` with `PartStaging`/`PendingBlob` staging model; free function `partFileMustStayBlob`; `fanOutBlobUploads` + `BlobUploadFanoutHooksForTest`; `CaContentWriteBuffer` and `CaInlineWriteBuffer` (`WriteBufferFromFileBase` subclasses). |
| `ContentAddressedTransaction.cpp` | 1,360 | Eager (non-deferred) mutation implementation: `writeFile`/`tryCreateWriteBuffer`, blob staging + upload fan-out, `createDirectory*`, `moveFile/moveDirectory/replaceFile/createHardLink/unlinkFile/removeRecursive/truncateFile`, `publishStaging`, `cleanupPendingTempFiles`, plus namespace-file and mountpoint-object writes. |
| `ContentAddressedExchange.h` | 95 | Cross-node exchange interface: `CasConfirmAnswer`, `CasRelinkSourceToken`, `CaRelinkPrepare`, `CaRelinkPromote`, `ICaPreparedRelink`, `IContentAddressedExchange` (`getPoolUUID`, `ownsNamespace`, `confirmExactRef`, `getRelinkOffer`, `prepareAdoptFromManifest`, `prepareInManifestRead`, `getBlobViewPlan`, `RelinkOffer`, `BlobViewPlan`). |
| `ContentAddressedExchange.cpp` | 154 | Only the relink-token wire codec: `encodeCasRelinkSourceToken` / `decodeCasRelinkSourceToken` with strict percent-encoding, 6 mandatory non-empty fields, 256-byte field cap, 1024-byte token cap, control-byte rejection, `"car1"` version tag. |
| `ContentAddressedSettings.h` | 56 | `ContentAddressedSettings` struct + `MacroExpander` typedef + settings traits declaration. |
| `ContentAddressedSettings.cpp` | 154 | The 29-entry `LIST_OF_CONTENT_ADDRESSED_SETTINGS` macro (scratch path, `gc_*` budgets, `blob_hash`, `gc_shards`, `server_root_id`, part-folder cache + validation policy, `staging_backend`, …), the `non_cas_keys` allow-list used to reject unknown disk keys, and macro expansion / validation. |

### `CA/Backend/` — 13 files, 3,207 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `CasBackend.h` | 240 | The object-store abstraction: `Range`, `GetResult`, `GetStreamResult`, `HeadResult`, `PutOutcome`, `CasOutcome`, `WriteResultT`, `DeleteOutcome`, `ListedKey`, `ListPage`, `ProbeOutcome`, `SentinelProbeResult`, `WriteSink`, and `class Backend` (pure: `get/getStream/head/putIfAbsent/putIfAbsentStream/putOverwrite/casPut/deleteExact/list/supportsListTokens`; defaulted: `checkPoolPreconditions`, `checkConditionalWriteSingleAttemptSupport`, `probeSentinelRaw`; `promoteStaged`/`resurrect` default to `NOT_IMPLEMENTED`). Plus `forEachListedKey`, `DeleteClass`, `classifyDeleteOutcome`, `deleteClassName`. |
| `CasObjectStorageBackend.h` | 119 | `ObjectStorageBackend final : Backend` with `Mode { Native, EmulatedSingleProcess }`, `native_token_type`, `EmuTokenExpiry`, `mintingTypeMatches`, conditional single-PUT cap; declares `casSizedReadSettings` and `detail::finalizeConditionalWrite`. |
| `CasObjectStorageBackend.cpp` | 933 | The only production `Backend`: S3/GCS conditional writes (`If-None-Match`/generation tokens), `promoteStaged` (Native-only server-side copy), `resurrect`, listing with tokens, and a full in-process emulation path (`emuPath`, token expiry) for `Mode::EmulatedSingleProcess`. |
| `CasInstrumentedBackend.h` | 137 | `InstrumentedBackend final : Backend` decorator; `CasNs`/`CasOp` classification enums, `classifyCasNs`, `incrementCasEvent`; forwards every `Backend` method to `inner` while counting ProfileEvents. |
| `CasInstrumentedBackend.cpp` | 163 | Key→namespace classification and the ProfileEvents increment table. |
| `CasInMemoryBackend.h` | 94 | `InMemoryBackend : Backend` with `Object`/`PendingDelete` maps; `supportsListTokens() == true`; overrides `promoteStaged`/`resurrect`. |
| `CasInMemoryBackend.cpp` | 393 | Full in-memory `Backend` implementation. **No caller in `src/` or `programs/`** (see coverage-map-2). |
| `CasRequestControl.h` | 178 | Conditional-write outcome algebra: `CasWriteOutcome`, `CasUnresolvedReason`, `unresolvedProvesNothingWasSent`, `describeUnresolvedReason`, `classifyConditionalWriteResult`, `CasRequestBudget` + `validateCasRequestBudget`, `makeCasWriteRetryLaterExceptionPtr`, `CasCreateOutcome/Result`, `CasOverwriteOutcome/Result`, `SlotOccupyResult`, `CasRequestController`. |
| `CasRequestControl.cpp` | 565 | Exception→outcome classification, retry/backoff budget enforcement, and the create/overwrite/occupy state machines built on top of `Backend`. |
| `CasProbe.h` | 13 | Declares `runCapabilityProbe(Backend&, prefix)` and `probeConditionalCopy(IObjectStorage&, prefix)`. |
| `CasProbe.cpp` | 260 | Boot-time capability probe: calls `checkPoolPreconditions`, `checkConditionalWriteSingleAttemptSupport`, then exercises put-if-absent / CAS / delete-exact / list against a scratch prefix. |
| `CasSentinelProbe.h` | 21 | `probeSentinel(Backend&, key)`; `BootstrapResidual` enum; `probePoolBootstrapResidual(Backend&, Layout&)`. |
| `CasSentinelProbe.cpp` | 91 | Distinguishes absent / present / indeterminate sentinel reads and classifies partial pool bootstrap residue. |

### `CA/Formats/` — 39 files, 5,677 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `CasFormat.h` | 82 | `FormatId` enum (all persisted object kinds), `currentWriterVersion`, `currentCompatibilityVersion`, `checkCompatibility`, `FormatChangePoint` + `changePoints`, `TextFamily`, `KeyStrictness`, `CompressionPolicy`, `FormatTraits`, `traitsFor`, `traitsForType`, `storedSuffix`. |
| `CasFormat.cpp` | 143 | The per-format traits table and the change-point tables (`BASELINE`, `REF_STREAM`, `REF_CKPT`, `REF_CATALOG`, `GC_MAINTENANCE_STATE`, `POOL_META`). |
| `CasTextFormat.h` | 175 | `CasJsonWriter` (hand-rolled JSON emitter), `JsonObjectReader`, `TextHeader`, `expectHeaderLine`, `sniffHeaderLine`, `readLine`, `findNextSpecialJsonByte`, `looksZstd`, `sealObject`, `openObject`. |
| `CasTextFormat.cpp` | 403 | Header/trailer framing, line-cap enforcement, zstd seal/open, JSON scanning primitives shared by every text format. |
| `CasWireVocab.h` / `.cpp` | 32 / 99 | Shared field vocabulary: token type / blob-hash-algo / object-kind word codecs, `writeTokenFields`, `writeBlobRefFields`, `writeManifestRefFields`, `manifestRefFromFields`. |
| `CasRefWireVocab.h` / `.cpp` | 35 / 47 | Ref-specific vocabulary: `RefOwnerKind`, `RefOwnerBinding`, `refOwnerKindToWord/FromWord`, `writeRefTxnIdFields`, `checkRefTxnIdNonzero`. |
| `CasByteBudget.h` | 28 | Overflow-safe budget arithmetic: `addByteBudget`, `mulByteBudget`, `fitsLineCap`, `fitsObjectCap`. |
| `CasLayout.h` | 273 | `class Layout` — the single source of key naming: `blobKey`, `blobMetaKey`, `parseBlobKey`, namespace stream/state prefixes, `refLogKey`, `refSnapshotKey`, `refCkptKey`, `manifestKey`, `namespaceFileKey`, `mountpointObjectKey`, `gcStateKey`, `gcMaintenanceStateKey`, `gcHbKey`, `gcGenPrefix`, `gcGenAttemptPrefix`, `foldSealKey`, `blobTargetRunKey`, `outcomesKey`, `serverRootPrefix`, `ownerKey`, `epochKey`, `mountKey`, `poolMetaKey`, plus parsers (`ParsedRefObjectKey`, `ParsedNamespaceFileKey`, `ParsedBlobTargetRunKey`) and `isCleanRelativeNamespaceFileName`. |
| `CasLayout.cpp` | 321 | Key parsers and namespace validation for the above. |
| `CasBlobEnvelopeFormat.h` / `.cpp` | 66 / 234 | Blob object envelope: `ObjectKind`, `ProvenanceOp`, `Provenance`, `EnvelopeHeader`, `encodeEnvelopeHeader`, `decodeEnvelopeHeader` (kind-checked, size-checked), `payloadOffset`. This is the header prefix that makes a blob object self-describing. |
| `CasBlobMetaFormat.h` / `.cpp` | 28 / 87 | Per-blob freshness meta record: `MetaState`, `BlobMeta`, `encodeBlobMeta`/`decodeBlobMeta`. |
| `CasPartManifestFormat.h` / `.cpp` | 56 / 313 | Part manifest: `EntryPlacement`, `ManifestEntry`, `PartManifest`, `encodePartManifest`/`decodePartManifest`, `computePayloadDigest`, `refMatchesBody`, `manifestNamespaceMatches`, `findEntry`, `entryRange`. |
| `CasPoolMetaFormat.h` / `.cpp` | 47 / 160 | Pool identity object: `PoolMeta`, `encodePoolMeta`/`decodePoolMeta`, `validatePoolBlobHeaderLen`, `validatePoolAlgosUsed`. |
| `CasRefLogFormat.h` / `.cpp` | 71 / 399 | Ref-log transaction: `RefOpKind`, `RefOp`, `RefLogTxn`, encode/decode (decode is bound to an expected namespace **and** txn id), sizing helpers, `refLogTxnIsRemovalClass`, `refLogTxnIsEpochSeal`, `validateEpochSealGrammarStructural/Contextual`. |
| `CasRefSnapshotFormat.h` / `.cpp` | 53 / 286 | Ref-table snapshot: `RefLifecycle`, `RefCommittedRow`, `RefTableSnapshot`, encode/decode, row/framing sizing. |
| `CasRefCkptFormat.h` / `.cpp` | 28 / 146 | Ref checkpoint object: `RefCkpt`, encode/decode, `checkRefCkptInvariants`. |
| `CasRefCatalogFormat.h` / `.cpp` | 76 / 360 | Namespace lifecycle catalog: `NsState`, `CreatorFence`, `CatalogEntry`, `RefCatalog`, encode/decode, `checkCatalogObjectBytes`, fold-seal reservation sizing (`foldSealFixedBytes`, `worstCaseEntryFoldReservationBytes`, `widestBlobTargetRunReservationBytes`, `widestCondemnedSummaryReservationBytes`, `checkFoldSealReservation`), `checkCatalogAdmission`. |
| `CasFoldSealFormat.h` / `.cpp` | 114 / 490 | GC fold seal: `RunRef`, `HoldReason`, `RefHold`, `RefCoverage`, `RefCleanupEvidence`, `RefLifeFoldState`, `CondemnedSummary`, `CasFoldSeal`, `FoldSealCaps`, encode/decode (generation-pinned), `validateFoldSealForWrite`. |
| `CasGcStateFormat.h` / `.cpp` | 42 / 116 | GC lease/state and heartbeat objects: `GcLease`, `GcState`, `GcHeartbeat` + codecs. |
| `CasGcMaintenanceStateFormat.h` / `.cpp` | 20 / 67 | `GcMaintenanceState` codec (janitor cursor / suppression state). |
| `CasGcOutcomesFormat.h` / `.cpp` | 38 / 126 | GC audit log: `OutcomeKind`, `OutcomeEntry`, `OutcomeLog` + codec. |
| `CasRecordStreamFormat.h` / `.cpp` | 80 / 312 | Append-only record run format: `SourceEdgeRecord`, run header line write/expect, `SourceEdgeRunWriter`, `sourceEdgeRunChecksum`, `SourceEdgeRunReader` (checksum-verifying). |
| `CasServerRootFormats.h` / `.cpp` | 49 / 175 | Server-root control objects: `OwnerObject`, `ServerEpoch`, `MountLease` + codecs. |

### `CA/Gc/` — 17 files, 6,352 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `CasGc.h` | 472 | `class Gc` (round driver: `runRegularRound`, `previewDeletes`, `rebuildBaseline`, `pulseHeartbeat`, phase sink), `UniversePolicy`, `RoundAnomaly`, `RebuildReport`, `RoundReport`, `GcPhaseRecord`/`GcPhaseSink`, `RefScanSummary`, `RoundInput`, `RefPlan`, `buildRefWalkPlan`, `RefWalkPlanRow`, `stuckRemovalWarning`, `TxnApplyLedger`, `retiredLogicalSize`, `shouldDeferRound`, plus `FoldResult` with an explicit `FrontierUnproven`/`FrontierDeficit` accounting model. |
| `CasGc.cpp` | 3,236 | The GC round: lease acquire/renew/steal, hot scan, ref-walk plan, fold seal write, condemn→graduate→delete pipeline, `drainCompletedRemoving`, `runNamespaceJanitorPage`, `reportStuckRemovals`, orphan sweep integration, generation prune, rebuild baseline. Largest single file in the feature. |
| `CasGcScheduler.h` / `.cpp` | 127 / 339 | Background scheduler: `GcRoundLogRecord` (Start/Finish/Phase × Success/NotALeader/Failed/Deferred × Scheduled/Manual), `GcRoundLogger`, `CasGcScheduler` with `GcHealth`; owns the thread, interval, stop/start, and manual-round request path. |
| `CasBlobInDegree.h` | 193 | Blob in-degree accounting: `RetiredEntry`, `SourceEdgeKeyCodec`, `sourceEdgeId`, `assertValidSourceEdgeId`, `CondemnedRow` codec, `SourceEdgeRunView` (+ `openSourceEdgeRun` from bytes or backend), `putDeterministicArtifact`, `BlobDelta` (size-asserted), `BlobSourceRetirement`, `BlobCandidate`, `ReplacedEntry`, `UnmatchedRemoveExample`, `RetiredMergeResult`, `GcRoundWorkBudget`, `foldDeltasIntoGeneration`, `zeroInDegree`. |
| `CasBlobInDegree.cpp` | 578 | Delta folding into a generation, run merge, and zero-in-degree candidate derivation. |
| `CasOrphanManifestSweep.h` | 91 | `BuildPrefix`, `ManifestKey`, `SweepRetainClass`, `NamespaceFoldView`, `manifestDeletionPremise`, `namespaceFoldView`, `ManifestSweepResult` + `Nomination`, `sweepNamespace`, `prefixEligible`, `planManifestCursorPage`. |
| `CasOrphanManifestSweep.cpp` | 731 | Budgeted orphan-manifest sweep with an explicit retain-class decision per manifest key. |
| `CasGcShardPlan.h` / `.cpp` | 52 / 60 | `blobShard` (used), `manifestCleanupShard` (**no caller**), `class ShardReducer` (**no caller**) — see coverage-map-1. |
| `CasGcMaintenanceState.h` / `.cpp` | 29 / 40 | `readGcMaintenanceState` (Absent/Valid/Corrupt) and `casGcMaintenanceState` (Committed/Conflict); consumed only by `CasNamespaceJanitor.cpp`. |
| `CasNamespaceJanitor.h` / `.cpp` | 33 / 134 | `NamespaceJanitor` + `NamespaceJanitorResult`: paged cleanup of removed-namespace residue, driven from `CasGc.cpp`. |
| `CatalogLifecycleReconciler.h` / `.cpp` | 58 / 121 | `AuthorityStatus`, `CatalogResolution`, `CatalogLifecycleReconcileResult`, `CatalogLifecycleReconciler`: reconciles catalog lifecycle rows against observed evidence; driven from `CasGc.cpp` (`drainCompletedRemoving`). |
| `CasGcPhaseTimer.h` | 58 | `GcPhaseTimer` — header-only phase duration accumulation feeding `GcPhaseSink`. |

### `CA/Parts/` — 4 files, 1,179 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `PartPathParser.h` | 60 | `PartFilePath`, `parsePartFilePath`, `parseTableUuid`, `isAtomicShardDir`, `endsWithTableUuidPair`, `isPartFilePath`, `TableFilePath`, `parseTableFilePath`, `isShadowPath`, `mirroredArchiveNamespace`, plus split-cache test accessors. |
| `PartPathParser.cpp` | 302 | Path grammar for `<uuid-prefix>/<uuid>/<part>/<file>` and shadow/detached/moving variants, with a memoized split cache. |
| `PartFolderAccess.h` | 205 | `PartRefKey`, `CommitOutcome`, `Freshness`, `PartFolderView` (the per-part manifest view used by all read paths), `PartFolderValidate` (`Always`/`Age`/`Never`), `PreparedPartWrite`, `CachedPartFolderAccess` with `CacheParams`, `LastDecision`, `ExplainResult`, and a weighted `CacheBase` view cache. |
| `PartFolderAccess.cpp` | 612 | View construction, freshness re-proof policy, cache admission/eviction, prepared-write/commit sequencing. |

### `CA/Pool/` — 31 files, 12,604 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `CasPool.h` | 484 | `PoolConfig`, `PartWriteInfo`, `UnattributableNamespaceKey`, `NamespaceListing`, and `class Pool` — the runtime facade: `open`/`openForDecommission`, epoch/watermark, `mayMutate`, mount fence (`armMountFence`, `checkFenceOrThrow`, `tripMountLost`), lifecycle (`PoolLifecycle`, `forgetDisk`), `beginPartWrite`, `resolveRef`/`confirmExactRef`/`readManifest`/`locate`/`listRefs`/`listNamespaces`, `dropRef`/`dropNamespace`, `appendRefOps`, `tryPublishSnapshotAndAdvanceCheckpointOnce`, namespace files, mountpoint objects, staging conditional writes, dedup cache, event sink, `WriterCleanupDuty/Queue`. Also holds 66 `*ForTest` members. |
| `CasPool.cpp` | 1,350 | Pool open/bootstrap (probe, pool-meta create-or-validate, mount claim, remount), the composition root that wires `InstrumentedBackend` over `ObjectStorageBackend`, `CasRefLedger`, `CasMountRuntime`, `CasPlainObjects`, `CasManifestReader`, dedup cache, and the writer-cleanup queue. |
| `CasPoolMeta.cpp` | 129 | `PoolMeta::createOrValidate` plus `mintPoolId`, `isAlgoAdmittedIn`, `joinAlgoNames`, `admitOrValidate` — the hash-algo admission gate for an existing pool (header lives in `Formats/CasPoolMetaFormat.h`). |
| `CasMountRuntime.h` | 189 | `PoolLifecycle`, `MountConfig`, `MountFence`, `class CasMountRuntime`: single-writer mount lease, epoch, fence generation, renew loop, remount scheduling, lifecycle terminal states. |
| `CasMountRuntime.cpp` | 430 | Lease renew/expiry/fence-trip implementation and lifecycle transitions. |
| `CasServerRoot.h` | 314 | `SingleWriterSlot` + `RenewPayload`, `validateServerRootId`, `serverRootSubtreeEmpty`, `readOwnerUuid`, `claimOwnerOrThrow`, `EpochMintPolicy`, `allocateWriterEpoch`, `MountPriorState`, `MountClaimResult`, `MountFencedException`, `claimMount`, `claimMountAwaitingExpiry`, `mountDoubleStartMessage`, `mountObservationThresholdMs`, `MountTokenObservation`, `HeartbeatFloor`/`computeHeartbeatFloor`, `NonTerminalMountSlot`/`probeNonTerminalMountSlots`, `MountInfo`/`listMounts`. |
| `CasServerRoot.cpp` | 1,170 | Owner claim, writer-epoch minting, mount lease claim/expiry-observation, heartbeat floor computation, mount enumeration (backs `system.cas_mounts`). |
| `CasRefLedger.h` | 544 | `class CasRefLedger` — the persistent ref engine: `ResolveAudit`, `RefLaneState`, `ConfirmAnswer`, `RefAppendAttempt`, `PreparedRefChunk`, `RefMutationItem`, `RefTableRuntime`, `RefNameSlot`, `WedgeResolution`/`WedgeResolutionResult`, `CarvePhaseForTest`; 45 `*ForTest` seams. |
| `CasRefLedger.cpp` | 3,607 | Ref-log append with conditional writes, precommit/commit lanes, snapshot publication, checkpoint advance, recovery replay, wedge detection/resolution, staging conditional-write helpers. Second-largest file. |
| `CasRefProtocol.h` | 327 | Pure (I/O-free) ref state machine: `CatalogLifeIndex`, `RootMutationOrigin`, `MutationScope`, `RootMutationKind`, `Resolved`, `RefPublishedAtUpdate`, `DropNamespaceStats`, `RefLedgerConfig`, `nextRefTxnId`, `RefTableState`, `stateFromSnapshot`, `applyRefLogTxn`, `snapshotOf`, `replay`, `RecoveryResult`, `RefReplayBuilder`, replay-memory accounting, `admits` (budget admission), `RefManifestEdge`/`manifestEdgesOfTxn`, `removalTxnId`, `RefTableListing`. |
| `CasRefProtocol.cpp` | 868 | The transition function and budget admission logic for the above. |
| `CasRefCatalog.h` | 139 | `class CasRefCatalog` with `Snapshot`, `BeginRemovingOutcome`, `CompletedRemovingDeleteOutcome`/`Result`, `LeaderFenceStatus`, `StalledCreatingCancelOutcome`, `NamespaceCreationOutcome`, `ReconcileCreatorOutcome` — the namespace lifecycle CAS protocol. |
| `CasRefCatalog.cpp` | 552 | Catalog read/CAS with creator fences, removing/creating drain, checkpoint publication on transitions. |
| `CasRefCkpt.h` / `.cpp` | 64 / 254 | `RecoveryGrounding`/`chooseRecoveryGrounding`, `mergeCkpt`, `publishCkpt`/`CkptPublishOutcome`/`CkptDeadline`, `readCkpt`/`CkptSample`, `MissingBaseVerdict`/`classifyMissingSampledBase`, `snapshotDeletableUnderCkpt` — the safety predicate GC uses before deleting a ref object. |
| `CasRefCowMap.h` / `.cpp` | 104 / 221 | Copy-on-write `std::map<String, RefCommittedRow>` with an overlay of `optional` (tombstone-capable) and a custom `const_iterator`/`ArrowProxy`; used by `RefTableState`. |
| `CasRefCowManifestSet.h` / `.cpp` | 49 / 103 | Copy-on-write `unordered_set<ManifestRef>` used by `RefTableState`. |
| `CasPartWriteTxn.h` | 150 | `BlobSource`, `PutBlobResult`, `BlobDepRecord`, `BlobUploadOutcome`, `BlobUploadRequest`/`Result`, `poolContentHash`, `class PartWriteTxn` with explicit `PrecommitState { NotAttempted, Uncertain, Durable, Settled }` and `CommitState { NotAttempted, Uncertain, Durable }`. |
| `CasPartWriteTxn.cpp` | 902 | Blob put (dedup HEAD-first, `promoteStaged`, `resurrect`), dependency recording, manifest build, precommit/commit against the ref ledger. |
| `CasManifestReader.h` / `.cpp` | 68 / 153 | `BlobLocation`, `CasManifestReader` with a weighted `ManifestDecodeCache` keyed by `ManifestCacheKey`; the read-path manifest decode cache. |
| `CasBlobMeta.h` / `.cpp` | 30 / 46 | `LoadedMeta`, `loadMeta`, `putMetaIfAbsent`, `casMeta`, `deleteMetaExact` — per-blob freshness meta object operations. |
| `CasPlainObjects.h` / `.cpp` | 57 / 124 | `CasPlainObjects`: fence-checked put/get/list/remove for namespace files and mountpoint objects (non-content-addressed side objects). |
| `CasBlobUploadPool.h` / `.cpp` | 24 / 75 | Process-global blob upload `ThreadPool`: `initializeBlobUploadPool`, `blobUploadPool`, `shutdownBlobUploadPool`. Initialized from `programs/server/Server.cpp` and `programs/local/LocalServer.cpp`. |
| `CasEventDispatcher.h` / `.cpp` | 31 / 46 | `EventDispatcher`: holds an optional `CasEventSink` and forwards `CasEvent`s (feeds `system.cas_log`). |

### `CA/Primitives/` — 10 files, 1,123 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `CasTypes.h` | 262 | `RootNamespace`, `ManifestRef`, `ManifestId`, `manifestOrdinalFileName`, `tryParseManifestRef`, `TokenType`, `Token`, `RefTxnId` + render/parse, `u128ToHex`/`hexToU128`, and `std::hash` specializations. |
| `CasBlobDigest.h` | 179 | `BlobHashAlgo { … }`, `blobHashAlgoName`, `blobHashLenFor`, `parseBlobHashAlgo`, `BlobDigest` + hash, `DigestCodec`, `BlobRef` + hash, `codecFor`, `blobHexOf`, `blobIdOf`. |
| `CasBlobDigest.cpp` | 47 | Algo name/length tables and parsing. |
| `CasBlobHashingWriteBuffer.h` / `.cpp` | 25 / 232 | `IBlobHashingWriteBuffer`, `makeBlobHashingWriteBuffer(algo, sink)`, `blobHashHexOneShot` — the streaming hash used on the write path. |
| `CasXxh3Streamer.h` | 46 | `Xxh3Streamer` and `xxh3_128_oneshot`. |
| `CasCodecUtil.h` | 84 | `u128ToBytesBE`/`u128FromBytesBE`, `readFixedBytes`, `isCanonicalRefName`, `checkCanonicalRefName`, `checkManifestRef` — shared decode guards. |
| `CasNamespaceLifeId.h` | 77 | `NamespaceLifePhysicalId`, `renderIncarnation`/`parseIncarnation`, `NamespaceLifeId` (namespace + incarnation identity used in every key). |
| `CasEvent.h` / `.cpp` | 76 / 95 | `CasEventType`, `CasEventObjectKind`, `CasEvent`, `CasEventSink`, `EventEmitter` (CTAD-enabled), `toString` overloads. |

### `CA/Tools/` — 6 files, 2,082 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `CasFsck.h` | 120 | `FsckProgress`, `FsckClass`, `FsckObject`, `FsckReport` (+ `clean()`), `FsckHardFinding` with a `static_assert(kFsckHardFindings.size() == 5)`, `runFsck(Pool&, detail, progress, …)`, `formatFsckSummary`. |
| `CasFsck.cpp` | 950 | Whole-pool consistency check: object enumeration and classification, ref/manifest/blob cross-checks, `chooseRecoveryGrounding` reuse, source-edge run verification. |
| `CasInspect.h` / `.cpp` | 12 / 579 | `caInspectToJson(layout, key, bytes, …)`: decodes any CAS object by key shape into JSON — the operator-facing single-object decoder. |
| `CasDecommission.h` / `.cpp` | 33 / 388 | `DecommissionReport`, `decommissionPoolMember(backend, config, victim_srid, …)`: removes a dead pool member's server-root subtree, using `Pool::openForDecommission`. |

### `CA/benchmarks/` — 1 file + CMake, 369 lines

| File | Lines | Role (from code) |
| --- | --- | --- |
| `benchmark_cas_ref_protocol.cpp` | 369 | Google-benchmark harness over `RefCowMap` / ref-protocol replay. Built only when `ENABLE_BENCHMARKS` is on (`src/CMakeLists.txt:143-145`); the top-level default is `OFF` (`CMakeLists.txt:148`), and `CMakeLists.txt:93` forces it to 0 in some configurations. |

## Subsystems and entry points

Ten subsystems, in dependency order (each depends only on the ones above it, with one exception noted):

1. **Primitives** (`CA/Primitives/`) — identity and hashing vocabulary. No dependency on `Backend`.
   Entry points: `BlobRef`/`BlobDigest`/`DigestCodec`, `ManifestRef`/`ManifestId`, `Token`, `RefTxnId`,
   `NamespaceLifeId`, `makeBlobHashingWriteBuffer`.
2. **Formats** (`CA/Formats/`) — pure encode/decode plus `Layout` key naming. Entry points: `Layout::*Key`
   / `Layout::parse*`, and one `encodeX`/`decodeX` pair per `FormatId`. `CasFormat.h` centralizes writer
   and compatibility versions (`currentWriterVersion`, `currentCompatibilityVersion`, `checkCompatibility`).
3. **Backend abstraction** (`CA/Backend/`) — `Cas::Backend` is the entire object-store contract
   (conditional put, CAS put, delete-exact-token, paged list, sentinel probe, optional server-side copy).
   Production stack: `InstrumentedBackend` wrapping `ObjectStorageBackend`, built in `CasPool.cpp`.
   Conditional-write outcome classification lives in `CasRequestControl` and is the fail-open/fail-closed
   pivot for the whole feature: `CasUnresolvedReason` + `unresolvedProvesNothingWasSent` decide whether an
   unresolved write may be retried or must be treated as possibly-applied.
4. **Ref ledger / catalog** (`CA/Pool/CasRef*`) — the durable ref table. Split cleanly into a pure state
   machine (`CasRefProtocol`: `RefTableState`, `applyRefLogTxn`, `replay`, `admits`) and an I/O engine
   (`CasRefLedger`, 3,607 lines) plus namespace lifecycle (`CasRefCatalog`) and the deletion-safety
   checkpoint (`CasRefCkpt`). Copy-on-write containers (`CasRefCowMap`, `CasRefCowManifestSet`) make
   `RefTableState` cheap to snapshot.
5. **Pool runtime** (`CA/Pool/CasPool*`, `CasMountRuntime`, `CasServerRoot`) — mount/lease/fence and epoch
   authority. `Pool::open` is the bootstrap entry point; `Pool::mayMutate` / `checkFenceOrThrow` /
   `fenceGeneration` are the write-admission guards; `CasServerRoot` holds the owner object, writer-epoch
   minting, and the mount lease CAS protocol including `claimMountAwaitingExpiry` and `computeHeartbeatFloor`.
6. **Part write path** (`CA/Pool/CasPartWriteTxn`, `CasBlobUploadPool`, `CasBlobMeta`) — `Pool::beginPartWrite`
   → `PartWriteTxn` (blob put with dedup, upload fan-out over the global thread pool, dependency records,
   manifest build, precommit → commit). The explicit `PrecommitState`/`CommitState` enums (including
   `Uncertain`) are the code-level statement that commit is not assumed atomic.
7. **Part folder access** (`CA/Parts/`) — `PartPathParser` turns a ClickHouse relative path into
   `(namespace, ref, file)`; `CachedPartFolderAccess`/`PartFolderView` is the cached manifest view that
   every `existsFile`/`getFileSize`/`listDirectory`/read call resolves against, with a configurable
   re-proof policy (`PartFolderValidate::Always|Age|Never`).
8. **GC** (`CA/Gc/`) — `CasGcScheduler` owns the background thread; `Gc::runRegularRound` is the round
   driver; `Gc::rebuildBaseline` is the rebuild path; `Gc::previewDeletes` is the dry-run path.
   Supporting: `CasBlobInDegree` (delta folding, zero-in-degree), `CasOrphanManifestSweep`,
   `CasNamespaceJanitor`, `CatalogLifecycleReconciler`, `CasGcMaintenanceState`, `CasGcPhaseTimer`.
9. **Metadata storage + transaction** (`CA/` top level) — `ContentAddressedMetadataStorage` (all read and
   enumeration verbs, admin verbs, exchange implementation) and `ContentAddressedTransaction` (all mutation
   verbs, eager). `ContentAddressedExchange` is the cross-node seam.
10. **Tools** (`CA/Tools/`) — `runFsck`, `caInspectToJson`, `decommissionPoolMember`. Exception to layering:
    `CasFsck.cpp` reaches into `Pool`, `Gc` helpers (`chooseRecoveryGrounding`) and `Formats` directly.

Key entry points, by trigger:

| Trigger | Entry point |
| --- | --- |
| Disk configuration | `registerContentAddressedMetadataStorage` → `ContentAddressedMetadataStorage` ctor (`MetadataStorageFactory.cpp:217-241,271`) |
| Server start / stop | `ContentAddressedMetadataStorage::startup/shutdown`; `Cas::initializeBlobUploadPool` / `shutdownBlobUploadPool` (`Server.cpp:1722,1500`; `LocalServer.cpp:425,902`) |
| Any read of a part file | `DiskObjectStorage::prepareRead` → `prepareInManifestRead` → `getBlobViewPlan` (`DiskObjectStorage.cpp:808-819`) |
| Any write of a part file | `DiskObjectStorageTransaction::dispatch` (eager because `transactionIsStagingOverlay()`) → `ContentAddressedTransaction::*` |
| Part fetch between replicas | `DataPartsExchange.cpp` relink path (`tryGetContentAddressedExchange`, `getRelinkOffer`, `prepareAdoptFromManifest`, `promote`) |
| Background GC | `CasGcScheduler` thread → `Gc::runRegularRound` |
| `SYSTEM CAS *` | `InterpreterSystemQuery::runContentAddressedGcRun / GcRebuild / Fsck`, `CAS_FORGET`, `CAS_GC_STOP/START`, `CAS_DROP_POOL_MEMBER` |
| `clickhouse-disks` | `cas-fsck`, `cas-gc-dryrun`, `cas-gc-rebuild`, `cas-inspect`, `cas-drop-member` (`DisksApp.cpp:345-349`) |
| Observability | `system.cas_log`, `system.cas_gc_log` (`SystemLog.h:20-21`), `system.cas_mounts` (`attachSystemTables.cpp:250`), 156 `CAS*` ProfileEvents, `ServerAsynchronousMetrics.cpp:374` |

## External integration seams

**Disk layer.**

- `src/Disks/IDisk.h:475` — `virtual bool isContentAddressed() const { return false; }` (new base virtual).
- `src/Disks/ReadOnlyDiskWrapper.h:88` — forwards `isContentAddressed`.
- `src/Disks/DiskObjectStorage/DiskObjectStorage.h:217`, `.cpp:763-766` — forwards to metadata storage.
- `DiskObjectStorage.cpp:755-761` — `supportsHardLinks()` returns `true` unconditionally for CAS, bypassing
  the `isWriteOnce`/`isPlain` test used for every other metadata storage.
- `DiskObjectStorage.cpp:806-822` — the read seam: `prepareInManifestRead` (inline/in-manifest content
  short-circuit) then `getBlobViewPlan` (substitutes a single `StoredObject` for `getStorageObjects`).
- `DiskObjectStorageCache.cpp:21` — a CAS metadata storage is excluded from the cache-metadata wrapper.
- `MetadataStorages/Cache/MetadataStorageFromCacheObjectStorage.{h:66,cpp:172-175}` — forwards `isContentAddressed`.
- `MetadataStorages/IMetadataStorage.h:306,308,310` — new virtuals `isContentAddressed`,
  `transactionIsStagingOverlay`, `supportsAtomicFileWrites`.
- `MetadataStorages/MetadataStorageFactory.cpp:217-241,271` — registration; creates `scratch_path` directories.
- `DiskObjectStorageTransaction.h:129-135` — `dispatch()` executes immediately when
  `transactionIsStagingOverlay()`, instead of queueing an undoable operation.
- `DiskObjectStorageTransaction.cpp:570-573, 619-622` — `commit`/`tryCommit` throw `LOGICAL_ERROR` if a
  staging-overlay transaction has any queued operation. This is a fail-closed detector for any mutation
  path that bypasses `dispatch()`; it is the seam that `idisk-contract` should exercise per verb.

**MergeTree.**

- `IDataPartStorage.h:192` — new virtual `isContentAddressed`; `DataPartStorageOnDiskBase.{h:43,cpp:276-279}`
  forwards to the disk.
- `DataPartStorageOnDiskBase.cpp:417-422` — backup via temporary hard links is refused on CAS
  (`SUPPORT_IS_DISABLED`).
- `DataPartStorageOnDiskBase.cpp:530-533` — clone creates an owned disk transaction when there is no
  external one, so CAS clones are transactional.
- `DataPartStorageOnDiskBase.cpp:702-712` — cross-disk clone into a CAS destination goes through
  `copyDirectoryContentIntoTransaction` + explicit `commit()`.
- `MergeTreeData.cpp:5919-5922` — empty-part creation explicitly commits the part-storage transaction on CAS.
- `MergeTreeData.cpp:7498-7500` — restore-from-backup creates a disk transaction on CAS.
- `MergeTask.cpp:562` — projections reuse the parent transaction when the parent part storage is CAS.
- `IMergeTreeDataPart.cpp:1359` — same rule for temporary projections.
- `DataPartsExchange.{h,cpp}` — the richest seam: `tryGetContentAddressedExchange` (`:109-114`),
  pool-identity + namespace-ownership match before trusting a relink (`:173-198`), source-token
  advertisement (`:311-320`), receiver-side pool match (`:588-600`, `:780-786`), and the
  prepare/promote handshake with three-valued outcomes (`:1148`, `:1183` `MechanismFallbackAllowed`,
  `:1240-1245` `Committed` / `MechanismFallbackAllowed` / `Unresolved`).

**Interpreters / server.**

- `InterpreterSystemQuery.{h:77-80,cpp:1012-1065,2337-2540}` — seven `SYSTEM CAS *` verbs, each with its own
  `AccessType` check, plus report-to-columns adapters.
- `Context.{h:131-132,1624-1625,cpp:6241-6255}` — `getContentAddressedLog`, `getContentAddressedGarbageCollectionLog`.
- `Interpreters/ContentAddressedLog.{h,cpp}`, `ContentAddressedGarbageCollectionLog.{h,cpp}` — the two system logs.
- `SystemLog.{h:20-21,cpp:34-35}`, `Common/SystemLogBase.{h:20-21,cpp:9-10}` — registration of both elements.
- `ServerAsynchronousMetrics.cpp:14,374` — per-disk CAS metrics via `tryFromDisk`.
- `Storages/System/StorageSystemContentAddressedMounts.cpp:122-149` — `system.cas_mounts` via
  `tryFromDisk` → `Cas::listMounts(backend, layout, now_ms, skew_margin_ms)`;
  `attachSystemTables.cpp:81,250`.
- `Access/Common/AccessType.h:351-357` — seven `SYSTEM_CAS_*` privileges.
- `Parsers/ASTSystemQuery.{h:150-156,187}`, `ASTSystemQuery.cpp:156,263-274`, `ParserSystemQuery.cpp:460-489` —
  grammar, including `SYSTEM CAS GC REBUILD [FORCE]`.
- `Common/ProfileEvents.cpp` — 156 `CAS*` events; all 156 are incremented somewhere in `src/` (verified by
  set difference), so there are no dead metrics.
- `Core/ServerSettings.cpp` — `cas_blob_upload_pool_size` (default 16).
- `programs/server/Server.cpp:106,1500,1722` and `programs/local/LocalServer.cpp:67,425,902` — blob upload
  pool lifecycle; `programs/server/config.xml` — CAS log tables.
- `programs/disks/CommandFsck.cpp`, `CommandCaGcDryRun.cpp`, `CommandCaGcRebuild.cpp`, `CommandCaInspect.cpp`,
  `CommandCaDropMember.cpp`, `DisksApp.{h,cpp:345-349}` — the offline tool surface.
- `Common/ThreadStatus.h` — modified in the working tree, but only by deletion of an explanatory comment
  about parenting a borrowed child thread group's trackers; `parent_thread_group` itself is unchanged.

Notably **absent** seams (checked, no hits): `src/Backups/**` has no CAS-specific branch (CAS backup is
refused at `DataPartStorageOnDiskBase.cpp:417`), and no `src/Storages/ObjectStorage/**` or
`src/Storages/MergeTree/MergeTreeDataPartWriter*` file references CAS.

## IDisk/IMetadataStorage override surface

**New virtuals added to base interfaces by this feature** (not overrides — additions):
`IDisk::isContentAddressed`, `IMetadataStorage::isContentAddressed`,
`IMetadataStorage::transactionIsStagingOverlay`, `IMetadataStorage::supportsAtomicFileWrites`,
`IDataPartStorage::isContentAddressed`. All default to `false`, so every non-CAS storage keeps its
behaviour; the risk is entirely in the CAS-side branches.

**`ContentAddressedMetadataStorage` overrides** (`ContentAddressedMetadataStorage.h`):

| Group | Overridden |
| --- | --- |
| Identity / capability | `getType` (`MetadataStorageType::CAS`), `getPath`, `supportsChmod` = false, `supportsStat` = false, `isReadOnly`, `isContentAddressed` = true, `transactionIsStagingOverlay` = true, `supportsAtomicFileWrites` = true, `supportsTransactionalMutableFiles` = true, `areBlobPathsRandom` = false, `getHardlinkCount` ≡ 0 |
| Existence / metadata | `existsFile`, `existsDirectory`, `existsFileOrDirectory`, `getFileSize`, `getLastModified` |
| Enumeration | `listDirectory`, `iterateDirectory`, `isDirectoryEmpty` |
| Object resolution | `getStorageObjects`, `getStorageObjectsIfExist` |
| Lifecycle | `createTransaction`, `startup`, `shutdown` |
| Exchange (new interface) | `getPoolUUID`, `ownsNamespace`, `confirmExactRef`, `getRelinkOffer`, `prepareAdoptFromManifest`, `prepareInManifestRead`, `getBlobViewPlan` |

**Left to the base** (i.e. CAS inherits the base default, which for several of these is
`throwNotImplemented()`): `getFileSizeIfExists`, `getLastModifiedIfExists`, `getLastChanged`, `stat`,
`readFileToString`, `readInlineDataToString`, `getSerializedMetadata`, `refresh`, `isTransactional`,
`isPlain`, `isWriteOnce`, `supportsEmptyFilesWithoutBlobs`, `getZooKeeperName`/`getZooKeeperPath`,
`getBlobsToRemove`/`recordAsRemoved`/`hasPendingRemovalBlobs`,
`getBlobsToReplicate`/`recordAsReplicated`/`hasUnreplicatedBlobs`,
`updateCache`/`updateCacheFromSerializedDescription`/`invalidateCache`/`dropCache`, `applyNewSettings`,
`supportWritingWithAppend`.

Two of these are worth naming for downstream audits:
`readFileToString`/`readInlineDataToString` throw `NOT_IMPLEMENTED` on CAS (`IMetadataStorage.h:242-252`),
so any caller that expects metadata-string access will get an exception rather than a fallback; and
the blob-removal / blob-replication ledger hooks are entirely un-implemented on CAS, which means CAS
relies on its own GC rather than the generic pending-removal machinery.

**`ContentAddressedTransaction` overrides** (`ContentAddressedTransaction.h:33-76`): `supportsChmod`,
`commit`, `tryCommit`, `generateObjectKeyForPath`, `getSubmittedForRemovalBlobs`,
`tryGetInFlightStorageObjects`, `tryReadFileInFlight`, `tryGetInFlightFileSize`, `hasInFlightDirectory`,
`listInFlightDirectory`, `createMetadataFile`, `tryCreateWriteBuffer`, `createDirectory`,
`createDirectoryRecursive`, `removeDirectory`, `removeRecursive`, `createHardLink`, `setLastModified`,
`chmod`, `setReadOnly`, `moveDirectory`, `moveFile`, `replaceFile`, `unlinkFile`, `truncateFile`.
**Not overridden:** `writeStringToFile`, `writeInlineDataToFile`, `addBlobToMetadata`,
`recordBlobsReplication` — all of which throw `NOT_IMPLEMENTED` in the base
(`IMetadataStorage.h:47-57,130,141`).

**Structural differences vs a classical `DiskObjectStorage` metadata storage:**

1. *Eager instead of deferred.* `transactionIsStagingOverlay() == true` makes
   `DiskObjectStorageTransaction::dispatch` apply each operation immediately, so the generic `undo()` path
   is unusable and `commit()` asserts the queue is empty. Rollback semantics move entirely into
   `ContentAddressedTransaction`'s own staging/`cleanupPendingTempFiles` logic.
2. *Path→object mapping is not 1:1.* A file resolves through `PartPathParser` → `PartFolderView` →
   `PartManifest` → `BlobRef`. `areBlobPathsRandom() == false`, and `getHardlinkCount()` is a constant 0
   even though `supportsHardLinks()` is forced true at the disk level.
3. *Read path is intercepted above `getStorageObjects`* (inline content and single-blob view plan).
4. *Writes are content-addressed and conditional.* No plain PUT: everything goes through
   `Backend::putIfAbsent`/`casPut`/`deleteExact` with tokens, and unresolved outcomes are explicitly
   classified rather than retried blindly.
5. *A single-writer mount lease with a fence generation* gates all mutation
   (`Pool::mayMutate`, `checkFenceOrThrow`) — there is no analogue in the classical storages.
6. *The storage owns a background GC thread and three system tables.* No other metadata storage schedules
   its own reclamation.

## Findings

### coverage-map-1 -- `Gc/CasGcShardPlan.h` shard-reduce API has no caller (Medium)

- **Anchor:** `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcShardPlan.h:24`
  (`manifestCleanupShard`), `:26-31` (`class ShardReducer`);
  definitions at `Gc/CasGcShardPlan.cpp:17`, `:23-27`, `:33`, `:38`.
- **Trigger:** Any GC round with `gc_shards > 1`.
- **Evidence:** Repo-wide search for `ShardReducer` returns only its own declaration and definition
  (`CasGcShardPlan.h`, `CasGcShardPlan.cpp`). `manifestCleanupShard` likewise appears only at its
  declaration and definition. By contrast the sibling `blobShard` (`CasGcShardPlan.h:16`) *is* used from
  `Gc/CasGc.cpp`. So the shard-ownership helper for *blobs* is live while the shard-ownership helper for
  *manifest cleanup* and the whole `ShardReducer::reduce(Backend&, Layout&, …)` driver are dead.
  `ShardReducer::ShardReducer` also contains the only range/`gc_shards >= 1` validation in the file
  (`CasGcShardPlan.cpp:27-31`), so that validation never runs.
- **Notes:** Two readings, both material for `gc-protocol` and `gc-rebuild-feature`: either sharded
  manifest cleanup was inlined into `CasGc.cpp` and this file is leftover (dead code, and the `gc_shards`
  range validation is silently unreachable), or the sharded reduce path was intended to be wired and is
  not, in which case multi-shard GC does not shard the way this API implies. `gc_shards` is a
  creation-time-only setting (`ContentAddressedSettings.cpp`), so a wrong assumption here is not
  reversible on an existing pool. Static evidence cannot distinguish the two readings; the GC audits
  should determine which, starting from how `CasGc.cpp` computes per-shard ownership without `ShardReducer`.

### coverage-map-2 -- `Cas::InMemoryBackend` (487 lines) has no caller in the shipped tree (Medium)

- **Anchor:** `Backend/CasInMemoryBackend.h:11` (`class InMemoryBackend : public Backend`),
  `Backend/CasInMemoryBackend.cpp:1-393`.
- **Trigger:** Build of `dbms` — the file is in `src/`, unconditionally compiled, with no `ENABLE_TESTS`
  or `ENABLE_BENCHMARKS` guard (unlike `CA/benchmarks/`, which `src/CMakeLists.txt:143-145` gates).
- **Evidence:** `rg InMemoryBackend src programs` matches only `CasInMemoryBackend.h` and
  `CasInMemoryBackend.cpp`. The 277 deleted `src/Disks/tests/gtest_cas_*` files were its callers
  (`gtest_cas_backend.cpp`, `gtest_cas_backend_contract.cpp`, `gtest_cas_backend_generation.cpp`,
  `gtest_cas_backend_listing.cpp`, and the shared `cas_test_helpers.h` are all in the deletion list).
- **Notes:** Two distinct consequences. (a) On this branch it is dead weight linked into the server
  binary, and `InMemoryBackend::supportsListTokens() == true` (`CasInMemoryBackend.h:30`) means it models
  a *stronger* backend than the production GCS path (`ObjectStorageBackend::supportsListTokens()` returns
  false when tokens are generations, `CasObjectStorageBackend.h:40`) — so any contract conclusion drawn
  from it would be optimistic. (b) It is the only second implementation of `Cas::Backend`, i.e. the only
  cross-check that the `Backend` contract is implementable more than once; with its tests stripped,
  `idisk-contract` and `ad7-protocol-skew` have no differential oracle on this tree. Severity is Medium
  rather than Low because it removes the differential evidence several other audits would otherwise rely on.

### coverage-map-3 -- 264 `*ForTest` seams compiled into production CAS classes, several state-mutating, with zero callers (Low)

- **Anchor:** `Pool/CasPool.h` (66 matching lines), `Pool/CasRefLedger.h` (45),
  `ContentAddressedMetadataStorage.h` (10), `Gc/CasGc.h` (8), `Pool/CasMountRuntime.h` (5), and 15 more files;
  264 occurrences of `ForTest` in `CA/` in total.
- **Trigger:** Any code path that can reach a `Pool`, `CasRefLedger`, `Gc`, or
  `ContentAddressedMetadataStorage` instance.
- **Evidence:** These are public members with no `#ifdef`. The   state-mutating ones are the concern, not the
  read-only counters: `Pool::setLifecycleForTest` (`CasPool.h:192`),
  `Pool::publishVanishedIntentForTest` (`:194`), `Pool::setLiveWriterEpochForTest` (`:270`),
  `Pool::scheduleRemountForTest` (`:274`), `Pool::beginShutdownForTest` (`:276`),
  `ContentAddressedMetadataStorage::armPromoteFailureForTest` (`:235`),
  `setEmptyProofProbeOverrideForTest` (`:228-231`), `setGcVerbAdmitWindowHookForTest` (`:233`),
  `startup_fault_injection_for_test` (`:134`, a public `std::function` member),
  `Gc::setRebuildEdgeBudgetForTest` / `setTrimEnabledForTest` (`CasGc.h:274,276`),
  `CasRefLedger::setCarveHookForTest` (`CasRefLedger.h:151`, driving the `CarvePhaseForTest` enum at
  `:140`). All callers were in the deleted gtest files.
- **Notes:** Not exploitable from SQL — no `SYSTEM` verb or setting reaches them. The reportable facts are
  that they enlarge the mutable API of the fence/lifecycle/epoch machinery (relevant to `security` and
  `concurrency` when reasoning about invariant enforcement points), and that on this tree they are
  uncovered code by construction (relevant to `test-coverage-fuzzing`).

### coverage-map-4 -- `Formats/CasFormat.h` change-point registry is populated but never consulted (Low)

- **Anchor:** `Formats/CasFormat.h:52-58` (`struct FormatChangePoint`, `changePoints(FormatId)`);
  `Formats/CasFormat.cpp:19-45` (six populated tables: `BASELINE`, `REF_STREAM`, `REF_CKPT`,
  `REF_CATALOG`, `GC_MAINTENANCE_STATE`, `POOL_META`, keyed by named generation constants such as
  `kContiguousRefStreamsGeneration`, `kUnifiedRefLifeFoldGeneration`).
- **Trigger:** Reading an object written by a different version.
- **Evidence:** `rg changePoints|FormatChangePoint src programs` matches only `CasFormat.h` and
  `CasFormat.cpp`. Nothing calls `changePoints()`. Version gating that *does* run goes through
  `checkCompatibility(compatibility_version, what)` and `currentCompatibilityVersion()`, which are used
  from `CasTextFormat.cpp`, `CasRecordStreamFormat.cpp`, `CasBlobEnvelopeFormat.cpp`.
- **Notes:** So per-format change-point knowledge exists in the binary as data but has no consumer; all
  actual cross-version admission collapses to one global compatibility integer. `upgrade-compat` and
  `ad7-protocol-skew` should treat the change-point tables as documentation-in-code with no enforcement,
  and check whether a per-format decision is needed anywhere the global version is too coarse.

No further confirmed defects: no duplicated implementation was found (`SourceEdgeRunView` in
`Gc/CasBlobInDegree.h:59` is a lifetime-owning wrapper around `Formats/CasRecordStreamFormat.h:61`'s
`SourceEdgeRunReader`, not a second implementation), every other subsystem in the tree has at least one
live caller, and all 156 `CAS*` ProfileEvents are both declared and incremented.

## Blind spots not covered by the 39 audit angles

Regions of the current code surface that no angle in the list
(codeonly-line, coverage-map, idisk-contract, write-protocol, read-protocol, gc-protocol,
gc-rebuild-feature, jepsen-anomaly, security, concurrency, interleaving, crash-consistency,
upgrade-compat, tla-fidelity, bc1-offset-overflow, bc2-writebuffer-spill, bc3-exception-safety,
bc4-protobuf-decode, bc5-wide-part-read, bc6-mtime-semantics, bc7-blocking-io-locks,
ad1-hash-determinism, ad2-deletion-erasure, ad3-day2-dr-runbook, ad4-migration,
ad5-resource-exhaustion, ad6-s3-lifecycle-cross-region, ad7-protocol-skew, mergetree-part-support,
datatype-agnosticism, alter-merge-mutation, encryption, performance, test-coverage-fuzzing,
tier1-4, backfill-not-reviewed) names as its subject:

1. **Configuration validation and the `non_cas_keys` allow-list.** `ContentAddressedSettings.cpp` is 154
   lines of parsing, macro expansion (`server_root_id` expands macros like the S3 endpoint), and rejection
   of unknown disk keys against a hardcoded 15-entry `non_cas_keys` set. A key that belongs to a new
   object-storage type and is absent from that set would make a valid disk config fail to start; a
   mis-parsed budget would silently change GC behaviour. 29 settings, several creation-time-only
   (`gc_shards`, `blob_hash`), none of them the subject of any listed audit.
2. **`Tools/CasInspect.cpp` (579 lines) as a decoder.** It re-decodes every object kind by key shape,
   independently of the writers. A key shape it fails to classify, or a format whose decode branch is
   missing, degrades the primary offline diagnostic. `ad3-day2-dr-runbook` covers procedure, not this
   decoder's completeness against `FormatId`.
3. **`Tools/CasDecommission.cpp` (388 lines) / `SYSTEM CAS DROP POOL MEMBER`.** A destructive, operator-
   triggered removal of another server's root subtree via `Pool::openForDecommission`. It has its own
   catalog duties and delete-classification logic. No listed angle owns it: it is not GC, not
   crash-consistency, and `security` as scoped covers privileges rather than this verb's blast radius.
4. **`system.cas_mounts` / `Cas::listMounts` / `computeHeartbeatFloor` clock-skew arithmetic.**
   `StorageSystemContentAddressedMounts.cpp:149` passes a `skew_margin_ms`; `CasServerRoot.h:199,227`
   define `mountObservationThresholdMs(ttl_ms, cadence_ms)` and `HeartbeatFloor`. Lease TTL vs renew
   cadence vs skew margin is a correctness-relevant arithmetic relationship
   (`validateCasRequestBudget(budget, mount_lease_ttl_ms, mount_renew_period_ms)`,
   `CasRequestControl.h:96`) that `concurrency` and `jepsen-anomaly` will exercise dynamically but no
   angle audits as arithmetic.
5. **Observability correctness.** 156 ProfileEvents, `system.cas_log` (`Primitives/CasEvent.h` +
   `Pool/CasEventDispatcher`), `system.cas_gc_log` (`Gc/CasGcScheduler.h` `GcRoundLogRecord`), and
   `ServerAsynchronousMetrics.cpp:374`. Whether an event fires on every branch it claims to describe —
   in particular the fail-closed and `Unresolved` branches — determines whether any incident is
   diagnosable. `performance` covers cost, not accuracy.
6. **`Formats/CasByteBudget.h` and the reservation-sizing chain.**
   `foldSealFixedBytes`, `worstCaseEntryFoldReservationBytes`, `widestBlobTargetRunReservationBytes`,
   `widestCondemnedSummaryReservationBytes`, `checkFoldSealReservation`, `checkCatalogAdmission`
   (`CasRefCatalogFormat.h:61-72`) form an admission-control sizing chain that decides whether a catalog or
   fold-seal write is even attempted. `bc1-offset-overflow` covers offsets, not these budget products;
   `ad5-resource-exhaustion` covers runtime exhaustion, not the static sizing math.
7. **`Parts/PartPathParser` split cache.** A memoized path-split cache (`splitCacheMissesForTest`,
   `resetSplitCacheForTest`, `PartPathParser.cpp:177`) sits on the hot path of every metadata call. Its
   invalidation and unbounded-growth behaviour is not owned by any listed angle.
8. **`Mode::EmulatedSingleProcess`.** Selected automatically whenever the object storage is
   `ObjectStorageType::Local` (`ContentAddressedMetadataStorage.cpp:509-511`) — i.e. by configuration
   shape, not by an explicit opt-in — and it substitutes in-process emulated conditional operations plus a
   key-prefix rewrite (`:526-541`). Correctness then depends on there being exactly one process. Since
   this is the mode most local testing runs in, results from every other angle may have been obtained
   against the emulated backend rather than the real conditional-write dialect. This is the single most
   consequential blind spot in the list.
9. **`ReadOnlyDiskWrapper` / read-only CAS.** `isReadOnly()` feeds `checkOpAdmitted`
   (`CasOpClass::{Factory,Probe,ContentRead,Write,Remove,Admin}` × `CasOpAdmission::{Proceed,TruthAbsent}`).
   The read-only and `TruthAbsent` admission matrix — which verbs are refused, and whether refusal is
   fail-closed — is not the subject of any angle.
10. **`forgetDisk` / `CAS_FORGET`.** `ContentAddressedMetadataStorage::forgetDisk` and
    `Pool::forgetDisk(stop_and_join_gc, reason)` tear down a live pool including joining the GC thread,
    both annotated `TSA_NO_THREAD_SAFETY_ANALYSIS` (`ContentAddressedMetadataStorage.h:125,128,130,132`).
    Thread-safety analysis is explicitly suppressed on `startup`, `forgetDisk`, `gcStop`, `gcStart` —
    exactly the four lifecycle verbs — which is worth a targeted look that neither `concurrency` nor
    `bc7-blocking-io-locks` currently scopes.
11. **The `benchmarks/` target.** `benchmark_cas_ref_protocol.cpp` (369 lines) is compiled only under
    `ENABLE_BENCHMARKS`, default `OFF`. It can rot without any signal, and it is the only in-tree
    performance harness for the ref protocol — relevant to `performance`, which will otherwise have no
    baseline.

## By-design / info / non-actionable

- `CA/benchmarks/` being unbuilt by default matches how `src/Common/benchmarks` and `src/Columns/benchmarks`
  are gated; not a defect.
- `Layout::casRefsPrefix()` (`Formats/CasLayout.h:85-88`) is an alias that returns
  `namespaceStreamRootPrefix()`. Both names are used (`CasRefProtocol.cpp`, `CasGc.cpp`,
  `CasInspect.cpp`), so this is a naming redundancy, not dead code.
- `Backend::promoteStaged` and `Backend::resurrect` default to `NOT_IMPLEMENTED`
  (`Backend/CasBackend.h:181-192`), but `ObjectStorageBackend` overrides both, so the throwing defaults are
  unreachable in production. `promoteStaged` additionally throws when
  `mode != Mode::Native` (`CasObjectStorageBackend.cpp:791`), which is a real reachable branch under the
  emulated mode and belongs to `write-protocol`.
- The `src/Common/ThreadStatus.h` working-tree diff is comment-only, consistent with the code-only strip.
- `Formats/README.md` and `CA/README.md` are deleted in the working tree; per the code-only rule they
  were not read, and their absence changes nothing about the code surface.

## Coverage

Enumerated: all 129 `.cpp`/`.h` files under `CA/` plus `benchmarks/CMakeLists.txt`, with line counts and a
code-derived role for each; nothing in the code root is unclassified.

Reachability: checked callers repo-wide for every subsystem-level class and for ~35 individual exported
free functions and `Pool`/`Backend`/`Layout` methods chosen as likely-orphan candidates. Confirmed live:
`InstrumentedBackend`, `CasPlainObjects`, `EventDispatcher`, `NamespaceJanitor`,
`CatalogLifecycleReconciler`, `runCapabilityProbe`, `probeConditionalCopy`, `readGcMaintenanceState`,
`casGcMaintenanceState`, `RefCowMap`, `RefCowManifestSet`, `probePoolBootstrapResidual`,
`probeNonTerminalMountSlots`, `publishCkpt`, `mergeCkpt`, `chooseRecoveryGrounding`, `blobShard`,
`foldSealCaps`, `checkFoldSealObjectBytes`, `classifyDeleteOutcome`, `forEachListedKey`, `traitsForType`,
`currentCompatibilityVersion`, `caInspectToJson`, `decommissionPoolMember`, `runFsck`, `previewDeletes`,
`tryRemountOnce`, `refreshAdmittedAlgos`, `mirroredArchiveNamespace`, `resurrect`, `promoteStaged`, and
all `Pool` namespace-file / mountpoint-object accessors. Confirmed dead: `ShardReducer`,
`manifestCleanupShard`, `changePoints`. No production caller: `InMemoryBackend`.

Seams: grepped `src/**` and `programs/**` for `isContentAddressed`, `ContentAddressed`, `Cas::`,
`CasBackend`, `transactionIsStagingOverlay`, `CaRelink*`, `CasRelinkSourceToken`,
`IContentAddressedExchange`, `getPoolUUID`, `ownsNamespace`, `confirmExactRef`, `getRelinkOffer`,
`prepareInManifestRead`, `getBlobViewPlan`, `CAS_*`, `cas_*`. 54 files match, of which 12 are inside the
code root; the 42 outside it are enumerated above with line anchors, together with the
`Access`/`Parsers`/`Core`/`ProfileEvents` seams found by the separate `CAS_*` / `cas_*` searches.

Override surface: diffed the declared virtuals of `IMetadataStorage`/`IMetadataTransaction`
(`IMetadataStorage.h`) against the `override` declarations in `ContentAddressedMetadataStorage.h` and
`ContentAddressedTransaction.h` to produce both the overridden and the not-overridden lists.

Not done (static-only limits): no build, no test execution, no coverage measurement, no dynamic
call-graph. Reachability conclusions are `rg`-based over `src/` and `programs/` only — a caller reached
exclusively through a template instantiation in a deleted test, or through a symbol name assembled at
compile time, would not be seen. Callers in `utils/**`, `contrib/**`, and `tests/**` were not searched;
for `ShardReducer`, `manifestCleanupShard`, and `changePoints` this does not change the finding, since a
non-`src` caller would not make the GC round or a format decode use them.

# tier2 (deep sweep: pool runtime, mount lifecycle, backend) -- fresh audit 2026-08-12

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`,
working tree as-is (read-only; no edits, no checkout). CAS root:
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Code-only rule applied: `docs/**` is deleted in this tree and was not consulted; comments were not
treated as evidence of intent. Shipped strings (exception text, log text, event reasons, setting
descriptions) were treated as normative. All CAS tests are deleted, so every claim below is derived
from the shipped code path alone.

## Scope and tier definition

Tier2 is a line-level sweep of **the pool runtime, the mount lifecycle and the backend layer** —
i.e. the machinery that decides *whether this process is currently allowed to write at all*, and the
machinery that turns object-store results into CAS outcomes. Concretely:

- `Pool/CasPool.{h,cpp}` — pool open / decommission-open / self-remount / teardown ordering.
- `Pool/CasMountRuntime.{h,cpp}` — the mount fence, the lifecycle state machine, the remount thread.
- `Pool/CasServerRoot.{h,cpp}` — owner claim, epoch allocation, mount claim, `SingleWriterSlot` /
  `MountLeaseKeeper`, GC heartbeat floor, mount listing.
- `Pool/CasPoolMeta.cpp`, `Pool/CasPlainObjects.cpp`, `Pool/CasManifestReader.*`,
  `Pool/CasEventDispatcher.*`, `Pool/CasBlobUploadPool.*`, `Pool/CasBlobMeta.*` (runtime aspects).
- `Backend/*` — the `Backend` contract, the object-storage backend, request control, probes,
  instrumentation, the in-memory backend.
- `ContentAddressedSettings.{h,cpp}` — validation, ranges, and what is (and is not) configurable.

Deliberately **out** of tier2 and left to the angle audits: the ref ledger / ref protocol internals,
the GC round machinery, formats/codecs, and the part write transaction body. They are only touched
where a tier2 gate is consumed by them.

Sibling findings cited, not re-derived: no intra-pool authentication; `retired_at_ms` / `gc_fenced`
writable by any peer; `attempt_timeout_ms` never reaches the wire; `NoSuchKey` folded into
`PreconditionFailed`; versioning check only on the GCS dialect and fails open; `skip_access_check`
hardcoded in the decommission remount; `Backend::resurrect` bypasses the controller; the emulated-mode
token is the filesystem mtime.

## Region walked

| File | Lines | Functions / regions reviewed |
| --- | --- | --- |
| `Backend/CasBackend.h` | 1-241 (all) | `Range::whole`, `Backend` default `probeSentinelRaw`, `promoteStaged`, `resurrect`, `forEachListedKey`, `classifyDeleteOutcome`, `deleteClassName`, all result structs and enums |
| `Backend/CasRequestControl.h` | 1-179 (all) | `CasWriteOutcome` / `CasUnresolvedReason` enums, `unresolvedProvesNothingWasSent`, `describeUnresolvedReason`, `CasRequestBudget` defaults, controller surface |
| `Backend/CasRequestControl.cpp` | 1-566 (all) | `classifyConditionalWriteResult`, `recordConditionalWriteAttemptStarted/Outcome`, `isDeterministicLocalFailure`, `validateCasRequestBudget`, `throwCasWriteRetryLater`, `makeCasWriteRetryLaterExceptionPtr`, `throwCasTransientUnavailable`, ctor, `backoffBeforeAttempt`, `pauseBeforeReissue`, `resolveByExactGet`, `putIfAbsentControlled`, `conditionalCreateControlled`, `putOverwriteControlled`, `putIfAbsentControlledMutable`, `slotOccupy` |
| `Backend/CasObjectStorageBackend.h` | 1-120 (all) | `supportsListTokens`, `tokenForHead`, `tokenForList`, `tokenMatches`, `mintingTypeMatches`, emulated token state members |
| `Backend/CasObjectStorageBackend.cpp` | 1-934 (all) | ctor, `checkPoolPreconditions`, `checkConditionalWriteSingleAttemptSupport`, `nativeHead`, `detail::finalizeConditionalWrite`, `finalizeConditionalWriteInstrumented`, `nativeConditionalPut`, `NativeStreamingSink`, `EmulatedBufferedSink`, `isObjectNotFound`, `readObjectRanged`, `openObjectRangedStream`, `casSizedReadSettings`, `etagComfortablyInThePast`, `emuPath/emuNowNs/emuPruneTokenState/emuExists/emuRead/emuWrite/emuObserveToken/emuMintToken`, `get`, `getStream`, `head`, `probeSentinelRaw`, `conditionalWriteSettings`, `putIfAbsent`, `putIfAbsentStream`, `putOverwrite`, `casPut`, `deleteExact`, `promoteStaged`, `resurrect`, `list` |
| `Backend/CasProbe.cpp` | 1-261 (all) | `runCapabilityProbe` (all 9 assertion blocks + `cleanup`), `probeConditionalCopy` |
| `Backend/CasSentinelProbe.cpp` | 1-92 (all) | `probeSentinel`, `isProbeSubtreeDebris`, `probePoolBootstrapResidual` |
| `Backend/CasInstrumentedBackend.h` | 1-138 (all) | `CasNs` / `CasOp` enums, every `InstrumentedBackend` override |
| `Backend/CasInstrumentedBackend.cpp` | 1-164 (all) | `cas_event_table`, `classifyCasNs`, `incrementCasEvent`, `InstrumentedWriteSink`, `putIfAbsentStream` |
| `Backend/CasInMemoryBackend.cpp` | 1-394 (all) | `InMemoryWriteSink`, `sliceWindow`, `mintToken`, `get`, `getStream`, `head`, `putIfAbsent`, `putIfAbsentStream`, `putOverwrite`, `casPut`, `applyDelete`, `deleteExact`, `promoteStaged`, `resurrect`, `list`, all fault-injection setters |
| `Pool/CasMountRuntime.h` | 1-190 (all) | `PoolLifecycle`, `MountConfig`, `MountFence`, full class surface and private state |
| `Pool/CasMountRuntime.cpp` | 1-431 (all) | `wallClockNowSeconds`, ctor, `bootMs`, `bootMsNow`, `waitSleep`, `mayMutate`, `tripMountLost`, `checkFenceOrThrow`, `refAppendFenceOk`, `setMountDeadline`, `armMountFence`, `minActive`, `peekNextBuildSeq`, `renewWatermarkOnce`, `allocateBuildSeq`, `registerInflightBuild`, `retireBuildSeq`, `cancelInflightBuildsForNamespace`, `mintRandomProcessEpoch`, `setProcessEpoch`, `setLiveWriterEpoch`, `installKeeper`, `keeperStart/RenewOnce/Reset/StartBackground/StopBackground`, `isVanished`, `setLifecycleForTest`, `noteLeaseLost`, `noteRemounted`, `enterIdentityLost`, `enterVanished`, `publishVanishedIntent`, `scheduleRemount`, `stopRemountThread`, `finishTeardown`, `remountTerminal` |
| `Pool/CasServerRoot.h` | 1-315 (all) | `SingleWriterSlot` surface, `validateServerRootId`, free-function declarations, `MountClaimResult`, `MountFencedException`, `HeartbeatFloor`, `MountLeaseKeeper` surface and state |
| `Pool/CasServerRoot.cpp` | 1-1171 (all) | `prefixHasAnyKey`, `defaultBootMs`, `readOwnerObject`, `throwIfOwnerRetired`, `serverRootSubtreeEmpty`, `readOwnerUuid`, `claimOwnerOrThrow`, `allocateWriterEpoch`, `makeMountBody`, `describeMountHolder`, `emitMountEvent`, `claimMount`, `mountDoubleStartMessage`, `mountObservationThresholdMs`, `claimMountAwaitingExpiry`, `computeHeartbeatFloor`, `probeNonTerminalMountSlots`, `listMounts`, `classifyFenceCertificate`, `isCreatorFenceTerminal`, `MountLeaseKeeper` (ctor, `refreshConfirmedDeadline`, `shouldFenceOnTransientRenewFailure`, `prepareRenew`, `encodeBody`, `claim`, `onRenewCommitted`, `onRenewSucceeded`, `onRenewFailed`, `onRenewMismatch`, `terminate`), `SingleWriterSlot` (ctor, dtor, `recordWrite`, `doStart`, `renewOnce`, `onRenewMismatch`, `doTerminate`, `startBackground`, `stopBackground`, `backgroundLoop`), `sweepOwnMountStaging` |
| `Pool/CasPool.h` | 1-485 (all) | `PoolConfig` (+ `refLedgerConfig`, `mountConfig`), `Pool` public/private surface, dedup cache types, writer-cleanup queue types, member declaration order |
| `Pool/CasPool.cpp` | 1-1351 (all) | `probePoolLifecycleGate`, ctor + member init order, `isAlgoAdmitted`, `refreshAdmittedAlgos`, `dedupCache*`, `bootMs`, `bootMsNow`, `mayMutate`, `tripMountLost`, `refAppendFenceOk`, `setMountDeadline`, `armMountFence`, `lifecycleReasonDetail`, `throwIfLifecycleTerminal`, `lifecycleSnapshot`, `open`, `mountWritable`, `openForDecommission`, `~Pool`, `forgetDisk`, `minActive`, `peekNextBuildSeq`, `tryRemountOnce`, `renewWatermarkOnce`, `retireBuildSeq`, `enqueueWriterCleanupDuty`, `writerCleanupDutiesPending`, `drainWriterCleanupDuties`, `beginPartWrite`, `peekForeignRefLogHeader`, `reportImpossibleInterference`, `currentGcRound`, plain-object and staging delegations, `listNamespaces`, `listMirroredChildren` |
| `Pool/CasPoolMeta.cpp` | 1-130 (all) | `mintPoolId`, `isAlgoAdmittedIn`, `joinAlgoNames`, `throwNotAdmitted`, `admitOrValidate`, `PoolMeta::createOrValidate` |
| `Pool/CasPlainObjects.cpp` | 1-125 (all) | `casPutObject`, `casGetObject`, `casRemoveObject`, namespace-file and mountpoint-object wrappers |
| `Pool/CasManifestReader.cpp` | 1-154 (all) | ctor, `ManifestCacheKeyHash`, `readManifestShared`, `readManifest`, `locate` |
| `Pool/CasEventDispatcher.cpp` | 1-47 (all) | `setSink`, `emit` |
| `Pool/CasBlobUploadPool.{h,cpp}` | all | `initializeBlobUploadPool`, `blobUploadPool`, `shutdownBlobUploadPool`, `blobUploadPoolInitializedForTest` |
| `Pool/CasBlobMeta.{h,cpp}` | all | `loadMeta`, `putMetaIfAbsent`, `casMeta`, `deleteMetaExact` |
| `ContentAddressedSettings.cpp` | 1-155 (all) | `non_cas_keys`, `LIST_OF_CONTENT_ADDRESSED_SETTINGS`, `loadFromConfig`, `validate`, cached-accessor getters |
| Cross-checked outside the CAS tree | — | `MetadataStorageFactory.cpp:217-244`, `IO/WriteBufferFromS3.cpp:650-660`, `IO/WriteBufferFromFileBase.h:20`, `IO/WriteBufferFromFileDecorator.h:22-27`, `IO/S3/getObjectInfo.cpp:135-158`, `S3ObjectStorage.cpp:479-510,602-620`, `IObjectStorage.h:214-232`, `Primitives/CasTypes.h:198-220` |

## Findings

### tier2-1 -- An empty conditional token turns a fenced write into an unconditional clobber (High)

- **Anchor.** `Backend/CasObjectStorageBackend.cpp:165-173` (token minting after a committed
  conditional PUT), `:677-678` (`putOverwrite` validates only the token *type*), `:683`
  (`ws.object_storage_write_if_match = expected.value`), `:698-707` (same in `casPut`);
  `IO/WriteBufferFromS3.cpp:656-657` (`if (!...object_storage_write_if_match.empty()) req.SetIfMatch(...)`);
  `IO/WriteBufferFromFileBase.h:20` (`getResultObjectETag()` default returns `{}`);
  `Pool/CasServerRoot.cpp:1005-1009` (`recordWrite`), `:1038` (renewal reuses `last_token`).
- **Trigger.** `nativeConditionalPut` returns `{PutOutcome::Done, token}` where `token` comes from
  `buf->getResultObjectETag()` and, when that is absent or empty, from a *second* request
  (`nativeHead`). If that fallback HEAD reports absent (a 404 in the eventual-consistency window, or
  a write buffer that is not `WriteBufferFromS3`, for which the base class returns no ETag), the
  result is `PutOutcome::Done` paired with `Token{"", TokenType::ETag}`. No caller checks
  `Token::empty()`. `SingleWriterSlot::renewOnce` latches that token as `last_token` and passes it as
  `expected` to the next `putOverwrite`; `putOverwrite` only checks `mintingTypeMatches(expected.type)`
  — which an empty `Token{}` passes, because `TokenType::ETag` is the struct default — and assigns the
  empty string to `object_storage_write_if_match`. `WriteBufferFromS3` then omits the `If-Match`
  header entirely.
- **Consequence.** The mount-lease renewal (and any other `putOverwrite`/`casPut` carrying an
  empty-valued token) becomes an **unconditional PUT**. The single-writer mount slot loses its
  compare-and-set protection precisely on the object whose whole purpose is to enforce
  exclusivity: a deposed incarnation can stamp its own lease body over its successor's, and
  `MountLeaseKeeper::terminate`'s "exclusivity violation" alarm (`CasServerRoot.cpp:960-975`) never
  fires because the write succeeds. The same degradation applies to every `casPut` (`:698-712`),
  which will then report `CasOutcome::Committed` for a write that was never conditional.
- **Evidence.** Type-only validation at `CasObjectStorageBackend.cpp:677` and `:698`; empty-token
  construction at `:171` and `:207`; the emptiness-gated header at `WriteBufferFromS3.cpp:656`. Note
  the asymmetry: `tokenForList` (`CasObjectStorageBackend.h:67-72`) *does* refuse to mint a token from
  an empty ETag, so the codebase already knows an empty ETag is not a token — the write path just
  never applies the same guard.

### tier2-2 -- Plain-object mutations bypass the request controller and use the margin-free fence (High)

- **Anchor.** `Pool/CasPlainObjects.cpp:21-41` (`casPutObject`), `:51-66` (`casRemoveObject`);
  the gate they use is `Pool/CasPool.cpp:144` → `Pool/CasMountRuntime.cpp:90-99`
  (`checkFenceOrThrow` → `mayMutate`), versus `CasMountRuntime.cpp:101-111` (`refAppendFenceOk`).
- **Trigger.** Any `putNamespaceFile` / `removeNamespaceFile` / `putMountpointObject` /
  `removeMountpointObject`. Two independent defects on the same path:
  1. `mayMutate()` (`CasMountRuntime.cpp:77-81`) admits a write while
     `bootMsNow() < deadline_boot_ms` — with **no** subtraction of
     `attempt_timeout_ms + lease_safety_margin_ms`. `refAppendFenceOk()` (`:101-111`) does exactly
     that subtraction for ref-log appends. So a namespace-file write can be admitted 1 ms before the
     local lease deadline and still be in flight for the whole request timeout afterwards.
  2. The fence is checked once *before* the write (`:28`, `:60`) and never re-checked after it
     commits, unlike every `CasRequestController` path, which re-evaluates `fence_ok()` post-commit
     and emits `CASConditionalWriteFenceLostPostWrite` (`CasRequestControl.cpp:305-309`).
- **Consequence.** A durable write can land on the store after this node's mount lease has lapsed and
  a successor incarnation has claimed the slot — the exact scenario the fence exists to prevent. The
  loop is also unprotected in three further ways: no backoff between the 100 attempts (a hot
  HEAD+PUT spin under contention), no operation deadline, and no ambiguity resolution — a
  `putOverwrite` that times out after committing propagates as a failure, so the caller believes the
  namespace file was not written when it was.
- **Evidence.** The two gates are visibly different functions with different arithmetic in the same
  file; `CasPool.cpp:151` wires `refAppendFenceOk` into the ref ledger while `CasPool.cpp:143-144`
  wires the raw generation check into `CasPlainObjects`. No `sleep`/backoff call exists anywhere in
  `CasPlainObjects.cpp`.

### tier2-3 -- `putIfAbsentControlled` swallows deterministic local failures and reports them as ambiguity (Medium)

- **Anchor.** `Backend/CasRequestControl.cpp:278-281` versus the three siblings at `:338-341`,
  `:398-401`, `:469-472` and `slotOccupy` at `:537-540`; `isDeterministicLocalFailure` at `:90-94`;
  `classifyConditionalWriteResult` at `:43-53`.
- **Trigger.** The backend throws a deterministic local error inside `putIfAbsentControlled` — e.g.
  `NOT_IMPLEMENTED` from `Backend::promoteStaged`/`resurrect` (`CasBackend.h:181-192`),
  `CORRUPTED_DATA` from a decode, `LOGICAL_ERROR` from a broken invariant, `BAD_ARGUMENTS` from a
  malformed key. `classifyConditionalWriteResult` only recognises S3 malformed-request /
  entity-too-large / access-denied and returns `Unresolved` for everything else (`:52`).
- **Consequence.** The bug is retried `max_attempts` times with capped-exponential backoff, burning
  the whole `operation_deadline_ms`, and is finally reported as
  `CasUnresolvedReason::AttemptsExhausted`. Callers translate `Unresolved` into
  `throwCasWriteRetryLater` (`:145-149`), whose shipped text is *"CAS write could not be committed
  (…); retrying later"* — so a permanent programming or configuration error is presented to the
  operator as transient object-store unavailability, forever. The other four controller entry points
  rethrow such errors immediately, so this is an inconsistency inside one file, not a design choice.
- **Evidence.** `putIfAbsentControlled`'s catch block is one line
  (`attempt_outcome = classifyConditionalWriteResult(e);`) with no `isDeterministicLocalFailure`
  check, while the four neighbouring methods all begin their catch with the identical
  `dynamic_cast<const Exception *>` + `isDeterministicLocalFailure` rethrow.

### tier2-4 -- Content equality is treated as proof of our own authorship, erasing CAS exclusivity (Medium)

- **Anchor.** `Backend/CasRequestControl.cpp:427-435` (`putOverwriteControlled`) and `:498-506`
  (`putIfAbsentControlledMutable`); consumers at `Pool/CasBlobMeta.cpp:31-38`
  (`putMetaIfAbsent` / `casMeta`) via `Pool/CasPool.cpp:1243-1251`.
- **Trigger.** Two writers issue a conditional write of *identical bytes* to the same mutable key.
  The loser's conditional write is definitively refused (`PutOutcome::PreconditionFailed`, not an
  ambiguity). The loser then re-reads the key, finds `got->bytes == bytes_s`, and returns
  `{CasOverwriteOutcome::Committed, got->token}` — the **winner's** token.
- **Consequence.** A compare-and-set that was refused is reported as committed, so two callers can
  simultaneously believe they won a mutually exclusive transition. Worse, the loser now holds the
  winner's current token, so its *next* conditional write will succeed against a slot it never
  legitimately acquired — the CAS chain is silently spliced. This is only sound if every key reached
  through these two methods is content-addressed (where byte equality does imply equivalence), but
  both are reached from `Pool::stagingConditionalOverwrite` / `stagingPutIfAbsentMutable`, whose very
  names ("Mutable", "Overwrite") say the value changes over time, and `casMeta` exists specifically
  to serialise successive *different* blob-meta states.
- **Evidence.** The `else if (got && got->bytes == bytes_s)` branch returns `Committed` with no check
  that our own attempt was ambiguous; the definite-refusal case falls into the same branch as the
  timeout case because `put` is only inspected for `PutOutcome::Done` (`:404`, `:475`).

### tier2-5 -- Ambiguous conditional creates are reported as foreign occupancy (Medium)

- **Anchor.** `Backend/CasRequestControl.cpp:357-368` (`conditionalCreateControlled`), `:543-562`
  (`slotOccupy`).
- **Trigger.** `attempt()` throws a non-deterministic error (a network timeout) after the object
  actually landed. The controller then probes with `backend->head(key_s)`; `exists` is true, so it
  returns `{CasCreateOutcome::Occupied, {}}`.
- **Consequence.** The caller is told the slot is held by someone else, when in fact the caller
  created it. `Occupied` carries no token and no `CasUnresolvedReason`, so the caller cannot recover
  the object it just wrote and cannot distinguish "a peer owns this" from "I own this but lost the
  reply". `putIfAbsentControlled` avoids exactly this by comparing bytes in `resolveByExactGet`
  (`:212-239`); `conditionalCreateControlled` has no bytes to compare (the payload is hidden behind
  the `attempt` callback) and does not ask the caller for a discriminator. `slotOccupy` has the
  mirror-image shape: it returns `Kind::Occupied` with `occupant_bytes` set to bytes that may be our
  own, and `unresolved_reason = NotUnresolved` — an affirmative claim that nothing is ambiguous.
- **Evidence.** The `head`-only occupancy test at `:361`; the absence of any own-attempt marker in
  either signature; contrast with the byte-comparing resolution used by the sibling method in the
  same class.

### tier2-6 -- Lost remount wakeup leaves the mount fenced closed until process restart (Medium)

- **Anchor.** `Pool/CasMountRuntime.cpp:341-369` (`scheduleRemount`), specifically the
  `remount_running.load()` gates at `:346` and `:349` versus `remount_running.store(false)` at
  `:367`, which is the worker's last statement after `break`.
- **Trigger.** The remount worker's `remount_attempt()` returns true and it breaks out of the loop.
  Before it executes `:367`, the freshly installed keeper (started in background at
  `CasPool.cpp:735-736`) loses a renewal, so `on_lost` (`CasMountRuntime.cpp:214-218`) calls
  `tripMountLost()` + `scheduleRemount()`. `scheduleRemount` observes `remount_running == true`,
  returns silently, and the worker then exits.
- **Consequence.** The mount is latched lost (`mount_fence.lost == true`) with no thread left to
  recover it. `mayMutate()` and `refAppendFenceOk()` both return false forever, so every durable
  write is refused with the `checkFenceOrThrow` text that tells the operator this is *"either a lease
  loss the disk auto-recovers from, or a FORGET decommission"* (`:93-98`) — but the auto-recovery
  path is gone. The lifecycle stays `TransientNotLive`, so `throwIfLifecycleTerminal`
  (`CasPool.cpp:275-282`) does not fail loud either; the disk simply refuses all writes until
  restart. `scheduleRemountCallCountForTest` (`:343`) is incremented before the gate, so the counter
  records a schedule that never happened.
- **Evidence.** There is no re-check or re-post after the worker clears `remount_running`, and no
  pending-request flag; the only other schedule sources are `reportImpossibleInterference`
  (`CasPool.cpp:989-990`) and the same keeper callback, both of which hit the identical gate.

### tier2-7 -- The whole mount/lease/request budget is unconfigurable, so its validation is dead code (Medium)

- **Anchor.** `ContentAddressedSettings.cpp:29-58` (the complete shipped setting list contains no
  `mount_lease_ttl_ms`, `mount_renew_period`, `attempt_timeout_ms`, `operation_deadline_ms`,
  `max_attempts`, `lease_safety_margin_ms`, `retry_*_backoff_ms`, or `recovery_retry_*`);
  `Pool/CasPool.h:73-74` and `:79` (defaults `30000` / `10000` / `CasRequestBudget{}`);
  `Backend/CasRequestControl.h:82-94` (defaults 5000 / 90000 / 16 / 2000 / 200 / 5000);
  `Backend/CasRequestControl.cpp:98-134` (`validateCasRequestBudget`).
- **Trigger.** Mount any content-addressed disk. `PoolConfig::cas_request_budget`,
  `mount_lease_ttl_ms` and `mount_renew_period` are never assigned anywhere in the tree — every
  occurrence is a read (`CasPool.cpp:147`, `:162`, `:401`, `:567`, `:595`). The values are therefore
  always the struct defaults.
- **Consequence.** Two distinct problems. (a) All four validation branches in
  `validateCasRequestBudget` are unreachable: with the fixed defaults, `5000 < 30000`,
  `2000 < 25000`, `5000 < 90000` and `200 <= 5000` all hold unconditionally, so the elaborate
  operator-facing rejection messages can never be emitted and the invariants they protect are never
  actually enforced against anything. (b) An operator on a high-latency, throttled or
  cross-region store cannot widen the 5 s attempt timeout, the 30 s lease TTL or the 10 s renew
  cadence, and cannot narrow the 90 s operation deadline. Their only lever is to accept repeated
  fence-outs. Combined with the sibling finding that `attempt_timeout_ms` never reaches the wire, the
  entire budget structure is inert: it is validated but never sourced and (for the timeout) never
  applied.
- **Evidence.** `validateCasRequestBudget` is called exactly once (`CasPool.cpp:401`) with the two
  `PoolConfig` defaults; the `LOG_INFO` at `CasRequestControl.cpp:127-133` prints a "budget in
  effect" line whose every field is a compile-time constant.

### tier2-8 -- A standard S3 client key under a `cas` disk aborts disk registration; numeric ranges unchecked (Medium)

- **Anchor.** `ContentAddressedSettings.cpp:23-27` (`non_cas_keys`), `:94-99` (every other child key
  is fed to `impl->set`), `:119-137` (`validate`);
  `MetadataStorageFactory.cpp:233-237` (the `config_prefix` passed in is the disk element itself).
- **Trigger.** Put any ordinary S3/disk tuning key inside a `metadata_type=cas` disk —
  `<connect_timeout_ms>`, `<request_timeout_ms>`, `<max_connections>`, `<retry_attempts>`,
  `<list_object_keys_size>`, `<support_batch_delete>`,
  `<server_side_encryption_customer_key_base64>`, `<role_arn>`, `<use_insecure_imds_request>`, and so
  on. `loadFromConfig` iterates *all* child keys of the disk prefix, skips only the nine-entry
  `non_cas_keys` allow-list plus the CAS settings, and hands everything else to
  `BaseSettings::set`, which throws "unknown setting".
- **Consequence.** The disk fails to register at server start, and the error blames a CAS setting
  name rather than telling the operator that CAS disks reject S3 client tuning. The allow-list is a
  hardcoded literal, so the failure set grows silently every time upstream adds an S3 disk key.
- **Consequence (second half).** `validate()` range-checks only `gc_interval_sec` and `gc_shards`.
  `gc_snapshot_generations_to_keep`, `part_folder_cache_max_entries`, `gc_meta_pool_size`,
  `manifest_sweep_list_budget_keys`, `manifest_sweep_delete_budget_keys`,
  `deduplication_head_first_min_bytes` and `gcs_max_conditional_put_bytes` all accept `0` with no
  check, even though `0` is documented as "unbounded" for some of them and is meaningless for others
  (`gc_meta_pool_size=0` reaches `initializeBlobUploadPool`-style pool sizing;
  `gcs_max_conditional_put_bytes=0` becomes the single-PUT cap at
  `CasObjectStorageBackend.cpp:635`).
- **Evidence.** The nine-name allow-list at `:23-27`; the unconditional `impl->set` at `:98`; the
  two-condition `validate` at `:123-126`.

### tier2-9 -- The durable mount-lease `seq` is reset to 1 on every mount (Low)

- **Anchor.** `Pool/CasServerRoot.cpp:1021` (`doStart` encodes the body with a literal seq of 1) →
  `:764-841` (`MountLeaseKeeper::claim` adopts our own live slot and writes that body with
  `putOverwrite` at `:813`), versus `:334` and `:347` (`claimMount` writes `existing.seq + 1`) and
  `:526` (the GC fence-out writes `m.seq + 1`).
- **Trigger.** Every writable mount. `mountWritable` claims the slot via `claimMount`
  (`CasPool.cpp:430-438`), which writes `existing.seq + 1`; `keeperStart()` (`:470`) then immediately
  adopts the same slot and overwrites it with `seq = 1`.
- **Consequence.** The persisted `seq` is not monotonic across incarnations. Every operator-facing
  surface that reports it is misleading: `mountDoubleStartMessage` prints it as `last_seq`
  (`:372`), `describeMountHolder` includes it in every mount-conflict exception and event
  (`:269-271`), `probeNonTerminalMountSlots` calls it "lease seq" (`:593`), and `emitMountEvent`
  publishes `holder_seq` (`:291`). No safety decision depends on `seq` today, which is why this is
  Low — but the field is presented as evidence of incarnation ordering and cannot serve that purpose.
- **Evidence.** `doStart` has no access to the observed lease at the point it calls
  `encodeBody(1, payload)`; `claim` receives the already-encoded `body` and cannot renumber it.

### tier2-10 -- The mount fence carries an identity it never checks (Low)

- **Anchor.** `Pool/CasMountRuntime.h:44-50` (`MountFence::server_uuid`, `writer_epoch`);
  `Pool/CasMountRuntime.cpp:120-121` (the only writes) versus `:77-81` and `:90-99`
  (`mayMutate` / `checkFenceOrThrow` consult only `lost`, `deadline_boot_ms` and `fence_generation`).
- **Trigger.** Any fenced write. A grep of `mount_fence.` across `Pool/` yields ten hits, of which
  `server_uuid` and `writer_epoch` appear exactly twice — both as assignments in `armMountFence`.
- **Consequence.** The fence is a bare generation counter plus a deadline; the (uuid, writer_epoch)
  pair that identifies *which* mount incarnation admitted a write is stored and then ignored. Any
  future path that re-arms the fence without incrementing the generation, or that wraps the counter,
  loses the only discriminator. The two fields are also plain non-atomic members written without
  synchronisation, so if a reader is ever added it will race with `armMountFence`.
- **Evidence.** Write-only fields; `checkFenceOrThrow`'s condition is
  `!mayMutate() || fenceGeneration() != admitted_generation`.

### tier2-11 -- `CasNs::Server` is unreachable, so eleven shipped ProfileEvents are permanently zero (Low)

- **Anchor.** `Backend/CasInstrumentedBackend.cpp:109-122` (`classifyCasNs` has no branch returning
  `CasNs::Server`), against `CasInstrumentedBackend.h:9-18` (the enum declares `Server`) and
  `CasInstrumentedBackend.cpp:99-102` (the fully populated `CASServer*` row) and `:53-63` (the eleven
  `extern const Event` declarations).
- **Trigger.** Any mount, owner or epoch operation. Those keys live under
  `gc/server-roots/<srid>/{mount,owner,epoch}`, which matches the `/gc/` test at `:119` and is
  classified as `CasNs::Gc`.
- **Consequence.** `CASServerPut`, `CASServerOverwrite`, `CASServerCompareSwap`,
  `CASServerCompareSwapConflict`, `CASServerHead`, `CASServerHeadMiss`, `CASServerGet`,
  `CASServerGetStream`, `CASServerDelete`, `CASServerList` and `CASServerPutDeduplicated` are always
  zero, and all mount-lifecycle store traffic is billed to the GC counters — so an operator cannot
  separate lease-renewal churn from GC churn. Two adjacent accounting inversions compound it:
  `:81` counts a conditional-create refusal as `PutDeduplicated` (benign dedup) even for mount/owner
  /epoch keys where it is a genuine conflict, and `:91` counts a conditional-*overwrite* refusal as
  `CompareSwapConflict`, so `CASxxxOverwrite` has no matching conflict counter at all.
- **Evidence.** The classifier's five `find(...) != npos` branches and its `return CasNs::Other`
  fallthrough; no key form in `Formats/CasLayout.h` reaches `Server`.

### tier2-12 -- `allocateWriterEpoch` can hand out writer_epoch 0 (Low)

- **Anchor.** `Pool/CasServerRoot.cpp:226-227` (the `next_writer_epoch == 0 → 1` normalisation) and
  `:230-236` (the value actually returned).
- **Trigger.** The epoch object exists and decodes with `next_writer_epoch == 0` — the struct default,
  reachable if the field is absent or zero in the stored record. The normalisation at `:226` is inside
  the `else` (object-absent) branch only, so the present-object path returns `next = 0` and stores
  `next_writer_epoch = 1`.
- **Consequence.** `0` is the "no epoch yet" sentinel throughout the runtime:
  `CasMountRuntime.h:166` initialises `live_writer_epoch{0}`, `mintRandomProcessEpoch`
  (`CasMountRuntime.cpp:188-189`) deliberately promotes a zero draw to 1, and
  `renderRefTxnId` (`Primitives/CasTypes.h:224-225`) throws when `writer_epoch == 0`. A mount that
  adopts epoch 0 would compare equal to "unset" in `PartWriteTxn`'s epoch check
  (`CasPartWriteTxn.cpp:125`) and would defeat the remount monotonicity guard — which is a
  `chassert` (`CasPool.cpp:722`) and therefore a no-op in release builds.
- **Evidence.** The asymmetric placement of the zero normalisation; the deliberate zero-avoidance in
  the sibling epoch minter shows the codebase treats 0 as reserved.

## Checked and sound

Read line-by-line and found no defect worth reporting:

- **Fence arithmetic on the ref-append path.** `refAppendFenceOk` (`CasMountRuntime.cpp:101-111`)
  correctly requires `attempt_timeout_ms + lease_safety_margin_ms < deadline - now`, guards the
  underflow with an explicit `now >= deadline` early return, and is the gate actually wired into the
  request controller (`CasPool.cpp:151` → `CasRefLedger.cpp:189-204`). The generation-plus-deadline
  admission protocol is conservative in both orders: `armMountFence` publishes the new deadline and
  bumps the generation *before* clearing `lost` (`:118-127`), and `tripMountLost` sets `lost` before
  bumping (`:83-88`), so every interleaving fails closed.
- **`backoffBeforeAttempt`** (`CasRequestControl.cpp:178-188`) — the `doublings >= 63` guard and the
  `initial > (cap >> doublings)` pre-check both avoid UB and overflow; `initial == 0` and
  `next_attempt < 2` short-circuit correctly.
- **`pauseBeforeReissue`** (`:190-210`) — checks the fence first, then verifies that
  `now + backoff + attempt_timeout` still fits inside the deadline before sleeping, and reports
  `DeadlineMidWay` versus `FenceLostMidWay` distinctly.
- **`CasUnresolvedReason` accounting** — `attempts_sent` is incremented only after both pre-send
  gates pass, so `NoAttemptSent` genuinely proves nothing was written; `earlier_attempt_unresolved`
  correctly downgrades a later `DefiniteFailure` to `DefiniteFailureAfterAmbiguity` (`:283-288`);
  `unresolvedProvesNothingWasSent` (`CasRequestControl.h:30-45`) enumerates every enumerator with no
  silent default.
- **`resolveByExactGet`** (`:212-239`) — treats a failed or absent GET as `Unresolved` (never as
  proof of absence) and escalates a *different* object at a content-addressed key to
  `CORRUPTED_DATA` rather than a retry.
- **`claimMount`** (`CasServerRoot.cpp:298-366`) — the four-way dispatch (fresh mint / foreign uuid /
  own epoch / other epoch) is exhaustive; reclaim requires an affirmative certificate
  (`gc_fenced`, the `min_active == UINT64_MAX` clean marker, or a token proven stable), never a
  wall-clock comparison, and every reclaim is a token-exact `putOverwrite`.
- **`claimMountAwaitingExpiry`** (`:398-453`) — restarts the observation whenever the token changes,
  bounds restarts at `kMaxObservationRestarts`, uses a *monotonic* clock for the stability window
  (`mono_ms_fn`) while using wall-clock only for the body it writes, and only passes
  `proven_dead_token` once the threshold is met.
- **`mountObservationThresholdMs`** (`:393-396`) — `ttl + ttl/20 + cadence` leaves headroom over
  both the TTL and one renew cadence.
- **`computeHeartbeatFloor`** (`:455-552`) — fences only on monotonic token stability (never on
  `expires_at_ms`), refreshes `first_seen_mono_ms` only on token change, bounds reclassification at
  `max_reclassify`, retries the fence-out `putOverwrite` on conflict, and prunes observations for
  srids that disappeared from the listing.
- **`MountLeaseKeeper::claim`** (`:764-842`) — refuses a foreign uuid, refuses a superseded
  writer_epoch, distinguishes `MountFencedException` (recoverable with a fresh epoch) from
  `LOGICAL_ERROR` (fail closed), and re-reads on conflict to classify the fence-inside-the-adopt
  window.
- **`MountLeaseKeeper::onRenewMismatch`** (`:864-919`) — five mutually exclusive, exhaustive
  classifications (GC-fenced, same-epoch-uncertain, superseded, foreign, vanished), each throwing
  rather than re-minting; the vanished case explicitly refuses to recreate the slot.
- **`shouldFenceOnTransientRenewFailure`** (`:732-739`) and the `backgroundLoop` transient path
  (`:1106-1128`) — `confirmed_deadline_ms == 0` fails closed, and the margin is applied before
  deciding to keep retrying; `confirmed_deadline_ms` is anchored on `last_attempt_wall_ms` captured
  *before* the write (`prepareRenew`, `:741-746`), which is the conservative choice.
- **`MountLeaseKeeper::terminate`** (`:921-987`) — token-exact release, and on conflict it
  distinguishes GC-fenced (no-op), already-deposed (skip the farewell rather than stamp over the
  successor), and a true exclusivity violation (fence + loud error + throw).
- **`SingleWriterSlot` state machine** (`:1000-1090`) — `dead`/`seq==0` guards reject
  start-after-terminate, renew-before-start and double-terminate; `stopBackground` moves the thread
  out under the lock before joining, so it is safe to call from both `stopBackground` and the
  destructor.
- **`claimOwnerOrThrow`** (`:105-159`) — re-verifies subtree emptiness *after* a losing
  `putIfAbsent`, re-reads the owner, and only accepts a matching uuid; `throwIfOwnerRetired` gates on
  the tombstone in both the fast and the re-read path.
- **`allocateWriterEpoch`'s absent-object branch** (`:183-224`) — refuses to re-mint over a non-empty
  subtree, requires an affirmative `KeyAbsent` mount probe, and fails closed on
  `ContainerAbsent`/`AccessDenied`/`Indeterminate` with the shipped text *"absence was never proven;
  failing closed"*. The `switch` covers every `ProbeOutcome`.
- **`probePoolLifecycleGate`** (`CasPool.cpp:93-131`) — requires `Present` + decodable +
  matching `pool_id` *and* `blob_header_len` to recover; requires *both* sentinels to probe
  `KeyAbsent` before declaring `IdentityLost`; every other outcome, including an undecodable body,
  stays `StayTransient`. This is the correct fail-safe polarity for a terminal state.
- **`Pool::open` bootstrap gating** (`:299-350`) — the four `BootstrapResidual` cases are handled
  exhaustively, `ResidualWithoutMeta` additionally enumerates non-terminal mount slots before
  refusing, and `Indeterminate` fails closed. `probePoolBootstrapResidual`
  (`CasSentinelProbe.cpp:24-89`) treats a failed LIST as `Indeterminate` and requires the catalog to
  be byte-identical to the canonical empty encoding.
- **`tryRemountOnce`** (`CasPool.cpp:633-767`) — serialised by `remount_mutex`, checks vanished and
  the lifecycle gate before touching the store, quiesces ref recoveries and ref tables *before*
  arming the fence, and arms the fence from an anchor captured before `keeperStart()`. Every failure
  path emits a typed event and returns false rather than half-arming.
- **`mountWritable`'s fence-recovery loop** (`:425-483`) — bounded at three recoveries, re-mints the
  writer epoch on `FencedSelf` and on `MountFencedException` from `keeperStart`, resets the keeper
  before retrying, and re-renews the lease if the claim itself consumed the TTL (`:506-513`).
- **`Pool::~Pool` / `forgetDisk` teardown order** (`:562-606`) — the remount thread is stopped
  before draining, the drain result gates whether a clean-release marker is written, and
  `forgetDisk` chassert-guards against running on a CAS pool thread (self-join deadlock).
  `finishTeardown` (`CasMountRuntime.cpp:399-428`) logs and downgrades to `stopBackground` when the
  ref lanes did not drain, rather than stamping a false clean farewell.
- **`drainWriterCleanupDuties`** (`CasPool.cpp:828-896`) — the `draining` flag plus condition
  variable serialises drains per namespace, the queue entry is popped only after the ref mutation
  succeeded, and the catch-all resets `draining` and re-notifies before rethrowing.
- **`beginPartWrite`** (`:898-912`) — `SCOPE_EXIT` retires the build sequence if registration throws,
  so the active-build watermark cannot leak.
- **`allocateBuildSeq` / `minActive` / `retireBuildSeq`** (`CasMountRuntime.cpp:129-167`) — all under
  `builds_mutex`; `minActive` returns `next_build_seq` when the active set is empty, which is the
  correct high-watermark answer. `cancelInflightBuildsForNamespace` (`:169-180`) copies the locked
  weak-pointer snapshot and calls out *without* the lock, avoiding lock inversion.
- **`enterVanished` / `noteLeaseLost` / `noteRemounted` / `enterIdentityLost`**
  (`CasMountRuntime.cpp:265-334`) — the compare-exchange transitions cannot regress a terminal state,
  `enterVanished` rejects non-terminal arguments with `LOGICAL_ERROR`, and
  `terminal_state_published.exchange` makes the first terminal publication win.
- **`runCapabilityProbe`** (`CasProbe.cpp:15-211`) — nine independent assertions covering
  conditional create, conditional overwrite (both directions), token freshness, token-exact CAS with
  nullopt and stale tokens, token-exact delete (both directions), list-after-write and
  list-after-delete, plus a `noexcept` cleanup on every exit path. Notably it re-reads the body after
  every "rejected" outcome, so a backend that reports a conflict while clobbering is caught.
- **`get`/`head` do not fold transient errors into absence.** `nativeHead` uses
  `tryGetObjectMetadata`, which reaches `S3::getObjectInfoIfExists`
  (`IO/S3/getObjectInfo.cpp:135-158`); that function returns an empty info only for a genuine
  not-found error and **throws** on everything else. So a 503 cannot masquerade as `KeyAbsent` and
  cannot drive `probePoolLifecycleGate` into the terminal `IdentityLost` verdict.
- **`probeSentinelRaw`** (`CasObjectStorageBackend.cpp:575-626`) — maps `NO_SUCH_KEY` /
  `RESOURCE_NOT_FOUND` to `KeyAbsent`, `NO_SUCH_BUCKET` to `ContainerAbsent`, `ACCESS_DENIED` to
  `AccessDenied` and every other S3 error plus every non-S3 exception to `Indeterminate`; the
  emulated branch checks container presence first. The `Backend` base default (`CasBackend.h:163-179`)
  is likewise `Indeterminate`-on-throw.
- **`conditionalWriteSettings`** (`:628-640`) — disables post-upload verification, forces a single-part
  upload with an explicit cap on generation-token dialects, caps unexpected-write retries at 1, and
  selects the `SingleAttempt` retry profile; `checkConditionalWriteSingleAttemptSupport` refuses to
  mount writable if the storage cannot honour it.
- **Emulated token bookkeeping** (`:344-465`, `:763-787`) — the `#N` disambiguation suffix, the
  bounded expiry sweep (`EMU_TOKEN_EXPIRY_SWEEP_SIZE`), the `etagComfortablyInThePast` staleness
  guard and the deferred erase on delete are internally consistent, and all emulated paths hold
  `emu_mutex`.
- **`list`** (both dialects, `:858-931`) — `limit == 0` returns empty, `next_cursor` is set only when
  a further in-prefix key exists, the cursor is applied as an exclusive `start_after` with a
  belt-and-braces `lk.key <= cursor` skip, and the prefix is re-verified per key. `ListedKey::token`
  is populated because `iterate`'s third parameter is `with_tags` (not `with_metadata`) and
  `getObjectInfoIfExists` is called with `with_metadata = true`, so `supportsListTokens()` is not
  over-promising.
- **`resurrect`'s byte accounting** (`:814-856`) — both dialects verify the streamed payload length
  against the declared size and abort the upload before publishing on mismatch; the native path
  re-heads and fails closed if the blob is absent afterwards.
- **`readManifestShared`** (`CasManifestReader.cpp:54-126`) — HEAD-then-GET is safe here because the
  body is independently validated against the journal `ManifestRef` (`refMatchesBody`) and the owning
  namespace (`manifestNamespaceMatches`) before it is cached, and the decode cache is keyed on
  (manifest id, token) so a rewritten object cannot serve a stale decode.
- **`PoolMeta::createOrValidate` / `admitOrValidate`** (`CasPoolMeta.cpp:57-127`) — validates
  `blob_header_len` and `gc_shards` before any store access, refuses to mint outside the verified
  bootstrap path when `allow_mint` is false, requires the explicit `blob_hash_allow_new` opt-in to
  widen `algos_used`, and re-reads on CAS conflict. The admission loop converges because each
  iteration either returns or observes a strictly more admitted set.
- **`validateServerRootId`** (`CasServerRoot.h:104-134`) — rejects empty, over-long, empty-segment,
  `.`/`..` and the reserved `_files` / `_manifests` segments, and is invoked both from settings
  validation and from `mountWritable`.
- **`CasBlobUploadPool`** — double-initialisation and use-before-initialisation both throw
  `LOGICAL_ERROR`; a zero size is rejected; all four entry points hold `pool_mutex`.
- **`InstrumentedBackend`** — every override forwards before counting, so a throwing inner call is not
  counted as a success, and `InstrumentedWriteSink` preserves the `cancel()`-on-destruction contract.
- **`InMemoryBackend`** — every method holds `mutex_`; `applyDelete` is the single mutation point
  shared by the immediate and held-delete paths; `list`'s cursor handling matches the real backend's.
- **`EventDispatcher::emit`** (`CasEventDispatcher.cpp:17-44`) — the `draining` re-entrancy guard
  prevents unbounded recursion when a sink emits, and a throwing sink is logged and the event dropped
  rather than propagating into a fence path. *Caveat, not reported as a finding because no shipped
  caller can trigger it:* `sink` is read at `:33` with the lock released, while `setSink` mutates it
  under the lock — a race if `setEventSink` is ever called after threads start. Today both callers
  (`CasPool.cpp:358`, `:554`) run before any pool thread exists.

## Coverage

- **Complete, line-by-line:** every file listed in the "Region walked" table was read in full, in
  order, including headers. That is the whole of `Backend/` and the whole of the tier2 slice of
  `Pool/`, plus `ContentAddressedSettings.cpp`.
- **Read only as far as needed to close a question:** `ContentAddressedSettings.h`,
  `CasPlainObjects.h`, `CasInMemoryBackend.h`, `CasProbe.h`, `CasSentinelProbe.h` (declarations
  consistent with the reviewed definitions); `Primitives/CasTypes.h` (Token / TokenType /
  `renderRefTxnId` only); `Formats/CasServerRootFormats.h` and `CasPoolMetaFormat.h` were **not**
  read, so the reachability of `next_writer_epoch == 0` in tier2-12 rests on the struct-default
  behaviour visible at `CasServerRoot.cpp:226` rather than on the decoder — the asymmetric
  normalisation is the defect regardless.
- **Cross-tree verification performed** (needed to confirm tier2-1, tier2-7, tier2-8): the S3 write
  buffer's `If-Match` gating, `WriteBufferFromFileBase::getResultObjectETag`'s default,
  `getObjectInfoIfExists`'s error policy, `S3ObjectStorage::removeObjectIfTokenMatches`,
  `IObjectStorage::iterate`'s parameter meaning, and `MetadataStorageFactory`'s `config_prefix`.
- **Explicitly not covered by tier2:** `CasRefLedger.*`, `CasRefProtocol.*`, `CasRefCatalog.*`,
  `CasRefCkpt.*`, `CasRefCow*.*`, `CasPartWriteTxn.*` (except the epoch check at line 125),
  `Gc/**` (except the two `computeHeartbeatFloor` call sites), `Formats/**`, `Primitives/**`,
  `Parts/**`, `Tools/**`, `ContentAddressedMetadataStorage.*`, `ContentAddressedTransaction.*`.
- **Not attempted:** no build, no execution, no test run — static reasoning only, as instructed. All
  CAS tests are deleted in this working tree, so no finding below is corroborated or contradicted by
  a test.
- **Confidence note.** tier2-1 through tier2-6 and tier2-9 through tier2-12 are anchored in shipped
  code with a concrete trigger. tier2-7 and tier2-8 are anchored in the absence of code (no setting
  declaration, no allow-list entry), which I verified by grepping every assignment to
  `cas_request_budget`, `mount_lease_ttl_ms` and `mount_renew_period` across `src/` — all hits are
  reads.

# tier1 (deep sweep: ref ledger and catalog core) -- fresh audit 2026-08-12

## Scope and tier definition

Target (read-only, working tree as-is): `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch
`cas-code-only-strip`, base `842f2b37b8f`. CAS root
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

This is one of four *tier* audits in the 39-audit re-run. Where the angle audits followed one protocol
across many files, a tier audit walks whole files line by line. **Tier1 = the ref ledger and catalog
core**: the in-memory ref table representation, transaction apply/replay, admission budgets, the append
lane (leader/batching/wedge/fault states), `_ckpt` checkpoint publication, snapshot publication and
pruning, catalog rows and their lifecycle transitions, and the recovery walk.

Code-only rule observed: `docs/**` is deleted in the working tree and was not consulted; comments were
read but not treated as intent. Shipped user-visible strings (exception messages, log lines) *are*
treated as the specification. All CAS tests are deleted in the working tree, so every claim below is
static reasoning over shipped code only.

Sibling findings cited, not re-derived: `removal_admission_closed` latching admission closed after a
failed `dropNamespace`; `leader_active` released non-RAII; unbounded ref-table cache growth; snapshot
re-encode every 256 txns; namespaces stranded in `Removing`; forked chains under two writer epochs.

## Region walked

| File | Lines | Functions / regions reviewed |
| --- | --- | --- |
| `Pool/CasRefLedger.cpp` | 1–3607 (all) | file-local helpers (`isTransientRecoveryError`, `chainLinkFor`, `makeEpochSealTxn`, `classifyRefLogOccupant`, `clampedCounterSub`), ctor + retry-sleep closure, `stagingPutIfAbsent/ConditionalCreate/ConditionalOverwrite/PutIfAbsentMutable`, `resolveRef`, `listRefs`, `hasAnyRefWithPrefix`, `confirmExactRef`, `lookupRefTableRuntime`, `acquireRefTableRuntime`, `acquireReadableRefTableRuntime`, `acquireMutableRefTableRuntime`, `invalidateRemovedCatalogLife`, `reconcileCatalogCut`, `checkRecoveryStillAdmitted`, `runRecoveryWalkOnce`, `resolveNamespaceLife`, `ensureRefTableRecovered`, `installRecoveryResult`, `cancelRecoveriesAndAwaitQuiescence`, `enforceRefTableCacheBudget`, `quiesceRefTablesForRemount`, `wedgedRefLaneCount`, `drainRefLanesForShutdown`, `appendRefOps`, `appendRefOpsOnRuntime`, `runRefQueueLeader`, `completeOwnedItemsAndReleaseLeadership`, `requireRecovery`, `resolveWedgeOnce`, `flushRefBatch`, `prepareRefChunk`, `commitRefChunk`, `hasStateBearingSnapshotCandidateUnderStateLock`, `admitSnapshotPublishUnderStateLock`, `dispatchSnapshotPublisher`, `settleSnapshotPublish`, `maybeScheduleSnapshotPublish`, publish/sweep backoff pairs, `publishCkptContribution`, `tryPublishSnapshotAndAdvanceCheckpointOnce(OnRuntime)`, `sweepStalePrecommitsForRead`, `maybeSweepStalePrecommits`, `sweepStalePrecommitsNow`, `dropRef`, `updateRefPublishedAt`, `namespaceLife`, `namespaceFilesLifeIfReadable`, `namespaceStillLogicallyPresent`, `dropNamespace`, `dropNamespaceImpl`, plus all `*ForTest` accessors |
| `Pool/CasRefLedger.h` | 1–545 (all) | `RefLaneState`, `RefTableRuntime` field set and its lock discipline, `RefNameSlot`, constants (`kMaxRefBatch`, `kRefRecoveryMaxRestarts`, `kRefRecoveryMaxSlotAttemptsPerEpoch`, `kRefAdmissionSafetyMargin`), `RefAppendAttempt`, `PreparedRefChunk`, `allocateRefTxnId` |
| `Pool/CasRefProtocol.cpp` | 1–868 (all) | `CatalogLifeIndex` (ctor/`resolve`/`isAmbiguous`/`throwIfAmbiguous`), `checkRemoveNamespaceOrdering`, `classifyOwnerTransitionShape`, replay memory probe, `decodedRefLogTxnFootprint`, `RefTableState::swap`, `manifestAlreadyOwned`, `applyOwnerTransition` (all 4 shapes), `applySetPublishedAt`, `applyOp`, `stateFromSnapshot`, `debugAssertBodyCounters`, `applyTxnInPlace`, `nextRefTxnId`, `applyRefLogTxn`, `snapshotOf`, `replay`, `RefReplayBuilder`, `encodedSnapshotBudgetSize`, `encodedRemovalBudgetSize`, `admits`, `manifestEdgesOfTxn`, `removalTxnId`, `groupRefKeys`, `planRefCleanup`, `crossEpochFromSeal`, `nextRefLogIdWithinCommittedFrontier`, `readCheckpointSnapshotBase`, `recoverRefTableDetailedFromAuthority` |
| `Pool/CasRefProtocol.h` | 1–327 (all) | `RefTableState` interface, `RefLedgerConfig` defaults, `RecoveryResult`, `RefCleanupPlan`, `EpochCross*` |
| `Pool/CasRefCatalog.cpp` / `.h` | 552 / 139 (all) | `readOptionalForBootstrap`, `read`, `initializeEmptyForNewPool`, `lifeIfCataloged`, `liveUniverse`, `casUpdateImpl`, `mintFreshIncarnation`, `findEntry`, `createNamespaceStep1`, `casUpdate`, `casAdmitEntry`, `beginRemoving`, `deleteCompletedRemoving`, `deleteCompletedRemovingAtSnapshot`, `cancelStalledCreating`, `completeCreation`, `createNamespace`, `reconcileStaleCreator`, `checkPublicationAdmittedOrThrow` |
| `Pool/CasRefCkpt.cpp` / `.h` | 254 / 64 (all) | `maxKnown`, `mergeCommittedThrough`, `lifeEpochWouldDecrease`, `throwLifeEpochDecrease`, `mergeCkpt`, `chooseRecoveryGrounding`, `readCkpt`, `publishCkpt`, `classifyMissingSampledBase`, `snapshotDeletableUnderCkpt` |
| `Pool/CasRefCowMap.cpp` / `.h` | 221 / 104 (all) | iterator `operator*`/`normalize`/`operator++`, `begin`/`end`/`find`/`at`, `insertLive`, `emplace`, `insert_or_assign`, both `erase` overloads, `operator==`, `materialize` (in-place and copy), `swap`, `net_delta` accounting |
| `Pool/CasRefCowManifestSet.cpp` / `.h` | 103 / 49 (all) | `contains`, `insert`, `erase`, `materialize` |
| `Formats/CasRefLogFormat.cpp` / `.h` | 399 / 71 (all) | op-kind vocab, `checkBudget`, `writeOp`/`readOpRecord`, `writeLogMeta`, `refLogTxnIsEpochSeal`, `validateEpochSealGrammarStructural`, `validateEpochSealGrammarContextual`, `encodeRefLogTxn`, `decodeRefLogTxn`, `encodedOpSize`, `refLogTxnIsRemovalClass`, `removalOpEncodedSize`, `removalFramingSize` |
| `Formats/CasRefCatalogFormat.cpp` | 360 (all) | `nsStateToWord/FromWord`, `creatorPairingOk`, `removalRoundPairingOk`, `isCanonicalCatalogOrder`, `encodeRefCatalog`, `decodeRefCatalog`, `checkCatalogObjectBytes`, `foldSealFixedBytes`, `worstCaseEntryFoldReservationBytes`, `widestBlobTargetRunReservationBytes`, `widestCondemnedSummaryReservationBytes`, `checkFoldSealReservation`, `checkCatalogAdmission` |
| `Formats/CasRefCkptFormat.cpp` | 146 (all) | `checkRefCkptInvariants`, `encodeRefCkpt`, `decodeRefCkpt` |
| `Formats/CasRefSnapshotFormat.cpp` | 286 (all) | sortedness checks, `checkSnapshotInvariants`, row writers, `encodeRefTableSnapshot`, `decodeRefTableSnapshot`, `committedRowEncodedSize`, `precommitRowEncodedSize`, `snapshotFramingSize` |
| Corroborating reads (outside the tier, used to confirm/refute) | — | `Backend/CasRequestControl.cpp` (`resolveByExactGet`, `putIfAbsentControlled`, `putIfAbsentControlledMutable`, `slotOccupy` entry), `Pool/CasMountRuntime.{h,cpp}` (fence generation, `armMountFence`, `tripMountLost`, `scheduleRemount`), `Pool/CasPool.cpp` (self-remount ordering, teardown, `resolveRef` forwarding), `Pool/CasServerRoot.cpp` (`allocateWriterEpoch`), `Gc/CasGc.cpp` (`planRefCleanup` call site), `Parts/PartFolderAccess.cpp` (`resolve`, `dropRefIfPresent`) |

## Findings

### tier1-1 -- Read path answers "the namespace/ref is absent" while removal admission is merely closed, including when the removal is rolled back (High)

- **Anchor**: `Pool/CasRefLedger.cpp:394-398` (`acquireReadableRefTableRuntime` returns `nullptr` when
  `removal_admission_closed`), consumed by `resolveRef` `:217-219`, `listRefs` `:263-265`,
  `hasAnyRefWithPrefix` `:283-285`, `namespaceFilesLifeIfReadable` `:3308-3311`. The latch is set at
  `:3451-3458` and can be *cleared again* at `:3534-3536`.
- **Trigger**: `dropNamespaceImpl` sets `rt->removal_admission_closed = true` and then waits for the
  append queue to drain (`:3452-3457`) — this happens *before* any catalog transition
  (`beginRemoving` is only reached at `:3492`). While that window is open the catalog row is still
  `Live` and every committed ref is still durable. A concurrent reader
  (`CachedPartFolderAccess::resolve` / `existsRef`, `Parts/PartFolderAccess.cpp:283,286-289`) gets a
  `nullptr` runtime and therefore `std::nullopt`. If `beginRemoving` then fails and the code rolls the
  latch back at `:3535`, the namespace was never removed at all, yet readers were already told the
  refs do not exist.
- **Consequence**: a *negative* (hard "absent") answer instead of the retry-later that every other
  admission refusal on this class uses (compare `appendRefOpsOnRuntime:1427-1430` and
  `namespaceLife:3272-3275`, which both `throwCasWriteRetryLater` with "is Removing … retry later").
  Callers cannot distinguish "gone" from "busy": `existsRef` reports false and
  `dropRefIfPresent` (`Parts/PartFolderAccess.cpp:483-487`) takes its "nothing to drop" branch, so a
  live part can be treated as non-existent. Combined with the sibling finding that a failed
  `dropNamespace` leaves this latch permanently closed, the wrong-negative becomes permanent for the
  process lifetime rather than a race window.
- **Evidence**: the same predicate is read under `ref_queue_mutex` in three places with three different
  answers — `nullptr`/absent on the read path (`:396-397`), retry-later on the mutate path
  (`:1427-1430`, `:1451-1454`), and retry-later in `namespaceLife` (`:3268-3275`). The rollback at
  `:3535` proves the latch is not a terminal state, so treating it as proof of absence is unsound.

### tier1-2 -- `RefLaneState::Closed` is a terminal state with no exit, contradicting its own shipped message (Medium)

- **Anchor**: `Pool/CasRefLedger.cpp:2501-2515` (append path) and `:1766-1772` (wedge path) set
  `rt->lane_state = RefLaneState::Closed`. No code anywhere transitions *out* of `Closed`:
  `ensureRefTableRecovered` re-runs recovery only for `NeedsRecovery` (`:962-967`), and
  `installRecoveryResult` — the only writer of `RefLaneState::Ready` (`:1120`) — is reachable only
  through that path.
- **Trigger**: a successor's epoch seal occupies the id this table derived
  (`classifyRefLogOccupant` → `Occupant::SuccessorSeal`). The lane is closed and every later
  `flushRefBatch` short-circuits in `resolveWedgeOnce` at `:1587-1620`
  (`lane_state != Wedged` → `invalid_lane_state` → `INVALID_STATE`), so all subsequent mutations of
  that namespace fail on this cached runtime.
- **Consequence**: the shipped exception text asserts "This mount's append lane resumes only under a
  later epoch" (`:1833-1837`, `:2511-2514`), but there is no code path that resumes it: a later epoch
  neither re-recovers nor rearms the lane. The runtime is also un-evictable, because
  `enforceRefTableCacheBudget` skips any slot whose `lane_state != RefLaneState::Ready`
  (`:1199-1200`), so the dead entry is pinned in `ref_name_slots` as well. Recovery of that namespace
  depends entirely on an unrelated event (self-remount, which clears the map at `:1244`, or process
  restart).
- **Evidence**: exhaustive writer set for `lane_state`: `Ready` at `:1120`, `:1801`, `:2614`, `:2674`,
  `:2694`; `Writing` at `:2437`; `Wedged` at `:2467`, `:2710`, `:1311`; `NeedsRecovery` only via
  `requireRecovery` `:1546`; `Faulted` at `:1776`, `:2367`, `:2491`, `:2521`; `Closed` at `:1770`,
  `:2508`. Every `Ready` writer other than `installRecoveryResult` requires the lane to already be
  `Writing`/`Wedged`, so `Closed` (like `Faulted`) is absorbing.

### tier1-3 -- Recovery must seal every skipped writer epoch one at a time, so first touch of an idle table costs O(mount generations) durable writes with no cap (Medium)

- **Anchor**: `Pool/CasRefLedger.cpp:740-824` (the per-epoch seal loop: `slotOccupy` at `:772-774`,
  then `publish_recovered_frontier` at `:783`, which itself does a `_ckpt` CAS plus an exact re-read,
  `:599-625`), driven by `chainLinkFor` `:101-106`; the density requirement is enforced by
  `Formats/CasRefLogFormat.cpp:239-246` (`prev_epoch_seal->writer_epoch + 1 != txn_id.writer_epoch`
  is `CORRUPTED_DATA`).
- **Trigger**: writer epochs are minted per mount from a single durable counter for the whole server
  root (`Pool/CasServerRoot.cpp:161-…`, `next_writer_epoch`), while the seal chain is per namespace.
  A namespace last written at epoch `E` that is first touched again when the pool is at epoch `E+N`
  must be walked: for each of the `N` dead epochs the recovery writes a seal object, publishes a
  `_ckpt` contribution and re-reads `_ckpt` to certify it (`:783-788`).
- **Consequence**: the first write (or read — see tier1-4) to a long-idle namespace performs `~3-4N`
  object-store round trips and leaves `N` seal log objects for GC, where `N` grows with every server
  restart/remount for as long as the namespace stays idle. There is no fast-forward and no bound: the
  only limits in the loop are per-epoch (`kRefRecoveryMaxSlotAttemptsPerEpoch`, `:751`) and the
  transient-error budget (`:1064`), neither of which caps `N`. A single operation deadline
  (`cas_request_budget.operation_deadline_ms`) is applied per `publishCkpt` call, not to the walk, so
  the caller simply blocks for `N` sequential round trips.
- **Evidence**: the loop advances strictly one epoch per iteration in all three exits
  (`:685-690`, `:701-706`, `:785-787`) and the non-Live shortcut at `:743-749` still costs one `GET`
  per epoch; nothing in the region collapses a run of dead epochs into a single seal, and the log
  grammar at `Formats/CasRefLogFormat.cpp:243-246` makes such a collapse impossible without a format
  change.

### tier1-4 -- `resolveRef`'s `allow_stale` argument is silently dropped, so "cached/stale-tolerant" reads still recover (and can throw) (Medium)

- **Anchor**: declaration `Pool/CasRefLedger.h:62-63` (`bool allow_stale = false`) vs definition
  `Pool/CasRefLedger.cpp:214-215`, where the parameter is unnamed (`bool  ,`) and never read. The
  value is threaded all the way down from `Pool/CasPool.cpp:1135-1137`.
- **Trigger**: `Parts/PartFolderAccess.cpp:283` passes `freshness == Freshness::CachedForLoad` and
  `:483` passes a literal `true`, i.e. callers explicitly request a stale-tolerant resolve. Because the
  flag is discarded, both take the strict path: `acquireReadableRefTableRuntime` (`:217`), which can
  `throwCasWriteRetryLater` when the cached life was detached (`:399-403`) or when the catalog moved
  under a cold reader (`:421-429`), followed by `ensureRefTableRecovered` (`:220`), which performs
  *durable* writes (epoch seals, `_ckpt` CAS — see tier1-3), and `sweepStalePrecommitsForRead`
  (`:221`) plus `maybeScheduleSnapshotPublish` (`:222`).
- **Consequence**: a read that the caller declared insensitive to staleness can fail with a
  retry-later error, block on a full recovery walk, or emit durable writes. `dropRefIfPresent`
  (`Parts/PartFolderAccess.cpp:481-487`) becomes a write-amplifying, throw-capable probe instead of a
  cheap existence check. The dropped parameter also means no code path in the shipped tree can ever
  produce a stale read, so the API contract is unimplemented rather than merely unused.
- **Evidence**: `resolveRef` has exactly one use of its third parameter — none; the only other
  read-side freshness lever, `ResolveAudit`, *is* honoured (`:239-250`), which shows the omission is
  specific to `allow_stale`.

### tier1-5 -- `enforceRefTableCacheBudget` re-reads concurrently mutated byte counters, so `total` can underflow and evict every evictable table (Low)

- **Anchor**: `Pool/CasRefLedger.cpp:1158-1167` computes `total` from
  `base_snapshot_bytes + tail_bytes_since_snapshot`; `:1182` re-reads the same atomics into
  `Cand::weight`; `:1204` does `total -= c.weight` on a `uint64_t`.
- **Trigger**: both reads happen under `ref_queue_mutex`, but the counters are `std::atomic<uint64_t>`
  mutated by threads that hold only `state_mutex` — `commitRefChunk` (`:2611-2612`), the wedge install
  (`:1798-1799`) and the snapshot publisher (`:3064-3068`). If a table's tail grows between the two
  reads, `c.weight` exceeds that table's contribution to `total`.
- **Consequence**: `total -= c.weight` wraps to a value near `2^64`, so the `total <= cache_bytes`
  break at `:1189-1190` never fires and the loop evicts every remaining candidate regardless of the
  configured budget. Effect is a cache stampede (each evicted namespace pays a full recovery walk on
  next touch — see tier1-3), not corruption.
- **Evidence**: the weight is captured once at `:1182` and reused at `:1204` without re-reading, while
  the eviction re-validates *everything else* it cares about (`use_count`, `leader_active`, `pending`,
  `lane_state`) at `:1198-1203` — the arithmetic is the one thing not re-validated.

## Checked and sound

Recorded so the sweep's negative coverage is auditable.

- **Apply/replay core** (`CasRefProtocol.cpp`): `applyTxnInPlace` enforces strict monotonicity
  (`:390-394`) *and* contiguity (`:396-402`) and validates seq-1 grammar with a lifecycle-aware
  `life_epoch` (`:404-406`); `applyRefLogTxn` is copy-then-swap, so a rejected txn cannot leave a
  half-applied state (`:425-430`). `RefReplayBuilder::applyOne` pins the namespace on first txn
  (`:484-488`). `checkRemoveNamespaceOrdering` correctly special-cases the `[birth, remove]`
  never-born shape (`:87-88`).
- **Owner-transition shapes**: all four shapes are exhaustively classified with an explicit throw for
  anything else (`:112-137`); every mutation keeps `snapshot_body_bytes`, `removal_body_bytes` and
  `owned_manifests` in step, and `Promote` correctly leaves `owned_manifests` untouched (`:248-267`).
  `applySetPublishedAt` updates only the snapshot counter, which is right because
  `removalOpEncodedSize` does not depend on `published_at_ms`.
- **Budget accounting**: `encodedSnapshotBudgetSize`/`encodedRemovalBudgetSize` deliberately frame with
  an empty ns and a `{1,1}` preview id, and the ledger compensates with
  `overhead = 4 + ns.size() + kRefAdmissionSafetyMargin` when deriving the budgets
  (`CasRefLedger.cpp:859-861`), with the subtraction guarded against underflow.
- **`RefCowMap` / `RefCowManifestSet`**: `net_delta` accounting was re-derived for every path
  (insert over tombstone, erase of overlay-only key, erase of base key, both `materialize` branches)
  and is exact; the in-place `materialize` is taken only when `base.use_count() == 1`, so a shared
  base is never mutated under another copy; iterator `normalize`/`operator++` correctly suppress
  tombstones and skip the shadowed base row; `erase(const_iterator)` advances before mutating, and the
  only `overlay.erase` case cannot invalidate the advanced iterator.
- **`_ckpt` merge and invariants**: `mergeCkpt` is monotone per field; `mergeCommittedThrough` refuses
  a cross-epoch jump unless the higher side carries a seal that covers the lower frontier
  (`CasRefCkpt.cpp:34-53`); `checkRefCkptInvariants` ties `last_epoch_seal` to `committed_through`'s
  immediately preceding epoch (`CasRefCkptFormat.cpp:48-60`). I traced the steady-state sequences
  (mid-epoch commits, first commit of a new epoch, recovery seals, snapshot contributions) and each
  merge satisfies the invariant; `life_epoch` is never taken as a maximum downwards
  (`CasRefCkpt.cpp:55-70`).
- **`publishCkpt` ambiguity handling**: an ambiguous `casPut` is resolved by a mandatory exact re-read,
  and "our contribution is already subsumed" is correctly reported as `Published`
  (`CasRefCkpt.cpp:197-233`); the deadline break falls through to a retry-later, never to a silent
  success.
- **Recovery grounding null-safety**: the several unguarded `sampled_ckpt->…` dereferences in
  `runRecoveryWalkOnce` (`:572`, `:577`, `:715`, `:724-727`, `:760-761`) are safe because
  `chooseRecoveryGrounding` throws for a `Live`/`Removing` namespace without a readable `_ckpt`
  carrying `life_epoch` (`CasRefCkpt.cpp:93-96`) and runs first (`:540-542`).
- **Recovery restart/retry control**: the vanish brake distinguishes a persistent stream hole
  (`CORRUPTED_DATA`) from a vanishing snapshot (retry-later) (`:1002-1015`); the transient-error retry
  re-checks fence, generation, catalog invalidation and supersession both before and after sleeping
  (`:1063-1100`); the exponential backoff shift is guarded against UB (`:1073-1075`); the lock is
  re-acquired on every throw path across the `unlock`/`lock` seams (`:1022-1034`, `:1084-1094`).
- **Append-lane liveness**: `runRefQueueLeader` cannot spin — every carve selects at least one item
  when `pending` is non-empty, and every carved item is completed on all paths
  (`flushRefBatch:2115-2118`, `:2183-2186`, `:2188-2200`; `commitRefChunk` completes
  `chunk_survivors` on all six `return false` paths and on success);
  `completeOwnedItemsAndReleaseLeadership` fails owned items closed rather than stranding them
  (`:1519-1541`).
- **Batching vs removal class**: a `WholeShard`-scoped item (which is what `dropNamespaceImpl` and the
  precommit sweep use) can never share a chunk with ref-scoped items (`:2043-2052`), so the terminal
  removal chunk cannot be poisoned by unauthorized siblings — the
  `all_of(terminal_removal_authorized)` guard at `:2277-2281` is defence in depth, not a live failure.
- **Wedge resolution**: the durable-then-install sequence re-verifies the exact wedge identity
  (id, bytes and admitted generation) before and after frontier publication (`:1657-1691`), the
  install region is `DENY_ALLOCATIONS_IN_SCOPE` + `static_assert(nothrow_swappable)` so the
  proven-durable hand-off cannot throw (`:1787-1807`), and every non-adopted outcome carries a
  precise reason string. A post-install `materializeCommitted` failure is retained coherently rather
  than losing the install (`:1810-1821`, `:2623-2633`).
- **Self-remount ordering**: `CasPool.cpp:730-734` publishes the new live epoch before arming the new
  fence and before `quiesceRefTablesForRemount`, which looks like a window where a writer could derive
  an id in the new epoch under the old admitted generation — it is closed because every remount path
  runs `tripMountLost()` first (`CasMountRuntime.cpp:212-218`, `CasPool.cpp:989-990`), so
  `mayMutate()` is false and `checkFenceOrThrow` refuses throughout the window.
- **Snapshot publication**: `putIfAbsentControlled` is idempotent for byte-identical objects via
  `resolveByExactGet` (`CasRequestControl.cpp:212-238`), so re-publishing the same snapshot after a
  crash between body and `_ckpt` converges; the publisher refuses to snapshot a non-`Ready` lane
  (`:2956-2978`), drops its captured state copy before the encode/PUT (`:2992-2995`), and re-checks
  admission before mutating tail counters (`:3057-3069`); `clampedCounterSub` cannot wrap.
  `pending_snapshot_publishes` is incremented under the state lock before dispatch and decremented on
  the dispatch-failure path, and the re-dispatch loop in `settleSnapshotPublish` is gated on
  `may_mutate()`, so `quiesceRefTablesForRemount`/`dropNamespaceImpl` waiters cannot be starved.
- **Ref-log format**: `decodeRefLogTxn` re-validates ns/id against the key it was read from
  (`:324-329`), rejects retired fields, enforces the trailer count and both structural and budget
  checks; `validateEpochSealGrammarStructural` requires `prev_epoch_seal->writer_epoch + 1 ==
  txn_id.writer_epoch`, which is what makes `crossEpochFromSeal` terminate (`target_epoch` strictly
  decreases each iteration, `CasRefProtocol.cpp:649-687`) — I specifically checked that loop for a
  same-epoch `prev_epoch_seal` spin and it is unreachable through the decoder.
- **GC/recovery interlock on log pruning**: `planRefCleanup` retains the checkpoint-named base log
  (`*checkpoint <= log_id`) and its predecessor seal via `retained_log_proof`
  (`CasRefProtocol.cpp:615-624`), and the GC call site actually supplies that proof from
  `readCheckpointSnapshotBase(...).predecessor_seal_id` (`Gc/CasGc.cpp:2381-2395`), so the two objects
  `readCheckpointSnapshotBase` requires cannot be pruned out from under recovery.
- **Catalog transitions**: `casUpdate` refuses row-identity changes (`CasRefCatalog.cpp:181-198`);
  `beginRemoving`/`cancelStalledCreating`/`reconcileStaleCreator`/`completeCreation` all re-verify the
  exact observed row inside the CAS mutate closure and re-check the fence there, and each maps
  interference to a distinct outcome; `deleteCompletedRemovingAtSnapshot` resolves an ambiguous erase
  by a complete re-read and refuses to report `Deleted` while the incarnation is still cataloged
  (`:361-382`); `CatalogLifeIndex` refuses to resolve a life id shared by two namespaces; the encoder
  enforces canonical ordering, `creator`/`removal_started_round` pairing and both object-cap
  predicates (catalog bytes and worst-case fold-seal reservation) before any write.
- **Shutdown latch**: `shutting_down` is set only by `drainRefLanesForShutdown`, whose sole callers are
  `Pool::~Pool` and `Pool::forgetDisk` (`CasPool.cpp:566`, `:594`) — both terminal, so the one-way
  latch is correct.
- **Read fencing**: `resolveRef`/`listRefs`/`hasAnyRefWithPrefix` all call `ensureRefTableRecovered`
  first, so a `NeedsRecovery` lane cannot serve a table that is known to be missing a durable txn;
  `confirmExactRef` refuses (`Unknown`) unless the lane is `Ready`, the queue is empty, no recovery is
  in flight and the fence is still held, and re-checks the fence after reading the row
  (`:298-333`).

## Coverage

- Lines read line-by-line in the tier region: 3607 + 545 (`CasRefLedger`), 868 + 327
  (`CasRefProtocol`), 552 + 139 (`CasRefCatalog`), 254 + 64 (`CasRefCkpt`), 221 + 104 (`CasRefCowMap`),
  103 + 49 (`CasRefCowManifestSet`), 399 + 71 (`CasRefLogFormat`), 360 (`CasRefCatalogFormat`), 146
  (`CasRefCkptFormat`), 286 (`CasRefSnapshotFormat`) — **8095 lines, 100% of the named region**, plus
  targeted reads in `CasRequestControl`, `CasMountRuntime`, `CasPool`, `CasServerRoot`, `CasGc` and
  `PartFolderAccess` to confirm or refute candidate findings.
- Every function in the region is accounted for above: 5 confirmed findings (1 High, 3 Medium,
  1 Low) and 20 groups explicitly walked and found sound.
- Candidates raised and **refuted** during the sweep (so they are not re-opened): unguarded
  `sampled_ckpt` dereferences in the recovery walk; a same-epoch `prev_epoch_seal` infinite loop in
  `crossEpochFromSeal`; `net_delta` drift in either COW container's in-place `materialize`; loss of the
  base snapshot's predecessor seal to GC; a non-idempotent snapshot republish after a crash between
  body and `_ckpt`; a leader spin in `runRefQueueLeader`; a terminal-removal chunk batched with
  unauthorized positive items; a new-epoch id derived during the self-remount window; starvation of the
  `pending_snapshot_publishes == 0` waiters by publisher self-re-dispatch; an aggregate byte-cap
  bypass through the per-op admission caps (`5000 * 4096 = 20,480,000` bytes stays under the
  20,971,520-byte transaction cap with ~480 KB of framing headroom, and the batching split bounds op
  count, so the caps do compose).
- Not covered by this tier (belongs to other audits): the GC fold/condemn protocol beyond the two
  ref-cleanup call sites checked here, blob and manifest paths, `ContentAddressedTransaction`, mount
  lease/keeper internals, and the `Tools`/`benchmarks` subtrees.

# concurrency -- fresh audit 2026-08-31

## Scope

- In-process races assigned by the brief: GC scheduler join, remount vs renew
  (`ceee42c` + `7f932d3`), fence/epoch, ref-lane leadership, snapshot-publish
  pending count, `shared_from_this`, DataPartsLock vs I/O.
- Files/dirs examined at `ceee42c51a06cb05e2c9a2d811ef7e1726825552`:
  `Gc/CasGcScheduler.{h,cpp}`, `ContentAddressedMetadataStorage.{h,cpp}`
  (`requestGcRoundSoon` / `shutdown` / `gcStop` / `stopAndDrainForTeardown`),
  `Pool/CasMountRuntime.{h,cpp}`, `Pool/CasServerRoot.{h,cpp}`,
  `Pool/CasRefLedger.{h,cpp}` (lane queue, `admitSnapshotPublishUnderStateLock`,
  `dispatchSnapshotPublisher`, `quiesceRefTablesForRemount`),
  `Pool/CasPool.{h,cpp}` (`tryDispatchDetached` / `~Pool`),
  `Pool/CasDetachedWork.{h,cpp}`, `src/Common/ThreadPool.h` (`ThreadFromGlobalPool`),
  `src/Storages/MergeTree/MergeTreeData.cpp` (`removePartsInRangeFromWorkingSet`
  empty covering part).
- Explicitly out of scope: cross-node interleavings (`jepsen-anomaly`,
  `interleaving`); GC protocol semantics; lock-hold latency as a performance
  finding except where it is the race mechanism.

## Findings

### concurrency-1 -- GC scheduler joins thread handles outside the mutex that guards them (Medium)

- Anchor: `Gc/CasGcScheduler.cpp:75-85` (`stop`), `:95-104` (`requestRoundSoon`),
  `:65-72` (`start`); caller `ContentAddressedMetadataStorage.cpp:426-434`
  (`requestGcRoundSoon`) at ceee42c
- Trigger: thread A runs `SYSTEM CAS DROP POOL MEMBER` (or any other
  `requestGcRoundSoon` site). That method snapshots `gc_scheduler` under
  `pointer_mutex` only (`:429-434`) and then calls `requestRoundSoon()`, which
  reads `thread.joinable()` **under** `mutex` (`:99`). Thread B concurrently
  runs `shutdown` / `gcStop` / `~CasGcScheduler`, all of which call `stop()`.
  `stop()` sets `stopping` under `mutex` (`:78-80`) then evaluates
  `thread.joinable()` / `thread.join()` and the same pair for `hb_thread`
  **with no lock held** (`:82-85`).
- Evidence: `ThreadFromGlobalPool::joinable()` is `initialized()` =
  `static_cast<bool>(state)` (`src/Common/ThreadPool.h:410-413`, `:426-429`).
  `join()` ends with `state.reset()` (`:400`). Those are a non-atomic
  `shared_ptr` read and write on the same member. The scheduler's `mutex` is
  still the declared synchronisation point for the handles (`start` and
  `requestRoundSoon` take it). The snapshot in `requestGcRoundSoon` keeps the
  object alive, so this is a data race on the handle, not a use-after-free of
  the scheduler. `hb_thread` has the same unguarded join and is not covered by
  the `thread.joinable()` early-return in `start`.
- Notes: same root cause as CAS-050. Not High: no evidence of a silent
  committed-state corruption; the practical outcome is UB on the thread
  object. The "joinable-but-dead scheduler that reports itself running" half
  from 2026-08-12 is not re-raised (self-exit still leaves the object
  joinable, but `requestRoundSoon` then no-ops on `stopping`).

### concurrency-2 -- empty covering part publishes a CA ref while holding DataPartsLock (Low)

- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:5884-5983`
  (`removePartsInRangeFromWorkingSet`) at ceee42c
- Trigger: `DROP`/`REPLACE PARTITION` on a CA table (new-syntax, non-MVCC,
  range starting at block 0). The caller already holds `DataPartsLock`. The
  function then `createEmptyPart` (directory + file I/O),
  `renameTempPartAndAdd(..., lock, rename_in_transaction=false)`, and — only
  for CA — `commitTransaction()` (`:5978-5980`) which runs the full
  stage/precommit/blob/promote path against the object store.
- Evidence: `commitTransaction` is network I/O under the table's parts lock.
  Every concurrent merge, fetch, SELECT that takes `lockParts()`, and any
  second partition command, blocks for the duration of that publish. The
  comment at `:5961-5977` states this call is the only thing that makes the
  covering ref durable. An ordinary object-storage disk already renamed
  under the same lock; CAS adds a multi-RTT publish.
- Notes: same shape as CAS-048. Rare path, work is one empty part, failure
  is loud. Scored Low: stall / lock-order pressure, not a data race and not
  a committed-state bug.

## By-design / info / non-actionable

- **Remount vs renew is now a single driver-state machine.** `admitKeeperCall`
  requires the expected `RenewalDriverState` and `MountLeaseKeeperState::Active`
  (`CasMountRuntime.cpp:324-345`). `installKeeper` / `startKeeper` are admitted
  only from `Dormant` or `Parked` (`:361-394`). `scheduleRemount` parks a live
  worker (`WorkerCall` → `ParkRequested`, `WorkerIdle` → `Parked`, `:1072-1083`)
  under `driver_mutex` and notifies. `renewalStopCause` / `waitForRetry` abort a
  worker PUT when parked or when the fence/lifecycle is lost (`:439-472`).
  `ceee42c` is the Active-keeper gate; `7f932d3` is the bounded-renewal /
  ownership split. No remaining unsynchronised `mount_keeper` replacement was
  found.
- **Fence generation fails closed across remount.** `armMountFence` bumps
  `fence_generation` before clearing `lost`. Durable paths capture
  `fenceGeneration()` at admission and re-check before every PUT
  (`checkFenceOrThrow`). Remount publishes the new `writer_epoch` and
  quiesces ref tables *before* re-arming (`CasPool.cpp:1348-1369`).
- **Ref-lane leadership is a single exit.** `leader_active` / `pending` live
  under `ref_queue_mutex`. `confirmExactRef` snapshots both mutexes and
  refuses `Yes` while a leader tenure or pending item exists
  (`CasRefLedger.cpp:426-434`, `:480-481`). `drainRefLanesForShutdown`
  latches `shutting_down` before snapshotting (`:1922-1927`).
- **`pending_snapshot_publishes` increment is under `state_mutex` and is
  retired on launch failure.** `admitSnapshotPublishUnderStateLock` (`:4023-4057`)
  is the only increment; `dispatchSnapshotPublisher` (`:4060-4079`) decrements
  in `SCOPE_EXIT` if the task never launched. `quiesceRefTablesForRemount`
  (`:1775-1779`) and `dropNamespace` wait on that count reaching zero.
- **`shared_from_this` on `Pool` is only used while a `shared_ptr` owner
  exists.** `tryDispatchDetached` (`CasPool.cpp:945-961`) allocates the lease
  first, then increments `in_flight` under the registry mutex, then arms.
  The task must not capture its own `Pool` pointer (`CasDetachedWork.h:45-47`).
  `~Pool` does not call `shared_from_this`.

## Closed-since-2026-08-12

- **concurrency-3 (High, snapshot-publish pending-count leak).** Closed: increment
  and launch-failure decrement are paired (`CasRefLedger.cpp:4053`, `:4072-4078`).
  The 2026-08-12 leak path (`829ad698ef6` era residual) is not on HEAD.
- **concurrency-4 (High, `shared_from_this` on an expiring pool).** Closed by
  `205af29c7f2`: detached work is a tracked `DetachedTaskLease` that pins the
  pool; admission refuses after `stopping`.
- **concurrency-5 / concurrency-6 (Medium, remount lost wakeup / uncaught
  remount body).** Closed by the `driver_mutex` + `driver_cv` park machine
  (`7f932d3` / subsequent remount rewrite). `scheduleRemount` notifies under
  the lock; workers wait on the same cv.
- **concurrency-7 (Medium, `mount_keeper` replaced with no synchronisation).**
  Closed: every keeper install/reset/renewal capture is under `driver_mutex`
  and only from `Dormant`/`Parked`.
- **concurrency-8 (Medium, renewal mutates fence state outside `state_mutex`).**
  Closed as a race: renewal is admitted only over an Active keeper (`ceee42c`);
  `consumeRenewResult` runs after `DriverLease::finish` has restored ownership.

## Coverage

- Reviewed: GC scheduler start/stop/join/`requestRoundSoon`; remount/renew
  driver states and Active-keeper admission; fence generation vs remount
  epoch publish; ref-lane leader election and confirm snapshot; snapshot
  publish pending count; detached-work `shared_from_this`; DataPartsLock
  vs CA `commitTransaction`.
- N-A: TSA completeness (still almost nil outside
  `ContentAddressedMetadataStorage.h`; not a confirmed defect).
- Deferred: TSan; lock-order of `lifecycle_mutex` → `gc_scheduler_mutex` →
  `pointer_mutex` under a new caller (existing sites match the comment).

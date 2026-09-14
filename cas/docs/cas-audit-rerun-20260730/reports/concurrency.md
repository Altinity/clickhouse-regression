# concurrency — re-run 2026-07-30

Static concurrency & memory-safety re-audit of the current CAS PR (branch
`cas-audit-20260730` in `/Volumes/workspace/ClickHouse`). Focus is C++-level
concurrency: locks, atomics, thread lifecycle, `unique_ptr` / `shared_ptr`
races, teardown UAF. This is the language-level counterpart to
`interleaving.md` (which reasons at the protocol level).

## Scope in current code

Walked files (all under
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`):

- `Pool/CasPool.{h,cpp}` — the class formerly `Cas::Store`; renamed `Pool`
  and split. Owns `event_sink_`, `event_dispatcher_`, `mount_runtime`,
  `ref_ledger`, `manifest_reader`. Contains `~Pool` teardown ordering and
  `forgetDisk`.
- `Pool/CasMountRuntime.{h,cpp}` — the extracted mount / heartbeat /
  self-remount machinery (`mount_keeper`, `remount_thread`, `remount_stop`,
  `remount_shutting_down`, `scheduleRemount`, `stopRemountThread`,
  `finishTeardown`, `installKeeper`, `keeperReset`).
- `Pool/CasServerRoot.{h,cpp}` — `SingleWriterSlot` (mount-lease keeper's
  background renewal thread; `MountLeaseKeeper` derives from it).
- `Pool/CasRefLedger.{h,cpp}` — ref-log lanes, snapshot-publisher detached
  thread, `drainRefLanesForShutdown`, `pending_snapshot_publishes`.
- `Pool/CasEventDispatcher.{h,cpp}` — NEW since original audit: serialized,
  reentrancy-safe delivery for `CasEvent` (mutex-guarded queue + drain).
- `Pool/CasManifestReader.{h,cpp}` — `ManifestDecodeCache` (LRU) replaces
  the wholesale-clear `manifest_cache` from the original audit.
- `Pool/CasPartWriteTxn.{h,cpp}` — build lifecycle, in-flight registration.
- `Gc/CasGcScheduler.{h,cpp}` — background + heartbeat thread lifecycle
  (`thread`, `hb_thread`, `stopping`, `wake`).
- `Gc/CasGc.{h,cpp}` — round engine (called from scheduler).

Not walked (out of scope, per README focus rule): MergeTree DataPartsLock
call sites live in `src/Storages/MergeTree/**`, so CAS-006 verdict here is
noted-but-not-verified — CAS-006 is properly re-audited under
`bc7-blocking-io-under-locks-audit`.

Structural note. The `Cas::Store` class named throughout the original C1-C4
findings has been renamed `Cas::Pool` and its mount/heartbeat/remount
mechanics extracted into a sibling `CasMountRuntime`. Two atomics that
figure in the fix (`remount_shutting_down`, `vanished_intent`) are new.
Two data structures the original audit referenced (`shard_write_seq`,
`shard_decode_cache`) no longer exist. Anchors below use the current
paths; each finding notes the correspondence to the original file/line.

## Findings still present

None of C1–C4 from the original concurrency audit are still reachable in
the current code. See "Findings fixed" and "By-design / N/A / info".

The four concurrency-class findings the parent brief asked me to re-check
against the current PR resolve as:

- CAS-023 (C1, teardown UAF / `std::terminate` — `scheduleRemount` ignores
  `remount_stop`) — **fixed**.
- CAS-090 (C2, `mount_keeper` `unique_ptr` reassigned without
  synchronization) — **still LATENT by construction, unchanged**.
- CAS-091 (C3, `event_sink_` published after keeper thread start) —
  **fixed by construction**; a residual latent race on `EventDispatcher::sink`
  is called out below.
- CAS-092 (C4, `shard_write_seq` never pruned) — **structurally
  eliminated**; the underlying map no longer exists.
- CAS-006 (BC7 family, publish under `DataPartsLock`) — outside CAS scope
  (MergeTree side); no CAS-side change alters the answer. Re-checked
  under `bc7-blocking-io-under-locks-audit`.

Details of each verdict are in the next two sections.

## Findings fixed / no longer reproducible

### CAS-023 — Teardown UAF / `std::terminate` race (C1) — fixed

**Anchor of fix:**
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.cpp:431`
(`scheduleRemount`) + `:486` (`stopRemountThread`) + `Pool/CasPool.cpp:778`
(`~Pool`).

**What changed vs. original.** Three defenses now compose:

1. A NEW `std::atomic<bool> remount_shutting_down` guard is checked at the
   top of `scheduleRemount` — both before AND under `remount_thread_mutex`:

   ```443:449:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.cpp
       if (remount_shutting_down.load() || remount_running.load() || remountTerminal())
           return;
       std::lock_guard g(remount_thread_mutex);
       if (remount_shutting_down.load() || remount_running.load() || remountTerminal())
           return;
       if (remount_thread.joinable())
           remount_thread.join();   /// Reap a previous recovery before starting a new one.
   ```

2. `stopRemountThread` latches `remount_shutting_down` UNDER the same
   `remount_thread_mutex` BEFORE setting `remount_stop` and joining. A
   keeper `on_lost` callback that races teardown therefore either sees the
   latch first (and returns) or is racing to acquire the same mutex — where
   `stopRemountThread` will release it only after the join, and where the
   in-mutex re-check fires:

   ```486:501:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.cpp
   void CasMountRuntime::stopRemountThread()
   {
       /// Refuse further recovery arming under the same mutex used by `scheduleRemount`, before joining.
       /// Thus a keeper callback racing with teardown cannot re-arm the recovery thread after the join.
       {
           std::lock_guard g(remount_thread_mutex);
           remount_shutting_down.store(true);
       }
       /// Stop recovery first; it could otherwise recreate the keeper while the heartbeat is being retired.
       remount_stop.store(true);
       remount_cv.notify_all();
       {
           std::lock_guard g(remount_thread_mutex);
           if (remount_thread.joinable())
               remount_thread.join();
       }
   }
   ```

3. `~Pool` explicitly reorders the two stops per the original audit's
   recommended remedy (b): stop remount FIRST, then heartbeat:

   ```778:805:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.cpp
   Pool::~Pool()
   {
       /// Teardown order is load-bearing and unchanged from the pre-3.5 inline sequence (only the
       /// mount/remount mechanics were relocated into `mount_runtime`):
       ///
       /// 1. Stop + join the self-remount recovery thread FIRST (it may otherwise re-create the keeper
       ///    below us). `stopRemountThread` latches `remount_shutting_down` under the thread mutex before
       ///    the join, so a keeper on_lost firing during teardown can never re-arm the thread after we join.
       mount_runtime.stopRemountThread();
       ...
       mount_runtime.finishTeardown(drained);
   }
   ```

   `finishTeardown` additionally performs a belt-and-suspenders second
   join of `remount_thread` after `mount_keeper->stop()`:

   ```535:542:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.cpp
       /// The second join closes the residual window where a keeper loss callback observed the shutdown gate
       /// late during the heartbeat stop operation.
       {
           std::lock_guard g(remount_thread_mutex);
           if (remount_thread.joinable())
               remount_thread.join();
       }
   ```

   The same discipline is also applied by `forgetDisk`
   (`CasPool.cpp:807-`), which stops GC → stops remount → drains → retires
   keeper, in that order, outside `remount_mutex`.

The original race trace (keeper thread's `on_lost → scheduleRemount` spawns
a fresh unjoined `remount_thread` on a destructing `Store`) is closed on
both sides: the latch stops the spawn AND the ordering stops the keeper
after the remount thread is guaranteed unjoinable.

### CAS-092 — `shard_write_seq` never pruned on `dropNamespace` (C4) — structurally eliminated

**Evidence.** A workspace-wide grep for `shard_write_seq` and
`shard_decode_cache` returns zero hits in the current CAS tree. Both maps
described in the original C4 (a decode-cache wholesale-cleared at
`SHARD_DECODE_CACHE_MAX_ENTRIES = 16384`, and a monotone `shard_write_seq`
map beside it) have been removed by the refactor.

What replaces the decode cache is a proper size- and count-bounded LRU on
manifests only (owned by `CasManifestReader`, not the ex-`Store`):

```37:40:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp
    if (manifest_decode_cache_bytes > 0)
        manifest_cache = std::make_unique<ManifestDecodeCache>(
            /*max_bytes=*/manifest_decode_cache_bytes, /*max_count=*/16384,
            ManifestDecodeCache::DEFAULT_SIZE_RATIO);
```

Since the sibling `shard_write_seq` map is gone (no unbounded per
`(namespace, shard)` counter map remains under any mutex I could find), the
original C4 leak vector is not reachable in the current code. If a
functional equivalent moved elsewhere and I missed it, this is worth a
follow-up grep by a reviewer familiar with the refactor.

## By-design / N/A / info

### CAS-090 — `mount_keeper` `unique_ptr` reassigned without synchronization (C2) — still LATENT, unchanged

**Anchor:**
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.h:400`
(the member) +
`CasMountRuntime.cpp:156-163` (`renewWatermarkOnce`, unlocked read) +
`CasMountRuntime.cpp:226-249` (`installKeeper`, unlocked reassign inside
`tryRemountOnce`'s `remount_mutex`) +
`CasMountRuntime.cpp:261-264` (`keeperReset`).

**Trigger (unchanged from original C2).**
`Pool::tryRemountOnce` (holding `remount_mutex`) calls
`mount_runtime.installKeeper(...)`, which does
`mount_keeper = std::make_unique<MountLeaseKeeper>(...)` — destroying the
old keeper and rebinding the pointer, with no lock on `mount_keeper`
itself. `renewWatermarkOnce` reads and dereferences `mount_keeper` on the
caller's thread WITHOUT taking `remount_mutex`:

```156:163:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasMountRuntime.cpp
void CasMountRuntime::renewWatermarkOnce()
{
    /// A read-only runtime has no heartbeat to renew. Report that misuse instead of fabricating a keeper
    /// or silently treating the call as successful.
    if (!mount_keeper)
        throw Exception(ErrorCodes::LOGICAL_ERROR, "CAS heartbeat: renewWatermarkOnce on a read-only Pool");
    mount_keeper->renewOnce();
}
```

Currently NOT reachable in production because `renewWatermarkOnce` is a
**test seam only**: a workspace grep shows every caller is in
`src/Disks/tests/gtest_cas_*.cpp` (the production keeper-adopt paths use
the background renewer instead). This is the same "config-based mutual
exclusion, unenforced" state the original audit reported.

**Notes.** Two things have changed since the original write-up that make
this a marginally lower-severity latent:

- Reassignment now runs UNDER `Pool::remount_mutex` (in `tryRemountOnce`)
  or during `~Pool`/`forgetDisk` after all keeper-touching threads are
  joined (`keeperReset`). Production remount → reassign is single-mutex
  serialized. But the test seam still bypasses `remount_mutex`.
- The remount thread no longer reassigns `mount_keeper` directly; only
  `tryRemountOnce` (the `remount_attempt` callback executed BY the remount
  thread, but under `Pool::remount_mutex`) and `keeperReset` do. So the
  original "remount thread frees a keeper that a foreground `renewOnce`
  is calling" trace narrows to: "test drives `renewWatermarkOnce` on
  thread A; a remount lands on thread B, wins `remount_mutex`, reassigns."
  Still a data race + UAF in that construction.

**Fix (unchanged from original).** Either guard `mount_keeper` with a
mutex (or an `atomic<shared_ptr>`), or make `renewWatermarkOnce` take
`Pool::remount_mutex`, or annotate the invariant on the header. A
compile-time separation (only-in-tests) would also work.

### CAS-091 — `event_sink_` `std::function` race at start-of-life (C3) — fixed by ordering

**Anchor (fix ordering):**
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.cpp:441-461`
(`open`) and `:762-774` (`openForDecommission`).

**What changed.** Both writable-open paths now call
`store->setEventSink(std::move(store->config.event_sink))` BEFORE any
background thread that would read `event_sink_` starts. In `open`:

```441:461:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.cpp
    /// Private ctor: make_shared cannot reach it.
    PoolPtr store(new Pool(std::move(backend), std::move(config), std::move(meta)));
    store->setEventSink(std::move(store->config.event_sink));

    ...

    if (!store->config.read_only)
        mountWritable(store, store->config.server_id, MountClaimPolicy::WaitForExpiry);
```

Every keeper start (`keeperStart`, `keeperStartBackground`) happens inside
`mountWritable` (`CasPool.cpp:640`, `:715`), which is called strictly
AFTER `setEventSink` on line 443. There is now a real happens-before edge
from `setEventSink`'s completion to any keeper thread launch.

Additionally, sink installation goes through a NEW `CasEventDispatcher`
which owns the actual `Sink` under a mutex; `event_sink_` in `Pool` is just
a thin forwarder assigned once at `setEventSink` and never re-swapped in
traffic:

```661:672:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.h
    void setEventSink(CasEventSink sink)
    {
        event_dispatcher_.setSink(std::move(sink));
        if (event_dispatcher_.hasSink())
            event_sink_ = [this](CasEvent e) { event_dispatcher_.emit(std::move(e)); };
        else
            event_sink_ = {};
    }
    ...
    void emitEvent(CasEvent && e) const { if (event_sink_) event_sink_(std::move(e)); }
```

`event_dispatcher_.setSink` takes the dispatcher's own mutex. A subsequent
`setSink` call — if one ever occurred — would still race the `emit` path's
lock-free `sink` read (`CasEventDispatcher.cpp:41`), but the contract
comments explicitly forbid concurrent traffic + `setSink`, and no such
call exists in the code (only the two `setEventSink` sites, both pre-
traffic). So this is a **contract-enforced** rather than
**construction-enforced** guarantee, kept as info under
`NEW-concurrency-1` below.

## New findings (not in original audit)

### NEW-concurrency-1 — `CasEventDispatcher::sink` read outside the mutex; safe today by unenforced "pre-traffic only" contract (Info)

**Anchor:**
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasEventDispatcher.cpp:38-42`
(reads `sink` outside `mutex`) and `:10-15` (`setSink` writes it under
`mutex`).

**Trigger.** `emit` unlocks its mutex before calling the sink to permit
reentrancy from within the sink:

```37:52:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasEventDispatcher.cpp
        try
        {
            /// `sink` is set pre-traffic and never swapped concurrently with delivery, so reading it
            /// here without `mutex` is race-free.
            if (sink)
                sink(std::move(next));
        }
        catch (...)
```

If a caller ever calls `setSink` (which does write `sink` under `mutex`)
while a concurrent `emit` runs, `emit` reads `sink` (a `std::function`) at
line 41 with the mutex released — data race on the `std::function`
control block. **Currently unreachable** because there are exactly two
`setSink` call sites (both from `Pool::setEventSink`), and both are
invoked pre-traffic (before any thread that could emit is started). This
is a direct successor to the original C3 pattern: safe by an unenforced
contract rather than by construction. Cheap fix: keep the mutex held
across the sink call (breaks reentrancy — undesirable), OR upgrade `sink`
to `std::atomic<std::shared_ptr<Sink>>` (or a `unique_lock` + local copy
under the lock). Severity: **Info** — no reachable trace today.

### NEW-concurrency-2 — Detached snapshot-publisher thread can `Pool::~Pool` on itself via last `shared_ptr` release (Info)

**Anchor:**
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.cpp:2286-2325`
(`dispatchSnapshotPublisher`).

**Trigger.** `dispatchSnapshotPublisher` captures `owner = pin_owner()`
(a `shared_ptr<Pool>` via `Pool::shared_from_this`) into a detached
`ThreadFromGlobalPool` lambda:

```2286:2309:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.cpp
void CasRefLedger::dispatchSnapshotPublisher(const RootNamespace & ns, const std::shared_ptr<RefTableRuntime> & rt)
{
    ...
    auto owner = pin_owner();
    try
    {
        ThreadFromGlobalPool([owner, this, ns, rt]
        {
            setThreadName(ThreadName::CAS_REF_SNAPSHOT_PUBLISH);
            ...
            settleSnapshotPublish(ns, rt);
        }).detach();
    }
```

Since the thread is **detached**, `Pool::~Pool` is not guaranteed to run
on the thread that dropped the last user `shared_ptr` — it will run on
whichever thread's `owner` release is the last. If that final release
happens inside the detached lambda, `~Pool` (which calls
`stopRemountThread` and joins other CAS threads) runs on the detached
snapshot-publisher thread. `~Pool` does NOT try to join the
snapshot-publisher (nothing owns its handle), and `~Pool` never runs on
the remount thread (already joined by `stopRemountThread`), so this does
NOT self-deadlock. But it's a subtle destruction-thread ambiguity that
tests / TSan / lifetime auditors typically want called out.

Severity: **Info**. Two mitigations if it ever became a problem: (a) hold
`owner` in a `weak_ptr` and reject if expired (already the pattern
`registerInflightBuild` uses for `inflight_builds`); (b) track the
detached thread's handle in a small `std::unordered_set<ThreadHandle>`
joined at teardown.

### NEW-concurrency-3 — `CasGcScheduler::stop()` reads `thread` / `hb_thread` outside `mutex` (Info)

**Anchor:**
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcScheduler.cpp:75-93`.

**Trigger.**

```75:93:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcScheduler.cpp
void CasGcScheduler::stop()
{
    {
        std::lock_guard lock(mutex);
        stopping = true;
    }
    wake.notify_all();
    if (thread.joinable())
        thread.join();
    if (hb_thread.joinable())
        hb_thread.join();
    ...
}
```

The `joinable()`/`join()` calls read the two `ThreadFromGlobalPool`
members without holding `mutex`, whereas `start()` writes them under the
mutex (`:66-73`). Safe today because `start()` and `stop()` are meant to
be single-owner serialized (the DiskContentAddressed owner holds the
scheduler; there is no path that calls both concurrently). If that ever
changes, `stop()` would race the assignment inside `start()`. Severity:
**Info**. Compare with `SingleWriterSlot::stopBackground`
(`CasServerRoot.cpp:1162-1174`) which correctly `std::move`s the handle
out under the lock and joins outside — same pattern applied to
`CasGcScheduler::stop` would eliminate the concern.

## Verified CLEAN (unchanged strengths retained)

Recording explicitly, since these are what makes the concurrency posture
robust in practice:

- **Lock ordering.** The `view_gate → RetireView` order and the
  keeper's "renew payload evaluated before `state_mutex`" discipline are
  intact. `stopBackground` in `SingleWriterSlot` moves the thread handle
  out under `background_mutex` and joins after release (`CasServerRoot.cpp:1162-1174`).
- **Atomic memory orderings.** `remount_shutting_down` and
  `vanished_intent` (new atomics for teardown) are consistently
  release-published / acquire-observed. `terminal_state_published`
  uses `exchange(acq_rel)` for the idempotency guard. `pool_lifecycle`
  compare-exchanges use `acq_rel`/`acquire`. `mount_fence` release/
  acquire pairing on `deadline_boot_ms` vs `lost` is unchanged.
- **`remount_cv` predicate** — predicate reads `remount_stop.load()` and
  the wait uses a bounded timeout, so setting `remount_stop` without
  `remount_cv_mutex` cannot cause a lost-wakeup hang (`CasMountRuntime.cpp:464-467`).
- **`remount_running` re-entrancy guard** — `scheduleRemount` returns
  early on `remount_running.load()` inside `remount_thread_mutex`, so a
  keeper `on_lost` firing while the remount loop is running never
  self-joins.
- **`shared_ptr`-based ownership pinning.** Every detached thread
  (snapshot publisher at `CasRefLedger.cpp:2297`, anomaly diagnostics at
  `CasPool.cpp:1248`) captures a `shared_ptr<Pool>` before detaching, so
  no touched-`this` UAF is reachable while the thread runs.
- **In-flight builds** use `std::weak_ptr` in
  `inflight_builds` (`CasMountRuntime.h:390`), so `dropNamespace`'s
  cancellation traversal never resurrects a build past its natural
  lifetime.
- **`ref_ledger.drainRefLanesForShutdown`** latches `shutting_down` under
  `std::memory_order_release`, then snapshots the runtime set under
  `ref_queue_mutex`, then waits on per-table `cv` with a shared deadline.
  Every `appendRefOps` critical section checks `shutting_down` under
  `std::memory_order_acquire` inside the same `ref_queue_mutex` critical
  section as its `pending.push_back` — the paired check makes the drain
  race-free against a first-touch newcomer.
- **`event_dispatcher_`** is declared BEFORE `event_sink_` in `Pool`
  (`CasPool.h:704-711`) so the forwarder captured by `event_sink_` never
  outlives its target — correct destruction ordering.

## Verdict summary table

| CAS-id  | Old severity | Status                             | Evidence anchor                                                                                                       |
|---------|--------------|------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| CAS-023 | Med          | ✅ fixed                           | `Pool/CasMountRuntime.cpp:431-471` (`scheduleRemount` + `remount_shutting_down`); `:486-501` (`stopRemountThread`); `Pool/CasPool.cpp:778-805` (`~Pool` order) |
| CAS-090 | Low (latent) | 📐 by-design (latent, unenforced)  | `Pool/CasMountRuntime.h:400`; `Pool/CasMountRuntime.cpp:156-163` (`renewWatermarkOnce` unlocked); `:226-249` (reassign under `Pool::remount_mutex` only) |
| CAS-091 | Low (latent) | ✅ fixed by construction (ordering); residual contract-enforced race called out as NEW-concurrency-1 | `Pool/CasPool.cpp:441-461` (setEventSink before `mountWritable`); `Pool/CasEventDispatcher.cpp:37-42` (residual)         |
| CAS-092 | Low (growth) | ✅ fixed (structure removed)       | Workspace grep `shard_write_seq` = 0 hits; `Pool/CasManifestReader.cpp:37-40` (LRU replacement)                        |
| CAS-006 | Med          | ⚪ out-of-scope here (MergeTree side); re-checked in `bc7-blocking-io-under-locks-audit` | n/a in this file                                                                                                       |

New findings this pass:

| ID                    | Severity | Anchor                                                                 |
|-----------------------|----------|------------------------------------------------------------------------|
| NEW-concurrency-1     | Info     | `Pool/CasEventDispatcher.cpp:37-42` (`sink` read outside mutex)         |
| NEW-concurrency-2     | Info     | `Pool/CasRefLedger.cpp:2286-2325` (detached publisher may run `~Pool`) |
| NEW-concurrency-3     | Info     | `Gc/CasGcScheduler.cpp:75-93` (`stop` reads thread handles outside `mutex`) |

## Headline

Every C1–C4 finding from the original concurrency audit is either fixed
(C1, C4) or unchanged-latent-but-not-reachable (C2, C3). C1's fix is
belt-and-braces: a new `remount_shutting_down` atomic + latch in the same
mutex as `scheduleRemount`, and `~Pool` explicitly stops the remount
thread before the heartbeat. C3's original data-race pattern moved to
`CasEventDispatcher`, but the "set before any traffic" ordering is now
correct in both writable-open paths. The three new findings are all
**Info**: patterns worth naming, none reachable in production today.

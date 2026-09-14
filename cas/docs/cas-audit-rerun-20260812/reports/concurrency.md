# concurrency -- fresh audit 2026-08-12

## Scope

In-process thread-safety of the CAS implementation in
`/Volumes/workspace/altinity-clickhouse/ClickHouse` (branch `cas-code-only-strip`, base
`842f2b37b8f`, working tree as-is), rooted at
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Covered: every `std::mutex` / `std::condition_variable` / `std::atomic` / thread object in the CAS
tree; all four TSA suppressions and all four TSA annotations; lock ordering across the mount
runtime, ref ledger, pool, GC scheduler, view/manifest caches, blob upload pool and event
dispatcher; background-thread start/stop/join/teardown; destruction-order and use-after-free
hazards; `std::terminate` risk; data races on shared caches and counters; condition-variable
predicates and lost/spurious wakeups; `shared_ptr`/`weak_ptr` lifetime across async callbacks;
`ThreadStatus`/`ProfileEvents` from background threads. Blocking I/O under a lock is reported here
only where it is the mechanism of a race, hang or deadlock — the latency angle belongs to bc7.

Excluded (sibling audits): cross-node interleavings and linearizability (jepsen-anomaly,
interleaving), GC protocol semantics (gc-protocol). Static reasoning only; nothing was built or
run. Code-only rule observed: no `docs/**` and no comment is used as evidence of intent; shipped
log/exception strings are quoted as evidence. All CAS tests are deleted in the working tree, so
every claim below is derived from non-test code paths.

Already reported by siblings, cited but not re-reported: GC lease has no TTL / rebuild never
renews; `SYSTEM CAS FSCK` holds `lifecycle_mutex` unbounded
(`ContentAddressedMetadataStorage.cpp:741`); view-cache byte accounting constant.

## Threads, locks and ownership

| Thread / primitive | Anchor | Owner & lifecycle | Notes |
| --- | --- | --- | --- |
| GC scheduler loop `thread` | `Gc/CasGcScheduler.h:112`, body `Gc/CasGcScheduler.cpp:219` | started `start()` `:63`, joined `stop()` `:75`, `stop()` from `~CasGcScheduler` `:54` | joined **outside** `mutex`; self-exits at `:241` on terminal lifecycle leaving the object joinable |
| GC heartbeat `hb_thread` | `Gc/CasGcScheduler.h:114`, body `:279` | started `:64`, joined `:77` | shares `wake` with the loop; predicate is `stopping` only |
| Remount thread | `Pool/CasMountRuntime.h:173`, body `Pool/CasMountRuntime.cpp:354` | started `scheduleRemount()` `:353`, joined `:352`/`:395`/`:426` | captures raw `this`; no try/catch in the body |
| Mount-lease keeper thread | `Pool/CasServerRoot.h:99`, body `:1092` | `startBackground()` `:1075`, joined `stopBackground()` `:1089`, also from `~SingleWriterSlot` `:1002` | holds `background_mutex` except across `renewOnce()` |
| Detached anomaly-diagnostics thread | `Pool/CasPool.cpp:995-1023` | `.detach()`, pinned by `shared_from_this()` `:992` | never joined; can outlive the disk |
| Detached snapshot-publisher thread | `Pool/CasRefLedger.cpp:2760-2772` | `.detach()`, pinned by `pin_owner()` `:2757` | never joined; settles via `settleSnapshotPublish` `:2771` |
| Blob upload pool (process-global) | `Pool/CasBlobUploadPool.cpp:32-65` | `initializeBlobUploadPool` / `shutdownBlobUploadPool`, `programs/server/Server.cpp:1500` | fan-out at `ContentAddressedTransaction.cpp:1152-1210` |
| `pointer_mutex` | `ContentAddressedMetadataStorage.h:303` | guards `cas_store`, `part_access`, `gc_scheduler` (`:296-299`) | only TSA-annotated fields in the tree |
| `gc_scheduler_mutex` | `...Storage.h:301` | serialises GC lifecycle verbs; guards `shutdown_called` `:302` | not taken by `requestGcRoundSoon()` `:303` |
| `lifecycle_mutex` | `...Storage.h:300` | admin verbs (`forgetDisk`, `gcStop`, `gcStart`, fsck, rebuild) | unbounded hold — sibling finding |
| `CasGcScheduler::mutex` / `gc_round_mutex` / `terminal_exit_mutex` | `Gc/CasGcScheduler.h:106-121` | wake state / round exclusion / test-only exit signal | `gc_round_mutex` not taken by `runGcRebuildNow()` |
| `remount_thread_mutex`, `remount_cv_mutex`, `remount_cv` | `Pool/CasMountRuntime.h:167-172` | remount thread lifecycle and backoff sleep | notifier at `:391` does not hold `remount_cv_mutex` |
| `builds_mutex` | `Pool/CasMountRuntime.h:159` | `next_build_seq`, `active_build_seqs`, `inflight_builds` | consistently held; `weak_ptr` copies taken under lock `:174-176` |
| `mount_keeper` (unique_ptr, unguarded) | `Pool/CasMountRuntime.h:164` | installed/reset from the remount thread `Pool/CasPool.cpp:725-726` | no mutex, no atomic, no TSA |
| `SingleWriterSlot::state_mutex` / `background_mutex` | `Pool/CasServerRoot.h:83,96` | lease seq/token/dead vs renewal thread | `prepareRenew()` mutates state outside `state_mutex` |
| `RefTableRuntime::state_mutex`, `cv`, `recovery_cv`, `publish_settle_cv` | `Pool/CasRefLedger.h:366-396` | per-namespace ref lane | two unbounded waits (`:1227`, `:3592`) |
| `ref_queue_mutex` | `Pool/CasRefLedger.h:421` | `ref_name_slots`, per-item `pending`/`done`, leader election | eviction relies on `use_count()==1` under this lock |
| `writer_cleanup_mutex` / `writer_cleanup_cv` | `Pool/CasPool.h:456-457` | abandon-duty queue, single drainer | unbounded wait `Pool/CasPool.cpp:832` |
| `remount_mutex`, `admitted_algos_mutex` | `Pool/CasPool.h:461,478` | vanish publication, cached algo list | short critical sections |
| `EventDispatcher::mutex` | `Pool/CasEventDispatcher.h:24` | queue + `draining` flag | `sink` invoked with the mutex released `:33` |
| `inflight_mutex` / `explain_mutex` | `Parts/PartFolderAccess.h:188,197` | view single-flight map / explain ring | single-flight key omits the manifest id |
| `condemn_marker_mutex` | `Gc/CasGc.h:443` | condemn-marker writes inside a round | one round at a time via `gc_round_mutex` |
| Backend emulation mutexes | `Backend/CasInMemoryBackend.h:82`, `Backend/CasObjectStorageBackend.h:90` | test/emulation state | not in the production path for S3 |

## Findings

### concurrency-1 -- GC scheduler joins its thread objects outside the mutex that guards them (High)

- **Anchor**: `src/.../Gc/CasGcScheduler.cpp:67-79` (`stop()`), `:81-90` (`requestRoundSoon()`),
  `:57-65` (`start()`); caller `ContentAddressedMetadataStorage.cpp:303-312`.
- **Trigger (interleaving)**: `stop()` releases `mutex` at `:72` and then evaluates
  `thread.joinable()` and `thread.join()` at `:74-77` with no lock held. `requestRoundSoon()` reads
  `thread.joinable()` at `:85` **under** `mutex`. Thread A runs `SYSTEM CAS DROP POOL MEMBER`,
  which reaches `ContentAddressedMetadataStorage::requestGcRoundSoon()`; that method copies the
  scheduler `shared_ptr` under `pointer_mutex` (`:307-308`) and then calls `requestRoundSoon()`
  holding **neither** `gc_scheduler_mutex` nor `lifecycle_mutex`. Thread B concurrently runs disk
  `shutdown()` (`ContentAddressedMetadataStorage.cpp:644-645`) or `SYSTEM CAS GC STOP`
  (`:706`), both of which call `stop()`. A's guarded `joinable()` read and B's unguarded
  `join()` touch the same `ThreadFromGlobalPool::state` `shared_ptr` concurrently.
- **Evidence**: `joinable()` is `return initialized();` and `join()` ends with `state.reset()`
  (`src/Common/ThreadPool.h:390-401`, `:410-412`) — a non-atomic `shared_ptr` member read and
  written concurrently. The scheduler's own `mutex` is the declared synchronisation point for
  `thread` (it is what `start()` and `requestRoundSoon()` use), and `stop()` steps outside it.
- **Notes**: the `shared_ptr` snapshot keeps the scheduler object alive, so this is a data race on
  the thread handle rather than an object-lifetime bug; the same unguarded `join()` is reached from
  `~CasGcScheduler` (`:52-55`). `hb_thread` (`:76-77`) has the identical exposure, and it is not
  covered by the `:60` guard in `start()` at all.

### concurrency-2 -- View single-flight collapses different manifest ids onto one key (High)

- **Anchor**: `src/.../Parts/PartFolderAccess.cpp:231-269` (`buildView`), consumers at `:150-215`
  (`getView`), cache write at `:198`.
- **Trigger (interleaving)**: the in-flight map is keyed on `key.cacheKey()` only (`:242`, `:248`,
  `:256`) while the value being computed is a view of one specific `resolved.manifest_id`
  (`:260`). Reader A calls `getView(key, CachedForLoad)`, resolves the ref to manifest M1 at
  `:152`, misses the cache, becomes the single-flight leader and blocks in
  `readManifestShared(M1)`. A writer repoints the same ref to M2 and invalidates the cache
  (`eraseView`, `:271-278`). Reader B then calls `getView(key, CachedForLoad)`, correctly resolves
  M2 at `:152`, misses the cache, enters `buildView`, finds A's in-flight entry, and returns A's
  **M1** view at `:252`. Back in `getView`, B stores that stale view into `view_cache` under
  `cache_key` at `:198`.
- **Evidence**: the follower path (`:251-252`) performs no comparison between `future.get()`'s
  `manifestId()` and the `resolved.manifest_id` the follower itself resolved, unlike every cache
  hit path, which does compare (`:162`, `:175`). `CASPartFolderViewValidationMismatches` is
  therefore not incremented for this case, so the condition is invisible in metrics.
- **Notes**: consequence is a read-after-write violation for the follower — a part read that
  resolved the new manifest is served the previous manifest's entry list (missing or extra files),
  and the stale view is additionally published into the shared cache. Later readers do revalidate
  at `:162` and recover, which is why this is silent rather than persistent.

### concurrency-3 -- Snapshot-publish dispatch can leak its pending count, hanging two unbounded waits (High)

- **Anchor**: `src/.../Pool/CasRefLedger.cpp:2754-2783` (`dispatchSnapshotPublisher`), increment at
  `:2747`, waits at `:1227-1228` (`quiesceRefTablesForRemount`) and `:3590-3596`
  (`dropNamespaceImpl`).
- **Trigger (interleaving)**: `admitSnapshotPublishUnderStateLock` increments
  `pending_snapshot_publishes` at `:2747` while holding `state_mutex`. The dispatcher then calls
  `pin_owner()` at `:2757`, which is **outside** the `try` block at `:2758`. `pin_owner` is the
  owner-pinning callback installed by the `Pool` (`Pool/CasRefLedger.h:334`) and resolves to
  `shared_from_this()` on the pool; once the pool's last `shared_ptr` has been released and
  `~Pool` is running (`Pool/CasPool.cpp:562-571`, which drains ref lanes at `:566`), that call
  throws `std::bad_weak_ptr`. The exception propagates out of `dispatchSnapshotPublisher` without
  reaching the `catch` at `:2774-2782`, so the compensating decrement at `:2778` and the
  `notify_all()` at `:2780` never run, and `pending_snapshot_publishes` stays at +1 forever.
- **Evidence**: both waiters have no timeout and no shutdown term in the predicate —
  `:1227` waits on `pending_snapshot_publishes == 0` while holding that lane's `state_mutex`, and
  `:3592` does the same at the end of a namespace drop. The only other decrement site is
  `settleSnapshotPublish` (`:2791`), which is reached only from inside the detached thread that was
  never launched.
- **Notes**: consequence is a permanent hang of the remount path (`quiesceRefTablesForRemount` is
  called from `tryRemountOnce`, `Pool/CasPool.cpp:733`) and of `DROP TABLE`/namespace removal, with
  a lane's `state_mutex` held for the duration, which in turn wedges every writer on that
  namespace. The same shape applies if the process runs out of threads: `ThreadFromGlobalPool`
  construction throwing *is* handled at `:2774`, so the only unhandled step is the pin itself.

### concurrency-4 -- Anomaly reporting calls `shared_from_this()` on a possibly expiring pool (High)

- **Anchor**: `src/.../Pool/CasPool.cpp:972-1029`, in particular `:992` (`shared_from_this()`
  outside the `try` at `:993`) and the detached thread at `:995-1023`.
- **Trigger (interleaving)**: `reportImpossibleInterference` is reachable from the remount thread
  (`tryRemountOnce` → backend reads) and from any query thread that observes foreign interference.
  The remount thread is only joined at `Pool/CasMountRuntime.cpp:395`/`:426`, i.e. *inside* `~Pool`
  (`Pool/CasPool.cpp:564`, `:570`). A remount attempt already in flight when `~Pool` starts is
  therefore still executing while the pool's weak references are expired; when it reaches `:992`,
  `shared_from_this()` throws `std::bad_weak_ptr`, which escapes the function (the `try` begins
  only at `:993`) and then escapes the remount thread body, which has no handler
  (`CasMountRuntime.cpp:354-368`).
- **Evidence**: the fence and remount side effects at `:989-990` have already been applied at that
  point, so the mount is left fenced closed while the diagnostic path aborts. Because the escaping
  exception skips `:367`, `remount_running` stays `true` — see concurrency-6 for the consequence.
- **Notes**: the detached diagnostics thread also pins the pool via `self` (`:995`), so `~Pool` —
  including `stopRemountThread()` and `finishTeardown()` — can end up running on that background
  thread after the disk has been unregistered. `ThreadFromGlobalPool` bodies do not terminate the
  process on an escaping exception (`src/Common/ThreadPool.cpp:1108` runs the body, and the pool
  worker catches at `:989`), so this is a lost-recovery bug, not a crash.

### concurrency-5 -- Lost wakeup when stopping the remount thread (Medium)

- **Anchor**: `src/.../Pool/CasMountRuntime.cpp:384-397` (`stopRemountThread`), sleeper at
  `:362-365`.
- **Trigger (interleaving)**: the remount thread takes `remount_cv_mutex` at `:362` and waits on
  `remount_cv` with predicate `remount_stop` (`:364`). `stopRemountThread` stores `remount_stop`
  at `:390` and calls `remount_cv.notify_all()` at `:391` **without holding
  `remount_cv_mutex`** (the surrounding `lock_guard` at `:387` is `remount_thread_mutex`, a
  different mutex, and it is released at `:389`). If the notifier's store and notify land after the
  waiter evaluated the predicate as false but before it is registered on the condition variable,
  the wakeup is lost and the waiter sleeps out its full backoff, which grows to 30 s (`:365`).
- **Evidence**: `stopRemountThread` then blocks in `remount_thread.join()` at `:395` while holding
  `remount_thread_mutex` (`:393`), so the stall propagates: `~Pool` (`Pool/CasPool.cpp:564`),
  `SYSTEM CAS FORGET` (`:590`) and any concurrent `scheduleRemount()` (`CasMountRuntime.cpp:348`)
  all wait behind it.
- **Notes**: bounded at ~30 s per stop, so this is a teardown stall rather than a deadlock. The
  latching of `remount_shutting_down` under `remount_thread_mutex` (`:387-388`) is correct and does
  prevent a post-teardown thread from being started, so no use-after-free follows.

### concurrency-6 -- Remount thread body has no handler; one throw disables self-healing permanently (Medium)

- **Anchor**: `src/.../Pool/CasMountRuntime.cpp:353-368`.
- **Trigger (interleaving)**: `remount_running` is set to `true` at `:353` before the thread is
  created and cleared only at `:367`, the last statement of the body. The body itself has no
  `try`/`catch`, and `remount_attempt()` (`:360`) is the pool's `tryRemountOnce`, which does wrap
  its own work (`Pool/CasPool.cpp:753-766`) — but not everything reachable from it: `remountTerminal()`
  and the `EventEmitter` paths run outside that wrapper, and `reportImpossibleInterference` throws
  `std::bad_weak_ptr` before entering any handler (concurrency-4). Any escaping exception skips
  `:367`.
- **Evidence**: every subsequent `scheduleRemount()` returns immediately at `:346` and `:349`
  because both check `remount_running.load()`. Since the flag is only ever cleared at `:367`, the
  pool can never attempt another remount for the lifetime of the process, and the mount stays
  fenced closed after a lease loss.
- **Notes**: the flag is not scope-guarded, which is what makes a single escape terminal. Exposure
  is also visible in the shipped seams `scheduleRemountForTest` / `scheduleRemountCallCountForTest`
  (`Pool/CasPool.h:274-275`), which count calls but cannot clear the flag.

### concurrency-7 -- `mount_keeper` is replaced by the remount thread with no synchronisation (Medium)

- **Anchor**: `src/.../Pool/CasMountRuntime.h:164` (plain `std::unique_ptr`, no mutex, no TSA),
  writes at `Pool/CasMountRuntime.cpp:205` (`installKeeper`) and `:233` (`keeperReset`), driven from
  the remount thread at `Pool/CasPool.cpp:724-728`; reads at `CasMountRuntime.cpp:143-145`, `:223`,
  `:228`, `:238`, `:243`, `:401-419`.
- **Trigger (interleaving)**: on the remount thread, `tryRemountOnce` stops the old keeper's
  renewal thread at `Pool/CasPool.cpp:725` and then reassigns the `unique_ptr` at `:726`, which
  destroys the old `MountLeaseKeeper`. Any concurrent reader that has already passed the null check
  — `renewWatermarkOnce` does exactly `if (!mount_keeper) throw; mount_keeper->renewOnce();`
  (`CasMountRuntime.cpp:143-145`) — then dereferences a destroyed object, and the pointer read
  itself races with the assignment.
- **Evidence**: no lock, atomic or annotation covers `mount_keeper`; by contrast the pool's other
  swappable state (`cas_store`, `gc_scheduler`) is copied under `pointer_mutex` before use
  (`ContentAddressedMetadataStorage.cpp:747-758`). The teardown readers at `:401-419` are safe only
  because both callers latch `remount_shutting_down` and join the remount thread first
  (`Pool/CasPool.cpp:564`, `:590`).
- **Notes**: the reachable-today reader is `Pool::renewWatermarkOnce()` (`Pool/CasPool.cpp:779-781`,
  declared `Pool/CasPool.h:161`), a public entry point with no in-tree caller — one of the uncalled
  seams noted by coverage-map. Severity is Medium rather than High for that reason: the hazard is
  one call away, not currently exercised.

### concurrency-8 -- Lease renewal reads and writes fence state outside `state_mutex` (Medium)

- **Anchor**: `src/.../Pool/CasServerRoot.cpp:741-746` (`prepareRenew`, mutating `mutable`
  members), called before the lock at `:1013` (`doStart`) and `:1028` (`renewOnce`); unguarded
  reads at `:1108` (`last_renew_failure_was_confirmed_mismatch`), `:732-739`
  (`shouldFenceOnTransientRenewFailure` reading `confirmed_deadline_ms`), `:846`, `:852`.
- **Trigger (interleaving)**: `renewOnce` acquires `state_mutex` at `:1030` but calls
  `prepareRenew()` at `:1028` before it; `prepareRenew` writes `last_attempt_wall_ms` and
  `last_attempt_boot_ms` (`:743-744`). Those same fields are later read under the lock to compute
  the confirmed lease deadline (`refreshConfirmedDeadline(last_attempt_wall_ms)`, `:846` via
  `onRenewCommitted`) and the local write-fence deadline (`on_renew_ok(last_attempt_boot_ms)`,
  `:852` → `setMountDeadline`, `CasMountRuntime.cpp:213`). With two concurrent renewals — the
  keeper's background loop at `:1104` and a foreground `Pool::renewWatermarkOnce()` — the
  foreground attempt's timestamp can be the one folded into the deadline for the background
  attempt's confirmed write, extending the local fence past what the backend confirmed
  (fail-open direction).
- **Evidence**: `backgroundLoop` reads `last_renew_failure_was_confirmed_mismatch` at `:1108` with
  no lock, while `renewOnce` writes it at `:1031` and `:1041` under `state_mutex`. That single bool
  selects between "retry transiently" (`:1109-1115`) and "latch the fence and stop renewing"
  (`:1118-1127`), so a stale read in either direction is safety-relevant: a genuine confirmed
  foreign mismatch classified as transient keeps this node writing while another incarnation owns
  the mount slot — the exact condition the shipped string at `:1052` says it must fail closed on.
- **Notes**: today the only caller of `renewOnce` besides the background loop is
  `CasMountRuntime::keeperRenewOnce()` from `Pool/CasPool.cpp:512`, which runs *before*
  `keeperStartBackground` at `:516`, so the two-renewal interleaving needs the uncalled
  `Pool::renewWatermarkOnce()` seam — hence Medium. `renewOnce` also holds `state_mutex` across
  `backend->putOverwrite` (`:1038`); that is safe against `doTerminate`, which joins the renewal
  thread at `:1057` *before* taking the lock at `:1059`.

### concurrency-9 -- Writer-cleanup drain waits with no timeout and no shutdown escape (Medium)

- **Anchor**: `src/.../Pool/CasPool.cpp:828-896`, wait at `:832-836`, drain I/O at `:862-876`,
  latch at `:805`.
- **Trigger (interleaving)**: the first caller for a namespace sets `draining = true` at `:841` and
  then performs ref-log appends against the backend at `:862` with the mutex released. A second
  caller for the same namespace blocks at `:832` on the predicate "no entry, or not draining" —
  no timeout, no `remount_stop`/vanished/lifecycle term. If the drainer's `appendRefOps` is itself
  waiting on a ref lane (for example the lane leader blocked on `publish_settle_cv`, see
  concurrency-3), the waiter blocks indefinitely, and because `~Pool` consults
  `writerCleanupDutiesPending()` at `:568`, pool destruction is drawn into the same wait.
- **Evidence**: the drainer resets `draining` on every exit path (`:855`, `:892`), so a hang
  requires the drainer itself to be stuck rather than to have leaked the flag — which is exactly
  the state concurrency-3 produces. The predicate at `:835` cannot observe shutdown.
- **Notes**: separately, `enqueueWriterCleanupDuty` is `noexcept` and latches
  `writer_cleanup_queue_failed` at `:805` on allocation failure; that latch is never cleared, so
  `writerCleanupDutiesPending()` returns `true` forever (`:820`) and every subsequent teardown takes
  the `drained == false` branch of `finishTeardown` (`CasMountRuntime.cpp:414-420`), permanently
  skipping the clean-release marker — the shipped string at `:417` describes the consequence
  ("the next mount will treat this end as unclean").

### concurrency-10 -- GC threads self-exit independently, leaving a joinable-but-dead scheduler (Medium)

- **Anchor**: `src/.../Gc/CasGcScheduler.cpp:232-242` (loop terminal exit), `:289-298` (heartbeat
  terminal exit), `:57-65` (`start()`), caller `ContentAddressedMetadataStorage.cpp:709-737`.
- **Trigger (interleaving)**: both threads evaluate the same terminal-lifecycle predicate
  (`isVanished() || vanishedIntentPublished() || lifecycle() == IdentityLost`) independently, at
  their own cadence (`interval` vs `hb_interval`, `:41-43`). The heartbeat thread can observe the
  transition first and return at `:297` while the loop thread is mid-round; `i_am_leader` stays
  `true` (it is only cleared at `:235`/`:273`), so the round continues to run as leader with no
  heartbeat being pulsed.
- **Evidence**: after either self-exit the corresponding `ThreadFromGlobalPool` remains
  `joinable()` because nothing joins it until `stop()` (`:74-77`). A subsequent `SYSTEM CAS GC
  START` reaches `start()` and returns silently at `:60-61` (`if (thread.joinable()) return;`),
  so the verb succeeds without restarting anything and without a diagnostic.
- **Notes**: the missing-heartbeat window compounds the sibling finding that the GC lease has no
  TTL. Also in this file: `requestRoundSoon()` notifies the shared `wake` (`:89`), which the
  heartbeat loop waits on with predicate `stopping` only (`:286`), so every manual round request
  spuriously wakes the heartbeat thread; that is benign (it re-checks and pulses early), noted for
  completeness.

### concurrency-11 -- `startup()` publishes pool identity after the pool itself, under a TSA suppression (Low)

- **Anchor**: `src/.../ContentAddressedMetadataStorage.cpp:577-630`; declaration
  `ContentAddressedMetadataStorage.h:125` (`TSA_NO_THREAD_SAFETY_ANALYSIS`); fields `:296-303`;
  reader `getPoolUUID()` `:147`, `lifecycleSnapshot()` `.cpp:330`.
- **Trigger (interleaving)**: `startup()` reads `cas_store` at `:579` with no lock even though the
  field is `TSA_GUARDED_BY(pointer_mutex)`, writes `read_only` (`:582`) and `physical_key_prefix`
  (`:585`) unguarded, starts the GC scheduler and heartbeat threads at `:616`, and only then
  publishes the pointers under `pointer_mutex` at `:622-627` — after which it writes `pool_uuid`
  (`:628`) and `conditional_copy_supported` (`:629`) outside the lock. Between `:616` and `:628`
  two background threads are running while pool identity is still unset; `lifecycleSnapshot()`
  reads `pool_uuid` with no lock at `.cpp:330` and uses emptiness to distinguish "constructing"
  from "shutdown" (`:339`).
- **Evidence**: the suppression at `.h:125` is what allows the guarded-field access at `:579` to
  compile. `getPoolUUID()` returns `const String &` (`.h:147`), so any caller holding that
  reference across a `pool_uuid` reassignment observes a torn or freed buffer.
- **Notes**: severity Low because the disk object is not reachable by other threads until the
  factory returns (`src/Disks/DiskObjectStorage/RegisterDiskObjectStorage.cpp:113` calls
  `startup()` on a freshly constructed disk), and neither background thread reads these fields —
  both `makeGcRoundLogger` and `makeCasEventSink` capture only `ctx` and `disk_name` by value
  (`.cpp:355-357`, `:429-431`). What the suppression removes is the compiler's ability to catch it
  if a second publication path ever appears. `shutdown()` (`:632-646`) is correctly annotated and
  correctly ordered by comparison.

### concurrency-12 -- Event dispatcher invokes the sink with the mutex released while it can be replaced (Low)

- **Anchor**: `src/.../Pool/CasEventDispatcher.cpp:17-44`, in particular `:30` (unlock), `:33-34`
  (read and call `sink`), versus `:10-15` (`setSink`).
- **Trigger (interleaving)**: the draining thread unlocks at `:30`, then reads the `sink`
  `std::function` and calls it at `:33-34`. `setSink` move-assigns `sink` at `:13` under the same
  mutex, which is free during that window, destroying the previous callable's captured state — a
  data race on the `std::function` and a use-after-free of its captures if the assignment lands
  between the test and the call.
- **Evidence**: `has_sink` is atomic (`:14`) but `sink` itself is a plain member
  (`Pool/CasEventDispatcher.h:23`), and the drain loop deliberately runs outside the lock so the
  sink can block.
- **Notes**: Low because the only caller, `Pool::setEventSink` (`Pool/CasPool.h:283-290`), runs
  once during `Pool::open`/`openForDecommission` (`Pool/CasPool.cpp:358`, `:554`) before the pool
  is published, so the interleaving is latent. `Pool::setEventSink` additionally assigns the plain
  `event_sink_` member (`CasPool.h:287-289`) that `emitEvent`/`hasEventSink` read from every thread
  (`:291-292`), so a second caller would race there too.

### concurrency-13 -- `noexcept` rollback helpers call an allocating helper outside their `try` (Low)

- **Anchor**: `src/.../Parts/PartFolderAccess.cpp:502-516` (`dropRefBestEffort`) and `:518-561`
  (`dropRefIfMatches`), both declared `noexcept` (`Parts/PartFolderAccess.h:157-158`);
  `eraseView` at `:271-278`.
- **Trigger (interleaving)**: `eraseView(key)` is called at `:515` after the `catch (...)` block
  closes, and again on the corresponding path in `dropRefIfMatches`. `eraseView` constructs a
  `String` (`:273`), removes from the shared `CacheBase` (`:275`) and calls `recordDecision`
  (`:277`), which takes `explain_mutex` and pushes into the explain ring. Under memory pressure any
  of those allocations throws `std::bad_alloc` inside a `noexcept` function → `std::terminate`.
- **Evidence**: the intent of the surrounding code is clearly best-effort — everything that can
  fail is wrapped (`:504-514`, `:521-559`) — but the cache-invalidation tail is left outside.
- **Notes**: Low: allocation failure only, and these paths are rollback paths that already run
  under stress. Listed because it is the only `std::terminate` exposure I could confirm in the tree:
  exceptions escaping a thread body do **not** terminate (`src/Common/ThreadPool.cpp:1108` invokes
  the body and the pool worker catches at `:989`), and every other CAS `noexcept` function wraps
  its whole body (`Pool/CasRefLedger.cpp:1543-1561`, `Pool/CasPool.cpp:789-816`,
  `Pool/CasServerRoot.cpp:1140`).

### concurrency-14 -- Audit events are attributed to the draining thread, not the emitting one (Low)

- **Anchor**: `src/.../ContentAddressedMetadataStorage.cpp:431-456`, in particular `:437-439`
  (timestamps) and `:452-453` (`thread_id`, `query_id`); dispatcher `Pool/CasEventDispatcher.cpp:22-42`.
- **Trigger (interleaving)**: thread T2 calls `emit`, finds `draining == true` (`:22`), queues its
  event and returns. Thread T1 — which may be the GC scheduler thread, the remount thread, or an
  unrelated query — later pops that event at `:28` and invokes the sink, which stamps
  `getThreadId()` and `CurrentThread::getQueryId()` (`.cpp:452-453`) plus
  `system_clock::now()` (`:437-439`) from **its own** context.
- **Evidence**: nothing in `CasEvent` carries the originating thread or query
  (`Primitives/CasEvent.h`), so the attribution is irrecoverably lost at drain time.
- **Notes**: `system.cas_log` is the shipped forensic surface for mount conflicts and foreign
  interference; rows can name the wrong query and be ordered by drain time rather than emit time,
  which is exactly the interleaving one would try to reconstruct from it. Unbounded queue growth
  when the sink is slow (`:20`, no cap) is the latency/memory angle and belongs to bc7.

## By-design / info

- **TSA coverage is effectively nil outside one header.** The whole CAS tree contains four
  `TSA_GUARDED_BY` annotations and one `TSA_REQUIRES`-free surface, all in
  `ContentAddressedMetadataStorage.h:296-302`. `CasRefLedger`, `CasMountRuntime`, `CasServerRoot`,
  `CasGcScheduler`, `CasPool`, `EventDispatcher` and `CachedPartFolderAccess` declare 20+ mutexes
  with no annotations at all, so the compiler cannot check any of the lock disciplines above. The
  four suppressions (`startup`, `forgetDisk`, `gcStop`, `gcStart` — `.h:125-132`) are consistent
  with coverage-map's note.
- **Ref-table eviction is safe despite reading fields under the wrong mutex.**
  `enforceRefTableCacheBudget` reads `leader_active`, `pending` and `last_touch_tick` under
  `ref_queue_mutex` only (`Pool/CasRefLedger.cpp:1180-1182`), but candidates are filtered on
  `rt.use_count() != 1`, and the only way to obtain a second reference is through the slot map
  under that same mutex. I initially flagged this and withdrew it.
- **Recovery budgets are leader-serialised.** `snapshot_budget`/`removal_budget` are written in
  `installRecoveryResult` (`:1116-1117`) and read in `flushRefBatch` (`:2165-2169`) on the same
  lane-leader thread; not a race.
- **Blob upload fan-out is correctly scoped.** `fanOutBlobUploads`
  (`ContentAddressedTransaction.cpp:1152-1210`) hands raw pointers into a stack-local `results`
  vector to pool tasks, but the `SCOPE_EXIT_SAFE` at `:1187` is declared after `handles` and so
  waits for every task before those objects unwind; `uploadBlobDetached` is `const` and touches only
  the internally-locked dedup cache (`Pool/CasPool.cpp:196-213`), with the single-threaded merge at
  `:1209`.
- **Global upload pool teardown order is correct.** `shutdownBlobUploadPool()` runs from the
  `SCOPE_EXIT_SAFE` at `programs/server/Server.cpp:1496-1503`, after context/disk shutdown; it
  holds `pool_mutex` across `~ThreadPool` (`Pool/CasBlobUploadPool.cpp:63-64`), which is safe only
  because no upload job calls `blobUploadPool()` — the sole call site is
  `ContentAddressedTransaction.cpp:241`, on the foreground commit path.
- **Manifest decode cache is safe.** `CacheBase` is internally synchronised and the key includes the
  object token (`Pool/CasManifestReader.h:37-42`), so it cannot collapse two different manifests the
  way the view single-flight does (concurrency-2).
- **Fence arming order fails closed.** `armMountFence` bumps `fence_generation` (`:123`) before
  clearing `lost` (`:126`), so a concurrent writer in that window sees either a generation mismatch
  (`checkFenceOrThrow`, `:92`) or `lost == true` (`refAppendFenceOk`, `:103`) and refuses the write.
  `mount_fence.server_uuid` and `writer_epoch` are non-atomic (`CasMountRuntime.h:46-47`) and
  written unguarded at `:120-121`, but I found no reader anywhere in the tree, so there is no race
  today.
- **`ProfileEvents` from background threads is fine.** `startThreadFromGlobalPool` installs a
  `ThreadStatus` for every `ThreadFromGlobalPool` body (`src/Common/ThreadPool.cpp:1103`), and the
  CAS background threads only use `ProfileEvents::increment` (atomic global counters) plus
  `setThreadName`. The two detached threads (`CasPool.cpp:997`, `CasRefLedger.cpp:2762`) are no
  different.
- **Cited, not re-reported**: GC lease has no TTL / rebuild never renews; `SYSTEM CAS FSCK` holds
  `lifecycle_mutex` unbounded (`ContentAddressedMetadataStorage.cpp:741-745`); view-cache byte
  accounting constant. `runGcRebuildNow()` serialising on `gc_scheduler_mutex` (`.cpp:496`) while
  scheduled rounds serialise on `gc_round_mutex` (`Gc/CasGcScheduler.cpp:245`) is a GC-protocol
  concern and is left to gc-protocol / gc-rebuild-feature.

## Coverage

Read in full or in the relevant regions: `ContentAddressedMetadataStorage.{h,cpp}` (lifecycle
verbs, pointer publication, sinks), `Pool/CasPool.{h,cpp}`, `Pool/CasMountRuntime.{h,cpp}`,
`Pool/CasServerRoot.{h,cpp}` (`SingleWriterSlot`, `MountLeaseKeeper`), `Pool/CasRefLedger.{h,cpp}`
(lane queue, recovery, snapshot publish, drop/quiesce), `Pool/CasEventDispatcher.{h,cpp}`,
`Pool/CasBlobUploadPool.{h,cpp}`, `Pool/CasPartWriteTxn.{h,cpp}`, `Pool/CasManifestReader.h`,
`Gc/CasGcScheduler.{h,cpp}`, `Parts/PartFolderAccess.{h,cpp}`, `ContentAddressedTransaction.cpp`
(fan-out and publish paths), plus `src/Common/ThreadPool.{h,cpp}` and
`programs/server/Server.cpp` for thread and pool semantics. Every `std::mutex`,
`std::condition_variable`, thread member, `.detach()` site and `TSA_*` occurrence in the CAS tree
was enumerated by search and inspected (see the inventory table).

Candidates investigated and **withdrawn** as unconfirmed: a data race on ref-table
`last_touch_tick` and on the recovery budgets (both serialised, see By-design); `finishTeardown`
allowing a post-teardown remount thread (both callers latch `remount_shutting_down` first,
`CasPool.cpp:564`/`:590`); destroying a locked `state_mutex` during remount (the keeper's renewal
thread is joined at `CasPool.cpp:725` before the pointer is replaced); a `state_mutex` →
`remount_thread_mutex` deadlock via `terminate()` → `on_lost()` → `scheduleRemount()`
(`CasServerRoot.cpp:970` / `CasMountRuntime.cpp:341`), which cannot fire because every path that
reaches `terminate()` has already latched `remount_shutting_down`; `std::terminate` from an
exception escaping a thread body (the global pool worker catches, `ThreadPool.cpp:989`);
`ThreadFromGlobalPool` move-assignment/destructor aborts (all sites are guarded by a `joinable()`
check or a prior join).

Not covered here by design: cross-node interleavings and linearizability, GC protocol invariants,
latency of blocking I/O under locks, and correctness of the ref-log/manifest formats. Dynamic
verification (TSan) was not run; all findings are static, and the two Medium findings that depend
on `Pool::renewWatermarkOnce()` / `mount_keeper` reads are explicitly marked as reachable only
through currently uncalled public seams.

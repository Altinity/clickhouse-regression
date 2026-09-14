# bc3-exception-safety -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is (read-only). CAS root `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (~36.6 kLOC, 21 `.cpp` files with exception handling).

Code-only: docs and comments were not treated as evidence of intent; only shipped strings, error codes and control flow. All CAS tests are deleted in the working tree, so no test evidence was used.

Audited: every `noexcept` function (21 declarations) and whether its body can throw; every destructor that performs work (9 out-of-line + 6 in-class); all 65 `catch (...)` sites including the 16 empty ones; RAII coverage of locks, leadership, in-flight build registrations, pending counters, admission latches, temp files and build handles; basic/strong guarantee of the mutating operations on the write path (`stageManifest`, `precommitAdd`, `promote`, `abandon`, `commitRefChunk`); exception propagation across `ThreadFromGlobalPool` and `ThreadPoolCallbackRunnerLocal`; error-code choice and callers' catch-by-code dispatch; `std::terminate` / `abort()` exposure via `ThreadFromGlobalPool` semantics (`src/Common/ThreadPool.h:376-408`, which calls `abort()` on move-assign/destroy of a joinable handle and on self-join).

Cited, not re-derived (sibling audits): the two `noexcept` rollback helpers in `Parts/PartFolderAccess.cpp:502-516` and `:518-562` that call the allocating `eraseView()` outside their `try`; the remount thread body in `Pool/CasMountRuntime.cpp:354-368` whose escaping exception disables self-healing; `dispatchSnapshotPublisher`'s `pin_owner()` outside the `try` in `Pool/CasRefLedger.cpp:2757`. Findings below that touch the same files address distinct sites and distinct triggers.

## Findings

### bc3-1 -- `dropNamespace` latches write admission closed and the only reopen path is swallowed by an empty catch (High)

- **Anchor**: `Pool/CasRefLedger.cpp:3451-3458` (latch), `:3517-3544` (recovery handler), `:3539` (empty catch), `:1451-1454` and `:1427-1430` (the refusal the latch produces).
- **Trigger**: `dropNamespace` sets `rt->removal_admission_closed = true` at `:3453` before it has made anything durable. The `try` at `:3465` then reads the catalog and calls `CasRefCatalog::beginRemoving`. A transient backend failure there (S3 5xx, timeout, fence check) lands in the handler at `:3517`, whose whole job is to re-read the catalog and, if the row is provably unchanged, reopen admission at `:3535`. That recovery read (`CasRefCatalog::read`, `:3521`) hits the *same* failing backend, so it very often throws too — and `catch (...) {}` at `:3539` discards it. Control falls to `:3542`, `removing_durable` is false, and the original exception is rethrown to the operator as a retryable error.
- **Guarantee violated**: basic guarantee on a mutating operation. `dropNamespace` fails but leaves the runtime half-updated: the namespace is still `Live` in the durable catalog, yet its cached runtime permanently refuses every positive ref mutation.
- **Evidence**: nothing else clears `removal_admission_closed` for a failed removal — the only other writers of `false` are the same `:3535` line and fresh runtime construction. Every subsequent `appendRefOpsOnRuntime` for that namespace throws at `:1428` or `:1452` with the text "is Removing: positive ref mutation admission is closed while its terminal fold and catalog removal complete; retry later", which is factually wrong (removal never began) and tells the operator to retry an operation that can never succeed. Inserts, merges, mutations and drops on every table in that namespace fail until remount or restart. The latch is not RAII-protected; a scope guard resetting it unless `removing_durable` would close the hole.

### bc3-2 -- append-lane leadership is released without RAII; a throw in the release path deadlocks the namespace forever (High)

- **Anchor**: `Pool/CasRefLedger.cpp:1519-1541` (`completeOwnedItemsAndReleaseLeadership`), specifically `:1531-1534`; the waiters at `:1488-1491`; the shutdown drain at `:1371-1385`.
- **Trigger**: `appendRefOpsOnRuntime` sets `rt->leader_active = true` at `:1474` and relies on `completeOwnedItemsAndReleaseLeadership` at `:1485` to clear it. That function allocates: `std::make_exception_ptr(Exception(...))` at `:1531` formats a message and heap-allocates the exception object. Under ClickHouse's `MemoryTracker` any allocation on a query thread can throw `MEMORY_LIMIT_EXCEEDED`, and `bad_alloc` is possible outside a query. If it throws, `rt->leader_active = false` (`:1539`) and `rt->cv.notify_all()` (`:1540`) never run.
- **Guarantee violated**: no guarantee at all — a resource (lane leadership) acquired at `:1474` has no unwind path. `std::lock_guard` releases the mutex, so other threads wake, see `leader_active == true`, and go back to `rt->cv.wait(lk)` at `:1490` with nobody left to notify them.
- **Evidence**: the wait at `:1490` is a bare `cv.wait` with no predicate and no timeout, so every writer to that namespace blocks permanently. `drainRefLanesForShutdown` at `:1373` waits on `!rt->leader_active`, so shutdown also stalls until its budget expires and then reports `timed_out`, which makes `Pool::~Pool` skip the clean-release marker (`CasMountRuntime.cpp:414-420`) and forces the next mount to treat the end as unclean. Note the same allocation-throw applies to the leader's own re-lock at `:1486`, but that one happens after leadership is released and only strands the caller.

### bc3-3 -- `Pool::~Pool` performs allocating, logging and joining work with no handler (Medium)

- **Anchor**: `Pool/CasPool.cpp:562-571`; the callees `Pool/CasRefLedger.cpp:1354-1396` and `Pool/CasMountRuntime.cpp:399-428`.
- **Trigger**: the destructor body has no `try`. `drainRefLanesForShutdown` allocates at `:1361-1364` (`reserve` + `push_back` over every ref-table runtime). `finishTeardown` formats and emits a `LOG_WARNING` at `CasMountRuntime.cpp:416-418` and calls `mount_keeper->stopBackground()` at `:419` — note the sibling `mount_keeper->stop()` branch at `:405-412` *is* wrapped in a `try`, the `:419` branch is not. Any exception (memory limit, `bad_alloc`, `std::system_error` from a mutex, a logger sink failure) escapes a destructor and terminates the process.
- **Guarantee violated**: destructors must not throw. This is a clean-shutdown path converted into `std::terminate`.
- **Evidence**: the asymmetry at `:405-412` vs `:419` shows the author knew `stopBackground()` is a throwing call. A second exposure compounds it: if the destructor unwinds before or during `stopRemountThread()`, `~CasMountRuntime` destroys a still-joinable `remount_thread`, and `ThreadFromGlobalPoolImpl::~ThreadFromGlobalPoolImpl` (`src/Common/ThreadPool.h:384-388`) calls `abort()` unconditionally. Both paths lose the graceful mount-lease farewell that the code at `CasServerRoot.cpp:984-986` exists to write.

### bc3-4 -- `putIfAbsentControlled` is the only conditional-write wrapper that swallows deterministic local failures, turning them into an UNCERTAIN ref-log wedge (Medium)

- **Anchor**: `Backend/CasRequestControl.cpp:271-281`; compare `:336-342`, `:396-402`, `:467-473`, `:535-541`, which all begin with `if (... isDeterministicLocalFailure(db_e->code())) throw;`. The consumer is `Pool/CasRefLedger.cpp:2453-2457` and its Unresolved handling at `:2706-2719`.
- **Trigger**: `backend->putIfAbsent` throws a `LOGICAL_ERROR`, `BAD_ARGUMENTS`, `NOT_IMPLEMENTED` or `CORRUPTED_DATA` — i.e. a deterministic, provably-never-landed local rejection (`isDeterministicLocalFailure`, `:90-94`). The catch at `:278` does not rethrow; it calls `classifyConditionalWriteResult`, which returns `Unresolved` for anything that is not a recognised S3 malformed/too-large/access-denied error (`:43-53`). The loop then re-issues the same doomed request `max_attempts` times and finally returns `Unresolved`.
- **Guarantee violated**: error-classification consistency. A definite failure is reported as an ambiguous one.
- **Evidence**: the ref-log append treats `Unresolved` as "this transaction may or may not be durable" and sets `rt->lane_state = RefLaneState::Wedged` at `Pool/CasRefLedger.cpp:2708-2710`, then refuses all further appends on that namespace until the *same key* resolves durable or is conclusively rejected. A local, deterministic bug or misconfiguration therefore wedges a namespace's write lane instead of failing that one call cleanly. The four sibling wrappers get this right, which makes the omission a defect rather than a design choice.

### bc3-5 -- `GcPhaseTimer::~GcPhaseTimer` allocates outside its guarded region (Medium)

- **Anchor**: `Gc/CasGcPhaseTimer.h:28-47`; the guard is only at `:46`.
- **Trigger**: the destructor builds `rec` before it reaches the `try`. `:38` takes a `ProfileEvents::Counters::Snapshot` (heap-allocated array) and `:39-44` inserts up to `num_counters` entries into `rec.profile_events`, each constructing a `String` key. Under a memory limit or `bad_alloc` this throws out of an implicitly-`noexcept` destructor.
- **Guarantee violated**: destructors must not throw; and this destructor most often runs while another exception is already in flight, since `GcPhaseTimer` is a scope object around GC phases — throwing during unwinding is an unconditional `std::terminate`.
- **Evidence**: the author wrapped `sink(rec)` at `:46` but not the record construction above it, so the intent to be non-throwing is explicit and the coverage is incomplete. The exposure scales with `ProfileEvents::Counters::num_counters` — the loop performs hundreds of allocations per phase exit.

### bc3-6 -- `noexcept` probe cleanup lambdas allocate outside their `try` (Medium)

- **Anchor**: `Backend/CasProbe.cpp:20-32` and `:218-228`.
- **Trigger**: `auto cleanup = [&]() noexcept { for (const auto & k : {key, cas_key}) { try { ... } catch (...) {} } }`. The braced list `{key, cas_key}` materialises a `std::initializer_list<String>` by copy-constructing both `String`s, which allocates. That happens in the loop header, outside the `try` at `:24`. A throw there hits the lambda's `noexcept` and terminates.
- **Guarantee violated**: a function declared `noexcept` can throw.
- **Evidence**: same shape as the two rollback helpers the sibling audit anchored in `Parts/PartFolderAccess.cpp:502-516` and `:518-562`, but distinct sites with a distinct allocating construct. Both probe lambdas are called on the capability-probe path that runs at mount, so the failure mode is "process aborts while mounting a CAS disk under memory pressure".

### bc3-7 -- `renewOnce` commits its state update before a callback that can throw, so a *successful* lease renewal can fence the mount (Medium)

- **Anchor**: `Pool/CasServerRoot.cpp:1026-1047`, especially `:1045-1046`; the caller `backgroundLoop` at `:1102-1128`.
- **Trigger**: `renewOnce` performs the durable `putOverwrite` at `:1038`, records the advance with `recordWrite(seq + 1, res.token)` at `:1045`, and only then calls the virtual `onRenewCommitted()` at `:1046`. `MountLeaseKeeper::onRenewCommitted` refreshes the confirmed deadline and can throw. `backgroundLoop` catches at `:1106` and cannot distinguish "the renewal never landed" from "the renewal landed and the post-commit bookkeeping failed": if the failure is not classified transient, it calls `onRenewFailed()` at `:1122`, which trips the mount fence and stops the keeper permanently (`:1119` "the mount lease stops advancing", then `return`).
- **Guarantee violated**: basic guarantee — the object is half-updated (seq/token advanced, deadline not refreshed) and the caller's recovery decision is made on incomplete information.
- **Evidence**: a related ordering hazard sits at `:1039-1045`: on `res.outcome != PutOutcome::Done` the code sets `last_renew_failure_was_confirmed_mismatch` and calls `onRenewMismatch`, but if an override returns instead of throwing (the base at `:1049-1053` throws, the contract is not enforced), execution falls through to `recordWrite(seq + 1, res.token)` and records the sequence and token of a *rejected* write as this writer's own state.

### bc3-8 -- `scheduleRemount` latches `remount_running` before a call that can throw, permanently disabling self-healing (Medium)

- **Anchor**: `Pool/CasMountRuntime.cpp:341-369`, specifically `:353-354` against the early-outs at `:346` and `:349-350`.
- **Trigger**: `remount_running.store(true)` at `:353` happens before `remount_thread = ThreadFromGlobalPool([this]{...})` at `:354`. The `ThreadFromGlobalPool` constructor schedules onto the global pool and throws (`CANNOT_SCHEDULE_TASK`) when the pool queue is saturated. The exception propagates out of `scheduleRemount` with `remount_running` still `true` and no scope guard to reset it.
- **Guarantee violated**: no unwind path for an acquired flag; the object is left in a state that permanently suppresses its own recovery.
- **Evidence**: every later `scheduleRemount` returns at `:346` or `:349` because `remount_running.load()` is true, and nothing else ever stores `false` except `:367` inside the thread body that was never started. Since `scheduleRemount` is the callback armed on lease loss (`:214-218`), the disk stays fenced and never re-mounts. The sibling audit anchored the complementary case — an exception escaping the loop body at `:355-367` skips the `:367` reset; this finding is the dispatch-side variant, and both share the missing RAII reset.

### bc3-9 -- an empty catch reclassifies any `gc/state` read failure as corruption and triggers a full baseline rebuild (Medium)

- **Anchor**: `Gc/CasGc.cpp:2633-2644`, empty catch at `:2641`; consequence at `:2645-2648` and `:2776-2781`.
- **Trigger**: `decodeGcState(got->bytes)` throws for any reason — genuine corruption, but equally `MEMORY_LIMIT_EXCEEDED` on a large state blob. The catch discards the exception, `decoded` stays empty, `healthy` is never set to `true`, and `rebuildBaseline` proceeds past the `:2776` refusal gate to rebuild the entire GC baseline at a new generation.
- **Guarantee violated**: a transient, recoverable condition is silently promoted to a permanent-damage verdict, and the discarded exception is the only evidence of which one it was.
- **Evidence**: the code demonstrably knows how to distinguish these — 20 lines below, at `:2656-2668`, the fold-seal read wraps the same kind of decode in `catch (const Exception & e)` and rethrows a `CORRUPTED_DATA` that quotes `e.message()`. The `gc/state` decode gets neither the message nor a log line.

### bc3-10 -- S3 staging objects of an aborted transaction are dropped from tracking without deletion (Low)

- **Anchor**: `ContentAddressedTransaction.cpp:148-172`, the `else if (committed)` at `:159` and the unconditional `st.pending_blobs.clear()` at `:170`.
- **Trigger**: the transaction is destroyed without commit (any exception on the write path) and `pb.backend == Cas::StagingBackend::S3`. The local-file branch at `:154-158` removes the temp file; the S3 branch only removes the object when `committed` is true. On the abort path the entry is cleared with no delete.
- **Guarantee violated**: RAII coverage of a remote resource — the only owner of that staging key drops it silently.
- **Evidence**: reclamation depends entirely on `sweepOwnMountStaging` (`Pool/CasServerRoot.cpp:1140-1168`), which runs only at mount start and, per its own log string at `:1161-1163`, is a leak-reclamation sweep rather than the primary owner. Long-lived servers with a high abort rate accumulate staging objects for the whole uptime, and the sweeper's own per-object failures are swallowed at `:1155`.

### bc3-11 -- `stageManifest` registers a durable manifest body in its debris list after the PUT (Low)

- **Anchor**: `Pool/CasPartWriteTxn.cpp:551-572`, specifically `:571-572` after the durable write at `:551`.
- **Trigger**: the manifest body is durable at `:551`; `staged_manifests.push_back(id)` / `staged_manifest_ids.insert(id)` at `:571-572` allocate and can throw. The body then exists in `_manifests` with no in-memory record.
- **Guarantee violated**: basic guarantee — durable side effect performed, bookkeeping not.
- **Evidence**: `cleanupStagedManifestDebrisBestEffort` (`:866-884`) iterates exactly `staged_manifests`, so an entry that never made it into the vector is never deleted on abandon; it survives until the orphan-manifest sweep. The window is narrow but the ordering is avoidable — reserving before the PUT would close it.

### bc3-12 -- empty catch around generation parsing can under-compute `max_gen` (Low)

- **Anchor**: `Gc/CasGc.cpp:2788-2801`, empty catch at `:2798`; consumer at `:2803`.
- **Trigger**: `std::stoull` on the generation path segment throws `std::out_of_range` (or `std::invalid_argument`) for a malformed key under the GC generation prefix. The key is skipped with no log and no counter.
- **Guarantee violated**: silent loss of input to a computation whose result (`generation = max_gen + 1`, `:2803`) must be strictly greater than every existing generation.
- **Evidence**: the surrounding code raises `CORRUPTED_DATA` for unparsable keys elsewhere (for example `Pool/CasRefProtocol.cpp:582-583` for a ref key under the ref prefix), so silently skipping here is inconsistent with the tree's own convention for unparsable keys under a known prefix.

## Error-code choice and catch-by-code dispatch

`CORRUPTED_DATA` currently carries three unrelated meanings in the CAS tree, and one of them is dispatched on by code:

1. "the durable bytes are damaged" — e.g. `Gc/CasGc.cpp:2610`, `Formats` decoders.
2. "the caller's operation is illegal against the current state" — the whole of `RefTableState::applyOwnerTransition` (`Pool/CasRefProtocol.cpp:198-269`) and `applySetPublishedAt` (`:272-288`). These are reachable, legitimate concurrency outcomes, not damage.
3. "a different object already occupies the exact key this attempt intended to create" — `Backend/CasRequestControl.cpp:236-238`, likewise a routine race with a successor's epoch seal.

`Pool/CasRefLedger.cpp:2461` branches on `getCurrentExceptionCode() != ErrorCodes::CORRUPTED_DATA` to decide between "wedge the lane" and "classify the occupant". That dispatch is currently *correct only by accident*: it works because meaning (3) is the only `CORRUPTED_DATA` that can escape `putIfAbsentControlled` today — meanings (1) and (2) are either caught earlier or not reachable on that call. But bc3-4 shows the same function deliberately swallows `CORRUPTED_DATA` raised by the backend at `:278`, and `isDeterministicLocalFailure` (`:90-94`) classifies `CORRUPTED_DATA` as a *local* deterministic failure — three different readings of one code within one file. A dedicated CAS code for "exact-key occupied" would make `:2461` explicit instead of coincidental. Reported here as a consistency hazard rather than a separate numbered finding, since no current caller misbehaves.

`LOGICAL_ERROR` is also used for reachable, non-programming-error conditions on the ref path: `Pool/CasRefLedger.cpp:2443-2446` ("lane changed before attempt could be armed") and `:2643-2647` ("durable but this table changed before installation") are concurrency outcomes, and `Pool/CasPartWriteTxn.cpp:599-602` fires from inside a mutator lambda evaluated against live state. `LOGICAL_ERROR` triggers `chassert`/abort behaviour in debug builds and is filtered as a bug by operators, so these are mislabeled.

## Empty/broad catch inventory

All 16 empty `catch (...)` sites in the CAS tree.

| anchor | what is swallowed | risk |
|---|---|---|
| `Pool/CasRefLedger.cpp:3539` | failure of the catalog re-read that is the sole path to reopen write admission after a failed `dropNamespace` | **High** — permanent write refusal for a live namespace (bc3-1) |
| `Pool/CasServerRoot.cpp:1124` | failure of `onRenewFailed()` — the fence/remount notification after a lost lease | High — the mount believes it is fenced but the remount may never be scheduled; pairs with bc3-8 |
| `Pool/CasServerRoot.cpp:1133` | failure of `onRenewSucceeded()` — the deadline refresh after a durable renewal | Medium — the fence deadline silently stops advancing while the lease is healthy; the mount self-fences on a wall-clock timeout |
| `Pool/CasServerRoot.cpp:1155` | per-object delete failure in the mount-start staging sweep | Low — leaked staging objects stay leaked, no counter, no log; amplifies bc3-10 |
| `Pool/CasServerRoot.cpp:1165` | any failure of the whole staging sweep, including the `listObjects` that drives it | Low-Medium — the sweep can be a total no-op every mount with zero observability |
| `Pool/CasRefLedger.cpp:1558` | logger failure inside `requireRecovery` | Low — correct; the state transition above it is already complete and unconditional |
| `Pool/CasRefLedger.cpp:2482` | failure to read back the occupant of a contended ref-log key | Low — handled: `classified` stays false and `:2485-2499` faults the lane with an explicit message |
| `Pool/CasPool.cpp:812` | logger failure inside the already-`noexcept` `enqueueWriterCleanupDuty` | Low — correct; `writer_cleanup_queue_failed` is latched at `:805` before the log attempt |
| `Pool/CasPartWriteTxn.cpp:880` | head/delete failure while removing never-precommitted staged manifest debris | Low — explicitly best-effort, reaped later by the orphan-manifest sweep |
| `ContentAddressedTransaction.cpp:165` | delete failure of a committed transaction's S3 staging object | Low — leak only; see bc3-10 for the abort path that does not even attempt the delete |
| `Gc/CasGcScheduler.cpp:121` | failure of the `system.cas_gc_log` row emission | Medium — GC rounds can complete with no durable record at all; the round itself is unaffected but post-hoc diagnosis is impossible |
| `Gc/CasGc.cpp:2641` | any failure decoding `gc/state`, including memory-limit | Medium — reclassified as corruption, forces a full baseline rebuild (bc3-9) |
| `Gc/CasGc.cpp:2798` | `std::stoull` failure while computing the highest existing GC generation | Low — silently under-counts generations (bc3-12) |
| `Gc/CasGcPhaseTimer.h:46` | phase-record sink failure | Low in itself — but the unguarded allocation *above* it is bc3-5 |
| `Backend/CasProbe.cpp:30` | head/delete failure cleaning up the capability-probe objects | Low — probe debris; the allocation outside the `try` is bc3-6 |
| `Backend/CasProbe.cpp:226` | same, second probe | Low — same as above |

None of the 16 swallows a durability *acknowledgement*: every site where a durable write's outcome matters uses either `tryLogCurrentException` with a specific message or an explicit state transition. The two that come closest are `Pool/CasServerRoot.cpp:1124` and `:1133`, which discard the outcome of the mount-fence callbacks that guard durability admission.

## Checked and sound

- **`mergeBlobUploadResults` gives the strong guarantee** — `Pool/CasPartWriteTxn.cpp:216-225` copies `deps` into `candidate`, applies all results (with the test hook able to throw mid-loop at `:222-223`), and only then `deps.swap(candidate)`. A throw at any point leaves `deps` exactly as it was.
- **The ref-log install region is genuinely non-throwing** — `Pool/CasRefLedger.cpp:2604-2620` runs the state publication under `DENY_ALLOCATIONS_IN_SCOPE`, and every operation inside is provably `noexcept`: `RefTableState::swap` is `noexcept` and backed by `static_assert`s on each member's swap (`Pool/CasRefProtocol.cpp:172-181`), plus relaxed `fetch_add`s. The `catch` at `:2616` calls `requireRecovery` before rethrowing, so the lane cannot silently continue with a half-installed state.
- **Abandoning an UNCERTAIN promote cannot corrupt durable state.** `PreparedPartWrite::promote` (`Parts/PartFolderAccess.cpp:368-379`) calls `abandonBuildBestEffort` unconditionally on failure, including when `commitIsUnresolved()` is true — the worrying shape. It is safe because the abandon's removal op is validated against live state: `applyOwnerTransition`'s `RemovePrecommit` case throws when the exact precommit binding is absent (`Pool/CasRefProtocol.cpp:221-231`), so a promote that actually landed makes the abandon fail before anything durable is written. The wedge machinery reinforces this: after an unresolved append the lane is `Wedged` (`Pool/CasRefLedger.cpp:2708-2710`) and refuses further appends until `resolveWedgeOnce` adjudicates.
- **`fanOutBlobUploads` propagates worker exceptions correctly** — `ContentAddressedTransaction.cpp:1181-1209`: `SCOPE_EXIT_SAFE` at `:1187` guarantees every task is joined even if enqueueing throws mid-loop, `waitForAllToFinishAndRethrowFirstError` at `:1206` surfaces the first worker error, and `mergeBlobUploadResults` at `:1209` runs only on the success path, so a partially-filled `results` vector is never merged.
- **`precommitAdd` is ordered fail-safe** — `Pool/CasPartWriteTxn.cpp:587-590` records `precommit_target_ns` / `precommit_final_ref` / `precommit_manifest` and sets state to `Uncertain` *before* the durable append, so `~PartWriteTxn` (`:105-115`) can always enqueue the cleanup duty. `abandon` mirrors this with `tolerate_absent` derived from the same state (`:809`).
- **`drainWriterCleanupDuties` unwinds its own flag** — `Pool/CasPool.cpp:844-895`: the `catch (...)` at `:887` clears `draining` and notifies before rethrowing, so a failed drain does not strand the queue.
- **`enqueueWriterCleanupDuty` is correctly `noexcept`** — `Pool/CasPool.cpp:789-816`: all allocating work is inside the `try`, the failure latch is set before the nested log attempt, and `writerCleanupDutiesPending` (`:818-826`) reads that latch first so the watermark stays conservative when the queue could not be recorded.
- **All `WriteSink` destructors delegate to a `noexcept` cancel** — `Backend/CasObjectStorageBackend.cpp:212-222` and `:250-260`, `Backend/CasInMemoryBackend.cpp:44-54`, `Backend/CasInstrumentedBackend.cpp:146`. Same for `CaContentWriteBuffer::~CaContentWriteBuffer` (`ContentAddressedTransaction.cpp:1262-1267`), whose `cancelImpl` and `removeTempFile` are both `noexcept` and use the `std::error_code` overload of `fs::remove` (`:1307-1311`).
- **`ContentAddressedTransaction::~ContentAddressedTransaction`** (`:101-123`) guards each `build->abandon()` individually, so one failing build does not skip the others.
- **`CasRefLedger::requireRecovery`** (`:1543-1561`) honours its `noexcept`: the state transition is done first, the only throwing call (the log) is guarded, and `ProfileEvents::increment` on a fixed event does not allocate.
- **`RefTableState::swap`** (`Pool/CasRefProtocol.cpp:172-181`) backs its `noexcept` with `static_assert`s rather than assertion by comment — the correct pattern, and the reason bc3-2's failure mode is confined to the leadership flag rather than the state itself.

## Coverage

| Area | Reviewed | Result |
|---|---|---|
| `noexcept` functions | 21 declarations across 13 files, each body traced for allocation, `String`/`fmt` formatting, logging, `ProfileEvents`, `shared_ptr` and container growth | 2 confirmed violations (bc3-6, plus the two sibling-cited helpers in `PartFolderAccess.cpp`); the rest sound |
| Destructors doing work | 9 out-of-line (`ContentAddressedTransaction`, `CaContentWriteBuffer`, `CaInlineWriteBuffer`, `PreparedPartWrite`, `PartWriteTxn`, `CasGcScheduler`, `SingleWriterSlot`, `Pool`) + 6 in-class (`MountLeaseKeeper`, `GcPhaseTimer`, 3 `WriteSink`s, `IBlobHashingWriteBuffer`) | 2 confirmed (bc3-3, bc3-5); the rest guarded |
| `catch (...)` sites | 65 total, 16 empty | full inventory above; 3 raised to findings (bc3-1, bc3-9, bc3-12) |
| RAII coverage of acquired state | lane leadership, `removal_admission_closed`, `remount_running`, `pending_snapshot_publishes`, in-flight build seqs, writer-cleanup `draining`, temp files, S3 staging keys, build handles | 4 gaps (bc3-1, bc3-2, bc3-8, bc3-10); `SCOPE_EXIT` at `CasPool.cpp:906` and the `draining` unwind at `:887-895` are correct |
| Mutating-op guarantees | `stageManifest`, `precommitAdd`, `promote`, `abandon`, `commitRefChunk`, `renewOnce`, `mergeBlobUploadResults`, `publishStaging` | 2 half-update windows (bc3-7, bc3-11); the ref-log install and the dep merge are strong |
| Thread/future boundaries | `ThreadFromGlobalPool` uses in `CasServerRoot`, `CasMountRuntime`, `CasGcScheduler`, `CasRefLedger`; `ThreadPoolCallbackRunnerLocal` in `fanOutBlobUploads`; detached publisher thread | fan-out sound; detached publisher's `pin_owner` gap cited to sibling; `abort()` exposure via `ThreadPool.h:376-408` feeds bc3-3 and bc3-8 |
| Error-code consistency | `CORRUPTED_DATA`, `LOGICAL_ERROR`, `BAD_ARGUMENTS`, `NETWORK_ERROR`, `INVALID_STATE`, `ABORTED` across all throw sites and every catch-by-code consumer | 1 confirmed misclassification (bc3-4); the `CORRUPTED_DATA` overloading and `LOGICAL_ERROR`-for-reachable issues documented above as hazards |
| Throw-during-unwinding / `std::terminate` | every destructor and `noexcept` boundary | bc3-3, bc3-5, bc3-6 are live `std::terminate`/`abort()` exposures |

Not covered: `benchmarks/`, `Tools/CasInspect.cpp` and `Tools/CasFsck.cpp` beyond their `catch (...)` sites (read-only diagnostics — their broad catches record `unchecked` verdicts, which is the correct fail-soft shape for a checker); runtime behaviour of any kind. Static reasoning only.

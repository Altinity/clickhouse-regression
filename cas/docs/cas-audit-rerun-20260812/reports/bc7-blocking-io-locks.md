# bc7-blocking-io-locks -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is.
CAS root: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.
Code-only: docs and comments are not evidence; shipped strings, defaults and control flow are. All CAS tests are deleted in the working tree.

This audit covers *blocking object-store I/O performed while a lock is held*, and the resulting stalls: latency, convoying and availability. Data races are the concurrency audit's problem; here the question is only "who cannot proceed, and for how long".

The numbers below are computed from the shipped defaults, not from prose:

* `CasRequestBudget` (`Backend/CasRequestControl.h:84-93`): `attempt_timeout_ms=5000`, `operation_deadline_ms=90000`, `max_attempts=16`, `lease_safety_margin_ms=2000`, `retry_initial_backoff_ms=200`, `retry_max_backoff_ms=5000`, `recovery_retry_budget_ms=120000`, `recovery_retry_initial_backoff_ms=1000`, `recovery_retry_max_backoff_ms=30000`.
* `PoolConfig` (`Pool/CasPool.h:73-74`): `mount_lease_ttl_ms=30000`, `mount_renew_period=10000`.
* `ContentAddressedSettings.cpp:40-49`: per-round GC object budgets (`manifest_sweep_list_budget_keys=1000`, `gc_round_graduation_budget=5000`, `gc_round_redelete_budget=5000`, `gc_round_ref_cleanup_budget=5000`, `gc_round_prefix_wholesale_budget=20000`, `gc_round_handoff_prefix_wholesale_budget=5000`, `gc_round_outcome_entry_budget=5000`); `gc_meta_pool_size=16`. There is no wall-clock GC round deadline setting.
* `ServerSettings.cpp:151`: `cas_blob_upload_pool_size=16`.
* S3 client (`src/IO/S3Defines.h:9-37`): `DEFAULT_CONNECT_TIMEOUT_MS=1000`, `DEFAULT_REQUEST_TIMEOUT_MS=30000`, `DEFAULT_RETRY_ATTEMPTS=500`.

**Derived unit cost — one "controlled write"** (`putIfAbsentControlled`, `conditionalCreateControlled`, `putOverwriteControlled`): the deadline is a *pre-send gate only* (`CasRequestControl.cpp:264, 328, 388, 459`), so the loop admits a new attempt while `now + 5000 <= deadline`. Backoff sum over 16 attempts is `200+400+800+1600+3200+5000*10 = 56.2 s`, below the 90 s deadline, so the deadline binds. Worst case per controlled write = **~90 s of gated attempts + one in-flight conditional PUT (<= ~31 s, single-attempt client) + one in-flight `resolveByExactGet` read (see bc7-4: bounded only by 500 x 30 s)**. I write this as **~121 s nominal / unbounded if reads hang** throughout.

**Derived cost — one part publish** (`ContentAddressedTransaction::publishStaging` -> `PartWriteTxn::stageManifest` + `precommitAdd` + `promote`, `Pool/CasPartWriteTxn.cpp:551, 592, 657`): 3 controlled writes + 1 manifest GET => **~363 s nominal**. A part *rename* (`republishRef`) adds a fourth (`dropRef`) => **~484 s nominal**.

Cited, not re-derived (siblings own these): `SYSTEM CAS FSCK` holds `lifecycle_mutex` unbounded (`ContentAddressedMetadataStorage.cpp:741`); the writer-cleanup drain waits with no timeout (`Pool/CasPool.cpp:831-836`); remount *stop* can stall 30 s under the remount thread mutex (`Pool/CasMountRuntime.cpp:348-352`); the GC rebuild scan has no deadline (`ContentAddressedMetadataStorage.cpp:496-504`). bc7-6 below is a *different* lock (`Pool::remount_mutex`, the remount body) and is reported here.

## Locks held across I/O

| Lock | I/O performed under it | Worst-case hold | Who is blocked | Anchor |
|---|---|---|---|---|
| `MergeTreeData` `DataPartsLock` | full CAS part publish: blob PUT fan-out + manifest PUT + 2 ref-log conditional PUTs (+ GETs) | ~363 s nominal, unbounded if reads hang | every INSERT, merge/mutation commit, part-set read, `system.parts`, DDL on that table | `src/Storages/MergeTree/MergeTreeData.cpp:5918-5922`; `preparePartForCommit` rename at `:5545-5546` |
| ref-append lane leadership (`RefTableRuntime::leader_active`, followers on `rt->cv`) | leader runs the whole `flushRefBatch`: conditional PUT of the ref-log chunk, occupant GET, wedge `slotOccupy`, checkpoint publish | leader flush, repeated until the follower's item is carved; >= 121 s per controlled write, no follower deadline | all writers to the same namespace (= one table): inserts, merges, mutations, drops, and `DROP TABLE` | `Pool/CasRefLedger.cpp:1490`, leader loop `:1508-1516`, write `:2455` |
| `CasGcScheduler::gc_round_mutex` | one entire GC round: LIST/GET/PUT/DELETE up to the per-round object budgets, plus `meta_pool->wait()` | no wall-clock bound; ~40 k object ops at default budgets (~67 min at 100 ms/op) | `SYSTEM CAS GC ROUND` (manual), and via `stop()`'s `thread.join()` also `SYSTEM CAS GC STOP`, `shutdown()`, `forgetDisk` | `Gc/CasGcScheduler.cpp:213, 245`, join `:74-77`, `Gc/CasGc.cpp:778` |
| `ContentAddressedMetadataStorage::gc_scheduler_mutex` | held *around* the manual GC round and the rebuild | same as above | `SYSTEM CAS GC STOP/START`, `shutdown()`, `forgetDisk` | `ContentAddressedMetadataStorage.cpp:468-486, 634, 692, 712, 664` |
| `Pool::remount_mutex` | lifecycle probe, catalog read, owner claim, epoch mint, **lease-expiry polling sleep**, recovery quiescence, publish settle | >= 30 s (lease TTL) + 120 s (recovery budget) + publish settle | `SYSTEM CAS FORGET DISK` (`enterVanished`), any other remount attempt | `Pool/CasPool.cpp:635, 702-712, 732-733`, waiter `:603` |
| `RefTableRuntime::recovery_in_progress` + `recovery_cv` | the recovery walk (ref-log/snapshot GET chain) is run with `state_mutex` dropped, but every other toucher waits on the cv | 120 s retry budget + one final walk | every reader and writer of that namespace: `resolveRef`, `listRefs`, all appends | `Pool/CasRefLedger.cpp:969-974`, walk `:1022-1034`, budget `:1064` |
| `CachedPartFolderAccess::inflight` single-flight future | leader's `readManifestShared` (HEAD + GET of the manifest body) | one manifest read on the default retry profile (see bc7-4) | every thread loading the same part: concurrent SELECTs, merge source reads, fetches | `Parts/PartFolderAccess.cpp:240-252` |
| `Cas::blobUploadPool()` (16 threads, process-global) | every blob body PUT of every CAS part commit | caller waits for all its tasks, no deadline | every concurrent CAS part commit on the server, across all CAS disks | `Pool/CasBlobUploadPool.cpp:45-49`, wait `ContentAddressedTransaction.cpp:1187, 1206` |
| `ObjectStorageBackend::emu_mutex` (emulated mode) | 2-3 round trips per operation (exists + body + head) inside one lock | serialized; N waiters x 3 round trips | every CAS metadata read and write on that disk | `Backend/CasObjectStorageBackend.cpp:491-507, 651, 715, 763` |
| `emulated_resurrect_mutex` (function-static, process-wide) | full blob body read + full body write | one blob body transfer | blob resurrect on *every* CAS disk in the process | `Backend/CasObjectStorageBackend.cpp:819-832` |

## Findings

### bc7-1 -- A CAS part publish runs to the object store while `DataPartsLock` is held (High)

- **Anchor**: `src/Storages/MergeTree/MergeTreeData.cpp:5918-5922` (`renameTempPartAndAdd(..., lock, /*rename_in_transaction=*/false)` then, CAS-specifically, `getDataPartStorage().commitTransaction()` — both inside the caller's `DataPartsLock & lock`); rename path `MergeTreeData.cpp:5545-5546` -> `DataPartStorageOnDiskBase.cpp:780-789` -> `ContentAddressedTransaction::moveDirectory` (`ContentAddressedTransaction.cpp:961`) and `ContentAddressedTransaction::commit` (`:312-352`) -> `publishStaging` (`:244-310`) -> `uploadPendingBlobs` (`:208-242`) + `PartWriteTxn::stageManifest/precommitAdd/promote` (`Pool/CasPartWriteTxn.cpp:551, 592, 657`).
- **Trigger**: `DROP PARTITION` / `REPLACE PARTITION` / any `removePartsInRangeFromWorkingSetAndGetPartsToRemoveFromZooKeeper` that creates the empty covering part on a CAS disk, while the object store is slow, throttling, or returning 5xx.
- **Worst-case stall**: the empty-part publish is 3 controlled writes plus its blob PUTs: **~363 s nominal**, unbounded if any read inside the loop hangs (bc7-4). The lock is not released for any part of it.
- **Who is blocked**: every thread that needs `lockParts()` on that table — all INSERT commits, all merge and mutation commits, `system.parts`/part-set snapshots, `ALTER`, `DROP`, `OPTIMIZE`. On a replicated table the queue executor blocks with them.
- **Evidence**: the shipped code explicitly forces the commit under the lock for CAS only (`if (new_data_part->getDataPartStorage().isContentAddressed() && ...hasActiveTransaction()) ...commitTransaction();` at `:5920-5922`), i.e. the CAS network commit is deliberately inside the `DataPartsLock` region rather than deferred like the `rename_in_transaction=true` paths at `StorageMergeTree.cpp:3250-3268`, which call `renameParts()` after dropping the lock.

### bc7-2 -- The ref-append lane is a single-flight leader and followers have no deadline (High)

- **Anchor**: `Pool/CasRefLedger.cpp:1457-1492` (`while (!item->done) { if (!rt->leader_active) {... runRefQueueLeader ...} else rt->cv.wait(lk); }`); leader loop `:1508-1516`; the leader's object-store write `:2455-2456`; occupant GET `:2476`; wedge `slotOccupy` `:1639`.
- **Trigger**: two or more concurrent writers to the same table namespace (concurrent INSERTs, or an INSERT racing a merge commit) while the ref-log conditional PUT is slow or ambiguous.
- **Worst-case stall**: a follower waits for the leader's *entire* flush. One flush contains at least one controlled write (>= ~121 s) and, on a wedge, a `slotOccupy` plus an occupant GET; `runRefQueueLeader` loops until the leader's own item is done, so a follower can span several flushes. No `wait_for`, no `wait_until`, no deadline on the follower side, and no interruption point — a `KILL QUERY` cannot free the waiting thread because `rt->cv.wait(lk)` does not consult query cancellation.
- **Who is blocked**: all mutating traffic for that one namespace (one table UUID): inserts, merges, mutations, `dropRefIfMatches` rollbacks, and `dropNamespace` (bc7-8).
- **Evidence**: the drain-for-shutdown path in the very same file *does* use a deadline (`rt->cv.wait_until(lk, deadline)` at `:1375`), which shows the deadline-carrying variant was available and was not used on the foreground follower path.

### bc7-3 -- `SYSTEM CAS GC STOP` and shutdown serialize behind the whole in-flight GC round (High)

- **Anchor**: `Gc/CasGcScheduler.cpp:213` (`runOneRoundNow`: `std::lock_guard round_lock(gc_round_mutex)`), `:245` (background `loop()` takes the same mutex for the round), `:67-79` (`stop()` sets the flag, then `thread.join()`), `Gc/CasGc.cpp:778` (`meta_pool->wait()` inside the round); `ContentAddressedMetadataStorage.cpp:468` (manual round under `gc_scheduler_mutex`), `:692` (`gcStop` needs the same `gc_scheduler_mutex`), `:634` (`shutdown` likewise).
- **Trigger**: an operator issues `SYSTEM CAS GC STOP`, or the server shuts down, while a GC round is in flight against a slow or throttling bucket.
- **Worst-case stall**: a round has *object-count* budgets but no wall-clock deadline. At defaults a single round may issue on the order of 40 000 object operations (20 000 wholesale prune deletes + 5 000 graduation + 5 000 redelete + 5 000 ref cleanup + 5 000 hand-off + 1 000 sweep LIST keys) — **~67 min at 100 ms/op**, and unbounded if any of them hits the default retry profile (bc7-4). `stop()` cannot shorten it: the stop flag is only read between rounds at `:227-230`, and the round itself never polls it.
- **Who is blocked**: the operator's `SYSTEM CAS GC STOP` and `SYSTEM CAS GC START` sessions, a manual `SYSTEM CAS GC ROUND`, `ContentAddressedMetadataStorage::shutdown()` (hence disk detach and server shutdown), and `forgetDisk`.
- **Evidence**: shipped operator-facing strings assume the stop verb is actionable (`"SYSTEM CAS GC STOP on content-addressed disk '{}': no GC scheduler ..."`, `ContentAddressedMetadataStorage.cpp:701-703`) while the code path to `snapshot->stop()` at `:706` is gated on a mutex that the running round holds. `meta_pool->wait()` at `Gc/CasGc.cpp:778` adds an unbounded join for up to `gc_meta_pool_size=16` in-flight freshness-meta writes inside that region.

### bc7-4 -- `attempt_timeout_ms` never reaches the wire; CAS reads run on a 500-retry client (High)

- **Anchor**: `Backend/CasRequestControl.h:84`; every use of it is arithmetic — `CasRequestControl.cpp:202, 264, 328, 388, 459, 526` (pre-send gate) and `Pool/CasMountRuntime.cpp:109`, `Pool/CasPool.cpp:567, 595` (lease margin). No call site passes it into `ReadSettings`/`WriteSettings` or the S3 client. Conditional *writes* do get a single-attempt client (`Backend/CasObjectStorageBackend.cpp:638` -> `S3ObjectStorage.cpp:351-354` -> `getSingleAttemptClient()` at `:895-913`, `max_retries = 0`), but reads, HEADs and LISTs go through the base client, whose shipped defaults are `DEFAULT_RETRY_ATTEMPTS=500` and `DEFAULT_REQUEST_TIMEOUT_MS=30000` (`src/IO/S3Defines.h:9-37`).
- **Trigger**: a bucket that accepts connections but stalls or 5xx-loops (throttling, partial partition, endpoint blackhole).
- **Worst-case stall**: one CAS read can occupy **up to 500 x 30 s ≈ 4.2 h** before returning. Because the operation deadline is only checked *before* an attempt, a controlled write that entered its last attempt at 89 999 ms can sit in `resolveByExactGet` (`CasRequestControl.cpp:212-239`, `:292`) for that whole time. `head` in `conditionalCreateControlled` (`:361`) and `get` in `putOverwriteControlled` (`:416`) are the same.
- **Who is blocked**: whoever holds the lock at that moment — which, per bc7-1/bc7-2/bc7-3/bc7-5, is `DataPartsLock`, the ref lane, `gc_round_mutex`, or the part-folder single flight. This finding is what makes every other worst case in this report formally unbounded rather than merely long.
- **Evidence**: `validateCasRequestBudget` refuses budgets whose `attempt_timeout_ms` violates the lease arithmetic (`CasRequestControl.cpp:106-112`) and logs `"CAS request budget in effect: attempt_timeout_ms={} ..."` (`:127-133`) — the shipped strings present it as an enforced per-attempt timeout, while no attempt is actually cancelled at 5 s.

### bc7-5 -- Part-folder single flight: followers block on `future.get()` with no deadline and no cancellation (Medium)

- **Anchor**: `Parts/PartFolderAccess.cpp:240-252` (`inflight_mutex` selects a leader; `if (!leader) return future.get();`), leader read `:260` (`store->readManifestShared(...)`).
- **Trigger**: several query threads open the same part concurrently (a SELECT with many streams, a merge reading a part another query is loading) and the leader's manifest HEAD+GET stalls.
- **Worst-case stall**: the leader's manifest read, on the default retry profile — nominally one 30 s request, up to ~4.2 h under bc7-4. `std::shared_future::get()` has no timeout variant here and does not observe query cancellation, so the followers are unkillable for the duration.
- **Who is blocked**: all query threads touching that part; at scale, threads accumulate on the query pool while blocked.
- **Evidence**: the surrounding cache code carefully bounds *memory* (`part_folder_cache_bytes`, `max_entries`, `max_entry_bytes` at `ContentAddressedSettings.cpp:52-54`) but there is no corresponding time bound on the coalescing wait; the `SCOPE_EXIT` at `:254-257` only guarantees the slot is freed, not that it is freed promptly.

### bc7-6 -- `Pool::remount_mutex` is held across lease-expiry polling and two quiescence waits (Medium)

- **Anchor**: `Pool/CasPool.cpp:635` (`std::lock_guard serialize(remount_mutex)`), then `:702-712` `claimMountAwaitingExpiry(..., ttl_ms, poll_interval_ms, sleep_ms, ...)` with `sleep_ms = std::this_thread::sleep_for` (`:701`), `:732` `cancelRecoveriesAndAwaitQuiescence()`, `:733` `quiesceRefTablesForRemount()`. Waiter: `Pool::forgetDisk` takes the same mutex at `:603`.
- **Trigger**: a fence-out (lease renewal failure) triggers a self-remount while a stale twin lease is still within its TTL, and an operator concurrently issues `SYSTEM CAS FORGET DISK`.
- **Worst-case stall**: `mount_lease_ttl_ms = 30 s` of polling sleep (`Pool/CasPool.h:73`, poll interval `mount_renew_period/2 = 5 s`) **+** `recovery_retry_budget_ms = 120 s` for `cancelRecoveriesAndAwaitQuiescence`, whose `recovery_cv.wait(slock, ...)` at `Pool/CasRefLedger.cpp:1140-1141` has no timeout, **+** `quiesceRefTablesForRemount`'s `publish_settle_cv.wait` at `:1226-1228`, also untimed, which waits for in-flight snapshot publishes (each a controlled write, >= ~121 s). **>= 150 s, realistically ~270 s.**
- **Who is blocked**: the operator's `SYSTEM CAS FORGET DISK` and every subsequent remount attempt.
- **Evidence**: the cancel flag is set before the wait (`CasRefLedger.cpp:1136`), so the wait is expected to be short — but the walk only samples it at `checkRecoveryStillAdmitted` (`:502-510`), i.e. between object-store round trips, so a single hung GET (bc7-4) defers the whole chain. Distinct from the sibling finding on `remount_thread_mutex` (`CasMountRuntime.cpp:348-352`).

### bc7-7 -- Ref-table recovery blocks every reader of the namespace for up to the recovery retry budget (Medium)

- **Anchor**: `Pool/CasRefLedger.cpp:956-1106`; waiters `:969-974` (`rt.recovery_cv.wait(lock)` — no predicate deadline); retry budget `:1064` and `:1095`; retry sleep `:1084-1087` (`recovery_retry_sleep_fn`, `:174-181`). Entered from every read: `resolveRef` `:220`, `listRefs` `:266`, `hasAnyRefWithPrefix` `:286`, and every append `:1433`.
- **Trigger**: a lane enters `NeedsRecovery` (ambiguous ref-log append) while the object store is throwing transient errors; the first toucher becomes the recoverer and everyone else queues.
- **Worst-case stall**: the recoverer retries with capped-exponential backoff (`1 s -> 30 s`) until `recovery_retry_budget_ms = 120 s` elapses, then throws; add the final in-flight walk (many GETs, each subject to bc7-4). Waiters get **~120 s + one walk** before they see the retry-later error.
- **Who is blocked**: every SELECT that resolves a ref on that table, plus every writer — a read path stalling on a *write*-side recovery is the availability cost here.
- **Evidence**: the wait at `:972` is the plain `wait(lock)` overload while the same class uses `wait_until` with a budget elsewhere (`:1375`); the code path is reached from read-only entry points (`resolveRef` at `:217-220`), so `allow_stale=true` readers are not exempt.

### bc7-8 -- `DROP TABLE` waits for the in-flight publish leader with no deadline (Medium)

- **Anchor**: `Pool/CasRefLedger.cpp:3451-3458` (`rt->removal_admission_closed = true; rt->cv.wait(queue_lock, [&]{ return !rt->leader_active && rt->pending.empty(); });`) inside `dropNamespaceImpl`.
- **Trigger**: `DROP TABLE` / `RENAME TABLE` on a CAS table while an INSERT's ref-log append is in flight against a slow store.
- **Worst-case stall**: one leader flush, i.e. >= ~121 s per controlled write and unbounded under bc7-4. The DDL thread holds the table's DDL/exclusive lock for the duration.
- **Who is blocked**: the `DROP`/`RENAME` session and everything queued behind the table's exclusive lock (subsequent DDL, and in `RENAME TABLE`'s case the database mutex holder).
- **Evidence**: admission is closed *before* the wait, so no new work can extend it — the exposure is exactly the current leader's object-store round trips, which have no cap.

### bc7-9 -- One 16-thread process-global pool serializes all CAS blob uploads; callers wait without a deadline (Medium)

- **Anchor**: `Pool/CasBlobUploadPool.cpp:45-49` (a single `pool_instance`, size from `cas_blob_upload_pool_size`, default 16 at `src/Core/ServerSettings.cpp:151`), obtained per commit at `ContentAddressedTransaction.cpp:241` (`Cas::blobUploadPool()`); fan-out and wait at `:1181-1207` (`waitForAllToFinish` in `SCOPE_EXIT_SAFE` at `:1187`, `waitForAllToFinishAndRethrowFirstError` at `:1206`).
- **Trigger**: 16 or more concurrent slow blob PUTs — e.g. a few large parts committing while the bucket throttles — on any CAS disk in the process.
- **Worst-case stall**: head-of-line blocking. Every other CAS part commit's tasks queue behind the 16 stuck PUTs, and each waiting commit thread sits in `waitForAllToFinish*` with no deadline while holding its transaction (and, in the bc7-1 shape, `DataPartsLock`). A single blob PUT is a `WriteBufferFromS3` on the single-attempt client, so ~31 s per part upload, but a multipart body is many such requests.
- **Who is blocked**: every concurrent CAS part commit *across all CAS disks*, since the pool is a namespace-scope singleton, not per disk.
- **Evidence**: `blobUploadPool()` returns the one static instance under `pool_mutex` (`:52-59`) with no per-disk keying; the pool is dedicated (not the shared IO pool) and the tasks do not re-enter it, so this is convoying rather than a self-deadlock — see "Checked and sound".

### bc7-10 -- Emulated mode holds one mutex across 2-3 round trips per operation, and a process-wide mutex across a whole blob body (Low)

- **Anchor**: `Backend/CasObjectStorageBackend.cpp:491-507` (`get`: `emu_mutex` held across `emuExists` HEAD + `emuRead` full-body GET + `emuObserveToken` HEAD), `:533-545` (`getStream`), `:651-660` (`putIfAbsent`: exists + write + head), `:687`, `:715`, `:763`; helpers `:418-445`. Process-static lock: `:819-832` (`static std::mutex emulated_resurrect_mutex;` held across the body build and `emuWrite`).
- **Trigger**: a content-addressed disk over local object storage — selected automatically at `ContentAddressedMetadataStorage.cpp:509-511` (`object_storage->getType() == ObjectStorageType::Local ? EmulatedSingleProcess : Native`).
- **Worst-case stall**: every CAS metadata operation on that disk is fully serialized, each holding 2-3 round trips; with N concurrent operations the last one waits `N x 3` round trips. The resurrect mutex is function-static, so it serializes blob resurrects across *every* CAS disk in the process for the duration of a full body read plus a full body write.
- **Who is blocked**: all readers and writers of that disk; for resurrect, all CAS disks.
- **Evidence**: the shipped startup string at `:515-520` presents emulated mode as a supported single-server configuration ("safe ONLY for a single server ... Use an S3-backed pool for multi-server"), i.e. this is a shipped path and not a test-only shim. Severity is Low because local-storage latency is small; it becomes Medium on a network-backed "local" mount, which is exactly the shape the same string warns about.

## Checked and sound

* `ref_queue_mutex` is never held across an object-store call. Every site copies shared pointers out and releases the lock before touching the backend (`CasRefLedger.cpp:337-340, 351-376, 1128-1133, 1217-1222, 1358-1365`), and the leader hand-off releases it before `runRefQueueLeader` (`:1475`) and re-takes it only for bookkeeping (`:1524-1541`).
* `RefTableRuntime::state_mutex` is correctly dropped around I/O: the recovery walk unlocks at `:1022` and relocks at `:1034` (with the same discipline on the throw path `:1029-1033`), the retry sleep unlocks at `:1084`, and the ref-log conditional PUT at `:2455` runs with no state lock held — the surrounding `lock_guard`s (`:2431-2440`, `:2464-2468`, `:2489-2492`) are short critical sections over in-memory state only.
* `drainRefLanesForShutdown` is the one wait in the ledger with a real budget (`cv.wait_until(lk, deadline)`, `:1367-1385`) and reports `timed_out` rather than hanging.
* `CasGcScheduler::mutex` guards only flags and the interval wait (`:59-64, 69-72, 83-89, 226-231, 285-288`); the heartbeat pulse (`:303`) is issued outside it, so a slow heartbeat cannot block `stop()`'s flag write.
* `Gc::meta_pool` is a dedicated `ThreadPool` (`Gc/CasGc.cpp:314-316`, size `gc_meta_pool_size=16`), not a shared server pool, and GC tasks do not re-enter it — no deadlock by pool starvation, only the unbounded `wait()` folded into bc7-3.
* The blob upload pool is likewise dedicated, and `uploadBlobDetached` does not schedule onto the same pool, so the fan-out cannot self-deadlock; the default queue size (10 000) means `enqueue` does not block the caller — the exposure is the wait, not the submit.
* Conditional writes do get a genuinely single-attempt client (`S3ObjectStorage.cpp:895-913`, `max_retries = 0`), so a conditional PUT cannot spin 500 times inside a lock; only reads/HEAD/LIST can (bc7-4).
* `CasRefLedger::confirmExactRef` uses `try_to_lock` on the state mutex and answers `Unknown` rather than blocking (`:310-312`), which is the right shape for a probe called from a contended path.
* `enforceRefTableCacheBudget` evicts under `try_to_lock` and skips busy runtimes (`:1197-1203`) — no eviction can block behind a lane that is doing I/O.

## Coverage

Read in full or in the relevant regions: `ContentAddressedSettings.cpp`, `Backend/CasRequestControl.{h,cpp}`, `Backend/CasObjectStorageBackend.cpp`, `Pool/CasRefLedger.{h,cpp}`, `Pool/CasPool.cpp` (lock structure, remount, writer-cleanup), `Pool/CasMountRuntime.cpp`, `Pool/CasPartWriteTxn.cpp`, `Pool/CasBlobUploadPool.cpp`, `Parts/PartFolderAccess.cpp`, `Gc/CasGcScheduler.cpp`, `Gc/CasGc.cpp` (pool and round-wait regions), `ContentAddressedMetadataStorage.cpp` (lock structure), `ContentAddressedTransaction.cpp` (commit, publish, fan-out, moveDirectory). Outside the CAS root: `MergeTreeData.cpp` (parts-lock publish path), `DataPartStorageOnDiskBase.cpp` (rename/commit shape), `StorageMergeTree.cpp` (rename-outside-lock comparison), `S3ObjectStorage.cpp` and `IO/S3Defines.h` (retry profile and timeout defaults), `ServerSettings.cpp`, `Common/threadPoolCallbackRunner.h`.

Not covered here, by design: pure data races and lost-wakeup analysis (concurrency audit); the FSCK `lifecycle_mutex` hold, the writer-cleanup drain, the remount-stop 30 s window, and the GC rebuild scan deadline (cited siblings). Not fully traced: the interior of `Gc::runRegularRound` phase by phase — the round is treated here as one uninterruptible unit under `gc_round_mutex`, which is sufficient for the stall bound but not a per-phase attribution; and `CasOrphanManifestSweep`/`CasBlobInDegree` internals, which run inside that same region. Dynamic verification of any of these bounds is out of scope: this is static reasoning only, and all CAS tests are deleted in the working tree.

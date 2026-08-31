# bc7-blocking-io-locks -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `src/Storages/MergeTree/MergeTreeData.cpp` (`Transaction::commit`, empty covering part), `MergeTreeSink.cpp`, `ContentAddressedTransaction.cpp` (`commit`, `fanOutBlobUploads`), `Pool/CasBlobUploadPool.cpp`, `Common/ThreadPool.cpp` (4-arg ctor), `Parts/PartFolderAccess.cpp` (`buildView` single-flight), `Pool/CasRefLedger.cpp` (follower `cv.wait`, dropNamespace wait), `Pool/CasEventDispatcher.cpp`, `Backend/CasObjectStorageBackend.cpp` (`emu_mutex`).
- Explicitly out of scope: data races (concurrency); GC `lifecycle_mutex` / FSCK deadline (sibling day-2); remount *stop* join (mount-runtime).

## Findings
### bc7-1 -- `Transaction::commit` still runs the full CAS publish under `DataPartsLock` (Medium)
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:9407-9420` (`Transaction::commit` holds `acquired_parts_lock` then `commitTransaction()`); `MergeTreeSink.cpp:408-409` (`renameTempPartAndAdd(..., /*rename_in_transaction=*/false)` then `transaction.commit(lock)`); empty-cover path `:5958-5980` at ceee42c
- Trigger: any INSERT/merge/mutation commit on a non-replicated MergeTree table on a CAS disk (the `MergeTreeSink` path), or `DROP`/`REPLACE PARTITION` creating the empty covering part. Object store slow, throttling, or 5xx.
- Evidence: `commitTransaction()` is `ContentAddressedTransaction::commit` → blob fan-out + `stageManifest` + ref-log conditional PUTs. That is network I/O, not a local rename. The lock is not dropped for any of it. Replicated sinks use `rename_in_transaction=true` and rename outside the lock; the CAS *publish* still happens in `Transaction::commit` under the lock when that overload is used. Ordinary object-storage disks also hold this lock while finishing a part write; the CAS-specific extra is minutes of gated S3 (default request budget ~90 s per controlled write, several writes per part) instead of a local `rename`. Not unbounded: each controlled write is deadline-gated. `KILL QUERY` does not abort an in-flight publish (bc7-3).
- Notes: same class as CAS-048, but the trigger is every `Transaction::commit`, not only the empty covering part. Operability, not silent corruption. Not High: bounded, same lock ordinary OS disks hold, fail-closed.

### bc7-2 -- single-flight view build and ref-append follower waits have no cancel (Medium)
- Anchor: `Parts/PartFolderAccess.cpp:286-287` (`future.get()`); `Pool/CasRefLedger.cpp:2108-2111` (`rt->cv.wait(lk)` with no timeout); `:5044-5047` (`dropNamespace` drain wait) at ceee42c
- Trigger: a concurrent `SELECT`/merge that joins a cold `CachedForLoad` view build whose leader is blocked on a slow manifest GET; or a writer waiting behind the append-lane leader; or `dropNamespace` waiting for the lane to idle. `KILL QUERY` / `max_execution_time` fire on the waiting thread.
- Evidence: `future.get()` and `cv.wait` take no stop token and do not poll `CurrentThread::isCancelled`. Each wait sits behind time-bounded I/O (request budget, recovery budget), so nothing hangs forever. Residual is non-cancellability and summed bounded work (CAS-015). Shutdown drain of ref lanes *does* use `wait_until` (`CasRefLedger.cpp:1943-1952`).
- Notes: CAS-015 residual.

### bc7-3 -- blob-upload pool `queue_size == max_threads`, so `schedule` blocks the committer (Low)
- Anchor: `Pool/CasBlobUploadPool.cpp:45-49` (`ThreadPool(..., size)`); `Common/ThreadPool.cpp:157-162` (4-arg ctor sets `queue_size = max_threads`) at ceee42c
- Trigger: more unique blob refs in flight than `cas_blob_upload_pool_size` (default 16) across *all* CAS disks in the process.
- Evidence: `ThreadPool::schedule` "Locks until the number of scheduled jobs is less than the maximum". The committer already holds `DataPartsLock` (bc7-1), so a saturated process-global pool extends that hold. This is ordinary backpressure, not a deadlock: the calling thread only submits and joins (`fanOutBlobUploads` `:1752-1753`) and never occupies a pool slot. Size is a server setting.
- Notes: CAS-047. Not raised as Medium: blocking enqueue is the intended cap.

## By-design / info / non-actionable
- `emu_mutex` is still held across exists+read/write+head (`CasObjectStorageBackend.cpp:427+`). That is the mechanism that makes emulated tokens linearizable. `EmulatedSingleProcess` is tests / local development only (CAS-135). Not a production lock-across-S3 finding.
- `EventDispatcher::emit` releases `mutex` before the sink (`CasEventDispatcher.cpp:34-51`). A sink throw is contained and `draining` is cleared. The old "every resolve serializes on one mutex" claim does not hold. Residual if the sink is installed with no `cas_log` consumer: events are still built and discarded (CAS-104 class; not re-measured here).
- Process-static emulated resurrect mutex from the previous report: the publish path is now `publishBlob` / `emuPublishBlobAtomically` (`:488+`). Emulated-only.
- Ref-queue mutex is not held across backend I/O. Leadership I/O runs after `lk.unlock()` (`CasRefLedger.cpp:2086`).

## Closed-since-2026-08-12
- Previous report's "default upload queue size 10 000 so enqueue does not block" is stale: the 4-arg `ThreadPool` ctor now sets `queue_size = max_threads`. Enqueue *does* block; that is backpressure, not a newly opened deadlock.
- `remount_running` latch (old remount-stop interaction) is gone; remount is a persistent worker (bc3 closed-since).

## Coverage
- Reviewed: `DataPartsLock` × `commitTransaction`; upload-pool enqueue/queue_size; `emu_mutex`; event-dispatcher mutex; single-flight `future.get`; ref-append follower / dropNamespace waits; shutdown drain timeout.
- N-A: emulated locks as a production multi-node hazard.
- Deferred: interior of `Gc::runRegularRound` phase-by-phase (treated as one unit under the scheduler lock; sibling GC audit).

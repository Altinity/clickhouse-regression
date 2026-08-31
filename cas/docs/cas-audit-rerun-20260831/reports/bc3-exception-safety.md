# bc3-exception-safety -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Pool/CasRefLedger.cpp` (lane leadership, `removal_admission_closed`, `pending_snapshot_publishes`, `completeOwnedItemsAndReleaseLeadership`), `Pool/CasMountRuntime.cpp` (`scheduleRemount`, remount worker), `Pool/CasPool.cpp` (`~Pool`), `Parts/PartFolderAccess.cpp` (`CommitOutcome`, `dropRefIfMatches`, `promoteBuild`), `ContentAddressedTransaction.cpp` (commit rollback), `Gc/CasGcPhaseTimer.h`, `Backend/CasProbe.cpp` (cleanup lambda), `ContentAddressedTransaction.cpp` (`cleanupPendingTempFiles`).
- Explicitly out of scope: lock *hold time* across I/O (bc7); data races (concurrency audit).

## Findings
### bc3-1 -- `dropNamespace` still latches admission closed without RAII; recovery empty-catch leaves it closed (Medium)
- Anchor: `Pool/CasRefLedger.cpp:5041-5048` (latch + drain wait), `:5107-5139` (recovery), empty catch at `:5133` at ceee42c
- Trigger: `dropNamespace` sets `rt->removal_admission_closed = true` then waits for the lane to idle, then reads the catalog / begins `Removing`. A transient backend error in that `try` hits the handler. The recovery re-read (`CasRefCatalog::read` at `:5115`) hits the same failing backend and throws into `catch (...) {}`. `removing_durable` stays false; the original exception is rethrown; the latch is not cleared.
- Evidence: the only reopen in this function is `:5129` (`removal_admission_closed = false`) after a *successful* exact re-read that still shows the original `Live` row. Nothing else clears the flag except a fresh runtime. Subsequent positive appends throw "is Removing: positive ref mutation admission is closed … retry later" (`:2043-2046`) even though removal never became durable. Inserts/merges on tables in that namespace fail until remount or restart reconstructs the runtime. The latch is a bare bool, not a scope guard.
- Notes: narrower than the 2026-08-12 High. Empty-catch / "permanently broken table" overstatement is not repeated (CAS-017). The residual is a process-local write refusal until remount.

### bc3-2 -- `GcPhaseTimer` destructor still allocates outside its `try` (Low)
- Anchor: `Gc/CasGcPhaseTimer.h:54-74` at ceee42c
- Trigger: a GC phase exits (normal or exceptional) under a memory limit. The dtor takes a `ProfileEvents` snapshot (`:64`) and `emplace`s `String` keys (`:69`) *before* `try { sink(rec); }` at `:74`.
- Evidence: a throw from an implicit-`noexcept` destructor during unwind is `std::terminate`. The author wrapped the sink but not the record construction. Same shape as the previous finding; still live.

### bc3-3 -- probe cleanup `noexcept` lambda still allocates `String`s in the loop header (Low)
- Anchor: `Backend/CasProbe.cpp:26-32` at ceee42c
- Trigger: mount-time capability probe under memory pressure. `for (const auto & k : {key, cas_key})` materialises an `initializer_list<String>` by copy. That allocation is outside the inner `try`.
- Evidence: a throw in a `noexcept` lambda terminates. Distinct site from the `PartFolderAccess` rollback helpers.

## By-design / info / non-actionable
- `CommitOutcome` rollback is exact: `publishStaging` writes the outcome into a preallocated slot (`ContentAddressedTransaction.cpp:515-521`); on exception only `created == true` refs are `dropRefIfMatches`'d (`:533-536`, `PartFolderAccess.cpp:646`). A concurrent repoint of the same name is left alone. Best-effort: a rollback failure does not mask the original error.
- `pending_snapshot_publishes` is incremented under the state lock in `admitSnapshotPublishUnderStateLock` (`CasRefLedger.cpp:4053`) and decremented on every path via `SCOPE_EXIT` (`:4072-4077`, `:4138`). The 2026-08-12 leak that wedged `quiesceRefTablesForRemount` is gone (`829ad698ef6` and still gone at HEAD).
- `completeOwnedItemsAndReleaseLeadership` (`:2145-2167`) is the single exit that clears `leader_active` and notifies waiters. Ownership is built *before* `leader_active = true` (`:2072-2085`). The previous "throw in `make_exception_ptr` deadlocks the namespace" High is closed as a leadership leak. Residual: `std::make_exception_ptr(Exception(...))` at `:2153` still allocates; if it throws, `leader_active` is not yet cleared. That is the same theoretical memory-limit class Filimonov left as P3, not a new High.
- S3 staging objects of an aborted transaction are intentionally retained for the mount sweeper (`ContentAddressedTransaction.cpp:188-208`).

## Closed-since-2026-08-12
- `remount_running` latch-before-spawn (CAS-070 / old bc3-8): symbol is gone. Remount is a persistent worker; `scheduleRemount` only bumps `remount_requested_generation` (`CasMountRuntime.cpp:1072-1078`). Failed thread create cannot stick a boolean that suppresses recovery.
- `Pool::~Pool` unguarded teardown (old bc3-3): each phase is now in a nested `try` (`CasPool.cpp:882-942`). `tryLogCurrentException` is itself guarded.
- `putIfAbsentControlled` / `promoteStaged` / `conditionalCreateControlled` swallow-local-failure wrapper (old bc3-4): those symbols are gone after the unconditional-publish rewrite (`940b1685bf9`).
- Leadership release without a single exit (old bc3-2 High): replaced by `completeOwnedItemsAndReleaseLeadership`.

## Coverage
- Reviewed: RAII latches (`removal_admission_closed`, remount generation, `leader_active`, `pending_snapshot_publishes`); `noexcept` / dtor allocation (`GcPhaseTimer`, probe cleanup, `~Pool`); `CommitOutcome` rollback; empty `catch (...)` on the drop-namespace recovery path.
- N-A: protobuf decoder exception taxonomy (bc4).
- Deferred: `Tools/CasFsck.cpp` catch-all (read-only checker; fail-soft is the correct shape).

# ad3-day2-dr-runbook -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Tools/CasFsck.{h,cpp}`; `Tools/CasInspect.cpp`; `Gc/CasGc.cpp` (`rebuildBaseline`, `previewDeletes`); `Gc/CasGcScheduler.{h,cpp}` (`GcHealth`); `ContentAddressedMetadataStorage.cpp` (`runFsckNow`, `runGcRebuildNow`); `src/Interpreters/InterpreterSystemQuery.cpp` (SQL FSCK); `programs/disks/CommandCaGcDryRun.cpp`; `programs/disks/CommandCaGcRebuild.cpp`; `src/Storages/System/StorageSystemContentAddressedMounts.cpp`; `Pool/CasPool.cpp` (`open` / `_pool_meta` gate).
- Explicitly out of scope: GC algebra correctness (gc-protocol); privilege model (security).

## Findings
### ad3-1 -- the only rebuild covers `gc/state`; `_pool_meta` and `ref_catalog` have no repair path (Medium)
- Anchor: `Gc/CasGc.cpp:3715` (`rebuildBaseline`); `Pool/CasPool.cpp:501-503` (`PoolMeta::createOrValidate` on every open); `Pool/CasPoolMeta.cpp:143-146` (absent meta outside bootstrap → `INVALID_STATE`); inspect dispatch `Tools/CasInspect.cpp:633-636` (no `_pool_meta` / `ref_catalog` / `owner` / `epoch` decoder).
- Trigger: corrupt or missing `_pool_meta` or `cas/ref_catalog`.
- Evidence: `cas-gc-rebuild` / `SYSTEM CAS GC REBUILD` rebuild the GC baseline only. Offline tools call `ca->store()` and therefore `Pool::open`, which requires a decodable `_pool_meta`. Shipped strings say recreate the pool or restore `_pool_meta`. Fail-closed and loud; the gap is the missing repair, not silent loss.
- Notes: CAS-061 residual.

### ad3-2 -- `SYSTEM CAS FSCK` is counts-only: no keys, no timeout, no namespace (Medium)
- Anchor: `src/Interpreters/InterpreterSystemQuery.cpp:2623` (`runFsckNow(/* detail= */ false)`); CLI `programs/disks/CommandFsck.cpp` (`--detail`, `--timeout`, `--namespace`).
- Trigger: SQL `SYSTEM CAS FSCK DISK x` reports `dangling=N`.
- Evidence: SQL returns scalar counts. Localizing keys requires a second, read-only disk config and `clickhouse-disks cas-fsck --detail`. No SQL deadline or scope.
- Notes: CAS-062 / CAS-049 residual.

### ad3-3 -- `cas-inspect` cannot decode the control objects whose damage is fatal (Low)
- Anchor: `Tools/CasInspect.cpp:567-636`. Recognized: part manifests, `_ckpt`, ref snap/log, `gc/state`, `*/mount`, `*/fold_seal`, blob-target runs, blob bodies, `.meta`.
- Trigger: operator has a raw `_pool_meta` / `ref_catalog` / `owner` / `epoch` key from `aws s3 ls`.
- Evidence: those keys throw `unrecognized key layout`. They are exactly the objects ad3-1 cannot rebuild.

### ad3-4 -- `cas-gc-dryrun` prints `preview_deletes=0` when `gc/state` is absent (Low)
- Anchor: `Gc/CasGc.cpp:4277-4279` (`if (!state_bytes) return out;`); `programs/disks/CommandCaGcDryRun.cpp:43-45`.
- Trigger: fresh pool, or `gc/state` never written, or an operator runs dry-run expecting "nothing to delete" vs "no GC state".
- Evidence: missing state and a truly empty retired set produce the same `preview_deletes=0` with no warning. Undecodable `gc/state` still throws `CORRUPTED_DATA`. Read-only diagnostic.
- Notes: CAS-095 residual.

### ad3-5 -- `last_success_age_seconds=0` means both "never led" and "just succeeded" (Low)
- Anchor: `Gc/CasGcScheduler.h:128`; `Gc/CasGcScheduler.cpp:392-404` (`ever_succeeded = last_ms != 0`; age computed only when `last_ms != 0`); `StorageSystemContentAddressedMounts.cpp:54,201` (column comment: "0 if it never led"; `ever_succeeded` not exposed).
- Trigger: alert `last_success_age_seconds > N` on a node that has never held the GC lease.
- Evidence: `GcHealth` computes `ever_succeeded` and the table drops it. Health columns are process-local and reset on restart.
- Notes: CAS-098 residual.

### ad3-6 -- no quiesce / leadership-handoff verb before planned stop (Low)
- Anchor: `Gc/CasGcScheduler.cpp` `stop()` joins threads and does not write `gc/state`; `~Pool` drains ref lanes and writes a farewell lease.
- Trigger: rolling restart of the current GC leader.
- Evidence: `SYSTEM CAS GC STOP` is in-memory; restart resumes GC. The durable GC lease is not released on a clean stop, so followers wait out the observation window. `SYSTEM CAS FORGET` / `DROP POOL MEMBER` are the node-removal verbs and are destructive of the member's namespaces. Not unbounded unavailability.
- Notes: CAS-099 residual. The prior "only shutdown is stop-and-join" claim is false: farewell exists.

## By-design / info / non-actionable
- CLI fsck has `--detail` / `--timeout` / `--namespace` and nonzero exit on hard classes.
- `cas_gc_log` correlates rounds by `round_id` with named phases.
- Each `SYSTEM CAS *` verb has its own GLOBAL privilege.
- Rebuild of a healthy pool requires `FORCE`.
- No per-table "bytes reclaimed if I drop X" surface (dedup is pool-wide). Operability, not a correctness defect.

## Closed-since-2026-08-12
- None of the rebuild / FSCK-SQL / inspect / dry-run / age-zero / no-handoff shapes were removed. Severity is lowered vs the 2026-08-12 High set: fail-closed recreate and CLI localization exist; Filimonov rejected "reported nowhere" and High-for-docs.

## Coverage
- Reviewed: SQL and CLI FSCK; inspect key coverage; dry-run empty; GC health columns; rebuild scope; quiesce/handoff; `_pool_meta` open gate.
- N-A: runtime DR drill.
- Deferred: byte accounting outside `blobs/` (capacity sibling).

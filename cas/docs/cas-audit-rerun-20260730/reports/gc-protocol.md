# gc-protocol — re-run 2026-07-30

## Scope in current code

- Files/dirs walked (line by line):
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.h` (621 lines)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp` (3114 lines) — full-file structural walk; focused reads of `runRegularRound`, `fold`, `runNamespaceCleanupPasses`, `cleanupRefObjects`, `pruneSupersededGenerations`, `rebuildBaseline`, `pulseHeartbeat`, `acquireOrRenewLease`.
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcScheduler.{h,cpp}` (222 + 407 lines)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcPhaseTimer.h` (87)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGcShardPlan.{h,cpp}` (167 + 64)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasBlobInDegree.{h,cpp}` (309 + 665) — read for the streaming-question anchor
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasOrphanManifestSweep.{h,cpp}` (89 + 462)
- Adjacent hooks consulted:
  - `Backend/CasProbe.{h,cpp}` — capability probe (versioning refusal).
  - `Backend/CasObjectStorageBackend.{h,cpp}` — `checkPoolPreconditions` / `isBucketVersioningEnabled`.
  - `Backend/CasBackend.h` — `DeleteOutcome::created_delete_marker`.
  - `Pool/CasRefLedger.{h,cpp}` — `dropNamespace`, `resolveRef` (allow_stale contract).
  - `Storages/System/StorageSystemContentAddressedMounts.cpp` — GC health surfacing.

---

## Findings still present

### CAS-032 — Zombie GC leader's `pulseHeartbeat` can still float `gc/hb.owner` under a stale identity

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.cpp:2989-3003` (`Gc::pulseHeartbeat`) + `CasGcScheduler.cpp:339-377` (`heartbeatLoop`).
- Trigger: a leader whose lease was stolen or that has been superseded, whose in-process `i_am_leader` has not yet been flipped by the pacing loop (the next scheduled round has not yet run and observed the loss). Between the loss and that reset, the heartbeat worker keeps pulsing.
- Evidence quote:
  - `pulseHeartbeat` unconditionally writes `hb.owner = gc_id` and increments `hb.hb_seq` (`CasGc.cpp:3000-3002`), with no read of `gc/state`'s current owner. It also has NO precondition (`expected` is the existing `gc/hb` token only, not the leader identity), so it cannot fail on identity grounds.
  - Follower steal logic in `acquireOrRenewLease` (`CasGc.cpp:3057-3068`) deliberately treats ANY movement of the observed `(hb.owner, hb.hb_seq)` pair as proof of life, EVEN under the deposed leader's own owner: "an hb pair that keeps moving under the OLD owner's name must still read as 'alive', or a live, pulsing new leader gets its lease stolen."
- Notes: the surface has been narrowed (heartbeatLoop line 366 checks `i_am_leader` before pulsing, and `stop()` clears the hint after joining both workers). This kills the pulse ONCE the scheduler has learned it is no longer leader, so the window is now bounded to (at most) one `interval` — the pacing tick that resets `i_am_leader` on the next `runRegularRound`. The finding is retained as **STILL PRESENT (attenuated)**: safety-preserving, still delays legitimate stealing of a dead incumbent by up to one interval, and the deliberate acceptance in the follower's steal comment closes any hope of a stricter check. Severity: LIVENESS, unchanged.

### CAS-033 — Persistent shard clamp still drives POOL-WIDE `suppress_destructive`

- Anchor: `CasGc.cpp:1833-1842` (`result.suppress_destructive = !report.anomalies.empty();`).
- Trigger: any single shard emits a fold anomaly (a clamp) this pass — persistent false-404, corrupt body, unreadable body, or a stuck fold barrier. Suppression applies pool-wide, halting graduations and pending-deletes on **every** shard until a clamp-free pass.
- Evidence quote:
  - "any clamp this pass means landed-before-cut events may be UNFOLDED behind a clamped cursor" (`CasGc.cpp:1817-1822`)
  - `runNamespaceCleanupPasses` (`CasGc.cpp:2170-2171`) and `cleanupRefObjects` (`CasGc.cpp:2079-2080`) both early-return on `suppress_destructive`, so the pool-wide gate cascades into namespace-physical-reclaim and ref-log cleanup too.
- Notes: safety-preserving over-retention (as originally called out). Verdict unchanged from the original audit's G-N1: safe-but-brittle liveness/operability cliff, no per-shard scoping introduced. **STILL PRESENT.**

### CAS-044 — Catalog↔CAS reconcile is still not owned inside CAS

- Anchor: `Pool/CasRefLedger.cpp:2890-2984` (`CasRefLedger::dropNamespace`) — the "official" removal path; there is no independent orphan-namespace scanner in `Gc/` that discovers a CAS-side namespace not owned by any catalog table.
- Trigger: crash between the catalog-side `DROP TABLE`/`RENAME`/`DETACH DATABASE` and the caller invoking `Pool::dropNamespace`. The CAS pool retains a Live namespace (refs, manifest bodies, verbatim files) with no owning table object.
- Evidence quote:
  - `dropNamespace` is caller-driven only; there is no periodic reconcile against an external catalog inventory. The GC round only reclaims namespaces whose durable `remove_namespace` transaction has landed — the RemoveNamespace transaction is what mints the `ns_cleanup_items` entry the GC round consumes (`CasGc.cpp:2145-2266`).
  - `Pool.h:451-458` documents "GC's namespace-cleanup item"; nothing scans the other direction.
- Notes: mitigated only in that a warm recreation (same server) preserves the namespace as-is (still Live, but with a fresh `writer_epoch` bumped only at open/remount — `CasGc.cpp:2206-2208`). A permanent catalog loss (Ordinary DB drop / manual metadata edit) leaves the orphan indefinitely; still surfaces as phantom parts / bytes with no owner. **STILL PRESENT** — architectural, unchanged in this PR.

### CAS-088 — Lost/corrupt GC-internal artifacts still wedge GC until manual `SYSTEM CONTENT ADDRESSED GC REBUILD`

- Anchor: `CasGc.cpp:2488-2903` (`Gc::rebuildBaseline`) + `CasGcScheduler.cpp:254-278` (self-exit on `IdentityLost`/`VanishedReplaced`).
- Trigger: loss/corruption of `gc/state`, adopted fold seal, referenced runs, or retired lists. `acquireOrRenewLease` throws `CORRUPTED_DATA` on a vanished-after-observed state (`CasGc.cpp:3016-3018`); `graduationDue` fail-closes on undecodable/missing seal (`CasGc.cpp:2436-2445`) and `readFoldSeal` rejects corrupt bytes.
- Evidence quote:
  - `runRegularRound`'s round CAS re-derives from `gc/state` each round; if `gc/state` cannot decode, the round throws and every tick re-throws. The self-exit case in `CasGcScheduler.cpp:268-278` handles the *terminal-pool* case but explicitly does NOT handle the `gc/state`-only corruption case — that path keeps re-throwing `CORRUPTED_DATA` until an operator issues rebuild.
- Notes: by-design blast radius (verdict unchanged from original audit G-N2 → CAS-088). GC is fail-stop-then-recover on internal-state loss, not self-healing. **STILL PRESENT / BY-DESIGN**, low severity.

### CAS-089 — Regular round mass-drop delta is still non-streaming

- Anchor: `CasGc.cpp:1362` (`std::vector<BlobDelta> deltas;` accumulated across the fold intake) + `CasGc.cpp:1582` (`deltas.push_back(std::move(d));`) and shard bucketing at `CasGc.cpp:1880-1882` (also in-memory: `std::vector<std::vector<BlobDelta>> buckets(state.gc_shards);`).
- Trigger: a mass drop (`dropNamespace` on a large table, mass RENAME, big TTL move) produces a very large number of removal deltas in one fold pass.
- Evidence quote:
  - The fold intake pushes every delta from every fully-folded `RootOwnerEvent` into the single `deltas` vector before the reduce phase splits into per-shard buckets. There is no per-shard budgeted flush during the intake in the regular round — unlike `rebuildBaseline` (`CasGc.cpp:2610-2645`), which explicitly flushes per-shard once `buckets[shard].size() >= budget`.
- Notes: `rebuild_edge_budget` (default 8_000_000, `CasPool.h:103`) is honored ONLY by `rebuildBaseline`, not the regular round. The safety-critical properties (idempotence, single-CAS commit) are unaffected; the concern is memory pressure and long fold latency during mass drops. **STILL PRESENT**, unchanged.

### CAS-106 — GC cadence/retention knobs still directly gate reclaim latency

- Anchor: `Pool/CasPool.h:84` (`gc_snap_generations_to_keep = 3`), `Pool/CasPool.h:90-91` (`manifest_sweep_list_budget_keys/delete_budget_keys`), `Pool/CasPool.h:96-99` (`gc_fold_threshold`, `gc_fold_max_defer_rounds`), `Pool/CasPool.h:103` (`rebuild_edge_budget`).
- Trigger: default retention pins `keep=3` generations. `keep == 0` (forensics-mode) is documented (`CasGc.cpp:2320-2321`) but the operator experience is: "wholesale prune is the sole reclaimer of ALL attempt debris" (`CasGc.cpp:2375-2382`), so any deposed-leader current-generation debris waits `keep` completion-advances before reclamation.
- Evidence quote: `CasGc.cpp:2378-2382`: "waits at most `keep` completion-advances to be reclaimed. This trades ~`keep` rounds of reclaim latency on (rare) concurrent-leader collisions".
- Notes: config knob, not a bug. **STILL PRESENT / BY-DESIGN**, CONFIG class.

### CAS-108 — `GC REBUILD` interrupted-run debris + generation ratchet

- Anchor: `CasGc.cpp:2570-2594` (`max_gen = max_gen + 1;` ratchets on EVERY rebuild attempt); `CasGc.cpp:2861` (deterministic seal PUT at `foldSealKey(generation, seal_attempt)`); `CasGc.cpp:2874-2879` (single `gc/state` CAS at the very end).
- Trigger: `SYSTEM CONTENT ADDRESSED GC REBUILD` interrupted after the fold-seal PUT and per-hash condemn-marker writes (`CasGc.cpp:2776-2800`) but before the final `gc/state` CAS. Re-running the command picks a strictly greater generation each attempt (the LIST at `CasGc.cpp:2576-2591` includes the already-written but not-adopted seal directory), so each interrupted rebuild ratchets the mint and leaves an unadopted `gc/gen/<g>/` subtree.
- Evidence quote: `CasGc.cpp:2570-2592`: "generation above ANY surviving gc/gen prefix (putDeterministicArtifact must never collide with debris of the lost era)". `max_gen = std::max(max_gen, ...)` walks EVERY numeric segment under `gc/gen/`, adopted or not.
- Notes: reclamation of orphan `gc/gen` prefixes still relies on `pruneSupersededGenerations` reaching them once they fall below `adopted_generation - keep` (`CasGc.cpp:2338-2367`). During the rebuild storm they are ABOVE the current adopted generation and are never reclaimed by the running system until a successful rebuild adopts a generation above them AND enough rounds pass. Live-adopted-referenced check (`referenced_generations.contains(g)`, `CasGc.cpp:2357`) never fires for these because the failed attempts are never referenced — they are simply skipped forward past. **STILL PRESENT** (verdict: LEAK + DAY2, unchanged). SYSTEM-gated, blast radius bounded.

---

## Findings fixed / no longer reproducible

### ✅ CAS-011 — Bucket versioning: mount-time closes the loud case (soft-delete still fails-open on unknown)

- Fix anchor: `Backend/CasObjectStorageBackend.cpp:60-84` — `checkPoolPreconditions` calls `isBucketVersioningEnabled()`; a *known-Enabled* result throws at mount time with a clear message ("versioning was NEVER enabled — note that merely SUSPENDING versioning is not enough"). Belt-and-suspenders: `Gc::runRegularRound` (`CasGc.cpp:517-521`) throws `LOGICAL_ERROR` if any pre-CAS `deleteExact` returns `created_delete_marker=true` ("the capability probe must reject this").
- Residual concern: `checkPoolPreconditions` fails-OPEN when the versioning check itself is inconclusive (`CasObjectStorageBackend.cpp:60-75`): "either the GetBucketVersioning-equivalent call failed (e.g. permissions) or the storage does not support answering it. We proceed on the ASSUMPTION that versioning is off". A malicious/mis-configured environment (IAM stripping s3:GetBucketVersioning, GCS Soft-Delete API for GCS buckets) still slips through the mount check; the delete-marker backstop in the round will catch it, but ONLY at the moment the FIRST reclaim delete tries to create a marker (i.e. only when there is actually something to reclaim). The residual is captured below as **NEW-gc-protocol-1** — the GCS-specific soft-delete API is never queried directly.
- Verdict: **✅ mostly-fixed** for the versioning-Enabled case; **downgraded** to a narrower OBSERV/LEAK on the fails-open API-unavailable path (see NEW-gc-protocol-1).

### ✅ CAS-014 — GC-liveness / reclaim-backlog metric now exists via `system.content_addressed_mounts`

- Fix anchor: `src/Storages/System/StorageSystemContentAddressedMounts.cpp:52-55` (columns `is_leader`, `pending_reclaim`, `last_success_age_seconds`, `wedged_namespace_count`) + `Gc/CasGcScheduler.cpp:379-394` (`gcHealth()`) + `src/Interpreters/ContentAddressedGarbageCollectionLog.cpp` (per-phase log rows).
- The four-column tuple is exactly the "reclaim stopped" signal the original finding said was invisible. `pending_reclaim` is cumulative condemned-minus-deleted for the CURRENT PROCESS's leadership tenure (`CasGcScheduler.cpp:191-193, 216`), so it resets on process restart or leader change — an operator should watch `last_success_age_seconds` alongside it, but the surface is there.
- Verdict: **✅ fixed** (surface exists). Physical-bytes/dedup-ratio remains a separate CAS-040 concern (SYS-1), out of scope here.

### ✅ CAS-085 — `allow_stale` decode-TTL ↔ GC coupling collapsed by making `allow_stale` a no-op

- Fix anchor: `Pool/CasRefLedger.cpp:174-179` — `resolveRef(..., bool /*allow_stale*/, ...)` explicitly ignores the parameter: "The `allow_stale` staleness-tolerance knob no longer selects anything: this mounted writer is the ONLY writer of `ns`'s ref state (no external CAS token to go stale against, unlike the old model)". Callers still pass `allow_stale=true`/`false` (`PartFolderAccess.cpp:318, 607`) but the ledger routes every call to the same authoritative cached table.
- Verdict: **✅ fixed** by design change (snapshot+log per-namespace ref model + single writer). The coupling with GC condemn→delete latency no longer exists because the read side never observes a decode-TTL freshness gap on refs.

### ✅ CAS-092 — `shard_write_seq` no longer exists

- Fix anchor: grepping the entire CAS tree for `shard_write_seq|write_seq|writeSeq|WriteSeq` returns zero hits. The old numeric-shard root-shard ref model has been replaced with the snapshot+log per-table ref model (one ref stream per namespace), so there is no per-(namespace, shard) sequence dictionary to grow.
- Verdict: **✅ fixed** by design change. `dropNamespace` now writes a durable `remove_namespace` transaction which mints a `ns_cleanup_items` entry (`CasGc.cpp:2145-2266`) that GC completes and prunes, and the Removed snapshot fully replaces the tail — no residual sequence-map state.

---

## New findings (not in original audit)

### NEW-gc-protocol-1 — Versioning-precondition failure is silently fail-open (S3 IAM-stripped or GCS Soft-Delete API-unknown)

- Severity: **Med** (LEAK / OBSERV — silent under mis-provisioning).
- Anchor: `Backend/CasObjectStorageBackend.cpp:60-84` (`checkPoolPreconditions`).
- Trigger: an S3 role without `s3:GetBucketVersioning`, or any backend whose `isBucketVersioningEnabled()` returns `std::nullopt`. The mount proceeds with a WARN log ("proceeding on the assumption that bucket versioning is OFF"). GCS Soft-Delete (bucket-level retention duration > 0) is NOT queried by an equivalent `getSoftDeletePolicy()` — GCS soft-delete quietly retains DELETEd objects for the configured duration without minting a `created_delete_marker`, so the pre-CAS-delete backstop at `CasGc.cpp:517-521` does NOT catch it.
- Notes: `checkPoolPreconditions`' own comment concedes "an outright refusal to mount whenever the check is inconclusive would be too aggressive". Recommend adding: (a) a *durable* signal (an operator-visible row / ProfileEvent counter) surfacing the "unable to verify versioning" outcome, so a monitor can alert; (b) an explicit GCS Soft-Delete-policy query on the GCS backend path. Currently the only trail is a single WARN at mount time.

### NEW-gc-protocol-2 — `pulseHeartbeat` has no gc/state cross-check; a bug that failed to clear `i_am_leader` produces silent zombie pulses

- Severity: **Low** (LIVENESS / hardening).
- Anchor: `CasGc.cpp:2989-3003`.
- Trigger: any code path that leaves `CasGcScheduler::i_am_leader == true` when the durable `gc/state` no longer names `gc_id` as owner. Today the pacing loop clears it in three places (`CasGcScheduler.cpp:239, 296, 333`), but the invariant is enforced by discipline, not by the pulse's own precondition. A future refactor that misses one path would produce a "zombie pulser" for arbitrarily long windows (bounded only by the next scheduled tick that reads `gc/state`).
- Notes: cheap defense-in-depth: read `gc/state`, decode, if `state.lease.owner != gc_id` skip the pulse (with a WARN). Cost = one extra small GET per hb tick (`hb_interval` ≥ 50 ms). The follower-side "hb pair keeps moving under OLD owner still reads as alive" bias (`CasGc.cpp:3057-3068`) IS the correctness fence today, but codifying the pulser side too would prevent the zombie in the first place, rather than tolerating it as follower policy.

### NEW-gc-protocol-3 — `deleteExact` `created_delete_marker` runtime backstop throws `LOGICAL_ERROR` mid-round

- Severity: **Low** (OPERABILITY / OBSERV).
- Anchor: `CasGc.cpp:517-521`.
- Trigger: a bucket flips to versioning-enabled while the pool is mounted (mount-time check passed; runtime does not), or a bucket that answered the versioning probe with `nullopt` at mount time turns out to have versioning on. The very first pre-CAS reclaim delete throws `LOGICAL_ERROR` and dies. Every subsequent round will re-attempt the delete (same reclaim entry is still `delete_pending`) and fail-loop.
- Notes: fail-loud is correct; suggest converting the exception path into a durable "suspend reclaim on this pool, do not retry" flag + operator-visible event, so the failure is not a per-round LOGICAL_ERROR log storm. Purely operability.

### NEW-gc-protocol-4 — `rebuildBaseline` full-traversal `LIST(blobsPrefix()) + HEAD each` is unbudgeted per invocation

- Severity: **Low** (PERF — already covered by CAS-050 in the summary, but explicitly recheck: still not budgeted).
- Anchor: `CasGc.cpp:2756-2769` — one HEAD per non-edge-bearing blob listed. `deltas` routing IS budgeted via `route_deltas` / `flush_shard` (`CasGc.cpp:2593-2645`), but the LIST/HEAD sweep is not.
- Notes: original audit already flagged this as CAS-050. Recorded here to confirm the re-check verdict: **STILL PRESENT**, unchanged.

### NEW-gc-protocol-5 — `dropNamespace` best-effort `publishRemovedSnapshotNow` swallow can mask a legitimate write failure

- Severity: **Low** (LEAK/OBSERV, transient).
- Anchor: `Pool/CasRefLedger.cpp:2970-2977`.
- Trigger: the removal transaction is durable, but the constant-size `Removed` snapshot PUT fails. The try/catch logs "best-effort" and returns success from `dropNamespace`. `runNamespaceCleanupPasses` (`CasGc.cpp:2244-2264`) will re-publish it idempotently, but only once GC finds a covering `ref_tables` listing AND the `Completed` transition. If GC is stopped or the pool has stalled, the removed namespace shows no durable Removed snapshot to a fresh reader — which is exactly the class of race the snapshot is supposed to close.
- Notes: recommend surfacing this via a ProfileEvent + a mount-health row column (`removed_snapshot_publish_pending`) so an operator can spot it before GC completes it.

---

## By-design / N/A / info

- 📐 `keep=0` (`gc_snap_generations_to_keep`) intentionally disables the wholesale prune (`CasGc.cpp:2320-2321`, `2381-2382`). This is documented forensics mode.
- 📐 `TokenMismatch` on `deleteExact` is a live re-incarnation and is intentionally treated as "Replaced" outcome (`CasGc.cpp:539-542, 566-577`) — a resurrect wrote a fresh incarnation at this hash (INV-1). Meta is left alone deliberately.
- 📐 `runOneRoundNow` (manual `SYSTEM ... GC`) forces `allow_steal=false` (`CasGcScheduler.cpp:234-241`) — dead-incumbent recovery is loop-only. Documented and enforced.
- 📐 Fold-seal `putDeterministicArtifact` — byte-identical replay is adopt-no-op; divergent bytes throw `CORRUPTED_DATA` (`CasGc.cpp:2018`, `1966-1971`). Fail-closed against a stale leader's collision under the same (generation, attempt) — but a deposed leader writes under its own unadopted `attempt`, so no collision in practice.
- ⚪ Info: `pending_reclaim` is process-scoped, not durable (`CasGcScheduler.h:214-218`). Reset on process restart or leader change — this is documented on the metric but operators comparing across servers must know it.

---

## Verdict summary table

| CAS-id  | Old severity | Status              | Evidence anchor                                                              |
|---------|--------------|---------------------|------------------------------------------------------------------------------|
| CAS-011 | High         | ✅ mostly-fixed → NEW-1 | `Backend/CasObjectStorageBackend.cpp:60-84`; `Gc/CasGc.cpp:517-521`; `Backend/CasProbe.cpp:215-225` |
| CAS-014 | High         | ✅ fixed             | `Storages/System/StorageSystemContentAddressedMounts.cpp:52-55`; `Gc/CasGcScheduler.cpp:379-394` |
| CAS-032 | Med (LIVENESS)| 🔴 still-present (attenuated) | `Gc/CasGc.cpp:2989-3003`; `Gc/CasGc.cpp:3057-3068`; `Gc/CasGcScheduler.cpp:366` |
| CAS-033 | Med (LIVENESS)| 🔴 still-present     | `Gc/CasGc.cpp:1833-1842`; `Gc/CasGc.cpp:2079-2080`; `Gc/CasGc.cpp:2170-2171` |
| CAS-044 | Med (LEAK)   | 🔴 still-present     | `Pool/CasRefLedger.cpp:2890-2984`; no reconciler in `Gc/**`                  |
| CAS-085 | Low          | ✅ fixed             | `Pool/CasRefLedger.cpp:174-179`                                              |
| CAS-088 | Low          | 📐 by-design         | `Gc/CasGc.cpp:2488-2903` (rebuild is the recovery); `CasGcScheduler.cpp:254-278` |
| CAS-089 | Low (PERF)   | 🔴 still-present     | `Gc/CasGc.cpp:1362, 1582, 1880-1882` (regular round intake not streamed)     |
| CAS-092 | Low (LEAK)   | ✅ fixed             | tree-wide grep: no `shard_write_seq` remains; snapshot+log ref model replaces it |
| CAS-106 | Low (CONFIG) | 📐 by-design         | `Pool/CasPool.h:84,90-99,103`                                                |
| CAS-108 | Low (DAY2)   | 🔴 still-present     | `Gc/CasGc.cpp:2570-2594, 2861, 2874-2879, 2338-2367`                         |
| NEW-1   | Med          | 🔴 new               | `Backend/CasObjectStorageBackend.cpp:60-75`                                  |
| NEW-2   | Low          | 🔴 new               | `Gc/CasGc.cpp:2989-3003`                                                     |
| NEW-3   | Low          | 🔴 new               | `Gc/CasGc.cpp:517-521`                                                       |
| NEW-4   | Low          | 🔴 new (dup CAS-050) | `Gc/CasGc.cpp:2756-2769`                                                     |
| NEW-5   | Low          | 🔴 new               | `Pool/CasRefLedger.cpp:2970-2977`                                            |

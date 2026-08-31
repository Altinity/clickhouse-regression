# gc-protocol -- fresh audit 2026-08-31

## Scope

- Files/dirs examined at `ceee42c51a06cb05e2c9a2d811ef7e1726825552`:
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/` (`CasGc.cpp`/`.h`,
  `CasGcScheduler.cpp`/`.h`, `CasGcMetaWriter.cpp`/`.h`, `CasOrphanManifestSweep.cpp`/`.h`,
  `CasNamespaceJanitor.cpp`/`.h`, `CasBlobInDegree.cpp`/`.h`, `CatalogLifecycleReconciler.cpp`/`.h`,
  `CasGcMaintenanceState.cpp`/`.h`, `CasGcShardPlan.cpp`/`.h`), plus the GC-adjacent slices of
  `Pool/CasPartWriteTxn.cpp` (stage-then-precommit order), `Pool/CasRefLedger.cpp`
  (`resolveNamespaceLife` / catalog birth), `Pool/CasRefCatalog.cpp`, `Tools/CasFsck.cpp`
  (whether `gc/` is enumerated).
- Angles required by the brief: lease/heartbeat/steal, fold, in-degree, condemn/graduate/delete,
  orphan-manifest sweep after `2649bce42db`, namespace janitor, generation prune, ref-cleanup
  catalog stillness after `83c03e26b18` (Filimonov 2026-08-21: still required whole-catalog token
  stillness), shutdown/cancellation of a round, meta-job ownership after `7f932d31352`.
- Explicitly out of scope: `rebuildBaseline` / `previewDeletes` / `SYSTEM CAS GC REBUILD`
  (`gc-rebuild-feature`); write-protocol adopt forms except where they set a GC fence premise;
  fsck/inspect as products.

Static reasoning only. Line numbers are from this pin.

## Findings

### gc-protocol-1 -- ref-cleanup still bails on whole-catalog token movement (Medium)

- Anchor: `Gc/CasGc.cpp:3275-3374` (`cleanupRefObjects` / `deleteRefObject`) at ceee42c
- Trigger: any concurrent catalog mutation in *another* namespace (table create, drop, or
  `Creating`→`Live`) while this round's post-CAS ref-object cleanup is deleting covered logs or
  snapshots. The catalog object token changes; the next `deleteRefObject` returns false; the
  caller `return`s out of the whole pass (`:3373`, `:3385`).
- Evidence: before every exact delete the helper re-reads the whole catalog and refuses unless
  `current_catalog.token != folded.catalog_cut->token` is false *and* the per-row identity still
  matches (`:3290-3293`). The per-row checks (`current_entry_it`, `observed_entry`,
  `current_life`) are sufficient to prove this namespace was not dropped or reborn. The token
  comparison is pool-global: one unrelated birth or removal flips it. On refusal the function
  does not continue to the next key or the next namespace — it stops the phase. `83c03e26b18`
  changed only `Pool/CasRefLedger.cpp` (presence probe and cold-reader admission); this GC site
  was not touched. Under a parallel CREATE/DROP workload the phase therefore starves the same
  way Filimonov recorded on 2026-08-21.
- Notes: same root cause as CAS-079. Not data loss — covered logs leak until a later quiet
  round. Fail-closed and loud (`LOG_DEBUG` "catalog observation/life moved").

### gc-protocol-2 -- orphan sweep still nominates a manifest whose namespace has no catalog row (Medium)

- Anchor: `Gc/CasOrphanManifestSweep.cpp:700-715,824-914` (`planManifestCursorPage`) at ceee42c
- Trigger: first write into a namespace that does not yet have a catalog row. Production order
  is still `stageManifest` then `precommitAdd` (`Pool/CasPartWriteTxn.cpp:511-609,612-657`;
  callers `Parts/PartFolderAccess.cpp:484-485`, `ContentAddressedTransaction.cpp:381-382,435-436`).
  `stageManifest` PUTs the body. Catalog birth happens only inside `appendRefOps` →
  `namespaceLife` → `resolveNamespaceLife` (`Pool/CasRefLedger.cpp:1288-1295,4829-4844`). If the
  sweep cursor page covers that key in the window, the body is nominated and its blob source
  edges are retired (`:904-914`).
- Evidence: every protection is still gated on `catalog_entry != nullptr`: `prefixEligible`
  (`:701-715`), `Creating` retain (`:751-760`), the recovered `active` set (`:766-800`), the
  `active` membership test (`:817`), and `manifestDeletionPremise` (`:828-855`). With a null
  entry control falls through to decode + nominate. The shipped comment at `:824-827` ("creation
  publishes its row before any life-owned object") is still false on this pin. `sweepNamespace`
  remains the opposite polarity (`:121` in the same file: no entry or `Creating` → return 0).
  Source-edge ids are per-manifest, so a shared blob named by another live manifest is not
  driven to zero — the damage is this body plus this build's exclusive blobs, then a loud
  promote failure and a `ManifestBodyMissing` hold that shuts `suppress_destructive` pool-wide
  until the build is provably dead.
- Notes: same root cause as the 2026-08-12 `gc-protocol-2` / CAS-022 residual. Window is the
  stage-to-precommit gap on a namespace that has never been opened for append. Outcome is loud,
  not silent data loss.

### gc-protocol-3 -- a referenced generation that leaves the seal on a suppressed round is never reclaimed (Medium)

- Anchor: `Gc/CasGc.cpp:3455-3528` (`pruneSupersededGenerations`), `:962-1031` (`handoff_reclaim`) at ceee42c
- Trigger: an idle gc-shard keeps a `RunRef` pointing at generation `G` via `carryParentRefs`
  (`:2846-2867`). A later non-suppressed prune walks past `G` while it is still in
  `referenced_generations` (`:3503-3508` `continue` inside `for (; …; ++g, ++pruned)`), so
  `snap_pruned_through` advances past `G` (`:3528`). Then a round that *does* fold a delta for
  that shard also has `suppress_destructive == true` (one hold or anomaly anywhere). The new
  seal drops `G`. Hand-off substitutes `kNoRuns` (`:997-999`) and the comment at `:987-996`
  states that suppression *loses* this one-shot difference.
- Evidence: wholesale prune never revisits a generation behind `snap_pruned_through` (`:3455-3458`,
  `:3495-3502`). Hand-off is the only other `deletePrefixWholesale` of `gc/gen/<g>/`. The code
  names `fsck` as the backstop (`:971-972`, `:995`). `Tools/CasFsck.cpp` still has no `gc/` /
  `gcGenPrefix` listing, so the named backstop does not exist. The leaked prefix is a fold seal
  plus that shard's source-edge run (proportional to the shard's edge population), not user
  blobs.
- Notes: same residual as CAS-074. Storage-only, unbounded, no self-heal. The 2026-08-12 claim
  that a crash in this window is "single-crash, no permanent leak" is still wrong for the
  *suppressed* path: the cursor has already moved.

### gc-protocol-4 -- every round, including a defer, fully lists and materializes `cas/ns/stream/` with no budget (Medium)

- Anchor: `Gc/CasGc.cpp:3637-3676` (`enumerateRefPrefix`), `:508` / `:571-577` (called before
  defer; deferred round drops the scan) at ceee42c
- Trigger: any pool whose ref-object count is large. Cost and peak memory are O(all ref-log +
  snapshot + ckpt keys), re-paid every `gc_interval_sec`, including rounds that then defer.
- Evidence: `forEachListedKey` over `layout.casRefsPrefix()` retains every key in `scan.keys`
  (`:3653`) and every log id in `logs_by_life` / `max_log_by_life` (`:3660-3663`). No
  `GcRoundWorkBudget` cap applies. The orphan sweep, janitor, and eight `gc_round_*` budgets
  are all bounded; this LIST is not. The fold itself walks by exact GET from the sealed cursor
  and does not trust the listing for intake, so LIST truncation cannot under-fold — this is
  liveness/memory, not correctness.
- Notes: same shape as CAS-035. Skip-unchanged (`shouldDeferRound`, `:268-277`) does not avoid
  the expensive step.

### gc-protocol-5 -- a janitor LIST error rewinds the durable cursor to empty (Low)

- Anchor: `Gc/CasNamespaceJanitor.cpp:23-30` (`NamespaceJanitor::runOnePage`) at ceee42c
- Trigger: a transient LIST failure on `namespaceRootPrefix()`.
- Evidence: the `catch` writes `GcMaintenanceState{}` (empty `janitor_cursor`) via
  `casGcMaintenanceState` and rethrows. `runNamespaceJanitorPage` (`CasGc.cpp:342-344`) logs
  and continues the round. The next successful page starts at the keyspace origin. Deletes
  already issued stay exact-token/idempotent; the only effect is re-walking already-decided
  prefix and delaying the unvisited tail.
- Notes: same root as CAS-078. Delayed reclamation only.

## By-design / info / non-actionable

- **Lease has no TTL.** Steal is differential: `{owner, seq}` and `{hb.owner, hb_seq}` both
  frozen across two `allow_steal=true` loop observations (`CasGc.cpp:4426-4464`). Manual
  rounds and rebuild pass `allow_steal=false` and do not arm `last_seen_*` (`:4447-4462`).
  `pulseHeartbeat` (`:4357-4371`) is advisory and discards the `casPut` result. The class
  comment (`CasGc.h:377-393`) states the lease is work deduplication: blob deletes are
  exact-token against previously published `delete_pending`; a deposed leader can duplicate
  work, not roll back. Matches Filimonov CAS-003.
- **Fold / in-degree / condemn-graduate-delete.** Intake walks by exact GET from the sealed
  cursor; a hold or unproven frontier sets `suppress_destructive` (`CasGc.cpp:2932-2934`)
  from anomalies ∪ carried holds ∪ incomplete frontier. In-degree is a source-edge *set*
  (`CasBlobInDegree.cpp:379-390`): duplicate `+1` is idempotent, unmatched `-1` is counted.
  `settleEntry` (`:439-512`) spares on recovered in-degree before any delete; graduation
  requires `condemn_round < current_round` and a confirmed durable `Condemned` marker
  (`:481-508`, `CasGc.cpp:1751-1761`). The only content delete is the pre-CAS
  `deleteExact` of previously published pending entries (`CasGc.cpp:633-666`), gated again
  at the site (`:664-665`). Three-round grace holds.
- **2649bce orphan-sweep skip.** An undecodable manifest body is retained, counted
  (`orphan_sweep.undecodable`), and the cursor advances past it
  (`CasOrphanManifestSweep.cpp:879-896`). It no longer aborts the round. CAS-040 closed.
- **7f932d3 meta-job ownership.** `GcMetaWriter` jobs capture only a `shared_ptr<State>`
  (`CasGcMetaWriter.cpp:103,140,149`). `runRegularRound` installs `SCOPE_EXIT` →
  `drainOnExitNoThrow` (`CasGc.cpp:364`) and a throwing `drain()` barrier before the
  `gc/state` CAS (`:891-894`). A job cannot reach a destroyed `Gc`.
- **Shutdown.** `CasGcScheduler::stop` (`CasGcScheduler.cpp:75-92`) sets `stopping`,
  notifies, joins both workers, then clears `i_am_leader`. An in-flight `runRegularRound`
  is not cooperatively cancelled — `stop` waits it out. No `stopping` / cancel probe exists
  inside `fold`. The durable lease is not released. Accepted extra round if `stop` races
  `gc_round_mutex` (`:294-297`). Not a correctness break.
- **Spared blobs keep durable `Condemned` meta.** Documented ADD-ONLY
  (`CasGc.cpp:769-779`, `CasGcMetaWriter.cpp:41-50`). The sole `→ Clean` writer is a
  writer's fresh incarnation. Not re-raised.
- **Catalog drain** still refuses to drop a `Removing` row whose parent carries a hold
  (`CatalogLifecycleReconciler.cpp:40-44`). Leader fence is re-checked on every step
  (`CasGc.cpp:4506-4520`).
- **`mount_obs` and `rounds_since_last_fold_`** are process-local. Conservative on failover.

## Closed-since-2026-08-12

- Undecodable orphan manifest wedges every subsequent round (CAS-040 / 2026-08-12
  coverage of the sweep abort): closed by `2649bce42db` — skip, count, continue.
- `~Gc` / meta-pool job outliving the state it referenced: closed by `7f932d31352`
  (`GcMetaWriter` shared `State` + `drainOnExitNoThrow`).
- Manifest-trust adopt as a GC-protocol High (2026-08-12 `gc-protocol-1`): not re-derived
  here. Filimonov CAS-002 is by design (`§4` / `8fe6331`); the GC fence (marker +
  in-degree spare + exact-token) is unchanged. Write-path adopt belongs to `write-protocol`.
- "Lease has no expiry ⇒ destructive phases are unfenced" as a Medium defect: closed as
  a *finding* (CAS-003 by design). The shape remains; the consequence does not.

## Coverage

- Reviewed: lease/heartbeat/steal; `runRegularRound` phase order; fold intake and
  `suppress_destructive`; in-degree reduce / `settleEntry` / condemn / graduate / redelete;
  orphan-manifest planner after `2649bce`; namespace janitor page + fence; generation prune
  + hand-off; `cleanupRefObjects` catalog revalidation after `83c03e2`; scheduler
  start/stop/heartbeat and round-exit meta drain.
- N-A: mixed-version GC peers (one `gc/state` per pool; no peer RPC).
- Deferred: rebuild / dry-run / SQL vs CLI postures (`gc-rebuild-feature`); S3/GCS
  capability probes; runtime cost of the unbudgeted LIST (static only).

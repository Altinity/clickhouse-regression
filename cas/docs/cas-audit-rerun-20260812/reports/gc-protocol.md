# gc-protocol -- fresh audit 2026-08-12

## Scope

Static, code-only audit of the **normal (non-rebuild) GC round** in the working tree of
`/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base
`842f2b37b8f`.

Throughout, `CA/` abbreviates
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Primary area: `CA/Gc/**` (17 files) plus `CA/Pool/CasRefLedger.cpp` where the ref log is
committed and the checkpoint frontier is published (GC folds against that frontier).
Adjacent files were read only far enough to decide GC questions: `CA/Pool/CasPartWriteTxn.cpp`
(the adopt/resurrect protocol that GC's condemn marker is supposed to fence),
`CA/Pool/CasRefCkpt.cpp`, `CA/Pool/CasRefCatalog.cpp`, `CA/Pool/CasServerRoot.cpp`
(mount-lease fence-out), `CA/Formats/CasGc*Format.cpp`.

Explicitly **out of scope** (covered by sibling audits): `Gc::rebuildBaseline`
(`CA/Gc/CasGc.cpp:2623-3015`) and `newestFoldSealRef`/`probeGenerationForSeal`, which exist only
to serve it; `SYSTEM CAS GC REBUILD` semantics; fsck/inspect tooling.

Calibration accepted without re-derivation: all CAS tests are deleted in the working tree;
`Mode::EmulatedSingleProcess` is auto-selected for local object storage; `gc_shards` is
creation-time-only and its range validation lives in dead code (`ShardReducer`,
`manifestCleanupShard` in `CA/Gc/CasGcShardPlan.cpp` have no caller) -- reported by
`coverage-map`.

No code was built or run. Every finding below is anchored to current source lines.

## GC protocol as implemented

A round is driven by `CasGcScheduler::loop` (`CA/Gc/CasGcScheduler.cpp:219-277`), which ticks
every `gc_interval_sec` (default 60, `CA/ContentAddressedSettings.cpp:32`) and calls
`Gc::runRegularRound` (`CA/Gc/CasGc.cpp:415-945`). A second thread,
`CasGcScheduler::heartbeatLoop` (`CA/Gc/CasGcScheduler.cpp:279-310`), pulses at
`max(50ms, interval/4)` (`CA/Gc/CasGcScheduler.cpp:41-43`) but only while `i_am_leader`
(`:299`), which is set in `onLeaseAcquired` (`:92-103`) and reset from the round's report
(`:215`, `:248`, `:273`).

**Phase 0 -- leadership.** `Gc::acquireOrRenewLease` (`CA/Gc/CasGc.cpp:3105-3193`) CASes
`gc/state`. Self-renew bumps `lease.seq` (`:3140-3153`). A foreign owner is stolen only if the
caller has a prior observation, the `{owner, seq}` pair is byte-identical to that observation,
and `gc/hb` has not advanced since (`:3155-3173`). There is **no TTL and no wall-clock or
monotonic component**: liveness is "nothing moved between my two reads".
`Gc::pulseHeartbeat` (`:3089-3103`) unconditionally overwrites `hb.owner` with the caller's
`gc_id`, increments `hb_seq`, and discards the `casPut` outcome (`:3102`). `gc_shards` in
`gc/state` is cross-checked against `_pool_meta` and mismatch is fatal (`:3135-3138`).
`gc/state` vanishing after it was once observed is fatal (`:3113-3118`).

**Phase 1 -- pre-fold catalog drain.** `drainCompletedRemoving` (`:3195-3234`) reads the adopted
parent seal and hands it to `CatalogLifecycleReconciler::reconcile`
(`CA/Gc/CatalogLifecycleReconciler.cpp:65-119`), which removes `Removing` catalog rows whose
parent seal row carries `cleanup_evidence` and **no** hold (`:32-49`). Every step re-checks the
leader fence (`CA/Gc/CasGc.cpp:3215-3230`); loss of authority aborts the round (`:455-457`).

**Phase 2 -- mount fencing (heartbeat floor).** `computeHeartbeatFloor`
(`CA/Pool/CasServerRoot.cpp:455-540`, called at `CA/Gc/CasGc.cpp:465-504`) lists
`_server_roots/*/mount`, and for any lease whose write token has been *unchanged* for
`mountObservationThresholdMs` on the GC leader's own monotonic clock, flips `gc_fenced` with a
token-exact overwrite. This is the mechanism that stops a sleeping writer from resuming into a
folded window. The observation map is per-`Gc`-object and in-memory, so a GC failover restarts
the observation (conservative).

**Phase 3 -- discovery.** `listRefPrefix` (`:2595-2621`) does a full, unpaged LIST of
`cas_refs/` (`enumerateRefPrefix`, `:2561-2593`), then reads the ref catalog
(`CasRefCatalog::read`, mandatory -- absence is fatal, `CA/Pool/CasRefCatalog.cpp:41-50`) and the
adopted fold seal. `buildRefWalkPlan` (`:180-256`) makes the **catalog the universe**: one row
per non-`Creating` catalog entry (`:188-200`); sealed parent rows, listed lives and listed tails
are then merged *into* those rows and dropped if they have no catalog row (`:202-254`).

**Phase 4 -- defer decision.** `shouldDeferRound` (`:279-289`) skips the fold when no shard
changed, no graduation is due (`graduationDue`, `:2534-2559`, which fails **open toward more
work**: an unreadable seal returns `true`), and `rounds_since_last_fold_` (process-local,
`:424`) is below `gc_fold_max_defer_rounds` (8, `CA/Pool/CasPool.h:66`). A deferred round still
runs the namespace janitor with deletes suppressed (`:560`) and does **not** advance `gc/state`.

**Phase 5 -- fold** (`Gc::fold`, `:1229-2260`), the heart of the protocol:

- *Intake*: for every catalog life, walk the ref log from the sealed cursor
  (`coverage.last_folded_ref_id`) forward by **exact GET** of each successive id
  (`:1662`), never from the LIST. The walk stops at the namespace's
  `_ckpt.committed_through` (`:1649-1660`, `:1800-1824`); reaching it sets
  `frontier_proven`. Any absence, undecodable body, unproven epoch crossing or missing manifest
  body raises a `hold` (`:1561-1582`, `:1669-1698`, `:1720`, `:1775-1776`) which is carried in
  the seal and re-armed each round (`:1854-1867`).
- *Edges*: `foldManifestEdges` (`:961-1025`) reads each named manifest body, fails closed on
  ref/namespace mismatch (`:974-979`) and on non-admitted hash algos (`:980-997`), and emits
  `BlobDelta{ref, source_id = hash(manifest_id, path), remove}`. In-degree is a **set of source
  edges**, not a counter, so a duplicated `+1` cannot over-count and a duplicated `-1` is a
  no-op (counted as `unmatched_removes`, `:2171-2188`).
- *Suppression gate* (`:2057-2065`): destructive work runs **only** when there are zero
  anomalies, zero carried holds, and `frontier_proven == frontier_namespaces` with a non-empty
  or provably-empty catalog. Any deficit is attributed and logged (`FrontierDeficit`,
  `:1189-1227`).
- *Reduce/condemn* (`CA/Gc/CasBlobInDegree.cpp:312-555`): the prior generation's source-edge
  runs are merged with this round's deltas and the sweep's `source_retirements`. A blob that is
  *touched* and ends with zero edges is HEAD-observed and **condemned** (`head_blob`,
  `CA/Gc/CasGc.cpp:1296-1339`), which records `{token, size, condemn_round}` as a sentinel row
  and schedules a durable `MetaState::Condemned` marker (`:352-360`, `:89-98`).
- *Graduation* (`settleEntry`, `CA/Gc/CasBlobInDegree.cpp:368-416`): a condemned entry with
  `condemn_round < current_round`, still zero in-degree, non-suppressed, **and a confirmed
  durable condemn marker** (`confirm_condemned_marker`, `CA/Gc/CasGc.cpp:1350-1372`) becomes
  `delete_pending`. Recovered in-degree at any point sends it to `spared` (`:381`), never to a
  delete.
- *Replacement* (`closeBlob`, `CA/Gc/CasBlobInDegree.cpp:424-449`): if the live token now
  differs from the condemned token, the stale entry is superseded and the *current* token is
  re-condemned from scratch.
- *Seal write* (`CA/Gc/CasGc.cpp:2244-2255`): `validateFoldSealForWrite` then
  `putDeterministicArtifact` (byte-identical re-put tolerated, divergence fatal,
  `CA/Gc/CasBlobInDegree.cpp:300-310`). Two whole-round invariants fail closed just before it:
  every folded transaction must have reached a reducer (`:2218-2235`) and the sealed cursor must
  cover exactly the logs applied (`:2237-2242`).

So the grace window is **three rounds**: condemn at R, graduate at >= R+1, exact-token delete at
>= R+2, with in-degree recomputed from scratch at every step.

**Phase 6 -- deletes and commit.** Blob redeletes run first (`:611-665`) with
`deleteExact(key, entry.token)`; a created delete marker is fatal (`:614-617`), a token mismatch
is re-classified `Absent` if the object is really gone (`:619-628`). Outcome logs are written
with `putIfAbsent` and adopted if already present (`:732-762`). The condemn-marker meta pool is
drained (`:772-783`) **before** `gc/state` is CASed forward (`:804-809`); a lost CAS aborts.
Then generation prune (`:2456-2500`), hand-off reclaim (`:822-856`), owner-removed manifest
deletes (`:858-888`), namespace janitor (`CA/Gc/CasNamespaceJanitor.cpp:9-132`), ref-object
cleanup (`:2288-2414`) and the orphan-manifest sweep deletes (`:903-942`).

## Findings

### gc-protocol-1 -- manifest-trust adopt bypasses the condemn marker, so GC can delete a blob a concurrent build has already adopted (High)

- **Anchor.** Adopt without observation: `PartWriteTxn::adoptEvidence`,
  `CA/Pool/CasPartWriteTxn.cpp:478-486` (records `BlobDepRecord{..., token = nullopt,
  adopted = true}` -- no HEAD, no `loadMeta`, no precommit-durability check). Commit accepts it
  unchecked: `PartWriteTxn::promote`, `CA/Pool/CasPartWriteTxn.cpp:675-695` (`if
  (depIsTokened(e.ref)) continue; if (!isTrustedAdopt(e.ref)) throw;` -- neither branch re-HEADs
  the blob or re-proves the source owner). Callers:
  `CA/Parts/PartFolderAccess.cpp:399-402`, `CA/ContentAddressedTransaction.cpp:195`,
  `CA/ContentAddressedTransaction.cpp:824`. GC side: condemn `CA/Gc/CasGc.cpp:1296-1339`,
  graduate `CA/Gc/CasBlobInDegree.cpp:394-410`, delete `CA/Gc/CasGc.cpp:611-628`.
- **Trigger.** Blob `B` is reachable only through committed manifest `M_src`. A build reads
  `M_src` (`createHardLink` does a `Freshness::ForceFresh` view read at
  `CA/ContentAddressedTransaction.cpp:816-824`) and adopts `B` by manifest trust. Before that
  build's own precommit ref-log record is durable, another session drops the ref that owned
  `M_src`. GC folds the `-1`, sees in-degree 0, condemns `B` at round R, graduates at R+1,
  deletes at R+2 (>= ~120 s at the default 60 s interval). The build then stages, precommits and
  promotes; `promote` succeeds because the dep is a trusted adopt. The pool now holds a
  **committed manifest naming a deleted blob**.
- **Evidence.** GC's *only* defence against an in-flight adopt of an already-condemned
  incarnation is the durable `MetaState::Condemned` marker, and the code says so in a shipped
  string: `CA/Pool/CasPartWriteTxn.cpp:273` -- *"observed token is condemned (meta point-read);
  caller must re-upload from source (INV-1)"*. Every other adopt form consults it:
  `observeAndAdmit` at `:261-278` (and additionally enforces EDGE-BEFORE-OBSERVE at `:280-285`,
  i.e. the adopting build's precommit edge must already be durable), and `uploadFromSource` at
  `:445-450` / `:452-476`. `adoptEvidence` is the one adopt form that consults neither the
  marker nor the object, and it is also the one form with **no** EDGE-BEFORE-OBSERVE
  precondition, so nothing forces an edge to exist before the adoption is trusted. The
  `ABORTED`-to-re-upload recovery that makes the marker safe elsewhere
  (`CA/Pool/CasPartWriteTxn.cpp:169-173`, `:186-190`) has no analogue here, and there is no
  source to re-upload from on a hardlink path.
- **Notes.** This is the only path I found where a blob that is *about to become reachable* can
  be deleted; the ordinary dedup-adopt path is provably safe (see Coverage). The residual
  narrowness is that it needs the last other owner to be retired inside the adopt-to-precommit
  window. The GC side is behaving exactly per its own contract -- the gap is that one writer
  path opts out of the contract. A HEAD + `loadMeta` re-proof of trusted-adopt deps inside
  `promote`'s ref-op closure (where the ref table is already held) would close it.

### gc-protocol-2 -- orphan-manifest sweep applies no protection at all to manifests whose namespace has no catalog row (Medium)

- **Anchor.** `planManifestCursorPage`, `CA/Gc/CasOrphanManifestSweep.cpp:546` obtains
  `catalog_entry` (may be `nullptr`), and then **every** protection is conditioned on it being
  non-null: build-liveness `prefixEligible` at `:547-561`, the recovered committed+precommit
  `active` set at `:605-636`, the `active` membership test at `:653`, and
  `manifestDeletionPremise` (coverage/hold/unconsumed-seal/tail-removal) at `:660-682`. With
  `catalog_entry == nullptr` control falls straight through to nomination at `:684-716`, which
  both queues the body for an exact-token delete (`CA/Gc/CasGc.cpp:903-930`) and emits a
  `BlobSourceRetirement` for **every** blob entry (`:710-714`). Those retirements force
  `present = false` and `cur_touched = true` in the reducer
  (`CA/Gc/CasBlobInDegree.cpp:531-537`), which is exactly the state that drives
  `head_blob`/condemn at `CA/Gc/CasBlobInDegree.cpp:450-461`.
- **Trigger.** The first-ever write into a CAS namespace. `PartWriteTxn::stageManifest` writes
  the manifest body (`CA/Pool/CasPartWriteTxn.cpp:547-551`) *before* `precommitAdd`
  (`:576-631`), and `precommitAdd` is what first creates the catalog row, via
  `resolveNamespaceLife` -> `createNamespace` (`CA/Pool/CasRefLedger.cpp:880-889`). Read paths do
  not create rows (`acquireReadableRefTableRuntime` returns `nullptr` for an uncataloged
  namespace, `CA/Pool/CasRefLedger.cpp:412-415`). If a GC round's sweep cursor page covers that
  key in the window, the body is deleted.
- **Evidence.** Contrast the sibling entry point `sweepNamespace`
  (`CA/Gc/CasOrphanManifestSweep.cpp:389-472`), which fails **closed** on the same condition:
  `if (!catalog_entry || catalog_entry->state == NsState::Creating) return 0;` (`:402-404`).
  The paged planner used by the round has the opposite polarity. Consequences of the trigger:
  `promote` fails closed with *"manifest body absent at {} -- failing closed (retry with a fresh
  ManifestId)"* (`CA/Pool/CasPartWriteTxn.cpp:643-646`), and the next fold clamps the whole pool
  into `suppress_destructive` on the missing precommit body (`CA/Gc/CasGc.cpp:1757-1777`) until
  `prefixEligible` turns the precommit provably dead (`:1736-1755`), i.e. until the next mount
  lease renewal publishes a `min_active` past that build.
- **Notes.** Not data loss on this trigger -- the part was never committed and the freshly
  uploaded blobs it condemns really are garbage. It is a spurious write failure plus a
  pool-wide GC stall. The reason I rate it Medium rather than Low is that the same branch would
  delete *committed* manifest bodies and retire their live edges for any namespace that reads as
  absent from a single `get` of the catalog object; nothing downstream would notice.

### gc-protocol-3 -- the GC lease has no expiry, and three of five destructive phases are not re-fenced (Medium)

- **Anchor.** `acquireOrRenewLease`, `CA/Gc/CasGc.cpp:3155-3173`: the steal predicate is purely
  differential (`incumbent_renewed || hb_alive || !allow_steal` -> back off), with no TTL, no
  skew margin and no monotonic clock -- unlike the mount lease, which has both
  (`CA/Pool/CasServerRoot.cpp:505-522`). `pulseHeartbeat` (`:3089-3103`) writes
  `hb.owner = gc_id` unconditionally and **discards** the `casPut` result at `:3102`, so a
  pulse lost to a concurrent writer is indistinguishable from a delivered one. Unfenced
  destructive phases after the lease is taken: blob redeletes `:611-628`, owner-removed manifest
  deletes `:865-884`, orphan-sweep manifest deletes `:906-930`, generation-prefix wholesale
  deletes `:2486-2494` and `:841-852`.
- **Trigger.** A GC leader stalls (process pause, IO stall, or heartbeat writes failing while
  `gc/state` reads succeed) for longer than one scheduler interval so that its heartbeat thread
  misses ~4 pulses. A follower's next two ticks see an unchanged `{owner, seq}` and an unchanged
  `hb_seq` and steal (`:3175-3185`). The stalled leader then resumes and runs its entire
  destructive phase list against a lease it no longer holds; only the final `gc/state` CAS at
  `:804-807` notices, long after the deletes.
- **Evidence.** The asymmetry is the tell: two paths in the same round *do* re-validate before
  each delete -- `cleanupRefObjects` re-reads the catalog **and** `gc/state` and compares
  `lease.owner`/`lease.seq` before every object (`:2338-2354`), and the namespace janitor passes
  a `fence_held` closure doing the same (`:392-399`, consumed at
  `CA/Gc/CasNamespaceJanitor.cpp:98-102`, `:116-117`). The three delete phases above take no such
  callback.
- **Notes.** I could not construct live-data loss from this. Both leaders derive their prune
  floor and referenced-generation set from the same parent seal, so the deposed leader's prune
  set is a subset of what the new leader would keep, and blob deletes are exact-token and
  condemn-marker gated (see Coverage), which makes them idempotent regardless of who issues
  them. What is real is duplicated destructive work under no authority, and the absence of any
  bound on how long a zombie may keep issuing it.

### gc-protocol-4 -- a superseded generation leaks permanently if it leaves the seal during a suppressed round (Medium)

- **Anchor.** `pruneSupersededGenerations`, `CA/Gc/CasGc.cpp:2456-2500`: returns immediately when
  `suppress_destructive` (`:2460`); the cursor `g` starts at `next.snap_pruned_through + 1`
  (`:2475`) and is **strictly monotone** -- a generation that is skipped because it is still
  referenced still advances the cursor past it (`:2479-2484` `continue` inside a
  `for (; ...; ++g, ++pruned)`), and `snap_pruned_through` is committed at `:2496`. Nothing ever
  rewinds it (`rebuildBaseline` carries it forward too, `:2982-2986`). The compensating reclaim
  is `handoff_reclaim`, `:822-856`, whose candidate set is `parent_seal_runs` -- and that set is
  emptied when the round is suppressed (`:831-832`).
- **Trigger.** A cold gc-shard keeps pointing at generation `G`'s source-edge run via
  `carryParentRefs` (`:2023-2041`, runs are carried by reference, not rewritten). Rounds advance;
  prune sweeps past `G` while it is still referenced, so `snap_pruned_through > G` with `G`'s
  objects still on disk. Later the shard finally changes in a round where
  `suppress_destructive` is true (one anomaly or one held namespace anywhere in the pool is
  enough, `:2063-2064`). That round's seal drops `G`. From the next round on, `G` appears in
  neither the current nor the parent seal, so hand-off never sees it, and prune's cursor is
  already past it.
- **Evidence.** `deletePrefixWholesale` is only ever invoked on `layout.gcGenPrefix(g)` from
  those two call sites (`:844`, `:2490`); there is no periodic reconciliation of
  `<pool>/gc/gen/` against the live seal anywhere in `CA/Gc/**`.
- **Notes.** Storage-only, but unbounded and silent: the leaked objects are a fold seal plus the
  shard's source-edge run, and the run is proportional to that shard's edge population. No
  self-heal path exists.

### gc-protocol-5 -- every round does an unbounded, unbudgeted full enumeration of the ref prefix, including rounds it then defers (Medium)

- **Anchor.** `Gc::enumerateRefPrefix`, `CA/Gc/CasGc.cpp:2561-2593`: `forEachListedKey` over
  `layout.casRefsPrefix()` with a **page** size of 1000 but no total budget and no cursor
  persisted anywhere; every key is retained in `scan.keys` (`:2571`) and every log id is
  additionally retained in `scan.logs_by_life` (`:2578`) and `max_log_by_life` (`:2579-2581`).
  It is called from `listRefPrefix` (`:2597`), which is called at `:511` -- i.e. **before** the
  defer decision at `:515`, so a deferred round pays the full cost and then returns at `:558-562`.
- **Trigger.** Any pool at scale: cost and peak memory are O(total ref-log + snapshot + ckpt
  objects across all namespaces), re-paid every `gc_interval_sec`.
- **Evidence.** Every other scan in the round is explicitly bounded, which shows the budget
  discipline was applied deliberately elsewhere and missed here: the orphan sweep is
  cursor-paged with `manifest_sweep_list_budget_keys` (`CA/ContentAddressedSettings.cpp:40`) and
  a persisted cursor in `gc/state` (`:791-792`); the janitor is paged at 1000 with a cursor in
  `cas_gc_maintenance_state` (`:390`, `CA/Gc/CasNamespaceJanitor.cpp:21-25`, `:119-130`); and
  eight further `gc_round_*` budgets are wired into `GcRoundWorkBudget` at `:440-448`. The ref
  enumeration takes none of them.
- **Notes.** Correctness is unaffected -- the fold walks by exact GET from the sealed cursor
  (`:1662`) and never trusts this listing, so LIST truncation or staleness cannot cause
  under-folding (see Coverage). This is a scaling/liveness finding only. It also makes the
  skip-unchanged optimisation (`shouldDeferRound`, `:279-289`) far less valuable than it looks,
  since the expensive part runs first regardless.

### gc-protocol-6 -- a spared blob keeps its durable `Condemned` marker forever (Low)

- **Anchor.** When in-degree recovers, the entry goes to `spared`
  (`CA/Gc/CasBlobInDegree.cpp:381`) and GC calls `forgetCondemnMarker`
  (`CA/Gc/CasGc.cpp:691`), which only erases an **in-process** set (`:374-378`,
  `condemn_markers_confirmed` at `CA/Gc/CasGc.h:443-444`). No code path ever transitions the
  durable meta back to `MetaState::Clean`: the only `Clean` writers are
  `CA/Pool/CasPartWriteTxn.cpp:290-291` (adopt backfill when meta is absent) and `:361-379`
  (resurrect). `writeCondemnedMeta` short-circuits on an already-`Condemned` meta
  (`CA/Gc/CasGc.cpp:95-97`), so the stale marker is also never refreshed.
- **Trigger.** Any blob whose condemnation races a fresh reference -- the exact case the code
  calls out at `:669-672` (*"a fresh dedup-adopt raced the condemn; spared (never a fail-closed
  delete)"*).
- **Evidence.** From then on every dedup adopt of that blob takes the resurrect branch:
  `observeAndAdmit` throws `ABORTED` (`CA/Pool/CasPartWriteTxn.cpp:263-278`), the caller catches
  it (`:169-173`) and re-uploads the full body (`:182`), even though the blob is provably live.
- **Notes.** Safe in both directions -- it only ever costs a redundant upload, and the
  re-upload rewrites the meta `Clean`, so it self-clears on first reuse. Worth noting because it
  turns a rare GC race into a permanent per-blob dedup regression until the blob is next
  written.

## By-design / info / non-actionable

- **Fail-open branches that are safe by direction.** `graduationDue` returns `true` when the
  seal is unreadable (`:2544-2549`) -- more work, not less. `confirm_condemned_marker` returns
  `false` on any meta read error (`:1362-1371`) -- carries the entry rather than graduating it.
  Meta-pool job failures are advisory and never wedge the round (`:320-350`), which is sound
  precisely because graduation independently re-proves the marker.
- **Deliberate hard stops.** Six `CORRUPTED_DATA` refusals halt the round rather than guess:
  missing adopted seal (`:1283-1288`, `:2609-2612`), a parent seal not total over `gc_shards`
  (`:2033-2038`), a snapshot with no surviving log and no sealed cursor (`:1491-1496`), a cursor
  that does not close the run it walked (`:1940-1945`), folded-but-unapplied transactions
  (`:2229-2234`), and a cursor advanced past an unapplied log (`:2237-2242`). All five of the
  last four are pure round-local invariants over data the round itself produced.
- **`ref_scan.holds` / `checkpoint_observations` are dead in production.** `buildRefWalkPlan`
  consumes them at `:224-244`, but `listRefPrefix`/`enumerateRefPrefix` never populate them;
  only `tests::buildRefWalkPlanForTest` (`:261-264`) does. Holds actually reach the plan through
  `parent_ref_lives` (`:202-213`). Harmless today, but it means two of the five merge loops in
  the plan builder are untested-by-construction now that the tests are deleted.
- **Dropped parent rows do not suppress.** A sealed ref-life row with no catalog row is dropped
  with a `CASGCUnmatchedAdoptedParentLives` ProfileEvent and a counter (`:204-213`), discarding
  its cursor **and any carried hold**, without forcing `suppress_destructive`. This is currently
  unreachable because `CatalogLifecycleReconciler::selectEligible` refuses to remove a row whose
  parent carries a hold (`CA/Gc/CatalogLifecycleReconciler.cpp:40-44`) and
  `deleteCompletedRemovingAtSnapshot` re-proves it (`ProofRefused`, `:108-111`). Listed as a
  latent fail-open: it is the one way a hold can silently disappear.
- **`deleteConfirmedMeta` deletes any meta state, not just `Condemned`** (`:100-106`). It can
  delete the `Clean` meta of a blob resurrected between the delete and the meta load. Benign:
  an absent meta is treated as not-condemned and backfilled on next adopt
  (`CA/Pool/CasPartWriteTxn.cpp:287-292`).
- **`mount_obs` is process-local**, so GC failover restarts the mount token-stability
  observation from zero (`CA/Gc/CasGc.h:432`). Conservative (delays fencing, never advances it).
- **`rounds_since_last_fold_` is process-local** (`CA/Gc/CasGc.h:424`) and resets on restart or
  leadership change, so `gc_fold_max_defer_rounds` is best-effort. Cannot stall reclaim, because
  `graduationDue` overrides deferral whenever anything is pending (`:2550-2557`).
- **`gc_frontier_probe_budget` defaults to `UINT64_MAX`** (`CA/Pool/CasPool.h:64`), so the
  budget-exhaustion suppression path at `:1444-1449` / `:1886-1894` is unreachable in a default
  deployment.
- **`min_active` staleness in `prefixEligible`** (`CA/Gc/CasOrphanManifestSweep.cpp:384-386`):
  the mount lease's `min_active` is only refreshed on lease renewal
  (`CA/Pool/CasServerRoot.cpp:741-745`), so a build started since the last renewal is not
  reflected and `min_active == UINT64_MAX` makes any same-epoch build "eligible". This is *not*
  exploitable on its own, because `manifestDeletionPremise` independently requires
  `manifest.prefix.writer_epoch < cov.last_folded_ref_id.writer_epoch`
  (`CA/Gc/CasOrphanManifestSweep.cpp:357-361`), which no current-epoch build can satisfy. Noted
  because the two guards are load-bearing for each other and only one of them is documented as
  such in a shipped string.

## Coverage

**Live-blob-deletion guards traced and found sound.** The ordering that prevents deleting a
reachable blob is a three-legged fence, and each leg holds:

1. *Exact-token delete.* Every blob delete is `deleteExact(key, entry.token)` with the token
   captured at condemn time (`:613`). Any resurrect writes a new incarnation
   (`backend.resurrect`, `CA/Pool/CasPartWriteTxn.cpp:463`, `:471`), so a resurrected blob
   token-mismatches and is classified `Replaced`, not deleted (`:630-633`). A created delete
   marker (versioning enabled) is a hard error rather than a silent soft-delete (`:614-617`).
2. *Condemn marker before graduation.* A blob cannot become `delete_pending` until its durable
   `MetaState::Condemned` marker is confirmed (`CA/Gc/CasBlobInDegree.cpp:396`, verified against
   the store at `CA/Gc/CasGc.cpp:1350-1372`), and the marker pool is drained before the round is
   adopted (`:772-783`). `observeAndAdmit` reads that marker on every ordinary adopt and forces
   a re-upload if set (`CA/Pool/CasPartWriteTxn.cpp:261-278`).
3. *Edge before observe.* An adopt of an existing incarnation is refused unless the adopting
   build's precommit ref-log record is already durable
   (`CA/Pool/CasPartWriteTxn.cpp:280-285`). Since `appendRefOps` only returns success after the
   `_ckpt` committed frontier has been published past that record
   (`CA/Pool/CasRefLedger.cpp:2534-2572`; failure marks the lane
   `requireRecovery` and throws), any adopt that took the *old* token is guaranteed to have its
   `+1` edge below `committed_through` -- which is exactly the frontier the next fold walks to
   (`CA/Gc/CasGc.cpp:1649-1660`). So the R+1 fold must see the recovered in-degree and spare the
   blob before it can ever graduate. This is the key closure, and it is tight.

  Finding gc-protocol-1 is exactly a violation of leg 3 by the one adopt form that skips both
  leg 2 and leg 3.

**Also checked and found sound:**

- *LIST truncation / staleness cannot under-fold.* The intake walk resolves successive ids by
  exact GET (`:1662`) and derives its universe from the mandatory ref catalog, not from the
  listing (`:188-200`, `:1432-1471`). A namespace missing from the LIST is still walked
  (`kNoListing` at `:1422`, `:1435`); a namespace that cannot be walked is either held or
  counted as an unproven frontier, and both suppress all destructive work (`:2057-2065`).
- *Under-count vs over-count.* In-degree is a set keyed by `sourceEdgeId(manifest_id, path)`
  (`CA/Gc/CasBlobInDegree.cpp:134-150`, with source_id 0 reserved as a sentinel and a collision
  with it treated as a `LOGICAL_ERROR`). Duplicate `+1` is idempotent (over-count impossible);
  duplicate `-1` is a no-op that is counted and reported (`:2171-2188`). Sentinel rows are
  validated on read (`CA/Gc/CasBlobInDegree.cpp:72-97`) and runs are checksum-verified
  (`:103`, `:573`).
- *Restart safety / monotonicity of persisted state.* `gc/state` is a single CASed object
  (`:804`); `round` and `lease.seq` only increase (`:3143`, `:3177`, `:790`);
  `snap_pruned_through` only increases (`:2475`, `:2496`); the fold seal and source-edge runs are
  written with `putDeterministicArtifact`, making a crash-and-retry byte-identical or fatal
  (`CA/Gc/CasBlobInDegree.cpp:300-310`). A crash between the seal write and the `gc/state` CAS
  leaves the old generation adopted and the next round simply re-folds at a new attempt.
  `decodeGcState` rejects a zero `gc_shards` and trailing bytes
  (`CA/Formats/CasGcStateFormat.cpp:62-67`).
- *Outcome logs.* `putIfAbsent` with adopt-existing-bytes and a fatal refusal on undecodable
  content (`:736-750`); keyed under the generation prefix
  (`CA/Formats/CasLayout.h:195-198`) so they are reclaimed with the generation.
- *Catalog drain.* Removes a `Removing` row only with matching no-hold cleanup evidence, with a
  leader-fence check on every step and a `LOGICAL_ERROR` if the row survives
  (`CA/Gc/CatalogLifecycleReconciler.cpp:32-118`). The loop is bounded by the number of eligible
  rows.
- *Namespace janitor.* Cursor-paged, fence-checked before each delete, refuses to delete when
  the catalog life index is ambiguous, and leaves the cursor unadvanced when the page was not
  fully decided (`CA/Gc/CasNamespaceJanitor.cpp:36-46`, `:98-102`, `:116-130`).
- *Ref-object cleanup.* Deletes only logs/snapshots strictly covered by the durable cursor and
  the checkpoint snapshot base, revalidates catalog observation, life identity **and** GC fence
  before every delete, and stops the whole namespace on the first refusal (`:2312-2412`).

**Not examined (deliberately):** `rebuildBaseline` and its enumeration helpers;
`previewDeletes` (read-only, `:3017-3080`); `CasFsck`/`CasInspect`; the S3/GCS backend
capability probes; anything under `Backend/` beyond the `DeleteOutcome`/`CasOutcome`
classification consumed by GC.

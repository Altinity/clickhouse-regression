# tier3 (deep sweep: GC internals and admin/tools surface) -- fresh audit 2026-08-12

## Scope and tier definition

Static, line-level sweep of the GC engine and the administrative/observability surface on
`/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`,
working tree as-is. No edits, no checkout, no execution.

This is a *tier* audit: it is not organised around one protocol question but around one region of code,
read line by line looking for implementation defects — accounting and counter errors, phase ordering,
shard planning, budget/limit handling, partial-failure handling *inside* a phase, state persistence
round-trips, sweep predicates with inverted polarity, off-by-one in round/generation handling, tool
output correctness, destructive-flag safety, and system-table column population.

Code-only rule observed: `docs/**` and in-tree comments were not treated as evidence of intent.
Shipped strings (log text, exception text, column `COMMENT`s, tool output) *were* treated as the
contract, because they are what an operator sees. All CAS tests are deleted in this tree, so no test
was used as evidence of intended behaviour.

Cited, not re-derived (owned by sibling audits in this re-run): `adoptEvidence` bypasses the condemn
marker; the GC leadership lease has no TTL; `rebuildBaseline` seeds an empty prior generation; the
orphan sweep skips guards when `catalog_entry` is null; `FsckReport::clean()` excludes the body/meta
counters; `SYSTEM CAS FSCK` hardcodes `detail=false`; `listMounts` keys off `/mount` only. Where a
tier3 finding *compounds* one of those, it says so and adds only the new mechanism.

## Region walked

| File | Lines | Functions / regions actually read |
| --- | --- | --- |
| `Gc/CasGc.cpp` | 3236 | `retiredLogicalSize`, `classifyDeleteOutcome`, `scheduleMetaJob`, `runRegularRound` (whole body: lease, pre-fold drain, heartbeat floor, defer decision, parent seal read, fold call, pending deletes, meta pool wait, round commit, hand-off reclaim, manifest deletes, namespace cleanup, ref-object cleanup, orphan sweep), `reportStuckRemovals`, `runNamespaceJanitorPage`, `fold` (2000-2290), `cleanupRefObjects`, `pruneSupersededGenerations`, `graduationDue`, `readFoldSeal`, `chooseRecoveryGrounding`, `rebuildBaseline`, `previewDeletes` |
| `Gc/CasGc.h` | 472 | `RoundAnomaly`, `RoundReport`, `RebuildReport`, `GcPhaseRecord`, `RefScanSummary`, `RefWalkPlanRow`, `TxnApplyLedger`, `GcRoundWorkBudget`, member state (`rounds_since_last_fold_`, `state_token`, observation fields) |
| `Gc/CasBlobInDegree.cpp/.h` | 578 / 193 | `foldDeltasIntoGeneration`, `openBlob`/`closeBlob`, condemn/graduate/settle transitions, `RetiredEntry`, `CondemnedRow`, `CondemnedSummary` accumulation |
| `Gc/CasGcScheduler.cpp/.h` | 339 / 127 | `loop`, `heartbeatLoop`, `runRoundLogged`, phase-row emission, `runOneRoundNow`, `gcHealth`, `GcHealth` |
| `Gc/CasGcShardPlan.cpp/.h` | 60 / 52 | `blobShard`, `manifestCleanupShard`, `ShardReducer` |
| `Gc/CasNamespaceJanitor.cpp/.h` | 134 / 33 | `runOnePage`, cursor persistence |
| `Gc/CasOrphanManifestSweep.cpp/.h` | 731 / 91 | `planManifestCursorPage`, `activeManifestKeys`, nomination/guard logic, `next_cursor` handling |
| `Gc/CatalogLifecycleReconciler.h` (+`.cpp`) | 58 / 121 | pre-fold catalog drain loop |
| `Gc/CasGcPhaseTimer.h` | 58 | `GcPhaseTimer`, `metric`, sink lifetime |
| `Formats/CasGcStateFormat.cpp` | 116 | `encodeGcState`, `decodeGcState`, caps |
| `Formats/CasGcOutcomesFormat.cpp` | 126 | `encodeGcOutcomes`, `decodeGcOutcomes` |
| `Formats/CasGcMaintenanceStateFormat.cpp` | 67 | encode/decode, cursor cap |
| `Formats/CasFoldSealFormat.cpp/.h` | 490 | GC-consumed aspects: `CondemnedSummary` validation, `RefCoverage`/`RefHold`, both `decodeFoldSeal` overloads |
| `Tools/CasFsck.cpp/.h` | 950 / 120 | `runFsckImpl` (full), `runFsck`, `formatFsckSummary`, `FsckReport::clean`, scoped vs unscoped branches, `blobStillReferenced` |
| `Tools/CasInspect.cpp/.h` | 579 / 12 | all `render*` functions, dispatch by object kind |
| `Tools/CasDecommission.cpp/.h` | 388 / 33 | member removal, slot retirement gating, `DecommissionReport` |
| `programs/disks/CommandCa*.cpp`, `CommandFsck.cpp`, `DisksApp.cpp` | — | argument parsing, flag handling, output formatting |
| `Storages/System/StorageSystemContentAddressedMounts.cpp` | 249 | column set, `read`, fallback row |
| `Interpreters/ContentAddressedGarbageCollectionLog.cpp` | 114 | column set, `appendToBlock` |
| `Interpreters/ContentAddressedLog.cpp` | 73 | column set, `appendToBlock` |

## Findings

### tier3-1 -- Generation hand-off reclaim is one-shot and drops its candidates on suppression, budget exhaustion, or partial drain (Medium)

- **Anchor**: `Gc/CasGc.cpp:2475-2496` (prune skip advances the durable cursor), `Gc/CasGc.cpp:829-856` (the compensating hand-off).
- **Trigger**: a generation that is still referenced by the live seal when it crosses the retention floor, followed by *any* of: (a) the round in which it drops out has `suppress_destructive` set — set by a single fold anomaly, a single held namespace, or an incomplete frontier (`CasGc.cpp:2063-2064`); (b) `gc_round_handoff_prefix_wholesale_budget` (default 5000) is exhausted earlier in the same loop; (c) `deletePrefixWholesale` drains the prefix only partially because `remaining` capped it.
- **Consequence**: the entire `gc/gen/<g>/` prefix leaks permanently. `pruneSupersededGenerations` sets `next.snap_pruned_through = g - 1` at line 2496 even for generations it `continue`d over, so the prune path will never look at `g` again; the hand-off at 833-852 is the only compensation and it is computed solely from *this* round's `parent_seal_runs`. Once this round's seal is written, `g` is absent from every future parent seal, so no future round can nominate it. Note also that unlike the prune loop (2489-2494), the hand-off ignores whether the prefix was fully drained: `deletePrefixWholesale` at 844 is called without the `fully_drained` out-param, and the loop unconditionally moves on.
- **Evidence**: shipped `LOG_TRACE` at 848-851 states the hand-off's purpose verbatim — "post-CAS wholesale reclaim (the prune had skipped it while referenced)" — establishing that the skipped generation *must* be reclaimed here or nowhere. The suppression log at 2082-2098 promises "Graduations and pending deletes are carried; nothing irreversible runs until a pass that clears all three", but this candidate list is not carried: `handoff_candidates` is bound to `kNoRuns` at 832 and the opportunity is consumed. The `handed_off.insert` at 839 happens *before* the budget check at 841-843, so a generation skipped for budget is still counted in the `generations_reclaimed` phase metric at 853.

### tier3-2 -- Round delete/spare/absent counters are derived from the budget-truncated outcome log, so the round report undercounts real deletes (Medium)

- **Anchor**: `Gc/CasGc.cpp:652-656`, `684-690`, `732-768` (report fields recomputed by replaying `log.entries`), `Gc/CasGc.h` `GcRoundWorkBudget::outcomeEntryAvailable`.
- **Trigger**: a round whose redelete + spare cohort exceeds `gc_round_outcome_entry_budget`, default **5000** (`ContentAddressedSettings.cpp:49`) — i.e. any round following a large `DROP`/`TRUNCATE`, which is exactly when an operator watches these numbers.
- **Consequence**: the deletes still happen, but the entries beyond the budget are never appended to the outcome object, and because the report tallies are computed from the written entries, `objects_deleted` / `objects_absent` / `objects_replaced` / `objects_spared` in `RoundReport`, in `system.cas_gc_log`, and in the `SYSTEM CAS GC` result set are silently lower than reality. There is no truncation flag on the round row, so the shortfall is indistinguishable from "GC did less work". Reconciling `entries_condemned` against `entries_redeleted` across rounds — the natural way to check the pipeline is draining — produces a phantom backlog.
- **Evidence**: `outcomeEntryAvailable()` gates the `outcomes.push_back` at 652 and 684 only; the physical `deleteExact` above it is unconditional. The `system.cas_gc_log` column comments (`ContentAddressedGarbageCollectionLog.cpp:43,50`) describe these as "Objects physically deleted this round" and "Pending exact-token blob deletes executed this round", which is not what the columns carry once the budget bites.

### tier3-3 -- `pending_reclaim` is a monotone accumulator that never sheds spared or replaced entries (Medium)

- **Anchor**: `Gc/CasGcScheduler.cpp:170-172`, surfaced at `Storages/System/StorageSystemContentAddressedMounts.cpp:53` and `:181`.
- **Trigger**: any dedup-adopt race or in-degree resurrection — every candidate that comes back as `spared` or `replaced` (412-save) at recheck.
- **Consequence**: the scheduler adds `condemned - redeleted` per round and never subtracts `spared`/`replaced`, so an entry that was condemned in round N and then spared in round N+1 is counted as permanent backlog forever. The column is documented as "Cumulative condemned-minus-deleted backlog", and it is the metric an operator would alert on for "GC is falling behind"; on a workload with steady dedup adoption it drifts upward without bound while GC is perfectly healthy. Nothing resets it short of a process restart.
- **Evidence**: the accumulation site takes only `report.condemned` and `report.redeleted`; `report.spared` and `report.replaced` are populated in the same struct and ignored. Compounded by tier3-2: `report.redeleted` is itself truncated by the outcome-entry budget, so the accumulator's negative term is undercounted as well.

### tier3-4 -- fsck verifies source-edge run checksums only when at least one unreferenced blob exists (Medium)

- **Anchor**: `Tools/CasFsck.cpp:654` (`if (!unref_hashes.empty())`), checksum comparison at `:695-700`.
- **Trigger**: run `cas-fsck` (or `SYSTEM CAS FSCK`) on a pool in which every present blob is reachable — the normal state of a healthy cluster.
- **Consequence**: `report.corrupted_runs` stays 0 and the entire GC snapshot run set goes unverified. Run corruption is precisely the failure that would cause a later fold to mis-plan deletes, and the tool that exists to detect it declines to look unless there happens to be garbage lying around. The summary line still prints `corrupted_runs=0` (`:932`), which reads as "checked, clean" rather than "not checked".
- **Evidence**: `openSourceEdgeRun` / `reader.accumulatedChecksum() != run.checksum` sit three scopes deep inside the `!unref_hashes.empty()` guard; the guard exists to build `unref_hashes` classification data, and the checksum check was placed inside it incidentally.

### tier3-5 -- The stale-edge check is gated on the `detail` flag, making the finding unreachable from SQL (Medium)

- **Anchor**: `Tools/CasFsck.cpp:677` (`if (detail && source_id != UInt128{0})` — the only writer of `unref_edge_sources`), `:707` (`stale_edge_check_available = detail && !unref_edge_sources.empty()`).
- **Trigger**: any fsck invocation with `detail=false`.
- **Consequence**: `report.stale_edge` is structurally always 0 without `detail`, yet the summary prints `stale_edge=0` at `:931` and `clean()` consults it. Combined with the sibling finding that `SYSTEM CAS FSCK` hardcodes `detail=false`, the stale-edge class of corruption can never be reported through the SQL surface at all — only through `clickhouse-disks` with the verbose flag. `detail` is elsewhere used purely as an output-verbosity switch (it controls whether per-object rows are pushed, `:628`, `:807`, `:881`); here it silently changes *what is checked*.
- **Evidence**: `unref_edge_sources[ref].push_back(source_id)` is the sole population site and is inside `if (detail ...)`; line 769 reads `stale_edge_check_available && eit != unref_edge_sources.end()`.

### tier3-6 -- Namespace-scoped fsck skips whole check families but still reports a clean, non-partial result (Medium)

- **Anchor**: `Tools/CasFsck.cpp:831-866` (the scoped `else` branch), versus the unscoped branch at `:598-829`; `runFsck` at `:903-920` sets `partial` only on `TIMEOUT_EXCEEDED`.
- **Trigger**: `cas-fsck --namespace <ns>` (or any call passing a non-empty `namespace_prefix`).
- **Consequence**: the scoped branch performs head checks on reachable blobs and nothing else. Unreferenced-blob classification (`pending_gc`/`awaiting_gc`/`unaccounted`), run-checksum verification, meta/body pairing, and janitor-pending detection are all skipped, but `report.partial` stays false and `clean()` therefore returns true. The summary line prints all of those counters as `0`, indistinguishable from "checked and found none". An operator scoping fsck to one table to make it affordable gets a clean bill of health for checks that never executed.
- **Evidence**: the counters that the scoped path can never increment (`pending_gc`, `awaiting_gc`, `unaccounted`, `stale_edge`, `corrupted_runs`, `meta_without_body`, `body_without_meta`, `namespace_janitor_pending*`) are all printed unconditionally at `:928-937` with no scope marker anywhere in the output string.

### tier3-7 -- `cas-inspect` drops `RefCoverage::hold` when decoding a fold seal (Medium)

- **Anchor**: `Tools/CasInspect.cpp:329-335` (`renderRefCoverage` emits only `classification` and `last_folded_ref_id`); the dropped field is `Formats/CasFoldSealFormat.h:57` (`std::optional<RefHold> hold`).
- **Trigger**: inspect a fold seal on a pool where GC is refusing to do destructive work.
- **Consequence**: `RefHold` is the record of *why* a namespace is held, and a non-empty set of carried holds is one of the three conditions that set `suppress_destructive` (`CasGc.cpp:2063-2064`). The primary diagnostic tool for reading GC state renders the seal to JSON with that field silently omitted, so the operator's first question ("which namespace is blocking GC and why?") cannot be answered from `cas-inspect` output — even though the answer is in the bytes it just decoded.
- **Evidence**: every other optional in the same function is rendered explicitly, including `cleanup_evidence` with an explicit `"null"` branch at `:343-345`; `hold` has no branch at all.

### tier3-8 -- `closeBlob` can only record a replacement for an entry the round already touched (Medium)

- **Anchor**: `Gc/CasBlobInDegree.cpp:428-448` (the `peek_head` / `cur_touched` interaction in `closeBlob`).
- **Trigger**: a blob whose condemned row is carried through a fold in which no delta touches it, while a resurrection replaces the underlying object.
- **Consequence**: the supersede/replacement bookkeeping is reachable only on the touched path, so a carried-but-untouched condemned row keeps its stale token. The subsequent exact-token delete then classifies as `replaced` rather than being suppressed at plan time — which is safe (the 412 saves the object) but is precisely the path that feeds the unbounded `pending_reclaim` drift in tier3-3, and it makes the condemn generation carry a token known to be dead.
- **Evidence**: the guard structure places the head peek behind the touched flag; the settle path immediately below it has no equivalent gate.

### tier3-9 -- Namespace janitor rewinds its durable cursor to the beginning on a transient list failure (Medium)

- **Anchor**: `Gc/CasNamespaceJanitor.cpp:22-31` (`runOnePage`, cursor reset on list error).
- **Trigger**: one failed LIST against the namespace prefix — an S3 5xx or a throttle.
- **Consequence**: the persisted cursor goes back to the start of the keyspace, so the janitor re-walks everything it had already cleared. On a pool large enough that a full walk exceeds the mean time between transient list errors, the janitor never reaches the end of the keyspace — a livelock in which it consumes its per-round budget forever without progressing. A cursor is exactly the mechanism that should survive a transient error; here the error is what destroys it.
- **Evidence**: the failure path assigns the empty cursor rather than leaving the previous value in place; the success path is the only one that advances it, so "leave unchanged" was available and is what the budgeted-stop path already does.

### tier3-10 -- `last_success_age_seconds` collapses "never led" into "succeeded just now", and `ever_succeeded` is computed but never exposed (Low)

- **Anchor**: `Gc/CasGcScheduler.h:74` (`bool ever_succeeded`), `Gc/CasGcScheduler.cpp:317-324` (`gcHealth`), `Storages/System/StorageSystemContentAddressedMounts.cpp:54` and `:182`.
- **Trigger**: query `system.cas_mounts` on a replica whose GC scheduler has never won the lease.
- **Consequence**: the column reads `0`, which for an age column means "zero seconds ago" — the healthiest possible value — for a node that has in fact never completed a round. The disambiguating flag exists in `GcHealth` and is simply not carried into the table's column list; `ever_succeeded` has no reader anywhere in the tree.
- **Evidence**: the shipped column comment at `:54` documents the collision outright ("0 if it never led"), so the ambiguity is known and the fix was already computed one struct away.

### tier3-11 -- A transient `listMounts` failure renders a healthy disk identically to a non-existent pool (Low)

- **Anchor**: `Storages/System/StorageSystemContentAddressedMounts.cpp:146-156` (`list_ok=false` on any exception) falling through to `:199-218` (the synthetic row).
- **Trigger**: one failed LIST of the mount prefix while `system.cas_mounts` is being read.
- **Consequence**: the disk is emitted as a single row with `state` defaulted to the empty string, all lease columns zeroed, and every health column NULL — byte-identical to the row emitted when there is no live pool at all. `state` is documented at `:51` as one of "live, expired, terminated, fenced or corrupt"; the empty string is outside that enumeration and is produced only by this path. Monitoring built on `state` sees a disk drop out of existence on a single S3 hiccup.
- **Evidence**: `col_state->insertDefault()` at `:212` on a `ColumnString`; the exception is logged but nothing distinguishes the two producers of the fallback row.

### tier3-12 -- `gc/state` encoding does not enforce the line cap that decoding enforces (Low)

- **Anchor**: `Formats/CasGcStateFormat.cpp:19-37` (`encodeGcState`, no length check on `manifest_sweep_cursor`) versus the decode-side line cap.
- **Trigger**: a manifest sweep cursor longer than the 64 KiB line cap — reachable because the cursor is an object key echoed from the store and is written back verbatim at `CasGc.cpp:792`.
- **Consequence**: the round commits a `gc/state` that no subsequent `decodeGcState` will accept, wedging GC on that pool until `SYSTEM CAS GC REBUILD` is run. This is an encode/decode asymmetry: the sibling `CasGcMaintenanceStateFormat` caps its cursor at encode time, so the pattern was known.
- **Evidence**: `encodeGcState` writes the cursor with no `checkLine`-style guard; the object cap (1 MiB) is checked, the line cap is not.

### tier3-13 -- Round-scoped observability uses the pre-increment round number and post-fold generation (Low)

- **Anchor**: `Gc/CasGc.cpp:512` (`reportStuckRemovals(*walk_plan, state.round)`), `:564-571` (`GcFoldBegin` emitted with `e.round = state.round`), `:585-595` (`GcFoldEnd` likewise), against `new_round` used by every delete/retire event.
- **Trigger**: any round; visible whenever `system.cas_log` is grouped by `round`.
- **Consequence**: the fold begin/end rows of round N land under round N-1, so grouping the event log by round splits every round's fold markers away from the work they bracket. `reportStuckRemovals` computes candidate age against the stale round, so every stuck-removal warning is off by one round of age — directly under-reporting how long a removal has been stuck. Additionally `e.gen` means the *parent* generation on `GcFoldBegin` and the *new* generation on `GcFoldEnd`, because `fold()` mutates `state.snap_generation` in between (`:2257`); the same column name carries two different generations on two rows of the same event pair.
- **Evidence**: `new_round` is `state.round + 1` and is threaded correctly into `condemn_round` and every delete event; only these observability sites read `state.round` directly.

### tier3-14 -- Phase rows in `system.cas_gc_log` always carry `round = 0` (Low)

- **Anchor**: `Gc/CasGcScheduler.cpp:141` (`Rec row = start;` — phase rows are copies of the Start record, whose `round` is unset), column comment at `Interpreters/ContentAddressedGarbageCollectionLog.cpp:40`.
- **Trigger**: `SELECT ... FROM system.cas_gc_log WHERE round = N`.
- **Consequence**: every Phase row is filtered out, because the round number is only known at commit time and is stamped onto the Finish record alone. The column comment says "GC round number (0 on Start)" — it does not say Phase rows are also 0, and the `phase` column comment at `:60` actively invites per-phase analysis. The `round_id` correlator is the workable join key, but nothing in the shipped column text tells the operator that `round` is unusable for phase rows.
- **Evidence**: the phase emitter never assigns `row.round` before appending.

### tier3-15 -- `previewDeletes` mixes physical and logical sizes and counts entries it will not delete (Low)

- **Anchor**: `Gc/CasGc.cpp:3043-3070` (`previewDeletes`), against `retiredLogicalSize` at `:268` used by the real retire path (`:1336`, `:1346`); consumed by `programs/disks/CommandCaGcDryRun.cpp`.
- **Trigger**: `cas-gc-dry-run` on any pool whose blobs carry a header (`blob_header_len > 0`).
- **Consequence**: the dry run reports raw object sizes while the round report and the retire accounting report header-adjusted logical sizes, so the previewed "bytes to be reclaimed" does not match what the subsequent round reports reclaiming. Zero-in-degree candidates are additionally emitted with an empty `token` and `condemn_round = 0`, so preview rows for the largest class of candidate carry no incarnation and a sentinel round — the two fields an operator would use to correlate a preview row against the eventual delete.
- **Evidence**: the preview builds sizes directly from the head/list result; `retiredLogicalSize` exists precisely to normalise that and is not called here.

### tier3-16 -- Phase metrics report constants and pre-budget counts (Low)

- **Anchor**: `Gc/CasGc.cpp:534` (`t.metric("fold_seal_reads", 2)`), `:853` (`t.metric("generations_reclaimed", handed_off.size())`).
- **Trigger**: any deferred round (534) or any budget-limited hand-off (853).
- **Consequence**: `fold_seal_reads` is a hardcoded literal, so it reports 2 even on the generation-0 path where no parent seal exists to read; `generations_reclaimed` counts generations inserted into the candidate set before the budget check at `:841-843` decides not to reclaim them, so it over-reports on exactly the rounds where tier3-1's leak occurs. `phase_metrics` is documented at `ContentAddressedGarbageCollectionLog.cpp:63-64` as "Phase-specific semantic counts a phase computes for itself", i.e. as ground truth no ProfileEvent can supply.
- **Evidence**: `handed_off.insert(...)` at `:839` precedes `handoffPrefixWholesaleRemaining()` at `:841`; the `break` leaves the inserted element in the set.

### tier3-17 -- `cas-inspect` renders sentinel values literally (Low)

- **Anchor**: `Tools/CasInspect.cpp:358` (`oldest_nonpending_condemn_round` rendered with `jsonUInt`).
- **Trigger**: inspect a fold seal for a shard with no non-pending condemned entries.
- **Consequence**: the field's "none" sentinel is `UINT64_MAX`, so the JSON reads `18446744073709551615`. Any tooling that treats the field numerically — a "how old is the oldest condemned entry" panel is the obvious one — computes an absurd age instead of recognising the empty case.
- **Evidence**: the same sentinel is compared against `UINT64_MAX` in `graduationDue` (`CasGc.cpp:2549-2557`), so its sentinel nature is established in code; the renderer has no branch for it.

### tier3-18 -- Counters computed and then discarded (Low)

- **Anchor**: `Tools/CasFsck.cpp:824-829` (`meta_without_body`, `body_without_meta`) versus `formatFsckSummary` at `:922-948`; `Tools/CasDecommission.h` `edge_deltas_emitted` versus the report rendered by `programs/disks/CommandCaDropMember.cpp`.
- **Trigger**: any fsck run; any decommission run.
- **Consequence**: fsck walks both key spaces to compute meta/body pairing and then prints neither counter — and per the sibling finding `clean()` ignores them too, so the check has no consumer whatsoever and a pool with orphaned metas is reported clean. `edge_deltas_emitted` is the one number that says how much work a decommission actually did, and it never reaches the operator.
- **Evidence**: `formatFsckSummary` enumerates 19 counters explicitly and both pairing counters are absent from the list; no other reader of those fields exists in the tree.

### tier3-19 -- `manifestCleanupShard` hashes with `std::hash` (Low)

- **Anchor**: `Gc/CasGcShardPlan.cpp:17-21`.
- **Trigger**: none today — the function has no callers, and `blobShard` (the shard function that *is* used for durable placement) correctly uses a stable content hash.
- **Consequence**: latent. `std::hash` is not stable across libstdc++/libc++ or across builds; wiring this into any durable shard assignment would make a rebuilt binary disagree with on-disk placement. Flagged because it sits in the shard-planning file next to the stable one, presenting itself as an equivalent utility. `ShardReducer` in the same file is likewise unused.
- **Evidence**: `blobShard` derives its shard from the content hash bytes directly; `manifestCleanupShard` calls `std::hash<...>` on the id.

## Checked and sound

Read line by line and found correct, with the reasoning that made them sound:

- **`CasGc::runRegularRound` phase ordering** — the emitted phase sequence (lease, pre_fold_ref_drain, heartbeat_floor, defer_decision, parent_seal_read, fold_*, pending_deletes, meta_pool_wait, round_commit, handoff_reclaim, manifest_deletes, namespace_cleanup, ref_object_cleanup, orphan_sweep) matches execution order exactly, and every destructive phase is placed after `round_commit`'s `casPut` of `gc/state`, so a lost CAS at `:804-807` aborts before anything irreversible.
- **`round_commit` CAS discipline** — `state_token` is threaded from the lease read through the commit, and a non-`Committed` outcome throws rather than retrying in place; `state`/`state_token` are only overwritten after success (`:808-809`).
- **`report.pending_candidates` accumulation** (`:815-820`) — `condemned_total - summary.pending_total` cannot underflow because `CasFoldSealFormat` validates `pending_total <= condemned_total` at decode.
- **`suppress_destructive` fan-out** — every destructive consumer is gated (`:610`, `:791`, `:832`, `:863`, `:2102`, `:2292`, `:2460`); I checked each of the seven sites individually and only the hand-off (tier3-1) treats suppression as "drop" rather than "defer".
- **`GcRoundWorkBudget`** — prune and hand-off budgets are reserved in separate counters so a prune-heavy round cannot starve the hand-off, which is what the shipped setting description claims; the arithmetic in `prefixWholesaleRemaining`/`handoffPrefixWholesaleRemaining` is correct including the zero-means-unbounded convention.
- **`blobShard`** — stable, content-derived, and consistent between the fold planner and the readers.
- **`Gc::scheduleMetaJob`** — exceptions are caught per job, logged, and counted into `CASGCMetaWriteAnomaly`; a failed meta job cannot escape and abort the round mid-phase.
- **`chooseRecoveryGrounding`** — validates that the chosen checkpoint carries a `life_epoch` before the later unchecked dereference at `:1602`, so that dereference is safe on this path.
- **`classifyDeleteOutcome`** — the absent/replaced/deleted mapping is exhaustive and the 412 path is classified as `replaced`, not as an error.
- **`SourceEdgeRunWriter` ordering** — key emission order is guaranteed sorted by construction, so the reader's streaming checksum is well-defined.
- **`CasGcOutcomesFormat` round-trip** — encode/decode are symmetric field-for-field, caps checked on both sides.
- **`CasGcMaintenanceStateFormat`** — caps its janitor cursor at encode time (the guard `CasGcStateFormat` lacks, tier3-12).
- **`decodeFoldSeal(data, layout, gc_shards, ...)`** — the structural overload validates shard membership and run-key layout; GC always calls the validating overload.
- **`CasGcPhaseTimer`** — RAII duration capture is correct, `metric()` on a moved-from/reset timer is not reachable, and the `meta_pool_wait` row's deliberately empty `ProfileEvents` matches its shipped column comment.
- **`GcRoundLogRecord` → `appendToBlock`** — column order in `appendToBlock` matches `getColumnsDescription` index for index (checked all 28 columns), same for `ContentAddressedLogElement` (all 18).
- **`StorageSystemContentAddressedMounts::read`** — health columns are correctly NULL on rows describing *other* servers' mounts (`m.srid == local_srid` test at `:177`), and the lifecycle columns are populated on every row including the fallback, so a not-live disk stays visible as the column comment promises.
- **`CommandCaGcRebuild` / `SYSTEM CAS GC REBUILD` argument handling** — the destructive path requires explicit invocation and does not default to running.
- **`blobStillReferenced`** — the re-check before declaring a blob dangling is correct and is what keeps fsck from crying wolf during a concurrent round.

## Coverage

Every file named in the tier3 brief was opened and read; the table above records the functions
actually walked rather than the files merely touched. `CasGc.cpp` was read in full at line
granularity for the round body, fold, prune/hand-off, rebuild, and preview regions; the remaining
helper bodies were read but produced no findings and are listed under "Checked and sound" where the
reasoning was non-trivial.

Not covered here, by design, and owned by sibling audits in this re-run: the GC *protocol* questions
(lease TTL, adopt-vs-condemn ordering, rebuild grounding, orphan-sweep guard conditions), the
crash-consistency and interleaving arguments, and the S3 backend contract. Findings above that touch
those areas cite them rather than re-deriving them.

Nineteen findings: zero High, nine Medium, ten Low. The Medium cluster is dominated by two themes —
GC accounting that is derived from budget-truncated or one-shot data structures (tier3-1, -2, -3), and
an admin surface whose checks silently do not run while its output still reads as clean (tier3-4, -5,
-6, -7). No memory-safety or data-loss defect was found in this region; the leaks are storage leaks
and the failures are failures of truthful reporting.

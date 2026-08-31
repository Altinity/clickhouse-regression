# gc-rebuild-feature -- fresh audit 2026-08-31

## Scope

- Files/dirs examined at `ceee42c51a06cb05e2c9a2d811ef7e1726825552`:
  `Gc/CasGc.cpp` (`rebuildBaseline` `:3715-4271`, `previewDeletes` `:4273-4348`,
  `acquireOrRenewLease` `:4373-4484`, `newestFoldSealRef` `:1330+`,
  `pruneSupersededGenerations` `:3451+`), `Gc/CasGc.h` (`RebuildReport`),
  `ContentAddressedMetadataStorage.cpp` (`runGcRebuildNow` `:667-701`, `gcStop` `:1042-1076`),
  `ContentAddressedMetadataStorage.h:204-207`, `InterpreterSystemQuery.cpp:2571-2607`
  and rebuild result columns `:2409-2446`, `programs/disks/CommandCaGcRebuild.cpp`,
  `programs/disks/CommandCaGcDryRun.cpp`, `Gc/CasGcScheduler.cpp` (background loop vs
  rebuild mutexes), `src/Disks/tests/gtest_cas_gc_rebuild.cpp` (what CI actually drives).
- Angles required by the brief: `SYSTEM CAS GC REBUILD` vs `clickhouse-disks cas-gc-rebuild`,
  mount interlock, condemn-universe reset, dry-run, reports, side effects of a refused rebuild.
- Explicitly out of scope: the normal round (`gc-protocol`); fsck as a product except where
  a rebuild comment names it as a backstop.

Static reasoning only. Line numbers are from this pin.

## Findings

### gc-rebuild-feature-1 -- production rebuild cannot acquire an existing `gc/state` lease (Medium)

- Anchor: `Gc/CasGc.cpp:3868-3879` (`acquireOrRenewLease(..., /*allow_steal=*/false)`);
  `ContentAddressedMetadataStorage.cpp:694-701` (fresh random `gc_id` per
  `runGcRebuildNow`); `programs/disks/CommandCaGcRebuild.cpp:60-65` (same mint);
  steal gate `Gc/CasGc.cpp:4442-4463`; `CasGcScheduler.cpp:86-91` (`stop` does not
  release the durable lease) at ceee42c
- Trigger: `SYSTEM CAS GC REBUILD [FORCE] <disk>` or `clickhouse-disks cas-gc-rebuild`
  on any pool that already has a `gc/state` object (the lost-run-artifact case
  `CASGCRebuild.RecoversLostGenerationArtifact` exists to cover, and the healthy
  `FORCE` case). The command returns `refusal = "another GC leader holds the lease"`.
  `SYSTEM CAS GC STOP` first does not help: the stopped scheduler's `gc_id` remains
  the lease owner.
- Evidence: `acquireOrRenewLease` renews only when `current.lease.owner == gc_id`
  (`:4411-4422`). A foreign owner with `allow_steal=false` always takes the back-off
  branch (`:4445-4463`), even on the first observation. Both production entry points
  construct a one-shot `Gc` with a new random id, so they never match the incumbent.
  The only production success path is an *absent* `gc/state` (the create-fresh branch
  at `:4381-4401`) — the vanished-state disaster. Gtests hide this: they call
  `rebuildBaseline` on the *same* `Gc` that just ran `runRegularRound` (same `gc_id`,
  so the renew branch fires; see `gtest_cas_gc_rebuild.cpp:174-195,210-220`). The
  header at `ContentAddressedMetadataStorage.h:204-206` documents the fresh identity
  as intentional. The shipped command text says rebuild is what you run after
  "the GC guard has refused every round" (`CommandCaGcRebuild.cpp:35-36`); that is
  exactly the state-exists-but-unhealthy case this gate now refuses.
- Notes: loud `BAD_ARGUMENTS`, no data loss. Workaround (delete `gc/state`, then
  rebuild) is the vanished-state path and is not named on either surface. Serious
  operability of the DR verb, not a silent corruption.

### gc-rebuild-feature-2 -- a vanished-state rebuild never pulses or renews; the live scheduler steals the lease it just created (Medium)

- Anchor: lease taken at `Gc/CasGc.cpp:3876` and consumed at `:4243`; no
  `pulseHeartbeat` / re-`acquireOrRenewLease` between. Steal at `:4426-4469`.
  Scheduler loop `Gc/CasGcScheduler.cpp:292-308` (`allow_steal` defaults true,
  `gc_round_mutex` only). Rebuild holds `ContentAddressedMetadataStorage`'s
  `gc_scheduler_mutex` (`ContentAddressedMetadataStorage.cpp:684`), a *different*
  mutex. CLI takes no storage lock at all.
- Trigger: `gc/state` is absent (finding 1's only success path) on a server whose
  background scheduler is still ticking. Rebuild creates a lease-bearing
  bootstrap body. Tick 1: scheduler sees a new owner, records the observation,
  backs off. Tick 2 (~`gc_interval_sec` later): `{owner, seq}` unchanged (rebuild
  never renews) and `gc/hb` unchanged (rebuild never pulses) → steal CAS commits.
  A regular round now runs against the in-flight rebuild.
- Evidence: consequences reachable from code. (a) Rebuild's terminal `casPut`
  fails (`:4244-4247`, `refusal = "gc/state changed under the rebuild (a competing
  writer) — re-run"`), discarding the scan; the next attempt hits the same wall
  unless the operator also stops GC. (b) `gcStop` takes `gc_scheduler_mutex`
  (`:1054`) and therefore blocks *behind* an in-flight SQL rebuild for the whole
  scan; it cannot be used as a mid-rebuild mitigation. (c) The CLI description
  says "never run against a disk a live server has mounted"
  (`CommandCaGcRebuild.cpp:37,54-58`) but the only gate is in-process
  `isReadOnly()`. It does not list mount slots or fence writers. A live RW
  server on the same prefix is invisible. Checkpoint-anchored recovery
  (`recoverRefTableDetailedFromAuthority` at `:4052-4053`) still prevents
  permanent edge loss from concurrent writers — this is a missing interlock and
  a steal/liveness defect, not a proven data-loss path.
- Notes: this is the surviving core of the 2026-08-12 High `gc-rebuild-feature-2`,
  narrowed to the vanished-state path. Filimonov's CAS-004 "SQL rebuild holds the
  GC lease" does not hold for a one-shot `Gc` on a live scheduler: it holds the
  lease only until the next steal window.

### gc-rebuild-feature-3 -- a refused or CAS-losing rebuild is not side-effect free; the residue is adoptable and sits above the prune floor (Medium)

- Anchor: `flush_shard` writes run objects mid-scan (`Gc/CasGc.cpp:3982-3998`,
  triggered at `:4007-4008`); seal `putDeterministicArtifact` at `:4232` *before*
  the `gc/state` CAS at `:4243`; missing-manifest refusal at `:4073-4078`;
  `newestFoldSealRef` at `:1330+`; prune floor `adopted_generation - keep`
  (`:3484-3486`). Header claim `ContentAddressedMetadataStorage.h:206-207`:
  "A refused rebuild (`report.performed == false`) writes nothing".
- Trigger: FORCE or vanished-state rebuild on a pool large enough to flush at
  least one shard, then either a committed ref naming a missing manifest
  (`:4073`) or a stolen-lease CAS failure (finding 2).
- Evidence: `performed` stays false and `gc/state` is unchanged, but
  `gc/gen/<max_gen+1>/` already holds run objects and, on the CAS-loss path, a
  complete-looking fold seal. Wholesale prune only deletes generations `<=
  adopted - keep`, so an *unadopted* generation above the live pointer is never
  a prune candidate. `newestFoldSealRef` is exactly the adoption source used
  when `gc/state` names no baseline (`:3823-3856`): a later vanished-state
  rebuild can carry holds from a *failed* rebuild's seal. The header's "writes
  nothing" claim is false for every refusal after the first `flush_shard`.
  Attempt numbering is a per-shard flush counter starting at 1 (`:3987`), not
  `lease.seq`; a second failed rebuild at the same `generation` / `attempt` 1
  hits `putDeterministicArtifact`'s divergent-bytes `CORRUPTED_DATA` if the
  bytes differ.
- Notes: nothing here deletes or condemns blobs (`:3988-3991`, `:4170-4187`).
  Fail-closed on collision is the right direction; the defect is that a refused
  rebuild manufactures the objects.

### gc-rebuild-feature-4 -- `cas-gc-dryrun` is not a preview of the next round and is silently empty when `gc/state` is missing (Low)

- Anchor: `Gc/CasGc.cpp:4273-4348`; empty return at `:4278-4279`; shipped
  description `programs/disks/CommandCaGcDryRun.cpp:23`.
- Trigger: run `cas-gc-dryrun` on a pool with no `gc/state` — the disaster
  `cas-gc-rebuild`'s own description names. Output is `preview_deletes=0`,
  indistinguishable from "the next round will delete nothing".
- Evidence: `previewDeletes` reads only the *adopted* seal's runs. It does not
  fold, so it cannot show new condemns or new spares; it applies none of
  `suppress_destructive`, graduation timing, or per-round budgets; it covers
  only blobs (no manifests, ref objects, generation prefixes, or janitor
  deletes). `reader.verifyAgainst` (`:4344`) throws while building the vector,
  so one bad run yields no rows. The "read-only, no deletes" half of the
  description holds.
- Notes: same residual as CAS-095. Diagnostic tool only.

### gc-rebuild-feature-5 -- CLI rebuild report omits the two hold-history fields; SQL surfaces no row on refusal (Low)

- Anchor: `RebuildReport` `Gc/CasGc.h:94-118` (`virgin_by_enumeration`,
  `adopted_seal_generation`); CLI print `CommandCaGcRebuild.cpp:67-75`; SQL
  columns `InterpreterSystemQuery.cpp:2409-2428` vs throw at `:2586-2587`.
- Trigger: a vanished-state rebuild that concluded the pool was virgin, or any
  refused rebuild on the SQL path.
- Evidence: SQL `LOG_INFO` and the result row include both new fields
  (`:2588-2594`, `:2426-2428`). The CLI prints `performed`…`clamped_shards`
  and not those two, even though `virgin_by_enumeration` is the one field the
  struct comment says the operator must see during a disaster (`CasGc.h:108-111`).
  On SQL, a refusal throws `BAD_ARGUMENTS` before `appendContentAddressedGcRebuildRow`,
  so the operator gets no counters; the CLI at least prints them first.
- Notes: `clamped_shards` is still incremented once per held precommit
  (`CasGc.cpp:4110`), not per shard.

## By-design / info / non-actionable

- **Condemn-universe reset is deliberate.** Rebuild writes `CondemnedSummary{}`
  for every shard (`CasGc.cpp:4223-4224`) and calls `foldDeltasIntoGeneration`
  with empty `head_blob` / `current_round == 0` (`:3988-3991`). A blob whose
  last owner was already gone before the rebuild is retained (named R4 residual,
  `:4182-4187`; pinned by `CASGCRebuild.RecoversLostStateAndConverges`).
  Filimonov CAS-025: by design, retention not loss.
- **Opposed read-only postures are documented design.** SQL
  `checkNotReadOnly("GC rebuild")` (`ContentAddressedMetadataStorage.cpp:669`);
  CLI requires `isReadOnly()` (`CommandCaGcRebuild.cpp:54-58`). Filimonov
  CAS-004: not a defect. The remaining gap is finding 2's missing *mount*
  interlock on the vanished-state path, not the SQL/CLI flag split.
- **Checkpoint-anchored recovery still holds.** `recoverRefTableDetailedFromAuthority`
  walks only to `_ckpt.committed_through` and fails closed on an absent log or
  snapshot base. Cursor is taken from that same recovery (`:4058`). Concurrent
  writer edges land above the cursor. Re-folding a `+1` is idempotent.
- **Missing/undecodable prior seal is a hard refuse** (`:3775-3795`,
  `:3838-3853`), including under `FORCE`. `newestFoldSealRef` refuses a seal
  above the listed maximum (listing-lied).
- **In-flight builds of a live mount are skipped** in the unowned-manifest pass
  via `prefixEligible` (`:4158-4159`).
- **Access control.** Each `SYSTEM CAS *` verb has its own `GLOBAL SYSTEM`
  privilege. `clickhouse-disks` is unauthenticated by construction.
- **Lock order** `lifecycle_mutex` before `gc_scheduler_mutex` is consistent.
  Finding 2's `gcStop` blocking is liveness, not deadlock.

## Closed-since-2026-08-12

- "SQL rebuild on a live disk is a High missing-interlock / data-loss substrate"
  (2026-08-12 `gc-rebuild-feature-1` as High): not re-raised at High. Rebuild
  condemns nothing; Filimonov CAS-004. The opposed `read_only` postures stay
  by design. What remains is finding 1 (lease unreachable) and finding 2
  (vanished-state steal / no mount census).
- "Scheduler steals a FORCE rebuild that holds the lease for an unbounded scan"
  as a general High: the FORCE / state-exists path no longer acquires a foreign
  lease at all (finding 1). The steal remains only on the vanished-state path
  (finding 2).
- Condemn-universe reset as data loss: still empty summaries; still CAS-025
  by design. Not a defect.

## Coverage

- Reviewed: both entry points and their `read_only` gates; `rebuildBaseline`
  health/lease/drain/walk/edge derivation/unowned-manifest pass/seal+CAS;
  `allow_steal=false` vs scheduler `allow_steal=true` and the two mutexes;
  condemn-universe reset; `previewDeletes` + CLI dry-run; `RebuildReport`
  fields vs CLI print vs SQL columns/throw; refusal and CAS-loss side
  effects vs `newestFoldSealRef` / prune floor; gtest `gc_id` reuse.
- N-A: privilege model beyond confirming `GLOBAL SYSTEM` verbs exist;
  `EmulatedSingleProcess` concurrency (out of contract).
- Deferred: runtime duration of the O(refs+manifests) scan; `cas-fsck` /
  `cas-inspect` as products; decommission interaction.

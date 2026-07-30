# tla-fidelity — re-run 2026-07-30

Re-verifies the six TLA-fidelity findings from `cas-tla-fidelity-audit.md` against the
current PR head (`altinity/cas-gc-rebuild` @ `cas-audit-20260730`). The TLA+ suite has
been substantially reworked since the original audit — several fidelity gaps flagged
then are now closed by newer model revisions (rev.6/rev.7/v9) and by matching code-side
hardenings (rev.7 [C2] fence-generation gate). Others remain.

## Scope in current code
- Files/dirs walked:
  - **TLA models** (`/Volumes/workspace/ClickHouse/docs/superpowers/models/`): 18+ specs.
    Read in detail: `CaCasMountCore.tla`, `CaErasureProof.tla`, `CaBuildRootPrecommit.tla`,
    `CaDiskLifecycle.tla`, `CaEdgeBeforeObserve.tla`, `CaB140DangleMerge.tla`,
    `CaGcAckFloorCore.tla`, `CaRefTableSnapshotLogCore.tla`.
  - **CAS code**:
    `Pool/CasServerRoot.{h,cpp}` (mount claim/epoch allocation),
    `Pool/CasMountRuntime.{h,cpp}` (fence, `mayMutate`, `fenceGeneration`, `checkFenceOrThrow`),
    `Pool/CasPool.{h,cpp}` (public forwarders),
    `Pool/CasPlainObjects.cpp` (`casPutObject`/`casRemoveObject` — fence-generation gate),
    `Pool/CasPartWriteTxn.cpp` (`streamIfAbsent` / `resurrectStaged` / `putOverwrite` displacement),
    `ContentAddressedTransaction.cpp` (`CaContentWriteBuffer` finalize path),
    `Backend/CasRequestControl.{h,cpp}` (per-attempt `fence_ok` callback).

## Methodology
Compared each of the six original fidelity findings against **both** (a) the current TLA
model text (which itself has evolved), and (b) the current code. Findings can move in two
directions: the model may be extended to cover a gap; the code may add a new guard that
neutralizes a hazard the model still doesn't formally check.

Verdicts use the repo vocabulary. A "🟡 partially closed" verdict marks a hazard whose
**worst-case** (data loss / silent corruption) has been eliminated but where a residual
liveness-only or availability-only degradation remains.

---

## Findings status

### CAS-002 — TLA-F1: shard `casPut` fenced by content token, not `writer_epoch` — ✅ **fixed at the model level, substantially closed at the code level**

**Original claim.** `CaCasMountCore.Write(a)` fused fence-check + mutation atomically
(`mount.epoch = localEpoch[a]` inside `Write`); the code did not — `mayMutate()` was
checked at flush-top, `casPut` was issued later on content-token only. Result: the
formal "SupersededWriterMakesNoMutation" guarantee did not transfer to the code.

**What changed in the model** (`CaCasMountCore.tla:838-848`):
```
Write(a) ==
    LET trulySuperseded == epoch > localEpoch[a]
    IN
    /\ ~rejected[a] /\ ~wedged[a]
    /\ ~crashed[a]
    /\ owner = a
    /\ clock < fenceUntil                              \* local monotonic fence ONLY
    /\ wrote' = wrote \union {<< a, localEpoch[a] >>}
    /\ rootEmpty' = FALSE
    /\ lostThenWrote' = (lostThenWrote \/ localLost[a])
    /\ supersededThenWrote' = (supersededThenWrote \/ trulySuperseded)
```
`Write` no longer contains `mount.epoch = localEpoch[a]` nor `~mount.fenced`. The
comment at `CaCasMountCore.tla:799-829` explicitly documents this as
*"matching the product's actual write path exactly — `Store::mayMutate` … reads NO shared
state at all: `!mount_fence.lost && bootMsNow() < deadline_boot_ms`, two LOCAL atomics"*.
The `SupersededWriterMakesNoMutation` invariant is now the **checked reachability**
argument (a bad state is unreachable), not a guard-mirror. Sabotage
`_sab_wallclockreclaim.cfg` deliberately reproduces the drift-through-reclaim window and
TLC flags `GlobalSupersededWriterMakesNoMutation`, proving the invariant is load-bearing
(it is not vacuously true).

**What changed in the code** (rev.7 [C2], `Pool/CasMountRuntime.{h,cpp}`,
`Pool/CasPlainObjects.cpp`, `Pool/CasPartWriteTxn.cpp`, `ContentAddressedTransaction.cpp`):
- A new `fence_generation` counter is bumped on every `armMountFence`/`tripMountLost`
  transition (`CasMountRuntime.cpp:87-142`).
- `checkFenceOrThrow(admitted_generation)` re-checks BOTH `mayMutate()` AND
  `fenceGeneration() == admitted_generation` (`CasMountRuntime.cpp:98-112`).
- The pattern is *capture-at-admission → re-check immediately before each durable PUT*:
  - `CasPlainObjects::casPutObject` — `casPut`/`putOverwrite` loop, re-check before
    each attempt (`CasPlainObjects.cpp:38-56`).
  - `CasPlainObjects::casRemoveObject` — same (`CasPlainObjects.cpp:75-88`).
  - `CasPartWriteTxn::uploadFromSource` displacement branches (`resurrectStaged`,
    `putOverwrite`) — `CasPartWriteTxn.cpp:683,705,747`.
  - Streaming staging finalize — `admitted_generation` captured in
    `ContentAddressedTransaction.cpp:887,901` and passed to `CaContentWriteBuffer` as
    a `finalize`-time fence check.
  - The request controller's `fence_ok` callback (`CasRequestControl.h:343-172`) is
    consulted before every attempt and every sleep, so a superseded writer with an
    already-in-flight retry loop stops emitting new attempts.

Together, model + code implement exactly the fix TLA-F1 recommended: split `Write` into
`admit (capture gen) → recheck (`checkFenceOrThrow`) → issue`, and the TLA suite has
added `CaErasureProof.tla` which models this three-phase writer explicitly, including a
"zombie" writer that lands its already-issued request AFTER the fence trip
(`CaErasureProof.tla:16-19,282-296,389-390`).

**Residual gap (why not fully green).** The model's `Write` is still a **single atomic
action** (guard + effect). What the model does NOT model is the specific `casPut`
attempt that is **already in flight over the network** when the fence trips — the code
has a residual "zombie land" window between the `checkFenceOrThrow` and the TCP RST /
success that neither `checkFenceOrThrow` nor `fence_ok` can revoke. `CaErasureProof`
explicitly models this as `ZombieLand(w)` (`CaErasureProof.tla:289,389-390`), and shows
that even under this residual window the `TruthEmpty` invariant holds because the
promotion path has separate qualification (`gcRound == 0`, guard counter == 0, grace).
So the code + model together carry the safety argument, but any code path that promotes
`Vanished(erased)` (Task-15 FORGET) or otherwise assumes "no writer can land after
this point" MUST use the erasure-proof qualification path — a bare `checkFenceOrThrow`
is insufficient to close a zombie window. No CAS code path violates this today.

**Anchors:**
- Model: `docs/superpowers/models/CaCasMountCore.tla:838-852`,
  `docs/superpowers/models/CaErasureProof.tla:12-30,124,209,256-305,401`.
- Code: `Pool/CasMountRuntime.cpp:81-142`, `Pool/CasPlainObjects.cpp:21-88`,
  `Pool/CasPartWriteTxn.cpp:683-748`,
  `ContentAddressedTransaction.cpp:884-902`.

**Verdict:** ✅ **fixed** (fidelity gap closed at the model level; matching code
implementation lands the fix TLA-F1 recommended). Note that this does **not** by itself
close CAS-002 as a whole — the audit-summary category is CORRECTNESS/SECURITY and the
code still has to be tested end-to-end against the exact pause/TOCTOU sequences. The
**fidelity** claim ("model can't find J1") is closed; the operational adequacy of the
in-flight-zombie window is the erasure-proof model's job and it does hold.

---

### CAS-001 — TLA-F2: reader unmodeled → R1 / X1 invisible — 🔴 **still present**

**Original claim.** No TLA model has a `Reader` actor with a
`resolveRef → readManifest → deferred blob GET` split, so the cross-protocol
reader-vs-GC-condemn-delete race is entirely outside the modeled state space.

**Re-check.** Searched every `.tla` file for a first-class SELECT-side reader:
`rg 'Reader|readPath|resolveRef|readManifest|NoReaderObservesDeleted'` returns only
`CaRefTableSnapshotLogCore.tla`, which models a **ref-log recovery reader**, not the
query-time SELECT reader that CAS-001 concerns (`ReaderInactive` in that file is a
mutual-exclusion state on ref-log recovery, not a deferred-blob-GET actor).

`CaErasureProof.tla` models writers (admit/recheck/land/zombie), a keeper, GC rounds,
an eraser, and an observer — but **no SELECT reader**. `CaB140DangleMerge.tla` models
dangles from the GC side only.

**Code side.** No reader-pin primitive was added. `rg 'reader.?pin|pinBlob|readerPin'`
across the CAS code returns zero matches. The `allow_stale` decode-TTL / GC-condemn
latency coupling that the read-protocol audit already flagged as CAS-085 is still the
only "convention" holding the reader safe, not a modeled invariant.

**Anchors:**
- Model: no reader actor anywhere in `docs/superpowers/models/**`.
- Code: no reader-pin — `ContentAddressedMetadataStorage.cpp` and the manifest-cache
  paths issue a deferred blob GET with no interlock against GC delete.

**Verdict:** 🔴 **still present**. Unchanged since the original audit.

---

### CAS-030 — TLA-F3: single global clock hides J3 (wall-vs-boot clock skew) — 🟡 **partially closed**

**Original claim.** `CaCasMountCore` had one `clock` variable advanced uniformly by
`Tick`; lease deadlines and expiry compared against that same clock. The code has two
clocks (wall for the lease deadline, boot for `mayMutate()`), so J3 (clock-skew reclaim)
was outside the modeled state space.

**What changed in the model.** `CaCasMountCore.tla` was reworked (`CaCasMountCore.tla:22,55,86-99`)
to introduce `Drift` as a first-class abstraction of wall-vs-boot skew, and:
- `SabWallClockReclaim` (`:127,235`) — deliberate sabotage that trusts the stamp
  (the pre-fix code behavior), reachable in `_sab_wallclockreclaim.cfg`;
- honest `GcFence` guard is `mount.deadline + Drift <= clock`
  (`CaCasMountCore.tla:99-100`), making `GcFence` and `Write` mutually exclusive on the
  same mount by construction for every `Drift`.

The `sab_wallclockreclaim` config is exactly the J3 test-coverage gap (T-G2 in the
audit-summary). TLC now reports `GlobalSupersededWriterMakesNoMutation` when this
sabotage is enabled — the model **can** rediscover J3.

**What changed in the code.**
- Local fence is boot-clock via `CLOCK_BOOTTIME` (`CasMountRuntime.cpp:61-71`).
- Wall-clock is **never trusted** on the reclaim path across nodes: the mount-claim
  reclaim logic (`CasServerRoot.cpp:379-422`) requires one of `gc_fenced` /
  clean-marker / `proven_dead_token` (a `mono_ms_fn`-observed token-stable window on
  the reclaimer's own monotonic clock) — a bare `expires_at_ms` comparison is
  explicitly rejected as unsafe (`CasServerRoot.cpp:414-418`).
- The mount-observation loop (`claimMountAwaitingExpiry`, `CasServerRoot.cpp:462-537`)
  bounds observation restarts (`kMaxObservationRestarts = 3`, `:454`) so a persistent
  live-twin is *reported* not *reclaimed*.
- The mount lease uses `now_ms` (wall) only for stamping the lease body, not for the
  fence itself (`CasMountRuntime.cpp` fence uses boot time).

**Residual gap (why 🟡 not ✅).** Two secondary sites still use bare wall-clock:
1. `computeHeartbeatFloor` (`CasServerRoot.cpp:539-…`) is drift-aware but its skew
   handling is not sabotage-covered in `CaCasMountCore.tla` (which models `GcFence`
   with `+ Drift`, but not `computeHeartbeatFloor` explicitly).
2. `allocateWriterEpoch` decommission-recovery branch does a bare
   `expires_at_ms > now_ms` comparison (`CasServerRoot.cpp:217`) — the code comment
   (`:206-227`) argues this is safe because the mint is DISTINCT from the survivor's
   epoch by construction, but this argument is a hand-carried informal proof, not a
   modeled invariant.

**Anchors:**
- Model: `docs/superpowers/models/CaCasMountCore.tla:22,55,86-99,127,235`.
- Code (honest boot-clock fence): `Pool/CasMountRuntime.cpp:61-85`,
  `Pool/CasServerRoot.cpp:379-422`, `Pool/CasServerRoot.cpp:462-537`.
- Code (residual bare wall-clock site): `Pool/CasServerRoot.cpp:217`.

**Verdict:** 🟡 **partially closed**. Model rediscovers J3 via
`SabWallClockReclaim`; honest code path never trusts wall-clock across clocks; two
audited secondary sites remain informal-argument-only.

---

### CAS-029 — TLA-F4: distinct-UUID assumption excludes J2 (VM clone) — 🔴 **still present in the model, blunted in code**

**Original claim.** `CaCasMountCore` declared "two server Actors (A,B), each a distinct
fixed ServerUUID." The mount safety argument leans on UUID uniqueness. J2 (a VM
clone/snapshot producing two live servers sharing one `server_uuid`) is outside the
state space by assumption.

**Re-check — model.** `CaCasMountCore.tla` still parameterizes actors as `Actors` and
the invariants are stated per-actor; no relaxation of the distinct-UUID premise has
been added. `rg 'shared.?uuid|sharedUuid|clone|snapshot|split.?brain'` on the models
returns no hits addressing J2. Unchanged since the original audit.

**Re-check — code.** The code has substantial defenses that blunt J2 to a bounded-
outage rather than a data-loss hazard:
- `allocateWriterEpoch` (`CasServerRoot.cpp:165-262`) is a CAS on the epoch object;
  two clones cannot both allocate the same `writer_epoch` — one wins the CAS, the
  other retries and gets `next+1`.
- `claimMount` (`CasServerRoot.cpp:320-422`) refuses to reclaim a same-uuid,
  different-epoch mount that is not `gc_fenced` / clean-marked / proven-dead
  (`CasServerRoot.cpp:391-422`): result is `LiveDoubleStart` — no write.
- The token-stability observation wait (`claimMountAwaitingExpiry`, `:462-537`) is
  bounded (`kMaxObservationRestarts = 3`, `:454`): a persistent live twin is
  **reported** to the operator (`mountDoubleStartMessage`, `:425-443`) rather than
  reclaimed.
- The self-remount recovery thread trips its own fence (`superseded_by_remount`,
  `Pool/CasRefLedger.cpp:335-1902`) so any concurrent stale-cache append fails
  closed.

So the code path for two clones sharing a `server_uuid` bounds the exposure to:
(a) the fresh clone's mount claim throws `LiveDoubleStart` at startup and the
    operator sees `mountDoubleStartMessage`;
(b) if the original is dead but its wall-clock expiry has passed, reclaim still
    requires either `gc_fenced` (a GC fence-out cert), a `clean_marker` (graceful
    farewell), or a monotonic-clock-observed proven-dead token — no bare wall-clock
    trust.

**Anchors:**
- Model: `docs/superpowers/models/CaCasMountCore.tla` (Actors as distinct ServerUUIDs — no shared-UUID relaxation).
- Code (defenses): `Pool/CasServerRoot.cpp:165-262,320-422,462-537`.
- Code (operator diagnostic): `Pool/CasServerRoot.cpp:425-443`.

**Verdict:** 🔴 **still present in the model** (the fidelity gap the audit named is
unresolved — no shared-UUID sabotage exists). CAS-029 as a WHOLE remains open in
audit-summary because the *deployment* premise is still operator-owned (nothing
prevents a VM clone at the infrastructure layer); the code defenses reduce the
exposure to an operator-observable outage rather than silent data loss.

---

### CAS-033 — TLA-F5: GC-reclamation liveness (G-N1) unmodeled — 🔴 **still present**

**Original claim.** `CaResurrectLiveness` checks *revival* liveness; there is no
liveness property asserting "a persistently clamped shard does not halt reclamation
pool-wide." G-N1 (a single anomalous shard tripping `suppress_destructive` and
stalling all graduations/deletes) is an operability/liveness concern the safety
specs do not flag.

**Re-check — model.**
- `CaGcAckFloorCore.tla:28,52-53,192-200` — models `clampedL` per-pass and a
  `SabotageClampNoSuppress` sabotage that proves the suppression rule is
  load-bearing FOR SAFETY (no over-count). But this is safety-only: the property
  `clampedL' = FALSE` (the "LIE: skipped, undeclared") is a sabotage of the safety
  clause, not of the liveness clause.
- No `CaResurrectLiveness`-style liveness witness exists for "some shard eventually
  graduates while another is persistently clamped." The pool-wide `SUPPRESS_DESTRUCTIVE`
  halts all reclamation and no model asserts this cannot happen.

**Re-check — code.** `suppress_destructive` is unchanged behaviorally (`Gc/CasGc.cpp`,
`Gc/CasGcShardPlan.{h,cpp}`, `Gc/CasBlobInDegree.{h,cpp}`); a clamped shard still
suppresses pool-wide destructive graduation.

**Anchors:**
- Model: `docs/superpowers/models/CaGcAckFloorCore.tla:28,52-53,192-200` (safety of
  clamp — modeled), no liveness-witness invariant.
- Code: `Gc/CasGc.cpp`, `Gc/CasGcShardPlan.{h,cpp}` — suppression rule unchanged.

**Verdict:** 🔴 **still present**. Unchanged since the original audit.

---

### CAS-205 — "verified core" (TLA+ suite with sabotage validation) — ⚪ **info, still verified-safe (and stronger than at audit time)**

**Original claim.** The TLA+ suite covers the entire write/GC/mount/incarnation
safety core with sabotage validation and liveness witnesses; this is why that core is
airtight in every prior audit.

**Re-check.** The suite has GROWN materially since the original audit:
- `CaErasureProof.tla` (new) — models the FORGET-verb erasure-proof observer
  including the *split-write / recheck / zombie-land* three-phase writer (the exact
  fix TLA-F1 recommended). Its `TruthEmpty` crown property is checked.
- `CaDiskLifecycle.tla` (new / substantial) — models `FORGET` and the
  Live/TransientNotLive/IdentityLost/Vanished state machine, with
  `ForgetTerminal` / `EarnedFarewell` / `OneWay` invariants + `_sab_nogcselfexit`,
  `_sab_notrip2`, `_sab_unearnedfarewell` sabotages.
- `CaCasMountCore.tla` (rev.6/rev.7/v9) — extensive rework matching the honest code
  fence shape, drift-aware `GcFence`, `SabWallClockReclaim` (models J3),
  `SupersededWriterMakesNoMutation`/`GlobalSupersededWriterMakesNoMutation` as
  checked invariants.
- `CaBuildRootPrecommit.tla`, `CaB140DangleMerge.tla`, `CaEdgeBeforeObserve.tla`,
  `CaGcRootLocalPartManifestCore.tla`, `CaRelinkConfirmCore.tla`,
  `CaGcCondemnMarkerGate.tla`, `CaGcRoundDeferCore.tla` — cover the B140-dangle
  fix, the edge-before-observe order (`precommit → adopt → promote`),
  root-local part manifest, relink confirm, condemn-marker gate, GC round-defer
  — collectively far broader than the "18 specs" quoted in the original audit
  (there are now 30+ `.tla` files under `docs/superpowers/models/`, each with a
  dedicated sabotage suite and often a witness/reachability config).

**Anchors:** every `.tla` under `docs/superpowers/models/` — the model action set
is not merely maintained but genuinely tracks new code actions (FORGET, erasure
proof, relink confirm).

**Verdict:** ⚪ **verified-safe** — stronger coverage than at audit time.

---

## Findings fixed / no longer reproducible
- **CAS-002 (TLA-F1)** — modeled honestly now; sabotage `sab_wallclockreclaim`
  reproduces the J1-adjacent drift; code adds rev.7 [C2] fence-generation gate on
  every durable PUT. See CAS-002 section above for anchors.
  ✅ **fixed** at the fidelity level (audit-summary CAS-002 severity should be
  re-evaluated by the write-protocol / jepsen auditors — this is only the
  fidelity claim).

## Findings still present
- **CAS-001 (TLA-F2)** — no reader actor in any model, no reader-pin in code.
- **CAS-029 (TLA-F4)** — shared-UUID sabotage not in the model.
- **CAS-033 (TLA-F5)** — no pool-wide reclamation-liveness witness.

## Partially closed
- **CAS-030 (TLA-F3)** — model rediscovers J3 via `SabWallClockReclaim`; honest code
  never trusts wall-clock across nodes; two secondary sites (`computeHeartbeatFloor`,
  `allocateWriterEpoch` decommission-recovery `expires_at_ms > now_ms`) remain
  informal-argument-only.

## New findings (not in original audit)

### NEW-tla-fidelity-1: `allocateWriterEpoch` decommission-recovery branch does a bare wall-clock liveness read — MEDIUM

- **Anchor:** `Pool/CasServerRoot.cpp:217`
  (`const bool live = !surviving.gc_fenced && surviving.expires_at_ms > now_ms;`).
- **Trigger:** `SYSTEM CONTENT ADDRESSED DECOMMISSION` on a server-root whose durable
  `epoch` object was lost but whose `/mount` object still exists. The recovery path
  compares the surviving mount's `expires_at_ms` against the caller's clock
  (`now_ms`, wall-clock) to decide whether the mount is "live" — the exact bare
  wall-clock comparison CAS-030 / TLA-F3 identified elsewhere.
- **Safety argument (in code comment `:206-227`):** the mint is DISTINCT from the
  survivor's epoch by construction, and `claimMount` right after applies its own
  STRONG liveness gate. So a mis-read here can only burn one epoch number on a
  doomed decommission attempt.
- **Fidelity gap:** the informal safety argument is not a modeled invariant. No
  `.tla` file models the decommission recovery epoch-mint path. If a future refactor
  moves this away from "mint distinct by construction" (e.g., attempting to re-use
  epoch 1), the safety argument silently breaks with no TLC alarm.
- **Recommendation:** add a `CaDecommissionRecovery.tla` (or extend
  `CaCasMountCore.tla`) with a sabotage `SabRecoverySameEpoch` proving the "mint
  distinct" clause is load-bearing.

### NEW-tla-fidelity-2: `resurrectStaged` displacement of condemned incarnation has no dedicated action in any TLA model — LOW-MEDIUM

- **Anchor:** `Pool/CasPartWriteTxn.cpp:686-711` (`resurrectStaged` branch) and
  `:713-748` (local `putOverwrite` displacement branch).
- **Trigger:** a writer observes its blob incarnation is Condemned (in the retired-
  ledger); it must displace the condemned incarnation with a freshly-tagged
  envelope. The correctness relies on: (a) INV-NO-RETURN via a fresh
  `incarnation_tag`, (b) the rev.7 [C2] fence-generation re-check immediately before
  the raw backend call.
- **Fidelity gap:** `CaEdgeBeforeObserve.tla` models displacement abstractly and
  `CaIncarnationCore.tla` models the dead-token-never-returns invariant; both
  invariants are checked and load-bearing. However, no model has an explicit
  `ResurrectStaged` action that composes (i) the fresh-tag mint, (ii) the fence-
  generation re-check, (iii) the exact-token delete of the condemned incarnation
  potentially still in flight from an earlier round. If a future refactor omits (i)
  or reverses the order of (ii) and (iii), no dedicated sabotage covers it. The
  code comments (`CasPartWriteTxn.cpp:686-711`) carry the full argument informally.
- **Recommendation:** add a `CaResurrectDisplacement.tla` (or extend
  `CaEdgeBeforeObserve.tla`) with explicit sabotage: `SabResurrectStaleTag`
  (verbatim server-side copy → same ETag → live delete), `SabDisplaceWithoutFenceGen`
  (raw backend call without `checkFenceOrThrow`).

### NEW-tla-fidelity-3: two secondary bare-wall-clock sites in `computeHeartbeatFloor` are drift-aware in code but not `_sab`-covered in `CaCasMountCore.tla` — LOW

- **Anchor:** `Pool/CasServerRoot.cpp:539-…` (`computeHeartbeatFloor`,
  reads `expires_at_ms` against `now_ms` with `skew_margin_ms`, `:697`).
- **Trigger:** the GC leader computes the mount heartbeat floor across all
  server-roots to know which epochs are still live for ack-floor purposes.
- **Fidelity gap:** `CaCasMountCore.tla` models `GcFence` with `+ Drift` (rev.6
  round 9), but `computeHeartbeatFloor` — a distinct call site that reads
  `expires_at_ms` differently — is not called out in any sabotage config. The
  code uses `skew_margin_ms` as its own margin.
- **Note:** severity is LOW because a mis-read here only mis-computes the ack
  floor, which is a REACHABILITY / LIVENESS concern (bounded delay of some
  deletes), never a safety concern (over-count / dangle).

### NEW-tla-fidelity-4: `SYSTEM CONTENT ADDRESSED FORGET` action is now modeled but its **operator-visible pre-checks** are not — INFO

- **Anchor:** `Pool/CasPool.cpp` `forgetDisk` orchestration path,
  `ContentAddressedMetadataStorage.cpp` `forgetDisk`, and
  `docs/superpowers/models/CaDiskLifecycle.tla`.
- **Trigger:** none — the model faithfully covers the mechanism (`ForgetTerminal`,
  `EarnedFarewell`, `OneWay`, trip#1/trip#2, keeperReset, etc.). But
  `CaDiskLifecycle.tla` starts from "the FORGET verb has been dispatched"; it does
  not model the SQL-layer pre-check that gates the verb.
- **Note:** this is an INFO item rather than a defect — the mechanism is sound;
  it just means "the model can't tell you if the operator invoked FORGET at the
  wrong lifecycle state." That is arguably out of scope for a protocol model.

---

## By-design / N/A / info
- **TLA-F6 (C++ concurrency out of scope)** — unchanged. `Threads`, `unique_ptr`
  lifetimes, destructor ordering, and atomic memory orderings are inherently
  outside protocol-level models. Findings CAS-023 / CAS-090 / CAS-091 / CAS-092
  are C++-safety concerns; no TLA suite can catch them. Correct scoping, not a
  defect.
- **W1 (CAS-020 promote-overwrite leak)** — unchanged. `INV_OVER_COUNT_ONLY` /
  `INV_NO_DANGLE` explicitly permit an over-count (leak); the model faithfully
  allows it, correctly not a violation. Handled at audit-summary as CAS-020
  (LEAK class, medium severity).

## Model-vs-code action-set delta (new to this re-run)

A brief audit of whether every code action in the CAS write / GC / mount / FORGET /
GC-rebuild pipeline has a corresponding TLA action or is composed of modeled
primitives:

| Code action | TLA coverage |
|---|---|
| `mount claim` (fresh / reclaim / live-double-start) | `CaCasMountCore` — full |
| `writer_epoch allocation` (normal) | `CaCasMountCore` — full |
| `writer_epoch allocation` (decommission-recovery bare wall-clock) | ❌ **not modeled** (see NEW-tla-fidelity-1) |
| `flushShardQueue` / durable PUT with fence-generation gate | `CaCasMountCore` (write) + `CaErasureProof` (three-phase writer) |
| `resurrectStaged` / condemned displacement | 🟡 covered as invariants in `CaEdgeBeforeObserve`+`CaIncarnationCore`; no dedicated action (see NEW-tla-fidelity-2) |
| `precommit → adopt → promote` order | `CaBuildRootPrecommit` + `CaEdgeBeforeObserve` — full |
| `GC fold → settle → condemn → graduate → delete` | `CaGcAckFloorCore` + `CaGcRoundDeferCore` + `CaGcRootLocalPartManifestCore` — full |
| `GC fence-out` (`GcFence`) | `CaCasMountCore` — full, drift-aware |
| `computeHeartbeatFloor` | 🟡 no dedicated action; drift only via `GcFence` (see NEW-tla-fidelity-3) |
| `SYSTEM CONTENT ADDRESSED FORGET` | `CaDiskLifecycle` — full |
| `SYSTEM CONTENT ADDRESSED GC REBUILD` | ❌ not directly modeled (rebuild is discussed in `CaGcAckFloorCore` sabotage `_sab_rebuild*` but not as a top-level action). See gc-rebuild-feature audit for CAS-015 / CAS-050. |
| `SELECT reader: resolveRef → readManifest → deferred blob GET` | ❌ **not modeled** (TLA-F2 / CAS-001) |
| `relink confirm` | `CaRelinkConfirmCore` — full (new since original audit) |
| `ref-log recovery` | `CaRefTableSnapshotLogCore` + `CaRefCatalogCore` + `CaRefDeltaIntakeCore` + `CaRefWriterCleanupCore` + `CaRefNsCleanupStaleLeaderCore` + `CaRefFoldClampRecoveryCore` — full (new since original audit) |

**Bottom line on action-set:** the model action set has *grown to track new code
actions* (FORGET, relink-confirm, ref-log recovery, erasure-proof). The remaining
code-not-in-model actions are: (i) the SELECT reader (CAS-001), (ii) `GC REBUILD` as
a top-level action (fidelity gap of CAS-015 / CAS-050 handled by their own audits),
(iii) `allocateWriterEpoch` decommission-recovery branch (NEW-tla-fidelity-1),
(iv) `computeHeartbeatFloor` bare-wall-clock read (NEW-tla-fidelity-3),
(v) `resurrectStaged` displacement as a dedicated action (NEW-tla-fidelity-2).

## Verdict summary table

| CAS-id | Old severity | Old fidelity status | Status | Evidence anchor |
|---|---|---|---|---|
| CAS-002 | High (SEC/CORR) | TLA-F1: inside scope, hidden by abstraction | ✅ fidelity fixed | `CaCasMountCore.tla:838-852`, `CaErasureProof.tla:12-30,124,209,256-305`, `Pool/CasMountRuntime.cpp:81-142`, `Pool/CasPlainObjects.cpp:38-88`, `ContentAddressedTransaction.cpp:884-902` |
| CAS-001 | High (DATA-LOSS) | TLA-F2: outside scope, reader unmodeled | 🔴 still present | no reader in models; no reader-pin in code |
| CAS-030 | Med (CORR/SEC) | TLA-F3: single global clock | 🟡 partially closed | `CaCasMountCore.tla:22,55,86-99,127,235`; `Pool/CasMountRuntime.cpp:61-85`; residual: `Pool/CasServerRoot.cpp:217,539-…` |
| CAS-029 | Med (CORR) | TLA-F4: distinct-UUID assumption | 🔴 still present (in model); code-blunted | model still `Actors` = distinct UUIDs; code defenses `Pool/CasServerRoot.cpp:165-262,320-422,462-537` |
| CAS-033 | Med (LIVENESS) | TLA-F5: no reclamation-liveness | 🔴 still present | `CaGcAckFloorCore.tla` covers clamp-safety only, not pool-wide liveness |
| CAS-205 | Info (verified core) | verified-safe | ⚪ verified-safe (stronger) | 30+ specs under `docs/superpowers/models/` incl. new `CaErasureProof`, `CaDiskLifecycle`, `CaRelinkConfirmCore`, etc. |
| NEW-tla-fidelity-1 | Medium | — | 🔴 new | `Pool/CasServerRoot.cpp:217` |
| NEW-tla-fidelity-2 | Low-Med | — | 🔴 new | `Pool/CasPartWriteTxn.cpp:686-748` |
| NEW-tla-fidelity-3 | Low | — | 🔴 new | `Pool/CasServerRoot.cpp:539-…` |
| NEW-tla-fidelity-4 | Info | — | ⚪ info | `CaDiskLifecycle.tla` covers FORGET mechanism but not SQL pre-check |

## Counts

- Original fidelity findings re-checked: **6** (CAS-002 TLA-F1, CAS-001 TLA-F2,
  CAS-030 TLA-F3, CAS-029 TLA-F4, CAS-033 TLA-F5, CAS-205 verified-core).
- ✅ Fidelity-level fixed: **1** (CAS-002 TLA-F1).
- 🟡 Partially closed: **1** (CAS-030 TLA-F3).
- 🔴 Still present: **3** (CAS-001 TLA-F2, CAS-029 TLA-F4, CAS-033 TLA-F5).
- ⚪ Verified-safe / info: **1** (CAS-205; stronger than at audit time).
- NEW findings: **4** (NEW-tla-fidelity-1..4; two Medium, one Low, one Info).

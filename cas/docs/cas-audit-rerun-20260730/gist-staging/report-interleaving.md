# cas-interleaving-audit — re-run 2026-07-30

Re-run of the original `cas-interleaving-audit.md` cross-protocol
(writer ∥ reader ∥ GC ∥ mount) interleaving audit against the current PR
HEAD (branch `cas-audit-20260730`, tracking `altinity/cas-gc-rebuild`).

Method: static walk of each finding along the current code paths named
in the original. No runtime. Every "still present" claim is anchored at
a file+line in `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**`.

## Scope in current code
- `Pool/CasRefLedger.{h,cpp}` — new **snapshot+log ref protocol**
  (replaces the per-shard CAS-token ref shard; single-mount-authoritative).
- `Pool/CasRefProtocol.{h,cpp}` — legal ref-op shape classifier;
  Add/Remove/Promote transitions with owner-index (`owned_manifests`).
- `Pool/CasMountRuntime.{h,cpp}` — mount fence: `mayMutate()`,
  `refAppendFenceOk()`, `fence_generation`, `armMountFence(server_uuid,
  writer_epoch, deadline_boot_ms)`, `checkFenceOrThrow`.
- `Backend/CasRequestControl.{h,cpp}` — every controlled put/CAS polls
  `fence_ok()` before every attempt, before every re-issue, and before
  every pause.
- `Backend/CasProbe.{h,cpp}` — capability probe under
  `pool_prefix + "/_probe/" + u128ToHex(probe_uid)` (unique per `Store::open`).
- `Gc/CasGc.{cpp,h}` — `pulseHeartbeat`, `acquireOrRenewLease`,
  `rebuildBaseline`, `runRegularRound`, universe fold, pipeline-blindness
  full-traversal condemn.
- `Gc/CasGcScheduler.{cpp,h}` — heartbeat pulse loop.
- `Parts/PartFolderAccess.{h,cpp}` — reader `Freshness` + `resolve`
  path; `readManifestShared` call sites.
- `Pool/CasManifestReader.cpp` — manifest read (still HEAD-less GET-only,
  immutable content-addressed body).
- `ContentAddressedMetadataStorage.cpp` — `runGcRebuildNow` command
  gate: `checkNotReadOnly` + `gc_scheduler_mutex` + `checkOpAdmitted(Admin)`.

## Findings still present

### CAS-001 — Reader has no pin across the deferred, unpinned blob GET
- Anchor: `Parts/PartFolderAccess.cpp:270,295` (`store->readManifestShared`
  is invoked, the returned `PartManifest` is captured, but nothing
  pins the referenced blobs' liveness against a concurrent
  `dropRef` + GC condemn/delete cycle).
- Anchor (no reader-side edge in fold): `Gc/CasGc.cpp:367` (`R1:
  heartbeat classification`); no reader-side reachability edge is
  ever emitted into the GC universe.
- Anchor: `Backend/CasObjectStorageBackend.cpp` — a later blob GET
  hits the object storage directly with the `StoredObject`
  captured at plan time; no token / no owner check.
- Trigger: same as original interleaving §5 row 6 — deferred
  blob GET on a ref-less / cross-node reader, while writer drops
  the ref, GC folds `-1`, condemns, and `deleteExact`s under the
  live token → `NoSuchKey` at the deferred GET.
- Evidence quote (still applies): "the reader participates in
  none of these ⇒ **C6 × B5** is the lone three-way dangle-to-reader."
- Notes: No new reader pin has been added. The two-phase graduation
  and mount-fence-derived ack floor still only bound the *window*,
  they do not close it for a ref-less reader.

### CAS-002 — Shard/state CAS still fenced by content token, not by writer_epoch
- Anchor (fence check): `Pool/CasMountRuntime.cpp:81-85` (`mayMutate`
  = `!lost && bootMsNow() < deadline`) and `:114-126` (`refAppendFenceOk`
  adds `attempt_timeout_ms + lease_safety_margin_ms` budget check).
- Anchor (per-attempt polling): `Backend/CasRequestControl.cpp:225,302,
  350,361,383,421,448,464,487,515,530,546,568,596,611` — `fence_ok`
  polled before every attempt / re-issue / pause across
  `putIfAbsentControlled`, `conditionalCreateControlled`,
  `putOverwriteControlled`, `putIfAbsentControlledMutable`.
- Anchor (durable-effect callers): `Pool/CasMountRuntime.cpp:98-112`
  (`checkFenceOrThrow(admitted_generation)`) and `:141`
  (`fence_generation.fetch_add(1)` on trip / re-arm) — a caller
  admitted under generation *g* aborts if the fence has been
  tripped-and-re-armed to *g+1* underneath it.
- Anchor (still content-token, not epoch): `Gc/CasGc.cpp:3002`
  (`store.backend().casPut(key, encodeGcHeartbeat(hb), expected)`),
  `:3026,:3043,:3097` (state CAS uses `token`/`std::nullopt`, no
  writer_epoch precondition).
- Trigger: paused writer past deadline but before another mount
  detects the lease loss can, on wakeup, still hold a valid token;
  the boot-time deadline + margin check catches it at *next* attempt,
  but there is no in-object writer_epoch precondition.
- Notes: **Mitigation, not fix.** The hazard window is now bounded by
  `deadline_boot_ms − margin` and by the `fence_generation` re-arm
  check. A cross-mount takeover still has to serialize by wall clock
  vs. boot clock — CAS-030 (skew) still applies. Verdict: **partially
  mitigated; still present in the strong-sense CAS-002 form** ("CAS
  precondition itself is not `writer_epoch`").

### CAS-015 — GC REBUILD has no mount-lease interlock (partially fixed)
- Anchor (command gate): `ContentAddressedMetadataStorage.cpp:621-655`.
  New guards: `checkNotReadOnly(:623)`, `checkOpAdmitted(Admin)`
  (`:630,:642`), full-run under `gc_scheduler_mutex` (`:638`),
  `Gc::rebuildBaseline`'s own `acquireOrRenewLease(false)` (`Gc/CasGc.cpp:2564`).
- Anchor (rebuild's safety additions): `Gc/CasGc.cpp:2673-2687` —
  **refuse** if a committed ref names a missing manifest ("DATA LOSS
  the rebuild must not bless"); `:2708-2737` include every
  unowned-but-not-provably-dead manifest as +1 (over-protect);
  `:2739-2770` pipeline-blindness condemn of every physically-present
  blob with zero rebuilt edges — but graduation still waits for
  every mount to ack past the minted round.
- Anchor (still no cross-mount interlock): the `checkNotReadOnly`
  gate is process-local; a live writer on **another mount** whose
  build straddles the rebuild's LIST/HEAD scan can have its edges
  missed by the baseline; the pipeline-blindness condemn will then
  put those blobs under a Condemned marker.
- Trigger: writer W on mount M2 finishes a `putBlob` after the
  rebuild's `discoverUniverse` / owner-scan (`Gc/CasGc.cpp:2648-2705`)
  has already visited M2's namespace, but before the LIST/HEAD
  full-traversal (`:2756`) sees the physical blob. Blob is
  edge-bearing per W but has no edge in the rebuilt baseline →
  condemned at minted round; graduation is gated on the ack floor
  which W's next heartbeat must exceed to save the blob.
- Notes: **Meaningfully hardened**: (a) refusal on any missing
  committed body, (b) over-protect on unowned manifests, (c) the
  usual ack-floor + two-phase graduation still apply to the
  full-traversal condemns. A ref-less reader (CAS-001) remains
  vulnerable if the ack floor advances before its deferred GET.
  Verdict: **still-present as a class**; the residual data-loss
  hazard now requires (writer on another mount) AND (ack-floor
  advance while a ref-less reader holds a plan). Recommended
  operator guidance ("rebuild during quiesced pool") is still
  unenforced.

### CAS-020 — `promote`-overwrite leak (structurally fixed for the ref shape; leak class reduced)
- Anchor (structural gate): `Pool/CasRefProtocol.cpp:243-273` —
  `OwnerTransitionShape::Promote` requires **same** `ref_name` AND
  **same** `manifest_ref`, and **throws `CORRUPTED_DATA`** at
  `:262-265` if a *different* already-committed manifest exists
  under this `ref_name` (which the pre-PR unconditional
  `refs[R]=…` would have silently displaced).
- Anchor (owner-index invariant): `Pool/CasRefProtocol.cpp:201-203`
  (`manifestAlreadyOwned` check on Add) — a duplicate manifest
  owner claim under any ref name is rejected before promote can
  even stage the precommit.
- Anchor (replay is symmetric): `Pool/CasRefLedger.cpp:174-236`
  (`resolveRef` reads the single authoritative in-memory state
  recovered from snapshot+log; RENAME/lost-ACK replay goes through
  the same shape classifier).
- Verdict: **✅ fixed for the ref-plane path the original called out.**
  The RENAME / lost-ACK replay path that produced W1/X2 (unconditional
  `refs[R]=…` overwrite) is no longer expressible; a corrupted /
  duplicated log line fails **closed** (`CORRUPTED_DATA`) instead of
  silently leaking the prior manifest.
- Notes: A residual concern remains for **manifest bodies whose
  owner never got the promote transaction persisted** (crash between
  precommit and promote); those are precommit-owned and cleaned by
  the stale-precommit sweep (`Pool/CasRefLedger.cpp:191,283`), and
  by `sweepStalePrecommitsForRead`. Not a leak class; covered by
  CAS-021 (multi-part commit atomicity) instead.

### CAS-032 — Zombie GC leader `pulseHeartbeat` (partially fixed / re-classed)
- Anchor: `Gc/CasGc.cpp:2989-3003` — `pulseHeartbeat` still
  unconditionally CAS-puts `hb.owner = gc_id` with `expected =
  got->token`. Prior heartbeat data is clobbered by design.
- Anchor (steal safety): `Gc/CasGc.cpp:3054-3092`. The follower's
  `hb_alive` predicate at `:3067-3068` is:
  `has_observation && (hb.owner != last_seen_hb_owner || hb.hb_seq
  > last_seen_hb_seq)`. **Owner change re-arms** the window (`:3064`);
  a steal requires **both** the `(owner, seq)` lease tuple AND the
  `(hb.owner, hb.hb_seq)` pair to be **frozen across a full window**
  (`:3070-3092`). A zombie continuing to pulse under its own id
  keeps `hb_seq` moving, so it correctly reads as alive — but this
  is now the **intended safety property**, not the SCHED-1 hazard.
- Anchor (round-CAS is the real fence): `Gc/CasGc.cpp:2238-2239`
  (round CAS is "the GC leadership fence gating publication") —
  a deposed leader's round CAS ABORTs before it can publish.
- Verdict: **CAS-032 hazard as originally described (follower
  steals from live long-round leader) is not reachable**: `hb_seq`
  advance under the same owner is enough to prove liveness. The
  clobber of `hb.owner` is deliberate. **Downgraded**: still-present
  as a *liveness* observation (a zombie that pulses can indefinitely
  extend its liveness window against a non-observing steal-eligible
  contender), not a *correctness* one.

### CAS-078 — Concurrent probe of shared prefix (still low, unchanged)
- Anchor: `Pool/CasPool.cpp:416` — `runCapabilityProbe(*backend,
  config.pool_prefix + "/_probe/" + u128ToHex(probe_uid))`. A unique
  128-bit `probe_uid` is minted per `Store::open`, so two concurrent
  opens use disjoint `_probe/{uid}/…` key spaces.
- Anchor: `Backend/CasProbe.h:32,60` — probe is scoped strictly under
  the caller-supplied `probe_prefix`.
- Verdict: **still-present but structurally unreachable** on the sole
  in-tree caller (`Store::open`). Left as an anti-footgun rule for
  any future caller that reuses a probe prefix.

### CAS-079 — Non-atomic HEAD-then-GET on a mutable object
- Anchor: `Backend/CasBackend.h:210` — `get(key, range)` returns
  `GetResult{bytes, token}` **atomically**; the read-your-own-token
  pairing is preserved by construction.
- Anchor: `Gc/CasGc.cpp:2764-2769` — the rebuild's pipeline-blindness
  sweep does `backend.head(k.key)` and captures the returned
  `HeadResult.token` for use in the *later* `deleteExact` two passes
  later. This is a HEAD-then-later-CAS pairing on a **content-addressed
  (immutable) blob body**; the write-time uploader-side token is
  refreshed by two-phase graduation (`deleteExact(token)` is the
  XT mechanism), so recreation under a fresh token causes a token
  mismatch, not wrong bytes.
- Anchor: no other HEAD-then-GET pairing observed on the mutable
  plane (`gc/state`, `gc/hb`, ref-shard log/snapshot objects all
  read via `get()` which returns `(bytes, token)` in one call).
- Verdict: **still-present as a latent contract rule** (any future
  code that does `head` then a separate `get` on a mutable object
  can pair an old token with new bytes). Not reachable on any
  current code path.

### CAS-085 — `allow_stale` ↔ GC condemn→delete latency coupling
- Anchor: `Pool/CasRefLedger.cpp:174-181` — `resolveRef` **explicitly
  ignores `allow_stale`** now: "the recovered-and-cached
  `RefTableState` is always this process's authoritative view".
- Anchor (single-writer-mount model): `Pool/CasRefLedger.cpp:604,1673`
  — the ledger runs under `live_writer_epoch` on the SOLE writer
  mount for a namespace; there is no external CAS token to go stale
  against.
- Anchor (callers still pass allow_stale): `Parts/PartFolderAccess.cpp:318`
  (`freshness == Freshness::CachedForLoad` → `allow_stale=true`),
  `:607` (`allow_stale=true`). No behavioural effect in current code.
- Verdict: **✅ fixed** for the coupling as originally framed (200 ms
  TTL cache vs. condemn→delete latency): the TTL knob no longer
  selects a stale view. The parameter is kept for callsite ABI. The
  underlying "reader has no pin" is CAS-001, not CAS-085.
- Notes: Latent surface remains — a **remote / cross-mount** reader
  (if that model is ever revived) would reintroduce the coupling.

## Findings fixed / no longer reproducible
- **CAS-020** (promote-overwrite leak): closed by
  `Pool/CasRefProtocol.cpp:262-265` (throw on any silent displace)
  and `:201-203` (`manifestAlreadyOwned` uniqueness).
- **CAS-085** (allow_stale ↔ condemn latency): closed by
  `Pool/CasRefLedger.cpp:174-181` (parameter is now a no-op).
- **CAS-032** as a *correctness* finding: closed by
  `Gc/CasGc.cpp:3067-3068` (hb-owner-change re-arms) and by
  `:3070-3092` (steal requires both tuples frozen across a full
  window). Retained as a *liveness* concern.

## New findings (not in original audit)

### NEW-interleaving-1 — Rebuild pipeline-blindness condemn ∥ concurrent writer on another mount
- Severity: Med (data-loss hazard, gated by ack floor)
- Anchor: `Gc/CasGc.cpp:2756-2770` (`edge_bearing` sweep) and
  `ContentAddressedMetadataStorage.cpp:623` (`checkNotReadOnly` is
  process-local; no cross-mount rebuild interlock).
- Trigger: writer W on mount M2 finishes `putBlob(B)` between the
  rebuild's owner-scan of W's namespace and the LIST/HEAD sweep.
  W has not yet promoted its precommit; the rebuild sees blob B
  in the LIST but no owning edge in the rebuilt baseline → B is
  added to `zero_condemned` at minted round. Graduation of B is
  then gated on every live mount acking past this round
  (`Gc/CasGc.cpp:2743-2745`), which W's next heartbeat renewal
  should satisfy — **provided** W is still up and W's ack has NOT
  raced past the round after ack was already latched. If W
  crashes between the rebuild's edge scan and its own promote,
  the precommit body is orphan and B legitimately becomes
  reclaimable; but if W crash-restarts, its rebuild-vintage
  precommit is now condemned before it can commit.
- Recommendation: an explicit mount-lease interlock on
  `runGcRebuildNow` — either (a) refuse rebuild if any other mount
  holds a live writer lease for a namespace covered by the scan,
  or (b) fold the whole rebuild under a pool-wide
  `suppress_writes` flag that every mount consults via its own
  `refAppendFenceOk`. Composition with CAS-015 is intentional.

### NEW-interleaving-2 — Deferred blob GET ∥ rebuild pipeline-blindness condemn (reader×rebuild)
- Severity: Med (reader data-loss variant of CAS-001; distinct
  interleaving because the source is `rebuildBaseline`, not the
  regular round)
- Anchor: `Gc/CasGc.cpp:2739-2770` (rebuild's full-traversal condemn)
  ∥ `Parts/PartFolderAccess.cpp:270,295` (unpinned deferred GET).
- Trigger: reader R has resolved a ref, read the manifest, holds
  `StoredObject(B)`, and defers the blob GET. Meanwhile
  `SYSTEM CONTENT ADDRESSED GC REBUILD` runs; its owner-scan
  finds R's ref namespace has an unowned manifest which is
  provably build-dead (the writer's build watermark passed), so
  the manifest is *not* over-protected (`Gc/CasGc.cpp:2727` —
  `prefixEligible` returns true → skipped). B's only reference
  came from that dead manifest → B lands in `zero_condemned` at
  the minted round → graduation → `deleteExact(B)`. R's deferred
  GET returns `NoSuchKey`.
- Notes: This is the CAS-001 hazard triggered by REBUILD's
  full-traversal instead of by a regular condemn round. The
  fix surface is the same reader pin.

### NEW-interleaving-3 — Zombie leader's pulseHeartbeat unconditional clobber vs concurrent CAS on `gc/hb`
- Severity: Low (churn, no correctness impact)
- Anchor: `Gc/CasGc.cpp:2989-3003` — `pulseHeartbeat` is a
  single-shot `get`-then-`casPut`; two schedulers racing (a
  deposed leader and a live new leader both pulsing) will each
  see their own `casPut` fail one out of two rounds (token stale),
  and the loop makes no retry. The `hb_seq` therefore does not
  monotonically advance under a single owner during churn; the
  follower's `hb_alive` predicate depends on `hb_seq` advance
  under a *specific* remembered owner.
- Trigger: two overlapping GC schedulers (e.g. shortly after a
  planned handover / a mount restart), both alive, both pulsing
  every second. Neither sees a monotonic sequence; the follower's
  steal-eligible observation window resets any time
  `last_seen_hb_owner` changes.
- Notes: Safety-preserving (no false steal). Downside: the
  follower's steal decision is effectively suspended for the
  duration of the churn. If both leaders subsequently die, the
  next follower has to wait a full window from its first
  observation — a small liveness cliff. Ties into CAS-033
  (pool-wide clamp) family.

### NEW-interleaving-4 — Ref-log recovery restart during writer append ∥ concurrent reader resolve
- Severity: Low
- Anchor: `Pool/CasRefLedger.cpp:604` (`greatest_listed_id->
  writer_epoch < my_epoch`), `:685-723` (recovery restart on
  `fence_ok_fn()` false or `superseded_by_remount`), and `:1379-1892`
  (append path re-reads recovery seal on fence-generation mismatch).
- Trigger: a fence-generation bump between the writer's
  `stagingPutIfAbsent` and its `applyOp` self-observation triggers
  a full re-recovery; a concurrent reader's `resolveRef`
  (`Pool/CasRefLedger.cpp:174`) sees `sweepStalePrecommitsForRead`
  which is safe (docs at `:191` explicitly state it must not fail a
  read), so no error surfaces. The concern is that the reader's
  view is temporarily behind while recovery replays.
- Notes: The single-mount-authoritative model absorbs this;
  parked here as an observation for future multi-writer revival.

## By-design / N/A / info
- The three-way invariant matrix (§5 of the original) still holds
  for the write↔GC plane: `CG ∨ AF ∨ 2P ∨ XT` compose the same way
  because the underlying mechanisms (fence generation + boot-clock
  deadline + condemn-round ack floor + `deleteExact(token)` +
  fold-barrier clamp) are all present. The reader still registers
  no reachability edge.
- Ref shard state is now snapshot+log; the "shard_write_seq
  RYOW" mechanism is subsumed by the local ledger being
  authoritative under `live_writer_epoch` (`Pool/CasRefLedger.cpp:604,
  1673`). The mutable-file coupling matrix (§5 last row) is
  therefore trivially satisfied — no external cache to invalidate.

## Verdict summary table
| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-001 | High (DATA-LOSS) | 🔴 still-present | `Parts/PartFolderAccess.cpp:270,295`; `Gc/CasGc.cpp:367` |
| CAS-002 | High (SECURITY/CORRECTNESS) | 🟡 mitigated (deadline+generation), still-present in strong form | `Pool/CasMountRuntime.cpp:81-142`; `Backend/CasRequestControl.cpp:225-611`; `Gc/CasGc.cpp:3002,3026,3043` |
| CAS-015 | High (DATA-LOSS) | 🟡 hardened, residual hazard | `ContentAddressedMetadataStorage.cpp:621-655`; `Gc/CasGc.cpp:2488-2770` |
| CAS-020 | Med (LEAK) | ✅ fixed (ref-plane path) | `Pool/CasRefProtocol.cpp:201-203,262-265` |
| CAS-032 | Med (LIVENESS) | 🟡 correctness closed; downgraded to liveness | `Gc/CasGc.cpp:2989-3003,3067-3092,2238-2239` |
| CAS-078 | Low (CORRECTNESS) | 🔴 still-present (latent, unreachable via `Store::open`) | `Pool/CasPool.cpp:416`; `Backend/CasProbe.h` |
| CAS-079 | Low (CORRECTNESS) | 🔴 still-present (latent contract; no reachable pairing) | `Backend/CasBackend.h:210`; `Gc/CasGc.cpp:2764-2769` |
| CAS-085 | Med (CORRECTNESS) | ✅ fixed (single-mount authoritative) | `Pool/CasRefLedger.cpp:174-181` |
| NEW-interleaving-1 | Med (DATA-LOSS class) | 🆕 | `Gc/CasGc.cpp:2756-2770`; `ContentAddressedMetadataStorage.cpp:623` |
| NEW-interleaving-2 | Med (DATA-LOSS class) | 🆕 | `Gc/CasGc.cpp:2727,2739-2770`; `Parts/PartFolderAccess.cpp:270,295` |
| NEW-interleaving-3 | Low (LIVENESS) | 🆕 | `Gc/CasGc.cpp:2989-3003,3067-3068` |
| NEW-interleaving-4 | Low | 🆕 | `Pool/CasRefLedger.cpp:604,685-723,1379-1892` |

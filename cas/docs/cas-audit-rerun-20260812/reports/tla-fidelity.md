# tla-fidelity -- fresh audit 2026-08-12

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base
`842f2b37b8f`, working tree audited as-is (read-only). CAS root
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`. All anchors below are
`<path-relative-to-CAS-root>:<line>` unless a full `src/...` path is given.

Static reasoning only. No build, no execution, no test run.

## Scope (and why no TLA+ model exists on this tree)

`find . -name '*.tla'` outside `contrib/` returns nothing: there is no formal model on this tree, so the
classic "model vs. code" diff has no left-hand side. `docs/en/antalya/cas/**` (including
`architecture/correctness.md`) is deleted in the working tree, and per the code-only rule prose and
comments are not admissible as intent anyway. All CAS tests are deleted as well, so no executable
specification exists either.

The audit is therefore redefined as **specification recovery plus self-consistency checking**: derive the
state machine and the safety/liveness properties from the code (control flow, guards, and shipped
strings, which *are* admissible), then check the code against the specification it implies. The core
deliverable is bypass analysis: for every guard that establishes an invariant, enumerate the other code
paths that reach the same durable effect without passing that guard.

Shipped strings used as intent evidence (all are user-visible exception/log text): the
`EDGE-BEFORE-OBSERVE invariant` message at `Pool/CasPartWriteTxn.cpp:281`, `INV-1`
(`re-upload from source bytes`) at `Pool/CasPartWriteTxn.cpp:276`, `INV-3` at
`Pool/CasPartWriteTxn.cpp:341`, `unique-ref invariant` at `Pool/CasPartWriteTxn.cpp:703`,
`never a fail-closed delete` at `Gc/CasBlobInDegree.cpp:377`, `single-writer exclusivity is broken` at
`Pool/CasServerRoot.cpp:963`, and the `WPromote owner==bld` predicate name at
`Pool/CasPartWriteTxn.cpp:672`.

## State machines recovered from code

### Blob body (key `<pool>/blobs/<algo>/<digest>`)

The blob object itself carries no state field; blob state is the join of three durable facts: the body's
existence/token, the freshness meta (`blobs/.../*.meta`, `Formats/CasBlobMetaFormat.h`: `Clean` |
`Condemned`), and the sentinel row for the digest inside the GC generation's source-edge run
(`Gc/CasBlobInDegree.cpp`: `kZeroMarker` | `kCondemned{delete_pending, marker_confirmed, token,
condemn_round}`).

| From | To | Anchor | Guard |
| --- | --- | --- | --- |
| absent | uploaded (token T, meta `Clean`) | `Pool/CasPartWriteTxn.cpp:406` (`stagingConditionalCreate`) then `:427` (`writeFreshMetaClean`) | conditional create (`if-none-match`), fence-controlled |
| uploaded (foreign incarnation) | referenced (adopted, no bytes moved) | `Pool/CasPartWriteTxn.cpp:290`-`:304` (`observeAndAdmit`) | meta not `Condemned` (`:262`) **and** `precommit_state == Durable` (`:280`) |
| uploaded/condemned | uploaded' (fresh incarnation, new token) | `Pool/CasPartWriteTxn.cpp:463` / `:471` (`Backend::resurrect`) then `writeResurrectMetaClean` `:465`/`:474` | reached only when `lm->meta.state == Condemned` (`:446`) |
| referenced | condemned (sentinel row `kCondemned`, meta `Condemned`) | `Gc/CasGc.cpp:1307`-`:1337` (`head_blob` lambda) + `Gc/CasBlobInDegree.cpp:467` (row write) | in-degree reached 0 in this fold pass (`cur_edges == 0 && cur_touched`, `Gc/CasBlobInDegree.cpp:450`) |
| condemned | condemned' (token superseded after a resurrect) | `Gc/CasBlobInDegree.cpp:428`-`:445` + `Gc/CasGc.cpp:727` | `peek_head` token differs from the retired entry's token |
| condemned | `delete_pending` (graduated) | `Gc/CasBlobInDegree.cpp:394`-`:409` | `condemn_round < current_round` **and** (`marker_confirmed` or `confirm_condemned_marker(e)`) **and** `!suppress_destructive` **and** graduation budget |
| condemned / `delete_pending` | spared (back to referenced) | `Gc/CasBlobInDegree.cpp:372`-`:382` | in-degree > 0 at this pass |
| `delete_pending` | deleted | `Gc/CasGc.cpp:613` (`deleteExact(blobKey, entry.token)`) | in-degree still 0, `!suppress_destructive`, redelete budget, token-exact |
| deleted | meta absent | `Gc/CasGc.cpp:662` -> `deleteConfirmedMeta` (`Gc/CasGc.cpp:100`) | best-effort, exceptions swallowed (`Gc/CasGc.cpp:329`-`:335`) |

Transitions with no inverse: **deleted** is terminal (bytes are gone; the only recovery is a writer
re-upload from its own source, which is a fresh `absent -> uploaded` transition, hence the `INV-1`/`INV-3`
strings). **`delete_pending` -> condemned** does not exist: once graduated, the row keeps
`delete_pending = true` forever (`Gc/CasBlobInDegree.cpp:404`-`:408`); the only escape is `spared`, which
requires in-degree recovery.

Unguarded transition: `Pool/CasPartWriteTxn.cpp:478` (`adoptEvidence`) records `referenced` with no head,
no meta read, and no `precommit_state` check -- the only entry into the reference graph that skips both
guards of the `observeAndAdmit` edge.

### Ref (namespace-scoped name -> manifest binding)

Encoded as owner bindings in the ref log (`Formats/CasRefLogFormat.h`, `RefOpKind::OwnerTransition`,
`RefOwnerKind::{Precommit, Committed}`); the in-memory projection is `RefTableState`
(`Pool/CasRefProtocol.h:131`, fields `committed` and `precommits`).

| From | To | Anchor | Guard |
| --- | --- | --- | --- |
| absent | precommitted | `Pool/CasPartWriteTxn.cpp:611`-`:617` (`precommitAdd`, `RootMutationKind::Precommit`) | manifest was staged by this txn or already the committed manifest (`:595`-`:602`) |
| precommitted | committed | `Pool/CasPartWriteTxn.cpp:715`-`:719` (`promote`) | precommit binding still live (`:668`), body revalidated (`:643`-`:651`), every blob leaf tokened or trusted-adopt (`:675`-`:695`) |
| precommitted | absent (abandon) | `Pool/CasPartWriteTxn.cpp:810`-`:821` (`RootMutationKind::Abandon`) | none beyond the binding existing |
| precommitted | absent (GC/successor reclaim) | `Pool/CasRefLedger.cpp:3152`-`:3166` (`RootMutationKind::ReclaimPrecommit`) | `mref.writer_epoch < live_epoch` (`:3142`) -- writer-epoch fence |
| committed | repointed | `Pool/CasPartWriteTxn.cpp:708`-`:714` (old removal + new transition in one txn) | `allow_repoint` (`:700`); otherwise fails closed on the `unique-ref invariant` |
| committed | dropped | `Pool/CasRefLedger.cpp:3207`-`:3210` (`dropRef`) | ref exists (`:3201`) |

Transition with no inverse: **repoint**. The old and new bindings move in a single ref-log record, so
there is no durable record from which the previous target can be restored, and no "undo repoint" op
exists in `RootMutationKind`. This is the sibling audits' *unrevertible repoint*; it is an instance of
"every state-changing op is a log append" holding, while "every op has an inverse" does not.

### Ref lane (per-namespace append lane) -- `RefLaneState`, `Pool/CasRefLedger.h:29`

`Ready -> Writing -> {Ready | Wedged}`; `Wedged -> Ready` (Adopted, `Pool/CasRefLedger.cpp:1801`),
`Wedged -> Closed` (successor epoch seal rejects the attempt, `:1770`), `Wedged -> Faulted` (foreign
occupant at the slot, `:1776`), `Wedged -> NeedsRecovery` (`requireRecovery`, `:1749`/`:1781`/`:1712`),
`NeedsRecovery -> Ready` (`installRecoveryResult`, `:1108`). `Closed` and `Faulted` have **no in-process
inverse**: both are cleared only by installing a fresh `RefTableRuntime`, which happens on remount
(`acquireRefTableRuntime`, `:342`, plus `superseded_by_remount`).

### Mount lease (`gc/server-roots/<srid>/mount`) -- `Pool/CasServerRoot.cpp`

States: absent | held(uuid, epoch, seq, expires_at_ms) | `gc_fenced` | terminated
(`min_active == UINT64_MAX`, the "clean farewell").

* absent -> held: `claimMount` `:308`-`:313` (`putIfAbsent`).
* held -> held' (renew, seq+1): `SingleWriterSlot::renewOnce` `:1037`-`:1046`, token-exact `putOverwrite`.
* held -> `gc_fenced`: `computeHeartbeatFloor` `:524`-`:528`, guarded by token-stability over
  `mountObservationThresholdMs = ttl + ttl/20 + cadence` (`:393`) measured on the GC leader's own
  monotonic clock, plus up to `max_reclassify = 4` re-reads.
* held -> terminated: `MountLeaseKeeper::terminate` `:921`-`:934`, token-exact.
* `gc_fenced`/terminated/proven-dead -> held (reclaim by the same uuid, new epoch): `claimMount`
  `:343`-`:359`. `proven_dead` requires the observed token to be unchanged for the threshold
  (`claimMountAwaitingExpiry` `:417`-`:419`).
* foreign uuid -> refuse always (`:318`-`:322`, `:785`-`:791`): there is no cross-identity takeover edge.

The in-process shadow of this machine is `CasMountRuntime`: `mayMutate() = !lost && bootMsNow() <
deadline_boot_ms` (`Pool/CasMountRuntime.cpp:77`) with `CLOCK_BOOTTIME` (`:60`, so suspend counts
against the lease), `armMountFence` (`:118`) is the only clear of `lost`, and `tripMountLost` (`:83`)
bumps `fence_generation` so every write admitted under the old generation fails
`checkFenceOrThrow` (`:90`).

### Writer epoch -- `allocateWriterEpoch`, `Pool/CasServerRoot.cpp:161`

Monotone allocation by CAS on `epoch` (`:234`). If the epoch object is absent, minting epoch 1 is gated on
`serverRootSubtreeEmpty` (`:183`) **and** a conclusive mount-lease absence probe (`:189`-`:224`), with
`Indeterminate`/`AccessDenied` failing closed. The only path that re-mints under a surviving mount object
is `EpochMintPolicy::DecommissionRecovery`, which still refuses if the surviving lease is live (`:200`-`:206`)
and otherwise continues from `surviving.writer_epoch + 1` (`:207`). No decrement edge exists. Per-epoch
build sequences (`CasMountRuntime::allocateBuildSeq`, `:148`) plus `min_active` published in the lease body
(`:745`, `:760`) form the newborn-debris watermark.

### GC round -- `Gc::runRegularRound`, `Gc/CasGc.cpp:415`

`lease -> pre_fold_ref_drain -> heartbeat_floor -> defer_decision -> {deferred | fold} -> pending_deletes
-> round_commit -> handoff_reclaim -> manifest_deletes -> namespace_cleanup -> ref_object_cleanup ->
orphan_sweep`. Lease acquisition (`acquireOrRenewLease`, `:3105`) is **purely token/sequence-based with no
TTL and no wall clock**: a steal requires the incumbent's `lease.seq` to be unchanged between two of this
process's own observations *and* `gc/hb` to be unchanged (`:3158`-`:3164`). Generation state is
`GcState{round, snap_generation, snap_attempt, snap_pruned_through, manifest_sweep_cursor, gc_shards,
lease}` advanced by a single CAS at `:804`. Fold seals (`gc/gen/<g>/<a>/...`) are write-once
deterministic artifacts (`putDeterministicArtifact`, `Gc/CasBlobInDegree.cpp:300`).

### Namespace lifecycle -- `Pool/CasRefCatalog.cpp`

`absent -> Creating` (`createNamespaceStep1`, `:149`, with a `CreatorFence`) `-> Live` (`completeCreation`,
`:427`, after the birth ckpt is published) `-> Removing` (`beginRemoving`, `:227`, exact-entry CAS with
`removal_started_round`) `-> absent` (`deleteCompletedRemovingAtSnapshot`, `:299`). Side edges:
`Creating -> absent` (`cancelStalledCreating`, `:390`, requires a terminal creator fence) and
`Creating -> Creating'` (`reconcileStaleCreator`, `:507`). Ref writes are inadmissible while `Creating`
(`checkPublicationAdmittedOrThrow`, `:543`). The catalog row is created *before* any of the life's ref
objects, which is what makes the janitor's list-then-read-catalog order safe (see Bypass analysis).
`Removing -> Live` does not exist: removal is irreversible once the row transitions.

## Safety invariants and their enforcement points

* **S1 (blob deletion is triple-guarded).** A blob body is deleted only if (a) its in-degree in the
  adopted generation is 0, (b) its row carries `delete_pending`, which was set in a *strictly earlier*
  round and only after a condemn marker was confirmed durable, and (c) the delete is token-exact against
  the token observed when the blob was condemned. Enforcement: (a) `Gc/CasBlobInDegree.cpp:372`/`:383`,
  (b) `Gc/CasBlobInDegree.cpp:394`-`:409`, (c) `Gc/CasGc.cpp:613`.
* **S2 (destructive work is globally suppressed on incomplete evidence).** No graduation, redelete,
  manifest delete, orphan sweep, prefix reclaim, ref-object cleanup or janitor delete runs in a pass with
  any anomaly, any carried hold, or an unproven ref frontier. Enforcement:
  `Gc/CasGc.cpp:2063`-`:2065`, consumed at `:610`, `:832`, `:863`, `:2102`, `:2292`, `:560`.
* **S3 (adoption of an existing incarnation requires a non-condemned marker).** Enforcement:
  `Pool/CasPartWriteTxn.cpp:262`-`:278`.
* **S4 (edge before observe).** No existing incarnation is adopted before this build's precommit binding
  is durable. Enforcement: `Pool/CasPartWriteTxn.cpp:280`-`:285`.
* **S5 (unique ref).** A committed ref is never silently retargeted. Enforcement:
  `Pool/CasPartWriteTxn.cpp:697`-`:705`.
* **S6 (promote is owner-exact).** Enforcement: `Pool/CasPartWriteTxn.cpp:668`-`:673`.
* **S7 (single writer per server root).** All mount mutations are token-exact `putOverwrite` on the
  mount object and never cross `server_uuid`. Enforcement: `Pool/CasServerRoot.cpp:1038`, `:318`, `:785`,
  `:960`-`:975`.
* **S8 (durable mutations only under a live, margin-checked mount incarnation).** Enforcement:
  `Pool/CasMountRuntime.cpp:101` (`refAppendFenceOk`, margin = `attempt_timeout_ms +
  lease_safety_margin_ms`) threaded into every ref/staging write via `Backend/CasRequestControl.cpp:193`,
  `:261`, `:305`, `:326`.
* **S9 (only dead namespace lives lose their objects).** Enforcement:
  `Gc/CasNamespaceJanitor.cpp:77` (`catalog_cut.life_index.resolve`) plus the per-key GC fence check at
  `:98`, and `Gc/CasGc.cpp:2320`-`:2354` for ref-object trimming.
* **S10 (ref-log trimming never destroys the recovery triple).** Logs are deletable only at or below the
  folded durable cursor *and* strictly below the checkpoint snapshot id, the checkpoint snapshot itself
  is retained, and the predecessor epoch-seal log is pinned. Enforcement:
  `Pool/CasRefProtocol.cpp:612`-`:628`, callers at `Gc/CasGc.cpp:2377`-`:2395`.
* **S11 (content address).** The body stored at `blobs/<algo>/<digest>` hashes to `digest`.
  Enforcement: single-pass hashing while writing
  (`ContentAddressedTransaction.cpp:1236`/`:1259`, `finalizeImpl` at `:1276`-`:1292`).
* **S12 (no versioned bucket).** Enforcement: `Backend/CasProbe.cpp:175`-`:183` at mount, plus the
  in-round `LOGICAL_ERROR` at `Gc/CasGc.cpp:614`.

## Bypass analysis

| Invariant | Enforcing check | Bypassing path | Anchor |
| --- | --- | --- | --- |
| S1/S3 (condemn marker gates reuse) | `observeAndAdmit` meta read | `adoptEvidence` records a trusted-adopt dep with no head and no meta read; `promote` blesses it as `manifest-trust` | `Pool/CasPartWriteTxn.cpp:478`-`:486`; `:679`-`:695` (sibling finding, cited) |
| S1(b) (marker confirmed before graduation) | `e.marker_confirmed \|\| !confirm_condemned_marker \|\| confirm_condemned_marker(e)` | the middle disjunct makes the guard **vacuous when the callback is absent**; `rebuildBaseline` calls the same reducer with `{}` for `head_blob`, `peek_head` and `confirm_condemned_marker` | check `Gc/CasBlobInDegree.cpp:396`; caller `Gc/CasGc.cpp:2816`-`:2821` (F1) |
| S1(b) (marker is evidence about *this* incarnation) | `confirm_condemned_marker` reads only `meta.state == Condemned` | `BlobMeta` has no token/incarnation field, and `writeCondemnedMeta` early-returns success when the meta is already `Condemned` whatever its `condemn_round`/size | `Gc/CasGc.cpp:1356`; `Formats/CasBlobMetaFormat.h:14`-`:22`; `Gc/CasGc.cpp:95`-`:97` (F4) |
| S1/S2 (deletes run under a held GC lease) | round-commit CAS `Gc/CasGc.cpp:804`; per-delete revalidation exists only in ref cleanup (`:2338`-`:2354`) | the blob redelete batch, the manifest-delete loop and the orphan sweep never revalidate lease ownership per delete; the redelete batch runs *before* the round-commit CAS | `Gc/CasGc.cpp:611`-`:665`, `:865`-`:884`, `:906`-`:930` (F2) |
| S1 "GC eventually reclaims" / condemn bookkeeping | two-phase condemn rows carried in the generation runs | `rebuildBaseline` starts from empty `prior_runs`, so all condemned/`delete_pending` rows and every zero-marker row are dropped; no code path ever lists `blobs/` except fsck | `Gc/CasGc.cpp:2809`-`:2824`; only `blobsPrefix()` list is `Tools/CasFsck.cpp:581` (F3) |
| S4 (edge before observe) | `precommit_state != PrecommitState::Durable` throw | `adoptEvidence` has no such check; `recordPendingBlobDep` likewise | `Pool/CasPartWriteTxn.cpp:280` vs `:478`, `:488` (F8) |
| S5 (unique ref) | `allow_repoint` gate | `allow_repoint = true` callers get an unrevertible one-record retarget; no inverse op exists in `RootMutationKind` | `Pool/CasPartWriteTxn.cpp:700`-`:714`; `Pool/CasRefProtocol.h:59`-`:69` (sibling finding, cited) |
| S8 (margin-checked fence on every durable mutation) | `refAppendFenceOk` (margin-aware) for ref/staging writes | `CasPlainObjects` is wired to `checkFenceOrThrow` -> `mayMutate()`, which has **no** attempt-timeout/safety margin, and issues raw `putIfAbsent`/`putOverwrite`/`deleteExact` outside the request controller | `Pool/CasPool.cpp:141`-`:144` vs `:151`; `Pool/CasPlainObjects.cpp:27`-`:38`, `:57`-`:63` (F5) |
| S9/S10 (only dead lives lose objects) | list-before-catalog-read ordering plus `resolve` | not bypassable as written: `backend.list` at `Gc/CasNamespaceJanitor.cpp:25` precedes `CasRefCatalog::read` at `:35`, and a life's catalog row is always created before its objects (`createNamespaceStep1`). The safety of this depends on list-after-write, which is proven at mount by the probe | `Gc/CasNamespaceJanitor.cpp:25`/`:35`; `Backend/CasProbe.cpp:154`-`:168` (no finding; backend-conditional) |
| "a manifest body owned by a live binding is never deleted" | `cleanupStagedManifestDebrisBestEffort` skips `precommit_manifest` | the txn tracks only the **last** `precommitAdd` triple, so a second `precommitAdd` leaks the first binding and this cleanup deletes the body it still owns | `Pool/CasPartWriteTxn.cpp:866`-`:884` vs `:587`-`:590` (F6) |
| S11 (content address) | single-pass hash while writing | every re-upload path re-reads the source and validates **size only**: the attempt loop, the head-miss re-upload, `resurrect` (local and staged) and the server-side `promoteStaged` copy | `Pool/CasPartWriteTxn.cpp:398`-`:402`, `:435`, `:463`, `:471`; `Backend/CasObjectStorageBackend.cpp:827`, `:841`, `:789`-`:812` (F7) |
| S12 (no versioned bucket) | `created_delete_marker` reporting | the signal exists only in the S3 native path; any backend whose `removeObjectIfTokenMatches` does not report delete markers (or the emulated backend, which hardcodes `false`) passes both the probe and the in-round assertion on a versioned bucket, and the GCS versioning check degrades to a warning when the API call fails | `Backend/CasProbe.cpp:175`; `Gc/CasGc.cpp:614`; `Backend/CasObjectStorageBackend.cpp:59`-`:67`, `:763`-`:786` (F9) |

## Liveness properties and their violation conditions

* **L1 -- GC eventually reclaims an unreferenced blob.** Requires a pass with no anomalies, no holds and a
  complete frontier (`Gc/CasGc.cpp:2063`), then a *later* round to graduate and a third to delete. Violated
  forever when: any namespace carries a permanent hold (e.g. `HoldReason::ManifestBodyMissing` minted at
  `Gc/CasGc.cpp:2902`, which is re-adopted from the parent seal every pass at `:2913`-`:2921` and has no
  clearing edge in this file); or after `rebuildBaseline`, for every blob that is already unreferenced at
  rebuild time (F3), because discovery is edge-transition-only.
* **L2 -- a wedged ref lane eventually resolves.** `Wedged` self-resolves only if the same slot resolves
  durable or a conclusive rejection is observed (`Pool/CasRefLedger.cpp:1760`-`:1784`). Violated forever
  within the process when the occupant classifies as `Foreign` (`:1773`, lane `Faulted`, deliberately left
  wedged) or `SuccessorSeal` (`:1766`, lane `Closed`); recovery requires a remount, and a remount is only
  scheduled if `config.background_watermark` is set (`Pool/CasMountRuntime.cpp:344`) and the pool is not
  already in a terminal lifecycle (`:346`).
* **L3 -- a mount eventually becomes claimable.** Held-by-foreign-uuid never becomes claimable by design
  (`Pool/CasServerRoot.cpp:318`). Own-uuid slots become claimable via fence-out or token-stability, but the
  observation loop gives up after `kMaxObservationRestarts = 3` token changes (`:390`, `:429`, `:439`) and
  returns `LiveDoubleStart` -- the mount then fails with `mountDoubleStartMessage`. A holder that renews
  fast enough to change the token on every poll therefore blocks a legitimate successor forever (this is
  intended for a genuinely live peer, but it is also the failure mode for a wedged peer that keeps
  renewing while making no progress).
* **L4 -- GC leadership eventually transfers.** There is no lease TTL: a steal needs
  `lease.seq` *and* `gc/hb` unchanged across two observations by the *same* process
  (`Gc/CasGc.cpp:3158`-`:3164`, `has_observation` gate at `:3161`). A fresh process has
  `has_observation == false` and therefore can never steal on its first attempt; combined with
  `pulseHeartbeat` running unconditionally (`:3089`, no lease check), a partially-dead leader whose
  heartbeat thread survives blocks all reclamation indefinitely. This is the sibling *no GC lease TTL*
  finding; the heartbeat-without-lease-check amplification is noted here.
* **L5 -- ref logs and snapshots are eventually trimmed.** `cleanupRefObjects` compares the *whole
  catalog token* before each delete (`Gc/CasGc.cpp:2327`) and `return`s from the entire function on the
  first refusal (`:2401`, `:2410`) rather than continuing with the next namespace. Any concurrent catalog
  mutation (any CREATE/DROP of any table anywhere in the pool) aborts trimming for every namespace in
  that pass; a steady stream of DDL starves trimming forever (F10).
* **L6 -- a namespace in `Removing` eventually disappears.** Needs `cleanup_evidence` present and no hold
  in the authoritative parent seal (`Pool/CasRefCatalog.cpp:285`-`:292`). A held life is stuck; the code
  only reports it (`stuckRemovalWarning`, `Gc/CasGc.h:166`, `reportStuckRemovals`, `Gc/CasGc.cpp:512`).
* **L7 -- an in-epoch leaked precommit is eventually reclaimed.** The sweep only reclaims
  `writer_epoch < live_epoch` (`Pool/CasRefLedger.cpp:3142`). A precommit leaked inside the *current*
  epoch (e.g. the double-`precommitAdd` shape of F6, or a failed `enqueueWriterCleanupDuty`) pins its
  manifest and all its blobs until the next epoch, i.e. until remount.
* **L8 -- snapshot publication converges.** Backoff is bounded
  (`snapshot_publish_backoff_max_ms`, `Pool/CasRefLedger.cpp:2816`-`:2829`) and re-armed on failure, so a
  persistently failing checkpoint CAS grows the log tail without bound while the lane stays writable.

## Backend-conditional assumptions

`Backend/CasProbe.cpp:runCapabilityProbe` is unusually thorough and converts most would-be assumptions
into mount-time proofs: read-after-write (`:48`-`:53`), conditional create rejection *and*
non-clobbering (`:55`-`:66`), conditional overwrite rejection and non-clobbering (`:68`-`:79`),
read-after-overwrite (`:91`-`:94`), token freshness on every write (`:88`-`:90`), CAS create-if-absent and
token-exact CAS (`:97`-`:137`), conditional delete rejection (`:139`-`:151`), list-after-write
(`:153`-`:168`), delete visibility and list-after-delete (`:184`-`:195`). What remains
backend-conditional:

* **Conditional DELETE atomicity.** `deleteExact` maps to a real `DeleteObject` with `If-Match`
  (`src/Disks/DiskObjectStorage/ObjectStorages/S3/S3ObjectStorage.cpp:479`-`:512`). The probe proves the
  header is *honoured for a mismatch* on one object, but not that it is honoured under concurrency; a
  store that evaluates the precondition non-atomically with the delete silently voids S1(c). No further
  code guard exists downstream of `deleteExact`.
* **Delete markers / versioning.** Detection depends entirely on the backend surfacing
  `created_delete_marker`; `ObjectStorageBackend::deleteExact` in emulated mode never sets it
  (`Backend/CasObjectStorageBackend.cpp:763`-`:786`), and the GCS-specific versioning precondition
  degrades to a warning when `isBucketVersioningEnabled()` returns `nullopt`
  (`:59`-`:67`). On a versioned bucket a delete marker also hides the object from `list` and `head`, so the
  probe's list-after-delete check passes -- there is no second detector (F9).
* **List tokens.** `supportsListTokens()` is false whenever the backend uses generation tokens
  (`Backend/CasObjectStorageBackend.h:40`), so `ListedKey::token` is absent on GCS and every
  list-then-delete consumer must fall back to a HEAD. Both consumers do
  (`Gc/CasNamespaceJanitor.cpp:80`-`:97`, `Tools/CasDecommission.cpp:44`-`:56`), which converts a
  correctness dependency into a per-key request cost, but it also *widens* the observe->delete window on
  exactly those backends.
* **Token type coupling.** `mintingTypeMatches` turns a token-type mismatch into
  `PreconditionFailed`/`TokenMismatch` rather than an error
  (`Backend/CasObjectStorageBackend.cpp:677`, `:698`, `:736`). Mixing modes against one pool therefore
  degrades into permanent conflicts rather than a loud refusal.
* **Emulated token identity.** The emulated backend synthesises tokens from etag plus a per-key counter
  and prunes that state after ~2s (`Backend/CasObjectStorageBackend.cpp:344`, `:396`-`:416`,
  `:447`-`:465`). Token distinctness across an A->B->A rewrite of identical bytes therefore depends on
  wall-clock-aged in-process state; after pruning, an ABA rewrite can re-mint the same token value. This
  is single-process-only by construction, but every token-exactness invariant above is weaker there.
* **Multipart conditional writes.** Native mode forces single-part uploads only for generation-token
  backends (`:632`-`:636`); on S3 an `if-none-match` multipart create is assumed to be atomic, and
  `checkConditionalWriteSingleAttemptSupport` (`:78`-`:91`) only proves that a single-attempt retry
  profile exists.
* **Read path.** Blob reads are plain ranged reads with no token, no `If-Match` and no digest
  verification (`Pool/CasManifestReader.cpp:133`-`:151`, `ContentAddressedMetadataStorage.cpp:1451`);
  read-after-overwrite semantics for a resurrected incarnation are relied on but are harmless only
  because content addressing makes the payload identical. There is no pin across the read (sibling
  finding), so a concurrent reclaim surfaces as a query-level `FILE_DOESNT_EXIST`.

## Findings

### tla-fidelity-1 -- graduation's condemn-marker guard is vacuous when the callback is omitted (Medium)

- **Anchor**: `Gc/CasBlobInDegree.cpp:396` (`if (e.marker_confirmed || !confirm_condemned_marker ||
  confirm_condemned_marker(e))`); caller that omits it: `Gc/CasGc.cpp:2816`-`:2821`.
- **Trigger**: any call of `foldDeltasIntoGeneration` with a default-constructed
  `confirm_condemned_marker` and a non-empty `prior_runs` containing condemned rows. `rebuildBaseline` is
  such a call site today; it is currently harmless only because it also passes an empty `prior_runs`
  (`Gc/CasGc.cpp:2809`, `prior_runs` starts empty and is only filled by this same loop), so no condemned
  row is ever reached. `head_blob` and `peek_head` are omitted in the same call.
- **Evidence**: the guard's polarity places the invariant in the *caller*, not the check. The reducer's own
  contract already tolerates absent callbacks (`Gc/CasBlobInDegree.cpp:428`, `:450` both test the
  callback for null before using it), so nothing in the signature or the body forces a caller to supply
  the marker prover. A future rebuild that seeds `prior_runs` from the parent seal -- the natural fix for
  finding tla-fidelity-3 -- would silently publish `delete_pending` with no durable marker and delete on
  the next round, defeating S3 (writers would still see `Clean` meta and adopt).
- **Notes**: the safe polarity is to require the prover (assert non-null) and let callers pass an
  explicit always-false prover when they intend to carry everything.

### tla-fidelity-2 -- the destructive part of a GC round is not lease-revalidated (Medium; High composed with the adoptEvidence bypass)

- **Anchor**: `Gc/CasGc.cpp:611`-`:665` (blob redeletes), `:865`-`:884` (manifest deletes), `:906`-`:930`
  (orphan sweep). Contrast `:2338`-`:2354`, where ref-object cleanup re-reads `gc/state` and compares
  `lease.owner`/`lease.seq` before *every* delete.
- **Trigger**: two GC actors on one pool. Leader A acquires the lease, folds (a long, list-heavy phase),
  and is stolen from by B (`:3175`-`:3185`) while folding. A then executes its whole redelete batch at
  `:613` and only discovers the loss at the round-commit CAS at `:804`, which aborts *after* the deletes.
- **Evidence**: the redelete batch is ordered before the only lease re-check in the round. Token-exactness
  bounds the damage to blobs whose current token still equals the token recorded at condemn time, so a
  resurrect-based in-degree recovery is safe; the unsafe case is an in-degree recovery that reuses the
  *same* incarnation, which is exactly what `adoptEvidence` (`Pool/CasPartWriteTxn.cpp:478`) permits
  because it neither HEADs the object nor reads the condemn marker. B spares the blob, A deletes it, and
  the build that adopted it commits a ref over missing bytes.
- **Notes**: the manifest-delete and orphan-sweep loops run after the round commit but still without a
  per-delete check, so a steal during those phases has the same shape with a shorter window. The cheap fix
  is to reuse the `deleteRefObject` revalidation closure for all three loops.

### tla-fidelity-3 -- GC REBUILD discards the condemn universe and permanently orphans already-unreferenced blobs (High)

- **Anchor**: `Gc/CasGc.cpp:2809`-`:2824` (`prior_runs` starts empty; `flush_shard` folds only `+1`
  deltas built from committed refs, live precommits and unowned-but-alive manifests, `:2876`-`:2951`).
  The only listing of `blobsPrefix()` anywhere in CAS is the fsck tool, `Tools/CasFsck.cpp:581`.
- **Trigger**: `SYSTEM CAS GC REBUILD` (or the FORCE path after any `gc/state` loss). Any blob that is
  unreferenced at that moment -- including every blob already carrying `delete_pending` -- is absent from
  the rebuilt generation.
- **Evidence**: blob discovery in the steady state depends on an edge *transition*: `closeBlob` only emits
  a `kZeroMarker`/`kCondemned` sentinel when `cur_edges == 0 && cur_touched`
  (`Gc/CasBlobInDegree.cpp:450`, `:472`), and `cur_touched` is set only by a prior-run row or a delta
  (`:513`, `:527`, `:535`). A blob with no owner produces no delta and has no prior row after a rebuild,
  so it is never touched again and `zeroInDegree` (`:557`) can never see it. Its `.meta` may still say
  `Condemned`, which does not help: nothing scans meta keys either.
- **Notes**: this is a permanent, unbounded space leak whose size equals "everything deleted but not yet
  reclaimed at rebuild time", and it is invisible in `RoundReport` (`candidates`/`condemned` simply stay
  zero). fsck can enumerate the orphans but has no reclaim path wired to the GC generation.

### tla-fidelity-4 -- the condemn marker is not incarnation-scoped, and "already condemned" is accepted as proof (Medium)

- **Anchor**: `Formats/CasBlobMetaFormat.h:14`-`:22` (`BlobMeta` has `state`, `condemn_round`, `size` and
  no token/incarnation); `Gc/CasGc.cpp:95`-`:97` (`writeCondemnedMeta` returns `true` when the meta is
  already `Condemned`, without comparing `condemn_round` or size); `Gc/CasGc.cpp:1356`
  (`confirm_condemned_marker` tests only `state == Condemned`); `Gc/CasGc.cpp:100`-`:106`
  (`deleteConfirmedMeta` deletes whatever meta is current).
- **Trigger**: a digest that goes through condemn -> resurrect -> re-condemn, or condemn -> delete with the
  meta-delete job failing (failures are swallowed at `Gc/CasGc.cpp:329`-`:335`) -> re-upload. In the
  `replaced` path (`Gc/CasBlobInDegree.cpp:433`-`:443`, marker write at `Gc/CasGc.cpp:727`) the new
  incarnation's marker write short-circuits on the *old* incarnation's marker and then
  `noteCondemnMarkerDurable` memoises confirmation for the *new* token
  (`Gc/CasGc.cpp:357`-`:358`).
- **Evidence**: the in-process memo `condemn_markers_confirmed` is keyed by `(ref, token)`
  (`Gc/CasGc.h:444`), i.e. the code's own model treats condemnation as incarnation-scoped, but the
  durable artifact it is derived from is not. Nothing compares the marker's `condemn_round` against the
  row's `condemn_round`, so a stale marker is accepted as evidence for a fresh condemnation.
- **Notes**: current impact is bounded because S3's adopt check also keys off the same coarse
  `Condemned` flag, so the composition still fails closed for readers/adopters; the defect is that
  graduation "evidence" proves less than the code's structure claims, and it removes the natural
  cross-check that would have caught tla-fidelity-1 and tla-fidelity-2.

### tla-fidelity-5 -- plain-object writes bypass the margin-checked write fence and the request controller (Medium)

- **Anchor**: `Pool/CasPool.cpp:141`-`:144` (plain objects get `fenceGeneration` +
  `checkFenceOrThrow`) versus `:151` (the ledger gets `refAppendFenceOk`);
  `Pool/CasMountRuntime.cpp:90`-`:99` (`checkFenceOrThrow` -> `mayMutate()`, no margin) versus `:101`-`:111`
  (`refAppendFenceOk`, margin = `attempt_timeout_ms + lease_safety_margin_ms`);
  `Pool/CasPlainObjects.cpp:27`-`:38` and `:57`-`:63` (raw `putIfAbsent`/`putOverwrite`/`deleteExact`).
- **Trigger**: a namespace-file or mountpoint-object write issued when the mount deadline is within one
  attempt timeout. `mayMutate()` still returns true, the request is sent, the lease lapses, the GC leader
  fences the mount (`Pool/CasServerRoot.cpp:527`), a successor reclaims it
  (`Pool/CasServerRoot.cpp:347`), and the in-flight write lands afterwards.
- **Evidence**: every other durable-write family routes through `CasRequestController`, which refuses to
  *start* an attempt without margin (`Backend/CasRequestControl.cpp:193`, `:261`, `:305`) and re-checks
  before each reissue (`:299`). `CasPlainObjects` has neither the margin nor the bounded-attempt
  accounting, and its retry loops run up to 100 attempts (`Pool/CasPlainObjects.cpp:18`).
- **Notes**: the head-then-conditional-write shape keeps this token-exact, so the failure is a lost or
  duplicated namespace-file mutation across incarnations rather than arbitrary clobbering.

### tla-fidelity-6 -- staged-manifest debris cleanup can delete a body that a live precommit still owns (Medium)

- **Anchor**: `Pool/CasPartWriteTxn.cpp:866`-`:884` (`cleanupStagedManifestDebrisBestEffort` skips only
  `precommit_manifest`/`precommit_target_ns`); `:587`-`:590` (`precommitAdd` *overwrites* the single
  `precommit_target_ns`/`precommit_final_ref`/`precommit_manifest` triple);
  `:807`-`:821` (`abandon` only removes that one binding); `:107`-`:112` (the destructor only enqueues
  cleanup duty for that one triple).
- **Trigger**: any build that calls `precommitAdd` more than once on one `PartWriteTxn` (two refs, or a
  retry that re-stages and re-precommits a second manifest), then abandons or is destroyed. The first
  precommit binding stays durable in the ref log while its manifest body is deleted here.
- **Evidence**: the resulting state -- a live `Precommit` owner naming an absent manifest body -- is
  exactly what the fold classifies as `HoldReason::ManifestBodyMissing` (`Gc/CasGc.cpp:2897`-`:2909`),
  which mints a hold, which sets `suppress_destructive` for the *entire pool* every pass
  (`:2063`-`:2065`), and which is re-adopted from the parent seal on every subsequent pass
  (`:2913`-`:2921`). The hold's only recorded escape is `next_retry_round`, and the stale-precommit sweep
  cannot clear it either because the binding's `writer_epoch` equals the live epoch
  (`Pool/CasRefLedger.cpp:3142`).
- **Notes**: one leaked in-epoch precommit therefore stops all reclamation pool-wide until the next
  writer epoch. Whether a second `precommitAdd` per txn is reachable from today's callers was not
  established statically; the defect is that the single-slot bookkeeping makes the cleanup's exclusion
  unsound by construction rather than by convention.

### tla-fidelity-7 -- no re-hash on any body re-upload: the content-address invariant is size-checked only (Medium)

- **Anchor**: `Pool/CasPartWriteTxn.cpp:387`-`:420` (`streamIfAbsent` copies `source.open()` and validates
  `written != source.size` only), `:435` (second attempt), `:463` and `:471` (`resurrect`), `:392`
  (`promoteStaged`, a server-side copy that never reads the bytes);
  `Backend/CasObjectStorageBackend.cpp:827` and `:841` (resurrect's own check is `!= payload_size`).
  The only hash of the payload is the single pass at `ContentAddressedTransaction.cpp:1273`/`:1281`.
- **Trigger**: the source bytes differ from the bytes that were hashed, at equal length -- a corrupted or
  concurrently rewritten local staging file between the hashing pass and any re-read, or a staged S3
  object mutated before `promoteStaged`. Every retry path re-reads rather than re-hashes.
- **Evidence**: `BlobSource` is a re-openable factory (`Pool/CasPool.h`, `source.open()`), and the upload
  path consumes it up to 8 times (`Pool/CasPartWriteTxn.cpp:177`-`:191`) without ever recomputing the
  digest. The stored envelope header does record `intended_ref`
  (`Formats/CasBlobEnvelopeFormat.cpp:119`-`:129`) but nothing on the write or read path compares the
  body against the digest in its own key; the read path does no verification at all
  (`Pool/CasManifestReader.cpp:133`-`:151`).
- **Notes**: consequence is silent cross-table corruption, because a wrong-content blob under digest `D`
  is dedup-adopted by every future writer whose data really does hash to `D`. Contrast the manifest path,
  which *does* verify a payload digest on decode (`Formats/CasPartManifestFormat.cpp:263`-`:267`) --
  the asymmetry is itself evidence that verification was intended.

### tla-fidelity-8 -- adoptEvidence bypasses both adoption guards and can downgrade a tokened dep (Low; the bypass itself is a cited sibling finding)

- **Anchor**: `Pool/CasPartWriteTxn.cpp:478`-`:486`; guards it skips are at `:262`-`:278` (condemn marker)
  and `:280`-`:285` (`EDGE-BEFORE-OBSERVE`); trusted at commit by `:679`-`:695`.
- **Trigger**: `deps[entry.ref] = {..., adopted = true}` unconditionally overwrites an existing dep, so a
  blob that this same build already uploaded with a real token becomes a tokenless trusted adopt if
  `adoptEvidence` is later called for that ref.
- **Evidence**: `mergeBlobUploadResults` explicitly refuses the *opposite* direction, rejecting tokenless
  records with "a tokenless dep must be recorded via adoptEvidence, never merged here"
  (`:201`-`:205`), and refuses any two differing records for one ref (`:206`-`:213`). No comparable
  guard protects `deps` from `adoptEvidence`.
- **Notes**: reported here only to complete the bypass table; the reachability and impact of the
  underlying condemn-marker bypass are the sibling audit's finding and are not re-litigated.

### tla-fidelity-9 -- the "no versioned bucket" precondition is unverifiable on backends that do not report delete markers (Medium)

- **Anchor**: `Backend/CasProbe.cpp:175`-`:183` (the only mount-time detector is
  `d.created_delete_marker`); `Gc/CasGc.cpp:614`-`:617` (the only in-round detector, same signal);
  `Backend/CasObjectStorageBackend.cpp:763`-`:786` (emulated `deleteExact` never sets it);
  `:53`-`:76` (`checkPoolPreconditions` only runs for generation-token backends and downgrades an
  unverifiable versioning check to a warning at `:59`-`:67`).
- **Trigger**: a CAS pool on a versioned S3-compatible bucket whose `DeleteObject` response omits
  `x-amz-delete-marker`, or whose ClickHouse object-storage implementation does not surface it.
- **Evidence**: on a versioned bucket a delete marker hides the object from both `head` and `list`, so the
  probe's delete-visibility and list-after-delete checks (`Backend/CasProbe.cpp:184`-`:195`) still pass.
  The shipped string at `:177`-`:183` states this condition "is NOT ignorable and has no override", which
  makes the single-signal dependency a specification gap rather than a tolerated risk.
- **Notes**: symptom is that GC reports healthy reclaim (`report.deleted` increments) while bucket size
  grows without bound; ref objects, which are rewritten on every commit, dominate the growth.

### tla-fidelity-10 -- ref-object trimming is starved by any concurrent catalog mutation (Medium)

- **Anchor**: `Gc/CasGc.cpp:2320`-`:2336` (revalidation requires
  `current_catalog.token == folded.catalog_cut->token`), `:2396`-`:2412` (`return` out of the whole
  function on the first refusal, for both logs and snapshots).
- **Trigger**: any CREATE/DROP of any table in the pool between the fold's catalog read and the cleanup
  phase. The catalog is a single object shared by all namespaces, so its token changes on every namespace
  lifecycle event anywhere in the pool.
- **Evidence**: the entry-level checks immediately after (`*current_entry_it != observed_entry`, life
  resolution, GC fence) are already sufficient for the per-namespace safety argument; the additional
  whole-object token equality makes the guard pool-global. Because the refusal exits the function rather
  than skipping the namespace, one unlucky namespace also starves all later ones in the same pass.
- **Notes**: consequence is unbounded growth of `ref/**` logs and snapshots (recovery replay cost grows
  with them, `Pool/CasRefLedger.cpp` recovery walk), on exactly the busy clusters that need trimming most.

## Coverage

Read in full or in the parts relevant to state transitions and guards:
`Backend/CasBackend.h`, `Backend/CasProbe.cpp`, `Backend/CasObjectStorageBackend.{h,cpp}`,
`Backend/CasRequestControl.{h,cpp}` (guard call sites only),
`Primitives/CasTypes.h`, `Formats/CasRefLogFormat.h`, `Formats/CasBlobMetaFormat.h`,
`Gc/CasBlobInDegree.{h,cpp}`, `Gc/CasGc.{h,cpp}` (lease, round, fold, condemn/graduate/delete, rebuild,
ref cleanup, preview), `Gc/CasNamespaceJanitor.cpp`, `Pool/CasBlobMeta.{h,cpp}`,
`Pool/CasPartWriteTxn.cpp`, `Pool/CasRefLedger.{h,cpp}` (lane/wedge/sweep/drop/publish),
`Pool/CasRefProtocol.{h,cpp}` (state projection, cleanup planning, epoch crossing),
`Pool/CasRefCatalog.cpp`, `Pool/CasServerRoot.cpp` (epoch, mount, keeper, heartbeat floor),
`Pool/CasMountRuntime.cpp`, `Pool/CasPlainObjects.cpp`, `Pool/CasManifestReader.cpp` (locate/read),
`Pool/CasPool.cpp` (wiring), `Tools/CasDecommission.cpp` (delete paths),
`ContentAddressedTransaction.cpp` (hashing write buffers),
`src/Disks/DiskObjectStorage/ObjectStorages/S3/S3ObjectStorage.cpp` (conditional delete).

Not covered (out of budget for this pass, no findings claimed about them): the ref recovery walk and
snapshot/checkpoint publication in detail (`Pool/CasRefLedger.cpp` `runRecoveryWalkOnce`,
`commitRefChunk`, ~1400 lines), `Gc/CasOrphanManifestSweep.cpp` retention classification,
`Gc/CatalogLifecycleReconciler.cpp`, `Gc/CasGcShardPlan.cpp`, `Tools/CasFsck.cpp`,
`Tools/CasInspect.cpp`, all `Formats/*` codecs beyond the three named above, and the
`ContentAddressedMetadataStorage`/`ContentAddressedExchange` disk-facing layer except the blob read
call site.

Method limits: static only. Reachability claims about caller shapes (notably the double-`precommitAdd`
in tla-fidelity-6 and the two-GC-actor deployment in tla-fidelity-2) were not confirmed by execution,
and are stated as triggers rather than as observed failures. No `.tla` model, no tests and no docs were
used as evidence.

# jepsen-anomaly -- fresh audit 2026-08-12

## Scope

Static, code-only audit of the CAS working tree at
`/Volumes/workspace/altinity-clickhouse/ClickHouse` (branch `cas-code-only-strip`, base
`842f2b37b8f`), root
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

Question asked: for each classical Jepsen-checker anomaly (lost update, dirty/aborted read,
stale read, non-monotonic read, read-your-writes, causal violation, split brain / dual writer,
replica divergence, missing/committed-but-unreadable read, resurrection, duplicate application,
non-linearizable register) — does the code admit it, with a concrete interleaving anchored at
`file:line`?

Method: types, control flow, and error classification only. `docs/**` and comments are not
treated as evidence of intent; shipped strings (exception messages, `DECLARE()` descriptions,
`describeUnresolvedReason` at `Backend/CasRequestControl.h:47-69`) are. All CAS tests are deleted
in the working tree, so nothing here is validated by a test in-tree.

Calibration accepted as given: transactions are eager (`transactionIsStagingOverlay()==true`,
`ContentAddressedMetadataStorage.h`, asserted at `DiskObjectStorageTransaction.cpp:619-622`);
`Mode::EmulatedSingleProcess` is auto-selected for local object storage
(`ContentAddressedMetadataStorage.cpp:509-520`).

Already found by sibling audits — cited where relevant, **not** re-reported as mine: unrevertible
repoint of a committed ref (`ContentAddressedTransaction.cpp:280-289,344-347`); `Backend::resurrect`
bypasses `CasRequestController`; GC `adoptEvidence` bypasses the condemn marker; the GC lease has no
TTL and rebuild never renews it; the read path never pins a blob across the GET; offset taken from
pool meta rather than the envelope; `PartFolderView` byte accounting is a constant 256
(`Parts/PartFolderAccess.cpp:128-131`).

## Registers and their CAS primitives

| Register | Key | Primitive | Real-backend semantics | Indeterminate outcome |
|---|---|---|---|---|
| ref (namespace,ref)→manifest | `refLogKey(life,{epoch,seq})`, `CasLayout.h:94-97` | write-once `putIfAbsent` on a derived id, via `putIfAbsentControlled` (`CasRefLedger.cpp:2455`) | S3 `If-None-Match: *` (`CasObjectStorageBackend.cpp:642-656`); id = `(writer_epoch, ref_sequence)` (`CasTypes.h:214-229`, `CasRefProtocol.cpp:418-423`). Log-structured CAS, **not** an in-place CAS; exclusion rests on the writer epoch being unique, i.e. one server root per namespace | resolved: `resolveByExactGet` compares bytes (`CasRequestControl.cpp:212-239`); else the lane **wedges** on the same key (`CasRefLedger.cpp:2684-2720`) |
| committed frontier `_ckpt` | `refCkptKey(life)`, `CasLayout.h:104-107` | raw `casPut` in a merge-monotone loop (`CasRefCkpt.cpp:137-240`) | ETag/generation CAS over a join of maxima; `mergeCommittedThrough` rejects non-adjacent epochs (`CasRefCkpt.cpp:34-53`) | resolved: mandatory exact re-read, then re-merge (`CasRefCkpt.cpp:202-232`) |
| namespace catalog | `refCatalogKey()`, `CasLayout.h:248-251` | raw `casPut` read-modify-write, `casUpdateImpl` (`CasRefCatalog.cpp:103-125`) | ETag/generation CAS, pool-global single object | **not** resolved in `casUpdateImpl` (throws out); one caller does resolve (`CasRefCatalog.cpp:335-383`). Retry-idempotent by construction (see "not admitted") |
| mount lease | `mountKey(srid)`, `CasLayout.h:228-231` | raw `putIfAbsent`/`putOverwrite(expected=last_token)` (`CasServerRoot.cpp:309,335,348,813,934,1038`) | true CAS; monotone `seq` in the body forbids ABA; steal requires a fenced/clean/token-stable certificate (`CasServerRoot.cpp:343-365,398-453`) | throws out of `renewOnce`; `backgroundLoop` keeps the lease only while `shouldFenceOnTransientRenewFailure()` is false (`CasServerRoot.cpp:732-739,1092-1138`) |
| writer epoch | `epochKey(srid)`, `CasLayout.h:223-226` | raw `casPut` allocate-and-bump (`CasServerRoot.cpp:230-244`) | true CAS; **per server root**, so epoch values repeat across server roots of one pool | throws out; a burned epoch is harmless |
| GC lease / state | `gcStateKey()`, `CasLayout.h:157-160` | raw `casPut` (`CasGc.cpp:3123,3144,3178,804,2987`) | true CAS on the state object, but liveness evidence is the separate `gc/hb` object whose `casPut` result is **discarded** (`CasGc.cpp:3089-3103`); steal predicate has no time term (`CasGc.cpp:3155-3184`) | throws out of the round, caught and ignored by the scheduler (`CasGcScheduler.cpp:271-275`) |
| pool meta | `poolMetaKey()`, `CasLayout.h:243-246` | raw `casPut` create-if-absent / admit-algo (`CasPoolMeta.cpp:74,118`) | true CAS | partially resolved by re-read; an absent key after a reported Conflict is a hard `LOGICAL_ERROR` (`CasPoolMeta.cpp:121-124`) |
| plain objects (namespace files, mountpoint objects) | `namespaceFileKey`, `mountpointObjectKey`, `CasLayout.h:124-155` | head-then-`putOverwrite` retry loop (`CasPlainObjects.cpp:21-41`), head-then-`deleteExact` loop (`:51-66`) | last-writer-wins; the loop re-heads and overwrites whatever it finds — no read-modify-write, no controller | **never** resolved: the exception escapes `casPutObject` (see jepsen-anomaly-4) |
| all of the above, local object storage | — | `Mode::EmulatedSingleProcess` | `emuExists`+`emuWrite` under a **process-local** `emu_mutex` (`CasObjectStorageBackend.cpp:651-655,687-693,715-731`); token = file mtime ns (`LocalObjectStorage.cpp:391,424`) with a process-local `#N` disambiguator (`:447-465`) | no cross-process atomicity at all (shipped warning, see by-design) |

## Findings

### jepsen-anomaly-1 -- Split brain / dual writer, replica divergence, terminal wedge: shadow (FREEZE) namespaces are pool-global while every exclusion primitive is per-server-root (High)

- **Anchor.** `ContentAddressedMetadataStorage.cpp:897-900`
  (`shadowNamespace(dir) = RootNamespace{canonicalDiskPath(dir)}` — no `serverPrefix()`), against
  `:886-889` (`liveNamespace = serverPrefix() + "/" + …`, and `serverPrefix() == server_root_id`,
  `:858-861`). The shadow dir is `shadow/<backup_name>/store/<xxx>/<table_uuid>`
  (`Parts/PartPathParser.cpp:204-208`) and is routed straight into the ref ledger as the namespace
  (`ContentAddressedMetadataStorage.cpp:907-913,1070-1073,1205-1212`). The exclusion primitives are
  all keyed by `server_root_id`: `mountKey(srid)`, `epochKey(srid)` (`CasLayout.h:223-231`), and the
  mount lease refuses take-over only across a *foreign server uuid* on *its own* slot
  (`CasServerRoot.cpp:318-323,785-802`).
- **Trigger (interleaving).** One pool prefix, two server roots `A` and `B` (a supported topology:
  `serverRootsPrefix()` is pool-global and GC iterates every server root,
  `CasServerRoot.cpp:455-552`). Both hold valid, non-conflicting mount leases and independent writer
  epochs. On each node: `ALTER TABLE t FREEZE WITH NAME 'b1'` for the same replicated table — the
  same `table_uuid`, the same backup name, hence byte-identical `shadow_table_dir` and one shared
  `RootNamespace`.
  1. `A` (live epoch 7) creates the catalog life and appends `(7,1)`, `(7,2)` binding
     `part_all_1_1_0 → M_A`.
  2. `B` recovers the *same* namespace, replays `A`'s log (`CasRefLedger.cpp:640-693`), and installs
     `A`'s refs into `B`'s in-memory table. `B`'s `SELECT`/list of its own `shadow/b1/…` now returns
     `A`'s parts, whose blobs are readable from the shared pool: **divergence / phantom read of
     another node's backup.**
  3. `B` appends with `nextRefTxnId(greatest_applied=(7,2), live_epoch=4) = (4,1)`
     (`CasRefProtocol.cpp:418-423`). Its `_ckpt` contribution carries `life_epoch = 4` below the
     durable `7`, so `publishCkpt` takes `lifeEpochWouldDecrease` and throws
     (`CasRefCkpt.cpp:55-70,157-168`). The shipped string states the consequence exactly: *"This
     object has NO in-place repair … every later writer will hit this same refusal and the namespace
     cannot be written again until it is recreated."* → **terminal wedge of the shared namespace.**
  4. Symmetric case, both epochs equal: both derive the same id, the loser's `putIfAbsent` sees a
     different occupant, `resolveByExactGet` raises `CORRUPTED_DATA`
     (`CasRequestControl.cpp:236-238`) and the lane faults via `on_impossible_interference`
     (`CasRefLedger.cpp:2472-2530`) — loud, but a permanent per-namespace fault until remount.
  5. Related second interleaving: `A` unfreezes (`removeRecursive` → `dropNamespace(shadowNamespace(path))`,
     `ContentAddressedTransaction.cpp:713-721`) while `B` is still freezing. `B`'s positive appends
     then refuse because the exact life is no longer `Live`
     (`CasRefLedger.cpp:2313-2335`), and `B`'s already-published backup refs are deleted by `A`'s
     namespace removal — a cross-node destructive interference on committed state.
- **Evidence.** The only thing that keeps two live server roots off one ref table is the namespace
  name being server-root-scoped; `liveNamespace` does that, `shadowNamespace` does not. The
  `_ckpt` refusal string ("Writer epochs are monotone **per server root**, so a lower contribution
  means a superseded writer's work reached this object") is shipped, admissible, and states the
  invariant that this namespace class violates.
- **Notes.** Jepsen names for the three observable outcomes: dual writer / split brain, divergence
  between replicas, and (4) a non-linearizable register that faults instead of losing data. The
  silent one is (2): reads on `B` return refs that `B` never wrote — a read of another node's writes
  with no error. Fix direction: scope the shadow namespace by `server_root_id` exactly like
  `liveNamespace`, or make the writer epoch pool-global.

### jepsen-anomaly-2 -- Aborted read (G1a) and intermediate read (G1b): a failed multi-ref commit publishes refs one at a time and compensates best-effort (Medium)

- **Anchor.** `ContentAddressedTransaction.cpp:312-352`. `commit()` loops
  `publishStaging(...)` per `(ns, ref)` (`:338-339`); each call performs a durable ref mutation
  (`repointRef` at `:280`, `promoteBuild` at `:305`). On any later failure the `catch` at `:341-348`
  compensates only entries with `oc->created`, via
  `CachedPartFolderAccess::dropRefIfMatches`, which is `noexcept` and swallows its own failure
  (`Parts/PartFolderAccess.cpp:518-562`, shipped log: *"the ref may remain live"*, counter
  `CASRefRollbackBestEffortDropFailed`). The eagerness is structural, not incidental:
  `DiskObjectStorageTransaction::tryCommit` refuses to let a CAS transaction queue deferred
  operations (`:619-622`), and `undo()` removes only blobs (`:698-709`).
- **Trigger (interleaving).** A transaction touching two parts of one table (e.g. a mutation or a
  multi-part attach) `P1` and `P2`:
  1. `publishStaging(P1)` → `repointRef` commits; the ref-ledger install makes it visible to every
     reader in the process immediately (`CasRefLedger.cpp:2578-2635`, then `resolveRef` reads the
     in-memory committed map, `:230-251`).
  2. A concurrent `SELECT`/merge/`system.parts` scan resolves `P1` and reads the new manifest →
     **intermediate read (G1b)** of a transaction that has not committed.
  3. `publishStaging(P2)` throws (any ambiguity: wedge, fence loss, `throwCasWriteRetryLater`).
  4. Compensation: `P1` is a repoint of a pre-existing ref, so `oc->created` is false and **nothing
     is attempted** — the aborted transaction's effect is permanent (this exact unrevertibility is
     the sibling finding at `:280-289,344-347`; cited, not claimed). If `P1` *was* a create, the
     compensating `dropRefIfMatches` is itself a fresh durable append that can fail and is swallowed
     → **aborted read (G1a)** with a success-shaped client error path.
- **Evidence.** Per-ref durable publication with no group commit, plus compensation that is (a) not
  attempted for repoints and (b) best-effort for creates. There is no barrier between step 1 and
  step 3 that hides `P1` from readers.
- **Notes.** The window in step 2 exists even when compensation succeeds, so it is not covered by
  the sibling's unrevertibility finding. A Jepsen list-append checker over per-part refs would flag
  both G1a and G1b.

### jepsen-anomaly-3 -- Non-linearizable register: a *definite* "conflict" is fabricated from an indeterminate write outcome (Medium)

- **Anchor.** `CasObjectStorageBackend.cpp:109-124`: `finalizeConditionalWrite` maps
  `PreconditionFailed` **and** `NoSuchKey` (both the exception name and the SDK error code) to
  `PutOutcome::PreconditionFailed`. `casPut` then converts that to `CasOutcome::Conflict`
  (`:696-712`) — a definite "someone else owns this key" answer. The producer of that `NoSuchKey`
  is `WriteBufferFromS3`, which throws `S3Exception(NO_SUCH_KEY, "Multipart upload failed with
  NO_SUCH_KEY error, retries {}")` after exhausting `max_unexpected_write_error_retries`
  (`IO/WriteBufferFromS3.cpp:698-717`, and the same handling for single-part at `:792-…`); CAS pins
  that budget to **1** (`CasObjectStorageBackend.cpp:637`,
  `s3_max_unexpected_write_error_retries_override = 1`), so the first such response is final.
- **Trigger (interleaving).** A store that answers a conditional PUT/CompleteMultipartUpload with
  `NoSuchKey` (the retry branch at `IO/WriteBufferFromS3.cpp:698-703` exists precisely because a
  store does this) while the key is in fact absent and unwritten:
  1. Pool bootstrap: `PoolMeta::createOrValidate` → `casPut(_pool_meta, …, expected=nullopt)` →
     `Conflict` → re-read shows the key **absent** → `LOGICAL_ERROR "create-if-absent reported
     Conflict but '{}' is absent on re-read"` (`CasPoolMeta.cpp:118-124`). The disk fails to start
     with an internal-inconsistency error for a transient store answer.
  2. Mount claim: `claimMount`'s `putIfAbsent` on an absent slot returns `!= Done` →
     `MountClaimResult::LiveDoubleStart` (`CasServerRoot.cpp:308-311`) → the waiter re-reads,
     finds nothing, restarts at most `kMaxObservationRestarts` times and gives up
     (`:423-435,388-391`) → the disk refuses to mount with `mountDoubleStartMessage`, i.e. a
     **phantom dual writer** report against a slot that does not exist.
  3. Lease renew: `SingleWriterSlot::renewOnce` sees `outcome != Done`, sets
     `last_renew_failure_was_confirmed_mismatch = true` and calls `onRenewMismatch`
     (`CasServerRoot.cpp:1038-1043`). The re-read shows our own uuid/epoch, unfenced, so the
     `same_epoch_state_uncertain` branch throws `ABORTED` (`:881-891`); because the failure is
     flagged *confirmed*, `backgroundLoop` skips the `shouldFenceOnTransientRenewFailure()` grace
     path (`:1108-1116`) and immediately fences the mount → every in-flight CAS write is refused and
     the pool self-remounts on a fresh epoch.
- **Evidence.** `PutOutcome` has exactly two values (`CasBackend.h:56-60`), so this layer cannot
  express "unknown"; the mapping at `:117-120` therefore has to pick one, and it picks the definite
  one. Contrast the project's own standard elsewhere: `publishCkpt` treats an ambiguous CAS as
  ambiguous and mandates an exact re-read (`CasRefCkpt.cpp:202-232`), and
  `CasUnresolvedReason`/`describeUnresolvedReason` exist precisely to keep "unproven" distinct from
  "failed" (`CasRequestControl.h:19-69`).
- **Notes.** All three consequences are fail-closed (availability and misdiagnosis, not corruption),
  which is why this is Medium and not High. The register-level defect is real though: a client of
  `casPut`/`putOverwrite` cannot distinguish "the store refused my precondition" from "the store lost
  my request", and two of the three call sites above turn the confusion into a terminal decision.

### jepsen-anomaly-4 -- Aborted read (G1a) on plain objects: an indeterminate namespace-file / mountpoint write is reported failed and never resolved (Medium)

- **Anchor.** `CasPlainObjects.cpp:21-41`. `casPutObject` does `head` → `putIfAbsent` or
  `putOverwrite(head.token)` in a bounded loop and lets **any** exception escape: there is no
  `try`, no exact-read resolution, no wedge, no controller — `CasRequestController` is never used on
  this path. Same shape for `casRemoveObject` (`:51-66`). Callers:
  `putNamespaceFile`/`removeNamespaceFile` (`:68-102`) and
  `putMountpointObject`/`removeMountpointObject` (`:104-122`).
- **Trigger (interleaving).** A single writer, no concurrency needed:
  1. `writeFile` on a non-part path → `casPutObject(k, v)`; the S3 PUT commits but the response is
     lost (socket timeout under the single-attempt profile,
     `CasObjectStorageBackend.cpp:628-640`).
  2. The exception propagates through `casPutObject` to the disk transaction, which reports failure;
     the query fails and the operation is treated as not applied.
  3. A later `readFile`/`listNamespaceFiles` returns `v` — the effect of an operation whose client
     was told it failed. **Aborted read (G1a)** on a durable register with no reconciliation path.
  4. Mirror case for `casRemoveObject`: the token-exact delete lands, the response is lost, the
     caller reports failure, and the object is gone.
- **Evidence.** Every other durable CAS register in the tree resolves ambiguity — the ref log wedges
  its lane on the same key until it resolves (`CasRefLedger.cpp:2684-2720`), `_ckpt` re-reads
  (`CasRefCkpt.cpp:202-232`), `putIfAbsentControlled` resolves by exact get
  (`CasRequestControl.cpp:290-303`). The plain-object path is the one register class with no such
  treatment, and it is exactly the class that backs table-level metadata files.
- **Notes.** Secondary observation on the same anchor: `casRemoveObject` re-heads on
  `TokenMismatch` and then deletes the *new* token, so it removes a version it never read; and
  `casPutObject`'s retry overwrites whatever it finds. Both are last-writer-wins by construction,
  which is linearizable for genuinely concurrent operations, so I do **not** report them as lost
  updates — the reportable defect here is the unresolved indeterminate outcome.

### jepsen-anomaly-5 -- Duplicate application: the GC lease is not a fencing token on the destructive path, and the liveness evidence that gates a steal is advisory (Medium)

- **Anchor.** Steal predicate: `CasGc.cpp:3155-3184` — a challenger takes the lease when the state's
  `(owner, seq)` is unchanged since its previous observation **and** `gc/hb` has not advanced; there
  is no time term, no TTL, and no expiry field in the decision. Liveness evidence:
  `pulseHeartbeat` (`CasGc.cpp:3089-3103`) **discards the `casPut` result** (line 3102 is a bare
  statement), and the scheduler swallows pulse exceptions (`CasGcScheduler.cpp:301-308`, shipped log
  *"heartbeat pulse failed (advisory; will retry)"*). Destructive path: the redelete loop calls
  `backend.deleteExact(blobKey(entry.ref), entry.token)` per entry with **no lease/generation
  re-check** inside or around the loop (`CasGc.cpp:605-640`); the same holds for the manifest and
  nomination deletes (`:868,908`) and the prefix sweeps (`:2364,2436-2440`).
- **Trigger (interleaving).** Leader `A` and follower `B` on one pool, `hb_interval < interval`:
  1. `A` acquires the lease (`owner=A, seq=5`), sets `i_am_leader`, enters a long round, and reaches
     the redelete loop.
  2. `A`'s heartbeat pulses fail or are refused for the span of one of `B`'s poll intervals — the
     `casPut` conflicts (result dropped, line 3102) or throws (swallowed,
     `CasGcScheduler.cpp:305-308`). `gc/state` also does not move, because `seq` is only bumped at
     round start (`CasGc.cpp:3140-3151`).
  3. `B` polls twice, sees `(A,5)` unchanged and `hb` unchanged, and steals:
     `casPut(gcState, {owner=B, seq=6}, expected=got->token)` → Committed
     (`CasGc.cpp:3175-3184`). `B` now believes it is the sole leader and starts its own fold.
  4. `A` is still inside its loop and keeps issuing token-exact deletes; nothing rejects them,
     because the object store has no notion of the GC lease and `A` re-reads `gc/state` only at the
     top of its *next* round. Two leaders act in the same window: **duplicate application** of the
     delete phase, with `A` deleting against a fold snapshot that `B`'s newer generation has already
     superseded.
- **Evidence.** The lease is authoritative (a real CAS) while the input to the steal decision is
  explicitly advisory, and the data path carries no fencing token derived from the lease. The
  contrast with the writer side is stark: durable ref writes pass a `fence_ok` closure into every
  attempt and re-check after the write (`CasRequestControl.cpp:261,305-309`), and the mount lease
  keeps a boot-clock deadline plus a safety margin (`CasMountRuntime.cpp:101-111`). The GC
  destructive path has neither.
- **Notes.** Related-but-distinct sibling finding: the GC lease has no TTL and rebuild never renews
  it (cited). My claim here is narrower and additive — the *steal is unfenced with respect to
  in-flight destructive work*, and the evidence gating it is silently droppable. Blast radius is
  limited by the condemn/graduate protocol and by `deleteExact` being token-exact (most double
  deletes are idempotent), which is why this is Medium; it becomes a resurrection/missing-read risk
  when combined with the sibling's `adoptEvidence`-bypasses-condemn finding.

## Anomalies checked and not admitted

- **ABA on any in-place register.** Native tokens are content ETags or GCS generations
  (`CasObjectStorageBackend.cpp:49-51`, `CasTypes.h:198-203`). ETag equality implies content
  equality, so an A→B→A cycle leaves the CAS base semantically valid; and the two registers where
  history (not content) matters carry monotone discriminators in the body — mount lease `seq`
  (`CasServerRoot.cpp:748-762,1037`) and GC lease `seq` (`CasGc.cpp:3140-3151`). Emulated tokens add
  a process-local `#N` counter for the same reason (`:447-465`). No harmful ABA found.
- **Conditional write silently degrading to unconditional for large payloads.** Checked because
  single-part is forced only for GCS generation tokens
  (`CasObjectStorageBackend.cpp:632-636`). `If-None-Match`/`If-Match` *are* applied to
  `CompleteMultipartUpload`, not just `PutObject` (`IO/WriteBufferFromS3.cpp:645-660` vs
  `:735-740`), so multipart conditional writes keep CAS semantics. Not admitted.
- **Lost update on the namespace catalog via an unresolved `casPut`.** `casUpdateImpl` does not
  resolve ambiguity (`CasRefCatalog.cpp:103-125`), but every caller is retry-idempotent: a lost
  `createNamespaceStep1` response is re-derived because the retry recognises its own creator fence
  (`CasRefLedger.cpp:904-914`), `completeCreation` converges on `Live`
  (`CasRefCatalog.cpp:445-467`), `reconcileStaleCreator`/`cancelStalledCreating` re-read and
  re-decide (`:401-425,507-541`). No anomaly, only a style inconsistency with `:335-383`.
- **Stale read from the part-folder view cache.** `getView` re-resolves the ref first and serves a
  cached view only when `cached->manifestId() == resolved->manifest_id`
  (`Parts/PartFolderAccess.cpp:149-188`). A repointed ref cannot be served from cache.
- **Non-monotonic read across ref-table eviction / remount.** A txn is installed into the in-memory
  table only *after* its `_ckpt` frontier is published (`CasRefLedger.cpp:2545-2614`), so anything a
  reader has observed is already durable and is re-derived by replay
  (`:640-693`). Reads cannot move backwards.
- **Split-brain of the mount lease via wall-clock trust.** The reclaim path refuses wall-clock
  reasoning and requires a fenced/clean/token-stable certificate
  (`CasServerRoot.cpp:343-365`); the stability threshold `ttl + ttl/20 + cadence`
  (`:393-396`) is measured from the challenger's *first sight* of a token that the incumbent had
  already written, and the incumbent's own boot-clock deadline is anchored *before* its renew is sent
  (`CasMountRuntime.cpp:113-127,202-219`), so the challenger's steal is strictly later than the
  incumbent's self-fence. Ordering holds; not admitted.
- **Lost lease renewal turning into a dual writer.** An ambiguous renew that actually landed makes
  the next renew's stale-token `putOverwrite` fail, and the mismatch classifier fences the runtime
  instead of re-minting (`CasServerRoot.cpp:864-919`). Fail-closed.
- **GC fencing out a live mount.** `computeHeartbeatFloor` fences only on token stability over a
  caller-supplied threshold and re-classifies up to `max_reclassify` times
  (`CasServerRoot.cpp:480-540`); the lease body changes on every renew, so a live renewing mount is
  never seen as stable.
- **Duplicate application of a ref transaction.** Ids are write-once slots; a replayed attempt with
  identical bytes resolves to `Committed` and a different occupant raises `CORRUPTED_DATA`
  (`CasRequestControl.cpp:229-238`), so a txn cannot be applied twice under one id.
- **Dedup against a condemned blob (missing read).** `observeAndAdmit` point-reads the blob meta and
  aborts on `MetaState::Condemned`, and refuses to adopt at all before the build's precommit is
  durable (`Pool/CasPartWriteTxn.cpp:250-305`), with the dedup cache hit still going through a real
  `head` (`:149-175`). Residual risk in this area belongs to the sibling `adoptEvidence` finding.
- **Manifest cross-wiring in a shared namespace.** Manifest keys are `(epoch, build_seq, ordinal)`,
  not content-addressed (`CasLayout.h:139-145`), so a shared namespace can collide; but
  `stageManifest` goes through `putIfAbsentControlled`, whose byte comparison raises
  `CORRUPTED_DATA` rather than adopting a foreign body
  (`Pool/CasPartWriteTxn.cpp:547-559`, `CasRequestControl.cpp:236-238`). Fails closed.

## By-design / info

- **Emulated mode is single-process by contract.** The shipped mount log states it: *"emulated
  in-process conditional operations — safe ONLY for a single server. Do NOT share this pool path
  between multiple ClickHouse servers (e.g. a shared/NFS mount): the CAS/GC invariants would break
  silently"* (`ContentAddressedMetadataStorage.cpp:514-520`). Two processes over one local path would
  give lost updates on every register (`emu_mutex` is process-local,
  `CasObjectStorageBackend.cpp:651-655`) and a dual mount lease; that is an admitted,
  documented-unsafe configuration, not a finding.
- **"Unresolved" writes becoming visible later is deliberate, and the wording is honest.** A wedged
  append tells the client the outcome is *"UNCERTAIN … this outcome is unproven, not failure"*
  (`CasRefLedger.cpp:2713-2718`), and recovery adopts a durable object above the frontier
  (`:662-693`) or a straggler occupant (`:790-811`). A checker would see it as an aborted read only
  if the client had been told "failed"; the shipped strings do not say that.
- **`DefiniteFailure` on the append path claims the id was never consumed** (*"cached state is
  unchanged and txn id {}-{} was never used"*, `CasRefLedger.cpp:2678-2681`). That claim rests on
  `classifyConditionalWriteResult` reserving `DefiniteFailure` for malformed / entity-too-large /
  access-denied only (`CasRequestControl.cpp:43-53`, `IO/S3Common.cpp:55-79`), all of which reject
  before storing, and on `earlier_attempt_unresolved` demoting a late definite failure to
  `Unresolved` (`CasRequestControl.cpp:283-288`). Sound as written; it is a standing invariant that
  the classifier must never be widened to an error that a store can return after storing.
- **`nativeConditionalPut` falls back to a `HEAD` for the token when the write returns no ETag**
  (`CasObjectStorageBackend.cpp:165-172`, `NativeStreamingSink::finalize` `:201-208`). Under a
  concurrent writer that would attribute another version's token to this write. Not reported as a
  finding because `WriteBufferFromS3` sets `object_etag` on every successful single-part and
  multipart completion (`IO/WriteBufferFromS3.cpp:691,785`), so the fallback is unreachable for the
  S3 backend; it stays a latent hazard for any future backend that omits the ETag.
- **GC leader liveness after a failed round.** `i_am_leader` is cleared by the round `catch`
  (`CasGcScheduler.cpp:271-275`), which also stops the heartbeat (`:299-300`) while the durable
  lease is still owned by that node. Availability only: the incumbent re-reads `gc/state` at the top
  of every round and yields if deposed (`CasGc.cpp:3140-3153`).

## Coverage

Registers examined end to end: ref log + `_ckpt` frontier + snapshots, namespace catalog, mount
lease, writer epoch, GC lease/state + `gc/hb`, pool meta, plain objects (namespace files,
mountpoint objects), and the emulated-mode variants of all of them. Primitive layer read in full:
`Backend/CasBackend.h`, `Backend/CasObjectStorageBackend.cpp`, `Backend/CasRequestControl.{h,cpp}`,
plus the S3 write path (`IO/WriteBufferFromS3.cpp`) and the error classifiers (`IO/S3Common.cpp`)
that determine what "conflict" and "definite failure" mean on a real backend. Protocol layer read:
`Pool/CasRefLedger.cpp` (append, commit, recovery walk, wedge resolution), `Pool/CasRefCkpt.cpp`,
`Pool/CasRefCatalog.cpp`, `Pool/CasServerRoot.cpp`, `Pool/CasMountRuntime.cpp`,
`Pool/CasPlainObjects.cpp`, `Pool/CasPoolMeta.cpp`, `Pool/CasPartWriteTxn.cpp` (upload/dedup/adopt),
`Parts/PartFolderAccess.cpp` (view cache, rollback), `ContentAddressedTransaction.cpp` (commit),
`ContentAddressedMetadataStorage.cpp` (namespace derivation, backend mode), and the GC lease /
delete paths in `Gc/CasGc.cpp` + `Gc/CasGcScheduler.cpp`.

Not covered here (delegated to sibling audits by scope): blob envelope/offset handling and the read
path's pinning, `Backend::resurrect`, GC fold/graduation arithmetic and `adoptEvidence`, orphan
manifest sweep, decommission and fsck tools, upgrade/format compatibility, and the TLA/Jepsen
harness fidelity question. Twelve classical anomalies were each adjudicated; five are admitted with
concrete interleavings, and eleven distinct not-admitted results are recorded above with their
reasons so the next re-run does not re-litigate them. No dynamic evidence exists in-tree: every CAS
test is deleted in the working tree, so all of the above is static reasoning only.

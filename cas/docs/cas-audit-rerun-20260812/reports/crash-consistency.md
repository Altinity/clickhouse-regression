# crash-consistency -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, working tree as-is
(base `842f2b37b8f`). CAS root `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`
(paths below are relative to that root unless prefixed with `src/`).

Question asked of every multi-step durable protocol: kill `-9` the process (or lose the node) between each
pair of durable effects and classify the residue as (a) consistent, (b) resumable/self-healing, or
(c) permanently broken/leaked. Repair claims are only accepted when a code path can be named that
re-drives the missing step; "nobody" means no such path exists in the tree.

Static reasoning only; no execution. Code-only rule observed: `docs/**` and comments are not treated as
evidence of intent, shipped log/exception strings are.

Cited, not re-reported (sibling audits): repoint is unrevertible and a multi-part commit leaves a published
prefix; `cas-gc-rebuild` is non-resumable; `adoptEvidence` bypasses the condemn marker.

Two structural facts drive most of what follows:

* Transactions are **eager**. Blob bodies, manifests and precommit bindings are durable in the object store
  long before `commit()` returns, so every crash window is a window in which durable side effects exist.
* GC is **reachability-driven, not enumeration-driven**. Its delete set is derived from folded ref-log edges
  (`Gc/CasGc.cpp:2254` fold seal, blob targets), never from listing `cas/blobs/`. Any durable object that is
  never named by a ref-log record is therefore outside GC's field of view by construction. The orphan
  manifest sweep (`Gc/CasOrphanManifestSweep.cpp`) is the one enumerating sweep, and it covers manifests
  only.

## Protocols, durable checkpoints and crash gaps

### 1. Part publish (single part)

Order of durable effects for a normal insert: local scratch staging -> manifest body -> precommit ref-log
record -> blob bodies + blob metas -> commit ref-log record. Blob bodies land **after** the precommit
because `observeAndAdmit` refuses to adopt an existing incarnation before the precommit is durable
(`Pool/CasPartWriteTxn.cpp:280-285`, "EDGE-BEFORE-OBSERVE invariant violated").

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1 | scratch temp file written (local staging) | `ContentAddressedTransaction.cpp:148` (`cleanupPendingTempFiles`) |
| D2 | manifest body PUT | `Pool/CasPartWriteTxn.cpp:507` (`stageManifest`) |
| D3 | precommit owner record appended | `Pool/CasPartWriteTxn.cpp:592-619` |
| D4 | blob body PUT | `Pool/CasPartWriteTxn.cpp:423` |
| D5 | blob meta marker `Clean` | `Pool/CasPartWriteTxn.cpp:427` (`writeFreshMetaClean`) |
| D6 | commit owner record appended | `Pool/CasPartWriteTxn.cpp:657` (`promote`) |
| D7 | ckpt/snapshot advance (async) | `Pool/CasRefLedger.cpp:2937` |

| Gap | Post-crash state | Repair |
|---|---|---|
| before D1 | nothing | n/a |
| D1..D2 | orphan `*.tmp` under `<path>/disks/<name>/cas_scratch/` | **nobody** -- see crash-consistency-6 |
| D2..D3 | manifest body with no precommit, invisible to readers | orphan manifest sweep, `Gc/CasOrphanManifestSweep.cpp:389` (subject to the epoch floor, crash-consistency-3) |
| D3..D4 | durable precommit naming blobs that do not exist; readers see only committed refs | stale-precommit sweep on the next mount (`Pool/CasRefLedger.cpp:857` sets `needs_stale_precommit_sweep`, consumed at `:3093-3107`, executed at `:3132`), then the manifest is orphan-swept. Self-healing, lazy. |
| D4..D5 | blob **body without meta**, unreferenced once the precommit is swept | **nobody** -- see crash-consistency-2 |
| D5..D6 | complete part content + precommit, no committed ref | same as D3..D4: precommit swept, manifest swept, blob bodies collectable only if some ref-log edge ever named them |
| D6..D7 | committed ref durable, checkpoint behind | recovery walk replays from the last ckpt (`Pool/CasRefLedger.cpp:525`); correct, only truncation is deferred |

`promote` fails closed rather than committing a torn part: absent manifest body
(`Pool/CasPartWriteTxn.cpp:643-646`), body/ref mismatch (`:648-651`), precommit binding no longer the live
owner (`:668-673`), and any blob leaf that is neither tokened by this txn nor a trusted adopt
(`:675-685`, "a pending upload never completed; failing closed"). This is the strongest crash-safety
property in the protocol: a crash can leak, but it cannot publish a part whose blobs were never uploaded.

Re-running the same insert after a crash self-repairs a missing meta: `observeAndAdmit` back-fills it
(`Pool/CasPartWriteTxn.cpp:287-292`, `CASMetaAdoptBackfill`). The leak in crash-consistency-2 is exactly
the case where nothing ever re-references the body.

### 2. Multi-part transaction commit

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1..Dn | per-part `stageManifest` + `precommitAdd` | `ContentAddressedTransaction.cpp:262-263`, `:297-298` |
| C1..Cn | per-part promote, sequentially | `ContentAddressedTransaction.cpp` commit loop -> `Parts/PartFolderAccess.cpp` |

Crash after `Ck` and before `Ck+1` leaves parts 1..k published and k+1..n not. Compensation exists only as
in-process unwinding in the `catch` of `commit()`; a `kill -9` skips it entirely, and repoints are not
revertible at all. Already reported by a sibling audit (published prefix / unrevertible repoint) -- cited
here because it is the dominant multi-part crash residue and not re-scored.

### 3. RENAME TABLE / `moveDirectory` across namespaces

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1..Dn | per-ref `republishRef(from_ns/ref -> to_ns/ref)`, each a stage+precommit+promote | `ContentAddressedTransaction.cpp:863`, `Parts/PartFolderAccess.cpp:419` |
| Dn+1 | source refs dropped | same loop |
| Dn+2 | `dropNamespace(from_ns)` | `ContentAddressedTransaction.cpp:874` -> `Pool/CasRefLedger.cpp:3396` |

Every gap is exposed. See crash-consistency-1.

### 4. DROP table / partition, namespace removal

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1 | catalog entry `Live` -> `Removing` | `Pool/CasRefCatalog.cpp:227` (`beginRemoving`), called at `Pool/CasRefLedger.cpp:3492` |
| D2 | terminal `RemoveNamespace` ref-log record | `Pool/CasRefLedger.cpp:3396` (`dropNamespaceImpl` tail) |
| D3 | GC folds the removal, produces cleanup evidence | `Gc/CasGc.cpp:2254` |
| D4 | janitor deletes ref-log/ckpt/namespace-file objects | `Gc/CasNamespaceJanitor.cpp` (`runOnePage`, cursor in `GcMaintenanceState`) |
| D5 | catalog row deleted | `Gc/CatalogLifecycleReconciler.cpp` via `Gc::drainCompletedRemoving`, `Gc/CasGc.cpp:3195` |

| Gap | Post-crash state | Repair |
|---|---|---|
| D1..D2 | catalog says `Removing`, ref table still fully live; writes refused, re-creation refused | **nobody inside CAS** -- see crash-consistency-8 |
| D2..D3 | terminal record durable, content still present | next GC round; correct |
| D3..D4 | evidence exists, physical objects still present | janitor resumes from its persisted cursor; correct |
| D4..D5 | objects gone, catalog row lingers `Removing` | next `drainCompletedRemoving`; correct |

D2..D5 is a genuinely well-built resumable chain: every step is re-derived from persisted state
(fold seal, janitor cursor, catalog row) rather than from process memory.

### 5. Relink / adopt handshake between two servers

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1 | receiver stages manifest + precommits | `ContentAddressedMetadataStorage.cpp:1624-1625` -> `Parts/PartFolderAccess.cpp:401-402` |
| D2 | receiver adopts/uploads blob evidence | `Pool/CasPartWriteTxn.cpp:478` |
| D3 | sender answers `confirmExactRef` | `ContentAddressedMetadataStorage.cpp:1465-1500` |
| D4 | receiver promotes | `Pool/CasPartWriteTxn.cpp:633` |

Crash on the receiver anywhere in D1..D4 leaves a stale precommit plus a staged manifest and nothing
committed; the fetch is retried by the replication layer with a fresh build prefix, and the debris is
reclaimed by the same stale-precommit + orphan-manifest pair as the part-publish D3..D4 gap. Precommits are
keyed by `(ref, manifest_ref)` (`Pool/CasPartWriteTxn.cpp:668`), so a stale one does not block the retry --
no wedge. Crash on the **sender** between D3 and D4 is harmless: the answer is advisory, and the receiver
re-verifies the manifest body at promote. Failure modes that are not crashes (body-absent precommit, ref
conflict) degrade to a byte fetch (`ContentAddressedMetadataStorage.cpp:1630-1634`).

### 6. GC round phases

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1 | lease acquired / heartbeat floor published | `Gc/CasGc.cpp:467` (`computeHeartbeatFloor`) |
| D2 | new generation's fold seal + blob targets | `Gc/CasGc.cpp:2254` (`putDeterministicArtifact(foldSealKey(new_generation, attempt))`) |
| D3 | condemn meta markers / `delete_pending` | `Gc/CasGc.cpp:92`, `:706` |
| D4 | blob bodies deleted | `Gc/CasGc.cpp:~660` |
| D5 | condemned metas deleted | `Gc/CasGc.cpp:662` (`deleteConfirmedMeta`) |
| D6 | `gc/state` CAS commit | `Gc/CasGc.cpp:804` |
| D7 | superseded generations pruned | `Gc/CasGc.cpp:2456` (`pruneSupersededGenerations`) |

| Gap | Post-crash state | Repair |
|---|---|---|
| D1..D2 | nothing durable beyond a fenced mount observation | next round |
| D2..D6 | a sealed generation exists that `gc/state` does not point at | next successful round adopts or prunes it via `probeGenerationForSeal` (`Gc/CasGc.cpp:1106-1155`) + `pruneSupersededGenerations`. Correct, but see crash-consistency-7 for the accumulation case. |
| D4..D5 | `meta_without_body` | idempotent: the blob is still `delete_pending` in the retired set, the next round re-deletes (head miss = Deleted) and re-schedules `deleteConfirmedMeta`. Self-healing. |
| D6..D7 | stale generation directories | next round's prune |

The two-phase condemn/graduate design means a crash never turns a *live* blob into a deleted one: deletion
requires a condemn marker published in an earlier round plus exact-token delete.

### 7. Ref-log checkpoint / snapshot / compaction

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1 | snapshot object PUT | `Pool/CasRefLedger.cpp:2937-3035` |
| D2 | ckpt contribution CAS advanced to the snapshot frontier | `Pool/CasRefLedger.cpp:3035` (`publishCkptContribution`) |
| D3 | superseded ref-log entries/snapshots deleted | `Gc::cleanupRefObjects` |

Crash D1..D2 leaves a snapshot object that no ckpt points at. Snapshot encoding is deterministic
(`Formats/CasRefSnapshotFormat.cpp` carries no timestamps), so a retry re-PUTs identical bytes and
`resolveByExactGet` resolves `Committed` -- the retry is safe. What is missing is a *driver* for the retry
on a namespace that stops receiving writes; see crash-consistency-5.

### 8. Mount claim / renew / release, writer epoch allocation

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1 | owner anchor claimed | `Pool/CasServerRoot.cpp:105` (`claimOwnerOrThrow`) |
| D2 | writer epoch allocated (`epoch` object bumped) | `Pool/CasServerRoot.cpp:161` (`allocateWriterEpoch`) |
| D3 | mount lease published, keeper renewing | `Pool/CasPool.cpp:384-395`, `MountLeaseKeeper` |
| D4 | per-mount S3 staging swept | `ContentAddressedMetadataStorage.cpp:607` (`sweepOwnMountStaging`) |

Every gap here is safe by construction: epoch allocation is monotone and a crash between D2 and D3 only
burns an epoch number; a crash after D3 leaves a lease that expires and is either reclaimed by the same
server on restart (fresh, higher epoch) or GC-fenced (`Pool/CasServerRoot.cpp:455`). Nothing published
under the dead epoch can be committed afterwards because the fence generation is checked on every write
(`CasMountRuntime::checkFenceOrThrow`). The residual problem is not the lease itself but what the dead
lease's watermark pins -- crash-consistency-3.

### 9. Pool creation / validation

`Pool::open` performs a bootstrap residual check and initialises an empty catalog
(`CasRefCatalog::initializeEmptyForNewPool`) before mounting (`Pool/CasPool.cpp:384`). A crash mid-bootstrap
leaves a partially-populated pool prefix; the next `open` re-runs the residual check and either completes
the bootstrap or fails loud. No finding.

### 10. Decommission / drop pool member

| # | Durable checkpoint | Anchor |
|---|---|---|
| D1 | victim namespaces dropped, debris swept | `Tools/CasDecommission.cpp:97` ff. |
| D2 | mount farewell captured, epoch captured under admin claim | `Tools/CasDecommission.cpp:242-294` |
| D3 | `mount` object deleted | `Tools/CasDecommission.cpp:297` |
| D4 | `epoch` object deleted | `Tools/CasDecommission.cpp:298` |
| D5 | owner anchor tombstoned (`retired_at_ms`) | `Tools/CasDecommission.cpp:333-341` |

Gap D3..D5 is unrecoverable by re-running the tool. See crash-consistency-4.

### 11. Fsck

`runFsck` is read-only: it classifies (`FsckClass`) and counts, and returns a `FsckReport`
(`Tools/CasFsck.h:114`). There is no repair entry point anywhere in `Tools/`. It is therefore a detector
for crash residue, never a repair -- and it does not detect all of it (crash-consistency-9).

## Findings

### crash-consistency-1 -- RENAME TABLE across namespaces has no atomicity and no reconciler (High)

- **Anchor**: `ContentAddressedTransaction.cpp:846-874` (`moveDirectory`), per-ref `republishRef` at `:863`,
  terminal `dropNamespace(from_ns)` at `:874`; `Parts/PartFolderAccess.cpp:419-431`.
- **Crash point**: `kill -9` after the loop has republished refs 1..k of n into `to_ns` (each already
  promoted and durable) and before the loop finishes, or after the loop and before `dropNamespace(from_ns)`
  returns.
- **Resulting state**: refs 1..k are committed in `to_ns` *and* still committed in `from_ns` (republish
  stages+precommits+promotes into the destination; the source drop is a separate ref-log record).
  Both namespaces are catalog-`Live`. If the crash lands after all refs moved but before the source
  namespace drop, `from_ns` survives as a fully-populated live namespace that no table references.
- **Repair mechanism or absence**: none. `Gc/CatalogLifecycleReconciler.cpp` only advances entries already
  in `Removing`; the janitor (`Gc/CasNamespaceJanitor.cpp`) only deletes objects of dead `life_id`s; the
  orphan manifest sweep protects everything a live namespace's ref table names
  (`Gc/CasOrphanManifestSweep.cpp:321-371`). A `Live` catalog entry with committed refs is, to every sweep
  in the tree, a healthy namespace. No startup path re-drives an interrupted rename -- `Pool::open`
  reconciles leases and precommits, not cross-namespace ref topology.
- **Evidence**: the destination-side guard is a *conflict* check, not a rollback: `republishRef` refuses
  when the destination is "already committed with different content" (`Parts/PartFolderAccess.cpp:431`),
  which means a re-issued rename over a partially-completed one is accepted for the already-moved refs and
  proceeds -- but nothing issues that re-run after a crash, because the ClickHouse-side rename either
  completed (metadata renamed) or did not, independently of how far the CAS loop got. Consequence: leaked
  namespace holding a full copy of the table's refs, and duplicate refs pointing at the same content in two
  live namespaces, indefinitely.

### crash-consistency-2 -- blob body is durable before its meta marker, and no GC phase enumerates bodies (Medium)

- **Anchor**: `Pool/CasPartWriteTxn.cpp:423-429` -- `streamIfAbsent()` returns `Done` (body durable), then
  `writeFreshMetaClean()` writes `cas/meta/<hash>`; also `:463-465` and `:471-474` on the resurrect paths.
- **Crash point**: `kill -9` between the body PUT acknowledgement and the meta PUT, for a blob whose
  enclosing build never commits (the precommit is later swept) and whose content hash is never inserted
  again.
- **Resulting state**: `cas/blobs/<hash>` exists with a valid envelope, no `cas/meta/<hash>`, and no
  ref-log record anywhere names it.
- **Repair mechanism or absence**: none in the incremental path. GC's delete set is derived from folded
  manifest edges; no code lists `cas/blobs/` (`layout.blobMetaKey` has no listing counterpart anywhere in
  `Gc/`). The orphan sweep is manifest-only (`Gc/CasOrphanManifestSweep.cpp:489`,
  `list(layout.casManifestsPrefix(), ...)`). Only `cas-gc-rebuild` could reclaim it, and a sibling audit
  established that rebuild is non-resumable.
- **Evidence**: the self-heal that *does* exist proves the gap is known to the write path -- a later insert
  of the same content back-fills the missing meta (`Pool/CasPartWriteTxn.cpp:287-292`,
  `ProfileEvents::CASMetaAdoptBackfill`). That path only triggers if the same hash is written again.
  Otherwise the bytes are a permanent, silent capacity leak. Fsck sees it but does not raise: it is counted
  into `report.body_without_meta` (`Tools/CasFsck.cpp:827-829`) and classified `Unaccounted`
  (`:753`, `:805`), neither of which is in `kFsckHardFindings` (`Tools/CasFsck.h:90-96`), so
  `FsckReport::clean()` stays true.

### crash-consistency-3 -- a permanently lost node pins its own manifest debris as unreclaimable (Medium)

- **Anchor**: `Gc/CasOrphanManifestSweep.cpp:373-387` (`prefixEligible`), reading the victim's mount lease
  via `floorForNamespace` (`:40-56`); fence-out at `Pool/CasServerRoot.cpp:455`
  (`computeHeartbeatFloor`).
- **Crash point**: node loss (not process restart) while builds with prefix `(writer_epoch = E,
  build_sequence >= min_active)` are in flight; the node never comes back and no decommission is run.
- **Resulting state**: the mount lease object stays at `(writer_epoch = E, min_active = M)`. GC eventually
  marks it `gc_fenced` so the dead writer can never commit again. But `prefixEligible` compares the debris
  prefix against that same lease: `prefix.writer_epoch == E` and `min_active <= prefix.build_sequence`
  returns `false`, forever. Every staged manifest of every in-flight build at the moment of node loss is
  permanently retained.
- **Repair mechanism or absence**: `prefixEligible` has no `gc_fenced` branch -- fencing a mount out for
  liveness does not raise its watermark. The only path that lifts the floor is a new mount by the same
  `srid` (higher epoch, so the `prefix.writer_epoch < w.writer_epoch` branch at `:380-381` fires) or
  `decommissionPoolMember`, which writes a farewell with `min_active = max`
  (`Tools/CasDecommission.cpp:279`). Both require operator action for a node that is gone.
- **Evidence**: the retain reason strings distinguish coverage/hold/seal cases
  (`Gc/CasOrphanManifestSweep.cpp:336-366`), but this case never reaches them -- `sweepNamespace` returns 0
  at `:392` before any premise is evaluated, so the retention is not even surfaced in the sweep's warning
  list. Silent by construction.

### crash-consistency-4 -- decommission crash between control-object deletion and owner tombstone is not repairable by re-running decommission (Medium)

- **Anchor**: `Tools/CasDecommission.cpp:297` (delete `mount`), `:298` (delete `epoch`), `:333-341`
  (tombstone `owner`); capture precondition at `:270-298`.
- **Crash point**: `kill -9` after both `deleteSlotObject` calls succeed and before
  `putOverwriteControlled` on the owner key lands.
- **Resulting state**: `mount` and `epoch` are gone; the owner anchor still exists with `retired_at_ms`
  unset, i.e. the slot still looks claimed and un-retired.
- **Repair mechanism or absence**: re-running the tool cannot finish it. The tombstone is gated on
  `captures_match`, which requires reading both the epoch object and the mount farewell and validating
  `mount.writer_epoch == epoch.next_writer_epoch - 1` (`:270-294`). With both objects deleted, both
  captures fail ("slot capture failed: ... is absent under the admin claim", `:247`, `:262`),
  `captures_match` is false, and the code never reaches `:333`. `report.slot_removed` is permanently false.
- **Evidence**: worse than a cosmetic leftover, because the epoch object is what makes epoch allocation
  monotone. If the decommissioned server is ever started again against this pool, `claimOwnerOrThrow`
  (`Pool/CasServerRoot.cpp:105`) sees a matching, non-retired owner and `allocateWriterEpoch`
  (`:161`) has no epoch object to bump -- the member re-mounts from a reset epoch counter and re-issues
  `RefTxnId`s in a range the fold seals already record as consumed. The liveness recheck at
  `Tools/CasDecommission.cpp:324-328` guards the concurrent-successor case but not the crash case.

### crash-consistency-5 -- snapshot published without ckpt advance is not re-driven on a quiescent namespace (Medium)

- **Anchor**: `Pool/CasRefLedger.cpp:2937-3035` (`tryPublishSnapshotAndAdvanceCheckpointOnceOnRuntime`),
  ckpt CAS at `:3035`; driver at `:2765`, invoked from the write path.
- **Crash point**: `kill -9` after the snapshot object PUT is durable and before `publishCkptContribution`
  commits, on a namespace that receives no further writes (a finished table, an append-once dataset).
- **Resulting state**: a snapshot object exists that no ckpt references; the ckpt frontier stays where it
  was; the ref-log tail below the snapshot is never truncated. Correctness is unaffected -- the recovery
  walk replays from the older ckpt (`Pool/CasRefLedger.cpp:525`).
- **Repair mechanism or absence**: the retry is driven off the write path
  (`Pool/CasRefLedger.cpp:2765`, inside a mutation), and `tryPublishSnapshotAndAdvanceCheckpointOnce` is
  exposed on `Pool` (`Pool/CasPool.h:239`) but has no background caller. A namespace that stops being
  written keeps replaying an unbounded ref-log prefix on every mount and pays the untruncated storage
  forever.
- **Evidence**: recovery cost is proportional to the un-truncated tail, and the tail also gates
  `Gc::cleanupRefObjects`, so this compounds: the objects the snapshot was meant to retire stay reachable
  from the ckpt-derived retention window.

### crash-consistency-6 -- local scratch staging is never swept at startup, unlike S3 mount staging (Medium)

- **Anchor**: scratch root created but never enumerated at
  `src/Disks/DiskObjectStorage/MetadataStorages/MetadataStorageFactory.cpp:236-238`
  (`<path>/disks/<name>/cas_scratch/`); the only cleaner is in-process
  (`ContentAddressedTransaction.cpp:148`, called at `:103` dtor, `:322`, `:350`).
- **Crash point**: `kill -9` while any transaction holds staged temp files -- i.e. after `writeFile` spilled
  a blob or an inline overflow to scratch and before `commit()`/rollback.
- **Resulting state**: `*.tmp` files persist on the local disk across restarts, unreferenced.
- **Repair mechanism or absence**: none. `startup()` creates the directory and moves on. The asymmetry is
  explicit: when `staging_backend == S3` the equivalent debris *is* swept at mount
  (`ContentAddressedMetadataStorage.cpp:596-607` -> `Pool/CasServerRoot.cpp:1140`,
  `sweepOwnMountStaging`), and that sweep is additionally skipped when conditional copy is unsupported
  (`:600-607`), in which case staging silently falls back to local -- the unswept path.
- **Evidence**: this is the only local (non-object-store) state the audit found that survives a crash, and
  it is also the only local state that does *not* need to survive: all authority lives in the object store,
  so the correct behaviour is to purge it at mount. Nothing else requires an fsync -- the server UUID file
  is ClickHouse-managed and its loss is fail-loud through `claimOwnerOrThrow`
  (`Pool/CasServerRoot.cpp:105`).

### crash-consistency-7 -- GC seals a generation before committing gc/state; repeated crashes accumulate orphan generations (Medium)

- **Anchor**: `Gc/CasGc.cpp:2254` (`putDeterministicArtifact(layout.foldSealKey(new_generation, attempt))`)
  vs the commit at `:804` (`backend.casPut(layout.gcStateKey(), ...)`); rebuild has the same shape at
  `:2980` / `:2987`.
- **Crash point**: `kill -9` after the new generation's fold seal and blob-target objects are durable and
  before the `gc/state` CAS.
- **Resulting state**: `gc/gen/<new_gen>/` exists and is sealed; `gc/state` still names the previous
  generation. Correctness is preserved -- readers and sweeps use the adopted generation from `gc/state`
  (`Gc/CasOrphanManifestSweep.cpp:80-91` reads the seal *through* `gc/state`).
- **Repair mechanism or absence**: the next *successful* round reclaims it -- `probeGenerationForSeal`
  (`Gc/CasGc.cpp:1106-1155`) detects the orphan seal and `pruneSupersededGenerations` (`:2456`) deletes the
  directory. The gap is that reclamation is tied to completion: a round that keeps crashing (OOM in fold,
  restart loop) writes a fresh sealed generation each attempt and prunes none, so the `gc/gen/` prefix grows
  by one sealed generation per crashed round while `gc/state` never moves.
- **Evidence**: the seal is written with `putDeterministicArtifact`, so re-running the same round rewrites
  identical bytes for the same `(generation, attempt)`; accumulation requires the attempt or generation
  number to advance across restarts, which it does whenever the previous state is re-read and a new attempt
  is begun.

### crash-consistency-8 -- namespace stuck in Removing with a live ref table refuses writes and refuses re-creation (Medium)

- **Anchor**: `Pool/CasRefLedger.cpp:3492` (`CasRefCatalog::beginRemoving`, durable `Live -> Removing`)
  vs the terminal `RemoveNamespace` append later in `dropNamespaceImpl` (`:3396` ff.);
  `Pool/CasRefCatalog.cpp:227`.
- **Crash point**: `kill -9` after the catalog CAS to `Removing` lands and before the terminal ref-log
  record is appended.
- **Resulting state**: the catalog says `Removing` while the ref table still holds every committed ref.
  Writes to the namespace are refused (the positive-append path admits only `Live` entries and converts the
  attempt into a retry-later), and re-creating the same namespace is refused because a `Removing` entry
  blocks the birth path. Reads still work. The data is intact but the namespace is inert.
- **Repair mechanism or absence**: no CAS-internal driver. GC cannot finish the removal: without the
  terminal record the fold produces no cleanup evidence, so `drainCompletedRemoving`
  (`Gc/CasGc.cpp:3195`) will not delete the catalog row -- it can only keep re-observing it and emitting a
  stuck-removal warning. The only repair is a re-issued DROP, which takes the "already `Removing`" branch
  and appends the terminal record.
- **Evidence**: exposure depends on the caller. A `DROP TABLE` reaching this code has usually already
  persisted its intent on the ClickHouse side, so the drop is retried after restart and the state resolves.
  The dangerous callers are the ones with no retry driver: the `dropNamespace(from_ns)` tail of
  `moveDirectory` (`ContentAddressedTransaction.cpp:874`) and `removeRecursive` on a path whose ClickHouse
  intent was not yet durable. In those cases the namespace stays inert until an operator issues a DROP.

### crash-consistency-9 -- fsck is report-only and its clean() verdict excludes the two crash-residue counters (Low)

- **Anchor**: `Tools/CasFsck.h:114` (`runFsck` returns a report; no repair function exists in `Tools/`),
  `Tools/CasFsck.h:90-112` (`kFsckHardFindings` = dangling, corrupted_runs, stale_edge, chain_broken,
  lifeless_keys), `Tools/CasFsck.cpp:819-829` (`body_without_meta`, `meta_without_body` computed).
- **Crash point**: any of crash-consistency-2 (body without meta) or a GC crash in the D4..D5 gap
  (meta without body).
- **Resulting state**: both counters are populated and both are excluded from `FsckReport::clean()`.
- **Repair mechanism or absence**: n/a -- the finding is about detection, not repair. An operator running
  fsck after a crash gets `clean == true` on a pool that is leaking bodies.
- **Evidence**: the `static_assert` at `Tools/CasFsck.h:98-104` documents that omission from the exit set is
  intentional only in the `stale_edge` style (documented reason plus a compensating soak assert); the two
  body/meta counters are not in the set at all, so their omission carries neither. `meta_without_body` is
  genuinely transient (self-heals next round), `body_without_meta` is not.

## By-design / info

* **Fail-closed promote.** The publish protocol cannot commit a part whose blobs are missing: four separate
  preconditions are checked at promote (`Pool/CasPartWriteTxn.cpp:643-685`), each throwing retry-later or
  logical-error rather than committing. Crash residue is leak-shaped, not corruption-shaped.
* **Two-phase blob deletion.** Condemn in round N, exact-token delete in round N+1, meta delete after
  (`Gc/CasGc.cpp:92`, `:662`, `:706`). Every intermediate crash state is re-derivable from the retired set,
  and a crash can never delete a blob that a live manifest reaches.
* **Idempotent conditional writes.** `putIfAbsentControlled` / `resolveByExactGet` make a crashed-and-retried
  PUT resolve to `Committed` when the bytes match, which is why the snapshot, fold-seal and ckpt writes are
  all safe to re-drive. All of them are written through deterministic encoders (no timestamps in
  `Formats/CasRefSnapshotFormat.cpp`).
* **Recovery walk + stale-precommit sweep.** The single most load-bearing self-heal: mount-time recovery
  sets `needs_stale_precommit_sweep` (`Pool/CasRefLedger.cpp:857`), and the first ledger operation on the
  namespace drops precommit bindings from dead epochs (`:3093-3107`, `:3132`). It is lazy (nothing happens
  on a namespace that is never touched again) but it is correct.
* **Janitor and reconciler are cursor-driven**, not memory-driven, so namespace teardown resumes across
  restarts from persisted state (`Gc/CasNamespaceJanitor.cpp` cursor in `GcMaintenanceState`,
  `Gc/CatalogLifecycleReconciler.cpp`).
* **Startup/mount reconciliation, precisely.** What it does: claim/validate the owner anchor, allocate a
  higher writer epoch, publish a lease, run the ref-table recovery walk from the last ckpt, arm the stale
  precommit sweep, sweep this mount's S3 staging prefix (S3 staging only), drain writer cleanup duties
  (`Pool/CasPool.cpp:789-848`). What it cannot detect: an interrupted cross-namespace rename (nothing
  compares namespaces), an unreferenced blob body (nothing lists `cas/blobs/`), local scratch debris
  (nothing lists the scratch dir), a namespace stranded in `Removing` (it is a legal state), and an orphan
  sealed GC generation (that is GC's job, not the mount's).
* **Local durable state.** Only the scratch directory. Nothing in CAS requires an `fsync` for correctness --
  all authority is object-store-resident, and the pool refuses to mount rather than guess if the owner
  anchor disagrees with the server UUID (`Pool/CasServerRoot.cpp:105`).

## Coverage

Walked with anchors: part publish (blob body/meta, manifest, precommit, promote, ckpt), multi-part commit
(deferred to the sibling finding), RENAME/`moveDirectory`, DROP/namespace removal through janitor and
catalog reconciler, relink/adopt on both sender and receiver, GC round phases D1..D7 including the rebuild
variant, ref-log snapshot/ckpt/compaction, mount claim/renew/fence and epoch allocation, pool bootstrap,
decommission, fsck.

Not covered: anything requiring execution (real S3 semantics under partial PUT, multipart upload residue in
the object store itself, `promoteStaged` copy atomicity on a specific vendor); crash behaviour of the
ClickHouse-side metadata/replication layers that call into CAS, except where the absence of a retry driver
is the finding (crash-consistency-8); and the encrypted-over-CAS and cross-pool attach paths, which other
audits in this run own.

Nine findings: 1 High, 7 Medium, 1 Low.

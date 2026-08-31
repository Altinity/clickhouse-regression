# crash-consistency -- fresh audit 2026-08-31

## Scope

- Kill `-9` (or equivalent node loss) between each pair of durable effects in
  the assigned multi-step protocols: `RENAME` / `moveDirectory`, blob body vs
  meta, precommit vs promote, `gc/state` vs fold seal, shutdown drain
  (`205af29`). Pin `ceee42c51a06cb05e2c9a2d811ef7e1726825552`.
- Files/dirs examined: `ContentAddressedTransaction.cpp` (`moveDirectory` /
  `commit` / `publishStaging`), `Pool/CasPartWriteTxn.cpp` (`ensureBlobPresent`
  / `precommitAdd` / `promote` / `abandon`), `Pool/CasBlobMeta.cpp`,
  `Pool/CasRefLedger.cpp` (stale-precommit sweep, recovery walk, `commitRefChunk`
  log-then-ckpt, `drainRefLanesForShutdown`), `Gc/CasGc.cpp` (`putDeterministicArtifact`
  fold seal, `gc/state` CAS, `pruneSupersededGenerations`),
  `ContentAddressedMetadataStorage.cpp` (`stopAndDrainForTeardown`),
  `Pool/CasPool.cpp` (`~Pool` / `stopAndDrainDetachedWork` / `finishTeardown`),
  `Pool/CasDetachedWork.{h,cpp}`.
- Repair claims require a named re-drive path. "Nobody" means no such path
  exists in the tree.
- Explicitly out of scope: in-process races (`concurrency`); two live actors
  (`interleaving` / `jepsen-anomaly`); rebuild resumability (`gc-rebuild-feature`).

## Findings

### crash-consistency-1 -- RENAME TABLE / cross-namespace `moveDirectory` has no journal (Medium)

- Anchor: `ContentAddressedTransaction.cpp:1248-1308` (`moveDirectory`) at ceee42c
- Trigger: `RENAME TABLE` (or any path pair that `parseTableUuid` classifies as
  two table dirs) on a CA disk. The function republishes every ref, copies
  namespace files, then `dropNamespace(from_ns)`. A crash after some
  `republishRef`s and before `dropNamespace` leaves the table split across
  two namespaces.
- Evidence: the shipped comment states the contract (`:1264-1272`): no native
  directory rename, no durable move-journal, no in-call compensation. Re-drive
  is idempotent (`republishRef` no-ops when the source is already gone;
  `dropNamespace` of an empty life is a no-op). Nothing at mount or GC
  compares the two namespaces or finishes a partial rename. Readers of the
  *destination* UUID see a prefix of parts; readers of the *source* UUID see
  the remainder. Nothing is physically deleted until the source life is
  dropped, so this is split visibility, not blob loss.
- Notes: same residual as CAS-006. Atomic-database `RENAME TABLE` is
  metadata-only and does not take this path; Ordinary (deprecated) and any
  caller that actually `moveDirectory`s two table UUID dirs do. Not High:
  re-drivable, no physical delete of unreplicated content.

### crash-consistency-2 -- blob body is durable before its meta sibling (Medium)

- Anchor: `Pool/CasPartWriteTxn.cpp:415-446` (`backend().publishBlob` then
  `reconcileMetaClean`) at ceee42c
- Trigger: crash after `publishBlob` returns and before `reconcileMetaClean`
  installs a `Clean` meta (or after `putMetaIfAbsent` is lost). The body key
  exists; `cas/blobs/<hash>.meta` does not.
- Evidence: the write protocol is now mandatory HEAD → adopt present
  non-condemned body, else unconditional publish, then meta
  (`:327-468`). That closed the old `putIfAbsentStream` / `promoteStaged`
  window; it did not close body-before-meta. GC fold never LISTs `cas/blobs/`
  — it deletes only from folded edges + `delete_pending`. A body with no
  meta and no surviving ref-log edge is invisible to regular GC. A later
  INSERT that HEADs the same hash back-fills meta (`CASMetaAdoptBackfill`,
  `:364-369`). If nothing ever re-references the hash, the body remains
  until an operator `fsck` `unaccounted` row.
- Notes: same residual as CAS-075 / R4. Leak, not silent corruption.
  `promote` still fails closed if a blob leaf has no dependency proof
  (`:827`).

### crash-consistency-3 -- multi-part `commit` crash leaves a published prefix (Medium)

- Anchor: `ContentAddressedTransaction.cpp:518-536` at ceee42c
- Trigger: a transaction with N>1 staged parts. Crash after `publishStaging`
  of part *k* and before part *k+1*. The in-process `dropRefIfMatches`
  compensation (`:533-536`) does not run.
- Evidence: each `promote` is a durable ref-log append. There is no
  all-or-nothing multi-ref record and no restart reconciler that looks for
  "this disk transaction's leftover refs". The leftover parts are
  well-formed and readable; the caller's MergeTree transaction will retry
  or abort independently. Same G1a residual as `jepsen-anomaly-1`, scored
  here because `kill -9` is the mechanism.
- Notes: CAS-005 residual. Common INSERT is one part.

## By-design / info / non-actionable

- **Precommit vs promote is self-healing.** Order is still manifest body →
  `precommitAdd` → blob materialize → `promote` (`ContentAddressedTransaction.cpp:424-436`,
  `CasPartWriteTxn.cpp:612-725`). Crash after precommit, before promote:
  readers see only `getCommitted()` so the part is invisible;
  `needs_stale_precommit_sweep` is set on recovery (`CasRefLedger.cpp:1255`)
  and `sweepStalePrecommitsForRead` / the mount sweep remove the exact
  precommit binding; the orphan-manifest sweep then takes the body. Crash
  after promote, before async snapshot: recovery walks from `_ckpt`
  (`commitRefChunk` publishes `committed_through = id` before installing
  the local table, `:3166-3170`, `:3750-3771`). A log object above a lost
  ckpt is `NeedsRecovery`, not a committed-but-unreadable ref.
- **`gc/state` vs fold seal: seal first, then one CAS; prune collects the
  rest.** `putDeterministicArtifact(foldSealKey)` runs in `fold_seal_write`
  (`CasGc.cpp:3181-3193`); `gc/state` is the single later CAS (`:941`). A
  crash after the seal leaves an unadopted `gc/gen/<g>/attempt/<a>/`
  object. `pruneSupersededGenerations` wholesale-deletes aged
  `gc/gen/<g>/` prefixes including unaccepted attempts (`:3476-3477`).
  Not a leak of an adopted generation.
- **Shutdown drain (`205af29`) fails closed.** `stopAndDrainForTeardown`
  moves the pool out from under `pointer_mutex`, stops GC, then
  `stopAndDrainDetachedWork(attempt_timeout_ms + lease_safety_margin_ms)`
  (`ContentAddressedMetadataStorage.cpp:920-978`). A timeout increments
  `CASDetachedWorkDrainTimeouts` and proceeds; it does **not** destroy the
  `Pool` while a `DetachedTaskLease` still holds `shared_from_this`.
  `~Pool` then `drainRefLanesForShutdown` and `finishTeardown(drained)`
  (`CasPool.cpp:925-942`). If ref lanes are wedged or the drain timed out,
  the clean-release marker is skipped (`CasMountRuntime.cpp:1146-1151`)
  and the next mount treats the end as unclean. Detached tasks are
  forbidden from capturing their own `Pool` pointer (`CasDetachedWork.h:45-47`).
- **`abandon` of an uncertain precommit is exact-binding, not a body delete.**
  `PartWriteTxn.cpp:1018-1043` appends a precommit-removal op; a crash
  mid-abandon leaves either the precommit (swept later) or the removal.

## Closed-since-2026-08-12

- **crash-consistency-7 (Medium, seal-before-`gc/state` accumulates orphan
  generations).** Not re-raised as a defect: HEAD still writes the seal
  first, but `pruneSupersededGenerations` is the regular collector of
  unadopted attempts (CAS-076: not a bug).
- **crash-consistency-3 (Medium, lost node pins its own manifest debris)
  for FREEZE/shadow.** Those namespaces now carry `server_root_id`, so
  `floorForNamespace` can resolve a mount floor. A *permanently* lost srid
  still pins its debris until decommission — control #9, not a new gap.
- **`freezeRemote` without a CA transaction (CAS-058).** Closed by
  `84b30f6b0d9` (`DataPartStorageOnDiskBase.cpp:687-744`).

## Coverage

- Reviewed: part publish D1–D7 (scratch, manifest, precommit, body, meta,
  promote, ckpt); multi-part `commit`; `moveDirectory` / RENAME TABLE;
  DROP / `dropNamespace`; relink prepare/promote (cited, not re-scored);
  GC seal vs `gc/state` vs generation prune; shutdown detached drain +
  ref-lane drain + clean-release skip.
- N-A: multipart upload residue inside a vendor SDK (no CAS-owned
  accounting; `_probe/` excluded from bootstrap).
- Deferred: local scratch sweep at startup (still nobody; cost-only
  residual, previously crash-consistency-6); fsck `clean()` excluding
  meta/body counters (Low, previously crash-consistency-9).

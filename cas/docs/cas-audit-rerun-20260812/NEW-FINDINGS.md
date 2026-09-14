# CAS audit 2026-08-12 -- consolidated findings

Deduplicated master list for the fresh 39-audit static re-run of the ClickHouse CAS
(content-addressed storage) feature. Every entry derives from at least one report in
[`reports/`](reports/); nothing here is inferred beyond what those reports anchor to code.

Target pin (see [`README.md`](README.md)): repo `/Volumes/workspace/altinity-clickhouse/ClickHouse`,
branch `cas-code-only-strip`, base commit `842f2b37b8f`, working tree as of 2026-08-12T09:40Z
(base plus the uncommitted comment/doc strip). Code-only rules: intent inferred from types,
control flow and fail-open/fail-closed branches, not from prose. `CA/` abbreviates
`src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/`.

**The `CAS-###` IDs below are freshly numbered for this round.** They do **not** correspond to,
and must not be cross-referenced against, the `CAS-###` numbering in tracking issue
[#2031](https://github.com/Altinity/ClickHouse/issues/2031) or in any earlier audit round. No
prior finding was carried forward; collisions with old numbers are coincidental.

Counts: **349 findings before dedup** across the 39 reports, merged by root cause into **138
global items** -- **135 product findings** (24 High, 98 Medium, 13 Low) plus **3 audit-round
notes** that are not product defects. Severities were re-graded in a dedicated pass against the
rubric in [Severity methodology](#severity-methodology); a merged finding is graded on its own
realistic impact, not on the highest severity any contributing audit assigned.

## Summary counts

| Severity | Count |
|---|---|
| High | 24 |
| Medium | 98 |
| Low | 13 |
| **Total** | **135** |

| Class | Count |
|---|---|
| PERF/SCALE | 21 |
| INTEGRITY | 19 |
| OBSERV/DAY2 | 15 |
| LEAK | 13 |
| CORRECTNESS | 12 |
| DATA-LOSS | 11 |
| LIVENESS | 8 |
| SECURITY | 6 |
| CONFIG | 6 |
| FEATURE-GAP | 6 |
| CONCURRENCY | 5 |
| COMPAT | 5 |
| DECODE/DoS | 4 |
| TEST-GAP | 4 |

Three items from the first pass were audit-process observations rather than product
defects; they are kept, with their substance and anchors, in
[Audit-round notes](#audit-round-notes-not-product-defects) as `NOTE-1`..`NOTE-3` and are
excluded from the counts above.

## Severity methodology

Severities are graded on **realistic impact under a plausible trigger**, not worst-case
theory. For every candidate High the three questions asked were: what concretely goes
wrong, how likely is the trigger, and does the system fail closed?

- **High** -- a realistic trigger leads to data loss, silent wrong results, split brain,
  integrity compromise, or unbounded unavailability of reads or writes.
- **Medium** -- a correctness, reliability or security defect with a narrower trigger (a
  specific configuration, a specific race, a specific provider, a specific scale), or a
  serious operability gap with no correctness break.
- **Low** -- diagnosability, accounting and metric accuracy, cosmetic-but-real
  inconsistency, dead code, and inefficiency with no correctness or availability break.

Two grading rules did most of the work, and both differ from the previous round:

1. **A fail-closed loud failure is graded below silent corruption.** A query or write
   that fails visibly with an error is normally Medium, however annoying, because the
   operator learns about it immediately and no data is silently wrong. It is graded High
   only when the refusal is unbounded or unrecoverable -- for example a pool-wide reader
   floor that locks older builds out permanently with no in-place migration.
2. **Operability, observability, cost and scale gaps are not High on their own.** They are
   promoted only when they directly cause an unbounded outage. A missing repair verb, a
   misleading counter, a budget below the steady-state rate and an O(total pool) round
   cost are Medium or Low here even where the previous round rated them High.

Applied symmetrically: findings whose impact is silent loss or silent wrong results were
promoted out of Medium regardless of how narrow their anchor looked.

## High severity

### CAS-001 -- shadow/FREEZE and backup namespaces are pool-global while every exclusion primitive is per-server-root
- Class: DATA-LOSS
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:897-900` (`shadowNamespace()`), against `:886-889` (`liveNamespace()` prepends `serverPrefix()`), `:1458-1463` (`ownsNamespace()`)
- Impact: two servers sharing one pool are unfenced concurrent writers on one shadow ref table; UNFREEZE on either deletes the other's frozen parts, and `DROP TABLE` leaves shadow refs pinning every byte forever. The same missing prefix removes the watermark floor, permanently disabling the orphan-manifest sweep and the fold's clamp release for those namespaces.
- Trigger: two mounts with distinct `server_root_id` on one pool holding replicas of one table; `FREEZE WITH NAME 'b'` on both, then `UNFREEZE` on either.
- Reported by: jepsen-anomaly-1, interleaving-1, interleaving-2, alter-merge-mutation-6, ad2-6

### CAS-002 -- manifest-trust `adoptEvidence` bypasses the condemn marker and EDGE-BEFORE-OBSERVE
- Class: DATA-LOSS
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:478-486` (`adoptEvidence`), accepted unchecked at `:675-695` (`promote`)
- Impact: a committed manifest can name a blob GC has already deleted. It is the one adopt form that consults neither the durable `Condemned` marker nor the object, and there is no source to re-upload from on a hardlink path. It also downgrades an already-tokened dep to a tokenless trusted adopt.
- Trigger: hardlink/clone adopting a blob whose last other owner is retired inside the adopt-to-precommit window.
- Reported by: gc-protocol-1, tla-fidelity-8

### CAS-003 -- the GC lease has no TTL, is stealable on differential observation, and the destructive phases are never revalidated
- Class: CONCURRENCY
- Anchor: `CA/Gc/CasGc.cpp:3155-3186` (steal predicate), `:3089-3103` (`pulseHeartbeat` discards its `casPut` result), destructive phases `:611-665`, `:865-884`, `:906-930`
- Impact: two GC actors can run destructive phases concurrently on one pool. The stolen-from leader executes its whole redelete batch and only discovers the loss at the round-commit CAS, after the deletes. The steal window is derived from the challenger's own `gc_interval_sec` while the incumbent's evidence ticks at the incumbent's cadence, and a rebuild never renews across its unbounded scan.
- Trigger: a GC leader stalls for longer than ~2 scheduler intervals (IO stall, process pause, or heartbeat writes failing while `gc/state` reads succeed).
- Reported by: gc-protocol-3, jepsen-anomaly-5, tla-fidelity-2, ad7-7, gc-rebuild-feature-2

### CAS-004 -- `GC REBUILD` has no writer/mount interlock and "read-only" does not gate writes
- Class: INTEGRITY
- Anchor: `CA/Gc/CasGc.cpp:2725` (the only exclusion taken), `ContentAddressedMetadataStorage.cpp:491` vs `programs/disks/CommandCaGcRebuild.cpp:26,43-47`; mount census result discarded at `CA/Gc/CasGc.cpp:2968-2971`
- Impact: the two entry points require opposite read-only postures, nothing examines mount leases, mount slots or writer epochs, and a rebuild is accepted on a live writable disk with inserts in flight.
- Trigger: `SYSTEM CAS GC REBUILD FORCE <disk>` on a running server.
- Reported by: gc-rebuild-feature-1

### CAS-005 -- a repointed committed ref is unrevertible, and durable CAS mutations happen before `commit()` with a silent best-effort rollback
- Class: DATA-LOSS
- Anchor: `CA/ContentAddressedTransaction.cpp:280-289` (repoint then a throwable ref-log mutation), `:327-348` (N independent publishes), `Parts/PartFolderAccess.cpp:518-562` (`dropRefIfMatches` is `noexcept` and swallows every error)
- Impact: multi-part and repoint commits are not atomic; `undo()` cannot revert what is already durable, compensation only covers newly created refs, and its failures are invisible. Readers can observe aborted and intermediate states (G1a/G1b).
- Trigger: any transaction writing to, or unlinking from, an already-committed part where a later step fails; also `REPLACE/ATTACH PARTITION`, which writes `metadata_version.txt` twice, the second time as a repoint of a committed ref.
- Reported by: write-protocol-1, write-protocol-2, jepsen-anomaly-2, idisk-contract-3, alter-merge-mutation-5

### CAS-006 -- cross-namespace `RENAME`/`moveDirectory` is a per-ref non-atomic migration ending in an unconditional source drop, with no reconciler
- Class: DATA-LOSS
- Anchor: `CA/ContentAddressedTransaction.cpp:846-874` (`moveDirectory`, per-ref `republishRef` at `:863`, terminal `dropNamespace(from_ns)` at `:874`), `Parts/PartFolderAccess.cpp:419-431`
- Impact: a crash mid-rename leaves refs split across two namespaces with nothing to finish or roll back the move; the ref set is a snapshot taken once, so refs added during the walk are dropped with the source. Ordinary part removal takes the same path, republishing a whole new manifest for a `delete_tmp_` ref before dropping the source.
- Trigger: `RENAME TABLE` across table UUIDs on a CAS disk, interrupted; or any part removal.
- Reported by: crash-consistency-1, interleaving-3, mergetree-part-support-8

### CAS-007 -- nested `server_root_id` is accepted, and decommissioning the ancestor destroys a live descendant member
- Class: DATA-LOSS
- Anchor: `CA/Pool/CasServerRoot.h:104-134` (validation), `CA/Tools/CasDecommission.cpp:124-135`, `:186-202` (prefix deletions), `CA/Formats/CasLayout.h:233-241`
- Impact: victim selection and deletion are prefix-based, so `SYSTEM CAS DROP POOL MEMBER` on `srid=a` erases the namespaces and control objects of a live member `srid=a/b`.
- Trigger: two disks configured with `server_root_id` values where one is a path prefix of the other.
- Reported by: ad7-1

### CAS-008 -- content addressing defaults to a non-cryptographic 128-bit hash and reads never re-verify
- Class: SECURITY
- Anchor: `CA/ContentAddressedSettings.cpp:33` (`blob_hash` default `cityhash128`), `CA/Primitives/CasBlobDigest.cpp:20-31`, `CA/Formats/CasLayout.cpp:28-31`
- Impact: a chosen collision substitutes data for every future reader of the colliding content: the second write dedups onto the first body, and no read path ever re-hashes what it fetched.
- Trigger: two byte strings with equal CityHash128 (or XXH3-128); write the first, then any write of the second dedups.
- Reported by: security-2

### CAS-009 -- an occupied content address is admitted on existence alone, and no re-upload or staged body is ever re-hashed
- Class: INTEGRITY
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:250-305` (`observeAndAdmit` computes `logical_size` and discards it), `:387-420`, `:463-471` (`streamIfAbsent`/`resurrect` check `written != source.size` only), `CA/ContentAddressedTransaction.cpp:1276-1295` (hash in memory, no `sink->sync()`, body re-read at commit)
- Impact: the content-address invariant is size-checked, never digest-checked, on every dedup admission, every retry, every resurrect and every staged-body promotion. Any length-preserving divergence (bit rot, a rewritten scratch file, a mutated staging object) publishes bytes under the wrong address.
- Trigger: any dedup hit, retry, or `promoteStaged` where the stored/re-read bytes are not the bytes that were hashed.
- Reported by: ad1-1, tla-fidelity-7, bc2-2

### CAS-010 -- an empty conditional token turns a fenced write into an unconditional clobber
- Class: INTEGRITY
- Anchor: `CA/Backend/CasObjectStorageBackend.cpp:165-173` (token minting), `:677-678` (`putOverwrite` validates only the token *type*), `:683`, `:698-707`; `src/IO/WriteBufferFromS3.cpp:656-657` (`If-Match` set only when non-empty)
- Impact: when the ETag is absent and the fallback HEAD reports absent, the minted token is empty and the next `putOverwrite`/`casPut` sends no precondition at all -- an unconditional overwrite on a key whose whole protocol assumes compare-and-set.
- Trigger: a write buffer that does not surface an ETag, or a 404 in the eventual-consistency window after a committed conditional PUT.
- Reported by: tier2-1

### CAS-011 -- plain-object writes bypass the request controller and the margin-checked fence, and their indeterminate outcomes are never resolved
- Class: INTEGRITY
- Anchor: `CA/Pool/CasPlainObjects.cpp:21-41` (`casPutObject`), `:51-66` (`casRemoveObject`), `:18` (`MAX_CAS_ATTEMPTS = 100`, no sleep); fence `CA/Pool/CasMountRuntime.cpp:90-99` (`mayMutate`, no margin) vs `:101-111` (`refAppendFenceOk`)
- Impact: namespace-file and mountpoint writes admit a request with no subtraction of `attempt_timeout_ms + lease_safety_margin_ms`, run with no `CasRequestController` (no attempt timeout, deadline or cap), let any exception escape as "failed" without an exact-read resolution, and retry the same key 100 times with zero backoff.
- Trigger: any `putNamespaceFile`/`removeNamespaceFile`/`putMountpointObject` issued when the mount deadline is within one attempt timeout, or under contention on one key.
- Reported by: tier2-2, tla-fidelity-5, jepsen-anomaly-4, ad5-7

### CAS-012 -- lifecycle rules, Object Lock and storage-class transitions are undetected and fail open; Glacier reads have no restore-and-retry and deny-DELETE is unclassified
- Class: DATA-LOSS
- Anchor: `CA/Backend/CasObjectStorageBackend.cpp:272-282`, `:588-609`; `ObjectStorages/S3/S3ObjectStorage.cpp:503-511`
- Impact: a lifecycle expiration rule covering the pool prefix silently deletes live blobs; a transition rule makes reads fail with no restore path; Object Lock/WORM and policy denies surface as raw S3 exceptions instead of a classified, actionable failure.
- Trigger: any lifecycle, Object Lock or bucket-policy configuration on the CAS prefix.
- Reported by: ad6-6, ad6-10

### CAS-013 -- one node admitting a hash algorithm rewrites the pool-wide reader floor to its own build number
- Class: COMPAT
- Anchor: `CA/Pool/CasPoolMeta.cpp:72` (`next.min_reader_generation = G_BUILD;`), `:115`; enforcement `CA/Formats/CasPoolMetaFormat.cpp:152-155`
- Impact: merely mounting one disk with `blob_hash_allow_new=1` and a new algorithm locks every older build out of the *entire* pool, no blob need be written; afterwards permanent algorithm divergence across nodes is invisible.
- Trigger: `blob_hash=<new>` plus `blob_hash_allow_new=1` on any single disk.
- Reported by: upgrade-compat-4, ad1-2, ad7-8

### CAS-014 -- the file-placement classifier is a closed suffix allowlist that misses shipped MergeTree file names, sending them down the fully-in-memory inline path
- Class: CORRECTNESS
- Anchor: `CA/ContentAddressedTransaction.cpp:65-73` (`partFileMustStayBlob`: exact `primary.idx` plus `.bin`/`.mrk*`/`.cmrk*` up to `3`), consumers `:539`, `:598`, accumulation `:1336-1348`
- Impact: `primary.cidx` (the shipped compressed-primary name, so the `primary.idx` case is dead code), `.mrk4`/`.cmrk4` substream marks, and every secondary-index data file (`.idx`, `.idx2`, `.dct.idx`, `.pst.idx`, `.pos.idx`, `skp_idx.packed`) are buffered whole in a `std::string` before any placement decision. Vector-similarity HNSW graphs and text-index postings are routinely hundreds of MB to GB. There is no `else` branch that logs, meters or rejects an unrecognised extension.
- Trigger: INSERT or merge on a table with a compressed primary key, substream marks, a projection, or any non-trivial skip index.
- Reported by: datatype-agnosticism-1, datatype-agnosticism-2, datatype-agnosticism-3, datatype-agnosticism-4, bc5-1, mergetree-part-support-2, bc2-3

### CAS-015 -- waits on CAS single-flight, leader and recovery paths have no deadline and no cancellation
- Class: LIVENESS
- Anchor: `CA/Pool/CasRefLedger.cpp:1457-1492` (ref-append followers `cv.wait`), `:956-1106` (recovery blocks every reader), `:3451-3458` (`DROP TABLE` waits for the publish leader); `CA/Parts/PartFolderAccess.cpp:240-252` (`future.get()`); `CA/Pool/CasPool.cpp:635`, `:702-733` (`remount_mutex` held across expiry polling and two quiescence waits), `:828-896`
- Impact: a slow or ambiguous object store converts any of these into an indefinite hang of unrelated work: concurrent INSERTs to one table, every reader of a recovering namespace, `DROP TABLE`, query threads loading the same part, `SYSTEM CAS FORGET DISK`, and writer-cleanup drain, none of which can be cancelled or times out.
- Trigger: two or more concurrent writers/readers on one namespace or part while the store stalls or 5xx-loops.
- Reported by: bc7-2, bc7-5, bc7-6, bc7-7, bc7-8, concurrency-9

### CAS-016 -- `attempt_timeout_ms` never reaches the wire, and the blob payload read bypasses the CAS backend entirely
- Class: LIVENESS
- Anchor: `CA/Backend/CasRequestControl.h:84` (every use is arithmetic: `CasRequestControl.cpp:202,264,328,388,459,526`); payload read `CA/ContentAddressedMetadataStorage.cpp:1447-1455` -> `DiskObjectStorage.cpp:903-904` (`object_storage->readObject` directly)
- Impact: CAS reads run on the default client's 500-retry profile with no attempt timeout, operation deadline or attempt cap, and payload GETs produce no CAS classification, no event and no request-control accounting -- a stalled bucket surfaces as a raw object-storage error after an unbounded delay.
- Trigger: a bucket that accepts connections but stalls or 5xx-loops.
- Reported by: bc7-4, read-protocol-3

### CAS-017 -- namespace removal latches read/write admission closed before anything is durable, and the lane has terminal states with no exit
- Class: LIVENESS
- Anchor: `CA/Pool/CasRefLedger.cpp:3451-3458` (latch set before `beginRemoving` at `:3492`), `:394-398` (readable runtime returns `nullptr` when latched), `:3517-3544` (recovery handler with an empty catch at `:3539`), `:2501-2515` (`RefLaneState::Closed`)
- Impact: during the window the catalog row is still `Live` and every committed ref reads as absent; a transient backend failure lands in a handler whose reopen is swallowed, so the table is permanently unreadable and unwritable; `Closed` and a catalog row stuck in `Removing` have no exit and refuse both writes and re-creation until restart.
- Trigger: `DROP`/`RENAME TABLE` on a CAS table while the object store returns a transient error.
- Reported by: bc3-1, tier1-1, tier1-2, crash-consistency-8

### CAS-018 -- latches and leadership are set or released outside RAII, and `noexcept`/destructor paths allocate
- Class: LIVENESS
- Anchor: `CA/Pool/CasRefLedger.cpp:1519-1541` (`completeOwnedItemsAndReleaseLeadership` allocates at `:1531`), `CA/Pool/CasPool.cpp:562-571` (`~Pool` allocates, logs and joins with no handler), `CA/Gc/CasGcPhaseTimer.h:28-47`, `CA/Backend/CasProbe.cpp:20-32`, `CA/Pool/CasServerRoot.cpp:1026-1047` (state committed before a throwable callback), `CA/Pool/CasPartWriteTxn.cpp:551-572`
- Impact: under a memory limit a throw in the leadership-release path deadlocks the namespace forever; a `bad_alloc` in `~Pool` or a `noexcept` cleanup lambda terminates the process; a *successful* lease renewal can fence the mount because the post-commit callback throws; a durable manifest body can end up with no in-memory record.
- Trigger: memory pressure or a `MEMORY_LIMIT_EXCEEDED` inside any of these paths.
- Reported by: bc3-2, bc3-3, bc3-5, bc3-6, bc3-7, bc3-11, concurrency-13

### CAS-019 -- part-folder single flight is keyed by ref only, collapsing different manifest ids onto one key
- Class: CORRECTNESS
- Anchor: `CA/Parts/PartFolderAccess.cpp:231-269` (`inflight.find(key.cacheKey())`), map `PartFolderAccess.h:189`, caller `:190-214`
- Impact: two concurrent `getView` calls straddling a commit/repoint of the same ref make the follower receive the leader's view for a *different* manifest than it resolved -- sizes and blob references from one manifest, presence decisions from another.
- Trigger: a repoint landing between two concurrent part loads.
- Reported by: concurrency-2, tier4-3

### CAS-020 -- `getStorageObjects` returns objects that are not the file's bytes, because the envelope offset is dropped
- Class: INTEGRITY
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:1336-1340`, `:1368-1371`; `CA/Pool/CasManifestReader.cpp:133-144`, `.h:14-19`
- Impact: the generic object-storage copy path (a `MOVE PART/PARTITION TO DISK` or TTL move to a disk with an equal `DataSourceDescription`) copies the whole blob object including its 256-byte envelope and treats it as file content, producing a corrupt destination part with no error.
- Trigger: `ALTER TABLE ... MOVE PART/PARTITION TO DISK` off a CAS disk, or a TTL move.
- Reported by: idisk-contract-1

### CAS-021 -- ambiguous conditional-write outcomes are reported as definite ones
- Class: INTEGRITY
- Anchor: `CA/Backend/CasRequestControl.cpp:427-435`, `:498-506` (content equality treated as proof of our own authorship), `:357-368`, `:543-562` (ambiguity reported as foreign occupancy); `CA/Backend/CasObjectStorageBackend.cpp:109-124` (`NoSuchKey` mapped to `PreconditionFailed`)
- Impact: a loser of a race that wrote identical bytes is told it committed, erasing CAS exclusivity on mutable keys; a write that actually landed before a network timeout is reported as someone else's object; and a multipart `NoSuchKey` becomes a definite "another writer owns this key".
- Trigger: two writers of identical bytes to one mutable key; or a timeout after a landed write.
- Reported by: tier2-4, tier2-5, jepsen-anomaly-3

### CAS-022 -- the orphan-manifest sweep applies no protection at all to a manifest whose namespace has no catalog row
- Class: DATA-LOSS
- Anchor: `CA/Gc/CasOrphanManifestSweep.cpp:546` (`catalog_entry` may be `nullptr`), every protection conditioned on it at `:547-561`, `:605-636`, `:653`, `:660-682`; nomination at `:684-716`
- Impact: the manifest body is deleted and a `BlobSourceRetirement` is emitted for every blob entry, driving condemnation of blobs that are about to become reachable. The window is the first-ever write into a namespace, because `stageManifest` writes the body before `precommitAdd` creates the catalog row.
- Trigger: a GC sweep page covering a brand-new namespace's manifest key during the first write.
- Reported by: gc-protocol-2

### CAS-023 -- deletes are accepted and silently do nothing when GC is disabled or the pool has settled as vanished
- Class: DATA-LOSS
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:611` (scheduler only when `gc_enabled`), `:461-464`, `:492-494`, `:715-717` (`GC RUN`/`START`/`REBUILD` -> `BAD_ARGUMENTS`), `:809-812` (`VanishedReplaced`/`VanishedForgotten` -> `TruthAbsent`); remove paths never consult `gc_enabled` (`CA/ContentAddressedTransaction.cpp:683`, `:705`, `:1069`)
- Impact: with `gc_enabled=false` -- a documented, supported setting -- deletes are accepted forever and every manual reclamation path is refused; on a settled-vanished pool `DROP TABLE`/`DROP PARTITION` returns success having done nothing at all.
- Trigger: `gc_enabled=false`; or a re-created pool prefix / `SYSTEM CAS FORGET` followed by a drop.
- Reported by: ad2-7, ad2-8

### CAS-024 -- two CAS disks sharing a pool and a `server_root_id` share one namespace, and a MOVE between them deletes the moved part
- Class: DATA-LOSS
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:886-889` (`liveNamespace` = srid + table uuid, no per-disk identity), `:903-934` (`route()` derives the ref from the part directory only); `CA/ContentAddressedSettings.cpp:119-137` (validation does not detect the collision)
- Impact: `MOVE PARTITION TO DISK` between the two disks resolves source and destination to the same `(namespace, ref)`, so the move publishes then drops the same ref -- the part is gone, silently.
- Trigger: a policy with two CAS disks on one pool prefix with the same `server_root_id`, then a MOVE.
- Reported by: ad4-3

## Medium severity

### CAS-025 -- `GC REBUILD` discards the condemn universe and permanently orphans already-unreferenced blobs
- Class: LEAK
- Anchor: `CA/Gc/CasGc.cpp:2809-2824` (`prior_runs` starts empty; `flush_shard` folds only `+1` deltas), `:2876-2951`
- Impact: every blob unreferenced at rebuild time -- including everything already carrying `delete_pending` -- is absent from the rebuilt generation and is never reclaimable again, because nothing but fsck ever lists `blobsPrefix()`. The graduation guard that would catch this is vacuous when the confirm callback is omitted, which is exactly what the rebuild call site does.
- Trigger: `SYSTEM CAS GC REBUILD`, or the FORCE path after any `gc/state` loss.
- Reported by: tla-fidelity-3, tla-fidelity-1

### CAS-026 -- relink treats `pool_uuid` equality as proof of "same bucket" and publishes the adopted part unverified
- Class: INTEGRITY
- Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:313-330`, `:780-787` (both gates are the same equality), `CA/ContentAddressedMetadataStorage.cpp:1592-1636`; publish with `check_consistency=false` at `DataPartsExchange.cpp:1262`
- Impact: a sender advertising a matching `pool_uuid` while pointing at a different physical prefix gets its manifest adopted with no presence check on any blob dependency, and the receiver loads the part without the checksum validation the byte-fetch path performs.
- Trigger: relink a part whose manifest names a blob not resolvable in the receiver's pool view.
- Reported by: ad7-2, ad4-5

### CAS-027 -- any bucket-credential peer can permanently disable, fence or misdirect another member; there is no intra-pool authentication
- Class: SECURITY
- Anchor: `CA/Pool/CasServerRoot.cpp:68-79` (`throwIfOwnerRetired`), `:105-159` (`claimOwnerOrThrow`), `:298-366` (`claimMount`), `:455-552` (`computeHeartbeatFloor` writes `gc_fenced` into a peer's slot)
- Impact: one PUT to another member's `owner` or `mount` object retires it permanently, fences its writes, or steals its slot. Every control object is authenticated only by possession of bucket credentials, which every member and every backup/log-shipping role has.
- Trigger: a single write to `gc/server-roots/<victim-srid>/{owner,mount}`.
- Reported by: security-1

### CAS-028 -- blob keys are unsalted pool-global content hashes: no per-subject shred, guessable residue, and a dedup confirmation oracle
- Class: SECURITY
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:145` (`key = layout.blobKey(ref)` -- content only, no namespace/table/tenant), `CA/Formats/CasLayout.cpp:28-31`, `src/Interpreters/ContentAddressedLog.cpp:29` (digest exposed in `system.cas_log`)
- Impact: a delete frees nothing while any other manifest anywhere in the pool shares the blob, so there is no shred primitive for a tenant or a table; unreclaimed deleted content stays addressable by anyone who can guess the digest; and under server-side encryption the digest is a plaintext hash exposed in key names and a system table, probeable by observing whether an upload dedups.
- Trigger: `DROP TABLE` on a pool where the same rows exist elsewhere or on any replica; or bucket LIST / `SELECT ... FROM system.cas_log`.
- Reported by: ad2-3, ad2-5, encryption-6

### CAS-029 -- the provider dialect is declared by configuration and never detected, so the one bucket-versioning precondition runs only for GCS clients and fails open when it runs
- Class: DATA-LOSS
- Anchor: `CA/Backend/CasObjectStorageBackend.cpp:53-67`; `src/IO/S3/Client.cpp:1301-1307`; `src/Disks/DiskObjectStorage/ObjectStorages/S3/S3ObjectStorage.cpp:514-529`
- Impact: on AWS S3 and every S3-compatible store the versioning check is skipped entirely; on GCS it is downgraded to a warning whenever `GetBucketVersioning` fails or is not permitted. A versioned bucket then either wedges all reclamation or aborts a GC round with `LOGICAL_ERROR` *after* the delete has happened, and prior deletes are silently recoverable versions. Backends that do not report delete markers make the precondition unverifiable by construction.
- Trigger: mount a CAS pool on a versioned AWS/MinIO/RustFS bucket, or enable versioning after mount.
- Reported by: ad6-1, ad6-2, ad6-5, ad2-10, ad6-8, tla-fidelity-9

### CAS-030 -- `skip_access_check` removes every bucket-configuration defense, and the decommission remount hard-codes it
- Class: CONFIG
- Anchor: `CA/Pool/CasPool.cpp:339-347`, `:528` (hard-coded skip), `CA/ContentAddressedSettings.cpp:35`; the probe it disables is `CA/Backend/CasProbe.cpp:15-66`
- Impact: the only proof that *this node's* path enforces conditional-write preconditions is opt-out per node, the opt-out is not recorded anywhere in the pool, and every decommission remount takes it unconditionally. The shipped description invites the setting ("start now, fix later").
- Trigger: `skip_access_check=true`, or any decommission.
- Reported by: ad6-3, ad7-6

### CAS-031 -- the conditional-write contract is validated only for single-PUT and then assumed for multipart
- Class: INTEGRITY
- Anchor: `src/IO/WriteBufferFromS3.cpp:409-416`; `CA/Backend/CasObjectStorageBackend.cpp:632-636`; `CA/Backend/CasProbe.cpp:42`
- Impact: on a store that honours `If-None-Match` on `PutObject` but ignores it on `CompleteMultipartUpload`, every blob large enough to go multipart loses its exclusivity guarantee while the probe reports the pool as safe.
- Trigger: any blob above the multipart threshold on such a store.
- Reported by: ad6-4

### CAS-032 -- zero cross-region / replicated-bucket awareness; a failover to a replica bucket is undetectable
- Class: INTEGRITY
- Anchor: `CA/Pool/CasPoolMeta.cpp:100-104`, `:111-119`
- Impact: nothing binds a pool identity to an endpoint or region, so DNS/endpoint failover to a CRR destination, or mounting a replica "for read scale-out", is indistinguishable from the primary -- conditional writes are then made against a bucket whose contents lag.
- Trigger: endpoint failover, or bidirectional replication configured over the pool prefix.
- Reported by: ad6-7

### CAS-033 -- all reclamation is gated on a whole-pool "clean pass" predicate with no bound and no retention signal
- Class: LEAK
- Anchor: `CA/Gc/CasGc.cpp:2063-2064` (`suppress_destructive`), consumed at `:609-610`, `:791-792`, `:799-800`, `:830-832`, `:862-863`, `:893-898`
- Impact: one anomaly anywhere (a single `lifeless` key, one undecodable row), one held namespace, or one namespace whose ref table cannot be walked suppresses *every* destructive action pool-wide, for as long as the condition persists. There is no bound, no retention target and no operator signal that reclamation has stopped.
- Trigger: any single anomaly or incomplete frontier in any namespace.
- Reported by: ad2-1

### CAS-034 -- per-round reclamation budgets sit below the steady-state creation rate
- Class: LEAK
- Anchor: `CA/ContentAddressedSettings.cpp:46` (`gc_round_ref_cleanup_budget = 5000`), `:32` (`gc_interval_sec = 60`), `:42-43`; `CA/Gc/CasGc.cpp:2398-2411`, `:390` (janitor 1000/round, one page)
- Impact: every part commit creates two ref objects (plus one snapshot per 256 appends) while cleanup reclaims at most 5,000 ref objects per 60 s round and the namespace janitor erases one 1,000-key page per round. Above that rate debris accumulates without bound; erasure latency for a `DROP` is a function of object count over the budgets, not a bounded time.
- Trigger: sustained commit rate above the cleanup ceiling, or `DROP TABLE`/`DROP DATABASE` at scale.
- Reported by: ad5-4, ad2-2, ad2-12

### CAS-035 -- the GC fold and its enumerations are O(total pool) every round, unbudgeted, with unbounded peak memory
- Class: PERF/SCALE
- Anchor: `CA/Gc/CasBlobInDegree.cpp:484-555` (fold over all edges), `CA/Gc/CasGc.cpp:1379` (`std::vector<BlobDelta> deltas`, no budget), `:2561-2593` (`enumerateRefPrefix`, full LIST retained in memory, no cursor), `:2597` (called unconditionally, including on rounds it then defers)
- Impact: round cost and peak memory are set by total pool size rather than churn since the last round, re-paid every `gc_interval_sec`; there is no per-round budget on ref-log GETs, manifest decodes or the delta vector, and no resumability, so a backlog must be absorbed in one round.
- Trigger: any pool at scale; worst after leader loss, a cleared hold, or an object-store outage.
- Reported by: performance-1, ad5-2, gc-protocol-5, gc-rebuild-feature-3, performance-9

### CAS-036 -- any bucket-sourced control object is materialized in memory unbounded, and one planted object costs quadratic CPU
- Class: DECODE/DoS
- Anchor: `CA/Backend/CasObjectStorageBackend.cpp:284-293` (`readStringUntilEOF`, no cap), `:333-338` (read buffer sized to the attacker's declared size), `:468-489`; `CA/Formats/CasTextFormat.cpp:164-166` (`std::find` over `seen_keys` per key), `:387-399` (zstd `out.resize(declared frame size)` before decompress)
- Impact: overwriting `_pool_meta`, `owner`, `mount`, `_ckpt` or a ref-log object with a multi-gigabyte body OOMs the victim before any format check runs; a single 64 MiB line with a few million distinct keys pins a GC or mount thread in Θ(k²) comparisons; a declared zstd frame size is allocated before decompression.
- Trigger: one write to any control object by any principal with bucket credentials.
- Reported by: security-3, security-4, bc4-6

### CAS-037 -- every CAS numeric field silently wraps mod 2^64, and `offset + length` overflows on the read path
- Class: DECODE/DoS
- Anchor: `CA/Formats/CasTextFormat.cpp:193-223` (`readU64Number`/`readU64String`/`readU32Number` over `readIntText`), `CA/Pool/CasManifestReader.cpp:139-143`, `CA/ContentAddressedMetadataStorage.cpp:1439-1454`
- Impact: wrapping defeats every decoder range gate, so a planted manifest `sz` produces a wrapped read window; `std::stoull` accepts `-1` for a GC generation key and `max_gen + 1` then overflows; `published_at_ms` overflows the Poco timestamp multiplication; the fsck referenced-bytes accumulator, the ms/µs conversions and `blob_header_len - 1` share the same class of unchecked arithmetic, and bodies accept non-canonical numeric spellings the key parser rejects.
- Trigger: any bucket-sourced object carrying an out-of-range or negative numeric field.
- Reported by: bc1-1, bc1-2, bc1-4, bc1-5, bc1-6, bc1-7, bc1-8, bc4-9

### CAS-038 -- decoders make liveness- and safety-critical fields optional and default them to the least-safe value
- Class: DECODE/DoS
- Anchor: `CA/Formats/CasServerRootFormats.cpp:147-169` (`decodeMountLease` requires only `su`/`we`; `eat`, `ma`, `fen` default to `0,0,false`), `CA/Formats/CasGcStateFormat.cpp:50-63`, `CA/Formats/CasBlobMetaFormat.cpp:66-81`, `CA/Formats/CasFoldSealFormat.cpp:294-305` (no required-field or junk check), `:286` (two unvalidated decode entry points)
- Impact: a truncated or partially written lease decodes to "expired, unfenced"; `{"st":"condemned"}` decodes to condemn round 0; the GC outcome log does not require the outcome it exists to record; two of four fold-seal entry points skip structural validation; and `gc/state` encoding does not enforce the line cap its decoder enforces, so a long sweep cursor produces an object that cannot be re-read.
- Trigger: any truncated, partially written or planted control object.
- Reported by: bc4-3, bc4-2, bc4-4, bc4-5, bc4-8, bc4-10, tier3-12

### CAS-039 -- `gc_shards` is adopted from bucket bytes with no upper bound and silently overrides the node's configured value
- Class: DECODE/DoS
- Anchor: `CA/Formats/CasPoolMetaFormat.cpp:116`, `:142`; `CA/Pool/CasPoolMeta.cpp:94-95`; `CA/Pool/CasPool.cpp:351-354`, `:547-550`; consumers `CA/Gc/CasGc.cpp:1294`, `:2140-2147`, `:2808-2810`
- Impact: the value read from `_pool_meta` sizes vectors and loop bounds with only a `>= 1` check, and a disagreement with local config is resolved by overwriting the local value without a log or comparison.
- Trigger: a planted or corrupted `_pool_meta`; or a node configured with a different `gc_shards` than the pool.
- Reported by: bc1-3, ad7-4

### CAS-040 -- the part-manifest payload-zone banner is written raw and validated only on decode
- Class: INTEGRITY
- Anchor: `CA/Formats/CasPartManifestFormat.cpp:64-67` (`bannerFor`), `:106-110` (appended raw on encode), `:248-252` (compared against one `readLine` on decode); entry-path validation exists only on the decode side at `:184-193`
- Impact: an entry path containing LF encodes successfully and produces a manifest that can never be decoded again -- a committed part permanently unreadable, with the corruption created by the writer.
- Trigger: any part-relative file name containing a newline reaching `encodePartManifest`.
- Reported by: bc4-1, datatype-agnosticism-6

### CAS-041 -- the manifest payload digest is recomputed by canonical re-encode, so any tolerated or foreign field reads as corruption
- Class: COMPAT
- Anchor: `CA/Formats/CasPartManifestFormat.cpp:263-267` (recompute and compare), `:272-279` (`computePayloadDigest` deep-copies and re-encodes the decoded model)
- Impact: the decoder is tolerant of unknown keys but the digest is derived from what the local struct can re-emit, so a manifest written by any other generation -- or carrying any key this build does not model -- is reported as `CORRUPTED_DATA`. The same implementation costs 2x work and ~3x transient memory on every decode.
- Trigger: read a manifest written by a build with any additional field.
- Reported by: upgrade-compat-1, ad1-5, bc5-3

### CAS-042 -- one global build number is stamped as every object's minimum reader, and the per-format change-point registry is populated but never consulted
- Class: COMPAT
- Anchor: `CA/Formats/CasFormat.h:10` (`G_BUILD = 9`), `CA/Formats/CasFormat.cpp:82-93` (`currentCompatibilityVersion`, `checkCompatibility`), the contradicting table at `:19-75`
- Impact: one generation bump invalidates every format including those that did not change; nothing binds a format change to a `G_BUILD` bump; tolerant decoders drop unknown keys that read-modify-write loops then discard, silently erasing a newer node's fields; and `FormatId::Roster` is registered in `changePoints()` with no traits row, so touching it throws `LOGICAL_ERROR`.
- Trigger: write any CAS object, then read it with an older build; or run mixed generations against one pool.
- Reported by: upgrade-compat-2, codeonly-line-5, upgrade-compat-5, upgrade-compat-10, coverage-map-4

### CAS-043 -- the relink handshake negotiates a replication protocol number that says nothing about CAS generation, and a mismatch escapes the byte-fetch fallback
- Class: COMPAT
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:1610-1619` (the `catch` filters on `CORRUPTED_DATA` only), `CA/Formats/CasFormat.cpp:90` (throws `UNKNOWN_FORMAT_VERSION`), call chain `src/Storages/MergeTree/DataPartsExchange.cpp:1182-1184`, `:793-799`
- Impact: a sender and receiver on different CAS generations complete the handshake, and the generation error is not the code the fallback catches, so the fetch fails outright instead of degrading to a byte fetch.
- Trigger: replica fetch between two nodes with different `G_BUILD`.
- Reported by: upgrade-compat-3

### CAS-044 -- the 16 MiB per-part inline budget is enforced only at commit, with no fallback
- Class: FEATURE-GAP
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:54` (`kMaxManifestInlineBytesTotal = 16 MiB`), enforced at `:514-528` with `LIMIT_EXCEEDED`
- Impact: a legitimately wide part whose inline-classified files sum past 16 MiB fails its INSERT permanently -- the check happens after everything is staged, and there is no re-classification to blob placement. Because the spenders are row-count-scaled index and marks data (CAS-014), the failure is schema-dependent and reproducible on retry.
- Trigger: many projections or many skip indexes on a wide table.
- Reported by: mergetree-part-support-1, datatype-agnosticism-5

### CAS-045 -- the part-folder view cache accounts every retained manifest as 256 bytes
- Class: PERF/SCALE
- Anchor: `CA/Parts/PartFolderAccess.cpp:128-131` (`estimatedBytes() = 256 + manifest_size`) with `CA/Pool/CasRefLedger.cpp:254-258`, `:273-276` (both producers hardwire `.manifest_size = 0`)
- Impact: `part_folder_cache_bytes` is inoperative -- 10,000 retained wide-part views pin gigabytes of decoded manifests including inline file bodies -- and the same constant defeats the oversized-entry bypass guard, so nothing is ever excluded for being too large.
- Trigger: read files from many distinct parts with large manifests.
- Reported by: read-protocol-1, bc5-5, mergetree-part-support-3

### CAS-046 -- local scratch staging is unreserved, unaccounted, uncapped, held for the whole transaction, and never swept at startup, while the CAS disk reports no free space at all
- Class: PERF/SCALE
- Anchor: `CA/ContentAddressedTransaction.cpp:1223-1235` (scratch creation), `:148-172` (reclaimed only in-process), `src/Disks/DiskObjectStorage/DiskObjectStorage.h:65-67` (`getTotalSpace/getAvailableSpace/getUnreservedSpace` return `{}`), `MetadataStorageFactory.cpp:233-238` (default scratch on the server data volume)
- Impact: concurrent INSERTs consume the server data volume in proportion to in-flight part bytes with no quota, no reservation and no visibility; scratch files live until every part in the transaction commits; a crash leaves them forever because only the in-process cleaner enumerates them; and an inline-overflow spill that fails leaks its file before any guard is installed.
- Trigger: concurrent INSERT/merge/mutation with the default `staging_backend=local`.
- Reported by: bc2-1, ad5-12, crash-consistency-6, bc2-4

### CAS-047 -- the blob upload pool is process-global, 16 threads with a 16-slot queue, and enqueue blocks
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasBlobUploadPool.cpp:45-49` (single instance), `src/Core/ServerSettings.cpp:151` (`cas_blob_upload_pool_size = 16`), `src/Common/ThreadPool.cpp:162`, `:180`; fan-out `CA/ContentAddressedTransaction.cpp:1181-1207`
- Impact: one wide part exceeds the queue by itself (`2C + 1` tasks; a 100-column part enqueues 201), so the committing thread blocks inside `scheduleImpl` for most of them, and all CAS uploads for every disk in the process serialize behind one undeadlined queue.
- Trigger: more than 16 in-flight blob uploads anywhere on the server.
- Reported by: ad5-3, bc7-9

### CAS-048 -- a CAS part publish runs object-store I/O while `DataPartsLock` is held
- Class: LIVENESS
- Anchor: `src/Storages/MergeTree/MergeTreeData.cpp:5918-5922` (rename plus `commitTransaction()` inside the caller's `DataPartsLock`), path `:5545-5546` -> `DataPartStorageOnDiskBase.cpp:780-789` -> `CA/ContentAddressedTransaction.cpp:961`
- Impact: a throttling or 5xx bucket stalls the table's parts lock, blocking every SELECT, merge scheduling and part-set mutation on that table for the duration of a remote publish.
- Trigger: `DROP PARTITION`/`REPLACE PARTITION` creating a covering part on a CAS disk while the store is slow.
- Reported by: bc7-1

### CAS-049 -- `GC STOP`, shutdown and `FSCK` serialize behind whole in-flight unbounded scans
- Class: LIVENESS
- Anchor: `CA/Gc/CasGcScheduler.cpp:213`, `:245` (`gc_round_mutex` held for the round), `:67-79` (`stop()` then `join()`); `CA/ContentAddressedMetadataStorage.cpp:739-745` (`lifecycle_mutex` held across `runFsck`), same mutex at `:663`, `:691`, `:711`
- Impact: an operator cannot stop GC, forget a disk, or shut the server down while a round or an fsck scan is in flight against a slow bucket -- exactly the situation in which they would want to. The SQL fsck path also declines to pass the deadline/progress/partial parameters the CLI passes.
- Trigger: `SYSTEM CAS GC STOP` or `SYSTEM CAS FSCK` on a large pool, then any other CAS lifecycle statement.
- Reported by: bc7-3, gc-rebuild-feature-6

### CAS-050 -- the GC scheduler joins its thread objects outside the mutex that guards them, and its threads self-exit independently
- Class: CONCURRENCY
- Anchor: `CA/Gc/CasGcScheduler.cpp:67-79` (`stop()`), `:81-90` (`requestRoundSoon()`), `:57-65` (`start()`), terminal exits `:232-242`, `:289-298`
- Impact: `stop()` races `requestRoundSoon()`/`start()` on the thread objects, and either thread can exit on its own leaving a joinable-but-dead scheduler that reports itself as running.
- Trigger: `SYSTEM CAS GC STOP`/`START` concurrent with a scheduled round, or a terminal error in either thread.
- Reported by: concurrency-1, concurrency-10

### CAS-051 -- snapshot-publish dispatch can leak its pending count, hanging two unbounded waits, and its fan-out is unbounded pool-wide
- Class: LIVENESS
- Anchor: `CA/Pool/CasRefLedger.cpp:2754-2783` (`dispatchSnapshotPublisher`, detached thread per namespace), increment at `:2747`, waits at `:1227-1228` and `:3590-3596`
- Impact: if dispatch fails after the increment, `quiesceRefTablesForRemount` and `dropNamespaceImpl` wait forever; and because the guard is per namespace with no global counter, an ingest wave crossing the 256-log threshold on N tables spawns N concurrent whole-namespace re-encodes.
- Trigger: thread-pool saturation at dispatch; or many tables crossing the snapshot threshold together.
- Reported by: concurrency-3, ad5-10

### CAS-052 -- anomaly reporting calls `shared_from_this()` on a possibly expiring pool
- Class: CONCURRENCY
- Anchor: `CA/Pool/CasPool.cpp:972-1029`, in particular `:992` (outside the `try` at `:993`) and the detached thread at `:995-1023`
- Impact: reporting an anomaly during pool teardown throws `bad_weak_ptr` out of an unguarded region, or hands a detached thread a pool that is being destroyed.
- Trigger: any anomaly report racing disk shutdown/forget.
- Reported by: concurrency-4

### CAS-053 -- the ref-table runtime cache budget is enforced only at recovery, cannot evict a table being written, and its arithmetic can underflow
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasRefLedger.cpp:1105` (sole call site), `:1149-1210` (`enforceRefTableCacheBudget`), skip predicates `:1180-1181`, `:1202-1203`; `CA/Pool/CasPool.h:92` (256 MiB, hardcoded)
- Impact: the 256 MiB budget runs once per namespace recovery and never again, so a workload with many simultaneously-written tables exceeds it without bound; and because `total` is recomputed from concurrently mutated atomics, it can underflow and evict every evictable table at once.
- Trigger: many tables written concurrently on one CAS disk.
- Reported by: ad5-1, tier1-5

### CAS-054 -- ref publication re-encodes the whole namespace every 256 transactions and obtains row byte counts by re-serializing rows
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasRefProtocol.h:120-121` (thresholds), `CA/Pool/CasRefLedger.cpp:2741-2745`, `:2964`, `:3000`, encoder `CA/Formats/CasRefSnapshotFormat.cpp:115-135`, `:259-271`; `CA/Pool/CasRefProtocol.cpp:362-386` (`debugAssertBodyCounters`)
- Impact: steady insert traffic on a namespace with many live parts pays an O(R) encode every 256 commits plus two full row encodes per ref operation; sanitizer and debug builds -- where soak and correctness runs execute -- turn every txn apply and every `admits()` into a further O(R) re-encode.
- Trigger: normal insert traffic; worst at high ref count with small transactions.
- Reported by: performance-2, performance-3, performance-4

### CAS-055 -- every hardlinked file re-reads the source part manifest from the object store, because `part_folder_validate` defaults to `always`
- Class: PERF/SCALE
- Anchor: `CA/ContentAddressedTransaction.cpp:816` (`getView(..., Freshness::ForceFresh)` inside `createHardLink`), cache short-circuit disabled at `CA/Parts/PartFolderAccess.cpp:172` when `validate.mode == Always`, shipped default `CA/ContentAddressedSettings.cpp:55`
- Impact: a mutation, clone or FREEZE of a wide part costs one manifest HEAD plus one full view rebuild per unchanged file -- hundreds to thousands of round trips for work that copies nothing.
- Trigger: `ALTER TABLE ... UPDATE`, `FREEZE PARTITION`, or any clone of a committed wide part.
- Reported by: alter-merge-mutation-1, bc5-8

### CAS-056 -- a single-file write or unlink on a committed part republishes the whole manifest twice and emits one adopt event per blob entry inside the ref-log CAS lambda
- Class: PERF/SCALE
- Anchor: `CA/ContentAddressedTransaction.cpp:256-290` (scratch manifest PUT + precommit, then `merged` + `repointRef`, then `abandon()`), `CA/Parts/PartFolderAccess.cpp:444-457`
- Impact: writing one small file into an existing wide part costs two full manifest encodes and PUTs plus per-entry adopt work executed inside the conditional-write retry closure; a no-op mutation costs two publishes and a full per-file adoption pass.
- Trigger: any standalone write/unlink on a committed part; any "mutation version bump" that touches every part.
- Reported by: bc5-2, alter-merge-mutation-7

### CAS-057 -- `moveFile`/`replaceFile` on a committed part file always throws `LOGICAL_ERROR`
- Class: FEATURE-GAP
- Anchor: `CA/ContentAddressedTransaction.cpp:1030-1055` (`moveFile`: "source not staged"), `:1058-1067` (`replaceFile` delegates)
- Impact: the standard "write `<name>.tmp`, then `replaceFile`" pattern is unusable against a published part, because the `.tmp` write commits in its own transaction. `DeleteBitmapFileOps::writeBitmapToStorage` does exactly this, so unique-key delete bitmaps fail on CAS with an internal error.
- Trigger: `DeleteBitmapFileOps::writeBitmapToStorage` on a committed part, or any equivalent two-transaction rename.
- Reported by: idisk-contract-2, mergetree-part-support-4

### CAS-058 -- cross-disk `ATTACH`/`REPLACE PARTITION FROM` into a CAS disk is unimplemented and fails part-way through the part
- Class: FEATURE-GAP
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:593-621` (`freezeRemote` passes only the empty `external_transaction`), against `:531-533` and `:702-718` which do open a CAS transaction
- Impact: every local->CAS, plain-S3->CAS and CAS-pool-A->CAS-pool-B attach takes a transaction-less copy branch and fails mid-part, leaving partial state rather than being rejected up front.
- Trigger: `ALTER TABLE cas_tbl ATTACH PARTITION p FROM src_tbl` where `src_tbl`'s disk is not in the CAS table's policy.
- Reported by: ad4-1

### CAS-059 -- an encrypted disk can be layered over CAS with no capability check, and it reports "not content-addressed" while still routing writes into CAS
- Class: CONFIG
- Anchor: `src/Disks/DiskEncrypted.cpp:190-208` (any `DiskPtr` accepted, no capability/metadata-type check), `src/Disks/DiskEncrypted.h:24` (never overrides `isContentAddressed()`/`supportsAtomicFileWrites()`), `:329`, `:344-354` (`use_fake_transaction` defaults true), `src/Disks/DiskEncryptedTransaction.h:36-42` (`wrappedPath` prefix)
- Impact: the combination is accepted at startup and fails only at the first part write; meanwhile every CAS-aware hook in MergeTree is disabled because the wrapper answers `false`, and the wrapper's `path` prefix silently reshapes CAS path classification (shadow detection, atomic-shard detection, table-file parsing).
- Trigger: `<disk><type>encrypted</type><disk>cas_disk</disk>...` in a storage policy.
- Reported by: encryption-1, mergetree-part-support-5, encryption-3

### CAS-060 -- per-file random IV makes every file a unique blob, silently destroying dedup
- Class: CORRECTNESS
- Anchor: `src/Disks/DiskEncryptedTransaction.cpp:105-112` (`InitVector::random()` per rewrite-mode write), `src/IO/FileEncryptionCommon.h:131`, `:139`; CAS hashes what it is handed at `CA/ContentAddressedTransaction.cpp:600-642`
- Impact: two replicas merging identical rows, or an `ATTACH`/re-insert of byte-identical data, produce entirely distinct blobs. The pool's core value is gone and nothing -- no counter, no warning -- detects it.
- Trigger: any write through an encrypted wrapper over CAS.
- Reported by: encryption-2

### CAS-061 -- only `gc/state` has a rebuild path; every other control object has no DR path, `_pool_meta` damage locks out the DR tools themselves, and no migration tooling exists
- Class: OBSERV/DAY2
- Anchor: `programs/disks/CommandCaGcRebuild.cpp:24-51`; `CA/Pool/CasPool.cpp:293-368` (esp. `:351-353`); `CA/Pool/CasRefCatalog.cpp:44-49`; `CA/Formats/CasPoolMetaFormat.cpp:89-95` (hard floor, shipped message "there is no in-place migration")
- Impact: damage to `_pool_meta`, the ref catalog, a mount lease or the checkpoint has no recovery verb, and because the tools open the pool through `_pool_meta` first, the one damaged object disables the instruments needed to diagnose it.
- Trigger: any corruption or partial write of a control object other than `gc/state`.
- Reported by: ad3-1, upgrade-compat-9

### CAS-062 -- `SYSTEM CAS FSCK` is counts-only and no repair path exists anywhere
- Class: OBSERV/DAY2
- Anchor: `src/Interpreters/InterpreterSystemQuery.cpp:2534` (`runFsckNow(/*detail=*/false)`), `CA/ContentAddressedMetadataStorage.cpp:739-745`, `CA/Tools/CasFsck.h:114` (returns a report; `Tools/` contains no repair function)
- Impact: the SQL path can tell an operator that the pool is corrupt but never which keys, with no timeout and no scoping; and the `clean()` verdict excludes the two crash-residue counters, so a pool with body-without-meta or meta-without-body residue reports clean.
- Trigger: `SYSTEM CAS FSCK <disk>` on a pool with any hard finding.
- Reported by: ad3-2, crash-consistency-9

### CAS-063 -- the only way to clear a dead member's mount slot is a verb that first erases that member's data, and a half-decommissioned member is invisible and not repairable by re-running the verb
- Class: OBSERV/DAY2
- Anchor: `CA/Tools/CasDecommission.cpp:137-183` (namespace drops) before `:236-363` (slot retirement), `:270-298` vs `:333-341` (delete `mount`/`epoch` before the owner tombstone); `CA/Pool/CasServerRoot.cpp:606-649` (`listMounts` enumerates `/mount` objects only)
- Impact: replacing a permanently dead node forces the operator to run a destructive verb; if it crashes between control-object deletion and the owner tombstone the member is left in a state `cas_mounts` cannot show and a re-run cannot repair, because the capture precondition no longer holds.
- Trigger: node replacement; or a crash during `SYSTEM CAS DROP POOL MEMBER`.
- Reported by: ad3-5, ad3-6, crash-consistency-4

### CAS-064 -- no CAS decoder is fuzzed, no property-based tests exist, and three live format classes skip the shared failure-mode battery
- Class: TEST-GAP
- Anchor: absence of `CA/fuzzers/`; `ci/workflows/nightly_fuzzers.py` and `tests/fuzz/` carry no CAS target; absence of `rapidcheck`/`RC_GTEST` under `src`; `src/Disks/tests/cas_format_test_battery.h` registrations omit `RunFile`, `RefCkpt`, `GcMaintenanceState`
- Impact: every CAS decoder consumes bucket-sourced input that any credential holder can shape, and CAS-036 through CAS-039 are exactly the bug class a fuzzer finds first. No invariant (in-degree, exclusivity, lease safety) is checked by generated input.
- Trigger: n/a -- absence of coverage.
- Reported by: test-coverage-fuzzing-1, test-coverage-fuzzing-4, test-coverage-fuzzing-5

### CAS-065 -- no CI lane exercises a native or GCS conditional-write dialect
- Class: TEST-GAP
- Anchor: `src/Disks/tests/gtest_cas_backend_contract.cpp:250-258`; `src/Disks/tests/gtest_cas_backend_generation.cpp:12-120`; `ci/defs/altinity_jobs.py` (no GCS parameter set), `:116-120` (CAS-over-local is one unsanitized lane)
- Impact: the exclusivity guarantee CAS is built on is only ever tested against the emulated in-process backend, so the entire native `If-None-Match`/`If-Match` path and the GCS generation-token path ship unverified end to end.
- Trigger: n/a -- absence of coverage.
- Reported by: test-coverage-fuzzing-2, test-coverage-fuzzing-3, test-coverage-fuzzing-8

### CAS-066 -- emulated single-process mode is chosen by storage type alone, with no override and only an INFO-level warning
- Class: CONFIG
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:509-520`; `CA/Backend/CasObjectStorageBackend.cpp:78-91` (`checkConditionalWriteSingleAttemptSupport` returns early for non-Native mode); no mode setting in `CA/ContentAddressedSettings.cpp:29-59`
- Impact: two servers over one `local` object storage on a shared mount both select `EmulatedSingleProcess`, whose conditional operations are in-process only, so neither's exclusivity is real and nothing refuses the configuration. Conversely a Native-typed store that cannot honour the single-attempt profile (Azure, HDFS) is only checked on the writable path, so read-only mounts never reach the check.
- Trigger: two servers pointed at one CAS pool over a shared `local` path.
- Reported by: ad7-5, tier4-13, tier4-12

### CAS-067 -- the emulated conditional-write token is a filesystem mtime, and its state pruning stalls permanently on clock skew
- Class: INTEGRITY
- Anchor: `src/Disks/DiskObjectStorage/ObjectStorages/Local/LocalObjectStorage.cpp:391`, `:424` (etag = mtime nanoseconds); `CA/Backend/CasObjectStorageBackend.cpp:347-362` (`etagComfortablyInThePast`), `:396-416` (`emuPruneTokenState`), `:447-465` (`emuMintToken`)
- Impact: on a filesystem whose mtime granularity is coarser than the rewrite interval for a hot key, two rewrites are indistinguishable and a stale token validates; and if the local wall clock is stepped back, or object mtimes come from a clock ahead of ours, pruning never fires and token state grows without bound.
- Trigger: emulated mode over NFS/CIFS, or an NTP step backwards.
- Reported by: bc6-7, bc6-8

### CAS-068 -- `putIfAbsentControlled` swallows deterministic local failures and reports them as ambiguity
- Class: INTEGRITY
- Anchor: `CA/Backend/CasRequestControl.cpp:271-281`, against the four siblings at `:336-342`, `:396-402`, `:467-473`, `:535-541` which all rethrow first; consumer `CA/Pool/CasRefLedger.cpp:2453-2457`, `:2706-2719`
- Impact: a `LOGICAL_ERROR`, `BAD_ARGUMENTS`, `NOT_IMPLEMENTED` or `CORRUPTED_DATA` -- provably never landed -- is converted into an UNCERTAIN outcome that wedges the ref lane into recovery instead of surfacing the bug.
- Trigger: `Backend::promoteStaged`/`resurrect` throwing `NOT_IMPLEMENTED`, or any decode failure inside the conditional write.
- Reported by: bc3-4, tier2-3

### CAS-069 -- empty catches reclassify transient read failures as corruption
- Class: INTEGRITY
- Anchor: `CA/Gc/CasGc.cpp:2633-2648` (empty catch at `:2641`, consequence at `:2645-2648`, `:2776-2781`), `:2788-2801` (empty catch at `:2798`, consumer `:2803`)
- Impact: a `MEMORY_LIMIT_EXCEEDED` on a large `gc/state` is indistinguishable from genuine corruption and drives a full baseline rebuild -- which by CAS-025 permanently orphans unreferenced blobs. A malformed generation key is skipped with no log, under-computing `max_gen`.
- Trigger: any transient failure decoding `gc/state`, or one malformed key under the generation prefix.
- Reported by: bc3-9, bc3-12

### CAS-070 -- remount self-healing is permanently disabled by a lost wakeup, a latched flag, or one unhandled throw
- Class: LIVENESS
- Anchor: `CA/Pool/CasMountRuntime.cpp:341-369` (`remount_running` latched at `:353` before a throwable `ThreadFromGlobalPool` at `:354`; gates at `:346`, `:349` vs the store at `:367`), `:384-397` (`stopRemountThread` lost wakeup), `:353-368` (thread body has no handler)
- Impact: after a fence-out the mount stays fenced closed until process restart -- writes to the disk fail permanently -- because the flag says a remount is running when none is, or the worker died on an exception with no handler.
- Trigger: thread-pool saturation at `scheduleRemount`, or a renewal loss racing the worker's final store.
- Reported by: concurrency-5, concurrency-6, bc3-8, tier2-6

### CAS-071 -- mount and pool state is read and written outside the mutex that guards it
- Class: CONCURRENCY
- Anchor: `CA/Pool/CasMountRuntime.h:164` (`mount_keeper` plain `unique_ptr`, replaced from the remount thread at `CA/Pool/CasPool.cpp:724-728`); `CA/Pool/CasServerRoot.cpp:741-746` (`prepareRenew` mutates before the lock at `:1013`, `:1028`), unguarded reads `:732-739`, `:846`, `:852`; `CA/ContentAddressedMetadataStorage.cpp:577-630` under `TSA_NO_THREAD_SAFETY_ANALYSIS`; `CA/Pool/CasEventDispatcher.cpp:30-34`
- Impact: keeper replacement races every reader of `mount_keeper`; fence/deadline state is torn between the renewal thread and `mayMutate()`; pool identity is published after the pool itself under a suppression, so `getPoolUUID()` can observe a half-initialized storage; the event sink can be replaced while being invoked.
- Trigger: a remount concurrent with any mount-state read; a lease renewal concurrent with a fenced write.
- Reported by: concurrency-7, concurrency-8, concurrency-11, concurrency-12

### CAS-072 -- staged-manifest debris cleanup tracks only one precommit binding and can delete a body a live precommit still owns
- Class: DATA-LOSS
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:866-884` (skips only `precommit_manifest`/`precommit_target_ns`), `:587-590` (`precommitAdd` overwrites the single triple), `:807-821`, `:107-112`
- Impact: a build that precommits twice and then aborts leaves the first precommit binding durable in the ref log while its manifest body is deleted -- a durable reference to a missing object.
- Trigger: any `PartWriteTxn` calling `precommitAdd` more than once (two refs, or a re-stage retry) that is then abandoned.
- Reported by: tla-fidelity-6

### CAS-073 -- the condemn marker is not incarnation-scoped, is accepted as its own proof, and is never cleared
- Class: INTEGRITY
- Anchor: `CA/Formats/CasBlobMetaFormat.h:14-22` (no token/incarnation), `CA/Gc/CasGc.cpp:95-97` (`writeCondemnedMeta` returns true when already `Condemned`), `:1356`, `:100-106`; spare path `CA/Gc/CasBlobInDegree.cpp:381` with `CA/Gc/CasGc.cpp:691` (in-process only), `:428-448` (`closeBlob`)
- Impact: a digest that goes condemn -> resurrect -> re-condemn cannot be distinguished by the marker, so a marker written for a previous incarnation licenses deleting the new one; a spared blob keeps its durable `Condemned` marker forever, and `closeBlob` can only record a replacement for an entry the round already touched.
- Trigger: condemn racing a resurrect or a fresh dedup-adopt.
- Reported by: tla-fidelity-4, gc-protocol-6, tier3-8

### CAS-074 -- generation prune advances a monotone cursor past still-referenced generations, and the compensating hand-off is one-shot
- Class: LEAK
- Anchor: `CA/Gc/CasGc.cpp:2456-2500` (returns on `suppress_destructive` at `:2460`; cursor advances even when skipping at `:2479-2484`; commit at `:2496`), compensating hand-off `:829-856`
- Impact: a generation that is still referenced when the cursor passes it, and then leaves the seal during a suppressed round or a budget-exhausted hand-off, leaks its objects permanently -- nothing revisits `snap_pruned_through`.
- Trigger: a cold gc-shard carrying a generation by reference, plus one suppressed or budget-limited round.
- Reported by: gc-protocol-4, tier3-1

### CAS-075 -- the blob body is durable before its meta marker, and no GC phase enumerates bodies
- Class: LEAK
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:423-429` (`streamIfAbsent` returns `Done`, then `writeFreshMetaClean`), also `:463-465`, `:471-474`
- Impact: a crash in the window leaves a body with no meta object; because the only lister of `blobsPrefix()` is fsck, that body is never reclaimed and never reported by the `clean()` verdict.
- Trigger: a crash between the body PUT and the meta PUT.
- Reported by: crash-consistency-2

### CAS-076 -- GC seals a generation before committing `gc/state`, so repeated crashes accumulate orphan generations
- Class: LEAK
- Anchor: `CA/Gc/CasGc.cpp:2254` (`putDeterministicArtifact(foldSealKey(new_generation, attempt))`) versus the commit at `:804`; the rebuild has the same shape at `:2980`/`:2987`
- Impact: each crash in the window leaves a complete-looking seal for a generation no `gc/state` references; nothing prunes generations the state never adopted.
- Trigger: repeated crashes during the seal-to-commit window.
- Reported by: crash-consistency-7

### CAS-077 -- a permanently lost node pins its own manifest debris as unreclaimable
- Class: LEAK
- Anchor: `CA/Gc/CasOrphanManifestSweep.cpp:373-387` (`prefixEligible`), floor lookup `:40-56`, fence-out `CA/Pool/CasServerRoot.cpp:455`
- Impact: the sweep needs the owning mount lease to compute a watermark floor; once the node is gone its debris is protected forever, and the only verb that removes the lease also erases its data (CAS-063).
- Trigger: node loss without decommission.
- Reported by: crash-consistency-3

### CAS-078 -- the namespace janitor rewinds its durable cursor to the beginning on a transient LIST failure
- Class: LEAK
- Anchor: `CA/Gc/CasNamespaceJanitor.cpp:22-31` (`runOnePage`, cursor reset on list error)
- Impact: one S3 5xx or throttle discards all prior progress, so on a pool with many dead-life namespaces the janitor -- already limited to one 1,000-key page per round -- can make no net progress at all.
- Trigger: one failed LIST against the namespace prefix.
- Reported by: tier3-9

### CAS-079 -- ref-object trimming is starved by any concurrent catalog mutation anywhere in the pool
- Class: LEAK
- Anchor: `CA/Gc/CasGc.cpp:2320-2336` (revalidation requires an unchanged catalog token), `:2396-2412` (returns out of the whole function on the first refusal)
- Impact: the ref catalog is one object shared by all namespaces, so any CREATE/DROP of any table between the fold's catalog read and the cleanup phase aborts all ref-log and snapshot trimming for the round -- on a busy cluster, most rounds.
- Trigger: any table lifecycle event in the pool during a GC round.
- Reported by: tla-fidelity-10

### CAS-080 -- a snapshot published without a checkpoint advance is not re-driven on a quiescent namespace
- Class: CORRECTNESS
- Anchor: `CA/Pool/CasRefLedger.cpp:2937-3035` (ckpt CAS at `:3035`), driver at `:2765` invoked only from the write path
- Impact: a crash between the snapshot publish and the checkpoint advance leaves the namespace paying full log replay on every recovery, and nothing repairs it until the table is written again.
- Trigger: a crash in that window on a table that then goes idle.
- Reported by: crash-consistency-5

### CAS-081 -- S3 staging residue is retained on abort and swept only for one's own `server_root_id`, silently and best-effort
- Class: LEAK
- Anchor: `CA/ContentAddressedTransaction.cpp:148-172` (S3 objects removed only in `else if (committed)`, tracking cleared unconditionally at `:170`); `CA/Pool/CasServerRoot.cpp:1140-1168` (`noexcept`, best-effort, own srid only, no age/incarnation filter); invoked once at `CA/ContentAddressedMetadataStorage.cpp:596-607`
- Impact: whole part-file plaintext persists in the bucket after any killed INSERT, mutation, cancelled MOVE or failed migration; if the node never returns with the same `server_root_id` (pod re-creation, macro change) nothing ever deletes it, and no tool lists it. Two disks sharing an srid sweep each other's live staging.
- Trigger: `staging_backend=s3` plus any abort, or a node identity change.
- Reported by: ad2-9, ad4-8, alter-merge-mutation-3, bc2-5, bc3-10, ad6-13

### CAS-082 -- there is no multipart-upload hygiene anywhere in CAS, and capability-probe debris is explicitly excluded from the residual scan
- Class: LEAK
- Anchor: exhaustive search of the CAS tree for `multipart` matches nothing; `src/IO/WriteBufferFromS3.cpp:244-276`, `:469-492`; `CA/Backend/CasProbe.cpp:20-32`, `CA/Backend/CasSentinelProbe.cpp:17-20`, `:43-44`
- Impact: a SIGKILL/OOM while streaming a large blob or staging object leaves an incomplete multipart upload that is billed, invisible to fsck's `physical_bytes`, and never aborted; probe objects left behind on exactly the mis-provisioned buckets the probe exists to detect are never swept.
- Trigger: a crash during a multipart upload; or a probe cleanup failure.
- Reported by: ad6-11, ad2-11, ad6-12

### CAS-083 -- lightweight `DELETE` and mutations free the deleted rows' bytes only for rewritten files
- Class: LEAK
- Anchor: `CA/ContentAddressedTransaction.cpp:782-829` (`createHardLink` re-adopts the same `BlobRef` under the new path), `CA/Parts/PartFolderAccess.cpp:442-473` (`repointRef`)
- Impact: `DELETE FROM ... WHERE` (mask only) and any partial-rewrite mutation republish the surviving entries against the same blobs, so deleted row bytes remain in the pool indefinitely -- relevant wherever deletion is expected to be an erasure.
- Trigger: lightweight `DELETE`, or a mutation that rewrites a subset of column files.
- Reported by: ad2-4

### CAS-084 -- reclaimed blobs are never evicted from the node-local filesystem cache
- Class: LEAK
- Anchor: `src/Disks/DiskObjectStorage/DiskObjectStorageCache.cpp:21-23` (the same metadata storage is reused, no cached-object-storage interposition); nothing in the CAS tree calls `removeCacheIfExists`
- Impact: after GC deletes a blob, its bytes remain on local disk in the filesystem cache with no invalidation -- capacity held indefinitely, and deleted content still readable locally.
- Trigger: a CAS disk with a filesystem cache: SELECT a part, drop it, let GC reclaim.
- Reported by: ad2-13

### CAS-085 -- `always_use_copy_instead_of_hardlinks=1` makes every CAS clone and mutation throw `NOT_IMPLEMENTED`, and nothing rejects the setting
- Class: FEATURE-GAP
- Anchor: `CA/ContentAddressedTransaction.cpp:363-366`, `:492-495` (`generateObjectKeyForPath`/`createMetadataFile` -> `notYet()`), reached from `src/Storages/MergeTree/MutateTask.cpp:2490-2494`, `:2513-2517`, `:3306-3311`
- Impact: the setting is accepted silently on a CAS table and then permanently breaks every `ALTER ... UPDATE/DELETE`, `MATERIALIZE INDEX`, `ATTACH/REPLACE PARTITION`, `FREEZE`, `MOVE PARTITION TO TABLE` and backup-restore clone on that table.
- Trigger: `ALTER TABLE cas_tbl MODIFY SETTING always_use_copy_instead_of_hardlinks = 1`, then any of the above.
- Reported by: idisk-contract-4, ad4-2, alter-merge-mutation-2

### CAS-086 -- IDisk directory and metadata queries deviate from the contract their generic callers rely on
- Class: CORRECTNESS
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:1293-1305` (`isDirectoryEmpty` returns true for every part dir), `:1172-1194` (`getLastModified` throws for directories `existsDirectory` reports present; never consults the manifest; ms->s truncation; epoch 0 means two different things), `.h:121` (`getHardlinkCount` constant 0 while `supportsHardLinks()` is true); `CA/ContentAddressedTransaction.cpp:683-780` (silent no-op removes on unclassified paths), `:831-834` (`setLastModified` no-op)
- Impact: `removeDirectory`'s non-empty guard never fires on CAS so a populated part directory is dropped without error; `getLastModified` dates files that do not exist and throws for directories that do; `getRefCount` always answers "not shared"; and removes on paths CAS cannot classify report success having done nothing.
- Trigger: `DiskObjectStorage::removeDirectory` on a part dir; `system.parts_columns` on a CAS part; `removeSharedRecursive` on an intermediate path.
- Reported by: idisk-contract-5, idisk-contract-6, idisk-contract-7, idisk-contract-8, bc6-1, bc6-2, bc6-3, bc6-4

### CAS-087 -- the part-path parser lets a component named `detached`/`moving` outrank part-dir detection, and silently reinterprets unclassified part dirs as table-level files
- Class: CORRECTNESS
- Anchor: `CA/Parts/PartPathParser.cpp:140-162` (scans for any `detached`/`moving` component before `looksLikePartDir`), `:101-132` (`looksLikePartDir` requires `_<num>_<num>_<num>`), `:274-277` (catch-all)
- Impact: on a non-Atomic layout a database or table literally named `detached` or `moving` misroutes every part in it; and any part directory whose name does not match the heuristic is stored as a table-level file rather than rejected, so the misclassification is discovered only on read.
- Trigger: an Ordinary-layout data path containing a `detached`/`moving` component; or a future part-name format.
- Reported by: mergetree-part-support-6, mergetree-part-support-7

### CAS-088 -- `resurrect` is an unconditional, budget-free, fence-unchecked overwrite that returns a token it did not write
- Class: INTEGRITY
- Anchor: `CA/Backend/CasObjectStorageBackend.cpp:814-856`; callers `CA/Pool/CasPartWriteTxn.cpp:457-466`, `:470-475`
- Impact: the fence check asserts only against the generation captured one line earlier, the write is not conditional, and the returned token is not the token of the bytes that landed -- so two writers (or a writer racing the tail of a GC delete) on one condemned blob can each believe they own the object.
- Trigger: two writers touching the same condemned digest.
- Reported by: write-protocol-3

### CAS-089 -- the blob envelope is written but never read back: offset comes from pool meta, its version is unchecked, and its identity field is silently truncatable
- Class: INTEGRITY
- Anchor: `CA/Pool/CasManifestReader.cpp:137-144` (`offset = meta.blob_header_len`); `CA/Formats/CasBlobEnvelopeFormat.cpp:74-87` (write truncates with no error), `:102` (version stamped), `:146` (`decodeEnvelopeHeader`'s `object_size` parameter unnamed); the only caller of the decoder is `CA/Tools/CasInspect.cpp:571`
- Impact: any object whose envelope is not exactly the pool-global `blob_header_len` is read at the wrong offset and the mismatch is never detected; the self-describing identity that would catch it is truncated on write and discarded on read; the stamped version is never enforced on a production read path.
- Trigger: any divergence between an object's real envelope length and the persisted `blob_header_len`.
- Reported by: read-protocol-2, upgrade-compat-6, bc4-7

### CAS-090 -- encryption interactions: SSE-C breaks staging promotion, CAS metadata stays plaintext, AES-CTR carries no MAC, and a pool cannot be re-keyed
- Class: SECURITY
- Anchor: `src/IO/S3/Client.cpp:1273-1287` (SSE-C headers on every request; no copy-source SSE-C headers exist in `src`); `CA/Formats/CasPartManifestFormat.h:20-39` with `CA/ContentAddressedTransaction.cpp:505-511`, `:638-654` (names, sizes and <=1 MiB bodies in the manifest); `src/IO/FileEncryptionCommon.h:21-30`, `:114-139` (CTR only, no auth tag); `src/Disks/DiskEncrypted.cpp:221-247`
- Impact: with `staging_backend=s3` plus SSE-C the server-side conditional copy fails; client-side encryption never covers file names, sizes or small-file bodies; a single flipped ciphertext byte is undetectable over a store that never re-verifies digests (CAS-008/CAS-009); and every historical key must be retained forever because CAS blobs are immutable and shared, so rotation cannot re-key a pool.
- Trigger: SSE-C plus S3 staging; or any encrypted-over-CAS deployment.
- Reported by: encryption-4, encryption-5, encryption-7, encryption-8, encryption-9

### CAS-091 -- `Layout::checkNamespace` accepts `.` and `..` segments, unlike every other CAS path validator
- Class: SECURITY
- Anchor: `CA/Formats/CasLayout.cpp:295-319`, against `CasLayout.h:25-30`, `CA/Primitives/CasCodecUtil.h:47-64`, `CA/Formats/CasPartManifestFormat.cpp:184-193`
- Impact: a namespace containing `..` produces object keys containing `..`; harmless as an S3 key component, but under the auto-selected emulated mode over local object storage those keys are joined onto a filesystem root, so the traversal is real.
- Trigger: a namespace derived from a path with a `..` segment on a CAS-over-local disk.
- Reported by: security-5

### CAS-092 -- the write fence and the request it admits are on different clocks, and one cross-node wall-clock liveness gate survives
- Class: CORRECTNESS
- Anchor: `CA/Pool/CasMountRuntime.cpp:57-62` (`CLOCK_BOOTTIME`), `:101-111`, `:212-213` against `CA/Backend/CasRequestControl.cpp:80-83` (`steadyClockNowMs`); `CA/Pool/CasServerRoot.cpp:196-209` (`expires_at_ms > now_ms` from `system_clock` via `CA/Pool/CasPool.cpp:386-396`); `CA/Pool/CasMountRuntime.cpp:60`, `CA/Pool/CasServerRoot.cpp:54` (`CLOCK_BOOTTIME` is Linux-only)
- Impact: a host suspend or VM live-migration between fence admission and the conditional PUT is invisible to the deadline that admitted it; the decommission epoch mint decides another node's liveness by comparing its own wall clock to a stamped deadline; and both clock reads are unguarded on Darwin/FreeBSD targets.
- Trigger: VM pause/live-migrate during a ref append; `SYSTEM CAS DROP MEMBER` from a node whose clock is ahead.
- Reported by: bc6-5, bc6-6, bc6-9

### CAS-093 -- the temp text-index directory lives inside the part, publishes a ref early, and its cleanup is a silent no-op
- Class: CORRECTNESS
- Anchor: `src/Storages/MergeTree/TextIndexUtils.cpp:601-609` (own `beginTransaction()` on a sibling dir *inside* the part), committed at `MutateTask.cpp:1939-1941` / `MergeTask.cpp:2235-2236`, cleaned at `MutateTask.cpp:2012-2014` / `MergeTask.cpp:2311-2313`
- Impact: a separate CAS transaction publishes a ref under the part before the part exists, and the `removeRecursive` meant to clean it up is one of the silent no-ops of CAS-086, so the temp ref and its blobs survive.
- Trigger: `MATERIALIZE INDEX` for a `text` index, or any merge rebuilding one, on a CAS disk.
- Reported by: alter-merge-mutation-4

### CAS-094 -- `GC REBUILD` refusals and failures are not side-effect free, and the residue is adoptable and can trip a fail-closed check
- Class: INTEGRITY
- Anchor: `CA/Gc/CasGc.cpp:2811-2824` (`flush_shard` writes run objects mid-scan), `:2832`, refusals `:2885-2888`, `:2990-2992`, seal at `:2980` before the state CAS at `:2987`; attempt numbering `:2810`, `:2816`, `:2976-2978` vs the normal round's `attempt = lease.seq`
- Impact: a refused rebuild reports `performed=0` while leaving complete-looking run objects and a fold seal behind, which a later round can adopt or reject as an "impossible" state.
- Trigger: a rebuild on a pool large enough to flush a shard, then any refusal (missing manifest, lease steal).
- Reported by: gc-rebuild-feature-4

### CAS-095 -- `cas-gc-dryrun` is not a preview of the next round and is silently empty in exactly the disaster state it exists for
- Class: OBSERV/DAY2
- Anchor: `CA/Gc/CasGc.cpp:3017-3080`, empty return at `:3021-3023`, checksum verification at `:3076`; shipped description at `programs/disks/CommandCaGcDryRun.cpp:23`
- Impact: on a pool whose `gc/state` is absent or unreadable the output is `preview_deletes=0`, indistinguishable from "nothing will be deleted"; one bad run object suppresses the whole output.
- Trigger: `cas-gc-dryrun` on a pool with a damaged `gc/state`.
- Reported by: gc-rebuild-feature-5

### CAS-096 -- the rebuild reports almost nothing about the quality of the baseline it blesses
- Class: OBSERV/DAY2
- Anchor: `CA/Gc/CasGc.h:48-63` (`RebuildReport`); dropped-row counters computed at `CA/Gc/CasGc.cpp:208-250` and exposed by `RefPlan::droppedParentRows()`/`droppedHolds()` but never read on the rebuild path (the normal round does surface them at `:529-531`)
- Impact: a rebuild that silently drops a parent row and its hold reports `performed=1` and nothing else, so an operator cannot tell an accurate baseline from a lossy one.
- Trigger: rebuild a pool whose prior seal carries a hold for a life no longer in the catalog cut.
- Reported by: gc-rebuild-feature-7

### CAS-097 -- no surface names namespaces or raw keys, and `cas-inspect` cannot decode 8 of the 18 CAS formats
- Class: OBSERV/DAY2
- Anchor: `src/Storages/System/StorageSystemContentAddressedMounts.cpp:55` (`wedged_namespace_count` only); `CA/Tools/CasInspect.cpp:517-576` (no branch for `_pool_meta`, `cas/ref_catalog`, `gc/maintenance_state`, `gc/hb`, `owner`, `epoch`, outcomes), `:329-335` (drops `RefCoverage::hold`), `:532-562` (namespace-state branch falls through and mis-decodes `_files/` names ending in `mount`/`fold_seal`), `:358` (sentinels rendered literally); `programs/disks/CommandCaInspect.cpp:26-27` (requires a raw key no shipped command can enumerate)
- Impact: every wedge state is countable but not nameable; the operator cannot list raw pool keys, and for the keys they can guess, the inspector either refuses, mis-decodes, or omits the field that explains why GC is refusing to work.
- Trigger: any attempt to localize a wedged namespace or read a control object.
- Reported by: ad3-7, ad3-13, tier4-2, tier3-7, tier4-11, tier3-17

### CAS-098 -- GC health is process-local and ephemeral, `GC STOP` is node-local and unobservable, and the counters that would show a stopped reclaimer are misleading
- Class: OBSERV/DAY2
- Anchor: `CA/Gc/CasGcScheduler.cpp:312-327` (`gcHealth`), `:170-172` (`pending_reclaim` monotone), `:67-79`, `.h:74` (`ever_succeeded` computed, never exposed); `src/Storages/System/StorageSystemContentAddressedMounts.cpp:52-55`, `:177-191`; `src/Common/CurrentMetrics.cpp:239-241` (no gauges), `src/Common/ProfileEvents.cpp:803` (`CASGCClampSuppressedPasses` fires every round by construction)
- Impact: `last_success_age_seconds=0` means both "never led" and "succeeded just now"; `is_leader=0` conflates stopped, follower and crashed; `GC STOP` does not survive restart and is invisible to any other node; `pending_reclaim` never sheds spared or replaced entries, so it grows monotonically; and the one counter that would flag a shut destructive gate is useless.
- Trigger: `SELECT * FROM system.cas_mounts` on any replica; `SYSTEM CAS GC STOP`.
- Reported by: ad3-8, ad3-9, ad3-10, tier3-3, tier3-10

### CAS-099 -- rolling restart and planned node removal have no quiesce, drain or leadership-handoff verb
- Class: OBSERV/DAY2
- Anchor: `CA/Gc/CasGcScheduler.cpp:67-79`; `CA/Pool/CasPool.cpp:562-571` (`~Pool`), `:455-461` (decommission refusal); `src/Interpreters/InterpreterSystemQuery.cpp:1048-1060`
- Impact: the only shutdown is "stop and join", so a rolling restart drops GC leadership abruptly (see CAS-003) and a planned removal has no ordered path between "in service" and the destructive decommission verb.
- Trigger: any rolling restart or planned node removal on a CAS pool.
- Reported by: ad3-11

### CAS-100 -- fsck skips whole check families yet still reports a clean, non-partial result
- Class: OBSERV/DAY2
- Anchor: `CA/Tools/CasFsck.cpp:654` (`if (!unref_hashes.empty())` gates run-checksum verification), `:677`, `:707` (stale-edge check gated on `detail`, which the SQL path never sets), `:831-866` (namespace-scoped branch skips families), `:903-920` (`partial` set only on timeout), `:824-829` (counters computed then discarded)
- Impact: on a healthy pool the source-edge checksums are never verified; from SQL the stale-edge finding is unreachable; a namespace-scoped run reports the same "clean" as a full run; and two crash-residue counters are computed and thrown away.
- Trigger: any fsck run; `cas-fsck --namespace <ns>`; `SYSTEM CAS FSCK`.
- Reported by: tier3-4, tier3-5, tier3-6, tier3-18

### CAS-101 -- GC round counters are derived from budget-truncated logs, and phase observability reports constants and the wrong round
- Class: OBSERV/DAY2
- Anchor: `CA/Gc/CasGc.cpp:652-690`, `:732-768` (report fields replayed from the truncated outcome log), `:534`, `:853` (constant and pre-budget metrics), `:512`, `:564-595` (pre-increment round with post-fold generation); `CA/Gc/CasGcScheduler.cpp:141` (phase rows copy the Start record, so `round = 0`)
- Impact: after a large DROP -- precisely when an operator watches these numbers -- the round undercounts real deletes; `system.cas_gc_log` phase rows cannot be filtered by round; and fold events carry a different round number than the delete events of the same round.
- Trigger: a round whose cohort exceeds `gc_round_outcome_entry_budget` (default 5000); any `SELECT ... FROM system.cas_gc_log WHERE round = N`.
- Reported by: tier3-2, tier3-13, tier3-14, tier3-16

### CAS-102 -- 11 of the 156 CAS ProfileEvents can never fire, and server-root I/O is counted as GC I/O
- Class: OBSERV/DAY2
- Anchor: `CA/Backend/CasInstrumentedBackend.cpp:109-122` (`classifyCasNs` never returns `CasNs::Server`), event table `:81-107`, enum `.h:9-18`, shipped descriptions `src/Common/ProfileEvents.cpp:844-854`
- Impact: every mount, heartbeat, epoch bump and lease renewal on every pool is attributed to GC, and eleven documented counters are permanently zero -- so lease/mount request volume cannot be measured or alerted on.
- Trigger: any CAS mount, always.
- Reported by: tier4-1, tier2-11

### CAS-103 -- savings and outcome counters are incremented before the outcome they claim is decided
- Class: OBSERV/DAY2
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:155-175` (`CASBlobHeadFirst` `:155`, `CASBlobBodyPutAvoided` `:159`, `CASBlobDeduplicationCacheHit` `:161`, then `observeAndAdmit` at `:164` and a swallowed `ABORTED` at `:169-173`, then a real upload at `:178-191`)
- Impact: dedup-savings metrics count bytes that were in fact uploaded, so the headline value of the feature is over-reported exactly on the condemned/untrusted path where resurrection was required.
- Trigger: a HEAD-first hit whose body is not admissible as evidence.
- Reported by: tier4-4, write-protocol-5

### CAS-104 -- audit-event dispatch funnels read and write hot paths through one mutex, and the shipped config enables the sink by default
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasEventDispatcher.cpp:17-44` (single mutex, inline drain), gate `CA/Primitives/CasEvent.h:55-63`, event struct `:31-45` (7 Strings plus a `std::map`), emitters `CA/Parts/PartFolderAccess.cpp:217-229` (every resolve), `CA/Pool/CasManifestReader.cpp:61-71`, `CA/Gc/CasGc.cpp:1297-1313` (per candidate blob)
- Impact: every ref resolve and manifest read builds a multi-String event and serializes on one mutex, by default, on the shipped configuration -- worst with many concurrent part loads against one pool.
- Trigger: normal read/write traffic with the shipped config.
- Reported by: performance-7

### CAS-105 -- the whole mount/lease/request budget and seven pool-level caps are unreachable from configuration, so their validation is dead code
- Class: CONFIG
- Anchor: `CA/ContentAddressedSettings.cpp:29-58` (the complete shipped list); `CA/Pool/CasPool.h:64-92` (`gc_frontier_probe_budget`, `gc_fold_threshold`, `gc_fold_max_defer_rounds`, `gc_stuck_removal_rounds`, `rebuild_edge_budget`, snapshot thresholds, `ref_table_cache_bytes`); `CA/Backend/CasRequestControl.h:82-94`, `:96-134` (`validateCasRequestBudget` validates nothing about `mount_renew_period_ms`)
- Impact: `mount_lease_ttl_ms`, `mount_renew_period`, `attempt_timeout_ms`, `operation_deadline_ms`, `max_attempts`, the backoffs and the recovery retries are always the struct defaults and are never assigned anywhere in the tree, so none of the scaling problems in this report can be tuned and the validator that exists can never fire.
- Trigger: any attempt to tune CAS pacing or memory for a workload.
- Reported by: tier2-7, ad5-11, codeonly-line-9

### CAS-106 -- the non-CAS config key allowlist is a fixed 18-entry set, so ordinary object-storage keys abort disk registration
- Class: CONFIG
- Anchor: `CA/ContentAddressedSettings.cpp:23-27` (`non_cas_keys`), `:94-99` (every other child key is fed to `impl->set`), `:119-137`; `MetadataStorageFactory.cpp:233-237`
- Impact: putting a standard `<connect_timeout_ms>`, `<max_connections>`, `<request_timeout_ms>`, `<support_batch_delete>`, `<role_arn>` or SSE key inside a `cas` disk element fails the disk load rather than being passed through, and numeric ranges are unchecked for the keys that are accepted.
- Trigger: declare a CAS disk over S3 with any ordinary S3 tuning key.
- Reported by: tier2-8, tier4-5

### CAS-107 -- no CAS setting can be changed by config reload, the ignore is silent, and a removed CAS disk keeps its mount
- Class: CONFIG
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/IMetadataStorage.h:340-343` (default no-op `applyNewSettings`, not overridden by CAS); `DiskObjectStorage.cpp:961-987`; `DiskSelector.cpp:176-183`, `:192-219` (a disk removed from config only warns)
- Impact: an operator editing any CAS setting sees the reload succeed with no effect and no message; deleting the disk from config leaves the mount lease held, so the slot cannot be reclaimed by anyone else.
- Trigger: edit any CAS setting, or remove a CAS disk, then reload configuration.
- Reported by: ad7-3

### CAS-108 -- dead code and test-only seams are compiled into the production binary
- Class: TEST-GAP
- Anchor: `CA/Backend/CasInMemoryBackend.{h,cpp}` (487 lines, 28 methods including `failNextCasPut`, `injectAmbiguousPutIfAbsent`, `setHoldDeletes`); `CA/Gc/CasGcShardPlan.h:24-40` (`manifestCleanupShard` -- which uses `std::hash` -- and `ShardReducer`, no callers); 264 `ForTest` seams across 20 CAS headers; `CA/Pool/CasRefCatalog.cpp:147-156` (file-scope `std::function` hook read and swapped on every namespace creation); `CA/ContentAddressedMetadataStorage.h:236-247` invoked on the commit path
- Impact: fault-injection surfaces link into `clickhouse-server`; a process-global, unsynchronized test hook is read (and racily swapped) on every namespace creation and every part commit, and one test seam drops a gate its production twin enforces. The unused shard-reduce API is also the only validation of `gc_shards > 1`, so that path has no caller at all.
- Trigger: any build of `dbms`; any namespace creation or part commit.
- Reported by: coverage-map-1, coverage-map-2, coverage-map-3, tier4-8, tier4-9, tier3-19

### CAS-109 -- there is no deterministic crash-at-step-N harness, and settings validation has one fail-closed test for the whole surface
- Class: TEST-GAP
- Anchor: `tests/integration/test_cas_shared_pool/test.py:265`, `test_cas_drop_pool_member/test.py:146`, `test_cas_gc_sharded/test.py:255`; `src/Disks/tests/gtest_cas_settings.cpp` (6 tests)
- Impact: every crash-consistency finding in this round (CAS-005, CAS-006, CAS-072, CAS-075, CAS-076, CAS-080) describes a window that only a step-injecting harness can pin, and none is covered; the 29-setting surface has essentially no validation coverage.
- Trigger: n/a -- absence of coverage.
- Reported by: test-coverage-fuzzing-6, test-coverage-fuzzing-7

### CAS-110 -- `resolveRef`'s `allow_stale` is plumbed through two layers and silently discarded
- Class: CORRECTNESS
- Anchor: declared `CA/Pool/CasRefLedger.h:62-63`, forwarded `CA/Pool/CasPool.cpp:1135-1137`, definition `CA/Pool/CasRefLedger.cpp:214-215` (parameter unnamed, never read); callers that request stale tolerance: `CA/Parts/PartFolderAccess.cpp:283`, `:483`
- Impact: callers that explicitly ask for a cached/stale-tolerant resolve get the strict path instead -- they can block on recovery and can throw where they expect a cheap best-effort answer.
- Trigger: any `getView(..., CachedForLoad)` or the literal `true` at `PartFolderAccess.cpp:483`.
- Reported by: codeonly-line-4, tier1-4

### CAS-111 -- the per-namespace 64 MiB ref-table admission cap fails writes permanently and non-retryably at roughly 610k refs
- Class: PERF/SCALE
- Anchor: `CA/Formats/CasRefLogFormat.h:50` (`ref_removal_max_bytes = 64 MiB`), `CA/Formats/CasRefSnapshotFormat.h:40`, `CA/Pool/CasRefLedger.cpp:859-861`, `:2161-2169` (`admits()` -> `LIMIT_EXCEEDED`)
- Impact: once one more transition would push the encoded snapshot or terminal-removal transaction past 64 MiB, every write to that table fails and retrying cannot help; reached by ordinary part accumulation on a wide-partitioned table.
- Trigger: a single table accumulating enough committed refs.
- Reported by: ad5-5

### CAS-112 -- every ref append re-reads and linearly rescans the pool-global ref catalog
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasRefLedger.cpp:2313-2325`, `:2292`; `CA/Pool/CasRefCatalog.cpp:109`, `:120` (each CAS iteration re-reads), `:139-143` (`std::find_if` over a vector kept sorted by `lower_bound`), `:163` (full deep copy per mutate)
- Impact: at least two full catalog GETs plus linear scans per part commit, with cost scaling in the number of namespaces in the pool -- entirely unrelated to the namespace being written -- and a whole-catalog deep copy and re-encode on every mutation.
- Trigger: every ref-log chunk commit; worst with many tables in one pool.
- Reported by: ad5-8, performance-10

### CAS-113 -- encoded-size caps are validated only after the oversized buffer has been built
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:541-544` (`encodePartManifest` then the cap check); `CA/Formats/CasRefSnapshotFormat.cpp:115-133`; `CA/Formats/CasRefLogFormat.cpp:49-64` with `:360`
- Impact: hitting a 256 MiB object cap requires first materializing 256 MiB, so the guard converts an over-limit condition into a memory spike plus a failure rather than an early rejection.
- Trigger: any object whose encoding lands over its cap (e.g. a manifest near `kMaxManifestEntries`).
- Reported by: ad5-9

### CAS-114 -- recovery must seal every skipped writer epoch one at a time, so first touch of an idle table costs O(mount generations) durable writes with no cap
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasRefLedger.cpp:740-824` (per-epoch seal loop, `slotOccupy` at `:772-774`, `publish_recovered_frontier` at `:783` doing a `_ckpt` CAS plus an exact re-read), density enforced by `CA/Formats/CasRefLogFormat.cpp:239-246`
- Impact: writer epochs are minted per mount for the whole server root while the seal chain is per namespace, so a table last written N mounts ago pays N sequential durable write pairs on first touch, uncapped.
- Trigger: first write to a long-idle table on a frequently restarted server.
- Reported by: tier1-3

### CAS-115 -- cache weight functions under-account their entries
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasManifestReader.h:49-58` (`PartManifestWeight` misses ~2x of the real per-entry footprint); `CA/Pool/CasPool.h:464-471` (`DedupWeight` returns a constant 64, ~3.1x under actual cost) with `CA/Pool/CasPool.cpp:165-168` (constructed with `NO_MAX_COUNT`, no entry-count backstop)
- Impact: both byte budgets over-admit by a large factor, so `deduplication_cache_bytes` and the manifest decode cache use several times their configured memory -- on top of the view cache in CAS-045 which does not account at all.
- Trigger: any pool writing more than ~1M distinct blobs; any wide-manifest working set.
- Reported by: bc5-4, ad5-6, performance-12

### CAS-116 -- staging is quadratic in the number of files in a part
- Class: PERF/SCALE
- Anchor: linear `std::erase_if` over the staged vector at `CA/ContentAddressedTransaction.cpp:510`, `:652`, `:810`, `:827`, `:930`, `:1051`, `:1064`, `:1076-1078`; lookups `:379-381`, `:448`
- Impact: every staging mutation rescans all prior staged entries, and `moveDirectory` re-scans the destination set once per source entry, so wide tables and many-projection parts pay O(F^2) before any I/O.
- Trigger: a part with many files -- wide tables, many projections or secondary indexes.
- Reported by: bc5-6, performance-5

### CAS-117 -- one object plus one meta object plus a 256-byte envelope per part file
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasManifestReader.cpp:133-144` (one `blobKey` per entry, no packing or shared container in the entry model at `CA/Formats/CasPartManifestFormat.h:20-30`), `CA/Pool/CasPool.h:46` (`blob_header_len` default 256)
- Impact: a wide part of small files is dominated by per-object overhead -- two objects and a padded envelope per file -- inflating request count, listing cost and stored bytes far beyond the payload.
- Trigger: wide parts with many small column files.
- Reported by: bc5-7

### CAS-118 -- no cache can serve a read without a network round trip, and one logical read resolves the ref several times
- Class: PERF/SCALE
- Anchor: `CA/Pool/CasManifestReader.cpp:56-78` (`backend.head(key)` at `:58` before the cache probe at `:76-78`; the cache key includes the freshness token); `CA/Parts/PartFolderAccess.cpp:152` (`resolve()` before the view-cache probe at `:158-170`); `CA/ContentAddressedMetadataStorage.cpp:955-978`, `:1145-1170`, `:1374-1400`, `:1419-1445` (each independently routes and resolves)
- Impact: the decode and view caches cannot eliminate latency, only bytes; opening one part file costs several resolves and thousands of per-namespace mutex acquisitions on a wide part; and because there is no read snapshot, a size can come from one manifest and the bytes from another.
- Trigger: any part open; worst with a working set larger than the caches.
- Reported by: performance-6, read-protocol-4, bc5-9

### CAS-119 -- throttling amplification: conditional writes lose client-side retry and each throttled attempt costs an extra un-jittered GET
- Class: PERF/SCALE
- Anchor: `CA/Backend/CasObjectStorageBackend.cpp:628-639` (single-attempt client for conditional writes); `ObjectStorages/S3/S3ObjectStorage.cpp:895-913`; `CA/Backend/CasRequestControl.cpp:43-53`, `:178-188`, `:290-302`; `.h:84-93` (16 attempts, fixed backoff)
- Impact: under `SlowDown`/429 the retry moves from the SDK (jittered) to CAS (un-jittered, up to 16 times), and each retry adds a resolution GET -- so a throttled prefix is driven harder by the client than it was throttling for.
- Trigger: S3 throttling during an insert burst or a GC-heavy window.
- Reported by: ad6-9

### CAS-120 -- there is no relink fast path for local moves inside one CAS pool, and the CAS copy is serial
- Class: PERF/SCALE
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:702-718` sends every CAS destination through `copyDirectoryContentIntoTransaction` (`:652-679`), a plain recursive `readFile`/`writeFile` loop; contrast the interserver path at `DataPartsExchange.cpp:310-330`
- Impact: a `MOVE PARTITION TO DISK` or TTL move between two CAS disks on the same pool re-reads and re-writes every byte one file at a time, when a manifest relink is available -- the optimization already exists for the network path.
- Trigger: `MOVE PARTITION ... TO DISK 'cas2'` or a TTL move within one pool.
- Reported by: ad4-4

### CAS-121 -- a CAS table outside an Atomic database cannot be backed up at all, and every CAS backup re-reads every byte
- Class: FEATURE-GAP
- Anchor: `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:417-422` (`SUPPORT_IS_DISABLED`), `MergeTreeData::backupParts:7213-7231`; `Backups/BackupEntryWithChecksumCalculation.cpp:124-127` with `CA/ContentAddressedMetadataStorage.h:120` (`areBlobPathsRandom()` returns `false`)
- Impact: `BACKUP TABLE ordinary_db.cas_tbl` is refused outright; where backup does work, checksums are always computed `FromReading`, so even an incremental backup re-reads the entire dataset.
- Trigger: `BACKUP` of a CAS table in a non-Atomic database; any `BACKUP` of a CAS table.
- Reported by: ad4-6, ad4-7

### CAS-122 -- the `!`-prefixed critical-key escape hatch has no producer, and strict formats report an additive field as data corruption
- Class: COMPAT
- Anchor: `CA/Formats/CasTextFormat.cpp:240-242` (a `!` key throws `UNKNOWN_FORMAT_VERSION`), the only writer guarded by `EnvelopeHeader::emit_unknown_critical_key` which is never set true; `:243-244` (`Strict` raises `CORRUPTED_DATA`), strict formats `CasFormat.cpp:107-112`
- Impact: the forward-compatibility mechanism cannot be used by any writer, and its error code is on the non-recoverable path; meanwhile any additive field in `RefCkpt`, `RefCatalog`, `GcMaintenanceState`, `RunFile` or `FoldSeal` is misreported as corruption rather than a version problem, which routes an operator to fsck/rebuild instead of a rollback.
- Trigger: add any field to a strict format, or attempt to emit a critical key.
- Reported by: upgrade-compat-7, upgrade-compat-8

## Low severity

### CAS-123 -- there is no byte accounting outside `blobs/` and no reclaim-forecast surface
- Class: OBSERV/DAY2
- Anchor: `CA/Tools/CasFsck.cpp:578-596`, `CA/Tools/CasFsck.h:44-79`; `src/Interpreters/InterpreterSystemQuery.cpp:2397-2421`; `CA/Gc/CasGc.cpp:3043-3070` (`previewDeletes`)
- Impact: a bucket-versus-table byte gap cannot be attributed to any object class (manifests, ref logs, snapshots, staging, generations), and "how much space would dropping table X reclaim" has no surface at all; the closest thing, `previewDeletes`, mixes physical and logical sizes and counts entries it will not delete.
- Trigger: any capacity investigation on a CAS pool.
- Reported by: ad3-3, ad3-4, tier3-15

### CAS-124 -- empty content hashes to the all-zero digest, which is also the sentinel fsck substitutes for an unparsable key
- Class: INTEGRITY
- Anchor: `src/IO/HashingWriteBuffer.h:21-30`, `src/IO/HashingReadBuffer.h:24-32`; `CA/Primitives/CasBlobDigest.h:41`, `:145-152`; sentinel use in `CA/Tools/CasFsck.cpp`
- Impact: a legitimate zero-length blob is indistinguishable from fsck's "could not parse this key" placeholder, so one confuses the other in reports.
- Reported by: ad1-3

### CAS-125 -- `Xxh3Streamer` dereferences a null state in its constructor, making the allocation-failure guard dead
- Class: CORRECTNESS
- Anchor: `CA/Primitives/CasXxh3Streamer.h:17`, `valid()` at `:24`, the unreachable guard at `CA/Primitives/CasBlobHashingWriteBuffer.cpp:87-88`
- Impact: with `blob_hash=xxh3-128` under memory pressure the process faults instead of raising `CANNOT_ALLOCATE_MEMORY`.
- Reported by: ad1-4, tier4-10

### CAS-126 -- the write-fence pre-check exists only on the S3 staging path
- Class: INTEGRITY
- Anchor: `CA/ContentAddressedTransaction.cpp:607-622` (S3 captures `fenceGeneration()` and passes `check_fence_before_finalize`) versus `:625-635` (local path passes nothing)
- Impact: on the default local backend a writer whose fence was lost mid-write streams the whole body and discovers the loss only at commit.
- Reported by: bc2-6

### CAS-127 -- avoidable per-byte and per-line copying and allocation on hot paths
- Class: PERF/SCALE
- Anchor: `CA/ContentAddressedTransaction.cpp:1220-1235` (three full copies per byte, two clamp-sized buffers per open blob file), `:1269-1274`; `CA/Formats/CasTextFormat.cpp:271-286` (byte-at-a-time `readLine`, no reserve), `:138-169` (String copy per key); `CA/Backend/CasInstrumentedBackend.cpp:109-121` (up to five substring searches per request)
- Impact: measurable constant-factor cost on every blob write, every manifest/snapshot decode and every backend request.
- Reported by: bc2-7, performance-8, performance-11

### CAS-128 -- inline entries staged into a destination part that never gets a build fail the whole commit closed
- Class: CORRECTNESS
- Anchor: `CA/ContentAddressedTransaction.cpp:800-812`, `:1035-1053`, guard at `:293-295`
- Impact: writing a small metadata file into part A and then hardlinking/moving it into a part B that is not otherwise written aborts the entire transaction.
- Reported by: write-protocol-4

### CAS-129 -- the writer-epoch fence on a build is checked only at entry to `promote`, not at the durable append
- Class: CONCURRENCY
- Anchor: `CA/Pool/CasPartWriteTxn.cpp:125-128` (`requireAlive`), `:635` (the only call), `:657-729` (the ops builder never re-checks); `CA/Pool/CasPool.cpp:722-740`
- Impact: a build admitted under epoch E1 can append on a fresh runtime after a self-remount to E2, up to `operation_deadline_ms` (default 90 s) later.
- Reported by: write-protocol-6

### CAS-130 -- mount-lease and epoch identity fields are written but not enforced
- Class: CORRECTNESS
- Anchor: `CA/Pool/CasServerRoot.cpp:1021` (`doStart` writes a literal `seq = 1` over the slot `claimMount` just bumped at `:334`, `:347`), `:226-236` (`allocateWriterEpoch` can return 0 on the object-present path); `CA/Pool/CasMountRuntime.h:44-50` with `:120-121` (`server_uuid`/`writer_epoch` assigned, never consulted by `mayMutate`/`checkFenceOrThrow`)
- Impact: the durable lease sequence is not monotone across mounts, the fence carries an identity it never checks, and writer epoch 0 -- the struct default -- can be handed out as a real epoch.
- Reported by: tier2-9, tier2-10, tier2-12

### CAS-131 -- audit-event and cache-counter attribution defects
- Class: OBSERV/DAY2
- Anchor: `CA/ContentAddressedMetadataStorage.cpp:431-456` (timestamps and `thread_id`/`query_id` taken on the draining thread); `CA/Parts/PartFolderAccess.cpp:152`, `:164-166` (deferred `RefResolve` dropped on load-side cache hits), `:164-214`, `:271-278`, `:564-573` (view-cache counters double-count and mix units)
- Impact: events are attributed to the wrong thread and query, cache-hit resolves are missing from the log, and the view-cache counters cannot be used to size the cache.
- Reported by: concurrency-14, tier4-6, tier4-7

### CAS-132 -- bucket layout, hostnames, PIDs and server UUIDs are disclosed in errors reachable by unprivileged SQL users
- Class: SECURITY
- Anchor: `CA/Pool/CasServerRoot.cpp:368-386` (`mountDoubleStartMessage`), `:120-126`, `:592-595`; `system.cas_mounts` readable with SELECT on `system`
- Impact: any user who can trip a CAS error path, or read `system.cas_mounts`, learns pool topology, peer hostnames/PIDs and literal object key paths.
- Reported by: security-6

### CAS-133 -- `cas_mounts` renders a transient LIST failure identically to a non-existent pool or a not-yet-started disk
- Class: OBSERV/DAY2
- Anchor: `src/Storages/System/StorageSystemContentAddressedMounts.cpp:146-156` (`list_ok=false` on any exception) falling through to the synthetic row at `:199-218`
- Impact: one throttled LIST while the table is read makes a healthy pool look absent -- the same rendering as an object-store outage or a disk that has not started.
- Reported by: ad3-12, tier3-11

### CAS-134 -- a receiver with two CAS pools in one policy advertises only the first, silently losing relink for the other
- Class: FEATURE-GAP
- Anchor: `src/Storages/MergeTree/DataPartsExchange.cpp:586-604` (first CAS disk in `getDisks()` order sets the single `cas_pool_uuid`), `:780-787` (a reservation on the other pool falls back to a byte fetch)
- Impact: fetches into the second pool silently transfer every byte instead of relinking, with no diagnostic.
- Reported by: ad7-9

### CAS-135 -- emulated mode holds one mutex across multiple round trips per operation, and a process-wide mutex across a whole blob body
- Class: PERF/SCALE
- Anchor: `CA/Backend/CasObjectStorageBackend.cpp:491-507`, `:533-545`, `:651-660`, `:687`, `:715`, `:763`; `:819-832` (`static std::mutex emulated_resurrect_mutex` held across the body build and write)
- Impact: CAS over local object storage serializes all reads and writes on one lock, and all resurrects process-wide.
- Reported by: bc7-10

## Cross-cutting themes

- **Namespace scoping is inconsistent.** The `server_root_id` prefix is applied to live namespaces and to nothing else, and namespace identity carries no per-disk component, so shadow/backup namespaces are pool-global, unowned by any exclusion primitive and invisible to the sweeps that depend on a mount lease; nesting is not rejected either. CAS-001, CAS-007, CAS-077, CAS-024.
- **Fail-open on ambiguous or unverifiable backend results.** Bucket-configuration preconditions are skipped or downgraded to warnings when they cannot be evaluated, and indeterminate write outcomes are reported as definite ones in both directions. CAS-029, CAS-030, CAS-031, CAS-012, CAS-032, CAS-021, CAS-068, CAS-069.
- **Budgets and caps are checked after materialization, or not reachable at all.** Size caps validate an already-built buffer, the inline budget fires only at commit, and the mount/lease/request budget plus seven pool caps have no configuration path, so their validators are dead code. CAS-044, CAS-046, CAS-105, CAS-113, CAS-115.
- **Cost is O(total pool) where it should be O(churn).** Every GC round re-folds all edges and re-lists the whole ref prefix; every 256 commits re-encodes an entire namespace; every ref append re-reads the pool-global catalog; every hardlink re-reads the source manifest. CAS-035, CAS-054, CAS-055, CAS-112, CAS-114, CAS-116, CAS-120.
- **Cache accounting is fictional.** The view cache weighs every manifest as 256 bytes, the manifest cache under-weighs by ~2x and the dedup cache by ~3.1x with no entry-count backstop -- so every configured memory budget is advisory and one of them also defeats an oversized-entry guard. CAS-045, CAS-115, CAS-118.
- **Durability is claimed before it is achieved, and cannot be undone.** Repoints, multi-part commits, cross-namespace renames, generation seals and blob bodies all become durable before the step that would make them consistent, with rollbacks that are `noexcept` and silent and no reconciler to finish the job. CAS-005, CAS-006, CAS-072, CAS-075, CAS-076, CAS-080.
- **Observability counters are incremented before durability or outcome.** Dedup savings are counted before admission and then the body is uploaded anyway; round counters are replayed from a budget-truncated log; phase rows carry round 0; eleven counters can never fire. CAS-101, CAS-102, CAS-103, CAS-131.
- **Content addressing is never re-verified.** Admission is by existence, re-uploads and resurrects are size-checked only, staged bodies are re-read but not re-hashed, reads never verify, and the default digest is a non-cryptographic 128-bit hash -- so every integrity guarantee rests on the single producer-side hashing pass. CAS-008, CAS-009, CAS-088, CAS-089.
- **Exclusive access rests on tokens and leases that are not fencing tokens.** An empty ETag becomes an unconditional clobber, the GC lease has no TTL and is not revalidated on destructive phases, plain-object writes skip the controller and the margin, and the mount fence carries an identity it never checks. CAS-003, CAS-010, CAS-011, CAS-129, CAS-130.
- **Latches and single-flight leadership have no deadline and no RAII.** Setting a latch before the durable work, releasing leadership outside RAII, and waiting on a leader with no timeout turn one slow or throwing object-store call into a permanent wedge of a table, a namespace or the whole mount. CAS-015, CAS-017, CAS-018, CAS-070.
- **Day-2 tooling can detect but not localize or repair.** fsck is counts-only and report-only with conditionally skipped checks, only `gc/state` has a rebuild path, `cas-inspect` cannot decode eight formats or enumerate keys, and the only verb that clears a dead member's slot first erases its data. CAS-061, CAS-062, CAS-123, CAS-063, CAS-097, CAS-100.
- **The safety-critical surfaces have no executable specification.** No decoder is fuzzed, no property-based test exists, no CI lane exercises a real conditional-write dialect, and there is no crash-at-step-N harness -- which is precisely the coverage that would pin CAS-036 through CAS-039 and every crash-consistency finding. CAS-064, CAS-065, CAS-109. (The audited working tree also has the CAS test corpus deleted, which is a property of this round rather than of the PR: see NOTE-1.)

## Traceability

Every audit maps to the global IDs it contributed. All 349 local findings are accounted for.

| Audit | Findings | Global IDs |
|---|---|---|
| ad1-hash-determinism | 5 | CAS-009, CAS-013, CAS-041, CAS-124, CAS-125 |
| ad2-deletion-erasure | 13 | CAS-001, CAS-023, CAS-028, CAS-029, CAS-033, CAS-034, CAS-081, CAS-082, CAS-083, CAS-084 |
| ad3-day2-dr-runbook | 13 | CAS-061, CAS-062, CAS-063, CAS-097, CAS-098, CAS-099, CAS-123, CAS-133 |
| ad4-migration | 8 | CAS-024, CAS-026, CAS-058, CAS-081, CAS-085, CAS-120, CAS-121 |
| ad5-resource-exhaustion | 12 | CAS-011, CAS-034, CAS-035, CAS-046, CAS-047, CAS-051, CAS-053, CAS-105, CAS-111, CAS-112, CAS-113, CAS-115 |
| ad6-s3-lifecycle-cross-region | 13 | CAS-012, CAS-029, CAS-030, CAS-031, CAS-032, CAS-081, CAS-082, CAS-119 |
| ad7-protocol-skew | 9 | CAS-003, CAS-007, CAS-013, CAS-026, CAS-030, CAS-039, CAS-066, CAS-107, CAS-134 |
| alter-merge-mutation | 7 | CAS-001, CAS-005, CAS-055, CAS-056, CAS-081, CAS-085, CAS-093 |
| backfill-not-reviewed | 10 | NOTE-1, NOTE-2 |
| bc1-offset-overflow | 8 | CAS-037, CAS-039 |
| bc2-writebuffer-spill | 7 | CAS-009, CAS-014, CAS-046, CAS-081, CAS-126, CAS-127 |
| bc3-exception-safety | 12 | CAS-017, CAS-018, CAS-068, CAS-069, CAS-070, CAS-081 |
| bc4-protobuf-decode | 10 | CAS-036, CAS-037, CAS-038, CAS-040, CAS-089 |
| bc5-wide-part-read | 9 | CAS-014, CAS-041, CAS-045, CAS-055, CAS-056, CAS-115, CAS-116, CAS-117, CAS-118 |
| bc6-mtime-semantics | 9 | CAS-067, CAS-086, CAS-092 |
| bc7-blocking-io-locks | 10 | CAS-015, CAS-016, CAS-047, CAS-048, CAS-049, CAS-135 |
| codeonly-line | 10 | CAS-042, CAS-105, CAS-110, NOTE-1, NOTE-3 |
| concurrency | 14 | CAS-015, CAS-018, CAS-019, CAS-050, CAS-051, CAS-052, CAS-070, CAS-071, CAS-131 |
| coverage-map | 4 | CAS-042, CAS-108 |
| crash-consistency | 9 | CAS-006, CAS-017, CAS-046, CAS-062, CAS-063, CAS-075, CAS-076, CAS-077, CAS-080 |
| datatype-agnosticism | 6 | CAS-014, CAS-040, CAS-044 |
| encryption | 9 | CAS-028, CAS-059, CAS-060, CAS-090 |
| gc-protocol | 6 | CAS-002, CAS-003, CAS-022, CAS-035, CAS-073, CAS-074 |
| gc-rebuild-feature | 7 | CAS-003, CAS-004, CAS-035, CAS-049, CAS-094, CAS-095, CAS-096 |
| idisk-contract | 8 | CAS-005, CAS-020, CAS-057, CAS-085, CAS-086 |
| interleaving | 3 | CAS-001, CAS-006 |
| jepsen-anomaly | 5 | CAS-001, CAS-003, CAS-005, CAS-011, CAS-021 |
| mergetree-part-support | 8 | CAS-006, CAS-014, CAS-044, CAS-045, CAS-057, CAS-059, CAS-087 |
| performance | 12 | CAS-035, CAS-054, CAS-104, CAS-112, CAS-115, CAS-116, CAS-118, CAS-127 |
| read-protocol | 4 | CAS-016, CAS-045, CAS-089, CAS-118 |
| security | 6 | CAS-008, CAS-027, CAS-036, CAS-091, CAS-132 |
| test-coverage-fuzzing | 8 | CAS-064, CAS-065, CAS-109 |
| tier1 | 5 | CAS-017, CAS-053, CAS-110, CAS-114 |
| tier2 | 12 | CAS-010, CAS-011, CAS-021, CAS-068, CAS-070, CAS-102, CAS-105, CAS-106, CAS-130 |
| tier3 | 19 | CAS-038, CAS-073, CAS-074, CAS-078, CAS-097, CAS-098, CAS-100, CAS-101, CAS-108, CAS-123, CAS-133 |
| tier4 | 13 | CAS-019, CAS-066, CAS-097, CAS-102, CAS-103, CAS-106, CAS-108, CAS-125, CAS-131 |
| tla-fidelity | 10 | CAS-002, CAS-003, CAS-009, CAS-011, CAS-025, CAS-029, CAS-072, CAS-073, CAS-079 |
| upgrade-compat | 10 | CAS-013, CAS-041, CAS-042, CAS-043, CAS-061, CAS-089, CAS-122 |
| write-protocol | 6 | CAS-005, CAS-088, CAS-103, CAS-128, CAS-129 |

## Audit-round notes (not product defects)

These three items are observations about **this audit round and the code-only strip it ran
against**, not defects in the CAS feature. They are recorded here so the round's confidence
qualifiers stay attached to it, and they are excluded from the severity counts. Genuine
product test-coverage gaps (no decoder fuzzing, no native/GCS conditional-write CI lane, no
property or crash-at-step-N harness) remain in the findings above with class `TEST-GAP`,
because those are real gaps in the PR.

### NOTE-1 -- the entire CAS test corpus is deleted in the audited tree, the strip-fidelity precondition was never verified, and narrative material remains in the repo
- Class: TEST-GAP
- Anchor: working tree: 134 deletions under `src/Disks/tests/`, 119 functional deletions under `tests/`, 25 docs, 2 READMEs; untracked `docs/superpowers/CAS.md` (2,198 lines) and `tmp/` (26 entries)
- Impact: the only executable specification of CAS behaviour is absent from the tree every conclusion in this round was drawn from, and the check that the strip removed only comments/docs -- made a precondition by `codeonly-line` -- was deferred and never performed. Untracked narrative trees remain fully visible to search and will bias any reader.
- Trigger: recovering an intended contract by reading the test that pins it; or a repo-wide search for a CAS symbol.
- Reported by: codeonly-line-1, backfill-2, codeonly-line-10

### NOTE-2 -- coverage gaps in the round itself: the `Gc/`/`Tools/` sweep was completed late by `tier3`/`tier4`, and several files and unresolved questions still have no owner
- Class: TEST-GAP
- Anchor: `CA/Gc/CasGc.cpp` (3,236 lines), `CA/Tools/` (2,082 lines), `CA/Pool/CasPartWriteTxn.cpp` (902 lines, excluded by both tier sweeps by name), `CA/Formats/CasRefWireVocab.{h,cpp}`, `CA/Gc/CasGcMaintenanceState.cpp`, `CA/Primitives/CasNamespaceLifeId.h`
- Impact: at the time `backfill-not-reviewed` was written the DR instrument set and the largest file in the tree lacked a phase-by-phase owner. `backfill-1` is now superseded on that point: both [`tier3`](reports/tier3.md) and [`tier4`](reports/tier4.md) exist -- they were produced after `backfill-not-reviewed` was written and they close the `Gc/`/`Tools/` sweep, contributing 32 local findings to this file. What still stands is the unowned-file and unowned-question residue: `interleaving`'s two explicitly unresolved questions (one a "both branches are bad" fork) and four items on `coverage-map`'s blind-spot list have no owner.
- Trigger: n/a -- audit-process gap; read as a confidence qualifier on findings anchored in `Gc/` and `Tools/`.
- Reported by: backfill-1, backfill-3, backfill-4, backfill-5, backfill-6, backfill-7, backfill-8, backfill-9, backfill-10

### NOTE-3 -- the strip removed argument labels, parameter names and the rationale of 16 `catch (...)` sites, leaving fail-open intent unrecoverable
- Class: OBSERV/DAY2
- Anchor: ~40 unlabeled positional literals (e.g. `CA/Backend/CasObjectStorageBackend.cpp:96`, `:288`, `CA/Gc/CasGc.cpp:560`, `:2725`); unnamed load-bearing parameters `CA/Backend/CasBackend.h:181`, `:187-188`, `CA/Gc/CasGc.cpp:1229`; empty catches `CA/Pool/CasServerRoot.cpp:1124`, `CA/Pool/CasRefLedger.cpp:3539`, `CA/Gc/CasGc.cpp:2641`, `:2798`; load-bearing empty `if` bodies `CA/Backend/CasRequestControl.cpp:424-439`, `:495-510`; underived constants `CA/Formats/CasPoolMetaFormat.cpp:19`, `CA/Gc/CasGc.h:434`, `CA/Pool/CasRefLedger.h:416-419`
- Impact: a reviewer cannot tell which flag a boolean sets, whether an unused parameter is dead by design, or whether a swallow is deliberate fail-open -- and CAS-069 shows at least two of those swallows are defects. Safety-critical bounds have no derivation, so "is this bound safe at the boundary?" is unanswerable from the tree.
- Trigger: reviewing any of these lines.
- Reported by: codeonly-line-2, codeonly-line-3, codeonly-line-6, codeonly-line-7, codeonly-line-8

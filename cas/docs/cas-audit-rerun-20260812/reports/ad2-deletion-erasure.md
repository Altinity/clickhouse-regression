# ad2-deletion-erasure -- fresh audit 2026-08-12

## Scope

Target: `/Volumes/workspace/altinity-clickhouse/ClickHouse`, branch `cas-code-only-strip`, base `842f2b37b8f`, working tree as-is (all CAS tests deleted, all CAS docs deleted). Static reading only; nothing built or run.

Question: when a user deletes data on a CAS disk, what happens to the bytes, how much of it is synchronous, what can stop reclamation, what stays readable, and what erasure guarantee the shipped code can actually support.

Read in full or in relevant part: `ContentAddressedTransaction.cpp` (all remove/move/link paths), `ContentAddressedMetadataStorage.cpp` (admission, startup, GC verbs, forget, relink), `Parts/PartFolderAccess.cpp`, `Pool/CasRefLedger.cpp` (`dropNamespaceImpl`), `Pool/CasPlainObjects.cpp`, `Pool/CasPartWriteTxn.cpp` (dedup/upload), `Gc/CasGc.cpp`, `Gc/CasBlobInDegree.cpp`, `Gc/CasNamespaceJanitor.cpp`, `Gc/CasGcScheduler.cpp`, `Backend/CasBackend.h`, `Backend/CasObjectStorageBackend.cpp`, `Backend/CasProbe.cpp`, `Formats/CasLayout.cpp`, `Tools/CasFsck.{h,cpp}`, `Tools/CasInspect.cpp`, `Tools/CasDecommission.cpp`, `ContentAddressedSettings.cpp`, plus the MergeTree callers (`DataPartStorageOnDiskBase.cpp`, `MergeTreeData.cpp::dropAllData`, `StorageReplicatedMergeTree::drop`, `DataPartsExchange.cpp`) and `DiskObjectStorageCache.cpp`.

Code-only rule honoured: deleted docs and comments were not used as evidence of intent; shipped log/exception strings were.

Cited, not re-derived (sibling reports of this run): GC rebuild permanently orphans already-unreferenced blobs; a blob body can be durable before the meta marker while the build never commits; nothing but `cas-fsck` ever lists `cas/blobs/`. Local write-buffer spill is `bc2-writebuffer-spill`.

## Delete chain per operation

| operation | synchronous effect (in the query) | deferred effect | who reclaims | anchor |
|---|---|---|---|---|
| `DROP TABLE` (table dir) | one ref-log append: `OwnerTransition` for every committed ref + every precommit + `RemoveNamespace`; catalog row -> `Removing`. Zero object bodies deleted. | blob/manifest deletes; dead-life namespace-object deletes | GC leader (fold + janitor) | `ContentAddressedTransaction.cpp:738-742`; `Pool/CasRefLedger.cpp:3549-3586`; `Parts/PartFolderAccess.cpp:564-573` |
| `DROP PARTITION` / any part removal (checksums-known fast path) | `unlinkFile` per file (staged `content_removed`) then `removeDirectory(part)` -> `dropRefIfPresent` -> one ref-log drop. No object deleted. | as above | GC leader | `DataPartStorageOnDiskBase.cpp:1019-1039`; `ContentAddressedTransaction.cpp:1069-1099`, `683-702` |
| `DROP PARTITION` (recursive fallback) | `removeRecursive(part)` -> `dropRefIfPresent`. No object deleted. | as above | GC leader | `ContentAddressedTransaction.cpp:759-762`; `DataPartStorageOnDiskBase.cpp:1005`, `1048` |
| `DETACH PARTITION` | `moveDirectory` -> `republishRef` (new ref name, same manifest), old ref dropped. Bytes stay referenced by design. | nothing | nobody (until the detached ref is dropped) | `ContentAddressedTransaction.cpp:908-963`; `Parts/PartFolderAccess.cpp:419-440` |
| `DROP DETACHED PARTITION` / `detached/` wholesale | `dropRefIfPresent` per detached ref | blob deletes | GC leader | `ContentAddressedTransaction.cpp:744-758`; `ContentAddressedMetadataStorage.cpp:1017` |
| `TRUNCATE TABLE` | per-part ref drops, then `format_version.txt` etc. removed, then table dir -> `dropNamespace` | blob/manifest deletes | GC leader | `MergeTreeData.cpp:4230-4241`, `4261-4266`; `ContentAddressedTransaction.cpp:738-742` |
| lightweight `DELETE` | nothing at all in CAS: a mask column is added; the row bytes stay in the same blobs, still referenced | nothing | nobody | `ContentAddressedTransaction.cpp:782-829` (`adoptEvidence` hardlink), `Pool/CasPartWriteTxn.cpp:139-194` |
| mutation / merge part replacement | new part published; unchanged column files adopt the *same* blobs (no copy); old part ref dropped | only blobs of *rewritten* files can lose their last edge | GC leader | `ContentAddressedTransaction.cpp:816-828`; `Parts/PartFolderAccess.cpp:442-473` |
| row-`TTL` expiry | materialised as a mutation/merge -> same as above | same | GC leader | as above |
| `TTL`/`ALTER ... MOVE` between disks | clone into `moving/`, swap, drop source ref; inside one pool the clone is a dedup hit (HEAD, no body PUT) | source blobs only if no other edge | GC leader | `MergeTreePartsMover.cpp:257`; `Pool/CasPartWriteTxn.cpp:149-175` |
| table-level non-part files (`format_version.txt`, mountpoint objects) | **real, synchronous, token-exact object DELETE** | none | the query itself | `ContentAddressedTransaction.cpp:768-779`, `1101-1127`; `Pool/CasPlainObjects.cpp:51-66`, `99-102` |
| blob body reclaim (all of the above) | never synchronous | round R: condemn (`condemn_round = round+1`); round >R: graduate to `delete_pending`; round after: `deleteExact` | GC leader only | `Gc/CasGc.cpp:1293`, `Gc/CasBlobInDegree.cpp:383-413`, `Gc/CasGc.cpp:605-665` |

Net: for part data, **no user-visible delete frees a single byte**. The only byte-freeing DELETE issued outside GC is for non-part table files, staging objects, and `SYSTEM CAS DROP POOL MEMBER` (`Tools/CasDecommission.cpp:58`, `79`, `198-199`).

## Findings

### ad2-1 -- All reclamation is gated on a whole-pool "clean pass" predicate with no bound and no retention signal (High)

- **Anchor**: `Gc/CasGc.cpp:2063-2064` (`suppress_destructive = !report.anomalies.empty() || !carried_holds.empty() || frontier_incomplete`), consumed at `:609-610` (blob deletes), `:791-792` (sweep cursor), `:799-800` (generation prune), `:830-832` (hand-off), `:862-863` (manifest deletes), `:893-898` (janitor + ref cleanup); log at `:2082-2098`.
- **Trigger**: any single anomaly anywhere in the pool (one `lifeless` key, one undecodable row), any held namespace, or a frontier where `frontier_proven != frontier_namespaces` (e.g. one namespace whose ref table cannot be walked). One such row suppresses **every** destructive action of that pass, pool-wide.
- **Consequence**: erasure of already-deleted data stops completely and stays stopped for as long as the condition persists. The condition is not per-namespace, so a defect in table A blocks the erasure of table B. Nothing bounds the delay; the shipped message says only "nothing irreversible runs until a pass that clears all three".
- **Evidence**: the suppression flag is computed once per fold and every delete site consults it; the only operator-facing signal is the log line and `anomalies` count in `cas_gc_log` (`Gc/CasGcScheduler.cpp:192`). There is no counter or column for "bytes withheld".

### ad2-2 -- Erasure latency is a function of object count over per-round budgets, unbounded in practice (Medium)

- **Anchor**: `ContentAddressedSettings.cpp:32` (`gc_interval_sec = 60`), `:42-43` (`gc_round_graduation_budget = 5000`, `gc_round_redelete_budget = 5000`); `Gc/CasBlobInDegree.cpp:385-409` (budget-capped graduation/redelete, remainder pushed to `still_retired`); `Gc/CasGc.cpp:1293` + `Gc/CasBlobInDegree.cpp:394` (two-phase: condemn round, then a strictly later round, then the delete).
- **Trigger**: `DROP TABLE` of a table with many blobs. Minimum three successful non-deferred rounds (~180 s at defaults) for the first cohort; each subsequent round retires at most 5000 blobs.
- **Consequence**: dropping 10M distinct blobs needs ~2000 rounds ~= 33 h of continuous healthy leadership at defaults; any deferred round (`shouldDeferRound`, `Gc/CasGc.cpp:515-562`) or any suppressed pass (ad2-1) extends it. An operator asking "when are my bytes gone?" cannot compute an answer from any exposed value.
- **Evidence**: budgets are per-round and shared across the whole pool; the fold also defers entirely when no shard reached `gc_fold_threshold` and no graduation is due, up to `gc_fold_max_defer_rounds = 8` (`Pool/CasPool.h:65-66`).

### ad2-3 -- Pool-wide content dedup with no per-subject shred primitive: a delete frees nothing while any other manifest anywhere shares the blob (High)

- **Anchor**: `Pool/CasPartWriteTxn.cpp:145` (`key = layout.blobKey(ref)`, content hash only -- no namespace, table, or tenant in the key), `:149-175` (HEAD hit adopts the existing body); edge identity is `(blob, source_id)` where the source is the manifest (`Gc/CasBlobInDegree.h:80-86`, `Gc/CasGc.cpp:613` deletes only at in-degree 0).
- **Trigger**: (a) the same rows exist in two tables/databases on the same pool; (b) a replica fetch relinks the part into its own namespace over the same manifest and blobs (`ContentAddressedMetadataStorage.cpp:1502-1528`, `1592-1619`; `DataPartsExchange.cpp:203`), so in an R-replica cluster the in-degree of every blob is R; (c) a `FREEZE`/backup shadow ref; (d) a `detached/` ref; (e) byte-identical small files (empty marks, low-cardinality column files) shared across unrelated parts.
- **Consequence**: "delete the customer's rows" is not expressible. The code offers no shred, purge, or per-namespace force-delete verb -- the entire admin surface is `CAS_GC_RUN`, `CAS_GC_REBUILD`, `CAS_GC_STOP/START`, `CAS_FSCK`, `CAS_FORGET`, `CAS_DROP_POOL_MEMBER` (`InterpreterSystemQuery.cpp:1012-1051`), none of which can target content. Erasure requires proving that *every* holder in the pool dropped its reference, and the code gives no per-blob holder listing outside `cas-fsck --detail` (`Tools/CasFsck.h:35-42`, `reachable_from`).
- **Evidence**: dedup is keyed purely on the content hash, so it crosses namespace, database, table, replica and shadow boundaries by construction.

### ad2-4 -- Lightweight DELETE and mutations free the deleted rows' bytes only for rewritten files (Medium)

- **Anchor**: `ContentAddressedTransaction.cpp:782-829` -- `createHardLink` resolves the source manifest entry and calls `buildFor(...).adoptEvidence(*src_entry)`, then republishes the same `ManifestEntry` (same `BlobRef`) under the new path; `Parts/PartFolderAccess.cpp:442-473` `repointRef` republishes a manifest for the surviving entries.
- **Trigger**: `DELETE FROM t WHERE ...` (mask only, no rewrite at all), or any mutation that rewrites a subset of column files.
- **Consequence**: after a lightweight `DELETE`, the deleted rows' bytes are still in a blob that the *live* part's manifest references -- GC will never consider it, and the data is intact and readable at the object level indefinitely. After the mutation materialises, only the rewritten files' old blobs can lose an edge; every untouched column file of the pre-delete part remains referenced through the adopt path.
- **Evidence**: `adoptEvidence` records a tokenless adopted dep (`Pool/CasPartWriteTxn.cpp:228-232`) -- no copy, no new blob, the identical body is re-referenced.

### ad2-5 -- Blob keys are unsalted, non-cryptographic content hashes: unreclaimed deleted content is addressable by anyone who can guess it (Medium)

- **Anchor**: `Formats/CasLayout.cpp:28-31` (`blobs/<algo>/<2-hex-shard>/<full hex>` derived only from the content), `ContentAddressedSettings.cpp:33` (default `blob_hash = cityhash128`); no encryption anywhere under the CAS tree (exhaustive search for `encrypt|cipher|sse|kms` matches nothing but unrelated identifiers).
- **Trigger**: any principal with plain read access to the bucket/prefix (backup tooling, a log-shipping role, a stale IAM policy, a snapshot of the bucket) during the window between the ref drop and the eventual `deleteExact` -- a window that ad2-1/ad2-2 can make unbounded.
- **Consequence**: two distinct exposures. (1) Existence oracle: a guessed plaintext yields the exact key, so presence/absence of specific content is testable without any manifest, forever, for live data too. (2) Retrieval: for deleted-but-unreclaimed content the body is still fetchable at that key even though no manifest, ref or catalog row names it any more, so the usual "the metadata is gone" argument does not apply.
- **Evidence**: the hash is the whole key; `cityhash128` is not a PRF and there is no per-pool salt or keyed digest option in the settings list (`ContentAddressedSettings.cpp:29-58`).

### ad2-6 -- `DROP TABLE` silently leaves frozen/backup copies pinning every byte (Medium)

- **Anchor**: `ContentAddressedTransaction.cpp:738-742` -- a table-UUID path drops **only** `liveNamespace(uuid)`; shadow (`FREEZE`) refs live in a separate root namespace removed only by an explicit `removeRecursive` on a shadow path (`:711-723`, `ContentAddressedMetadataStorage.cpp:897-909`).
- **Trigger**: `ALTER TABLE t FREEZE` (or a backup that froze), then `DROP TABLE t`.
- **Consequence**: the drop succeeds and reports nothing; every blob of every frozen part keeps a live edge and is never reclaimed. Because the shadow namespace is keyed by the shadow directory, not by the table UUID, the drop path cannot even enumerate what it is leaving behind, and no warning is emitted. Reclamation then requires `SYSTEM UNFREEZE`/removal of the shadow path, which is a different subject name than the table the user dropped.
- **Evidence**: the live-namespace branch returns immediately after `dropNamespace`; no shadow enumeration exists on that path.

### ad2-7 -- `gc_enabled = false` accepts deletes forever and refuses every manual reclamation path (Medium)

- **Anchor**: `ContentAddressedMetadataStorage.cpp:611` (scheduler only created when `context && gc_enabled && !read_only`), `:461-464` (`SYSTEM CAS GC RUN` -> `BAD_ARGUMENTS`), `:715-717` (`SYSTEM CAS GC START` -> `BAD_ARGUMENTS`), `:492-494` (`GC REBUILD` -> `BAD_ARGUMENTS`); the remove paths never consult `gc_enabled` (`ContentAddressedTransaction.cpp:683`, `705`, `1069`).
- **Trigger**: a disk configured with `gc_enabled=false` (a documented, supported setting), or a pool whose only GC-enabled member is down.
- **Consequence**: `DROP`/`TRUNCATE`/mutations all report success, refs disappear, and there is no in-server way to ever reclaim -- not even a manual one-shot round. Recovery requires a config change plus restart. The only signal is an `INFO` line from `SYSTEM CAS GC STOP` ("disabled/read-only/not started -- nothing to stop", `:701-704`); `system.cas_mounts.pending_reclaim` is `NULL` because there is no scheduler (`StorageSystemContentAddressedMounts.cpp:160-182`).
- **Evidence**: three separate verbs fail closed on `gc_enabled`, while the deletion side is unconditional.

### ad2-8 -- A settled-vanished pool turns deletes into silent no-ops that report success (Medium)

- **Anchor**: `ContentAddressedMetadataStorage.cpp:809-812` -- for `VanishedReplaced`/`VanishedForgotten`, `checkOpAdmitted(Remove)` returns `TruthAbsent`; every remove entry point then returns immediately (`ContentAddressedTransaction.cpp:685-686`, `708-709`, `1071-1072`).
- **Trigger**: the pool prefix was re-created/replaced under the same disk name, or the disk was decommissioned with `SYSTEM CAS FORGET`, and a `DROP TABLE`/`DROP PARTITION` is then issued.
- **Consequence**: the DDL succeeds and the server believes the data is gone, while the bytes of the *previous* pool incarnation are untouched and now unreferenced by any live catalog -- and no GC will ever run against a prefix nothing mounts. The code itself says so: "decommissioned by SYSTEM CAS FORGET at {} -- erasure was NOT verified; if this was a mistake the data may be intact" (`ContentAddressedMetadataStorage.cpp:682-684`, `Pool/CasPool.cpp:268`).
- **Evidence**: `TruthAbsent` is deliberately returned for `Probe` and `Remove` only, i.e. deletes are reported as vacuously satisfied.

### ad2-9 -- S3 staging holds whole part-file plaintext that only the same `server_root_id` ever sweeps, and no tool lists it (Medium)

- **Anchor**: `ContentAddressedMetadataStorage.cpp:596-607` (startup sweep, only when `staging_backend=s3` **and** conditional copy is supported **and** not read-only, and only under `.../staging/<own server_root_id>/`); `Pool/CasServerRoot.cpp:1140-1168` (`noexcept`, best-effort, swallows all errors); per-transaction cleanup at `ContentAddressedTransaction.cpp:155-165`; the only other deleter is `SYSTEM CAS DROP POOL MEMBER` for a named victim (`Tools/CasDecommission.cpp:198-199`). `cas-fsck` lists exactly `cas/blobs/`, the namespace root and per-namespace manifests (`Tools/CasFsck.cpp:427`, `578-581`, `873-875`) -- never `staging/`; GC never lists it either.
- **Trigger**: a server crashes or is killed mid-insert with `staging_backend=s3` and never comes back with the same `server_root_id` (container/pod re-creation, macro change, node replacement).
- **Consequence**: full uncompressed-by-CAS part-file bodies remain at `.../staging/<dead srid>/<random>.tmp` permanently. They are invisible to `SYSTEM CAS FSCK` and to every GC phase, so neither an operator audit nor an erasure claim will ever mention them, and they are not content-addressed, so a later re-insert of the same data does not even collide with them.
- **Evidence**: the sweep prefix is built from the *own* `server_root_id`; there is no pool-wide staging enumeration anywhere in the tree.

### ad2-10 -- Bucket versioning turned on after mount wedges all reclamation and converts prior deletes into recoverable versions (Medium)

- **Anchor**: `Gc/CasGc.cpp:613-617` -- if `deleteExact` reports `created_delete_marker`, GC throws `LOGICAL_ERROR` ("versioning is enabled on the pool (mis-provisioned; the capability probe must reject this)"); the probe runs only once, at mount (`Pool/CasPool.cpp:339-342`), and is skippable via `skip_access_check` (`ContentAddressedSettings.cpp:35`); probe check at `Backend/CasProbe.cpp:171-187`.
- **Trigger**: enabling versioning (or a bucket policy that forces it) on a live pool; or mounting with `skip_access_check=1` onto a versioned bucket.
- **Consequence**: the first blob delete of the round throws, the round aborts mid-way (`Gc/CasGcScheduler.cpp:199-208`), and every subsequent round re-reaches the same point -- reclamation stops permanently while deletes keep being accepted. Worse for erasure: every already-issued delete became a delete marker with the body retained as a non-current version, and CAS has no code that lists or removes non-current versions.
- **Evidence**: `DeleteOutcome::created_delete_marker` is only ever checked to fail; nothing in the tree issues a versioned delete, `ListObjectVersions`, or a lifecycle configuration.

### ad2-11 -- No multipart-upload hygiene anywhere in CAS (Low)

- **Anchor**: exhaustive search of the CAS tree for `multipart` matches nothing; the only object-level removals are `Backend/CasObjectStorageBackend.cpp:734-747`, `:776`, `Backend/CasProbe.cpp:224`, `Pool/CasServerRoot.cpp:1152`, plus GC's `deleteExact` sites. `cas-fsck`'s listing set (`Tools/CasFsck.cpp:427`, `578-581`, `873-875`) contains no multipart accounting, and `physical_bytes` (`Tools/CasFsck.h:69`) is computed from listed keys only.
- **Trigger**: a server killed while streaming a large blob body or a large staging object through an S3 multipart upload.
- **Consequence**: in-progress upload parts are neither aborted nor reported; they hold user bytes and cost, and an fsck-based "the pool is clean" statement does not cover them. Erasure of that residue is only achievable with a bucket lifecycle rule the code neither sets nor verifies.
- **Evidence**: absence is exhaustive for the CAS subtree; the capability probe checks conditional write, delete-exactness and versioning (`Backend/CasProbe.cpp:141-201`) but not multipart cleanup or lifecycle.

### ad2-12 -- Dead-life namespace debris (including verbatim table-file bodies) erases at 1000 objects per round, one page per round (Low)

- **Anchor**: `Gc/CasGc.cpp:390` (`NamespaceJanitor janitor(backend, layout, 1000)`), invoked once per round (`:560`, `:893`); `Gc/CasNamespaceJanitor.cpp:25` (single `list` page), `:105` (token-exact delete), `:119-130` (cursor advanced only if the whole page was decided).
- **Trigger**: `DROP TABLE`/`DROP DATABASE` on a pool with many namespaces or long ref histories.
- **Consequence**: ref logs, checkpoints and namespace files of dropped tables -- which include verbatim table file bodies written by `putNamespaceFile` -- disappear at 1000 keys per GC interval, i.e. days for a large pool, and the page is skipped entirely on any pass where `suppress_deletes` is set (ad2-1) or the catalog life index is ambiguous (`:36-46`).
- **Evidence**: the budget is a hard-coded constructor argument, not a setting; there is no way to raise it.

### ad2-13 -- Reclaimed blobs are never evicted from the node-local filesystem cache (Medium)

- **Anchor**: `DiskObjectStorageCache.cpp:21-23` -- when a CAS disk is wrapped with a cache layer, the *same* `ContentAddressedMetadataStorage` is reused (no `MetadataStorageFromCacheObjectStorage` interposition), so CAS keeps deleting through the object storage it was constructed with (`Backend/CasObjectStorageBackend.cpp:745`); nothing in the CAS tree calls `removeCacheIfExists` (declared at `ObjectStorages/Cached/CachedObjectStorage.h:105`), and `CachedObjectStorage` does not override `removeObjectIfTokenMatches` (default throws, `ObjectStorages/IObjectStorage.h:283-287`).
- **Trigger**: a CAS disk with a filesystem cache configured; `SELECT` a part (populating the cache), then drop it and let GC reclaim the blobs.
- **Consequence**: the object is gone from the bucket but the cached segments containing the same plaintext stay in the local cache directory on every node that read them, until unrelated LRU pressure evicts them. Any erasure statement based on bucket state is wrong by the size of the caches, and no CAS-side counter or fsck class covers it.
- **Evidence**: the delete path bypasses the cache wrapper entirely; the cache is only ever invalidated by the non-CAS metadata paths that call `removeCacheIfExists`.

## Erasure guarantee supportable from code

**None, in the strict sense.** Concretely:

1. **Nothing is erased synchronously.** For part data every user-facing delete is a metadata-only ref-log append (`ContentAddressedTransaction.cpp:683-780`, `1069-1099`). The only synchronous byte deletes are non-part table files and mountpoint objects (`Pool/CasPlainObjects.cpp:51-66`). A successful `DROP TABLE` is therefore not evidence that any byte was freed.
2. **The best case is a soft, unenforced bound**, not a guarantee: `>= 3` successful non-deferred GC rounds after the last reference disappears, times `ceil(objects / 5000)` rounds, times `gc_interval_sec` -- and only while all of the following hold simultaneously: this disk has `gc_enabled` (ad2-7), some member holds the GC lease (`Gc/CasGc.cpp:415-433`), the fold's frontier is complete with zero anomalies and zero held namespaces (ad2-1), the pool is not versioned (ad2-10), and **no other manifest anywhere in the pool references the blob** (ad2-3).
3. **It is unbounded in general**, because condition 2 has failure modes that persist indefinitely with no timer and no escalation: a single anomaly, an unwalkable namespace, a disabled GC, a vanished pool that ACKs deletes as no-ops (ad2-8), a versioned bucket that wedges the delete phase.
4. **There is no per-subject erasure primitive at all.** Content dedup is pool-wide on an unsalted hash, so the unit of reclamation is "content with zero references", never "this tenant's rows". Lightweight `DELETE` frees nothing ever (ad2-4). Freeze/backup/detached/replica refs each independently pin everything (ad2-3, ad2-6).
5. **Deleted-but-unreclaimed data stays readable** at a key derivable from the content itself, with no manifest needed (ad2-5), plus in staging objects (ad2-9), local caches (ad2-13), local scratch (see `bc2-writebuffer-spill`), non-current object versions (ad2-10), and blobs orphaned by GC rebuild (see `gc-rebuild-feature`), which are reported by fsck as non-fatal `unreachable` and reclaimed by nothing.
6. **The operator can partially tell, but not in bytes.** Available: `cas_gc_log` per-round `entries_condemned/graduated/redeleted`, `objects_deleted` and phase metrics (`Gc/CasGcScheduler.cpp:178-196`); `system.cas_mounts.pending_reclaim` -- but that is a *process-local cumulative* `condemned - redeleted` counter in objects, reset by restart and `NULL` for non-leaders (`Gc/CasGcScheduler.cpp:170-172`, `StorageSystemContentAddressedMounts.cpp:53-54`); and `SYSTEM CAS FSCK` classes `pending_gc`/`awaiting_gc`/`unreachable` with per-object sizes in detail mode (`Tools/CasFsck.h:19-82`). Missing: any bytes-pending-erasure figure, any per-subject attribution once refs are dropped, any signal on the suppression backlog.

**What an operator must actually do to guarantee erasure**, given this code: (a) remove every reference, not just the table -- all replicas'/namespaces' refs, `detached/`, every `FREEZE`/shadow namespace, every pool the data was moved between; (b) materialise lightweight deletes (`OPTIMIZE`/mutation) because masked rows are never candidates; (c) drive GC to quiescence with `SYSTEM CAS GC RUN` repeatedly until `cas_gc_log` shows zero `graduated`/`redeleted` **and** zero `anomalies` (a suppressed pass looks like progress otherwise); (d) verify with `SYSTEM CAS FSCK` detail that no `pending_gc`, `awaiting_gc` or `unreachable` object of interest remains -- this is the only ground-truth surface; (e) clean the residue CAS's model does not own: `SYSTEM CAS DROP POOL MEMBER` for every dead `server_root_id` (staging), the local `scratch_path` of every node, every node's filesystem cache, non-current versions / delete markers / incomplete multipart uploads via bucket lifecycle; (f) accept that (a)-(e) still cannot prove erasure of a *subject* because dedup destroys attribution and the key is the content -- so the only defensible guarantee is external: per-tenant encryption at rest with key destruction, or deleting the whole pool prefix.

## Checked and sound

- Blob deletes are token-exact and fail closed on ABA: `deleteExact` with the retired entry's token, `TokenMismatch` re-HEADed and reclassified rather than force-deleted, replaced incarnations re-condemned instead of deleted (`Gc/CasGc.cpp:613-628`, `710-729`).
- Two-phase graduation with an in-degree recheck: a blob that regained an edge between condemn and delete is spared, never fail-closed deleted (`Gc/CasBlobInDegree.cpp:368-382`, `Gc/CasGc.cpp:666-692`).
- A delete that creates a versioning delete marker aborts rather than being treated as success (`Gc/CasGc.cpp:613-617`), and the mount-time probe rejects both markers and ineffective deletes (`Backend/CasProbe.cpp:171-187`).
- `truncateFile` refuses instead of silently mutating an immutable blob, with an accurate message (`ContentAddressedTransaction.cpp:1130-1135`).
- `removeRecursive` on a shadow prefix reports keys it could not attribute to a namespace life instead of dropping them silently, and names `cas-fsck` as the follow-up (`ContentAddressedTransaction.cpp:727-734`).
- `dropNamespace` closes positive-mutation admission, waits for in-flight leaders/publishes, cancels in-flight builds and appends the terminal record with the owner transitions of both committed refs and precommits -- so a drop cannot leave a half-visible ref set (`Pool/CasRefLedger.cpp:3451-3458`, `3549-3596`).
- Non-part table files and mountpoint objects are removed with a token-exact CAS loop with a live-lock brake (`Pool/CasPlainObjects.cpp:51-66`).
- The janitor deletes dead-life objects token-exactly, only advances its cursor when the whole page was decided under a held fence, and counts what it could not delete as `leaked` with a diagnostic (`Gc/CasNamespaceJanitor.cpp:80-130`).
- Suppression is logged with its exact cause and deficit, at `WARNING` when the cause is per-round (`Gc/CasGc.cpp:2081-2098`).
- `cas-inspect` renders metadata only -- it has no blob-body dump path (`Tools/CasInspect.cpp:404-413`, `567-576`), and there is no SQL surface to read a dropped ref (the CAS verbs are GC/fsck/forget/decommission only, `InterpreterSystemQuery.cpp:1012-1051`).
- `SYSTEM CAS FORGET` does not claim erasure; the persisted reason string explicitly says erasure was not verified (`ContentAddressedMetadataStorage.cpp:682-684`).

## Coverage

Covered: every remove/move/link entry point of `ContentAddressedTransaction`; ref-drop and namespace-drop down to the ledger append; the full GC round (lease, heartbeat floor, defer decision, fold, suppression, pending deletes, prune, hand-off, manifest deletes, ref-object cleanup, orphan sweep, janitor); in-degree settle rules; dedup/upload path; blob key layout; capability probe; staging and scratch lifecycles; fsck/inspect/decommission tooling surfaces; the MergeTree callers for part removal, table drop, freeze/detach and mover; the cache-wrapping path.

Not covered (out of scope or not statically decidable here): dynamic behaviour (nothing was built or run; all CAS tests are deleted in this tree); S3/GCS server-side lifecycle, versioning and replication configuration; encryption layered outside CAS; the `Cache` metadata storage's own semantics; backup/`RESTORE` engine internals beyond the shadow-namespace boundary; performance of the fsck full-listing path at scale.

Deliberately not re-derived (siblings of this run): GC rebuild orphaning already-unreferenced blobs (`gc-rebuild-feature`); durable blob body before a never-committed build (`write-protocol`, `crash-consistency`); local write-buffer spill residue (`bc2-writebuffer-spill`); `cas/blobs/` being listed by nothing but fsck (`gc-protocol`).

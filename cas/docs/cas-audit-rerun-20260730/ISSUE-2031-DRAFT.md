**DRAFT — DO NOT POST until reviewed. Proposed replacement body for https://github.com/Altinity/ClickHouse/issues/2031.**

# CAS (`metadata_type = content_addressed` MergeTree backend) — consolidated audit tracking

This is a **tracking issue** for a static-analysis audit of the Content-Addressed Storage (CAS) MergeTree
disk backend. It consolidates audit reports into a single deduplicated checklist of **131 distinct
findings**, each with a unique `CAS-###` id.

> [!IMPORTANT]
> This is a static/logical review. **Many items are expected to be by-design, not-a-bug, latent, or
> already-handled.** The checklist is meant to be triaged item-by-item — please dismiss or resolve freely.

### 📎 Audit reports
- **Original (2026-07-09)**: https://gist.github.com/vzakaznikov/8b0506a495187ce3d634385544beebea
- **Re-run vs PR #2073 (2026-07-30)**: *https://gist.github.com/alsugiliazova/7fb1441688ff428cc0e0a18918077c26* — all per-audit reports + `RECONCILIATION.md` + New Findings.
- **PR under review**: https://github.com/Altinity/ClickHouse/pull/2073

### How to triage
For each item, when reviewed:
1. **Check the box** once it is triaged (resolved, dismissed, or filed as its own issue).
2. Replace `resolution:` inline with a verdict, e.g.
   `✅ fixed (#PR)` · `🛠 will-fix` · `❌ wontfix` · `🚫 not-a-bug` · `📐 by-design` · `🟡 needs-repro` · `↗ split-out (#NNN)` · `🔴 still-present`.
3. Add reasoning as a **comment** referencing the `CAS-###` id.

Severity is the highest assigned by any source audit. Class tags:
`DATA-LOSS · LEAK · LIVENESS · CONCURRENCY · INTEGRITY · SECURITY · DECODE/DoS · COMPAT · FEATURE-GAP ·
PERF/SCALE · OBSERV/DAY2 · COMPLIANCE · CONFIG · TEST-GAP · CORRECTNESS`.

---

## 🔴 High

- [x] **CAS-001** Reader holds no pin across the deferred, unpinned blob GET → a `dropRef`+GC condemn→delete can remove a committed blob mid-query for ref-… · `DATA-LOSS` — resolution: 🚫 not-a-bug (Filimonov: not reachable in CH — reader cannot keep reading after part removed) · re-audit still flags ref-less/cross-node path
- [x] **CAS-002** Shard `casPut` fenced by content token, not `writer_epoch` → pause/TOCTOU/clone/clock-skew opens a dual-writer window (split-brain / zomb… · `SECURITY / CORRECTNESS` — resolution: 🚫 not-a-bug / 🟡 needs-repro (Filimonov: looks overstated / "высосана из пальца"; maybe recheck carefully — **not a blocker**)
- [x] **CAS-003** Non-cryptographic content hash (CityHash128) + reads never re-verify → collision-based blob poisoning across a shared pool via pool-globa… · `SECURITY / INTEGRITY` — resolution: 🟡 partial / 📐 by-design (Filimonov: selectable hash landed — closes weak-collision concern; will **not** re-verify hash on read — incompatible with "CH does not slow down")
- [x] **CAS-004** No intra-pool authorization; identities self-asserted → bucket credential is the whole perimeter; a pool-write peer can forge mounts, tam… · `SECURITY` — resolution: 📐 by-design (Filimonov: bucket credential = whole trust boundary; all pool users same trust)
- [x] **CAS-005** Blob payload never re-hashed against `logical_hash` on the normal read path → silent S3 bit-rot / truncation undetected by CAS; integrity… · `INTEGRITY` — resolution: 📐 by-design / YAGNI (Filimonov: S3 has many durability nines and hashes objects itself; CAS will not re-hash on read)
- [x] **CAS-006** CAS durable publish runs under `DataPartsLock` (blob PUTs + precommit + promote + ref CAS, each with retries) → table-wide writer/DDL sta… · `LIVENESS / PERF` — resolution: ✅ fixed (Filimonov: durable publish no longer runs under `DataPartsLock`)
- [x] **CAS-007** UniqueKey / upsert MergeTree: DeleteBitmap + SSTIndex hot-rewrite — delete-bitmap is not in the mutable-per-part set, so every `replaceFi… · `FEATURE-GAP / PERF` — resolution: 🚫 not-a-bug / 🟡 soft (Filimonov: should be fine — tests catch nothing; glance someday — **not a blocker**)
- [x] **CAS-008** Untrimmed root-shard journal under churn hits the 64 MiB hard limit → writes rejected until GC folds/trims. Couples write availability to… · `LIVENESS / SCALE` — resolution: ✅ fixed (Filimonov: journals should be fine now — he fixed this)
- [x] **CAS-009** Rolling upgrade across a format-generation bump breaks old nodes — `compatibility_version` always stamped at `G_BUILD` (write-down-to-flo… · `COMPAT` — resolution: ↗ out-of-scope (Filimonov: needs attention later; not a blocker; model may be wrong)
- [x] **CAS-010** No coverage-guided fuzzing of any CAS decoder despite untrusted shared-pool bytes (envelope, run-file, manifest, root-shard, gc-formats, … · `TEST-GAP / DoS` — resolution: 📐 by-design / YAGNI (Filimonov: same trust model as CAS-005 — trust S3; less trust ⇒ more perf loss; no decoder fuzz mandate as gate)
- [x] **CAS-011** Bucket versioning / GCS soft-delete silently breaks GC reclaim; guarded only when the versioning API is queryable, else fails open (mount… · `OBSERV / LEAK` — resolution: ✅ fixed / 📐 by-design (Filimonov: CAS checks at startup that versioning is off; versioned buckets unsupported)
- [x] **CAS-012** Native conditional-write path not end-to-end tested on real S3/GCS (only RustFS + emulation) — the single most safety-critical untested s… · `TEST-GAP` — resolution: ✅ fixed (Filimonov: e2e tested on real S3 and GCS; Azure still not)
- [x] **CAS-013** `fsck` (reachability / dangling / physical-vs-logical) is not operator-accessible via SQL — the most valuable health diagnostic is intern… · `OBSERV/DAY2` — resolution: ✅ fixed (Filimonov: SQL fsck landed; still slow vs GC — backlog to speed up)
- [x] **CAS-014** No GC-liveness / reclaim-backlog / physical-bytes metric — the most common silent failure ("GC stopped reclaiming") is invisible without … · `OBSERV/DAY2` — resolution: ✅ fixed / 🛠 recheck (Filimonov: should be OK now; worth re-verify — **not a blocker**)
- [x] **CAS-015** `GC REBUILD` has no mount-lease interlock → run against a live pool, its non-atomic universe/blob scans can bless a baseline missing a co… · `DATA-LOSS` — resolution: 🟡 partial (Filimonov: GC REBUILD still poorly tested / may have issues; mount-lease should take correctly now — **not a blocker**)
- [x] **CAS-016** Lifecycle expiration rule deletes live blobs (age-based rules hit the oldest, most-shared blobs) → dangling refs / data loss. Unguarded. · `DATA-LOSS / CONFIG` — resolution: 📐 by-design / 🛠 docs (Filimonov: lifecycle expiration must be off like versioning; add explicit user-facing bucket requirements; hard to detect without admin access)
- [x] **CAS-017** Object Lock / WORM / retention breaks CAS entirely — mutable root-shards and `gc/state` cannot be overwritten → all writes + GC fail. Ung… · `CONFIG / LIVENESS` — resolution: 📐 by-design (Filimonov: do not enable Object Lock/WORM/retention/lifecycle/versioning on the bucket — plain bucket only)
- [x] **CAS-018** No bounded delete→physical-erase SLA — reclaim is GC-deferred and stallable indefinitely; cannot promise GDPR/CCPA erasure deadlines from… · `COMPLIANCE` — resolution: 📐 by-design / ❌ wontfix (Filimonov: erase SLA is not part of the disk contract; operator can `GC RUN` anytime; GC cadence ~5–10 min; GDPR faster-than-that unlikely)
- [x] **CAS-019** Dedup means one owner's delete may erase nothing while any other ref shares the byte-identical blob; no per-subject "shred everywhere" pr… · `COMPLIANCE` — resolution: 📐 by-design / ❌ wontfix (Filimonov: this *is* the essence of CAS dedup — will not "fix")
- [x] **CAS-046** `DiskEncrypted` random-IV ciphertext defeats content-addressed dedup — every encrypted file becomes a unique blob; CAS's whole value null… · `FEATURE-GAP` — resolution: ↗ out-of-scope (Filimonov: CAS+encryption needs design/dev/testing; should be workable later — not now)

## 🟠 Medium

- [x] **CAS-020** `promote`-overwrite leaks the prior committed manifest (unconditional `refs[R]=…`); reachable via RENAME / lost-ACK replay. The only non-… · `LEAK` — resolution: ✅ fixed (Filimonov: will-address retry/republish; code now OwnerTransition/allow_repoint) — `Pool/CasRefProtocol.cpp:262-265`, `Parts/PartFolderAccess.cpp:520-529`
- [ ] **CAS-021** Multi-part `commit()` is not atomic → power-loss / compounded-failure mid-loop leaves a durable partial commit; best-effort rollback is n… · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:458-513``
- [ ] **CAS-022** RENAME TABLE (`moveDirectory`) is non-atomic multi-op → crash mid-way leaves a table split across namespaces; re-drivable but no durable … · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:1200-1287``
- [x] **CAS-023** Teardown UAF / `std::terminate` race — `scheduleRemount` ignores `remount_stop`; keeper stopped after remount join can re-arm a thread on… · `CONCURRENCY` — resolution: ✅ fixed — ``Pool/CasMountRuntime.cpp:486-502` (`remount_shutting_down` latch under `remount_thread_mutex`)`
- [ ] **CAS-024** `locate()` uses fixed `PoolMeta.blob_header_len`, not the blob's own envelope `header_len` → wrong payload offset under config drift / mi… · `CORRECTNESS` — resolution: 🔴 still-present — ``Pool/CasManifestReader.cpp:144-168``
- [x] **CAS-025** `PartManifest.payload_digest` written but never re-verified on decode/read → a bit-flip in a `blob_hash`/`blob_size` is undetected. · `INTEGRITY` — resolution: ✅ fixed — ``Formats/CasPartManifestFormat.cpp:293-302``
- [x] **CAS-026** Protobuf `ParseFromArray` with unchecked `static_cast ` and no size cap → OOM / negative-size on a corrupt/planted oversized object; no d… · `DECODE/DoS` — resolution: ✅ fixed (Filimonov 2026-07-17: protobuf/binary formats removed → self-describing text) — `Formats/CasTextFormat.cpp:389,401`
- [ ] **CAS-027** Additive protobuf fields dropped on re-encode by an older build → silent mixed-version control-plane data loss. · `COMPAT / DATA-LOSS` — resolution: 🔴 still-present — ``Formats/CasPartManifestFormat.cpp:145-152` (`skipUnknown` + decode-to-struct → additive fields dropped on re-encode)`
- [x] **CAS-028** `RunFileReader::next()` parses record `klen`/`plen` with unchecked `operator[]`/`substr` → OOB heap read / non-`CORRUPTED_DATA` throw on … · `DECODE/DoS` — resolution: ✅ fixed (Filimonov 2026-07-17: protobuf/binary formats removed → NDJSON record streams) — `Formats/CasRecordStreamFormat.cpp:228–304`
- [ ] **CAS-029** VM-clone / snapshot split brain — two live servers share one `server_uuid`; dual mount bounded only by renew period. · `CORRECTNESS` — resolution: 🔴 still-present (Filimonov: narrow J2 dual-mount; will check deeper)
- [x] **CAS-030** Wall-clock mount-lease expiry vs boot-clock local fence → clock skew → premature reclaim / false unavailability (token-guarded, no corrup… · `CORRECTNESS / SECURITY` — resolution: ✅ fixed / 🟡 residual tradeoff (Filimonov 2026-07-17: lease liveness via token stability on observer clock, no cross-node wall-clock trust; remaining mount-wait tradeoff accepted)
- [ ] **CAS-031** Relink / rename receiver trusts sender-supplied `entry.blob_size`/`path` (`payload_digest` ignored) → only blob *presence* revalidated → … · `INTEGRITY` — resolution: 🔴 still-present — ``Pool/CasPartWriteTxn.cpp:781-796`; receiver at `ContentAddressedMetadataStorage.cpp:2143-2221``
- [ ] **CAS-032** Zombie GC leader's unconditional `pulseHeartbeat` clobbers `gc/hb.owner` (defeats B160) → a follower can steal the lease from a live long… · `LIVENESS` — resolution: 🔴 still-present — ``Gc/CasGc.cpp:2989-3003``
- [x] **CAS-033** Persistent shard clamp → pool-wide `suppress_destructive` halts all reclamation with no self-heal (safety-preserving). · `LIVENESS` — resolution: 📐 by-design (Filimonov: prefer fail-closed safety under GC uncertainty; reclaim may stall)
- [ ] **CAS-034** Coalesced shard read has no deadline → a hung leader GET blocks all coalesced followers (reader convoy). · `LIVENESS` — resolution: 🔴 still-present — ``Parts/PartFolderAccess.cpp:264-303``
- [ ] **CAS-035** Presence-asserting closures misreport a lost-ACK-succeeded write as failure (e.g. `dropRef` re-reads its own committed drop → `FILE_DOESN… · `CORRECTNESS` — resolution: 🔴 still-present (Filimonov: minor; doubts whether removal retries should be idempotent)
- [x] **CAS-036** `blob_header_len` floor (96, 8-aligned) is below the mandatory provenance-TLV need (~128 B) → configuring 96–120 bricks all blob writes (… · `CONFIG` — resolution: ✅ fixed — ``Formats/CasPoolMetaFormat.cpp:36-46``
- [x] **CAS-037** Content-hash algorithm is an unversioned, unpinned pool contract (not recorded in `PoolMeta`); a future CityHash/algorithm change silentl… · `INTEGRITY / COMPAT` — resolution: ✅ fixed (Filimonov 2026-07-17: selectable CityHash128/XXH3-128/SHA256 recorded in PoolMeta, fail-closed) — `Formats/CasPoolMetaFormat.h:29-31`, `Pool/CasPoolMeta.cpp:56-102`
- [ ] **CAS-038** Scratch temp file un-fsynced and never verified against its key between hash and upload → local scratch corruption → silent wrong-bytes b… · `INTEGRITY` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:1819–1846` (finalize hands `hash_hex` and `temp_path` with no re-verify) + `Pool/CasPartWriteTxn.cpp:594–602` (upload verifies `
- [x] **CAS-039** Envelope size-consistency check bypassable via `logical_size` uint64 overflow wrap (`header_len + logical_size == object_size`). · `DECODE` — resolution: ✅ fixed — ``CasBlobEnvelopeFormat.cpp:162,240-248` — `logical_size` removed from envelope; `header_len` derived from `'\n'`; the size-consistency invariant it tried to enf`
- [ ] **CAS-040** `system.parts.bytes_on_disk` is logical, over-reports physical N× under dedup; no physical/dedup-ratio system view (numbers exist only in… · `OBSERV` — resolution: 🔴 still-present — ``Storages/System/StorageSystemParts.cpp:74``
- [ ] **CAS-041** Cross-disk `MOVE PARTITION TO DISK/VOLUME` is unverified and byte-copies (no relink even CAS→CAS same-pool). · `FEATURE-GAP / PERF` — resolution: 🔴 still-present — ``tests/queries/0_stateless/04280_content_addressed_clone_partition_works.sql` (same-disk only); `src/Storages/MergeTree/DataPartStorageOnDiskBase.cpp:735` byte-`
- [ ] **CAS-042** BACKUP is Atomic-DB-only (Ordinary/non-UUID DBs rejected on the temp-hardlink path); incremental-backup dedup + RESTORE round-trip untested. · `FEATURE-GAP` — resolution: 🔴 still-present — ``DataPartStorageOnDiskBase.cpp:417-427`; no BACKUP/RESTORE CAS IT`
- [ ] **CAS-043** DROP/TRUNCATE/TTL-move frees zero bytes synchronously (GC-deferred; leaks forever if GC disabled/read-only); TTL move off-CAS double-bill… · `LEAK / OBSERV` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:1032-1074`; `Gc/CasGc.cpp:1833,2075,2170``
- [ ] **CAS-044** Crash between catalog drop and `dropNamespace` → permanently orphaned namespace (live refs, no owning table); no catalog-vs-pool reconcil… · `LEAK` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:1032-1074`; `Pool/CasRefLedger.cpp:2979-2982``
- [x] **CAS-045** ZK part-set vs CAS ref can diverge on partial commit (ZK-has/CAS-missing → broken part; CAS-has/ZK-missing → invisible live-ref leak). · `CORRECTNESS / LEAK` — resolution: 🚫 not-a-bug / not CAS (Filimonov: general ReplicatedMergeTree ZK↔storage divergence; RMT already recovers via detached/re-fetch)
- [ ] **CAS-047** Two "size" semantics for a file (payload-only from `getStorageObjects` vs envelope+payload plan); correctness depends on all reads going … · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedMetadataStorage.cpp:1793` vs `:1915-1917``
- [ ] **CAS-048** `getLastModified` = ref publish time (resets on relink) / epoch(0) for verbatim / throws on unresolved → cross-replica divergence, part-c… · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedMetadataStorage.cpp:1565-1595`, publish stamp restamped at `CasPartWriteTxn.cpp:1240``
- [ ] **CAS-049** Decode caches wholesale-clear at 16384 entries (no LRU) → thundering-herd re-HEAD/GET/decode cliff at scale / high multi-tenancy. · `PERF/SCALE` — resolution: 🟡 partial/mitigated — ``Pool/CasManifestReader.cpp:37-40` (bytes+count LRU; count cap = fixed 16384)`
- [ ] **CAS-050** `GC REBUILD` zero-condemn scan is O(all blobs) with a synchronous HEAD each, unbudgeted → millions of round-trips exactly at DR time. · `PERF/SCALE` — resolution: 🔴 still-present — ``CasGc.cpp:2749–2770`; `discoverUniverse()` duplicated at `:2517` and `:2648``
- [ ] **CAS-051** Cross-region replication accumulates an un-GC'd shadow bucket; failover onto it is token/ETag-incoherent and unvalidated. · `CORRECTNESS / LEAK` — resolution: 🔴 still-present — `Whole-tree: no cross-region/replica awareness; `Backend/CasObjectStorageBackend.cpp` deleteExact/promote path source-only`
- [ ] **CAS-052** Archive-tier transition (Glacier/IA/Deep-Archive) leaves cold blobs present-but-unreadable; read path has no restore-and-retry → query fa… · `FEATURE-GAP` — resolution: 🔴 still-present — ``Pool/CasManifestReader.cpp:56` + `Backend/CasObjectStorageBackend.cpp` (no `InvalidObjectState` / restore handling)`
- [ ] **CAS-053** Throttle/429/SlowDown storms compound with CAS-conflict retries (no CAS-level adaptive backoff) → retry storm / latency collapse. · `LIVENESS` — resolution: 🔴 still-present — ``Backend/CasRequestControl.cpp:46-56` lumps 429/5xx with `PreconditionFailed``
- [x] **CAS-054** Relink cookie *value* not validated (only presence); pool-uuid/metadata_version framing is an implicit wire contract → a future v2 framin… · `COMPAT` — resolution: ✅ fixed — ``DataPartsExchange.cpp:128, 916-924, 935-937``
- [ ] **CAS-055** Non-MergeTree engines / `tmp` disks / SSD-cache dictionaries / Distributed spool are ungated on a CAS disk → runtime `NOT_IMPLEMENTED`/mi… · `CONFIG / FEATURE-GAP` — resolution: 🔴 still-present — `no `isContentAddressed()` gate in `src/Storages/StorageLog.cpp` / `StorageStripeLog.cpp` / `StorageDistributed.cpp` / `registerStorages.cpp` / `Interpreters/**``
- [ ] **CAS-056** `root_shards` is a fixed, pool-wide, create-time constant — one-shot write-parallelism decision, no live reshard; same-shard writes singl… · `SCALE / CONFIG` — resolution: 🟡 partial/mitigated — ``gc_shards` create-once `Gc/CasGc.cpp:3022-3025`; root shards gone`
- [ ] **CAS-057** GC discovery LIST is O(namespaces × shards) — round cost scales with pool size, not churn; no parallel discovery. · `PERF/SCALE` — resolution: 🟡 partial/mitigated — ``Gc/CasGc.cpp:2393-2411` (single LIST, no ns×shard fan-out)`
- [ ] **CAS-058** Read-your-writes / strongly-consistent LIST is a hard, per-backend assumption (startup part discovery, drop enumeration, rebuild) — S3 ok… · `COMPAT` — resolution: 🔴 still-present — ``Pool/CasPool.cpp:1326-1328`; `Gc/CasGc.cpp:2397-2398``
- [ ] **CAS-059** MergeTree experimental transactions (MVCC `txn_version`) mechanically supported but untested on CAS; multi-part visibility inherits parti… · `TEST-GAP / FEATURE-GAP` — resolution: 🟡 partial/mitigated — ``05004_content_addressed_transactions.sh`; multi-part merge B53 gap`
- [ ] **CAS-060** Failed-build debris reclaimed only by sweeps; failure storms (OOM/disk-full) accumulate debris faster than sweeps clear → transient bloat. · `LEAK / LIVENESS` — resolution: 🔴 still-present — ``Pool/CasServerRoot.cpp:1239-1274`; orphan/precommit sweeps`
- [ ] **CAS-061** Full-text (GIN/Text) & vector-similarity index build/merge/read on CAS untested (large multi-file structures, inline-cap/stream behavior,… · `FEATURE-GAP` — resolution: 🔴 still-present — `absence of text/GIN/vector tests under `test_cas_*` / `test_content_addressed_*``
- [ ] **CAS-062** No lease/owner introspection or documented force-release/recovery runbook (stuck lease on dead server, reused `server_root_id`). · `OBSERV/DAY2` — resolution: 🛠 will-fix — ``StorageSystemContentAddressedMounts.cpp:40-59`; `DROP_POOL_MEMBER``
- [ ] **CAS-063** No `PoolMeta` / control-plane backup-restore story — a corrupt `PoolMeta` fails the mount closed with no runbook. · `OBSERV/DAY2` — resolution: 🔴 still-present — `absence of PoolMeta backup/restore under `Pool/`/`Tools/``
- [ ] **CAS-064** `server_root_id` uniqueness is operator-owned; collision → mount-lease outage, reuse → inherits stale owner/epoch. · `CONFIG` — resolution: 🔴 still-present — ``Pool/CasServerRoot.h:188-223`; `CasServerRoot.cpp:428-432``
- [ ] **CAS-065** Azure / non-S3 object stores effectively unsupported for Native CAS (`conditionalOpsUseGenerationTokens`/versioning only in S3ObjectStora… · `COMPAT` — resolution: 🔴 still-present — ``Backend/CasObjectStorageBackend.cpp:94-108``
- [ ] **CAS-066** `createOrValidate` silently ignores passed `root_shards`/`blob_header_len` when a pool exists (validates then uses persisted values, no o… · `CONFIG` — resolution: 🔴 still-present — ``Pool/CasPoolMeta.cpp:118-124``
- [ ] **CAS-067** No read-side blob cache/pin — cold reads re-GET each blob; warm-read cost depends entirely on the two decode caches. · `PERF` — resolution: 🔴 still-present — ``Pool/CasPool.h:68-78` (dedup+manifest caches only; no read blob pin)`
- [ ] **CAS-068** FS-cache-over-CAS caches whole-blob (envelope-inclusive) ranges; FileView applied above — correct but envelope-offset alignment under par… · `TEST-GAP` — resolution: 🟡 partial/mitigated — ``DiskObjectStorage.cpp:876-922`; `test_cas_file_cache` (no partial-hit envelope test)`
- [ ] **CAS-069** Migration onto/off CAS is always a full data rewrite (no in-place conversion), transiently double-bills, and a CAS volume narrows the who… · `FEATURE-GAP / PERF` — resolution: 🔴 still-present — `no in-place converter; `DataPartStorageOnDiskBase.cpp:748``
- [ ] **CAS-070** FREEZE shadow refs, detached refs, and `gc/snap` retention silently retain deleted data/metadata — erasure must sweep every FREEZE/detach… · `COMPLIANCE` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:1044-1074`; `Pool/CasPool.h:79-84``
- [ ] **CAS-071** No crypto-shred; physical erasure depends on backend DELETE semantics (versioning/soft-delete/CRR may retain copies CAS never removes). · `COMPLIANCE` — resolution: 🔴 still-present — ``Backend/CasObjectStorageBackend.cpp:55-84`; `Gc/CasGc.cpp:519``
- [ ] **CAS-093** `fsck` detects Dangling (=already-lost) but never repairs; no forced cadence — non-replicated tables: dangling = permanent part loss. · `INTEGRITY / DAY2` — resolution: 🔴 still-present — ``Tools/CasFsck.cpp` (no repair path); `InterpreterSystemQuery.cpp:2524-2551` (no `REPAIR` verb)`
- [ ] **CAS-113** `DiskEncrypted`-over-CAS leaves control-plane metadata plaintext, read-path composition untested/unguarded, cross-replica dedup lost. · `SECURITY / TEST-GAP` — resolution: 🔴 still-present — `control-plane via `CasObjectStorageBackend`; 0 DiskEncrypted refs in CAS tree`

## 🟡 Low / hardening

- [ ] **CAS-072** Post-CAS T0 hand-off reclaim: a crash between the round CAS and the hand-off permanently strands a `gc/gen/ /` prefix (fsck-only, no auto… · `LEAK` — resolution: 🔴 still-present — ``Gc/CasGc.cpp:793-833``
- [ ] **CAS-073** `looksLikePartDir` false-positives on non-Atomic table/dir names ending in three numeric groups → misroutes table files as part files. · `CORRECTNESS` — resolution: 🔴 still-present — ``Parts/PartPathParser.cpp:136-168``
- [ ] **CAS-074** `checkNamespace` / `mountpointObjectKey` don't reject `.`/`..` → path-traversal risk on a filesystem/normalizing backend (safe only for l… · `SECURITY` — resolution: 🔴 still-present — ``Formats/CasLayout.cpp:260-284` + `CasLayout.h:229-235` (`mountpointObjectKey`)`
- [x] **CAS-075** Envelope `header_hash` (CityHash64) covers only the 94-B core, not TLVs; "critical extension" enforcement relies on writer honesty. · `INTEGRITY` — resolution: ✅ fixed — ``Formats/CasBlobEnvelopeFormat.h:53–58` (`header_hash` removed); `!`-key gate `CasTextFormat.cpp:249–251``
- [ ] **CAS-076** `FormatId::Roster` defined but `magicFor(Roster)` throws → dead/incomplete path. · `CORRECTNESS` — resolution: 🔴 still-present — ``Formats/CasFormat.cpp:112-118` (`traitsFor` throws for `FormatId::Roster`)`
- [ ] **CAS-077** `decodeFoldSeal` casts `folded_token_type`/`classification` enums without validation (unlike sibling decoders). · `DECODE` — resolution: 🔴 still-present — ``Formats/CasFoldSealFormat.cpp:189` (`cls` uint8 truncation cast); `tt` half fixed via `tokenTypeFromWord``
- [ ] **CAS-078** Concurrent probes of a shared `probe_prefix` can spuriously read `NOT_IMPLEMENTED` (low: `Store::open` uses a unique prefix). · `CORRECTNESS` — resolution: 🔴 still-present — ``Backend/CasProbe.cpp:61-67`; call-site at `ContentAddressedMetadataStorage.cpp:788``
- [ ] **CAS-079** Non-atomic HEAD-then-GET can pair an old token with new bytes / wrong ranged size for a mutable object (masked by CAS write patterns). · `CORRECTNESS` — resolution: 🔴 still-present — ``Backend/CasObjectStorageBackend.cpp:599-636``
- [ ] **CAS-080** `allocateWriterEpoch` has no overflow guard; a fresh mount pins the GC heartbeat floor to 0 until first renewal (transient GC stall on st… · `CORRECTNESS` — resolution: 🔴 still-present — ``Pool/CasServerRoot.cpp:249-251`; MountLease `min_active` default 0`
- [x] **CAS-081** `abandon` retires `build_seq` before appending the precommit-removal event (fragile ordering; safe only because in-degree is a set). · `CORRECTNESS` — resolution: ✅ fixed — ``Pool/CasPartWriteTxn.cpp:1354–1413` (`abandon` appends precommit-removal, THEN flips `alive`, THEN retires seq; ordering documented at 1407–1412)`
- [ ] **CAS-082** Lost-ACK replay double-appends journal events (set-idempotent → journal bloat only). · `LEAK` — resolution: 🔴 still-present (Filimonov: minor; will probably fix journal double-append on idempotent retry)
- [ ] **CAS-083** Flat-combining leader convoy + batch-wide failure amplification under S3 stall (latency, not correctness). · `LIVENESS` — resolution: 🔴 still-present (Filimonov: minor; will probably fix batch timeout/control)
- [ ] **CAS-084** Orphan multipart uploads / ownerless manifest bodies on interrupt — reclaimed by S3 lifecycle + watermark sweep; CAS neither aborts nor r… · `LEAK / DAY2` — resolution: 🔴 still-present (Filimonov: minor; MPU leftovers typical for S3, GC cleans eventually)
- [x] **CAS-085** `allow_stale` decode-TTL ↔ GC condemn→delete latency coupling is a convention, not an enforced invariant. · `CORRECTNESS` — resolution: ✅ fixed (Filimonov classed R3 cosmetic; `allow_stale` retired in code) — `Pool/CasRefLedger.cpp:174-179`
- [ ] **CAS-086** `readManifest` HEAD+GET is not coalesced and absence not negatively cached → HEAD+GET storm under throttling. · `PERF` — resolution: 🔴 still-present (Filimonov: R4 classed minor/cosmetic with R2–R4)
- [ ] **CAS-087** Force-fresh read isn't fresh on eventually-consistent backends (backend-conditional stale serve/retry). · `COMPAT` — resolution: 🔴 still-present — ``Pool/CasPool.cpp:1326-1328` (assumption declared, not enforced); `Parts/PartFolderAccess.cpp:166-215``
- [x] **CAS-088** Lost/corrupt GC-internal artifacts wedge GC until manual `GC REBUILD` (by-design fail-stop-then-recover). · `LIVENESS` — resolution: 📐 by-design (Filimonov: corrupt GC state ⇒ GC stop; recover via GC REBUILD)
- [x] **CAS-089** Regular-round mass-drop delta is a non-streaming in-memory point (rebuild is batched; regular round isn't). · `PERF/SCALE` — resolution: ❌ wontfix / architectural limit (Filimonov: huge single-round delta is a known limit, not a bug)
- [x] **CAS-090** `mount_keeper` `unique_ptr` reassigned without synchronization vs `renewWatermarkOnce` (latent UAF; safe only by unenforced config mutual… · `CONCURRENCY` — resolution: 📐 by-design — ``Pool/CasMountRuntime.h:400`; `Pool/CasMountRuntime.cpp:156-163` (`renewWatermarkOnce` unlocked); `:226-249` (reassign under `Pool::remount_mutex` only)`
- [x] **CAS-091** `event_sink_` published after keeper thread start (`std::function` data race; timing-masked). · `CONCURRENCY` — resolution: ✅ fixed — ``Pool/CasPool.cpp:441-461` (setEventSink before `mountWritable`); `Pool/CasEventDispatcher.cpp:37-42` (residual)`
- [x] **CAS-092** `shard_write_seq` never pruned on `dropNamespace` → unbounded growth by lifetime (namespace, shard) pairs. · `LEAK` — resolution: ✅ fixed — ``Pool/CasRefLedger.cpp:762-810`, `Pool/CasPool.h:204``
- [ ] **CAS-094** No proactive scrubbing of cold blobs — bit-rot accumulates until a query/CHECK TABLE touches it (one rotted shared blob damages every ded… · `INTEGRITY` — resolution: 🔴 still-present — `absence of cold-blob scrub/re-hash in `Gc/`/`Tools/``
- [ ] **CAS-095** Fragile read-window arithmetic: `resizeWorkingBuffer` size_t-underflow-then-signed-cast; `SEEK_CUR` negative underflow caught only downst… · `DECODE` — resolution: 🔴 still-present — ``ReadBufferFromFileView.cpp:169-179` — size_t-underflow-then-signed-cast unchanged.`
- [ ] **CAS-096** Scratch-FS-full/error fails the insert late (no pre-flight check; undocumented sizing); temp-file uniqueness relies on a random string (a… · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:1749`, `.cpp:904–914`, `ContentAddressedMetadataStorage.h:381` (no preflight FS-full check; `scratchPath()` capacity contract u`
- [ ] **CAS-097** `updateRefPayload` one-shots are intentionally not rolled back → "commit failed" ≠ "no durable effect"; already-published refs transientl… · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:468-472, :509-512``
- [ ] **CAS-098** Wide-part read path branches: inline vs blob dual path, right-mark mid-stream narrowing, projection nested-key routing — all correct, eac… · `TEST-GAP` — resolution: 🔴 still-present — ``src/Disks/tests/gtest_cas_part_write.cpp` is the only file mentioning `wide_part`; no dedicated wide/compact/packed read-branch gtest; stateless tests do not t`
- [ ] **CAS-099** `setLastModified` is a no-op ("touch to refresh age" silently fails); `clearOldTemporaryDirectories` inert on CAS (GC is the real tmp rea… · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:1180-1186` (no-op body; only Vanished-disk gate added)`
- [ ] **CAS-100** Manifest soft-limit backpressure (≤1 s, per-flush) delays but can't prevent the hard-limit wedge; no per-tenant quota in a shared pool (f… · `SCALE` — resolution: 🔴 still-present — ``Pool/CasRefLedger.cpp:1208`, `Pool/CasBlobUploadPool.h:54`, `Pool/CasPartWriteTxn.cpp:824-872``
- [ ] **CAS-101** System-table quirks: empty `remote_path` for in-manifest files, many-to-one remote paths, placeholder free space, unverified mutations/pa… · `OBSERV` — resolution: 🔴 still-present — ``Storages/System/StorageSystemParts.cpp:74`; `StorageSystemReplicatedFetches.cpp` unchanged`
- [ ] **CAS-102** Relink vs byte-fetch indistinguishable in `system.replicated_fetches`; cache observability by blob key not part path (join needed). · `OBSERV` — resolution: 🔴 still-present — ``Storages/System/StorageSystemReplicatedFetches.cpp:27-60` (no relink flag)`
- [ ] **CAS-103** Move-vs-concurrent-GC untested (R1/X1 class); `move_factor` free-space heuristics inert on CAS source. · `TEST-GAP` — resolution: 🔴 still-present — `No `MOVE PART`/`MOVE PARTITION` grep hits in `tests/integration/test_c*a*s*/**` or `tests/queries/0_stateless/*content_addressed*` (only `04280_content_addresse`
- [ ] **CAS-104** Non-replicated dedup-log durability rides mutable-file commit; crash mid-update → bounded duplicate part (CAS content-dedups anyway). · `CORRECTNESS` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:800-824`; `Parts/PartPathParser.h:72-75``
- [ ] **CAS-105** RESTORE round-trip + Packed storage-type parts (arriving via RESTORE/ATTACH) untested/unsupported on CAS. · `TEST-GAP / FEATURE-GAP` — resolution: 🔴 still-present — ``05005_content_addressed_backup_restore.sh` / `04284_content_addressed_backup_pointer_holding.sh` do not cover Packed storage-type parts on RESTORE`
- [x] **CAS-106** GC cadence/retention knobs (`gc_interval`, `gc_snap_generations_to_keep`, sweep budgets) directly gate reclaim latency (LC-1). · `CONFIG` — resolution: 📐 by-design — ``Pool/CasPool.h:84,90-99,103``
- [ ] **CAS-107** Big-endian would silently fork dedup (no explicit LE guard); manifest bytes / ManifestId not version-stable across CH versions (harmless). · `COMPAT` — resolution: 🔴 still-present — `no `static_assert`/BE guard in tree; explicit BE wire ops at `Primitives/CasCodecUtil.h:18-40`, `Primitives/CasBlobDigest.h:177-186`, `Gc/CasGcShardPlan.h:38-41`
- [ ] **CAS-108** `GC REBUILD` DoS/amplification + `FORCE` blast radius (SYSTEM-gated); interrupted rebuild leaks un-swept `gc/gen` artifacts and ratchets … · `DAY2 / LEAK` — resolution: 🔴 still-present — ``Gc/CasGc.cpp:2570-2594, 2861, 2874-2879, 2338-2367``
- [ ] **CAS-109** System log tables on CAS produce a tiny-part storm (manifest/ref churn + inflated logical bytes); tooling (`clickhouse-disks`), `EXCHANGE… · `PERF / TEST-GAP` — resolution: 🔴 still-present — `no `*content_addressed*` test references `system.query_log` / `part_log`, `EXCHANGE TABLES`, `clickhouse-disks`, or cache/web disk over CAS`
- [ ] **CAS-110** FETCH-to-detached never relinks (full byte transfer even same-pool); quorum/SYNC REPLICA/cloneReplica correct-by-composition but untested. · `PERF / TEST-GAP` — resolution: 🟡 partial/mitigated (Filimonov: RPL-4 will recheck; RPL-5 soft-dismiss — ran all stateless on CAS; SYNC covered in IT)
- [x] **CAS-111** Committed single-file `unlinkFile` is a deliberate fail-open no-op — becomes a correctness bug if a future path surgically deletes one co… · `CORRECTNESS` — resolution: ✅ fixed — ``ContentAddressedTransaction.cpp:1520-1568`, repoint at `:362-381``
- [ ] **CAS-112** `chmod` / `generateObjectKeyForPath` throw `NOT_IMPLEMENTED` (latent; no MergeTree path calls them today). · `FEATURE-GAP` — resolution: 🔴 still-present — ``ContentAddressedTransaction.cpp:531-533,1188-1191``
- [x] **CAS-114** Storage-class cost/latency skew from tiering; CAS sets no storage class (bucket default applies). · `CONFIG` — resolution: ⚪ info — `zero matches for `storage_class`/`StorageClass` in CAS tree; bucket default applies`
- [x] **CAS-115** Manifest duplicate-path detection is adjacent-only (`prev_path` check, valid only because encode sorts) → a corrupt/unsorted embedded Run… · `DECODE / INTEGRITY` — resolution: ✅ fixed — ``Formats/CasPartManifestFormat.cpp:257–267` (strict-ascending check catches non-adjacent duplicates)`
- [x] **CAS-116** Per-file `lookupPath`/`listDirectory` are linear scans over `manifest.entries` → O(entries²) to read all files of a wide part (thousands … · `PERF/SCALE` — resolution: ✅ fixed — ``Formats/CasPartManifestFormat.cpp:329-351`; `Parts/PartFolderAccess.cpp:85-134``
- [ ] **CAS-117** `FINAL` / parallel-replica reads / lightweight-update patch-apply-on-read untested for correctness-under-concurrent-merge — all issue mor… · `TEST-GAP` — resolution: 🔴 still-present — `no FINAL/patch-apply references in `ContentAddressed/**``

## ⚪ Info / by-design / verified-safe (non-actionable — for the record)

- [x] **CAS-201** B151 early publish in `moveDirectory` exposes a rollback-window read; commit-time non-atomicity across parts is documented. · `TXN-4, TXN-1(codeonly)` — resolution: ⚪ info — `early-publish gone `:1349-1353`; residual commit window `:458-508``
- [x] **CAS-202** CAS is fully data-type agnostic — stores opaque files keyed by content hash; all MergeTree column types (incl. JSON/Variant/Dynamic/QBit/… · `datatype-agnosticism (AD1-6 etc.)` — resolution: ✅ fixed — ``Formats/CasPartManifestFormat.h:50-65`, `Formats/CasLayout.cpp:34-37`; zero `#include DataTypes/**` across CAS tree`
- [x] **CAS-203** All mainstream MergeTree part types supported — Wide/Compact (always Full storage), projections, patch parts, lightweight deletes, detach… · `part-support, ENG-1/3, M1/M2/M7/M8, BAK-2` — resolution: ⚪ info — ``PartPathParser.{h,cpp}`, `PartFolderAccess.cpp:73-80`, `DataPartsExchange.cpp:1388-`, `MergeTreeData.cpp:5167, 6744-6756``
- [x] **CAS-204** S3 SSE (SSE-S3/KMS/C) is fully supported and recommended — transparent, encrypts all objects at rest, preserves dedup. · `encryption` — resolution: 📐 by-design — ``ContentAddressed/Backend/CasObjectStorageBackend.cpp` uses `IObjectStorage` transparently; SSE is applied by the underlying `S3ObjectStorage``
- [x] **CAS-205** Fail-closed everywhere on the safety core — content addressing, two-phase precommit→promote, ack-floor-latched-before-cut, two-phase grad… · `jepsen, gc, interleaving, tla, concurrency §4, bc3` — resolution: ✅ fixed — `30+ specs under `docs/superpowers/models/` incl. new `CaErasureProof`, `CaDiskLifecycle`, `CaRelinkConfirmCore`, etc.`
- [x] **CAS-206** `GC REBUILD` `--force` is correctly narrow (bypasses only the healthy-state refusal; never the lease-conflict or missing-manifest refusal… · `GCR-6, GCR-7` — resolution: ⚪ info — ``CasGc.cpp:2549` (only healthy gate); refusals at `:2565, :2681, :2874` unconditional`
- [x] **CAS-207** Content-addressed keys make the FS cache ideal (no invalidation, cache-level dedup); one file = one blob = one payload ⇒ no cross-blob co… · `CACHE-1, BC5-1, BC5-6` — resolution: ⚪ info — ``DiskObjectStorage.cpp:876-922`; `test_cas_file_cache``
- [x] **CAS-208** TTL is data-driven, not mtime-driven → synthetic mtime does not affect TTL expiry/moves. · `BC6-4` — resolution: ⚪ info — `Negative-grep: no `TTL` consumer of `getLastModified` in CAS tree`
- [x] **CAS-209** Relink is data-safe under version skew (fail-closed publish-nothing → byte-fetch fallback; format bumps caught by the manifest's own comp… · `SKEW-2/3/4/7, RPL-1` — resolution: 📐 by-design — ``ContentAddressedExchange.h:140-146`; `Formats/CasFormat.cpp:64-70``
- [x] **CAS-210** Onto-CAS migration dedups on landing — a genuine storage-cost win. · `MIG-8` — resolution: ⚪ info — ``Pool/CasPartWriteTxn.cpp:178-212``
- [x] **CAS-211** Repudiation: provenance/`CasEvent` are self-asserted (forgeable by a pool-write adversary); blobs plaintext / content-equality observable… · `SEC-8, SEC-9` — resolution: 📐 by-design (Filimonov: bad actor with pool access is already doomed; provenance self-asserted / content-equality observable)
- [x] **CAS-212** Retired `FormatId` values rely on "pre-release, nothing deployed" — freeze the enum + retired-shape reservations at GA. · `UPG2` — resolution: ⚪ info — ``Formats/CasFormat.h:38-67` (comment-only retirement)`
- [x] **CAS-213** `manifestCleanupShard` hashes the qualified `ManifestId`; GC-artifact determinism is load-bearing and fail-closed. · `GC-shard-plan, BID-1` — resolution: ⚪ info — ``Gc/CasGcShardPlan.cpp:17-25``
- [x] **CAS-214** Instrumentation is extensive (66 ProfileEvents); `classifyCasNs` uses unanchored substring match (metric misattribution only, no correctn… · `INSTR-1, OBS-4` — resolution: ⚪ info — ``Common/ProfileEvents.cpp` (`grep -c '^\s*M(Cas' → 142`); `Backend/CasInstrumentedBackend.cpp:113-130``

---


---

## Mikhail Filimonov triage (Slack / 2026-07-17 update)

Source: Slack thread with Vitaliy Zakaznikov + Dmitry Titov, plus Mikhail's "Update since 9th of July" (formats / hash / lease / fetch pin). Dispositions below are **author intent**; the 2026-07-30 re-audit may still flag code paths.

### Closed by Filimonov (dismissed or fixed)

| CAS-id | Disposition | His words / update |
|---|---|---|
| CAS-001 | 🚫 not-a-bug | R1/X1: reader cannot keep reading after part removed in ClickHouse |
| CAS-004 | 📐 by-design | SEC-2/3: bucket credential = trust boundary |
| CAS-020 | ✅ fixed | W1 retry/`republishRef` path to address; OwnerTransition landed |
| CAS-026 / CAS-028 | ✅ fixed | 2026-07-17: protobuf/binary → self-describing text |
| CAS-030 | ✅ / 🟡 residual | 2026-07-17: token-stability lease (no cross-node wall clock); mount-wait tradeoff |
| CAS-033 | 📐 by-design | G-N1/X3: prefer fail-closed under GC uncertainty |
| CAS-037 | ✅ fixed | 2026-07-17: selectable hash recorded in PoolMeta |
| CAS-045 | 🚫 not CAS | RPL-2: general ReplicatedMergeTree ZK↔storage; RMT recovers |
| CAS-085 | ✅ fixed | R3 classed cosmetic; `allow_stale` retired |
| CAS-088 | 📐 by-design | G-N2: corrupt GC state ⇒ stop; rebuild recovers |
| CAS-089 | ❌ architectural limit | G-N4: huge single-round delta — not a bug |
| CAS-211 | 📐 by-design | Dedup/provenance side-channel: pool-write adversary already doomed |

### Acknowledged real (keep tracking)

| CAS-id | Disposition | His words |
|---|---|---|
| CAS-002 | 🔴 open | J1: will check deeper (TLA+ / SIGSTOP) |
| CAS-003 | 🔴 / 🟡 partial | SEC-1: "the real concern"; selectable hash landed, default CityHash128 remains |
| CAS-015 | 🔴 open | GCR-1: "Yep, this looks real"; GC REBUILD almost untested |
| CAS-016 | 🔴 open | LIFE-1 footgun not dismissed; versioning-bucket cost TBD |
| CAS-029 | 🔴 open | J2: narrow dual-mount; will check deeper |

### Minor / will-probably-fix

| CAS-id | Disposition | His words |
|---|---|---|
| CAS-035 | minor / think | W-N1: doubts on removal-retry idempotency |
| CAS-082 | will probably fix | W-N2/J5/X2: journal double-append |
| CAS-083 | will probably fix | W-N3: batch timeout/control |
| CAS-084 | minor | W-N4: MPU leftovers; GC cleans eventually |
| CAS-086 | minor/cosmetic | R4 with R2–R4 |
| CAS-110 | recheck / soft-dismiss | RPL-4 perf recheck; RPL-5: all stateless ran on CAS |


### Round 2 — Filimonov High-severity triage (2026-07-30)

| CAS-id | Disposition | His words (paraphrased) |
|---|---|---|
| CAS-003 | 🟡 / 📐 | Selectable hash solves weak-collision concern; **no** read-path re-hash ("CH does not slow down") |
| CAS-002 | 🚫 / 🟡 | Looks overstated; maybe recheck — **not a blocker** |
| CAS-005 | 📐 YAGNI | S3 durability + S3 hashing; do not re-verify on read |
| CAS-006 | ✅ fixed | Durable publish **no longer** under `DataPartsLock` |
| CAS-007 | 🚫 soft | Should be fine; tests quiet; glance someday — **not a blocker** |
| CAS-008 | ✅ fixed | Journals OK now (he fixed) |
| CAS-009 | ↗ out-of-scope | Needs attention later; not a blocker; model may be wrong |
| CAS-010 | 📐 YAGNI | Same as CAS-005 — trust S3; fuzz/re-verify costs perf |
| CAS-011 | ✅ / 📐 | Startup checks versioning off; versioned buckets unsupported |
| CAS-012 | ✅ fixed | Tested on real S3 + GCS (not Azure) |
| CAS-013 | ✅ fixed | SQL fsck landed; still slow (backlog) |
| CAS-014 | ✅ / recheck | Should be OK; re-verify later — **not a blocker** |
| CAS-015 | 🟡 partial | REBUILD poorly tested; lease should be correct now — **not a blocker** |
| CAS-016 | 📐 / docs | Lifecycle off like versioning; document bucket requirements; hard to detect w/o admin |
| CAS-017 | 📐 by-design | No Object Lock / WORM / retention / lifecycle / versioning on bucket |
| CAS-018 | 📐 / ❌ | Erase SLA not a disk contract; manual/auto GC (~5–10 min) |
| CAS-019 | 📐 / ❌ | Dedup non-erasure **is** CAS; will not "fix" |
| CAS-046 | ↗ out-of-scope | Encryption+CAS needs design; later |

## 🆕 New findings from the 2026-07-30 re-run

These are **new** issues surfaced against PR #2073 code that were **not** in the original 131-id catalog.
Full write-ups (complete sentences, anchors, discussion) live in the re-run gist: [`NEW-FINDINGS.md`](https://gist.github.com/alsugiliazova/7fb1441688ff428cc0e0a18918077c26#file-new-findings-md) and the per-audit `report-*.md` "New findings" sections.
Triage separately — do not reuse `CAS-###` ids from the original list.

- [ ] **NEW-AD1-1** (Low) `blob_hash_allow_new` semantics are dedup-fracturing by design.
- [ ] **NEW-AD1-2** (Info) `payload_digest` is hardcoded to CityHash128 regardless of pool algo.
- [ ] **NEW-AD1-3** (Info) CAS-025 fix incidentally lands here. `Formats/CasPartManifestFormat.cpp:293-301` now re-computes `payload_digest` on `decodePartManifest` and throws `CORRUPTED_DATA` on mismatch. Original AD1 audit predates this; belongs to `bc4-protobuf-decode` / integrity family.
- [ ] **NEW-ad2-1** (High for compliance) `isBucketVersioningEnabled()` unknown → mount proceeds.
- [ ] **NEW-ad2-2** (Med) versioning precondition is GCS-only; S3 versioning / object-lock / CRR / soft-delete not checked.
- [ ] **NEW-ad2-3** (Med) no post-`deleteExact` verification anywhere in the pipeline.
- [ ] **NEW-ad2-4** (Med) `SYSTEM CONTENT ADDRESSED FORGET` explicitly documents "erasure NOT verified".
- [ ] **NEW-ad2-5** (Low) `gc_snap_generations_to_keep` retention floor is uncapped by wall-clock.
- [ ] **NEW-ad3-1** (Low) SQL fsck cannot bound its runtime. `Cas::runFsck` accepts a `deadline` and a `partial_on_deadline` flag (`CasFsck.h:148-150`), but `runContentAddressedFsck` in `InterpreterSystemQuery.cpp:2524-2551` never plumbs the query-level `max_execution_time` / an explicit `DEADLINE '...'` clause into it. An operator running `SYSTEM CONTENT ADDRESSED FSCK` against a large / slow pool has no way to say "give me what you have after 10 min"; the scan runs to completion or throws `TIMEOUT_EXCEEDED` from `checkDeadline` (`CasFsck.cpp:43-48`).
- [ ] **NEW-ad3-2** (Low) `SYSTEM CONTENT ADDRESSED GC STOP` truthfully-but-misleadingly reports `is_leader`.
- [ ] **NEW-ad3-3** (Low) `SYSTEM CONTENT ADDRESSED FORGET` explicitly does not verify erasure.
- [ ] **NEW-ad3-4** (Info) `Nullable` peer-row columns in `content_addressed_mounts` are a good pattern to keep.
- [ ] **NEW-MIG-1** (Med) CAS-041 explicit sub-case: CAS → CAS same-pool MOVE does NOT relink; it byte-copies through streaming reads+writes.
- [ ] **NEW-MIG-2** (Med) CAS-210 confirmed: HEAD-first "dedup on landing" trusts backend object identity by NAME only; no body re-hash verify.
- [ ] **NEW-MIG-3** (Med) provenance envelope field is present but NOT driven by the operation kind; every fresh CAS write hardcodes `ProvenanceOp::Insert`.
- [ ] **NEW-MIG-4** (Low) off-CAS MOVE reads never re-verify blob against manifest/BLAKE hash — INT-1 exposure at migration boundary is symmetric with NEW-MIG-2.
- [ ] **NEW-ad5-1** (Med) the manifest write path is hard fail-closed only; no smoothing at all near the caps.
- [ ] **NEW-ad5-2** (Low) `enforceRefTableCacheBudget` LRU-evicts a namespace's cached state; a hot table churning enough to force re-hydration under memory pressure pays repeated recovery cost.
- [ ] **NEW-ad5-3** (Low) `RefLog` / `RefSnapshot` seal-decode ceilings are 64 MiB decompressed and enforced at decode, but the encode-side complete-table admission uses the same 64 MiB budget with only `kRefAdmissionSafetyMargin` headroom — essentially zero real slack.
- [ ] **NEW-AD6-1** (Low) GCS-versioning precondition treats "cannot verify" as fail-open by design, but the log level is `LOG_WARNING` inside `checkPoolPreconditions`, which many operators filter out at aggregation.
- [ ] **NEW-AD6-2** (Info) `Pool/CasPool.cpp:1327` bakes the "S3 strongly consistent since 2021" assumption in a comment, without a runtime capability check or a documented supported-backends matrix (RustFS is explicitly listed as unverified in the same comment).
- [ ] **NEW-ad7-1** (Info) `assertEOF` after `readStringBinary(sender_manifest_bytes)` will hard-fail any future v2-with-trailer sender talking to this exact v2 receiver.
- [ ] **NEW-ad7-2** (Info) Cookie-value gate happens BEFORE the pool-uuid re-check, but AFTER `ca_relink` cookie parse — an empty cookie value on the wire is silently treated as "no relink" rather than as a malformed offer.
- [ ] **NEW-ad7-3** (Info) `locate()` does not read the envelope's own `header_len` before ranging — soft coupling to pool_meta's `blob_header_len` invariant.
- [ ] **NEW-bc1-1** (Low) `decodeEnvelopeHeader` discards `object_size` but the payload extent still depends on `object_size >= h.header_len`, which is **not checked here**.
- [ ] **NEW-bc1-2** (Info) `getBlobViewPlan`'s `StoredObject(..., location.offset + location.length)` and `readBlobPayload`'s identical expression are duplicated.
- [ ] **NEW-BC2-7** (Low) `SCOPE_EXIT`-only cleanup covers throw but not a survivor if `stageBlobPartFile` succeeds and a later transaction step throws (inline-overflow branch).
- [ ] **NEW-BC2-8** (Low) envelope header pre-write is not covered by the streaming-size sanity check in S3 staging.
- [ ] **NEW-BC2-9** (Info) inline-overflow bounded but still holds full bytes in memory before spill.
- [ ] **NEW-bc4-protobuf-decode-1** (Info) `Backend/CasBackend.h:219` has a stale doc comment referring to the deleted `RunFileReader`.
- [ ] **NEW-bc4-protobuf-decode-2** (Info) `ShardCoverage::classification` is decoded as an unvalidated `uint8_t` (`Formats/CasFoldSealFormat.cpp:189`).
- [ ] **NEW-BC7-1** (Med) Asymmetric fix: replicated write paths use the `renameParts()` off-lock publish, but plain-MergeTree paths (`MergeTreeSink.cpp:379`, `MutatePlainMergeTreeTask.cpp:134`, `MergePlainMergeTreeTask.cpp:160`) still publish under `DataPartsLock`.
- [ ] **NEW-BC7-2** (Low) Belt-and-suspenders duplication: after `renameParts()` (`MergeTreeData.cpp:8986-8988`) runs the publish loop, the identical `commitTransaction()` loop inside `commit()` (`MergeTreeData.cpp:9008-9010`) is guarded only by `hasActiveTransaction()`.
- [ ] **NEW-codeonly-line-1** (Low) Non-cryptographic checksum still trusted on run objects, now under `CityHash128`-of-object-body — `Formats/CasRecordStreamFormat.cpp:210-219` (`sourceEdgeRunChecksum`).
- [ ] **NEW-codeonly-line-2** (Info) Envelope pad-zone now enforces "must be ASCII space up to '\n'" — `CasBlobEnvelopeFormat.cpp:230-248`.
- [ ] **NEW-codeonly-line-3** (Low) `PartWriteTxn::adoptEvidence` records the sender-supplied `entry.blob_size` in `deps[entry.ref]` and then verifies only that a blob exists in `promote`.
- [ ] **NEW-codeonly-line-4** (Info) `checkNamespace` is now also called on operator-supplied `server_root_id`-derived subpaths via a wide surface (`refsNamespacePrefix`, `manifestNamespacePrefix`, `namespaceFileKey`, `namespaceFilesPrefix`).
- [ ] **NEW-datatype-agnosticism-1** (Info) original audit's Layer 1 quote used `UInt128 blob_hash{}`.
- [ ] **NEW-datatype-agnosticism-2** (Info) original audit's edge-case table noted mutable per-part files (`uuid.txt`/`txn_version.txt`/`metadata_version.txt`) were kept out of the content manifest.
- [ ] **NEW-datatype-agnosticism-3** (Info) the only place CAS inspects a file's name to alter behavior is `Cas::partFileMustStayBlob` (`ContentAddressedTransaction.cpp:65-73`) which handles `primary.idx`/`.bin`/`.mrk*`/`.cmrk*`.
- [ ] **NEW-jepsen-1** (Med — observability/operability) Post-write fence-loss surfaces as `Unresolved`, never `Committed`; but the durable object may exist and be visible to other mounts.
- [ ] **NEW-jepsen-2** (Low — soft-vs-hard fence) `fenceGeneration` admission covers the durable-effect blob finalize path only for `ContentAddressedTransaction::writeFile`; the ref-append lane relies on `fence_ok_fn` (boolean) rather than a captured generation token.
- [ ] **NEW-jepsen-3** (Med-High) X1/R1 reader pin gap surface is unchanged; the refactor added no reader-side coupling to GC's ack floor.
- [ ] **NEW-read-1** (Med, liveness) `readManifestShared` HEAD-GET race window amplifies dangle.
- [ ] **NEW-read-2** (Low, coverage) Retained-view age policy uses wall-clock `now_ms_fn()` (`PartFolderAccess.cpp:203`) subtracted from `cached->validatedAtMs()`.
- [ ] **NEW-read-3** (Info) `CachedPartFolderAccess::buildView` single-flight drops leader exceptions onto every follower (`l.301: promise.set_exception`).
- [ ] **NEW-security-1** (Med — default-hardening) `BlobHashAlgo` default is `CityHash128`.
- [ ] **NEW-security-2** (Low — clean-shutdown) `Xxh3128BlobHashingWriteBuffer::finalizeImpl` is not overridden; `getHashHex` calls `next()` but skips `finalize()`, and the class also lacks a `cancelImpl`.
- [ ] **NEW-security-3** (Low — defense in depth) `_pool_meta` / `_manifests` / `_files` reserved-segment gate does not include the newer reserved prefixes in the `roots/` and `blobs/` trees.
- [ ] **NEW-security-4** (Low) `mountpointObjectKey` and `checkNamespace` accept single-character segments `.` and `..` (sub-finding of CAS-074, called out separately for the mountpoint path).
- [ ] **NEW-TCF-1** (Med) no GCS-backed integration test despite `utils/ca-soak/docker-compose-gcs.yml` being present.
- [ ] **NEW-TCF-2** (Low) `ca-soak/scenarios/` is model/checker-oriented but has no explicit **MOVE / RESTORE / quorum** cards even though it has multi-replica infra (`docker-compose-10replicas.yml`).
- [ ] **NEW-TCF-3** (Info) `gtest_cas_ref_decode_bounds.cpp` exists and is a natural seed corpus for a `cas_ref_decode_fuzzer`.
- [ ] **NEW-tier2-1** (Low, cache/observability) page memory cache key prefix disk-scopes CAS blob dedup.
- [ ] **NEW-tier2-2** (Low, system-tables gap) no CAS view of pool-level counters despite `CasFsck` numbers.
- [ ] **NEW-tier2-3** (Low, TTL/tiering) no move-path hook to short-circuit CAS→CAS same-pool moves.
- [ ] **NEW-tier3-1** (Low, feature-gap-with-safety-note) `moveFile` on committed non-part files throws `LOGICAL_ERROR` when the source is not staged in this transaction.
- [ ] **NEW-tier3-2** (Low, robustness) cross-namespace `moveDirectory` (RENAME TABLE) is documented as best-effort, non-atomic, idempotent-on-retry but has no in-call compensation.
- [ ] **NEW-tier3-3** (Info) Same-pool same-disk `moveDirectory` for part-dirs is a pure metadata `republishRef` (`ContentAddressedTransaction.cpp:1370`), i.e.
- [ ] **NEW-tier4-1** (Low, test-coverage) FETCH-to-detached relink correctness has code but no dedicated integration test.
- [ ] **NEW-tier4-2** (Low, test-coverage) RENAME TABLE / cross-engine table move on CAS is best-effort non-atomic and the "SPLIT across namespaces" recovery path is idempotent by construction, but no integration test injects a fault between the `republishRef` loop and `dropNamespace` and asserts idempotent re-drive.
- [ ] **NEW-tier4-3** (Low, observability) a `CasBlobAdoptTrusted` ProfileEvent (`src/Common/ProfileEvents.cpp:900`) partially closes the original OBS-3 gap (relink hit-rate is measurable at the "adoption" level), but there is still no counter distinguishing a **relink fetch** from a **byte fetch** in the replication log (`system.replicated_fetches` bytes-transferred remains the only signal).
- [ ] **NEW-upgrade-compat-1** (Med) `changePoints()` history stayed frozen at `{{1,1}}` across two `G_BUILD` bumps.
- [ ] **NEW-upgrade-compat-2** (Low) backward pool-meta floor is a hard `< 3` gate, no operator override.
- [ ] **NEW-upgrade-compat-3** (Low) tolerant-key silent-drop has no per-generation "critical additive" mechanism.
- [ ] **NEW-upgrade-compat-4** (Info) pool-meta admission ratchets `min_reader_generation` irreversibly on any new-algo union.
- [ ] **NEW-upgrade-compat-5** (Info) no LE-only build assertion. No occurrence of `std::endian::native` / `__BYTE_ORDER__` / `static_assert` guarding LE-only in `MetadataStorages/ContentAddressed/**`. Explicit-BE wire codec covers CAS's own bytes, but the underlying `CityHash128` implementation is not audited BE-safe. Cheap one-liner recommendation.**
- [ ] **NEW-write-1** (Low, LEAK/OBSERV) `CaContentWriteBuffer::finalizeImpl` sets `temp_ownership_transferred = true` (line 1845) even after `on_finalized` throws in the tail of that lambda, because the flag is set after the callback.
- [ ] **NEW-write-2** (Low, CORRECTNESS/COMPAT) `CaContentWriteBuffer::finalizeImpl` reports the payload size via `count()` (line 1822), which is the byte count of what THIS buffer forwarded to `hashing`.
- [ ] **NEW-write-3** (Low, LIVENESS/PERF) `ContentAddressedTransaction::moveDirectory`'s RENAME-TABLE branch (`:1231–1249`) does `for (const auto & [ref, _] : store->listRefs(from_ns))` and calls `republishRef(...)` per ref, then `putNamespaceFile` per verbatim file, then `dropNamespace(from_ns)`.
---

<details>
<summary>Genuine data-loss / correctness paths (the short list to look at first)</summary>

`CAS-001` (reader pin), `CAS-002` (writer_epoch fencing — single highest-leverage fix), `CAS-015`
(GC REBUILD mount-lease interlock), `CAS-016`/`CAS-017` (lifecycle expiration / Object Lock —
config-triggered), and the integrity delegation `CAS-005`+`CAS-003`.
Everything else biases to a reclaimable **leak**, a **liveness/operability** cliff, or an **unverified edge**.

</details>

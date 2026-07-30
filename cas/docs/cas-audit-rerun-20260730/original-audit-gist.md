# CAS (content_addressed MergeTree) audit reports — 39 audit files + consolidated summary

- Owner: vzakaznikov
- Created: 2026-07-09T14:14:30Z
- Public: no
- Comments: 0
- Forks: 0

## audit-summary.md

Language: Markdown

# CAS — Consolidated Audit Summary (all audits, deduplicated)

Single master table for every finding across the 39 CAS audit files. Each distinct issue gets **one
unique `CAS-###` id**; the **Merged from** column lists the original per-audit ids that describe the same
underlying issue (many findings recurred under different names across audits). Severity is the highest
assigned by any source audit.

**Source audits (39):** write / read / gc / interleaving / jepsen / security / concurrency /
crash-consistency / upgrade-compat / idisk-contract / performance / test-coverage-fuzzing / tla-fidelity /
mergetree-part-support / alter-merge-mutation / datatype-agnosticism / encryption / tier1–4 /
ad1–ad7 / bc1–bc7 / gc-rebuild-feature / codeonly-line / coverage-map.

Legend — **Class:** DATA-LOSS · LEAK (over-count) · LIVENESS · CONCURRENCY · INTEGRITY · SECURITY ·
DECODE/DoS · COMPAT · FEATURE-GAP · PERF/SCALE · OBSERV/DAY2 · COMPLIANCE · CONFIG · TEST-GAP · CORRECTNESS.
Most correctness findings are **fail-closed / over-count-safe**; the few genuine data-loss paths are flagged.

---

## 1. High severity

| ID | Title | Class | Merged from |
|----|-------|-------|-------------|
| CAS-001 | **Reader holds no pin across the deferred, unpinned blob GET** → a `dropRef`+GC condemn→delete can remove a committed blob mid-query for ref-less / cross-node readers (`NoSuchKey`). The one reachable cross-protocol data-loss path (fail-loud, not wrong results). | DATA-LOSS | R1, X1, MVCC-1, M5, TIER-3, ENG-2, Jepsen "missing read", TLA-F2, T-G1, F-N2 (amplifier) |
| CAS-002 | **Shard `casPut` fenced by content token, not `writer_epoch`** → pause/TOCTOU/clone/clock-skew opens a dual-writer window (split-brain / zombie write). `mayMutate()` checked at flush-top, CAS committed later on ETag only. | SECURITY / CORRECTNESS | J1, SEC-7(J1), TLA-F1, M6, C-U3, RPL-3, T-G2 |
| CAS-003 | **Non-cryptographic content hash (CityHash128) + reads never re-verify** → collision-based blob poisoning across a shared pool via pool-global dedup; wrong bytes served silently. | SECURITY / INTEGRITY | SEC-1, INT-2, AD1-7 |
| CAS-004 | **No intra-pool authorization; identities self-asserted** → bucket credential is the whole perimeter; a pool-write peer can forge mounts, tamper `gc/state`, poison/delete anything. | SECURITY | SEC-3 |
| CAS-005 | **Blob payload never re-hashed against `logical_hash` on the normal read path** → silent S3 bit-rot / truncation undetected by CAS; integrity delegated entirely to MergeTree checksums. | INTEGRITY | INT-1, BC2-1(read side), BOOT-3, MIG-6, INT-4(related) |
| CAS-006 | **CAS durable publish runs under `DataPartsLock`** (blob PUTs + precommit + promote + ref CAS, each with retries) → table-wide writer/DDL stall under S3 latency/throttling. | LIVENESS / PERF | BC7-1, BC7-2, BC7-3, BC7-4 |
| CAS-007 | **UniqueKey / upsert MergeTree: DeleteBitmap + SSTIndex hot-rewrite** — delete-bitmap is not in the mutable-per-part set, so every `replaceFile` triggers a whole-part republish; correctness + churn untested, misfit for CAS. | FEATURE-GAP / PERF | G1 |
| CAS-008 | **Untrimmed root-shard journal under churn hits the 64 MiB hard limit → writes rejected** until GC folds/trims. Couples write availability to GC progress. | LIVENESS / SCALE | RES-1, M-C2/M-C3(referenced) |
| CAS-009 | **Rolling upgrade across a format-generation bump breaks old nodes** — `compatibility_version` always stamped at `G_BUILD` (write-down-to-floor unimplemented); old nodes fail-closed on new shared objects. Latent while `G_BUILD=1`. | COMPAT | UPG1 |
| CAS-010 | **No coverage-guided fuzzing of any CAS decoder** despite untrusted shared-pool bytes (envelope, run-file, manifest, root-shard, gc-formats, pool-meta). | TEST-GAP / DoS | FZ1 |
| CAS-011 | **Bucket versioning / GCS soft-delete silently breaks GC reclaim**; guarded only when the versioning API is queryable, else fails **open** (mounts, leaks forever). S3-bucket-versioning not checked at all. | OBSERV / LEAK | OSC-2, OSB-3, LIFE-5 |
| CAS-012 | **Native conditional-write path not end-to-end tested on real S3/GCS** (only RustFS + emulation) — the single most safety-critical untested seam (412/NoSuchKey→PreconditionFailed mapping). | TEST-GAP | OSC-1, OSB-2 |
| CAS-013 | **`fsck` (reachability / dangling / physical-vs-logical) is not operator-accessible** via SQL — the most valuable health diagnostic is internal/test-only. | OBSERV/DAY2 | DR-1 |
| CAS-014 | **No GC-liveness / reclaim-backlog / physical-bytes metric** — the most common silent failure ("GC stopped reclaiming") is invisible without log-diving or a full scan. | OBSERV/DAY2 | DR-2, OBS-1, OBS-2, SYS-1(ties) |
| CAS-015 | **`GC REBUILD` has no mount-lease interlock** → run against a live pool, its non-atomic universe/blob scans can bless a baseline missing a concurrent writer's edges → later rounds condemn/delete live blobs. Only guard is in-process `isReadOnly()`. | DATA-LOSS | GCR-1 |
| CAS-016 | **Lifecycle expiration rule deletes live blobs** (age-based rules hit the oldest, most-shared blobs) → dangling refs / data loss. Unguarded. | DATA-LOSS / CONFIG | LIFE-1 |
| CAS-017 | **Object Lock / WORM / retention breaks CAS entirely** — mutable root-shards and `gc/state` cannot be overwritten → all writes + GC fail. Unguarded. | CONFIG / LIVENESS | LIFE-2 |
| CAS-018 | **No bounded delete→physical-erase SLA** — reclaim is GC-deferred and stallable indefinitely; cannot promise GDPR/CCPA erasure deadlines from CAS mechanics. | COMPLIANCE | ERASE-1 |
| CAS-019 | **Dedup means one owner's delete may erase nothing** while any other ref shares the byte-identical blob; no per-subject "shred everywhere" primitive. | COMPLIANCE | ERASE-2 |
| CAS-046 | **`DiskEncrypted` random-IV ciphertext defeats content-addressed dedup** — every encrypted file becomes a unique blob; CAS's whole value nullified. Use S3 SSE instead. | FEATURE-GAP | E-1 |

---

## 2. Medium severity

| ID | Title | Class | Merged from |
|----|-------|-------|-------------|
| CAS-020 | **`promote`-overwrite leaks the prior committed manifest** (unconditional `refs[R]=…`); reachable via RENAME / lost-ACK replay. The only non-reclaimed orphan class. | LEAK | W1, X2, Jepsen overwritten-write/failed-removal, crash-audit W1 |
| CAS-021 | **Multi-part `commit()` is not atomic** → power-loss / compounded-failure mid-loop leaves a durable partial commit; best-effort rollback is not crash-durable and its failure is **silent**. | CORRECTNESS | DUR1, C-U5, BC3-1, BC3-6, M4, TXN-2(tier3) |
| CAS-022 | **RENAME TABLE (`moveDirectory`) is non-atomic multi-op** → crash mid-way leaves a table split across namespaces; re-drivable but no durable move-journal / auto-re-drive. | CORRECTNESS | DUR2, C-U1, TXN-2(codeonly), G10 |
| CAS-023 | **Teardown UAF / `std::terminate` race** — `scheduleRemount` ignores `remount_stop`; keeper stopped after remount join can re-arm a thread on a destroying `Store`. | CONCURRENCY | STORE-C1, C1, T-G6 |
| CAS-024 | **`locate()` uses fixed `PoolMeta.blob_header_len`, not the blob's own envelope `header_len`** → wrong payload offset under config drift / mixed-version writers → silent misread. | CORRECTNESS | STORE-2 |
| CAS-025 | **`PartManifest.payload_digest` written but never re-verified on decode/read** → a bit-flip in a `blob_hash`/`blob_size` is undetected. | INTEGRITY | MC-1 |
| CAS-026 | **Protobuf `ParseFromArray` with unchecked `static_cast ` and no size cap** → OOM / negative-size on a corrupt/planted oversized object; no decode-time size guard before GET (amplified by O(object) `refs`/`journal`/`mutable_files` decode). | DECODE/DoS | RSC-1, BC4-1, BC4-3, BC4-4, SEC-4 |
| CAS-027 | **Additive protobuf fields dropped on re-encode by an older build** → silent mixed-version control-plane data loss. | COMPAT / DATA-LOSS | RSC-2, BC4-2 |
| CAS-028 | **`RunFileReader::next()` parses record `klen`/`plen` with unchecked `operator[]`/`substr`** → OOB heap read / non-`CORRUPTED_DATA` throw on a CRC-valid malformed block. Reachable from manifest decode, GC fold, fsck. | DECODE/DoS | RF-1 |
| CAS-029 | **VM-clone / snapshot split brain** — two live servers share one `server_uuid`; dual mount bounded only by renew period. | CORRECTNESS | J2, TLA-F4 |
| CAS-030 | **Wall-clock mount-lease expiry vs boot-clock local fence** → clock skew → premature reclaim / false unavailability (token-guarded, no corruption). NTP-spoof amplifiable. | CORRECTNESS / SECURITY | J3, SR-1, SEC-7(J3), TLA-F3 |
| CAS-031 | **Relink / rename receiver trusts sender-supplied `entry.blob_size`/`path`** (`payload_digest` ignored) → only blob *presence* revalidated → wrong-length reads (chains CAS-005/CAS-024). | INTEGRITY | MW-1 |
| CAS-032 | **Zombie GC leader's unconditional `pulseHeartbeat` clobbers `gc/hb.owner`** (defeats B160) → a follower can steal the lease from a live long-round leader (non-corrupting churn). | LIVENESS | SCHED-1, SCHED-2 |
| CAS-033 | **Persistent shard clamp → pool-wide `suppress_destructive`** halts all reclamation with no self-heal (safety-preserving). | LIVENESS | G-N1, X3, TLA-F5 |
| CAS-034 | **Coalesced shard read has no deadline** → a hung leader GET blocks all coalesced followers (reader convoy). | LIVENESS | F-N1 |
| CAS-035 | **Presence-asserting closures misreport a lost-ACK-succeeded write as failure** (e.g. `dropRef` re-reads its own committed drop → `FILE_DOESNT_EXIST`). | CORRECTNESS | W-N1 |
| CAS-036 | **`blob_header_len` floor (96, 8-aligned) is below the mandatory provenance-TLV need (~128 B)** → configuring 96–120 bricks all blob writes (`BAD_ARGUMENTS`). | CONFIG | BUILD-2 |
| CAS-037 | **Content-hash algorithm is an unversioned, unpinned pool contract** (not recorded in `PoolMeta`); a future CityHash/algorithm change silently forks dedup and breaks relink. | INTEGRITY / COMPAT | BUILD-1, AD1-3 |
| CAS-038 | **Scratch temp file un-fsynced and never verified against its key between hash and upload** → local scratch corruption → silent wrong-bytes blob (pairs with CAS-005). | INTEGRITY | BC2-1, BC2-2 |
| CAS-039 | **Envelope size-consistency check bypassable via `logical_size` uint64 overflow wrap** (`header_len + logical_size == object_size`). | DECODE | ENV-1, BC1-1 |
| CAS-040 | **`system.parts.bytes_on_disk` is logical, over-reports physical N× under dedup**; no physical/dedup-ratio system view (numbers exist only in fsck). | OBSERV | SYS-1 |
| CAS-041 | **Cross-disk `MOVE PARTITION TO DISK/VOLUME` is unverified and byte-copies** (no relink even CAS→CAS same-pool). | FEATURE-GAP / PERF | B-2, TIER-1, MIG-2, G3 |
| CAS-042 | **BACKUP is Atomic-DB-only** (Ordinary/non-UUID DBs rejected on the temp-hardlink path); incremental-backup dedup + RESTORE round-trip untested. | FEATURE-GAP | B-1, BAK-1, BAK-3, MIG-7 |
| CAS-043 | **DROP/TRUNCATE/TTL-move frees zero bytes synchronously** (GC-deferred; leaks forever if GC disabled/read-only); TTL move off-CAS double-bills until reclaim. | LEAK / OBSERV | LC-1, LC-4, TIER-2, CFG-4, MIG-3 |
| CAS-044 | **Crash between catalog drop and `dropNamespace` → permanently orphaned namespace** (live refs, no owning table); no catalog-vs-pool reconcile; surfaces as phantom parts at startup. | LEAK | LC-2, ERASE-6, DR-3, BOOT-2 |
| CAS-045 | **ZK part-set vs CAS ref can diverge on partial commit** (ZK-has/CAS-missing → broken part; CAS-has/ZK-missing → invisible live-ref leak). | CORRECTNESS / LEAK | RPL-2 |
| CAS-047 | **Two "size" semantics for a file** (payload-only from `getStorageObjects` vs envelope+payload plan); correctness depends on all reads going through `prepareRead`+FileView, else envelope-as-data. | CORRECTNESS | BC5-2, MW-2 |
| CAS-048 | **`getLastModified` = ref publish time (resets on relink) / epoch(0) for verbatim / throws on unresolved** → cross-replica divergence, part-check timing skew, misleading `modification_time`. TTL unaffected. | CORRECTNESS | BC6-1, BC6-2, C-U2 |
| CAS-049 | **Decode caches wholesale-clear at 16384 entries** (no LRU) → thundering-herd re-HEAD/GET/decode cliff at scale / high multi-tenancy. | PERF/SCALE | RES-3 |
| CAS-050 | **`GC REBUILD` zero-condemn scan is O(all blobs) with a synchronous HEAD each, unbudgeted** → millions of round-trips exactly at DR time. | PERF/SCALE | GCR-2, GCR-4 |
| CAS-051 | **Cross-region replication** accumulates an un-GC'd shadow bucket; failover onto it is token/ETag-incoherent and unvalidated. | CORRECTNESS / LEAK | LIFE-4 |
| CAS-052 | **Archive-tier transition (Glacier/IA/Deep-Archive)** leaves cold blobs present-but-unreadable; read path has no restore-and-retry → query failures. | FEATURE-GAP | LIFE-3 |
| CAS-053 | **Throttle/429/SlowDown storms compound with CAS-conflict retries** (no CAS-level adaptive backoff) → retry storm / latency collapse. | LIVENESS | ERR-1 |
| CAS-054 | **Relink cookie *value* not validated (only presence); pool-uuid/metadata_version framing is an implicit wire contract** → a future v2 framing change mis-read by a v1 receiver. Gate the exact cookie value now. | COMPAT | SKEW-1, SKEW-5, SKEW-6 |
| CAS-055 | **Non-MergeTree engines / `tmp` disks / SSD-cache dictionaries / Distributed spool are ungated on a CAS disk** → runtime `NOT_IMPLEMENTED`/misroute mid-write; fail-closed at DDL/config recommended. | CONFIG / FEATURE-GAP | G4, G5, G6, G8 |
| CAS-056 | **`root_shards` is a fixed, pool-wide, create-time constant** — one-shot write-parallelism decision, no live reshard; same-shard writes single-object-CAS-bound. | SCALE / CONFIG | P3, P2, CFG-1, RES-2 |
| CAS-057 | **GC discovery LIST is O(namespaces × shards)** — round cost scales with pool size, not churn; no parallel discovery. | PERF/SCALE | P4, RES-5 |
| CAS-058 | **Read-your-writes / strongly-consistent LIST is a hard, per-backend assumption** (startup part discovery, drop enumeration, rebuild) — S3 ok, others unconfirmed. | COMPAT | BOOT-1, OSC-4, GCR-5 |
| CAS-059 | **MergeTree experimental transactions (MVCC `txn_version`) mechanically supported but untested on CAS**; multi-part visibility inherits partial-commit (CAS-021). | TEST-GAP / FEATURE-GAP | TXN-1(tier3), TXN-2(tier3) |
| CAS-060 | **Failed-build debris reclaimed only by sweeps**; failure storms (OOM/disk-full) accumulate debris faster than sweeps clear → transient bloat. | LEAK / LIVENESS | ERR-2 |
| CAS-061 | **Full-text (GIN/Text) & vector-similarity index build/merge/read on CAS untested** (large multi-file structures, inline-cap/stream behavior, dedup). | FEATURE-GAP | G2 |
| CAS-062 | **No lease/owner introspection or documented force-release/recovery runbook** (stuck lease on dead server, reused `server_root_id`). | OBSERV/DAY2 | DR-4, CFG-2 |
| CAS-063 | **No `PoolMeta` / control-plane backup-restore story** — a corrupt `PoolMeta` fails the mount closed with no runbook. | OBSERV/DAY2 | DR-5 |
| CAS-064 | **`server_root_id` uniqueness is operator-owned**; collision → mount-lease outage, reuse → inherits stale owner/epoch. | CONFIG | CFG-2 |
| CAS-065 | **Azure / non-S3 object stores effectively unsupported for Native CAS** (`conditionalOpsUseGenerationTokens`/versioning only in S3ObjectStorage) → falls to unsafe Emulated. | COMPAT | OSC-3 |
| CAS-066 | **`createOrValidate` silently ignores passed `root_shards`/`blob_header_len` when a pool exists** (validates then uses persisted values, no operator warning). | CONFIG | PM-1 |
| CAS-067 | **No read-side blob cache/pin** — cold reads re-GET each blob; warm-read cost depends entirely on the two decode caches. | PERF | P1 |
| CAS-068 | **FS-cache-over-CAS caches whole-blob (envelope-inclusive) ranges; FileView applied above** — correct but envelope-offset alignment under partial-hit is untested. | TEST-GAP | CACHE-2 |
| CAS-069 | **Migration onto/off CAS is always a full data rewrite** (no in-place conversion), transiently double-bills, and a CAS volume **narrows the whole table's ALTER surface**; no bulk relink/warm-start import. | FEATURE-GAP / PERF | MIG-1, MIG-3, MIG-4, MIG-5 |
| CAS-070 | **FREEZE shadow refs, detached refs, and `gc/snap` retention silently retain deleted data/metadata** — erasure must sweep every FREEZE/detached ref. | COMPLIANCE | ERASE-3, ERASE-4 |
| CAS-071 | **No crypto-shred; physical erasure depends on backend DELETE semantics** (versioning/soft-delete/CRR may retain copies CAS never removes). | COMPLIANCE | ERASE-5 |
| CAS-093 | **`fsck` detects Dangling (=already-lost) but never repairs; no forced cadence** — non-replicated tables: dangling = permanent part loss. | INTEGRITY / DAY2 | INT-3 |
| CAS-113 | **`DiskEncrypted`-over-CAS leaves control-plane metadata plaintext, read-path composition untested/unguarded, cross-replica dedup lost.** | SECURITY / TEST-GAP | E-2, E-3, E-4 |

---

## 3. Low / hardening

| ID | Title | Class | Merged from |
|----|-------|-------|-------------|
| CAS-072 | Post-CAS T0 hand-off reclaim: a crash between the round CAS and the hand-off permanently strands a `gc/gen/ /` prefix (fsck-only, no auto-reclaim). | LEAK | GC-1 |
| CAS-073 | `looksLikePartDir` false-positives on non-Atomic table/dir names ending in three numeric groups → misroutes table files as part files. | CORRECTNESS | PPP-1, B-4 |
| CAS-074 | `checkNamespace` / `mountpointObjectKey` don't reject `.`/`..` → path-traversal risk on a filesystem/normalizing backend (safe only for literal-key object stores). | SECURITY | LAY-1, LAY-2, SEC-5 |
| CAS-075 | Envelope `header_hash` (CityHash64) covers only the 94-B core, not TLVs; "critical extension" enforcement relies on writer honesty. | INTEGRITY | ENV-2, ENV-3 |
| CAS-076 | `FormatId::Roster` defined but `magicFor(Roster)` throws → dead/incomplete path. | CORRECTNESS | FMT-1 |
| CAS-077 | `decodeFoldSeal` casts `folded_token_type`/`classification` enums without validation (unlike sibling decoders). | DECODE | GS-1 |
| CAS-078 | Concurrent probes of a shared `probe_prefix` can spuriously read `NOT_IMPLEMENTED` (low: `Store::open` uses a unique prefix). | CORRECTNESS | PROBE-1 |
| CAS-079 | Non-atomic HEAD-then-GET can pair an old token with new bytes / wrong ranged size for a mutable object (masked by CAS write patterns). | CORRECTNESS | OSB-1 |
| CAS-080 | `allocateWriterEpoch` has no overflow guard; a fresh mount pins the GC heartbeat floor to 0 until first renewal (transient GC stall on start). | CORRECTNESS | SR-2, SR-3 |
| CAS-081 | `abandon` retires `build_seq` before appending the precommit-removal event (fragile ordering; safe only because in-degree is a set). | CORRECTNESS | W2 |
| CAS-082 | Lost-ACK replay double-appends journal events (set-idempotent → journal bloat only). | LEAK | W-N2, J5 |
| CAS-083 | Flat-combining leader convoy + batch-wide failure amplification under S3 stall (latency, not correctness). | LIVENESS | W-N3 |
| CAS-084 | Orphan multipart uploads / ownerless manifest bodies on interrupt — reclaimed by S3 lifecycle + watermark sweep; CAS neither aborts nor reports MPUs. | LEAK / DAY2 | W-N4, ERR-3, DR-6 |
| CAS-085 | `allow_stale` decode-TTL ↔ GC condemn→delete latency coupling is a convention, not an enforced invariant. | CORRECTNESS | R3 |
| CAS-086 | `readManifest` HEAD+GET is not coalesced and absence not negatively cached → HEAD+GET storm under throttling. | PERF | R4, F-N4 |
| CAS-087 | Force-fresh read isn't fresh on eventually-consistent backends (backend-conditional stale serve/retry). | COMPAT | F-N3 |
| CAS-088 | Lost/corrupt GC-internal artifacts wedge GC until manual `GC REBUILD` (by-design fail-stop-then-recover). | LIVENESS | G-N2 |
| CAS-089 | Regular-round mass-drop delta is a non-streaming in-memory point (rebuild is batched; regular round isn't). | PERF/SCALE | G-N4 |
| CAS-090 | `mount_keeper` `unique_ptr` reassigned without synchronization vs `renewWatermarkOnce` (latent UAF; safe only by unenforced config mutual-exclusion). | CONCURRENCY | C2 |
| CAS-091 | `event_sink_` published after keeper thread start (`std::function` data race; timing-masked). | CONCURRENCY | C3 |
| CAS-092 | `shard_write_seq` never pruned on `dropNamespace` → unbounded growth by lifetime (namespace, shard) pairs. | LEAK | C4, RES-4 |
| CAS-094 | No proactive scrubbing of cold blobs — bit-rot accumulates until a query/CHECK TABLE touches it (one rotted shared blob damages every deduped ref). | INTEGRITY | INT-4 |
| CAS-095 | Fragile read-window arithmetic: `resizeWorkingBuffer` size_t-underflow-then-signed-cast; `SEEK_CUR` negative underflow caught only downstream; plan trusts manifest offset/length vs real object size. | DECODE | BC1-2, BC1-3, BC1-4 |
| CAS-096 | Scratch-FS-full/error fails the insert late (no pre-flight check; undocumented sizing); temp-file uniqueness relies on a random string (add PID/counter). | CORRECTNESS | BC2-3, BC2-4, BC2-6 |
| CAS-097 | `updateRefPayload` one-shots are intentionally not rolled back → "commit failed" ≠ "no durable effect"; already-published refs transiently observable during the rollback window. | CORRECTNESS | BC3-2, BC3-3 |
| CAS-098 | Wide-part read path branches: inline vs blob dual path, right-mark mid-stream narrowing, projection nested-key routing — all correct, each needs explicit coverage. | TEST-GAP | BC5-3, BC5-4, BC5-5 |
| CAS-099 | `setLastModified` is a no-op ("touch to refresh age" silently fails); `clearOldTemporaryDirectories` inert on CAS (GC is the real tmp reaper). | CORRECTNESS | BC6-3, BC6-5 |
| CAS-100 | Manifest soft-limit backpressure (≤1 s, per-flush) delays but can't prevent the hard-limit wedge; no per-tenant quota in a shared pool (fairness/DoS). | SCALE | RES-6, RES-7 |
| CAS-101 | System-table quirks: empty `remote_path` for in-manifest files, many-to-one remote paths, placeholder free space, unverified mutations/part_log/replicated_fetches fields. | OBSERV | SYS-2, SYS-3, SYS-4, SYS-5 |
| CAS-102 | Relink vs byte-fetch indistinguishable in `system.replicated_fetches`; cache observability by blob key not part path (join needed). | OBSERV | OBS-3, CACHE-3 |
| CAS-103 | Move-vs-concurrent-GC untested (R1/X1 class); `move_factor` free-space heuristics inert on CAS source. | TEST-GAP | TIER-3, TIER-4 |
| CAS-104 | Non-replicated dedup-log durability rides mutable-file commit; crash mid-update → bounded duplicate part (CAS content-dedups anyway). | CORRECTNESS | DEDUP-2 |
| CAS-105 | RESTORE round-trip + Packed storage-type parts (arriving via RESTORE/ATTACH) untested/unsupported on CAS. | TEST-GAP / FEATURE-GAP | BAK-4, B-3, G12 |
| CAS-106 | GC cadence/retention knobs (`gc_interval`, `gc_snap_generations_to_keep`, sweep budgets) directly gate reclaim latency (LC-1). | CONFIG | CFG-3 |
| CAS-107 | Big-endian would silently fork dedup (no explicit LE guard); manifest bytes / ManifestId not version-stable across CH versions (harmless). | COMPAT | AD1-2, AD1-5 |
| CAS-108 | `GC REBUILD` DoS/amplification + `FORCE` blast radius (SYSTEM-gated); interrupted rebuild leaks un-swept `gc/gen` artifacts and ratchets the generation. | DAY2 / LEAK | SEC-6, GCR-3 |
| CAS-109 | System log tables on CAS produce a tiny-part storm (manifest/ref churn + inflated logical bytes); tooling (`clickhouse-disks`), `EXCHANGE TABLES`, and disk-layering (cache/web over CAS) untested. | PERF / TEST-GAP | G7, G9, G10, G11 |
| CAS-110 | FETCH-to-detached never relinks (full byte transfer even same-pool); quorum/SYNC REPLICA/cloneReplica correct-by-composition but untested. | PERF / TEST-GAP | B-5, RPL-4, RPL-5 |
| CAS-111 | Committed single-file `unlinkFile` is a deliberate fail-open no-op — becomes a correctness bug if a future path surgically deletes one committed file (ties CAS-007). | CORRECTNESS | C-U4, TXN-3(codeonly), B-6 |
| CAS-112 | `chmod` / `generateObjectKeyForPath` throw `NOT_IMPLEMENTED` (latent; no MergeTree path calls them today). | FEATURE-GAP | C-U6, C-U7 |
| CAS-114 | Storage-class cost/latency skew from tiering; CAS sets no storage class (bucket default applies). | CONFIG | LIFE-6, LIFE-7 |
| CAS-115 | **Manifest duplicate-path detection is adjacent-only** (`prev_path` check, valid only because encode sorts) → a corrupt/unsorted embedded RunFile carrying **non-adjacent** duplicate paths passes decode undetected. | DECODE / INTEGRITY | MC-2 |
| CAS-116 | **Per-file `lookupPath`/`listDirectory` are linear scans over `manifest.entries` → O(entries²) to read all files of a wide part** (thousands of column files ⇒ millions of comparisons). Cheap fix: index entries by path in the decoded `PartManifest`. | PERF/SCALE | STORE-3 |
| CAS-117 | **`FINAL` / parallel-replica reads / lightweight-update patch-apply-on-read untested for correctness-under-concurrent-merge** — all issue more concurrent ranged GETs against pinned parts; read-amplification + decode-cache (shard/manifest) interaction under `FINAL` wide fan-in unverified (expected-correct). | TEST-GAP | MVCC-3 |

---

## 4. Info / by-design / verified-safe (non-actionable)

Retained for completeness; not defects.

| ID | Note | Merged from |
|----|------|-------------|
| CAS-201 | **B151 early publish** in `moveDirectory` exposes a rollback-window read; commit-time non-atomicity across parts is documented. | TXN-4, TXN-1(codeonly) |
| CAS-202 | **CAS is fully data-type agnostic** — stores opaque files keyed by content hash; all MergeTree column types (incl. JSON/Variant/Dynamic/QBit/Geo) supported with no type-specific logic; names `escapeForFileName`-normalized and never S3 key segments. | datatype-agnosticism (AD1-6 etc.) |
| CAS-203 | **All mainstream MergeTree part types supported** — Wide/Compact (always Full storage), projections, patch parts, lightweight deletes, detached/temp/frozen, ReplicatedMergeTree via fetch-by-relink; zero-copy intentionally disabled. | part-support, ENG-1/3, M1/M2/M7/M8, BAK-2 |
| CAS-204 | **S3 SSE (SSE-S3/KMS/C) is fully supported and recommended** — transparent, encrypts all objects at rest, preserves dedup. | encryption |
| CAS-205 | **Fail-closed everywhere on the safety core** — content addressing, two-phase precommit→promote, ack-floor-latched-before-cut, two-phase graduation, exact-token deletes, attempt-scoped generations, baseline guard; TLA+ suite with sabotage validation covers the write/GC/mount/incarnation core. Verified-clean lock order, release/acquire atomics, immutable cached payloads, exception-safe write buffers & txn dtor. | jepsen, gc, interleaving, tla, concurrency §4, bc3 |
| CAS-206 | **`GC REBUILD` `--force` is correctly narrow** (bypasses only the healthy-state refusal; never the lease-conflict or missing-manifest refusals) — cannot bless data loss. | GCR-6, GCR-7 |
| CAS-207 | **Content-addressed keys make the FS cache ideal** (no invalidation, cache-level dedup); one file = one blob = one payload ⇒ no cross-blob compression-boundary hazard. | CACHE-1, BC5-1, BC5-6 |
| CAS-208 | **TTL is data-driven, not mtime-driven** → synthetic mtime does not affect TTL expiry/moves. | BC6-4 |
| CAS-209 | **Relink is data-safe under version skew** (fail-closed publish-nothing → byte-fetch fallback; format bumps caught by the manifest's own compat gate). | SKEW-2/3/4/7, RPL-1 |
| CAS-210 | **Onto-CAS migration dedups on landing** — a genuine storage-cost win. | MIG-8 |
| CAS-211 | Repudiation: provenance/`CasEvent` are self-asserted (forgeable by a pool-write adversary); blobs plaintext / content-equality observable (delegated to S3). | SEC-8, SEC-9 |
| CAS-212 | Retired `FormatId` values rely on "pre-release, nothing deployed" — freeze the enum + retired-shape reservations at GA. | UPG2 |
| CAS-213 | `manifestCleanupShard` hashes the qualified `ManifestId`; GC-artifact determinism is load-bearing and fail-closed. | GC-shard-plan, BID-1 |
| CAS-214 | Instrumentation is extensive (66 ProfileEvents); `classifyCasNs` uses unanchored substring match (metric misattribution only, no correctness impact); per-decision `CasEvent` log is comprehensive but high-volume (ensure gated). | INSTR-1, OBS-4 |

---

## 5. Test-coverage gaps (findings that also lack a failing test)

| Finding (CAS id) | Missing test |
|---|---|
| CAS-010 | Decoder fuzzers (`src/Disks/fuzzers/`) for envelope/run-file/manifest/root-shard/gc-formats/pool-meta (FZ1). |
| CAS-001 | Read-vs-GC race: `resolve→manifest→(delay)→blob GET` against concurrent `dropRef`+GC delete (T-G1). |
| CAS-002 | Fencing TOCTOU: stale-epoch writer between `mayMutate()` and `casPut` (T-G2). |
| CAS-009 | Two-generation rolling-upgrade compat (T-G5, after write-down-to-floor lands). |
| CAS-023 | TSan stress for Store open/close + remount teardown (T-G6). |
| CAS-021 / CAS-022 | Power-loss-mid-commit and crash-mid-RENAME re-drive completeness (T-G3, T-G4). |
| CAS-012 | Real-S3 / real-GCS conditional-write + error-classification e2e (OSC-1). |
| CAS-015 | Concurrent-writer during `rebuildBaseline`; command-layer (`isReadOnly` gate) tests (GCR-1, proof code drafted). |

---

## 6. Cross-reference index (original id → CAS id)

Write: W1→CAS-020, W2→CAS-081, W-N1→CAS-035, W-N2→CAS-082, W-N3→CAS-083, W-N4→CAS-084.
Read: R1→CAS-001, R2→CAS-205(by-design), R3→CAS-085, R4→CAS-086, F-N1→CAS-034, F-N2→CAS-001, F-N3→CAS-087, F-N4→CAS-086.
GC: G-N1→CAS-033, G-N2→CAS-088, G-N3→CAS-205(safe), G-N4→CAS-089, GC-1→CAS-072, SCHED-1/2→CAS-032.
Interleaving: X1→CAS-001, X2→CAS-020, X3→CAS-033.
Jepsen: J1→CAS-002, J2→CAS-029, J3→CAS-030, J5→CAS-082.
Security: SEC-1→CAS-003, SEC-2→(dedup oracle, CAS-003 family), SEC-3→CAS-004, SEC-4→CAS-026, SEC-5→CAS-074, SEC-6→CAS-108, SEC-7→CAS-002/CAS-030, SEC-8/9→CAS-211.
Concurrency: C1→CAS-023, C2→CAS-090, C3→CAS-091, C4→CAS-092.
Crash: DUR1→CAS-021, DUR2→CAS-022.
Upgrade: UPG1→CAS-009, UPG2→CAS-212.
IDisk: C-U1→CAS-022, C-U2→CAS-048, C-U3→CAS-002, C-U4→CAS-111, C-U5→CAS-021, C-U6/7→CAS-112.
Perf: P1→CAS-067, P2→CAS-056, P3→CAS-056, P4→CAS-057.
TLA: F1→CAS-002, F2→CAS-001, F3→CAS-030, F4→CAS-029, F5→CAS-033, F6→CAS-023/090/091/092.
Part-support: B-1→CAS-042, B-2→CAS-041, B-3→CAS-105, B-4→CAS-073, B-5→CAS-110, B-6→CAS-111.
ALTER/merge: M1→CAS-020(n/a), M4→CAS-021, M5→CAS-001, M6→CAS-002.
Encryption: E-1→CAS-046, E-2/3/4→CAS-113.
Tier1: RPL-2→CAS-045, RPL-3→CAS-002, RPL-4/5→CAS-110, LC-1→CAS-043, LC-2→CAS-044, INT-1→CAS-005, INT-2→CAS-003, INT-3→CAS-093, INT-4→CAS-094, MVCC-1→CAS-001.
Tier2: SYS-1→CAS-040, SYS-2/3/4/5→CAS-101, CACHE-2→CAS-068, CACHE-3→CAS-102, TIER-1→CAS-041, TIER-2→CAS-043, TIER-3/4→CAS-103, DEDUP-2→CAS-104.
Tier3: TXN-1→CAS-059, TXN-2→CAS-059/021, BAK-1→CAS-042, BAK-3→CAS-042, BAK-4→CAS-105, BOOT-1→CAS-058, BOOT-2→CAS-044, BOOT-3→CAS-005, CFG-1→CAS-056, CFG-2→CAS-064, CFG-3→CAS-106, CFG-4→CAS-043, ENG-2→CAS-001.
Tier4: OSC-1→CAS-012, OSC-2→CAS-011, OSC-3→CAS-065, OSC-4→CAS-058, ERR-1→CAS-053, ERR-2→CAS-060, ERR-3→CAS-084, OBS-1/2→CAS-014, OBS-3→CAS-102.
AD1: AD1-2→CAS-107, AD1-3→CAS-037, AD1-5→CAS-107, AD1-7→CAS-003.
AD2: ERASE-1→CAS-018, ERASE-2→CAS-019, ERASE-3/4→CAS-070, ERASE-5→CAS-071, ERASE-6→CAS-044.
AD3: DR-1→CAS-013, DR-2→CAS-014, DR-3→CAS-044, DR-4→CAS-062, DR-5→CAS-063, DR-6→CAS-084.
AD4: MIG-1/3/4/5→CAS-069, MIG-2→CAS-041, MIG-6→CAS-005, MIG-7→CAS-042.
AD5: RES-1→CAS-008, RES-2→CAS-056, RES-3→CAS-049, RES-4→CAS-092, RES-5→CAS-057, RES-6/7→CAS-100.
AD6: LIFE-1→CAS-016, LIFE-2→CAS-017, LIFE-3→CAS-052, LIFE-4→CAS-051, LIFE-5→CAS-011, LIFE-6/7→CAS-114.
AD7: SKEW-1→CAS-054, SKEW-5/6→CAS-054, SKEW-2/3/4/7→CAS-209.
BC1: BC1-1→CAS-039, BC1-2/3/4→CAS-095.
BC2: BC2-1/2→CAS-038, BC2-3/4/6→CAS-096.
BC3: BC3-1/6→CAS-021, BC3-2/3→CAS-097.
BC4: BC4-1→CAS-026, BC4-2→CAS-027.
BC5: BC5-2→CAS-047, BC5-3/4/5→CAS-098.
BC6: BC6-1/2→CAS-048, BC6-3/5→CAS-099, BC6-4→CAS-208.
BC7: BC7-1..4→CAS-006, BC7-5→CAS-006.
GC-rebuild: GCR-1→CAS-015, GCR-2/4→CAS-050, GCR-3→CAS-108, GCR-5→CAS-058, GCR-6/7→CAS-206.
Codeonly: ENV-1→CAS-039, ENV-2/3→CAS-075, FMT-1→CAS-076, MC-1→CAS-025, MC-2→CAS-115, RF-1→CAS-028, RSC-1→CAS-026, RSC-2→CAS-027, RSC-3→(verified-safe, fail-closed journal validation), GS-1→CAS-077, LAY-1/2→CAS-074, LAY-3→(retracted), PM-1→CAS-066, PROBE-1→CAS-078, OSB-1→CAS-079, OSB-2→CAS-012, OSB-3→CAS-011, INSTR-1→CAS-214, SR-1→CAS-030, SR-2/3→CAS-080, STORE-C1→CAS-023, STORE-2→CAS-024, STORE-3→CAS-116, BUILD-1→CAS-037, BUILD-2→CAS-036, MW-1→CAS-031, MW-2→CAS-047, PPP-1→CAS-073, TXN-1/2/3/4(codeonly)→CAS-021/022/111/201, BID-1→CAS-213.
Tier1 (MVCC): MVCC-1→CAS-001, MVCC-2→(verified-safe, no wrong-results), MVCC-3→CAS-117, LC-3→(verified-safe, cross-pool DROP preserves shared blobs). BC4-4→CAS-026 (folded), OBS-4→CAS-214 (folded).
Info/verified-safe items intentionally not given their own CAS id (no defect): AD1-1, AD1-4, ERASE-7, DR-7, RES-8, BC1-5/6, BC2-5, BC3-4/5, BC4-5/6, BC6-6, BC7-6, DEDUP-1/3, ASYNC-1, BOOT-4, ERR-4, M3(safe), TLA-F6(scope) — plus AD-5≡CAS-008 and AD-6≡CAS-063 (runbook aliases of existing findings).
Coverage-map: G1→CAS-007, G2→CAS-061, G3→CAS-041, G4/5/6/8→CAS-055, G7→CAS-109, G9/10/11→CAS-109, G12→CAS-105.

---

## 7. Headline

Deduplicated, the ~330 per-audit findings collapse to **131 distinct issues** (128 actionable `CAS` ids +
CAS-115/116/117 added by the completeness re-scan). The safety core
(write two-phase spine, GC ack-floor/two-phase/exact-token, content addressing, fail-closed decode) is
**genuinely airtight** — every crash/concurrency/fault interleaving on the write↔GC plane biases to a
reclaimable **leak**, never data loss or a false commit.

The **genuine data-loss / correctness** paths are narrow and well-characterized:
**CAS-001** (ref-less reader has no pin across the deferred blob GET), **CAS-002** (shard CAS fenced by
content token, not `writer_epoch` → split-brain), **CAS-015** (GC REBUILD lacks a mount-lease interlock),
and the config-triggered **CAS-016/CAS-017** (lifecycle expiration / Object Lock). **CAS-005** (no read-time
payload re-hash) + **CAS-003** (non-crypto hash) mean CAS delegates all content integrity to MergeTree.

The largest clusters are **not** correctness bugs but **operability**: GC-deferred reclamation with no
liveness metric (CAS-013/CAS-014/CAS-043), a fixed pool-wide `root_shards` (CAS-056), the untrimmed-journal
write-availability coupling (CAS-008), blocking S3 publish under `DataPartsLock` (CAS-006), and a wide set
of unverified edges (backup-on-Ordinary, cross-disk MOVE, UniqueKey/DeleteBitmap, real-S3 conditional-write
tests). Highest-leverage single fix: **carry `writer_epoch` into the shard-CAS precondition** (resolves
CAS-002 and most Jepsen/security fencing findings at once).

## cas-ad1-hash-determinism-audit.md

Language: Markdown

# AD-1 — Hash Determinism & Cross-Platform Reproducibility Audit

Question: CAS dedup, relink, and integrity all rest on "identical bytes → identical hash **everywhere**."
Is that true across CPU architectures, compilers, and ClickHouse versions? Grounded in
`CasManifestCodec.cpp` (`encodePartManifest`, `manifestId`), `CasBuild.cpp` (`poolContentHash`),
`CasStore.cpp` (`shardOf`), `CasEnvelope.cpp`, `CasFormat.{h,cpp}` (`G_BUILD`).

---

## 1. What is hashed, and how

| Hash | Input | Algorithm | Serialization |
|---|---|---|---|
| **Blob content hash** (dedup key) | raw file **payload bytes only** | `CityHash128` | none — raw bytes |
| **ManifestId** | the **encoded** `PartManifest` | `CityHash128` | hand-rolled, all `writeBinaryLittleEndian` |
| **Shard selector** (`shardOf`) | `ref_name` string | `CityHash64 % root_shards` | raw string bytes |
| **Envelope header hash** | 94-byte core header | `CityHash64` | LE fields |
| GC canonical ids | encoded records | `CityHash128` | LE |

Two determinism-critical properties:
1. **Serialization is explicitly little-endian** everywhere (`writeBinaryLittleEndian`, `writeU128LE`).
2. **Manifest entries are sorted by path** before encoding (`std::sort` on `entry.path`), with duplicate
 rejection → canonical order independent of insertion order.

---

## 2. Findings

**AD1-1 (Info — blob dedup key IS deterministic and endian-safe ✅).** The blob content hash is
`CityHash128` over the raw payload with no serialization in between. CityHash is a fixed integer
algorithm (no floating point, no locale, no allocation-order dependence); on any little-endian platform
it yields identical output. **All ClickHouse-supported production architectures (x86-64, aarch64/Graviton)
are little-endian**, so a part built on x86 and a byte-identical part built on ARM produce the **same blob
key** → cross-architecture dedup and relink work. This is the core value prop and it holds.

**AD1-2 (Low — big-endian is unsupported and would silently fork dedup).** CityHash's canonical
implementation only guarantees identical output across endianness if it byte-swaps loads on big-endian;
ClickHouse's bundled `CityHash_v1_0_2` targets LE. A hypothetical big-endian node in the same pool could
compute different hashes for identical bytes → **silent dedup fork / relink false-negatives** (never a
false *positive*, so no data corruption — just lost dedup + wasted transfer). ClickHouse doesn't support
BE builds in practice, so this is theoretical, but there is **no explicit guard/assert** that the pool is
LE-only. Recommend a one-line documented invariant.

**AD1-3 (Med — the content-hash algorithm is a permanent, unversioned pool-wide contract).** The blob key
= `CityHash128(payload)`. Nothing pins the *hash algorithm identity* in `PoolMeta`: `G_BUILD` /
`compatibility_version` gate the *envelope/manifest format*, but **not** which hash function produces blob
keys. If a future ClickHouse ever changed the bundled CityHash implementation (or switched dedup to a
different hash), then:
- existing blobs remain addressable (keys are stored, reads use stored keys), **but**
- new writes of content identical to old blobs would compute a **different** key → the pool **forks**:
 two physical copies of the same bytes, dedup ratio silently degrades, and relink between an
 old-hash replica and a new-hash replica **false-negatives** (adopt-by-hash misses).

There is no fail-closed check that the running build's hash matches the pool's original hash. **This is
the most important finding**: the dedup hash must be treated as an immutable pool contract and ideally
recorded + verified in `PoolMeta` (like a "hash_algo_id"). Today it's implicit.

**AD1-4 (Info — ManifestId is intentionally identity-scoped, NOT content-only).** `encodePartManifest`
embeds `writer_epoch`, `build_sequence`, `manifest_ordinal`, `root_namespace_id`, and `writer_version`
**into the bytes that get hashed** into the ManifestId. So two replicas building the "same" part get
**different ManifestIds** (different epoch/namespace) — by design: relink republishes a *receiver-local*
manifest. Consequence to state plainly: **manifest-level dedup is never cross-replica; only blob-level
dedup is.** Correct, but it means the achievable dedup across replicas is bounded by blob sharing, and
the manifest object itself is duplicated per replica (small, but non-zero).

**AD1-5 (Low — manifest bytes are not version-stable across CH versions).** Because `currentWriterVersion()`
(= `G_BUILD`) and `format_version` are embedded in the hashed manifest bytes, the **same logical part
encoded by two different ClickHouse versions produces different manifest bytes and a different
ManifestId**. Harmless (ManifestId is local identity, and blob keys are unaffected), but it means "rebuild
the same part, get the same manifest object" is **false across versions** — worth knowing for
reproducibility/debugging expectations and for any test that asserts manifest-byte equality.

**AD1-6 (Info — file-name normalization is deterministic).** Manifest entry keys are `escapeForFileName`
paths (`[A-Za-z0-9_%]`), a pure deterministic transform, sorted canonically. No locale/collation
dependence. ✅

**AD1-7 (Low — CityHash is non-cryptographic; determinism ≠ collision-resistance).** Cross-references
SEC-1 / INT-2. Deterministic hashing means *the same* content always collides to *the same* key (good),
but distinct content could also collide (bad, silent wrong-bytes sharing) and, combined with INT-1
(no read-time payload re-verification), would be undetectable at the CAS layer. Determinism audit's job
is to confirm the *intended* collisions happen everywhere; it does **not** rescue the collision-resistance
concern.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| AD1-1 | Info | Blob dedup key is deterministic + endian-safe on all supported (LE) archs ✅ |
| AD1-2 | Low | Big-endian unsupported; would silently fork dedup; no explicit LE guard |
| AD1-3 | **Med** | Content-hash algorithm is an unversioned, unpinned permanent pool contract; a future hash change forks the pool silently |
| AD1-4 | Info | ManifestId is identity-scoped by design → no cross-replica manifest dedup, only blob dedup |
| AD1-5 | Low | Manifest bytes/ManifestId not version-stable across CH versions (harmless) |
| AD1-6 | Info | File-name normalization deterministic ✅ |
| AD1-7 | Low | Deterministic ≠ collision-resistant (see SEC-1/INT-2) |

**Verdict:** the reproducibility foundation is **sound on all real platforms** (LE, fixed CityHash), and
the careful LE serialization + canonical entry sort are the right choices. The one thing that should be
hardened is **AD1-3**: record and fail-closed-verify the dedup hash-algorithm identity in `PoolMeta`, so a
future implementation change can never silently fork a live pool's dedup and break relink.

## cas-ad2-deletion-erasure-audit.md

Language: Markdown

# AD-2 — Data-Deletion & Erasure-Guarantee Audit (GDPR "right to be forgotten")

Question: when a user issues DELETE / DROP / TTL-expiry on a CAS-backed table, **when — if ever — are the
underlying bytes actually gone from S3?** Can a regulated operator *prove* erasure? Grounded in the
deletion path (`ContentAddressedTransaction::removeRecursive`/`dropRefIfPresent`, `Store::dropNamespace`),
GC reclaim (`CasGc.cpp` two-phase graduation + `deleteExact`, `gc/snap` retention), and dedup semantics
(source-edge sets).

---

## 1. The deletion pipeline (how bytes actually leave S3)

A logical delete on CAS is a **pointer unlink**, not an erase:

```
DELETE/DROP/TTL  →  dropRef / dropNamespace        (tombstone the ref; bytes untouched)
                 →  GC round: discover unreachable  (blob now has in-degree 0)
                 →  two-phase graduation: delete_pending → deleteExact   (S3 DELETE)
                 →  gc/snap generations retained (default keep 3)        (audit trail)
```

Bytes physically leave S3 only at the `deleteExact` step, which is gated by:
- the blob being **unreferenced by every live ref in the whole pool** (dedup: any surviving ref pins it),
- GC actually **running** (enabled, has a leader, has a mount),
- passing the **two-phase graduation** delay (safety against zombie leaders),
- **not** being resurrected by copy-forward,
- the backend actually **reclaiming** on DELETE (not archiving — see OSC-2 GCS versioning).

---

## 2. Findings

**ERASE-1 (High for compliance — "delete" ≠ "erased"; no bounded erasure SLA).** There is **no upper
bound** on the wall-clock time between a logical delete and physical byte removal. Reclaim is entirely
GC-deferred (LC-1) and can be delayed indefinitely by: GC disabled / read-only disk (CFG-4), no
live writer/mount, GCS bucket versioning (OSC-2), a stalled GC leader, or `suppress_destructive` clamping
after an anomaly. A regulated operator **cannot promise** "data erased within N days" from CAS mechanics
alone. GDPR/CCPA erasure deadlines are the operator's problem with no engine support.

**ERASE-2 (High for compliance — dedup means one user's delete may erase nothing).** Because blobs are
shared by content, deleting user A's row/part does **not** remove the bytes if user B (another
table/partition/replica, or a FREEZE shadow) holds a ref to a byte-identical blob. The bytes survive,
legitimately reachable, potentially **forever**. For "erase all of subject X's data" this is a genuine
semantic gap: **erasure of a logical record does not guarantee erasure of the underlying bytes** when
those bytes are shared. There is no per-subject "shred this content everywhere" primitive, and no way to
enumerate "which refs share this blob" at delete time (fsck can, offline).

**ERASE-3 (Med — FREEZE shadow refs and detached parts silently retain deleted data).** A `FREEZE`d
partition keeps shadow-namespace refs that pin the blobs (BAK-2: zero-copy freeze). So after a DELETE +
DROP PARTITION, a prior FREEZE still holds the data alive until the backup is explicitly UNFROZEN.
Likewise `detached/` refs (B181) survive table-level operations. Erasure must therefore also sweep every
FREEZE/backup and detached ref — easy to miss operationally.

**ERASE-4 (Med — `gc/snap` retention keeps a metadata audit trail referencing deleted content).** GC
retains N snap generations (default 3). These do not keep *blob bytes* alive (they're not live refs), but
they retain **metadata about what existed and was reclaimed** (ids, sizes, timings). Depending on the
compliance regime, retained metadata about deleted subjects may itself be in scope. Low data-content risk,
noted for completeness.

**ERASE-5 (Med — no crypto-shredding / secure-erase; relies on S3 DELETE semantics).** CAS issues a plain
`deleteExact` (S3 DELETE). Actual byte destruction depends on the object store: versioned buckets archive
noncurrent versions (OSC-2), soft-delete/recycle-bin features (GCS soft-delete, S3 with MFA-delete or
replication) may retain copies, and cross-region replication (AD-6) may have propagated the object to
another bucket that CAS never deletes. There is **no crypto-shredding option** (encrypt-per-subject + drop
key) — and it wouldn't compose with CAS anyway because per-subject keys defeat dedup (see encryption
audit E-1). So erasure assurance is only as strong as the bucket's DELETE-actually-destroys guarantee,
which CAS neither verifies nor documents.

**ERASE-6 (Low — orphaned namespaces/refs (LC-2, RPL-2) retain data indefinitely).** The crash-orphaned
namespace and ZK/CAS-divergent orphaned ref findings mean data that the *catalog* believes is gone can
persist on S3 with a live ref forever, invisible to any DROP. This is both a leak (LC-2) **and** an
erasure hole: a deleted table's data could linger in an orphaned namespace.

**ERASE-7 (Info — the deferred model is the right *engineering* choice; the gap is contractual).** The
GC-deferred, dedup-sharing, two-phase design is correct and safe for a storage system. The findings above
are not bugs — they are the **absence of a compliance-grade erasure contract/tooling** on top of a system
whose whole point is to *not* delete shared bytes eagerly.

---

## 3. What would close the gap (recommendations)

1. **A "reclaim now" + "prove erased" tool**: a foreground command that, for a given namespace/blob set,
 forces GC graduation and returns confirmation once `deleteExact` completed pool-wide (and errors if any
 surviving ref shares the blob, naming those refs — fsck already computes reachability).
2. **A bounded-reclaim SLA config + metric**: "max time from unreference to delete" with alerting when
 exceeded (ties to OBS-2).
3. **Erasure-scope enumeration**: given a subject/partition, list every ref (live, detached, FREEZE
 shadow, other tables) that pins its blobs, so an operator can execute complete erasure.
4. **Document the deletion model explicitly**: DELETE/DROP are logical; physical erasure is GC-deferred,
 dedup-gated, and backend-DELETE-dependent (versioning/soft-delete/replication caveats).
5. **Backend erasure preconditions**: refuse (or loudly warn) on buckets with versioning/soft-delete/CRR
 when an erasure guarantee is required (extends the OSC-2 check).

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| ERASE-1 | High (compliance) | No bounded time from logical delete to physical erase; GC-deferred & stallable |
| ERASE-2 | High (compliance) | Dedup: deleting one owner erases nothing while any ref shares the blob; no per-subject shred |
| ERASE-3 | Med | FREEZE shadow refs + detached refs silently retain deleted data |
| ERASE-4 | Med | `gc/snap` retains metadata (not bytes) about deleted content |
| ERASE-5 | Med | Plain S3 DELETE; no crypto-shred; versioning/soft-delete/CRR may retain copies CAS never removes |
| ERASE-6 | Low | Orphaned namespaces/refs (LC-2/RPL-2) retain deleted data indefinitely |
| ERASE-7 | Info | Deferred/dedup model is correct engineering; the gap is a missing compliance contract/tooling |

**Verdict:** CAS is **not, out of the box, a compliance-grade erasure system**. It is safe and correct as
storage, but "the data is deleted" is only true logically; physical erasure is unbounded, dedup-gated, and
backend-dependent. Regulated deployments need the reclaim/prove/enumerate tooling above plus explicit
documentation — this is the highest-impact finding of AD-2.

## cas-ad3-day2-dr-runbook-audit.md

Language: Markdown

# AD-3 — Day-2 Operations & Disaster-Recovery Readiness Audit

Question: for every failure mode the prior audits surfaced, **can an operator (a) detect it and
(b) recover from it**, and does the tooling exist? This consolidates scattered findings into a
recovery-readiness matrix. Grounded in the exposed operator surface (`ASTSystemQuery.h`:
`CONTENT_ADDRESSED_GARBAGE_COLLECTION`, `CONTENT_ADDRESSED_GC_REBUILD [FORCE]`;
`InterpreterSystemQuery.cpp`), plus `CasFsck.cpp`, `CasProbe.cpp`, `CasServerRoot.cpp`
(owner/mount/epoch), `CasOrphanManifestSweep.cpp`.

---

## 1. The operator toolbox that exists today

| Tool | Surface | Purpose |
|---|---|---|
| `SYSTEM CONTENT ADDRESSED GARBAGE COLLECTION` | SQL | Run one GC round now (foreground) |
| `SYSTEM CONTENT ADDRESSED GC REBUILD [FORCE]` | SQL | Rebuild `gc/state` baseline from owner state (the gc-rebuild spec) |
| `system.content_addressed_garbage_collection_log` | table | Per-round Start/Finish audit rows |
| `system.content_addressed_log` | table | Per-decision CAS event trace |
| startup probe (`CasProbe`) / `checkStorePreconditions` | automatic | Fail-closed mount validation (incl. GCS versioning) |
| mount lease + owner anchor + writer epoch | automatic | Single-writer enforcement, fail-closed on conflict |
| `CasOrphanManifestSweep` + GC | automatic | Reclaim pre-precommit manifest debris |

**Notably absent from the operator surface:** `runFsck` (the reachability / dangling / physical-vs-logical
diagnostic) is **internal/test-only — not exposed as a SQL SYSTEM command or table function.**

---

## 2. Recovery-readiness matrix (failure mode → detect? → recover? → gap)

| Failure mode (source finding) | Detectable today? | Recovery path today? | Gap |
|---|---|---|---|
| **`gc/state` lost/corrupt** | GC round errors in log | ✅ `GC REBUILD` (designed for exactly this) | Well covered ✅ |
| **GC silently stopped reclaiming** (OSC-2 GCS versioning, no leader, `suppress_destructive`) | 🟡 only by log-diving / no metric (OBS-2) | run GC / fix bucket | **No liveness/backlog metric or alert** |
| **Dangling blob — reachable ref, object missing** (INT-3, INV-NO-LOSS) | ❌ only via internal fsck | manual re-fetch from replica (Replicated only) | **fsck not operator-exposed; no auto-repair** |
| **Silent blob bit-rot in payload** (INT-1) | ❌ (no read-time hash verify) | `CHECK TABLE` (MergeTree checksums) if run | **No CAS-level scrub; must know to run CHECK TABLE** |
| **Orphaned namespace after crash-during-drop** (LC-2) | ❌ no catalog-vs-pool reconcile | none automated | **No orphan-namespace sweeper; permanent leak** |
| **Orphaned ref: CAS-has / ZK-missing** (RPL-2) | 🟡 phantom part at startup (BOOT-2) | detach/drop churn | **No reconcile tool; behavior untested** |
| **ZK-has / CAS-missing part** (RPL-2) | broken part on load | re-fetch from replica | Recoverable on Replicated; **fatal on non-replicated** |
| **Split-brain / zombie writer** (J1, SEC-7 clock skew) | 🟡 lease conflict logged | fail-closed refusal (mount lease) | Mostly covered; **no explicit "who holds the lease" view** |
| **Stuck mount lease (dead server, TTL not expired)** | 🟡 new writer blocked, logged | wait for TTL / manual? | **No documented "force-release lease" procedure** |
| **`PoolMeta` corrupt / unreadable** | mount fails closed | none documented | **No pool-meta backup/restore runbook** |
| **Manifest hard-limit wedge (shard > 64 MiB)** (AD-5) | write errors (TOO_MANY) | GC must trim refs | **No direct "split/compact shard" tool** |
| **Failed-build debris accumulation** (ERR-2) | 🟡 fsck Unreachable class | sweep + GC | Covered, but debris rate unbounded under failure storm |
| **Incomplete multipart uploads after crash** (ERR-3) | ❌ (needs bucket inspection) | bucket lifecycle rule | **CAS doesn't abort orphaned MPUs** |
| **Whole-pool disaster (bucket lost)** | obvious | restore from another region/backup | **No CAS-native pool backup/replication story** (AD-6) |

---

## 3. Findings

**DR-1 (High — fsck is not operator-accessible).** The single most valuable diagnostic — independent
reachability recomputation, dangling detection, physical-vs-logical byte accounting, dedup ratio — exists
(`runFsck`) but is only reachable from tests/internal code. Operators cannot answer "is my pool healthy?
am I losing data? how much am I actually storing?" via SQL. **Expose it** as `SYSTEM CONTENT ADDRESSED
CHECK`/`FSCK` (with the deadline + progress-sink it already supports) or a table function.

**DR-2 (High — no GC-liveness / reclaim-backlog signal).** So many failure modes terminate in "GC
silently stops reclaiming," yet there is no metric for "rounds since last successful reclaim," "bytes
pending reclaim," or "GC leader present." A stalled GC (the most common silent failure) is invisible
without log-diving. **Add gauges + an alertable staleness threshold** (ties OBS-1/OBS-2).

**DR-3 (Med — no orphan reconciliation between catalog/ZK and the pool).** LC-2 and RPL-2 orphans have
**no detection or repair tool**. A `SYSTEM CONTENT ADDRESSED RECONCILE` that diffs live catalog/ZK part
sets against enumerated CAS namespaces/refs (report + optional drop of provably-orphaned refs) would close
both the leak (AD-2 ERASE-6) and the phantom-part-at-startup churn (BOOT-2).

**DR-4 (Med — no documented lease/owner recovery procedures).** Single-writer safety is enforced via the
mount lease + owner anchor + epoch, all fail-closed. But there is **no runbook** for the inevitable
operational events: a dead writer whose lease hasn't expired (how long must the new server wait? is there
a safe force-release?), an accidentally-reused `server_root_id` (CFG-2), or a need to inspect "who owns
this server_root." Provide read-only introspection (`system` view of owner/mount/epoch) + a documented,
safe recovery sequence.

**DR-5 (Med — no pool-metadata backup/restore story).** `gc/state` has REBUILD, but `PoolMeta`, owner
anchors, and the broader control plane have no documented backup/restore. A corrupt `PoolMeta` fails the
mount closed with no recovery runbook. Document (and ideally tool) control-plane backup.

**DR-6 (Low — no MPU-abort hygiene).** Crash-orphaned multipart uploads are billed until a bucket
lifecycle rule aborts them; CAS neither aborts nor reports them (ERR-3). Document the required bucket
lifecycle rule.

**DR-7 (Info — the one recovery tool that exists is excellent).** `GC REBUILD` (with its fail-closed
"baseline guard" on trimmed history and the `FORCE` escape hatch) is a well-designed, well-scoped DR tool
for its intended threat (accidental `gc/state` loss). The problem is *breadth* — it's the only rich DR
tool, and the failure surface is much wider.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| DR-1 | High | fsck (health/dangling/physical-bytes) is not operator-accessible via SQL |
| DR-2 | High | No GC-liveness / reclaim-backlog metric; the most common silent failure is invisible |
| DR-3 | Med | No catalog/ZK-vs-pool orphan reconciliation tool (LC-2/RPL-2/ERASE-6) |
| DR-4 | Med | No lease/owner introspection or documented force-release/recovery runbook |
| DR-5 | Med | No `PoolMeta`/control-plane backup-restore story |
| DR-6 | Low | Orphaned multipart uploads neither aborted nor reported |
| DR-7 | Info | `GC REBUILD` is an excellent, well-scoped DR tool — but it's the only rich one |

**Verdict:** CAS has **strong automatic safety** (fail-closed everywhere) and **one excellent recovery
tool** (GC REBUILD), but **weak Day-2 observability and a narrow manual-recovery toolbox.** The highest-
value additions are operator-exposed **fsck (DR-1)** and **GC-liveness metrics (DR-2)** — without them,
most of the "silent" failure modes across all prior audits are undetectable in production until they cause
a visible outage or bill shock.

## cas-ad4-migration-audit.md

Language: Markdown

# AD-4 — Migration Onto / Off CAS Audit

Question: how does an existing MergeTree table (on local/plain-S3) get its data **onto** a CAS disk, and
back **off**? Is there a supported path, and what are its hazards? Grounded in the partition-command
gating (`MergeTreeData.cpp` `MetadataStorageType::ContentAddressed` supported list + the in-code
"cross-disk is a follow-up to verify" note), the cross-disk byte-copy `clonePart` path, and the write
transaction model.

---

## 1. Available migration mechanisms (there is no in-place conversion)

CAS is a `metadata_type` of a disk. You **cannot** convert a plain-S3/local disk's existing metadata into
CAS metadata in place — the on-S3 layout is fundamentally different (content-addressed blobs + manifests
vs 1:1 file objects). So migration is always **data movement**, via one of:

| Path | Onto CAS | Off CAS | Mechanism |
|---|---|---|---|
| `INSERT SELECT` into a new table on a CAS storage policy | ✅ | ✅ | normal write path; re-parts everything |
| Add CAS volume to storage policy + `ALTER MOVE PARTITION ... TO VOLUME/DISK` | ✅ | ✅ | **cross-disk byte-copy `clonePart`** |
| TTL move rules (hot→CAS cold) | ✅ | ✅ | same cross-disk byte-copy |
| `ATTACH PARTITION FROM` (another table) | 🟡 | 🟡 | `REPLACE_PARTITION`; same-disk verified, cross-disk unverified |
| `FETCH PARTITION` from a replica onto a CAS disk | ✅ | n/a | byte fetch → content-addresses on landing |
| BACKUP → RESTORE into a CAS table | ✅ | ✅ | RESTORE via whole-part transaction (Atomic DB only, BAK-1) |

---

## 2. Findings

**MIG-1 (Med — no in-place conversion; migration always rewrites all data).** Every migration path
physically reads and rewrites bytes (then CAS content-addresses + dedups on landing). For a large table
this is a **full data rewrite** (I/O, S3 request cost, time), not a metadata flip. Operators expecting a
cheap "switch this table to CAS" will instead pay a full copy. Should be documented; there is no
fast-path.

**MIG-2 (Med — cross-disk MOVE onto/off CAS is the known-unverified path).** The primary in-place-ish
migration (`ALTER TABLE ... MOVE PARTITION ... TO DISK/VOLUME`) uses the cross-disk byte-copy `clonePart`
path, which `MergeTreeData.cpp` itself flags: *"only same-disk `MOVE ... TO TABLE` is verified here —
cross-disk is a follow-up to verify."* So the single most natural migration mechanism is **explicitly
unverified** on CAS (ties Tier 2 TIER-1, coverage-map G3). Onto-CAS is lower-risk (it's just a normal
write on landing); off-CAS reads via the CAS read path then writes to the target — also unverified for
correctness under concurrent GC.

**MIG-3 (Med — migration onto CAS + GC-deferred source reclaim double-bills).** During onto-CAS MOVE, the
source part persists until removed; on off-CAS MOVE, the CAS source ref drops but blobs persist until GC
(LC-1/TIER-2). A large migration wave therefore transiently **doubles storage** and, for off-CAS, leaves
the CAS bytes billed until GC catches up. No throttle couples migration rate to reclaim rate.

**MIG-4 (Med — mixed storage policy (CAS + non-CAS volumes) inherits every CAS ALTER restriction).** Once
a CAS disk is in a table's storage policy, the table is subject to the CAS partition-command allowlist
(`MergeTreeData.cpp`): commands not on the supported list throw `SUPPORT_IS_DISABLED`. So a table
straddling CAS and non-CAS volumes has a **reduced ALTER surface** for the whole table, even for
partitions currently on the non-CAS volume. Migrating *into* a mixed policy silently narrows what the
table can do. Must be documented.

**MIG-5 (Med — zero cross-replica warm-start / no bulk relink import).** Bringing a new replica onto a
shared CAS pool relies on per-part fetch (relink where possible). There is **no bulk "adopt this whole
table's refs" import** — each part is fetched/relinked individually through the replication queue. For a
huge table this is a long warm-up. And `FETCH PARTITION ... TO detached` never relinks (RPL-4), so
detached-target migration transfers full bytes.

**MIG-6 (Low — off-CAS migration reads through the CAS read path (INT-1 exposure)).** Moving data off CAS
reads blobs via ranged GETs with no payload hash re-verification (INT-1). A silently-corrupt CAS blob
would be copied verbatim to the destination, propagating corruption undetected unless MergeTree checksums
catch it. Migration is a good moment to verify integrity, but nothing forces it.

**MIG-7 (Low — BACKUP/RESTORE migration is Atomic-DB-only).** Using BACKUP→RESTORE to migrate onto CAS
inherits BAK-1 (Ordinary/non-UUID DBs unsupported) and BAK-4 (round-trip untested). Viable only for
Atomic databases.

**MIG-8 (Info — onto-CAS dedup is a genuine migration upside).** Migrating multiple tables / historical
partitions with overlapping content onto one CAS pool **collapses duplicates on landing** — a real
storage-cost win that plain-S3 migration doesn't offer. The `INSERT SELECT` path benefits most (fresh
content-addressing of everything).

---

## 3. Recommendations
1. Document that CAS migration is **always a full data rewrite** (no in-place conversion) and give a
 recommended procedure (new table + `INSERT SELECT`, or add-volume + MOVE with reclaim-aware pacing).
2. **Verify the cross-disk MOVE/clonePart path on CAS** (MIG-2/G3) — it's the mechanism most operators
 will reach for.
3. Warn/document that adding a CAS volume **narrows the table's ALTER surface** (MIG-4).
4. Provide a bulk-relink / warm-start import for standing up new replicas on a shared pool (MIG-5).
5. Recommend running `CHECK TABLE` (integrity) as part of any off-CAS migration (MIG-6).

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| MIG-1 | Med | No in-place conversion; migration always rewrites all bytes |
| MIG-2 | Med | Cross-disk MOVE (the natural migration path) is the code's own known-unverified path (G3) |
| MIG-3 | Med | Migration transiently double-bills; off-CAS leaves bytes billed until GC (LC-1) |
| MIG-4 | Med | A CAS volume in a mixed storage policy narrows the whole table's ALTER surface |
| MIG-5 | Med | No bulk relink/warm-start import for new replicas; per-part fetch only |
| MIG-6 | Low | Off-CAS migration reads via CAS read path with no payload re-verify (INT-1) |
| MIG-7 | Low | BACKUP/RESTORE migration is Atomic-DB-only (BAK-1) |
| MIG-8 | Info | Onto-CAS dedup collapses duplicates on landing — a real migration upside |

**Verdict:** migration works only as **full data movement** (no metadata flip), the most natural path
(cross-disk MOVE) is **explicitly unverified**, and adopting CAS into a mixed policy **silently reduces the
table's ALTER capabilities**. The upside is real (dedup on landing). The action items are verifying the
cross-disk MOVE path and documenting the rewrite-cost + reduced-ALTER-surface reality.

## cas-ad5-resource-exhaustion-audit.md

Language: Markdown

# AD-5 — Resource-Exhaustion & Scalability-Ceiling Audit

Question: where does CAS **break** (not just cost more) as tables, parts, churn, and multi-tenancy grow?
Grounded in `CasStore.h`/`CasStore.cpp` limits: `manifest_soft_limit` (16 MiB), `manifest_hard_limit`
(64 MiB), `manifest_max_delay_ms` (backpressure), `gc_trim_body_soft_limit` (8 MiB), `dedup_cache_bytes`
(64 MiB LRU), `SHARD_DECODE_CACHE_MAX_ENTRIES`/`MANIFEST_CACHE_MAX_ENTRIES` (16384 each), `root_shards`,
`kMaxManifestOrdinal`, and the "journal is never trimmed here" note (M-C2).

---

## 1. The hard ceilings

| Resource | Limit | Behavior at limit |
|---|---|---|
| Encoded root-shard body | **`manifest_hard_limit` = 64 MiB** | **writes to that (namespace, shard) REJECTED** (`TOO_MANY...`) |
| Encoded root-shard body | `manifest_soft_limit` = 16 MiB | LOG_WARNING + linear backpressure delay (≤ `manifest_max_delay_ms` = 1s) for Writer mutations |
| Manifests per build | `kMaxManifestOrdinal` | decode/encode rejects out-of-range ordinal |
| Shard decode cache | 16384 entries | **wholesale clear** on overflow |
| Manifest decode cache | 16384 entries | **wholesale clear** on overflow |
| Dedup known-present cache | 64 MiB | proper LRU eviction (honest ceiling) |
| Write parallelism per namespace | `root_shards` (default 8, fixed at pool creation) | contention beyond fanout |

---

## 2. Findings

**RES-1 (High — churn-driven journal growth can wedge a shard at the hard limit).** The root-shard object
carries both the live `refs` map **and** a `journal` of owner-change events (publish/drop). The code note
(M-C2) states plainly: *"the manifest journal is never trimmed here — trimming needs `folded_cursor`
(INV-JOURNAL-COVERAGE), which is GC state landing in M-C3; the manifest size guard (soft warn / hard
throw) bounds growth meanwhile."* So on a **high-churn table** (many merges/mutations/inserts → many
publish+drop events on the same shard), the journal grows monotonically **even if the live ref count stays
modest**, pushing the encoded body toward 64 MiB. At the hard limit, **all writes to that shard are
rejected** until GC folds the journal (advances `folded_cursor`) and trimming reclaims space. This makes
**write liveness of a hot table directly dependent on GC keeping up with folding.** If GC lags (OSC-2,
stalled leader, disabled), a churny shard can wedge. This is the most serious scalability finding: a
**correctness-adjacent liveness coupling** between GC progress and write availability.

**RES-2 (Med — `root_shards` is a fixed, pool-wide parallelism ceiling).** Set once at pool creation
(CFG-1). All tables share the same fanout. A table hotter than `root_shards` allows will serialize writes
through the flat-combining queue per shard; you **cannot add shards** to relieve it without recreating the
pool. Combined with RES-1, a low `root_shards` on a churny workload both increases per-shard journal
growth and caps parallelism. Sizing is permanent and unforgiving.

**RES-3 (Med — cache wholesale-clear is a thundering-herd perf cliff, not a memory leak).** The shard and
manifest decode caches are correctly memory-bounded (16384 entries, wholesale clear on overflow). But a
server touching **> 16384 distinct (namespace, shard) or (ManifestId, Token)** working-set entries (large
multi-tenant deployments, many tables/partitions/detached/FREEZE dirs) will trigger **full cache clears**,
causing a burst of re-HEAD + re-GET + re-decode across all concurrent readers. Not a crash, but a latency
cliff under scale. No LRU (unlike the dedup cache) — it's all-or-nothing.

**RES-4 (Med — `shard_write_seq` grows with distinct (namespace, shard) pairs, never cleared).** Flagged
in the concurrency audit (C4): `shard_write_seq` is monotonic and *deliberately* never reset (correctness
requires it). It's "bounded by distinct (namespace, shard) pairs," which for a very-many-tables server is
large and grows for the process lifetime. Small per-entry, but unbounded in table count over a long-lived
server. Low memory risk, noted for completeness at extreme multi-tenancy.

**RES-5 (Med — S3 LIST/HEAD cost scales with namespace & blob count).** Startup part enumeration and
`listNamespaces`/`dropNamespace` walk S3 LIST pages; a pool with a very large number of namespaces/refs
makes startup and drop LIST-bound (perf audit territory, but a *ceiling* at extreme object counts where
LIST pagination dominates). No sharded/parallel LIST for discovery.

**RES-6 (Low — manifest soft-limit backpressure is capped at 1s and per-flush).** Backpressure delay is
linear from soft→hard and capped at `manifest_max_delay_ms` (1s), applied at most once per flush. It
smooths approach to the hard limit but **cannot prevent** hitting it under sustained churn — it only buys
time for GC. If GC never catches up, backpressure just adds latency before the eventual hard-limit
rejection (RES-1). Backpressure is a shock absorber, not a governor.

**RES-7 (Low — no per-tenant quota within a shared pool).** A shared pool has no per-`server_root_id` /
per-table quota on blob bytes, ref count, or namespace count. One runaway tenant can consume pool storage
and inflate everyone's LIST/GC cost. Multi-tenancy fairness is unmanaged (ties security audit SEC-4 DoS).

**RES-8 (Info — blob-level scaling is S3-native and fine).** Individual blobs are content-addressed
objects; blob count scales as well as S3 does. Object-size ceilings are S3's (multipart). No CAS-specific
blob-count wall besides the LIST/GC cost (RES-5).

---

## 3. Recommendations
1. **RES-1**: prioritize the deferred journal trimming (M-C3), and/or expose a per-shard journal-size /
 distance-to-hard-limit metric + alert; consider a foreground "compact shard" op. This liveness coupling
 is the top risk.
2. **RES-2**: publish `root_shards` sizing guidance keyed to expected churn/parallelism (it's permanent).
3. **RES-3**: consider LRU (not wholesale-clear) for the decode caches, or make the cap configurable, to
 avoid the scale latency cliff.
4. **RES-7**: add per-tenant quotas/accounting for shared pools.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| RES-1 | High | Untrimmed journal grows with churn → shard hits 64 MiB hard limit → writes rejected until GC folds; write liveness coupled to GC progress |
| RES-2 | Med | `root_shards` is a fixed, unchangeable pool-wide parallelism ceiling |
| RES-3 | Med | Decode caches wholesale-clear at 16384 entries → thundering-herd re-decode cliff at scale |
| RES-4 | Med | `shard_write_seq` grows with distinct namespace/shard pairs, never reset (extreme multi-tenancy) |
| RES-5 | Med | Startup/drop LIST cost scales with namespace/blob count; no parallel discovery |
| RES-6 | Low | Soft-limit backpressure (≤1s, per-flush) delays but can't prevent the hard-limit wedge |
| RES-7 | Low | No per-tenant quota in a shared pool (fairness/DoS) |
| RES-8 | Info | Blob-level scaling is S3-native and fine |

**Verdict:** the memory-side is disciplined (bounded caches, honest LRU). The dangerous ceiling is
**RES-1**: untrimmed root-shard journals under high churn couple **write availability to GC keeping up**,
and the hard limit **rejects writes** rather than degrading gracefully. Landing journal trimming (M-C3)
and surfacing a distance-to-hard-limit metric are the priorities; `root_shards` being a permanent choice
(RES-2) makes churn sizing a one-shot decision operators must get right.

## cas-ad6-s3-lifecycle-cross-region-audit.md

Language: Markdown

# AD-6 — S3 Lifecycle / Object-Expiration / Cross-Region Interaction Audit

Question: CAS assumes an object it wrote **persists unchanged until CAS itself deletes it, and a
`deleteExact` actually destroys it.** Bucket-level features (lifecycle expiration, storage-class
transition, versioning, Object Lock, cross-region replication) violate one or both assumptions. What
breaks? Grounded in `CasObjectStorageBackend.cpp` (plain PUT/GET/HEAD/DELETE, no storage-class or
lifecycle-tag handling; `checkStorePreconditions` only checks GCS versioning) and the mutable control-plane
objects (root shards, `gc/state`, mount lease, owner/epoch — all overwritten via conditional PUT).

CAS sets **no storage class, no lifecycle tags, no object-lock exemptions** — it issues vanilla object
operations and trusts the bucket to be a plain, mutable, durable key-value store.

---

## 1. The two load-bearing assumptions

1. **Persistence**: every blob/manifest/shard exists byte-identical until CAS deletes it (reachability &
 INV-NO-LOSS depend on this).
2. **Mutability + real deletion**: control-plane objects (root shards, `gc/state`, mount lease) can be
 **conditionally overwritten** (`casPut`/`putIfAbsent`), and `deleteExact` **frees the bytes**.

Every finding below is a bucket feature that breaks assumption 1 or 2.

---

## 2. Findings

**LIFE-1 (High — lifecycle _expiration_ rules cause silent data loss / dangling refs).** An S3/GCS
lifecycle rule that **expires (deletes) objects by age** will delete CAS blobs out from under live refs.
CAS has no awareness: the ref still points at the blob → **INV-NO-LOSS violation, dangling blob, part
becomes unreadable** (fsck would classify Dangling — INT-3). Because CAS blobs are *immutable and old by
nature* (cold deduped data can be ancient but still live), an age-based expiration rule is **especially
dangerous** — the oldest objects are often the most-shared, most-referenced blobs. **A CAS bucket must
have NO expiration lifecycle rule.** There is no guard against this today.

**LIFE-2 (High — Object Lock / WORM / retention BREAKS CAS entirely).** CAS's control plane is **mutable**:
root-shard objects are overwritten on every publish/drop (`casPut` = conditional overwrite), and `gc/state`
is CAS-updated every round. **S3 Object Lock (compliance/governance mode), bucket WORM, or a retention
period forbids overwriting/deleting an object** for its retention window. On such a bucket:
- root-shard `casPut` overwrite → **denied** → **all writes fail**;
- `gc/state` update → denied → **GC cannot commit**;
- `deleteExact` → denied → **GC cannot reclaim** (also AD-2 erasure hole).
So a compliance/WORM bucket is **fundamentally incompatible** with CAS's mutable-object model. This is not
checked (`checkStorePreconditions` only inspects GCS versioning). Ironically, users most likely to *want*
WORM (compliance) are exactly those CAS cannot serve this way. **Needs a fail-closed precondition check.**

**LIFE-3 (Med — storage-class transition to archive (Glacier / IA / Intelligent-Tiering archive tiers)
breaks reads).** A lifecycle rule (or Intelligent-Tiering) that transitions cold objects to Glacier /
Deep Archive leaves the object *present* (assumption 1 holds) but **not directly readable** — a ranged GET
returns `InvalidObjectState` until an async restore completes (hours). CAS's read path (`readObjectRanged`)
would **fail the query** on any archived blob, and GC's `deleteExact` still works (delete is allowed), but
the read path has **no restore-and-retry logic**. Cold deduped blobs are the prime transition target →
queries touching cold partitions fail. **A CAS bucket should not auto-transition to non-immediately-readable
classes** unless the read path learns to restore.

**LIFE-4 (Med — cross-region replication (CRR/GRR) creates an un-GC'd shadow bucket).** If the CAS bucket
has cross-region replication, every PUT is copied to the replica bucket, but CAS's `deleteExact` deletes
only in the **source** bucket (unless delete-marker replication is configured, and even then versioning
interacts — OSC-2). So the replica bucket **accumulates objects CAS never reclaims** (cost + AD-2 ERASE-5
erasure hole), and a **failover to the replica bucket** hands CAS a pool whose `gc/state`, mount lease,
owner/epoch, and root-shard tokens (ETags differ across buckets!) may be **inconsistent or stale** — the
token/ETag-based `casPut` conditions were written against source-bucket ETags. **DR failover onto a
replicated CAS bucket is unvalidated and likely token-incoherent.**

**LIFE-5 (Med — versioning / soft-delete / MFA-delete (superset of OSC-2)).** Beyond the GCS-versioning
check: S3 versioning, S3 soft-delete-equivalents, and GCS soft-delete all make `deleteExact` **archive a
noncurrent version instead of freeing bytes** → GC "reclaims" nothing (silent storage bloat + erasure
hole). `checkStorePreconditions` covers **only GCS generation-token versioning**; the equivalent S3
condition (bucket versioning enabled on the CAS bucket) is **not checked** in the S3/Native path. Extend
the precondition check to S3 versioning + GCS soft-delete.

**LIFE-6 (Low — requester-pays / storage-class cost skew).** CAS's dedup value assumes uniform storage
cost; if lifecycle moves blobs to cheaper IA/Glacier tiers, the read-cost/latency model changes silently
(and LIFE-3 read breakage). Purely economic/behavioral, noted.

**LIFE-7 (Info — CAS sets no storage class, so bucket default applies).** All CAS objects land in the
bucket's default storage class. There's no way to say "keep control-plane objects in Standard, blobs in
IA" — no per-object-kind class policy. For a bucket configured entirely Standard with no lifecycle rules
(the intended config), everything is fine.

---

## 3. The safe-bucket contract (what CAS actually requires, undocumented today)

A CAS pool bucket **must**:
- have **no expiration lifecycle rule** (LIFE-1),
- have **no Object Lock / WORM / retention** (LIFE-2),
- have **no transition to archive/Glacier/Deep-Archive** classes (LIFE-3),
- have **versioning OFF** and **soft-delete OFF/duration 0** (LIFE-5, OSC-2),
- treat **cross-region replication as unsupported for failover** (LIFE-4),
- ideally have an **abort-incomplete-multipart-upload** rule (the *one* lifecycle rule that IS safe/helpful — ERR-3).

None of this is enforced or documented beyond the partial GCS-versioning check.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| LIFE-1 | High | Expiration lifecycle rule deletes live blobs → dangling refs / data loss; unguarded |
| LIFE-2 | High | Object Lock / WORM / retention forbids overwriting mutable root-shards & gc/state → CAS writes+GC break entirely; unguarded |
| LIFE-3 | Med | Archive-tier transition (Glacier/IA) leaves blobs unreadable → query failures; no restore-retry |
| LIFE-4 | Med | Cross-region replication accumulates un-GC'd shadow bucket; failover is token-incoherent/unvalidated |
| LIFE-5 | Med | S3 versioning / soft-delete makes DELETE archive not free (OSC-2 superset); only GCS checked |
| LIFE-6 | Low | Storage-class cost/latency skew from tiering |
| LIFE-7 | Info | CAS sets no storage class; bucket default applies; fine for a plain-Standard no-lifecycle bucket |

**Verdict:** CAS silently assumes a **plain, mutable, immediately-readable, non-versioned, no-lifecycle,
no-WORM** bucket. The two highest risks are **LIFE-1 (expiration → data loss)** and **LIFE-2 (Object
Lock/WORM → total incompatibility)**, both **unguarded**. `checkStorePreconditions` should be extended into
a full **safe-bucket precondition check** (expiration rules, object lock, archive transitions, S3
versioning/soft-delete) that fails closed or loudly warns at mount — mirroring the existing GCS-versioning
guard — and the safe-bucket contract above should be documented.

## cas-ad7-protocol-skew-audit.md

Language: Markdown

# AD-7 — Inter-Replica On-Wire Protocol Version-Skew Audit

Question: during a rolling upgrade (one replica on old code, one on new) that share a CAS pool, the
**fetch-by-relink live wire protocol** negotiates between versions. Where can skew mis-decode, silently
fall back, or corrupt? Grounded in `DataPartsExchange.cpp` (relink send/receive, `CA_POOL_UUID_PARAM`,
`CA_RELINK_COOKIE`, `REPLICATION_PROTOCOL_VERSION_*` constants) and `CasManifestCodec.cpp` /
`CasFormat.cpp` (`checkCompatibility`, `format_version`, `G_BUILD`).

This is distinct from the on-S3 format-compat audit (objects at rest): here two **running** replicas of
different versions exchange a **live stream**.

---

## 1. The relink wire, and its version signals

```
Receiver → Sender:  ?content_addressed_pool_uuid=<receiver pool id>   (query param)
Sender → Receiver:  cookie content_addressed_relink = "part_manifest_v1"
                    + writeStringBinary(<encoded PartManifest bytes>)
                    + writeBinary(Int32 metadata_version)
```

Version signals in play:
- `server_protocol_version` cookie + `REPLICATION_PROTOCOL_VERSION_WITH_*` constants (base replication
 stream framing).
- The relink **cookie value** `"part_manifest_v1"` (a wire-format tag).
- The manifest's **internal** `format_version` (`kPartManifestFormatVersion` = 1) + `writer_version`,
 gated on decode by `checkCompatibility` (fail-closed if `> G_BUILD`).
- Pool identity gate: relink only offered when `receiver_pool_uuid == sender.getPoolUUID()`.

---

## 2. Findings

**SKEW-1 (Med — the relink cookie _value_ is NOT validated; only its presence is).** The receiver does:
```cpp
String ca_relink = parse<String>(in->getResponseCookie(CA_RELINK_COOKIE, ""));
if (!ca_relink.empty()) { readStringBinary(sender_manifest_bytes, *in); readBinary(metadata_version, *in); ... }
```
It checks **non-empty**, never that the value equals `"part_manifest_v1"`. Today only v1 exists, so this
is **latent**. But it means a future `"part_manifest_v2"` that changes the **framing** (e.g., adds a field
*before* the manifest bytes, or reorders the `metadata_version`/manifest pair) would be **blindly read as
v1 by an old receiver** → `readStringBinary`/`readBinary` consume the wrong bytes → either an
`assertEOF`/decode failure (safe-ish: exception → part fetch fails, retries) or, worst case, a
**mis-parse** that produces a structurally-valid-but-wrong manifest. The **only** thing protecting against
the worst case is the manifest's internal `format_version`/magic check (SKEW-2). **Recommendation: gate on
the exact cookie value now**, so a v2 sender's payload is treated as "not relinkable" by a v1 receiver and
falls back to byte fetch. This is the single actionable hardening.

**SKEW-2 (Low — the manifest's internal magic + `format_version` fail-closed is the real safety net).**
`decodePartManifest` checks the `"CAPT"` magic and calls `checkCompatibility(format_version)` → a manifest
whose `format_version`/`compatibility` exceeds `G_BUILD` throws `UNKNOWN_FORMAT_VERSION`. So even if
SKEW-1 lets a mis-framed payload through, a *bumped-format* v2 manifest read by a v1 receiver fails
closed → relink returns/aborts → **byte-fetch fallback**. This makes the *common* forward-incompat case
(format bump) safe. The residual risk is a v2 that changes **framing but keeps format_version = 1** (SKEW-1
worst case) — magic would still match and the length-prefixed read could desync. Belt-and-suspenders:
SKEW-1's cookie gate closes it.

**SKEW-3 (Low — fail-closed direction is correct; skew degrades to byte fetch, never to corruption of the
shared pool).** By construction, a failed/aborted relink **publishes nothing** (adopt→revalidate→promote
is fail-closed; a discarded temporary relink part preserves shared blobs). So even a mis-negotiated relink
cannot corrupt the shared pool or another replica — worst case is a failed fetch that retries as a byte
fetch. The safety *posture* is right; SKEW-1 is about avoiding a spurious hard-failure/mis-parse, not a
data-safety hole.

**SKEW-4 (Low — old sender + new receiver is inherently safe).** If the sender is old (never sets the
relink cookie), the new receiver just does a normal byte fetch — no skew surface. Skew only exists when
the **sender is newer** than the receiver (sender offers a wire the receiver may not understand), which is
exactly the SKEW-1 direction. During a rolling upgrade both directions occur, so SKEW-1 matters.

**SKEW-5 (Med — pool-identity gate assumes `getPoolUUID()` semantics are version-stable).** Relink is
gated on `receiver_pool_uuid == sender.getPoolUUID()`. If a future version ever changed how the pool id is
derived/reported, a new replica and an old replica on the **same physical pool** could report **different**
pool-uuid strings → relink never offered → silent fallback to full byte fetch for the entire upgrade
window (perf regression, not correctness). Conversely, an over-broad future match risks a mis-relink
(caught downstream by blob revalidation). The pool id is `PoolMeta::pool_id` (stable), so this is
low-probability, but the contract ("pool id derivation is permanent") should be explicit.

**SKEW-6 (Low — `metadata_version` Int32 framing is a fixed wire contract).** The relink payload appends a
bare `Int32 metadata_version` after the manifest bytes. This is an implicit wire contract with no length
guard beyond `assertEOF`. Any future addition of trailing fields must bump the cookie version **and**
(given SKEW-1) be gated — otherwise `assertEOF` fails on a new sender → hard fetch failure for old
receivers. Reinforces SKEW-1.

**SKEW-7 (Info — base replication protocol versioning is orthogonal and already handled).** The
`REPLICATION_PROTOCOL_VERSION_WITH_*` constants gate the standard part-stream fields (projections,
metadata_version, columns-substreams) with the usual `server_protocol_version` negotiation. Relink rides
*on top* as a cookie + payload; it doesn't alter the base negotiation. No new issue in the base protocol.

---

## 3. Recommendations
1. **SKEW-1 (do this now, cheap)**: validate the relink cookie value exactly (`ca_relink ==
 "part_manifest_v1"`); unknown values → treat as non-relink → byte-fetch fallback. This future-proofs
 the wire against a v2 framing change with zero downside today.
2. Document the relink wire (cookie value + payload framing + `metadata_version` trailer) as a **versioned
 contract**, and require both a cookie-version bump *and* a receiver-side gate for any change.
3. Make the "pool-id derivation is permanent" assumption (SKEW-5) explicit in `PoolMeta`.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| SKEW-1 | Med | Relink cookie value is not checked (only presence) → future v2 framing mis-read by v1 receiver; gate it now |
| SKEW-2 | Low | Manifest magic + `format_version` fail-closed is the real safety net for format bumps |
| SKEW-3 | Low | Skew degrades to byte fetch, never corrupts the shared pool (fail-closed publish-nothing) |
| SKEW-4 | Low | Old-sender/new-receiver is inherently safe; skew risk is only newer-sender |
| SKEW-5 | Med | Relink gated on pool-uuid equality; assumes version-stable pool-id derivation (perf, not safety) |
| SKEW-6 | Low | Bare `Int32 metadata_version` trailer is a fixed wire contract; future additions need a gated cookie bump |
| SKEW-7 | Info | Base replication-protocol versioning is orthogonal and already handled |

**Verdict:** the relink wire is **data-safe under version skew** (fail-closed publish-nothing → byte-fetch
fallback; format bumps caught by the manifest's own compatibility gate). The one real gap is **SKEW-1**:
the cookie version tag is emitted but never checked, so the wire is not yet future-proof against a v2
*framing* change. Gating on the exact cookie value now is a one-line, zero-risk hardening that closes the
only latent mis-parse path.

## cas-alter-merge-mutation-audit.md

Language: Markdown

# CAS — ALTER / Merge / Mutation Support & Bug Audit

Two questions: **(1) enumerate every ALTER supported on a MergeTree table**, and **(2) exhaustively
audit each — plus merges and mutations — against the content-addressed (CAS) backend for bugs.**

Grounded in `AlterCommands.{h,cpp}`, `MutationCommands.h`, `PartitionCommands.h`,
`MergeTreeData::{checkAlterIsPossible,checkAlterPartitionIsPossible,alter}`, `StorageMergeTree::alter`,
`MutateTask.cpp`, `MergeTask.cpp`, `IMergeTreeDataPart::writeMetadataVersion`, and the CAS transaction /
`PartPathParser`.

---

## PART 1 — Enumeration of ALTERs on MergeTree

ALTER splits into **three command families** by execution path:

### A. Table/column metadata ALTERs (`AlterCommand::Type`)
`ADD_COLUMN`, `DROP_COLUMN`, `MODIFY_COLUMN`, `COMMENT_COLUMN`, `RENAME_COLUMN`, `MODIFY_ORDER_BY`,
`MODIFY_SAMPLE_BY`, `REMOVE_SAMPLE_BY`, `ADD_INDEX`, `DROP_INDEX`, `ADD_CONSTRAINT`, `DROP_CONSTRAINT`,
`ADD_PROJECTION`, `DROP_PROJECTION`, `ADD_STATISTICS`, `DROP_STATISTICS`, `MODIFY_STATISTICS`,
`MODIFY_TTL`, `REMOVE_TTL`, `MODIFY_SETTING`, `RESET_SETTING`, `MODIFY_QUERY`, `MODIFY_REFRESH`,
`MODIFY_SQL_SECURITY`, `COMMENT_TABLE`, `MODIFY_DATABASE_SETTING`, `MODIFY_DATABASE_COMMENT`.

### B. Data-rewriting commands → mutations (`MutationCommand::Type`)
`DELETE`, `UPDATE`, `MATERIALIZE_INDEX`, `MATERIALIZE_PROJECTION`, `MATERIALIZE_STATISTICS`,
`MATERIALIZE_TTL`, `MATERIALIZE_COLUMN`, `READ_COLUMN` (incompatible MODIFY COLUMN), `DROP_COLUMN`
(CLEAR), `DROP_INDEX`, `DROP_PROJECTION`, `DROP_STATISTICS`, `RENAME_COLUMN`, `REWRITE_PARTS`,
`APPLY_DELETED_MASK`, `APPLY_PATCHES`, `ALTER_WITHOUT_MUTATION` (metadata pass-through).

### C. Partition ALTERs (`PartitionCommand::Type`)
`ATTACH_PARTITION`, `MOVE_PARTITION`, `DROP_PARTITION`, `DROP_DETACHED_PARTITION`, `FORGET_PARTITION`,
`FETCH_PARTITION`, `FREEZE_PARTITION`, `FREEZE_ALL_PARTITIONS`, `UNFREEZE_PARTITION`,
`UNFREEZE_ALL_PARTITIONS`, `REPLACE_PARTITION` (+ `DETACH` via the `detach` flag). *(Audited in
`cas-mergetree-part-support-audit.md`; summarized below.)*

An ALTER is routed by `commands.isSettingsAlter()` / `isCommentAlter()` (pure metadata, non-replicated),
`isRequireMutationStage()` / `isMetadataOnlyConversion()` (metadata-only vs mutation), else partition op.

---

## PART 2 — How CAS executes the three paths

CAS invariant: **a part = one atomic unit → one manifest → one ref.** Content files are content-addressed
manifest entries; the three **mutable per-part files** (`uuid.txt`, `txn_version.txt`,
`metadata_version.txt`) are stored in the ref's `RefPayload.mutable_files`, **excluded from content
identity** so byte-identical parts still dedup.

### Merges — **SUPPORTED**
`MergeTask` writes the merged part fresh; on CAS the projection sub-parts ride the **parent part's
whole-part transaction** (`projection_uses_parent_transaction = isContentAddressed()`, B58), and the
merged part is published as **one new ref** at `renameTempPartAndReplace` (CAS commits the storage
transaction there). New part name (higher level) ⇒ **no ref overwrite** ⇒ the promote-overwrite leak
(W1) is **not** triggered. Unchanged blobs shared with source parts by content addressing (zero-copy).

### Mutations — **SUPPORTED** (`MutateTask`, three sub-paths)
1. **No rows affected** → `clonePart` (bumped mutation version): a new ref to the same blobs (cheap,
 `part_id` identical). `DataPartStorageOnDiskBase` self-creates one whole-part CA transaction.
2. **mutateSomePartColumns** (partial) → `createHardLinkFrom` for unchanged files (= **copy-by-reference /
 tokenless W-EVIDENCE dep** on CAS) + write changed files + regenerate `columns.txt`/`checksums.txt`;
 all staged into the new part and committed as **one ref**.
3. **mutateAllPartColumns** (full rewrite) → new part written fresh → one ref.

The zero-copy-only hacks (`copy_checksumns`, `always_use_copy_instead_of_hardlinks`) are inert on CAS
(`supportZeroCopyReplication()==false`).

### Metadata-only ALTERs — **SUPPORTED**
Update table metadata + bump the table metadata version. Existing parts are **not rewritten**: column
add/drop/compatible-modify are applied lazily on read via alter-conversions; each part's
`metadata_version.txt` is updated by `IMergeTreeDataPart::writeMetadataVersion`, which wraps a
`beginTransaction()`/`commitTransaction()` around a remove+write of the **mutable** file → on CAS an
`updateRefPayload` one-shot (no manifest republish, no content-file rewrite). Dropped-column blobs stay
referenced by the old manifest until the part is next merged/mutated, then GC reclaims them.

---

## PART 3 — Exhaustive per-ALTER audit

| ALTER | Path | CAS mechanism | Verdict |
|---|---|---|---|
| ADD COLUMN | metadata | bump metadata_version (mutable/per-ref); column materialized on read | ✅ |
| ADD COLUMN … MATERIALIZE | mutation | new part (write column) | ✅ |
| DROP COLUMN | metadata (lazy) | metadata bump; old blobs reclaimed on next merge/mutation | ✅ |
| CLEAR COLUMN IN PARTITION | mutation | new part without the column data | ✅ (rejected only on UNIQUE KEY) |
| MODIFY COLUMN (compatible) | metadata (`isMetadataOnlyConversion`) | metadata bump; conversion on read; **no in-place columns.txt rewrite on existing parts** | ✅ |
| MODIFY COLUMN (incompatible) | mutation (`READ_COLUMN`) | new part, changed column rewritten, rest hardlinked=copy-by-ref | ✅ |
| RENAME COLUMN | metadata or mutation | mutation renames entries via `createHardLinkFrom(old→new)` → new manifest names, same blobs | ✅ |
| COMMENT COLUMN / COMMENT TABLE | metadata (comment alter) | table metadata only | ✅ |
| MODIFY ORDER BY | metadata | metadata only (rejected on UNIQUE KEY) | ✅ |
| MODIFY / REMOVE SAMPLE BY | metadata | metadata only | ✅ |
| ADD INDEX | metadata | metadata only; files built on MATERIALIZE/merge | ✅ |
| MATERIALIZE INDEX | mutation | new part with index files | ✅ |
| DROP INDEX | metadata/mutation | metadata; index files dropped on next merge or via mutation → new part | ✅ (see B-2 below) |
| ADD / DROP CONSTRAINT | metadata | pure metadata (check exprs) | ✅ |
| ADD PROJECTION | metadata | nested `.proj/` keys; parent-transaction on rebuild | ✅ (rejected on UNIQUE KEY / deduplicate_merge_projection_mode=throw) |
| MATERIALIZE PROJECTION | mutation | new part; projection sub-part rides parent whole-part txn (B58) | ✅ |
| DROP PROJECTION | metadata/mutation | metadata; projection removed on next merge or via mutation → new part | ✅ |
| ADD / DROP / MODIFY STATISTICS | metadata (+ MATERIALIZE mutation) | metadata; stats files via mutation → new part | ✅ |
| MODIFY TTL / REMOVE TTL | metadata (+ MATERIALIZE TTL mutation) | metadata bump; MATERIALIZE TTL rewrites parts → new parts | ✅ |
| MODIFY SETTING / RESET SETTING | settings alter | table metadata only (RESET storage_policy/disk rejected only on UNIQUE KEY) | ✅ |
| MODIFY QUERY / MODIFY REFRESH | metadata (MV) | no MergeTree part data | ✅ (N/A to parts) |
| MODIFY SQL SECURITY | metadata | table metadata only | ✅ |
| ALTER DELETE | mutation | new parts (rows filtered) | ✅ |
| ALTER UPDATE | mutation | new parts (values rewritten) | ✅ |
| DELETE FROM (lightweight) | patch/deleted-mask mutation | patch part or `_row_exists`; new/patch part | ✅ |
| APPLY DELETED MASK / APPLY PATCHES | mutation | new part | ✅ |
| **Partition ops** | partition | allow-list: DROP/DROP_DETACHED/FORGET/ATTACH/REPLACE/MOVE(same-disk→table)/FETCH/FREEZE*/UNFREEZE* via whole-part txn | ✅ allow-listed / 🚫 else fail-closed |

**Global ALTER gates (not CAS-specific but relevant):** immutable disks reject non-settings ALTERs
(`!supportsHardLinks`); UNIQUE-KEY tables reject ALTER DELETE/UPDATE, MATERIALIZE/CLEAR of UK columns,
MODIFY ORDER BY; text index requires a feature flag. CAS disks `supportsHardLinks()==true` (hardlink =
copy), so none of the immutable-disk gates fire on CAS. **There is no CAS-specific gate on any
column/index/statistics/TTL/setting ALTER** — only the partition allow-list.

---

## PART 4 — CAS-specific merge/mutation bug analysis

| # | Concern | Analysis | Verdict |
|---|---|---|---|
| M1 | **W1 promote-overwrite leak** on merge/mutation | merges & mutations always mint a **new part name** (level/mutation bump) → publish to a fresh ref, never overwrite an existing committed ref → **W1 not triggered** by the merge/mutate path | ✅ not reachable here |
| M2 | **Copy-forward evidence dep vs GC** | mutation hardlink records a **tokenless W-EVIDENCE** dep on the source blob; if the source part is dropped + GC condemns→deletes the blob before the new part's `promote`, `promote` re-proves via `observeAndAdmit` → `copyForwardFromCondemned` re-materializes | ✅ handled by write protocol (relies on its robustness) |
| M3 | **metadata_version.txt update on a committed part** | `writeMetadataVersion` = beginTransaction + remove+write of a **mutable** file + commit → CAS `updateRefPayload` one-shot; manifest untouched, no B21 one-file-tree | ✅ (this is why the file is mutable) |
| M4 | **Merge/mutate partial-commit atomicity** | each result part is one whole-part transaction; a multi-part mutation commit is per-ref (no cross-ref atomic publish, DUR1/C-U5) — a crash mid-commit can leave some result parts published, some not | ⚠ inherits DUR1 (partial on crash; MergeTree tolerates missing parts) |
| M5 | **Reader vs merge/mutate cleanup (source part drop)** | after merge/mutation the source parts become Outdated then dropped; a concurrent SELECT holding no CAS blob pin can hit the R1/X1 dangle if GC condemns→deletes the source blob mid-query | ⚠ inherits R1/X1 (read-side pin gap) |
| M6 | **Fencing on merge/mutate writes** | merge/mutate publishes go through the same shard CAS as INSERT; a paused/superseded writer's promote is fenced only by content token, not writer_epoch | ⚠ inherits J1 (zombie-writer window) |
| M7 | **Unchanged-part clone (no-op mutation)** | `clonePart` → new ref to same blobs; identical content ⇒ same part_id ⇒ effectively free; one CA transaction | ✅ |
| M8 | **RENAME COLUMN file rename** | `createHardLinkFrom(old→new)` re-keys the entry under the new name pointing at the same blob in the new manifest | ✅ |

**No new merge/mutation-specific bug** was found. The concerns that apply (M4/M5/M6) are **inherited**
from the previously documented general findings (DUR1 partial commit, R1/X1 read-side pin, J1 fencing) —
they are not introduced by the ALTER/merge/mutate machinery, they simply also apply to the parts it
produces.

---

## PART 5 — Summary

**Are merges supported?** **Yes** — the merged part is written through a whole-part CA transaction and
published as one new ref; projection sub-parts ride the parent transaction (B58). Content addressing
makes shared blobs zero-copy across the source and merged parts.

**Are mutations supported?** **Yes** — all three mutate sub-paths (clone-on-no-change,
hardlink-unchanged+rewrite-changed, full-rewrite) resolve to a **new whole-part ref**; hardlink =
copy-by-reference so unchanged columns cost nothing to carry forward.

**ALTER behavior:**
- **Metadata-only** (ADD/DROP COLUMN, compatible MODIFY, COMMENT, SETTINGS, TTL, ORDER BY, index/
 projection/statistics *declarations*): update table metadata + bump each part's **mutable**
 `metadata_version.txt` (per-ref `updateRefPayload`); **existing parts' content files are never
 rewritten in place**; column changes apply lazily on read. Clean fit for CAS.
- **Mutation-triggering** (ALTER DELETE/UPDATE, incompatible MODIFY COLUMN, MATERIALIZE *, CLEAR,
 lightweight DELETE): produce **new parts** via `MutateTask`. Fully supported.
- **Partition ops**: allow-listed set supported via whole-part transactions; everything else is
 **fail-closed** (`SUPPORT_IS_DISABLED`) to avoid the per-file-autocommit corruption mode.

**What's broken / to watch:**
- Nothing in the **normal ALTER → merge → mutate lifecycle is broken** on CAS.
- The applicable risks are **inherited**, not new: **M4** (multi-part commit not crash-atomic, DUR1),
 **M5** (SELECT vs GC delete of dropped source parts, R1/X1), **M6** (zombie-writer fencing on
 merge/mutate promotes, J1).
- **From the partition/backup surface** (separate audit): BACKUP is Atomic-DB-only, cross-disk
 MOVE PARTITION is unverified, non-allow-listed partition ops fail closed.

Net: the ALTER/merge/mutation surface is **broadly and correctly supported** on CAS, precisely because
the design funnels every part-producing operation through the single whole-part transaction and keeps
the three genuinely-mutable files out of the content-addressed manifest. The only exposure is the
already-known cross-cutting findings (J1 fencing, R1/X1 read pin, DUR1 multi-part commit), which surface
here as the merge/mutate outputs inherit them.

## cas-bc1-offset-overflow-audit.md

Language: Markdown

# BC-1 — Integer / Offset Arithmetic & Overflow Audit

Static read of the actual arithmetic on the read path: `getBlobViewPlan` / `readBlobPayload`
(`ContentAddressedMetadataStorage.cpp` ~968–1005), `ReadBufferFromFileView.cpp` (bounds, seek,
resize), and the envelope size validation (`CasEnvelope.cpp` decode ~236–267). This is the bug class
(offset/length under/overflow, off-by-one) prior audits skipped.

---

## 1. The offset model

A blob is `[CHCA envelope header | payload]`. A `ManifestEntry` → `BlobLocation{key, offset, length}`,
where `offset` = start of this file's payload window inside the blob (= header length for a one-file
blob) and `length` = payload length. Reads:
- `plan.object = StoredObject(key, path, offset + length)` ← object "size" is the readable extent
- `plan.payload_offset = offset`, `plan.payload_end = offset + length`
- `ReadBufferFromFileView(impl, path, left_bound=offset, right_bound=offset+length)` presents
 `[offset, offset+length)` as a standalone file based at 0.

---

## 2. Findings

**BC1-1 (Med — envelope size validation can be bypassed by `logical_size` overflow).** Decode computes
`expected_object_size = static_cast<uint64_t>(header_len) + h.logical_size` and checks it equals the real
`object_size`. `logical_size` is read straight from the (attacker/corruption-controlled) header before
this check. Because the addition is `uint64_t`, a crafted `logical_size` near `UINT64_MAX` **wraps** and
can be made to equal the true `object_size`, passing the consistency check. The bogus `logical_size` then
flows into `length`/`payload_end` used for ranged reads. Downstream S3 clamps the GET to the real object,
so the practical outcome is a short/again-inconsistent read rather than an OOB memory read — **but the
size-consistency invariant that is *supposed* to fail closed here does not for this input.** Add an
explicit `logical_size <= object_size` (and `header_len <= object_size`) guard *before* the addition.

**BC1-2 (Low — `resizeWorkingBuffer` clamp relies on size_t-underflow-then-signed-cast).**
```cpp
size_t extra_bytes = file_offset_of_buffer_end - getRightBound();   // guarded > 0
size_t new_size = std::max(static_cast<Int64>(working_buffer.size() - extra_bytes), static_cast<Int64>(0));
```
`working_buffer.size() - extra_bytes` is computed in **size_t**; if `extra_bytes > size` it underflows to
a huge value, and correctness depends on that huge value being `> 2^63` so the `Int64` cast makes it
negative and `max(.,0)` yields 0. It *does* work for all realistic magnitudes (both operands < 2^63), but
it's **fragile two's-complement-dependent arithmetic**; a straightforward `new_size = size > extra ? size
- extra : 0` would be obviously correct.

**BC1-3 (Low — `SEEK_CUR` with negative offset underflows before the downstream bound check).** In
`seek`, `new_pos = current_position + off` with `new_pos` a `size_t` and `off` a signed `off_t`. A
negative `off` larger in magnitude than `current_position` underflows `new_pos` to a huge value; the code
then relies on `impl->seek(huge)` returning a value that the subsequent `result < left_bound || result >
right_bound` check rejects. Correctness therefore depends on the impl reporting the requested (huge)
position rather than clamping/succeeding. Safe with `ReadBufferFromS3`, but it's an implicit contract on
the impl, not a local guard.

**BC1-4 (Low — plan trusts manifest `offset`/`length` without validating against the real object size).**
`getBlobViewPlan` builds `payload_end = offset + length` directly from the `ManifestEntry` with no check
that `offset + length <= actual blob object size` (it never HEADs at plan time). A corrupt manifest with
oversized `offset`/`length` yields a plan that only fails later at the S3 GET (confusing error) rather
than a crisp fail-closed at resolve time. `offset + length` is itself an unguarded `uint64` addition
(overflow theoretically possible with a corrupt manifest, though object sizes are S3-bounded).

**BC1-5 (Info — the FileView bound checks and exception-safe buffer swap are correct ✅).**
`setReadUntilPosition` rejects `left_bound + position > right_bound`; `seek` rejects results outside
`[left_bound, right_bound]`; and `executeWithOriginalBuffer` restores the buffer swap **on exception**
(explicitly, with a comment explaining that not doing so would serve wrong bytes). These are the
load-bearing correctness points for windowed reads and they are handled properly. The envelope decode
also bounds `header_len` (`invalid header_len` / `MAX_HEADER_LEN`) and rejects unknown critical TLVs.

**BC1-6 (Info — 64-bit only; no 32-bit truncation concern in practice).** All offset/size arithmetic is
`size_t`/`uint64_t`; ClickHouse servers are 64-bit, so `size_t` truncation of a >4 GiB offset is not a
real-world path. Noted so the audit is explicit rather than silent.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| BC1-1 | Med | Envelope `header_len + logical_size == object_size` check bypassable via uint64 overflow of a crafted `logical_size`; validate magnitudes before adding |
| BC1-2 | Low | `resizeWorkingBuffer` clamp relies on fragile size_t-underflow → signed-cast → max(.,0) |
| BC1-3 | Low | `SEEK_CUR` negative-offset underflow caught only by downstream impl-dependent bound check |
| BC1-4 | Low | Blob view plan trusts manifest offset/length; no validation vs real object size at resolve time |
| BC1-5 | Info | FileView bound checks + exception-safe buffer-swap restore are correct ✅ |
| BC1-6 | Info | 64-bit-only arithmetic; no practical 32-bit truncation path |

**Verdict:** the read-window machinery is **basically sound** — the one substantive item is **BC1-1**, a
real (if hard-to-hit) fail-closed gap where an overflowing `logical_size` defeats the envelope's own
size-consistency check. The rest are fragile-but-currently-correct patterns worth tidying. This is the
first audit that actually traced the arithmetic rather than the protocol, and it found one genuine
validation hole the narrative audits missed.

## cas-bc2-writebuffer-spill-audit.md

Language: Markdown

# BC-2 — Write-Buffer Spill-Path Audit

Static read of `ContentAddressedWriteBuffers.{h,cpp}` — the path prior audits never opened.
`CaContentWriteBuffer` spills a content part file to a local scratch temp file while streaming a
`HashingWriteBuffer` (CityHash128), then hands `(hash_hex, size, temp_path)` to the transaction, which
uploads the temp file to S3 post-precommit. `CaInlineWriteBuffer` accumulates small bytes in memory.

---

## 1. Lifecycle (as coded)

```
ctor: create_directories(temp_dir); temp_path = temp_dir + "/" + getRandomASCIIString(32) + ".tmp";
      temp_file = WriteBufferFromFile(temp_path); hashing = HashingWriteBuffer(*temp_file);
nextImpl: hashing->write(working_buffer, offset())
finalizeImpl: next(); size=count(); hash=hashing->getHash(); hashing->finalize(); temp_file->finalize();
              on_finalized(hash_hex, size, temp_path); temp_ownership_transferred = true;
dtor: cancel(); if(!temp_ownership_transferred) removeTempFile();
cancelImpl: hashing->cancel(); temp_file->cancel(); removeTempFile();
```

Ownership transfer (B188): after `on_finalized`, the transaction owns the temp file and uploads/cleans it;
`cleanupPendingTempFiles()` removes it at commit end and, defensively, in the transaction destructor
(verified: `~ContentAddressedTransaction` calls `cleanupPendingTempFiles()` on both paths).

---

## 2. Findings

**BC2-1 (Med — the uploaded blob is never verified to match the hash it was keyed by).** The blob key is
the CityHash128 computed **while spilling** to the temp file. The transaction later **re-reads that temp
file** and PUTs its bytes as the blob whose key is that hash. Nothing re-hashes the uploaded bytes, and
the read path never re-verifies either (INT-1). So if the temp file is corrupted **between hashing and
upload** — a page-cache bit flip, a bad scratch disk, a truncation from a full scratch FS not surfaced as
an error — CAS uploads content that **does not match its key**, silently, and dedup/relink will later hand
those wrong bytes to every ref that adopts the key. The window is small (same process, usually same page
cache) but the failure is silent and permanent. A cheap mitigation: hash-verify on upload, or upload
*from* the hashing buffer rather than re-reading an unverified temp file.

**BC2-2 (Med — scratch temp file is `finalize()`d but never `fsync`ed before it's read for upload).**
`finalizeImpl` calls `temp_file->finalize()` (flush to OS) but **not** `temp_file->sync()` (the `sync()`
method exists and calls `temp_file->sync()`, but finalize doesn't invoke it). This is *fine for
durability* (the blob's durability comes from S3, and an uncommitted transaction is discardable), **but**
it interacts with BC2-1: if the OS/page cache loses/short-writes buffered bytes under memory pressure or a
scratch-FS error that `finalize()` didn't surface, the re-read for upload sees different bytes than were
hashed. Combined with BC2-1, "no fsync + no re-verify" means the write path trusts local scratch integrity
end-to-end with no check.

**BC2-3 (Low — scratch-FS-full / write errors surface only through `WriteBufferFromFile`).** The temp file
is a real local file; a full scratch FS or I/O error throws from `temp_file` writes/finalize. That
propagates up (build fails, no commit) — fail-closed, good. But there is **no pre-flight scratch space
check** and no dedicated error class; a scratch-full during a large wide-part INSERT fails the whole insert
late (after buffering) with a generic write error. `scratchPath()` sizing is an undocumented operational
requirement (must hold the largest in-flight part's files).

**BC2-4 (Low — `getRandomASCIIString(32)` collision safety is assumed, not enforced).** Temp uniqueness
relies on 32 random ASCII chars. Collision probability is negligible **if** the RNG is well-seeded and
thread-safe; two concurrent spills colliding would have two builds writing the **same** temp file →
corruption/interleave. The code assumes `getRandomASCIIString` is safe (it uses ClickHouse's thread-local
RNG); worth an explicit note since a bad RNG here is a silent-corruption vector. A PID/counter component
would make it collision-proof by construction.

**BC2-5 (Info — cleanup-on-throw is correct ✅).** RAII is solid: `~CaContentWriteBuffer` calls `cancel()`
and removes the temp file unless ownership transferred; the inline-overflow path in `writeFile` uses
`SCOPE_EXIT` to drop its temp on `stageBlobPartFile` throw; and the transaction destructor defensively
runs `cleanupPendingTempFiles()` whether or not it committed. No temp-file leak on the exception paths I
traced.

**BC2-6 (Info — `CaInlineWriteBuffer` accumulates in memory; bounded by INLINE_CAP only at finalize).** It
appends all writes to an in-memory `std::string` and only at finalize does the caller decide inline
(≤ INLINE_CAP) vs spill-to-blob (the `writeFile` overflow branch). So a file wrongly routed to the inline
buffer holds its **entire** contents in memory until finalize; for the intended tiny mutable/metadata
files this is fine, but the safety net for an oversized inline candidate is *post-hoc* (after full
buffering), not streaming.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| BC2-1 | Med | Uploaded blob never verified against the hash it was keyed by; scratch corruption → silent wrong-bytes blob |
| BC2-2 | Med | Scratch temp file finalized but not fsynced before re-read for upload; compounds BC2-1 |
| BC2-3 | Low | Scratch-FS-full/error fails the insert late; no pre-flight check; scratch sizing undocumented |
| BC2-4 | Low | Temp-file uniqueness relies on random string; collision would corrupt; add PID/counter |
| BC2-5 | Info | Cleanup-on-throw (RAII + dtor + SCOPE_EXIT) is correct ✅ |
| BC2-6 | Info | Inline buffer holds full contents in memory; oversized-candidate spill is post-hoc |

**Verdict:** RAII/cleanup is genuinely well done, but the spill path has a real **integrity gap
(BC2-1/BC2-2)**: CAS hashes bytes into a key, then trusts an un-fsynced local temp file to still hold
exactly those bytes at upload, with no verification on write **or** read (INT-1). The whole content-address
guarantee assumes local scratch never silently corrupts between hash and PUT. Verifying the upload against
its key would make the write path self-checking — the highest-value fix here and a natural pair to INT-1.

## cas-bc3-exception-safety-audit.md

Language: Markdown

# BC-3 — Exception-Safety & Partial-State Cleanup Audit

Static read of what happens when an exception is thrown midway through
`build → precommit → upload → promote → commit`. Grounded in `ContentAddressedTransaction::commit`
(~323–368, compensating rollback), `publishStaging`, `cleanupPendingTempFiles`, the transaction
destructor (~85–94), and the write-buffer RAII (BC-2).

---

## 1. The commit sequence and its guards (as coded)

- **`commit()`** iterates staged parts, calls `publishStaging(ns, ref, st)` for each, and records refs it
 created. On **any** exception it runs a **compensating rollback**: best-effort `dropRef` of only the
 refs *this* commit created (never pre-existing refs), then rethrows. `committed=true` and
 `cleanupPendingTempFiles()` run only on success.
- **`publishStaging`** is **precommit-first (B188)**: blobs upload *after* precommit, the ref publishes
 last. A throw before the ref-publish leaves uploaded blobs as **unreferenced debris** (GC-reclaimable),
 never a dangling ref.
- **Destructor** always calls `cleanupPendingTempFiles()` (both committed and uncommitted paths) — so
 scratch temp files never leak on the exception path. An uncommitted transaction's uploads are
 min_active-spared debris (abandoned, later reclaimed).

---

## 2. Findings

**BC3-1 (Med — multi-part commit is not atomic; a mid-loop throw yields a durable PARTIAL commit).** The
code is explicit (comment B122): "there is no multi-ref atomic publish." If a transaction stages parts
A, B, C and `publishStaging(B)` throws after A already published, the rollback best-effort `dropRef`s A.
But the rollback is **best-effort**: "a ref we cannot unpublish becomes unreferenced debris ... never mask
the original failure." So if the rollback `dropRef(A)` *also* throws (e.g., the same S3 outage that failed
B), **A remains durably published while the transaction reports failure** → the durable pool diverges from
the disk layer's all-or-nothing contract. For MergeTree this is rare (parts have unique names, most commits
are single-part), but multi-part transactions (e.g. some ATTACH/REPLACE flows) can hit it. This is the
**concrete code behind the DUR1 finding** — now confirmed to be a *deliberate, documented* wiring-layer
compromise, not an invariant violation, but still a real partial-commit window under compounded failure.

**BC3-2 (Low — `updateRefPayload` one-shots are intentionally NOT rolled back).** Mutable-file updates on
an already-committed part (e.g. `metadata_version.txt`, `txn_version.txt`) are "individually durable by
design and deliberately NOT rolled back." So a transaction that both publishes a new ref *and* updates a
committed part's payload, then throws, will roll back the new ref but **leave the payload update durable**.
This is correct for the mutable-file autocommit contract, but it means "transaction failed" does **not**
imply "no durable effect" — a subtlety callers (and MVCC txn_version, TXN-2) must not rely on.

**BC3-3 (Low — rollback ordering is unspecified vs partial visibility).** During the rollback window,
already-published refs A are **live and readable** by concurrent readers/GC between their publish and their
compensating `dropRef`. A concurrent query could observe A, or GC could begin reasoning about A, before the
rollback unpublishes it. No correctness violation (each ref is independently valid), but it means an aborted
transaction can be **transiently observable** — a mild atomicity/visibility surprise for readers.

**BC3-4 (Info — precommit-first ordering makes the throw-safe story genuinely good ✅).** The
upload-after-precommit + publish-last ordering means the dangerous states are debris (uploaded-but-
unreferenced blobs, orphaned precommit manifests), all of which are GC/sweep-reclaimable and never a
dangling live ref. This is the right invariant ordering (INV: reachability-before-content on the way in,
content-after-reachability on the way out) and it holds on the exception paths.

**BC3-5 (Info — temp-file & buffer RAII is complete ✅).** Cross-checked with BC-2: write-buffer dtors +
`SCOPE_EXIT` on the inline-overflow spill + the transaction destructor's unconditional
`cleanupPendingTempFiles()` mean no local scratch leaks on any throw path traced. Best-effort `noexcept`
cleanup functions (`cleanupPendingTempFiles`, `removeTempFile`) correctly swallow errors so they can't
mask the original exception.

**BC3-6 (Low — best-effort `catch(...)` swallowing can hide operational signal).** The rollback's inner
`catch (...) {}` (NOLINT bugprone-empty-catch) intentionally discards rollback failures to preserve the
original error. Correct for control flow, but it means a **failed rollback (→ durable partial commit,
BC3-1) is silent** — no metric, no distinctive log at that point. Given BC3-1's consequence, the failed-
rollback case deserves at least a WARNING/metric so operators can detect a divergence.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| BC3-1 | Med | Multi-part commit non-atomic; compounded-failure rollback is best-effort → durable partial commit possible (DUR1, in code) |
| BC3-2 | Low | `updateRefPayload` one-shots not rolled back → "commit failed" ≠ "no durable effect" |
| BC3-3 | Low | Already-published refs are transiently observable during the rollback window |
| BC3-4 | Info | Precommit-first ordering makes dangerous mid-states debris, never dangling refs ✅ |
| BC3-5 | Info | Temp-file/buffer RAII cleanup on throw is complete ✅ |
| BC3-6 | Low | Failed-rollback is silently swallowed; no signal for the resulting partial commit |

**Verdict:** exception-safety for **resources** (temp files, buffers, orphaned uploads) is genuinely
well-engineered — everything dangerous degrades to GC-reclaimable debris. The real gap is
**transactional atomicity across multiple refs (BC3-1)**: it's a documented compromise, but under a
compounded S3 failure it can leave a durable partial commit, and that outcome is **silent** (BC3-6).
Surfacing failed-rollback and, longer term, narrowing multi-ref commits are the action items.

## cas-bc4-protobuf-decode-audit.md

Language: Markdown

# BC-4 — Protobuf Decode-Hazard Audit

Static read of the one protobuf surface in CAS: `CasRootShardCodec.cpp` (`decodeRootShard` ~153–204,
`encodeRootShard`). Root shards are the *mutable, CAS-by-token* control-plane objects (all live refs +
the owner-change journal for a namespace). Manifests and envelopes are hand-rolled binary (BC-1), so this
is the only Protocol-Buffers attack surface. Question: recursion/size limits, unknown-field handling,
malloc bombs, determinism.

---

## 1. How decode works (as coded)

```cpp
if (data.empty()) throw CORRUPTED_DATA;
Cas::Proto::RootShardManifest msg;
if (!msg.ParseFromArray(data.data(), (int)data.size())) throw CORRUPTED_DATA;   // parse FIRST
if (msg.header().magic() != magicFor(Manifest)) throw CORRUPTED_DATA;           // validate AFTER
checkCompatibility(msg.header().compatibility_version(), "root shard");
... copy refs map, journal repeated, mutable_files map into the RootShard struct ...
```
Encode uses `CodedOutputStream` with **`SetSerializationDeterministic(true)`** (sorts `map<>` entries).

---

## 2. Findings

**BC4-1 (Med — no max-object-size guard before GET + full-buffer `ParseFromArray`).** The shard object is
HEAD+GET into memory in full, then `ParseFromArray` parses the whole buffer. CAS's write side bounds shard
bodies (`manifest_hard_limit` = 64 MiB), but **nothing on the read/decode side enforces a maximum object
size** before allocating and parsing. A corrupt or **maliciously planted** oversized object (any pool
participant can write — SEC-3: no intra-pool authorization) forces an unbounded read + parse →
**allocation/OOM DoS**. Protobuf's own default total-byte limit (~2 GiB) is the only backstop, and it's
far above CAS's own 64 MiB write ceiling. Recommend a decode-time size cap tied to `manifest_hard_limit`
(reject before GET via the HEAD size).

**BC4-2 (Med — additive protobuf fields are silently DROPPED on re-encode by an older build → data loss
in mixed-version).** Decode copies fields **out of** the protobuf `msg` into the `RootShard` struct;
`encodeRootShard` builds a **fresh** `msg` from the struct. So any field a *newer* build added that an
older build's struct doesn't know is **not preserved** — the older build, when it mutates the shard
(publish/drop under flat-combining), re-encodes without it, **permanently dropping the new field's data**.
`checkCompatibility` protects only against **breaking** bumps (`compatibility_version > G_BUILD` →
fail-closed); an **additive** change that keeps `compatibility_version` unchanged would let an old node
parse, mutate, and silently strip the new data. This is the classic proto3 "unknown fields aren't
round-tripped through a struct mapping" hazard, and here it applies to the **live control plane** during a
rolling upgrade. Ties to the upgrade-compat audit but is a concrete codec-level mechanism.

**BC4-3 (Low — parse happens before magic/compat validation).** `ParseFromArray` runs over fully
untrusted bytes *before* the magic and `compatibility_version` checks. So the protobuf wire-format parser
(and its allocations) is exposed to arbitrary bytes first; magic/compat only gate *after* a successful
parse. Standard for protobuf, and `ParseFromArray` returns false on malformed input (→ CORRUPTED_DATA,
fail-closed), but combined with BC4-1 the pre-validation parse is where a resource attack lands.

**BC4-4 (Low — large `refs`/`journal`/`mutable_files` counts scale memory/CPU with object size).** The
`refs` map, repeated `journal`, and per-ref `mutable_files` maps are all copied into heap structures
(`root.refs[name] = ...`). A large (but < protobuf limit) object yields large maps; decode is O(object)
memory and CPU. Bounded by BC4-1's (missing) size cap. Recursion is **not** a concern — the schema is
shallow/fixed-depth, so protobuf's default recursion limit (100) is irrelevant here.

**BC4-5 (Info — determinism is correctly forced on encode; corrects an earlier speculation).** Encode sets
`SetSerializationDeterministic(true)`, so `map<>` fields serialize in sorted order → stable bytes (golden
tests). Note: this does **not** matter for correctness because the root shard is **CAS-by-token (ETag),
not content-addressed** — the code says so. (This also retires the AD-1 worry that protobuf map ordering
could affect a content hash: root shards aren't hashed for identity.)

**BC4-6 (Info — journal semantic validation is present and fail-closed ✅).** Decode rejects a
`RootOwnerEvent` that has neither binding nor tombstone, and `decodeManifestRef` validates
`manifest_ordinal` range. So structurally-valid-but-semantically-meaningless events fail closed rather
than folding to silent no-ops.

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| BC4-1 | Med | No decode-time max-object-size cap before GET+ParseFromArray → OOM DoS from a corrupt/planted oversized shard |
| BC4-2 | Med | Additive protobuf fields dropped on re-encode by older build → silent control-plane data loss in mixed-version |
| BC4-3 | Low | Parse runs over untrusted bytes before magic/compat validation |
| BC4-4 | Low | refs/journal/mutable_files decode is O(object) memory/CPU; bounded only by (missing) size cap |
| BC4-5 | Info | Deterministic serialization forced; irrelevant to correctness (shard is CAS-by-token, not content-addressed) ✅ |
| BC4-6 | Info | Journal event semantic validation is fail-closed ✅ |

**Verdict:** the protobuf path is **functionally careful** (fail-closed parse, semantic validation, forced
determinism) but has two robustness gaps a fuzzer/adversary would find: **BC4-1** (no size cap before
parse → OOM) and **BC4-2** (additive-field loss on old-build re-encode → mixed-version control-plane data
loss). Cap decode size at the HEAD stage and either forbid additive changes without a compat bump or
carry-through unknown fields. The hand-rolled manifest/envelope codecs (BC-1) are actually *better*
hardened (explicit length bounds) than this protobuf path.

## cas-bc5-wide-part-read-correctness-audit.md

Language: Markdown

# BC-5 — Read Correctness of a Realistic (Wide) Part Audit

Static read of the full read composition for a wide part: `DiskObjectStorage::prepareRead` (~808–918:
`needGather` → `storage->prepareRead` (+cache) → page cache → async prefetch → `needFileView`),
`getBlobViewPlan` / `getStorageObjects` (the two different size semantics), inline vs blob placement, and
mark-bound propagation (`setReadUntilPosition`). Question: does a wide part actually return the *right
bytes*?

**Honesty note (self-critique):** unlike the narrative audits, reads here **are** exercised by
`tests/integration/test_content_addressed_s3` and gtests (`gtest_cas_inline_placement`,
`gtest_cas_store`, `gtest_ca_wiring`). So this is "trace the composition for correctness hazards," not
"nobody tested reads."

---

## 1. The wide-part read model (as coded)

- A wide part = one file per column (`col.bin`, `col.mrk*`) + `primary.idx` + metadata. In CAS **each
 logical file is its own blob** `[envelope | payload]` (or an inline manifest entry for small files).
- Per file, `getBlobViewPlan` → `StoredObject(blob_key, path, size = offset+length)` +
 `payload_offset/payload_end`. The pipeline reads the blob and the **FileView** clamps to
 `[offset, offset+length)`, presenting the payload as a standalone file based at 0.
- Marks (`.mrk`) address offsets **within the logical (payload) file**; because the FileView rebases to 0,
 a mark offset maps directly to a view offset. `MergeTreeReaderStream` right-mark bounds →
 `setReadUntilPosition(pos)` → `read_until_position = left_bound + pos` (B116).

---

## 2. Findings

**BC5-1 (Info — one file = one blob = one payload ⇒ compression-block/blob-boundary is a NON-issue ✅).**
The classic object-store hazard (a compression block straddling two backing objects) **cannot occur**:
each column file is a single contiguous payload inside a single blob. There is no cross-blob compression
block, no gather-seam inside a file. `needGather` runs but joins a single object (no-op). So decompression
and mark seeking operate exactly as on a plain file. This is a genuinely clean design point.

**BC5-2 (Med — two different "size" semantics for the same file; correctness depends on ALL reads going
through `prepareRead`+FileView).** `getStorageObjects(path)` returns size = **`location.length`** (payload
only), while `getBlobViewPlan` returns a `StoredObject` sized **`offset+length`** (envelope+payload) that
the read pipeline then windows. So the *size a consumer sees* and the *extent the reader reads* differ by
the envelope header. This is intentional and guarded (mutable/in-manifest files return an empty-key
placeholder so a bypassing reader "fails loudly"), **but** any code path that (a) gets a blob-backed
StoredObject via `getStorageObjects` and (b) reads it **without** the `prepareRead` FileView stage would
read `offset+length` bytes starting at 0 — i.e., **the envelope header as if it were data**. The safety
rests entirely on the invariant "all byte reads go through `DiskObjectStorage::prepareRead`'s CA branch."
That invariant holds today, but it's a **structural fragility**: a future reader that constructs a buffer
from `getStorageObjects` directly (as is valid on plain S3 disks) would silently read wrong bytes on CAS.

**BC5-3 (Low — inline vs blob split is decided at write finalize; mixed placement within a part is
normal).** Small files (≤ INLINE_CAP: often `primary.idx`, `columns.txt`, small `.mrk`) are stored
**inline** in the manifest and served from memory (`prepareInManifestRead` → `ReadBufferFromOwnMemoryFile`)
**bypassing** the blob/FileView path entirely; large files go through blobs. So a single wide part read
mixes two read paths. Both are individually correct, but it means read-path coverage must exercise **both**
per part (a part with all-large columns never hits the inline path and vice-versa). The `inline == blob`
hash equivalence keeps dedup consistent across the split.

**BC5-4 (Low — mark right-bound propagation is correct but relies on impl rebase discipline).** B116:
`MergeTreeReaderStream` sets a right-mark bound that becomes `setReadUntilPosition(left_bound + pos)`,
checked against `right_bound` (BC-1 BC1-5). The FileView carefully **rebases** `file_offset_of_buffer_end`
from the impl's post-op accounting after `setReadUntilPosition`/`seek`/`next` (because `ReadBufferFromS3`
may discard its buffer on a range change). This is correct but subtle; a regression in that rebase would
mis-clamp reads. It's the kind of thing that needs an explicit test for a **range read that changes the
read-until-position mid-stream** (right-mark narrowing), not just a full-file read.

**BC5-5 (Low — projections read through the parent ref; nested-key resolution adds a routing step).** A
projection's column files are nested (` /.proj/ `) inside the **parent** part's manifest.
Reads route through `parsePartFilePath` → nested key → the parent ref's tree. Correct by construction, but
projection reads exercise a distinct routing branch; correctness depends on the nested-path parser +
manifest tree lookup agreeing on the key encoding (`escapeForFileName`). No defect found, flagged as a
distinct path to keep tested.

**BC5-6 (Info — the async-prefetch / page-cache / FS-cache stages sit BELOW the FileView).** The FileView
is the **last** stage, so caches operate in blob (envelope-inclusive) coordinates and the FileView narrows
on top (CACHE-2). For reads this composes correctly; the only consequence is that cached byte ranges are
blob-relative (shared across every part referencing the blob — a plus).

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| BC5-1 | Info | One file = one blob = one payload ⇒ no cross-blob compression-block/gather-seam hazard ✅ |
| BC5-2 | Med | Two size semantics (payload-only vs envelope+payload); correctness depends on ALL reads using prepareRead+FileView; a direct getStorageObjects read would return envelope-as-data |
| BC5-3 | Low | Inline vs blob split ⇒ two read paths within one part; both correct, both need coverage |
| BC5-4 | Low | Right-mark bound propagation correct but relies on subtle impl-rebase; needs a mid-stream range-narrowing test |
| BC5-5 | Low | Projection reads use a distinct nested-key routing branch |
| BC5-6 | Info | Caches sit below FileView (blob coordinates); composes correctly |

**Verdict:** wide-part reads are **structurally correct**, and the one-file-one-blob layout elegantly
sidesteps the usual object-store compression-boundary hazards. The real risk is **BC5-2**: the design
carries two different notions of a file's "size" and stays correct **only** because every byte read is
funneled through the `prepareRead` FileView branch — a strong, undocumented invariant that a future/
alternate read path could violate and read the envelope header as data. Worth an assertion or a
consolidated single-size accessor to make the invariant enforced rather than conventional.

## cas-bc6-mtime-semantics-audit.md

Language: Markdown

# BC-6 — `getLastModified` / mtime-Semantics Audit

Static read of what CAS returns for `getLastModified` (`ContentAddressedMetadataStorage.cpp` ~695–713)
and how MergeTree *consumes* disk mtimes (`MergeTreeData.cpp` `modification_time` at 2100/6388/9558,
`isOldPartDirectory`/`clearOldTemporaryDirectories` 3197–3265; `ReplicatedMergeTreePartCheckThread.cpp`
426; `MergeTreePartsMover.cpp` 301). Question: does the *synthetic* mtime break any age-based logic
(TTL, old-parts cleanup, merge/part-check scheduling)?

---

## 1. What CAS returns (as coded)

```cpp
// part file / part dir with a committed ref:
return Poco::Timestamp::fromEpochTime(resolved->published_at_ms / 1000);   // = ref PUBLISH time
// table-level / generic verbatim file:
if (existsFile(path)) return Poco::Timestamp(0);                           // = EPOCH (1970)
throw FILE_DOESNT_EXIST;                                                    // unresolved path
```
`setLastModified(...)` is a **no-op** (can't set mtime on content-addressed objects).

---

## 2. Findings

**BC6-1 (Med — part mtime = ref *publish* time, which RESETS on every re-publish / relink).** A part's
`modification_time` is loaded from `getLastModified` = `published_at_ms`, i.e. when *this replica*
published the ref — **not** when the data was created. Consequences:
- **Cross-replica divergence**: the same logical part has a **different** `modification_time` on each
 replica (each replica's own relink/publish time). Fetch-by-relink stamps "now."
- **A re-published part looks younger than its data.** `ReplicatedMergeTreePartCheckThread`
 (`part->modification_time + MAX_AGE_OF_LOCAL_PART_THAT_WASNT_ADDED_TO_ZOOKEEPER < current_time`) uses
 this to decide when a not-in-ZK local part is old enough to act on — on CAS the clock starts at
 relink/publish, so the check waits **longer** than intended after a relink.
- **`system.parts.modification_time` is misleading** for any operator/tool treating it as data age
 (retention scripts, "oldest part" dashboards). Cosmetic but real.

**BC6-2 (Med — verbatim/table-level files report EPOCH(0); unresolved paths THROW).** Table-level and
generic verbatim files (`format_version.txt`, `deduplication_logs/…`) return `Poco::Timestamp(0)` → ~1970
→ "infinitely old" to any `now - mtime` heuristic. And a path that resolves to no ref/file **throws
`FILE_DOESNT_EXIST`** from `getLastModified`. So callers that (a) age-check a verbatim file see it as
maximally old, or (b) call `getLastModified` on a not-yet/never-committed path must be inside a
try/catch. `clearOldTemporaryDirectories` **is** wrapped in try/catch (line 3263) — but any *other* caller
that assumes `getLastModified` never throws would surface an error where a plain disk returns a timestamp.

**BC6-3 (Low — `setLastModified` is a no-op → "touch to refresh age" silently fails).** Any MergeTree/ops
flow that *sets* a directory/file mtime to reset its age (a known pattern for protecting in-use temp dirs)
has **no effect** on CAS. Age is always derived from publish time; you cannot bump it. Low impact today
but a latent surprise for any future logic relying on writable mtimes.

**BC6-4 (Info — TTL is data-driven, NOT mtime-driven, so TTL moves/deletes are UNAFFECTED ✅).** MergeTree
TTL uses the min/max of the TTL expression over the part's rows (`getMinMaxTime`/column data), not the
file mtime. So the synthetic mtime does **not** corrupt TTL expiry or TTL moves. This clears an obvious
worry and is worth stating explicitly.

**BC6-5 (Low — `clearOldTemporaryDirectories` is largely inert on CAS; crash tmp-debris relies on GC).**
Uncommitted tmp part staging on CAS has **no ref**, so it isn't enumerated by `iterateDirectory` (which
lists refs), and `getLastModified` on such a path throws (caught → skipped). Committed `delete_tmp_` /
`tmp-fetch_` refs get `published_at_ms`. Net: the temporary-directory sweep — MergeTree's "extra
protection" against leaked tmp dirs — is effectively a **no-op** on CAS, and abandoned in-flight staging
is cleaned by **GC** instead (ERR-2 debris). Correct outcome, but the safety mechanism operators expect
(`temporary_directories_lifetime`) doesn't do anything here; document that GC is the real reaper.

**BC6-6 (Info — `MergeTreePartsMover` and load paths tolerate the publish-time mtime).** Moves and loads
set `modification_time` from `getLastModified` and use it only for bookkeeping/`remove_time` seeding;
functionally tolerant of publish-time semantics (no correctness break, just the BC6-1 skew).

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| BC6-1 | Med | Part mtime = ref publish time; resets on relink → cross-replica divergence, part-check timing skew, misleading `system.parts.modification_time` |
| BC6-2 | Med | Verbatim files report epoch(0) (infinitely old); unresolved paths throw from getLastModified |
| BC6-3 | Low | `setLastModified` no-op → "touch to refresh age" silently fails |
| BC6-4 | Info | TTL is data-driven, not mtime — TTL moves/deletes unaffected ✅ |
| BC6-5 | Low | `clearOldTemporaryDirectories` effectively inert on CAS; GC is the real tmp-debris reaper |
| BC6-6 | Info | Movers/load paths tolerate publish-time mtime (bookkeeping only) |

**Verdict:** no *data* corruption from mtime — crucially, **TTL is safe (BC6-4)**. The real issues are
**semantic/operational**: part `modification_time` means "published/relinked here," not "data age"
(BC6-1), diverges across replicas, and verbatim files read as 1970 (BC6-2). The most important operational
note is **BC6-5**: the `temporary_directories_lifetime` safety net is inert on CAS and GC is the actual
cleaner — a behavior operators must understand. These would never show up in the protocol-level audits; they
only appear by reading the mtime consumers.

## cas-bc7-blocking-io-under-locks-audit.md

Language: Markdown

# BC-7 — Blocking S3 I/O Under MergeTree Locks Audit

Static read of *where* CAS's synchronous S3 round-trips execute relative to MergeTree's global
per-table locks. Grounded in `MergeTreeData::Transaction::commit` (`MergeTreeData.cpp` 8788–8807:
`lockParts()` then, **under the lock**, `part->getDataPartStorage().commitTransaction()`),
`Transaction::renameParts()` (8778–8785), `preparePartForCommit` (5358–5380, `rename_in_transaction`),
and `DataPartsLock` (531). Question the protocol audits never asked: **does a slow S3 round-trip stall the
whole table?**

---

## 1. Where the network work lands (as coded)

MergeTree's commit is two-phase w.r.t. the rename:
- **`rename_in_transaction = true`** → `renameParts()` runs the rename (`part->renameTo`) **before**
 `commit()` and **outside** `DataPartsLock`. On CAS `renameTo` = `moveDirectory` = *staging into the
 metadata transaction* (in-memory), not yet an S3 write.
- **`commit()`** then does `auto lock = data.lockParts();` and, **inside the lock**, for every precommitted
 part:
  ```cpp
  if (part->getDataPartStorage().hasActiveTransaction())
      part->getDataPartStorage().commitTransaction();   // <-- CAS: publishStaging → S3
  ```

On a plain/local disk `commitTransaction()` is a cheap local rename + metadata flush. **On CAS it is the
entire durable-publish protocol** (B188 precommit-first): blob PUTs, precommit-manifest write, promote,
and the ref-shard `casPut` — **each a network round-trip, each with CAS-conflict + throttling retries** —
all executed **while holding `DataPartsLock`**.

---

## 2. Findings

**BC7-1 (High — the CAS durable publish runs under `DataPartsLock`, serializing the whole table's
part-set behind S3 latency).** `DataPartsLock` is a single per-table mutex guarding `data_parts_indexes`.
Because `commitTransaction()` (blob uploads + precommit + promote + ref CAS) executes inside `commit()`
under that lock, **every concurrent INSERT/merge/mutation commit on the table serializes behind each
other's full S3 publish**, and any operation that needs `DataPartsLock` (part-set mutations, some
introspection, cleanup) blocks for the duration. On a healthy S3 this is tens of ms; under **throttling /
429 with CAS-conflict retries (ERR-1)** a single commit can hold the lock for **seconds**, stalling all
other part-set operations table-wide. This is a genuine, CAS-specific scalability/latency hazard that
does not exist on local disks and is invisible to the protocol-correctness audits.

**BC7-2 (Med — the flat-combining `mutateShard` queue + single-writer mount lease compound the stall).**
The ref-publish inside `commitTransaction()` goes through `mutateShard`'s in-process flat-combining queue
(one CAS per shard batch). So concurrent commits to the **same namespace shard** don't just contend on
`DataPartsLock` — they also **queue** on the shard mutator, and each shard `casPut` may retry on conflict.
The two serialization layers (DataPartsLock + per-shard mutator) stack: the lock is held while waiting in
the shard queue and while the shard CAS retries. Worst case, `root_shards` sets the ceiling (RES-2) and a
hot table funnels commits through both bottlenecks.

**BC7-3 (Med — merge/mutation commits hold `currently_merging_mutating_parts` across the same S3
publish).** A merge finalizes by committing its result part via the same `Transaction::commit()` path, so
the merge's S3 publish also runs under `DataPartsLock` (and the merge selection state
`currently_merging_mutating_parts` remains occupied until the merge finishes). Slow publishes therefore
also **lengthen the window merges occupy scheduling slots**, indirectly throttling merge throughput and
letting the active-part count drift up under insert pressure.

**BC7-4 (Med — DROP/DETACH/RENAME issue synchronous S3 CAS under their own table locks).** `removeRecursive`
→ `dropNamespace`/`dropRefIfPresent` (tombstone shard `casPut`) and `moveDirectory(relative_data_path,
new_table_path)` for RENAME TABLE are synchronous S3 mutations executed while the DDL holds the relevant
table/structure lock. A throttled/slow S3 turns a `DROP`/`RENAME` into a lock-holding stall, and because
`DROP` tombstones don't free bytes synchronously (LC-1) the operator sees a slow DDL that *also* didn't
reclaim space.

**BC7-5 (Low — startup part-loading does S3 LIST/GET under loading synchronization).** Enumerating parts at
startup requires read-your-writes `listNamespaces`/`listDirectory` + per-ref manifest GETs (BOOT-1). These
network round-trips run during table attach/load; a slow or throttled bucket lengthens startup and holds
loading-side synchronization, delaying table availability. Not a steady-state lock but a
availability-latency concern.

**BC7-6 (Info — reads mostly copy the parts snapshot under the lock briefly, then release ✅).** SELECT
paths take `DataPartsLock` only to snapshot the active-parts vector, then release before doing blob GETs.
So query **reads** don't hold `DataPartsLock` across S3 I/O; the stall in BC7-1 is between **writers/DDL**,
not readers-vs-storage. This bounds the blast radius (SELECTs aren't directly blocked by a slow commit's
GETs, only by the brief snapshot contention).

---

## Summary

| ID | Sev | One-liner |
|----|-----|-----------|
| BC7-1 | High | CAS durable publish (blob PUTs + precommit + promote + ref CAS, each with retries) runs inside `Transaction::commit()` under `DataPartsLock` → table-wide writer stall under S3 latency/throttling |
| BC7-2 | Med | Flat-combining `mutateShard` queue + shard CAS retries stack under the held lock; `root_shards` caps parallelism |
| BC7-3 | Med | Merge/mutation commits hold `currently_merging_mutating_parts` across the same slow publish → merge-throughput drag |
| BC7-4 | Med | DROP/DETACH/RENAME issue synchronous S3 CAS under DDL locks → slow-DDL stalls |
| BC7-5 | Low | Startup part-loading does S3 LIST/GET under loading sync → attach-latency |
| BC7-6 | Info | Reads snapshot parts under the lock briefly then release; SELECTs not blocked across storage I/O ✅ |

**Verdict:** this is the **most operationally significant finding of the BC series**. CAS turns
`Transaction::commit()` — a cheap local operation on ordinary disks — into a **multi-round-trip S3
protocol executed under the per-table `DataPartsLock`** (BC7-1). Correctness is unaffected, but under S3
throttling the lock-hold time balloons and serializes all writers/DDL on the table, compounded by the
per-shard flat-combining queue (BC7-2). Reads are largely spared (BC7-6). The fix direction is to move the
network-heavy publish **out** of the `DataPartsLock` critical section (upload/precommit before taking the
lock; keep only the in-memory index swap + final ref promotion under it), mirroring the `rename_in_transaction`
split that already moves `renameParts()` outside the lock.

## cas-codeonly-line-audit.md

Language: Markdown

# CAS Code-Only, Line-by-Line Re-Audit

Behavior derived **from code only** (comments ignored except where code *contradicts* them, which is
itself a finding). One section per subsystem batch. IDs are prefixed by file. Severity is engineering
judgement; everything here is static (unbuilt/unrun).

Scope: all 68 files under `src/Disks/.../ContentAddressed/` (18,564 LoC) plus the disks command and
gtests already covered separately.

Legend: **[BUG]** code defect · **[HARDENING]** missing guard · **[CONTRADICTION]** code ≠ comment ·
**[OK]** verified-correct load-bearing behavior worth recording.

---

## Consolidated findings index (all 7 batches)

Ordered by severity. "New" = first surfaced by this code-only pass; others reconfirm/refine prior audits.

### Medium

| ID | File | One-line |
|----|------|----------|
| RF-1 | CasRunFile | `RunFileReader::next()` parses record `klen`/`plen` with an unchecked `operator[]`/`substr` → OOB heap read / non-`CORRUPTED_DATA` throw on a CRC-valid but malformed block. Reachable from manifest decode, GC fold, and fsck. |
| MC-1 | CasManifestCodec / CasStore | `PartManifest.payload_digest` is written but **never re-verified** on decode/read → a bit-flip in a `blob_hash`/`blob_size` is undetected. |
| RSC-1 | CasRootShardCodec (+GcFormats, GenerationSeal, GcOutcomes) | Protobuf parse via `ParseFromArray(…, static_cast (size))` with no size/recursion limit and an unchecked `int` cast (>2 GiB → negative). |
| RSC-2 | CasRootShardCodec (+GC decoders) | Additive protobuf fields dropped on re-encode (mixed-version control-plane data loss). |
| STORE-2 | CasStore | `locate()` uses the fixed `PoolMeta.blob_header_len`, not the blob's own envelope `header_len` → wrong offset under config drift / mixed-version writers (silent misread). |
| STORE-C1 | CasStore | Teardown race: `scheduleRemount` can re-arm `remount_thread` while `mount_keeper` is stopping → UAF / `std::terminate`. |
| SR-1 | CasServerRoot | Mount-lease liveness is wall-clock (`expires_at_ms>now`); clock skew → premature reclaim / false unavailability (token-guarded, so no corruption). |
| SCHED-1 (new) | CasGcScheduler / CasGc | A resurrected zombie leader's unconditional `pulseHeartbeat` clobbers `gc/hb.owner`, defeating B160 → a follower can steal the lease from a live long-round leader (non-corrupting churn). |
| MW-1 (new) | ContentAddressedMetadataStorage | Relink/rename receiver trusts sender/source `entry.blob_size` (payload_digest ignored); only blob *presence* is revalidated → wrong-length reads (chains MC-1/STORE-2). |
| TXN-2 (new) | ContentAddressedTransaction | RENAME TABLE is a non-atomic multi-op move; a throw mid-loop leaves the table split across namespaces (no in-call compensation). |
| OSB-2 | CasObjectStorageBackend | `finalizeConditionalWrite` (412/NoSuchKey→PreconditionFailed) has no real-S3/GCS e2e coverage (test-gap). |

### Low / hardening

| ID | File | One-line |
|----|------|----------|
| ENV-1 | CasEnvelope | Size-consistency check bypassable via `logical_size` overflow wrap. |
| ENV-2/3 | CasEnvelope | `header_hash` covers only the 94-B core, not TLVs; "critical extension" enforcement relies on writer honesty. |
| FMT-1 | CasFormat | `FormatId::Roster` defined but `magicFor` throws → dead/incomplete path. |
| GS-1 | CasGenerationSeal | `decodeFoldSeal` casts enums without validation (unlike sibling decoders). |
| LAY-1/2 | CasLayout | `checkNamespace`/`mountpointObjectKey` don't reject `.`/`..` → path-traversal risk on `LocalObjectStorage`. |
| PM-1 | CasPoolMeta | `createOrValidate` silently ignores passed `root_shards`/`blob_header_len` when a pool exists (config footgun). |
| PROBE-1 | CasProbe | Concurrent probes of a shared `probe_prefix` can spuriously read `NOT_IMPLEMENTED`. |
| OSB-1/3 | CasObjectStorageBackend | Non-atomic HEAD-then-GET token/bytes skew; GCS versioning "inconclusive" fails open. |
| BUILD-1 | CasBuild | Content hash is a chunked CityHash128 tied to unversioned `DBMS_DEFAULT_HASHING_BLOCK_SIZE`. |
| BUILD-2 | CasBuild | `blob_header_len` floor (96) is below the mandatory provenance-TLV need → 96–120 bricks all blob writes. |
| SR-2/3 | CasServerRoot | `allocateWriterEpoch` no overflow guard; fresh mount pins GC floor to 0 until first renewal. |
| GC-1 (new) | CasGc | Post-CAS T0 hand-off reclaim: a crash between the round CAS and the hand-off permanently strands a `gc/gen/ /` prefix (fsck-only, no auto-reclaim). |
| PPP-1 (new) | PartPathParser | `looksLikePartDir` false-positives on non-Atomic table/dir names ending in three numeric groups → misroutes table files as part files. |
| TXN-1/3/4 | ContentAddressedTransaction | Non-atomic multi-part commit; committed-content-file unlink is a fail-open no-op; B151 early publish exposes a rollback-window read. |

### Info / [OK] highlights

C4 (unbounded `shard_write_seq` growth), STORE-3 (O(N²) wide-part listing), INSTR-1 (unanchored metric
classification), BID-1 (GC-artifact determinism is load-bearing/fail-closed), INT-1 (payload never
re-hashed on the normal read path), INT-3 (fsck detects but never repairs), MW-2 (`getStorageObjects`
header-offset trap). Verified-correct load-bearing paths: `flushShardBatch` flat-combining + snapshot
isolation, `promote` journal-replay + blob revalidation, the one-pass GC round's single-CAS commit with
idempotent pre-CAS deletes, `reclaimDroppedShards` layered guards, exception-safe write buffers & txn dtor.

---

## Batch 1 — Primitives & Codecs

Files: `CasIds.h`, `CasToken.h`, `CasManifestId.h`, `CasEnvelope.{h,cpp}`, `CasFormat.{h,cpp}`,
`CasCodecUtil.h`, `CasManifestCodec.{h,cpp}`, `CasRootShardCodec.{h,cpp}`, `CasRunFile.{h,cpp}`,
`CasGcFormats.{h,cpp}`, `CasGenerationSeal.{h,cpp}`.

### RF-1 [BUG, Med] — `RunFileReader::next()` parses record lengths with an *unchecked* reader

`CasRunFile.cpp:435–459`. Every other parse in this file bound-checks against the buffer
(`le32of`/`le64of` throw `CORRUPTED_DATA` on OOB; the footer and block-frame parsers even document
"defense in depth"). **The record loop drops that discipline.** Inside `next()`:
```cpp
auto le32at = [&](const String & s, size_t off){ ... s[off + i] ... };   // NO bounds check (operator[])
uint32_t klen = le32at(cur_block, cur_block_pos); cur_block_pos += 4;
key = cur_block.substr(cur_block_pos, klen);      cur_block_pos += klen;  // substr clamps, but += klen doesn't
uint32_t plen = le32at(cur_block, cur_block_pos); cur_block_pos += 4;
payload = cur_block.substr(cur_block_pos, plen);  cur_block_pos += plen;
```
`cur_block_records` (record count) and the per-record `klen`/`plen` all come from the block payload.
`installBlockFrame` verifies a **crc32c** over that payload — but crc32c is a **non-cryptographic,
forgeable** checksum, and any pool participant can write objects (no intra-pool authz). A CRC-valid block
with `klen`/`plen` overrunning the block, or a `rec_count` larger than the records present, drives
`cur_block_pos` past `cur_block.size()`, after which `le32at`'s `operator[]` performs an **out-of-bounds
heap read** (UB in release; a hardening trap otherwise) and `substr(pos>size)` throws
`std::out_of_range` — a raw `std::exception`, **not** the fail-closed `CORRUPTED_DATA` the rest of the
decoder guarantees. Reachable from `decodePartManifest` (embedded entries RunFile) and every GC fold that
streams a run. **Fix:** bound-check `cur_block_pos + 4` and `+ klen`/`+ plen` against `cur_block.size()`
before each read (use the same `le32of`-style guard), and validate `rec_count` against remaining bytes.

### MC-1 [BUG/HARDENING, Med] — `PartManifest.payload_digest` is written but *never verified*

`CasManifestCodec.cpp`: `encodePartManifest`/`computePayloadDigest` set the digest (`CasBuild.cpp:685`),
`decodePartManifest:135` reads it into the struct, and **no code recomputes and compares it** (confirmed by
grep — the only callers are the write-side set and the digest function itself). The manifest object key is
**build-identity** (`writer_epoch/build_seq/ordinal`), *not* a content hash, so there is also no
content-hash-vs-key check to catch corruption. Net: a bit-flip in an entry's `blob_hash` or `blob_size`
inside a manifest body is **undetected** — the reader will resolve a wrong blob / wrong length. This is the
manifest-level analogue of INT-1 (blob payload not verified on read). The header comment even states the
digest is "integrity/debug only: NEVER a key" — i.e. the *design* declines to verify it. **Fix:** verify
`payload_digest` against `computePayloadDigest` when decoding a manifest read from storage.

### ENV-1 [BUG, Med] — envelope size-consistency check bypassable via `logical_size` overflow (confirms BC1-1)

`CasEnvelope.cpp:263`:
```cpp
const uint64_t expected_object_size = static_cast<uint64_t>(header_len) + h.logical_size;
if (expected_object_size != object_size) throw ...;
```
`header_len` is bounded (≤16384). `h.logical_size` is read raw at :237 with **no prior magnitude check**.
A crafted `logical_size = 2^64 − header_len + object_size` makes the `uint64_t` addition **wrap** to exactly
`object_size`, passing the only guard, while `h.logical_size` retains its ~`2^64` value. The
size-consistency invariant that is *supposed* to fail closed here does not for this input. **Fix:** check
`logical_size ≤ object_size` and `header_len ≤ object_size` before the addition.

### ENV-2 [HARDENING, Low] — `header_hash` covers only the 94-byte core, not the TLV extension area

`CasEnvelope.cpp:181,249–259`. The CityHash64 integrity field is computed over `[0,94)` only. A bit-flip
inside the `[94, header_len)` TLV area (e.g. a `provenance` body value) is **not** caught by `header_hash`
— only by structural TLV parsing / the zero-padding check, which a value-flip inside a well-formed TLV
passes. Low because those fields are diagnostic (provenance/intended_ref), not load-bearing.

### ENV-3 [CONTRADICTION, Low] — "critical extension" is writer-controlled, not self-enforcing

`CasEnvelope.cpp:221–223, 310–314`. The fail-closed path fires only if the **global** `flags` critical bit
is set *and* an unknown TLV is seen. A writer that emits an unknown TLV **without** setting the flag has it
silently skipped by readers. So "critical extension → fail closed" is advisory on writer honesty, not a
property the decoder enforces. Correct for forward-compat, but weaker than the comment implies.

### RSC-1 [HARDENING, Med] — `decodeRootShard` has no pre-parse size cap; size cast to `int` is unguarded (confirms BC4-1)

`CasRootShardCodec.cpp:160`: `msg.ParseFromArray(data.data(), static_cast (data.size()))`. No
`CodedInputStream` byte/recursion limit is set, and `static_cast (data.size())` is **negative/UB for a
>2 GiB object**. Bounded by `manifest_hard_limit` on the *write* side, but the *read/decode* side enforces
no maximum before allocating+parsing → OOM / bad-size on a corrupt or maliciously-planted oversized shard.

### RSC-2 [BUG, Med] — additive protobuf fields are dropped on re-encode (confirms BC4-2)

`CasRootShardCodec.cpp`: `decodeRootShard` copies fields *out* into `RootShard`; `encodeRootShard` rebuilds
a fresh `msg` from the struct. Any field a newer build added is **not carried through** — an older build
that mutates the shard silently strips it. `checkCompatibility` only blocks a *breaking* bump; an additive
field with an unchanged `compatibility_version` is lost. Mixed-version control-plane data loss.

### RSC-3 [OK] — root-shard journal validation is genuinely fail-closed ✅

`CasRootShardCodec.cpp:200–217` rejects: neither-binding-nor-tombstone events; `transition_version >
shard_version`; and a decreasing journal. `decodeOwnerBinding:89–94` enforces the
`owner_kind ↔ build_id` invariant. `decodeManifestRef:63` range-checks the ordinal. These are the
load-bearing fold-safety guards and they hold.

### MC-2 [HARDENING, Low] — manifest duplicate-path detection assumes sorted storage order

`CasManifestCodec.cpp:147`. Decode rejects duplicates via an **adjacent** `prev_path` check, valid only
because encode sorts. A corrupt/unsorted embedded RunFile could carry **non-adjacent** duplicate paths
undetected. (Encode-side dedup at :74 is correct.)

### FMT-1 [HARDENING, Low] — `FormatId::Roster` has a compat entry but no magic

`CasFormat.cpp:67` — `magicFor(Roster)` falls through to `LOGICAL_ERROR`, yet `changePoints` returns a
baseline for it. A defined-but-magic-less format id; any call to `magicFor(Roster)` is a hard error. Latent
(Roster appears unused/"pre-roster").

### GS-1 [HARDENING, Low] — `decodeFoldSeal` does not validate enum fields (inconsistent with `decodeRetiredSet`)

`CasGenerationSeal.cpp:100–104`. `folded_token_type` is `static_cast (e.folded_token_type())`
and `classification` is `static_cast<uint8_t>(e.classification())` — **neither is range-validated**. By
contrast `decodeRetiredSet` (`CasGcFormats.cpp:219`) routes `token_type` through `tokenTypeFromProto`,
which fails closed on an unknown value. A corrupt fold seal therefore yields an out-of-range `TokenType`
or a truncated `classification` (uint32→uint8) silently, which then drives fold graduate/condemn decisions.
Low (fold seal is token-addressed, single trust domain) but an inconsistent fail-closed discipline.

### RSC-1/RSC-2 generalize to the whole GC control plane

Re-reading `CasGcFormats.cpp` and `CasGenerationSeal.cpp`: **all four** protobuf decoders — `decodeRootShard`,
`decodeGcState`, `decodeRetiredSet`, `decodeFoldSeal` — use `ParseFromArray(data.data(),
static_cast (data.size()))` with no pre-parse byte cap and the unguarded `int` size cast (RSC-1), and
all decode-into-struct / encode-from-struct, dropping additive fields on re-encode (RSC-2). So the OOM-cap
gap and the mixed-version field-loss hazard apply to the **entire GC/control plane**, not just root shards.
`decodeGcState` does add a real semantic guard (`gc_shards == 0` → `CORRUPTED_DATA`, :126) and
`decodeRetiredSet` validates `kind`/`token_type` — good, but the size/round-trip issues are pool-wide.

### Batch-1 [OK] notes (verified-correct, load-bearing)

- `CasCodecUtil.h::readFixedBytes` bound-checks `n > in.available()` **before** allocating → truncation and
 oversized-length fields fail closed as `CORRUPTED_DATA` (not OOM); `decodeGuarded` translates EOF-class
 read errors to `CORRUPTED_DATA` and is sound *only* because all codec input is in-memory (documented and
 true).
- `CasRunFile.cpp` footer and block-frame parsing bound-check **every** offset/length, verify **crc32c** on
 footer and each block, and cap the index reservation on the untrusted `block_count` (`min(.,64)`). Strong.
 (The single exception is RF-1's record loop.)
- `CasIds.h` strong-typed id wrappers make BlobId/TreeId/RootNamespace non-interchangeable at compile time
 (explicitly the fix for a prior id-mixing data-loss class); `hexToU128` validates length + each hex digit.
- `CasFormat.cpp::checkCompatibility` fails closed (`UNKNOWN_FORMAT_VERSION`) on any object whose
 `compatibility_version > G_BUILD`.

---

## Batch 2 — Layout / Key construction / Pool metadata / Capability probe

Files: `CasLayout.h`, `CasPoolMeta.{h,cpp}`, `CasProbe.{h,cpp}`.

### LAY-1 [HARDENING, Med] — `checkNamespace` does NOT reject `..` / `.` segments

`CasLayout.h:282–312`. `checkNamespace` rejects empty segments and the reserved `_files` / `_manifests` /
`_precommits`, but **not** a segment equal to `..` or `.`. Every namespaced key (`rootShardKey`,
`manifestKey`, `manifestNamespacePrefix`, `namespaceFilesPrefix`) is built by string-concatenating the raw
namespace. On S3 `..` is a literal segment (harmless), but on a **`LocalObjectStorage`** backend the key
*is* a filesystem path and `..` **traverses out of the pool prefix** → read/write/delete outside the pool.
Notably, `namespaceFileKey:88–90` *does* reject `..` for the file-name part — so the authors know `..`
matters, but the check was **not** applied to the namespace segments. Safe today only because the upstream
wiring derives namespaces via `escapeForFileName` (which encodes `.`→`%2E`, so a literal `..` can't arise
from SQL), i.e. this is an unguarded security boundary relying on an external invariant. **Fix:** reject
`.`/`..` segments in `checkNamespace`.

### LAY-2 [HARDENING, Low] — `mountpointObjectKey` omits the same `..` check

`CasLayout.h:123–129` checks empty / leading-trailing `/` / `//` but not `..` segments, unlike the sibling
`namespaceFileKey`. Same latent-traversal note on a Local backend; the input is a "server-prefixed mirrored
path" so again relies on the caller never producing `..`.

### LAY-3 [CROSS-REF → Batch 4] — empty-root precondition must span three prefixes

`serverRootDataPrefix` is `roots/ /`, but Phase-1 data lives under `cas/refs/ /`
(`casRefsServerPrefix`) and `cas/manifests/ /` (`casManifestsServerPrefix`). The mount-safety
"empty root precondition" must LIST **all three** or it can declare a server root empty while `cas/…`
holds data. Flagged to verify in `CasServerRoot` (Batch 4).

### PM-1 [CONTRADICTION, Low] — mismatched reopen config is silently ignored (confirms CFG-1/2)

`CasPoolMeta.cpp:110–138`. `createOrValidate` validates the *passed* `root_shards`/`blob_header_len`
(`BAD_ARGUMENTS` on bad values) but, when the pool object already exists, returns
`decodePoolMeta(existing)` and **discards the passed config with no comparison/warning**. An operator who
edits `root_shards` in config after pool creation gets **no error and no warning** — the old value silently
persists. Confirms the CFG footgun at the code level.

### PROBE-1 [HARDENING, Low → verify caller] — capability probe is not concurrency-safe on a shared prefix

`CasProbe.cpp:52–57`. Step 1 does `putIfAbsent(probe_prefix + "/token")` and treats
`PreconditionFailed` as "backend is unexpectedly occupied or broken" (→ `NOT_IMPLEMENTED`, mount refused).
If two servers run the probe against the **same** `probe_prefix` concurrently, the loser sees
`PreconditionFailed` on the fresh-key step and wrongly fails its mount. Safe only if `probe_prefix` is
unique per mount (server_root_id / random token) — flagged to verify at the call site.

### Batch-2 [OK] notes

- `CasPoolMeta::validateConstants` enforces invariants in **both** directions with the right code
 (`BAD_ARGUMENTS` at create, `CORRUPTED_DATA` on decode); `min_reader_generation` gates an
 too-old binary at startup (`UNKNOWN_FORMAT_VERSION`). Create is a race-safe create-if-absent CAS that
 re-reads the winner on conflict.
- `CasProbe` is a genuinely strong mount-time gate: it verifies conditional create, token-exact overwrite,
 token-exact CAS (create-if-absent + stale-token conflict), token-exact delete, list-after-write/delete,
 **and** detects a versioning delete-marker — refusing the mount (`NOT_IMPLEMENTED`) on any deviation.
 This is the enforcement behind the "backend must support CAS semantics" contract.
- `Layout` cleanly separates hot `cas/refs/`, cold `cas/manifests/`, content `blobs/`, and control
 `gc/server-roots/` subtrees; shard numbers are numeric (can't collide with `_files`).

---

## Batch 3 — Backends (real S3, in-memory, instrumented)

Files: `CasBackend.h`, `CasObjectStorageBackend.{h,cpp}`, `CasInMemoryBackend.{h,cpp}`,
`CasInstrumentedBackend.{h,cpp}`.

### OSB-1 [BUG/HARDENING, Low] — Native `get`/`getStream` return a token+bytes pair that can straddle a concurrent overwrite

`CasObjectStorageBackend.cpp:426–522`. The Native path does `nativeHead(key)` (token = ETag, plus size),
then a **separate** ranged `readObject`. The two are not atomic. If a **mutable** object (root shard,
gc/state) is overwritten between the HEAD and the GET, the returned `GetResult` carries the **old** token
(from HEAD) with the **new** bytes (from GET); and because `readObjectRanged` reuses `hr->size` as
`known_size`, a shrunk object yields a **short read** clamped to the stale size. Deletion is handled
(`isObjectNotFound → nullopt`); **replacement is not**. Masked in practice because callers use the token
for a subsequent token-guarded CAS (a stale token → `Conflict` → retry), but it is a genuine
read-inconsistency window for any read-only decision on a mutable object. Immutable blobs are unaffected
(write-once). **Note:** `InMemoryBackend::get` returns a *consistent* pair under one mutex, so this hazard
is **not reproducible** in the gtest harness — real-store-only.

### OSB-2 [TEST-GAP, Med] — Native conditional-write outcome mapping is not covered end-to-end (confirms OSC-1)

`CasObjectStorageBackend.cpp:113–133` (in-code "HONEST NOTE"): `finalizeConditionalWrite` — the classifier
that maps a lost `If-None-Match`/`If-Match` (412 / `NoSuchKey`) to `PreconditionFailed` — is exercised
end-to-end **only against RustFS** at M-W; CI coverage is the Emulated mode, the typed-catch compile path,
and the classifier unit test. So the real-S3/GCS conditional-write path (the load-bearing CAS primitive) is
**not** in automated coverage. The mapping is at least fail-safe in direction (a misread error becomes a
retryable `PreconditionFailed`, never a false `Done`).

### OSB-3 [HARDENING, Low/Med] — `checkStorePreconditions` fails OPEN on an unverifiable versioning check (confirms OSC-2)

`CasObjectStorageBackend.cpp:51–80`. On GCS (generation-token dialect), a *confirmed* versioning-enabled
bucket refuses the mount (`NOT_IMPLEMENTED`, correct — token-exact DELETE would archive noncurrent
versions and GC would stop reclaiming). But if the versioning query **can't be answered** (permissions/
unsupported), the code **logs a warning and proceeds assuming versioning is off**. If versioning is
actually on, GC silently stops reclaiming space. Deliberate (avoid over-aggressive refusal) and logged,
but it is a fail-open on an unknown for a correctness-critical precondition.

### INSTR-1 [Info] — `classifyCasNs` uses unanchored substring matching

`CasInstrumentedBackend.cpp:112–140` classifies a key's namespace by ordered `key.find("/blobs/")`,
`/cas/refs/`, `/cas/manifests/`, `/_watermark`, `/_precommits/`, `/roots/`, `/gc/` … else Other. Unanchored
`find` could misattribute a key that embeds one of these tokens in a table path. **Metrics-only, no
correctness impact.**

### CORRECTION [supersedes OBS-1/OBS-2] — CAS **is** instrumented

`CasInstrumentedBackend.cpp` wires **6 namespaces × 11 ops = 66 `ProfileEvents`** (Put/PutDedup/Overwrite/
Cas/CasConflict/Head/HeadMiss/Get/GetStream/Delete/List per namespace). Critically, `putIfAbsent`
`Done`→`Put`, `PreconditionFailed`→**`PutDedup`**, so **per-namespace dedup rate is observable**, and
`CasCasConflict` makes **CAS-retry storms observable**. This retracts the earlier "no metrics" finding
(OBS-1/2). Each physical op increments exactly once (no retry double-count). What is *not* here is a
continuous physical-bytes / reclaim-backlog / GC-liveness gauge (those remain valid gaps).

### Batch-3 [OK] notes

- Native `get`/`getStream`/`head` honor the `optional`/empty contract, convert only the not-found signal
 (`NoSuchKey` enum **or** name; `FILE_DOESNT_EXIST` local) to absent, and **propagate every other error**
 (network/auth/throttle/corruption) unchanged — fail-closed by construction.
- `casWriteSettings` deliberately skips the post-upload existence/size recheck for CAS-mutable keys,
 because a concurrent conditional PUT legitimately replaces the object between upload and recheck (a live
 RustFS incident terminated the server on that false-positive). Integrity = conditional-PUT outcome + token.
- `nativeConditionalPut` takes the new token from the write-response ETag and only falls back to a HEAD
 when the backend returns none (local files) — removing ~73% of the backend's HEADs.
- `InMemoryBackend` (test-only) is strongly consistent and exposes the harness fault model:
 `failNextCasPut`, `setHoldDeletes`/`landPendingDelete` (deferred/lost delete), `setSimulateDeleteMarkers`,
 `setEnforceTokens`. It does **not** model HEAD-GET skew (OSB-1), LIST lag, partial writes, or network
 errors — bounding what the gtests can prove.

---

## Batch 4 — Store / ServerRoot / SingleWriterSlot

Files: `CasStore.{h,cpp}` (1573), `CasServerRoot.{h,cpp}` (643), `CasSingleWriterSlot.{h,cpp}`.

### STORE-C1 [BUG, Med] — teardown ordering can resurrect the remount thread after it is joined (UAF)

`CasStore.cpp:272–299` (dtor) stops the self-remount machinery **first** (`remount_stop=true`; join
`remount_thread`), **then** stops `mount_keeper` (`:292`). But `mount_keeper->stop()` →
`SingleWriterSlot::doTerminate` → `stopBackground()` joins the keeper's background loop, and if the loop's
final in-flight `renewOnce()` **fails** it runs `onRenewFailed()` → `raw->tripMountLost()` +
`raw->scheduleRemount()` (`:453–456`). `scheduleRemount` (`:497–523`), with `background_watermark` true,
takes `remount_thread_mutex` and **assigns a fresh `remount_thread`** — *after* the dtor already joined the
old one and will not join again. The new thread sees `remount_stop==true` and exits fast, but it is created
during destruction and is never joined by the dtor: the `remount_thread` member is then destroyed while
potentially joinable, and the thread body touches `this->remount_stop/remount_running` as `Store`'s members
are torn down → **thread-destroyed-while-joinable / UAF**. Narrow window (renew must fail exactly during
`mount_keeper->stop()`), but real. **Fix:** stop `mount_keeper` (join its background thread, so no further
`onRenewFailed→scheduleRemount`) **before** joining/destroying the remount machinery; or re-join
`remount_thread` after `mount_keeper->stop()`. (Refines the prior C1/C2 latent-UAF findings with the exact
call chain.)

### STORE-2 [BUG, Med] — `locate()` trusts the pool-fixed `blob_header_len`, never the blob's own envelope

`CasStore.cpp:928–947`. For a `Blob` entry, `locate` returns `offset = meta.blob_header_len` and
`length = entry.blob_size` — it **never reads the blob's envelope `header_len`**. Correctness depends
entirely on the invariant "every blob in the pool was written with a header of exactly
`meta.blob_header_len`". A blob written with a different header length — a mixed/edited pool
`blob_header_len` (PM-1 shows config drift is silently ignored), or any future writer using envelope TLV
extensions / `pad_to_header_len` (which `CasEnvelope` explicitly supports) — is read at the **wrong
offset**. Combined with INT-1 (payload is not hash-verified on read), this is **silent data corruption**,
not a fail-closed error. **Fix:** either verify the blob envelope `header_len == meta.blob_header_len` at
read, or read the offset from the envelope.

### STORE-3 [PERF, Low] — `lookupPath` / `listDirectory` are linear scans → O(entries²) per part read

`CasStore.cpp:907–926`. Each per-file open scans `manifest.entries` linearly; reading all files of a wide
part is O(entries²). Bounded by `manifest_hard_limit`, but a wide part (thousands of column files) does
millions of comparisons. Cheap fix: index entries by path in the decoded `PartManifest`.

### SR-1 [confirms SEC-7, Med] — mount-lease liveness is wall-clock based; clock skew can misjudge it

`CasServerRoot.cpp:342,464` and `CasStore.cpp:181–185`. Both the startup claim (`claimMount`
`expires_at_ms > now_ms`) and the GC fence (`computeHeartbeatFloor` `now_ms <= expires_at_ms +
skew_margin_ms`) compare a **durable wall-clock** expiry stamped by one server against the **local
wall-clock** of another. Skew → a live holder judged dead (premature reclaim/fence) or a dead one judged
live (unavailability). *Corruption* is prevented by the layered guards — the reclaim/fence PUTs are
token-guarded, the loser's keeper latches its write fence lost (`onRenewFailed→tripMountLost`), and
same-shard writes serialize through the shard CAS with distinct `writer_epoch`s — so the residual is
availability plus the already-known GC-vs-fenced-writer window (J1). The operator error text even carries a
"CLOCK SKEW CAVEAT". Confirmed at code.

### SR-3 [HARDENING, Low] — a freshly-claimed mount pins the GC floor to round 0 until its first renew

`CasServerRoot.cpp:286–297` (`makeMountBody`) leaves `observed_gc_round`/`min_active` defaulted to 0;
`computeHeartbeatFloor:451,468` folds `min_ack = min(.., observed_gc_round)`. So between `claimMount` and
the keeper's first `renewOnce`, the mount advertises `observed_gc_round = 0`, pinning the GC heartbeat floor
to 0 — a transient reclaim stall on every server start. Conservative/safe; the first beat clears it.

### SR-2 [Info] — `writer_epoch` has no overflow guard at UINT64_MAX

`CasServerRoot.cpp:270`: `next_writer_epoch = next + 1` with no check; `UINT64_MAX` is the retired
sentinel. Unreachable (2⁶⁴ mounts) but unguarded.

### LAY-3 — RETRACTED ✅

`CasServerRoot.cpp:172–184` `serverRootSubtreeEmpty` LISTs **all three** prefixes (`casRefsServerPrefix`,
`casManifestsServerPrefix`, `serverRootDataPrefix`), so the empty-root precondition is correct. Non-issue.

### MC-1 — reconfirmed at the read path

`Store::readManifest` (`CasStore.cpp:817–905`) verifies `refMatchesBody` (journal ref == body ref) **and**
`manifestNamespaceMatches` (both **structural** identity checks), and surfaces INV-NO-DANGLE on a missing
body — but it **never** recomputes/compares `payload_digest`. A corrupt entry inside a correctly-ref'd,
correctly-namespaced manifest is undetected (see Batch 1 MC-1).

### C4 — confirmed by grep (already documented)

`shard_write_seq[key]` is inserted at `:737/:756`, incremented at `:1263`, and **never erased** — not even
by `dropNamespace` (`:1445–1451` erases `shard_decode_cache` for the dropped shards but leaves
`shard_write_seq`). Unbounded growth ∝ distinct (namespace,shard) pairs ever written. (= prior C4/RES-4.)

### Batch-4 [OK] notes

- `flushShardBatch` (`:1057–1289`) is carefully exception-safe: **per-closure snapshot isolation** (a
 throwing closure rolls back only its own edits and drops out with its exception, `:1172–1184`);
 hard-limit degrades to **solo re-flush** so only the offending mutation gets `LIMIT_EXCEEDED`; the
 `view_gate` **shared** lock spans the whole flush so a beat's newer `observed_gc_round` can't overtake an
 in-flight batch; the CAS loop re-reads and replays on cross-writer `Conflict`. Lock order documented and
 consistent: `view_gate → RetireView mutex`, and payloads are computed off `state_mutex`.
- `coalescedReadShardDecoded` (`:655–697`) is a correct single-flight (promise/future) that publishes both
 success and exception to followers — no thundering herd on a hot shard.
- B157 read-your-writes: a committed shard CAS bumps `shard_write_seq` and erases the decode cache under
 one lock; `loadShardDecoded` skips caching a decode that raced a concurrent write (never serves a stale
 self-write).
- `SingleWriterSlot` lock discipline is clean: `prepareRenew` runs off `state_mutex` (subclass callbacks
 may take Store locks); `stopBackground` moves the thread out under `background_mutex` then joins outside
 it; the dtor deliberately runs no terminal op (crash-path semantics: seq freezes, GC observes it); a
 failed renew stops the loop with no re-arm (`startBackground` throws until `stopBackground`).
- Mount safety is genuinely layered: identity (owner anchor, clock-free) → durable-monotone `writer_epoch`
 (CAS-bumped, reset-hazard fail-closed) → liveness (mount lease) → local write fence. Every foreign/
 superseded touch fails closed (`LOGICAL_ERROR`/`ABORTED`), and reclaim is always token-guarded.

---

## Batch 5 — Build / write path

Files: `CasBuild.{h,cpp}` (991), `ContentAddressedWriteBuffers.{h,cpp}`.

### BUILD-1 [BUG-latent, Med] — pool content hash is a *chunked* CityHash128 with an unversioned block-size dependency (confirms AD1-3)

`CasBuild.cpp:71–77` `poolContentHash` hashes via `HashingReadBuffer` (chunked CityHash128 chained per
`DBMS_DEFAULT_HASHING_BLOCK_SIZE = 2048`), and the write path uses the same `HashingWriteBuffer`. The comment
records a live incident: a one-shot `CityHash128` **diverges** from the chunked one for any payload > one
block. So the pool's content-identity is **block-size-dependent** and that dependency is **not versioned**
(`FormatId::Blob` is baseline `{1,1}`). If `DBMS_DEFAULT_HASHING_BLOCK_SIZE` ever changed, every new blob's
hash would diverge from existing ones → dedup silently stops matching and copy-forward verification (`:528`)
falsely reports `CORRUPTED_DATA`. Load-bearing global constant with no guard tying it to the format version.

### BUILD-2 [BUG, Low/Med] — `blob_header_len` floor (96) is below what the mandatory provenance TLV needs → a misconfig bricks all blob writes

`CasBuild.cpp:313–341` (`buildHeader`) **unconditionally** attaches a `Provenance` TLV (`:323`) and sets
`pad_to_header_len = meta.blob_header_len`. Core header = 94 B; provenance TLV adds ~33 B → ~128 B needed.
But `CasPoolMeta::validateConstants` only requires `blob_header_len ≥ 96` (8-aligned). Configuring
`blob_header_len ∈ {96,104,112,120}` makes `encodeEnvelopeHeader` throw `BAD_ARGUMENTS`; the catch drops
only `intended_ref` (diagnostic), **not** provenance, so the retry throws again → **every blob write
fails**. Such a pool is write-bricked. **Fix:** raise the `blob_header_len` floor to cover core+provenance.

### INT-1 / STORE-2 — reconfirmed from the write side

The **normal** read path never re-hashes payloads; `CasBuild.cpp:523–533` (`copyForwardFromCondemned`) is
the **only** payload-hash re-verification and it is write-side. Separately, `buildHeader` /
`copyForwardFromCondemned` always pad to `meta.blob_header_len`, so the fixed-offset `locate()` invariant
(STORE-2) holds within one consistent config — STORE-2's silent misread needs config drift (PM-1) or a
mixed-version writer.

### Batch-5 [OK] notes

- Write buffers are exception-safe: `CaContentWriteBuffer` streams to a random-named temp file, hashes
 in-flight, and sets `temp_ownership_transferred` **only after** `on_finalized` returns — a throw there
 leaves the dtor to `removeTempFile()`; `cancel()` always removes it (BC-2/BC-3 positive).
- `stageManifest` enforces fail-closed caps **before** the body write (entries ≤ 2²⁰, per-inline ≤ 1 MiB,
 total inline ≤ 16 MiB, encoded ≤ 256 MiB) and mints a collision-free `ManifestRef = {epoch,seq,ordinal}`.
- `promote` is a fail-closed pure owner-move: re-reads+validates the body, **replays the shard journal** to
 confirm the precommit is still the live owner (removal ⇒ `ABORTED`, TLA+ `WPromote owner==bld`), and
 HEAD-revalidates **every** blob leaf (absent/condemned ⇒ `ABORTED`). `abandon` appends a precommit-removal
 event (never writer-deletes a live precommit body) via reliable `mutateShard`.
- `requireAlive` gates every build op on `epoch == store->liveWriterEpoch()`, so a build minted under a
 fenced-out incarnation fails `ABORTED`.
- `observeAndAdmit` guards the `hr.size - header_len` subtraction against unsigned underflow
 (`CORRUPTED_DATA`), unlike the envelope's ENV-1.

---

## Batch 6 — GC subsystem

Files: `CasGc.{h,cpp}` (2203), `CasBlobInDegree.cpp` (350), `CasRetireView.cpp` (95), `CasFsck.cpp` (373),
`CasOrphanManifestSweep.cpp` (326), `CasGcScheduler.cpp` (242), `CasGcOutcomes.cpp` (145),
`CasGcShardPlan.cpp` (60), `CasEvent.cpp` (95).

### SCHED-1 [BUG, Med] — a resurrected zombie leader's heartbeat pulse clobbers the live leader's `gc/hb` owner, defeating the B160 anti-false-steal guard

`CasGcScheduler.cpp:217–240` runs `heartbeatLoop` gated only on the local `i_am_leader` atomic, which is
updated **only at the end of a round** (`:185`) or on a round exception (`:211`). `Gc::pulseHeartbeat`
(`CasGc.cpp:1837–1851`) **unconditionally** overwrites `gc/hb` with `owner = gc_id` and `++hb_seq` — it never
re-checks that this `gc_id` still owns the `gc/state` lease. Scenario: leader D stalls (GC pause / long I/O);
leader L legitimately steals the lease (`acquireOrRenewLease` steal path `:2050–2061`, bumps `fence_seq`); D
resumes and, for up to one round `interval`, its `hb_thread` keeps pulsing `gc/hb` with `owner = D`. A
follower F evaluating the steal predicate checks `hb.owner == current.lease.owner` (`:2036`) — now L — but the
latest pulse set owner = D, so `hb_alive` is **false**. If L is busy in a long round (its `lease.seq` frozen,
which is the exact case B160's heartbeat exists to cover), F also sees `incumbent_renewed == false` and
**steals the lease from the live leader L**. The data plane is safe (round-commit CAS on `gc/state` is
token-guarded → the loser's round `ABORTED`s; pre-CAS deletes are idempotent `delete_pending` replays), but
B160's whole purpose — preventing false steals during long rounds — is defeated by a zombie pulser, causing
lease churn, extra `fence_seq` bumps, and wasted/aborted rounds. **Fix:** gate `pulseHeartbeat` on current
lease ownership (re-read `gc/state`, or CAS `gc/hb` only if still the `gc/state` owner), or make the
follower's liveness check tolerant of a stale owner without dropping the true leader.

### GC-1 [BUG, Low] — the T0 post-CAS hand-off reclaim can permanently strand a whole `gc/gen/ /` prefix on a crash, with no automated reclaimer

`runRegularRound` R5b (`CasGc.cpp:371–404`) reclaims a generation the wholesale prune skipped-while-referenced
**only** on the round that first moves the live ref off it, and only *after* the round CAS committed (R5,
`:362`). The code's own comment (`:379–381`) concedes: a crash between the CAS and the hand-off leaks the
prefix, and "the cursor already advanced, so a plain retry will NOT re-attempt it; fsck is the backstop."
But (a) `pruneSupersededGenerations` advanced `snap_pruned_through` past `g` (`:1190`) so the wholesale prune
never revisits it; (b) the next round captures `parent_seal_runs` from the **new** state (ref already moved
off `g`, `:192–194`) so the hand-off never re-triggers for `g`; and (c) **fsck only reports, never reclaims**
(see below). So `g`'s entire prefix (fold seal, retired/outcomes sets, all shard runs) is orphaned
permanently — bounded per incident but a monotonic GC-metadata leak across such crashes with no automatic
cleanup. **Fix:** make the hand-off crash-recoverable (e.g. derive the reclaim target from a durable diff of
referenced-generations vs `snap_pruned_through` at round start, so a retry re-attempts it).

### INT-3 [confirmed at code] — fsck is diagnostic-only; it never repairs

`CasFsck.cpp:runFsck` walks authoritative refs (never GC state, `:112`), HEAD-confirms reachable blobs
against LIST lag before declaring loss (`:198–205`), and classifies every present object
(Reachable/Dangling/PendingGc/AwaitingGc/Unaccounted/Unreachable). It contains **no** delete/repair path.
Dangling (committed ref → missing manifest body, or manifest → missing blob = data loss) and "Unaccounted"
(present-but-unreferenced, not in any GC view — a candidate leak) are **surfaced only**. Combined with GC-1,
there is no automated reclaimer for stranded GC-internal prefixes; recovery of real dangles is the manual
`SYSTEM CONTENT ADDRESSED GC REBUILD`.

### RF-1 [reconfirmed reachable] — the RunFile record-length over-read is reachable from the GC fold and fsck

`CasBlobInDegree.cpp` (`PriorEdgeCursor`/`zeroInDegree`/`inDegreeInGeneration`) and `CasFsck.cpp:264–275`
all stream run objects via `RunFileReader::next`, which is the Batch-1 RF-1 unchecked `klen`/`plen` path.
So a crafted/corrupt run block (pool-write access) reaches the OOB read during a GC round and during fsck,
not only via manifest embeds. Reinforces RF-1's severity.

### RSC-1 [generalizes] — `decodeOutcomeLog` shares the unguarded protobuf parse

`CasGcOutcomes.cpp:119` `ParseFromArray(data.data(), static_cast (data.size()))` with no
`CodedInputStream` size/recursion limit and an unchecked `int` cast — same class as RSC-1. (Its enum decoders
are correctly fail-closed, unlike GS-1.)

### BID-1 [Info] — GC-artifact determinism is load-bearing and fails closed on any divergence

`putDeterministicArtifact` (`CasBlobInDegree.cpp:129–140`) `putIfAbsent`s fold seals, in-degree runs, and
cleanup bundles, and throws `CORRUPTED_DATA` if an existing occupant's bytes differ. So *any* non-determinism
in the encode (map iteration order, unsorted input, protobuf non-canonical output) between two leaders
replaying the "same" attempt wedges GC with a spurious corruption error. The code defends this everywhere
(`std::stable_sort` of deltas `:169`, sorted cleanup rows `:1074`, sorted prior_retired gate `:157`), so it
is currently sound — but it is a fragile global contract worth a determinism regression test.

### Batch-6 [OK] notes

- `foldDeltasIntoGeneration` treats "prior retired list not sorted by hash" as a **release gate**
 (`CORRUPTED_DATA`, `:157`), and the two-phase graduation (`settleEntry` `:195–216`) correctly honors
 `suppress_destructive` (clamp-suppressed passes carry pending UNCHANGED, never graduate/redelete), matching
 the audited ack-floor protocol.
- `RetireView::refresh` reads `gc/state` first and resolves the per-shard retired refs from that same body
 (round + refs are one atomic read); an absent ref/object contributes *less* condemnation (writer-safe).
- The one-pass round structure holds: the SINGLE `gc/state` CAS (R5) is the only commit; pre-CAS deletes are
 only prior-published `delete_pending` (idempotent); R5b/R6 are best-effort post-CAS (leak-to-fsck, never
 dangle) — modulo GC-1.
- Fold fail-closed guards are intact: missing adopted fold seal under a live `gc/state` ⇒ `CORRUPTED_DATA`
 (`:522`), baseline-trim-proof guard (`:712–725`), incarnation-mismatch ABA cursor reset (`:690–704`),
 clamp-below-unresolvable-event + round-wide `suppress_destructive` (`:739–759`, `:871`).
- `reclaimDroppedShards` is layered fail-closed (refs-empty + tombstone-last + fully-folded + incarnation
 match + no live owner binding + fresh-GET token) — the activated-precommit blob-leak (Guard 4) is closed.
- `reclaimAbandonedPrecommit` judges death only by the durable watermark fact (never the K=2 frozen-seq
 heuristic), and its `shard_version` arithmetic yields contiguous transition versions.
- `CasGcShardPlan::manifestCleanupShard` hashes the **qualified** `ManifestId` (ns + full ref), avoiding the
 `SabotageKeyByRefNotId` cross-namespace merge hazard.

### Batch-6 minor / info

- SCHED-2 [Low]: `runOneRoundNow` builds a **fresh** `Gc` each manual call → `has_observation=false` →
 `incumbent_renewed` is forced true → a manual driver can never *steal* a stale lease (only take a free one),
 and, sharing `gc_id` with the scheduled `loop()`, both can believe they hold the lease and run concurrent
 rounds (one `ABORTED`s at the CAS; non-corrupting). Matches the scheduler's "stable observer required" note.
- `discoverUniverse` (`:1227`) requires read-your-writes LIST on `cas/refs/`; the code annotates RustFS as
 "to confirm in soak" — an unverified backend-consistency dependency (data-plane-safe: publish re-observes).
- `retiredLogicalSize` (`:66–75`) throws `CORRUPTED_DATA` if a blob object is smaller than
 `blob_header_len`; reached inside the fold's `head_blob`, so such a blob (BUILD-2 / STORE-2 territory)
 wedges the GC round every pass until repaired — fail-closed but a per-blob wedge.

---

## Batch 7 — metadata-storage integration (wiring layer)

Files: `ContentAddressedMetadataStorage.cpp` (1100), `ContentAddressedTransaction.cpp` (1250),
`PartPathParser.cpp` (284).

### PPP-1 [BUG, Low] — `looksLikePartDir` false-positives on non-Atomic table/dir names ending in three numeric underscore groups

`PartPathParser.cpp:54–86` classifies a path component as a part directory iff its last three
`_`-separated groups are all decimal (the `_ _ _ ` grammar). On a **non-Atomic** database (no
uuid anchor, so the right-to-left grammar fallback runs, `:121–124`), a table or partition literally named
like `events_2024_01_01` matches (`2024`,`01`,`01` all numeric). A path such as
`data/db/events_2024_01_01/columns.txt` is then parsed with `part_name = events_2024_01_01` and
`file = columns.txt`, misrouting a **table-level** file as a **part** file. Only affects Ordinary/non-Atomic
databases (deprecated), hence Low; on Atomic the uuid anchor takes precedence and is safe.

### MW-1 [HARDENING, Med] — the relink/rename receiver trusts sender/source `entry.blob_size`; only presence is revalidated (payload_digest ignored, chains MC-1 + STORE-2)

`adoptPartFromManifest` (`ContentAddressedMetadataStorage.cpp:1032–1098`) decodes a transferred
`PartManifest`, explicitly **ignores** `payload_digest`/`ManifestRef`/`root_namespace_id` (`:1039`), and
republishes using **only the entries** — trusting each `entry.blob_size`/`entry.path` verbatim.
`promote` HEAD-revalidates that every referenced blob is **present and not condemned**, but does **not**
check that `entry.blob_size` matches the blob's actual envelope logical size. A buggy/hostile sender can
therefore make the receiver publish a manifest with an inflated `blob_size`; a later read uses that size for
the view window (`locate`/`getBlobViewPlan`), reading past the real payload (STORE-2 territory). Same trust
holds for the intra-server `republishRef` (`:143–176`). Interserver fetch is normally trusted-cluster, so
Med not High — but combined with MC-1 (the digest is never verified even locally) manifest-entry integrity is
unchecked end-to-end. **Fix:** verify `entry.blob_size` against the blob envelope's logical size at
adopt/promote (and/or re-verify `payload_digest`).

### MW-2 [Info] — `getStorageObjects` returns the blob key with payload length but no header offset

`getStorageObjects` (`:866–907`) returns `StoredObject(location.key, path, location.length)` — the payload
*length* but **no** offset, and (for a part blob) the **raw** pool key (not `physicalKey`-adjusted, unlike
`getBlobViewPlan:990` and `readBlobPayload:1002`). The design routes all byte reads through
`getBlobViewPlan`, which applies `[offset, offset+length)`. A consumer that instead reads bytes straight from
this `StoredObject` gets header-shifted bytes on S3 (Native) or a fail-loud missing key on Local (raw key
unresolved). Latent trap, not a live bug given the documented read path.

### TXN-2 [BUG / atomicity gap, Med] — RENAME TABLE is a non-atomic multi-op move that can leave the table split across namespaces

`moveDirectory` table→table (`ContentAddressedTransaction.cpp:875–901`) republishes every ref + verbatim
file into the new namespace then `dropNamespace`s the old one, with **no in-call compensation**: a throw
mid-loop (`:890`) logs and rethrows, leaving the table **split** across the old and new namespaces. Recovery
relies on the operation being re-driven (each step is idempotent). This is a real divergence from a normal
disk where RENAME TABLE / EXCHANGE is a single atomic directory rename; if the DDL is not retried, some parts
remain under the old namespace and some under the new. Documented as out-of-scope (B126) but it is a genuine
correctness gap for a common Atomic-DB operation.

### TXN-1 / TXN-3 / TXN-4 [known/documented, reconfirmed at code]

- **TXN-1** commit (`:323–368`) is **not** atomic across multiple parts: it publishes parts sequentially and,
 on a throw after some published, best-effort drops only the refs *it* created (absent-before). A rollback
 drop that itself fails leaves GC-reclaimable debris — a partial commit vs the disk layer's all-or-nothing
 expectation (restores the wiring contract, not a CAS invariant).
- **TXN-3** `unlinkFile` of a **committed content file** is a deliberate **fail-open no-op** (`:1189–1231`):
 correctness rests on the load-bearing MergeTree invariant that a part is removed as a whole via
 `removeDirectory()`. Any future path that surgically deletes one committed content file and expects
 it gone becomes a silent correctness bug.
- **TXN-4** B151 publishes the final part ref at the **lock-free rename**, *before* the transaction's commit
 decision (`moveDirectory:1012–1016`); the dtor drops it on abort (`:101–110`). A concurrent read / replica
 fetch during the commit window can observe a part that is later rolled back (replicated ZK reconcile then
 detaches the unexpected part).

### Batch-7 [OK] notes

- `~ContentAddressedTransaction` is exception-safe: always `cleanupPendingTempFiles()`, drops early-published
 refs, and `abandon()`s every open build, all under `catch(...)` so the dtor never throws.
- `publishStaging` ordering is safe: `stageManifest → precommitAdd → upload pending blobs → promote`. The
 precommit reserves reachability before promote's fail-closed blob revalidation; B189 filters orphaned
 pending blobs (entry removed by unlink/replace) out of the upload set by staged-tree hash.
- `writeFile`'s inline-overflow spill uses `SCOPE_EXIT` to drop the temp file unless `stageBlobPartFile`
 takes ownership (mirrors `CaContentWriteBuffer`), so no scratch leak on a staging throw.
- `moveDirectory`/`moveFile` mutable-file merges are **source-wins** and **fail loud** on a differing-bytes
 collision (`:969–974`) rather than silently dropping a just-written file (lost-update guard).
- `startup` fail-closes the mutating surface in read-only mode and loudly warns that the Local/emulated
 backend is single-process-only (shared-pool misconfig is undetectable by the probe — confirms B25).

## cas-concurrency-audit.md

Language: Markdown

# CAS — Concurrency & Memory-Safety Audit (C++ level)

Scope: the in-process concurrency of `Cas::Store` and its helpers (`MountLeaseKeeper` /
`SingleWriterSlot`, the self-remount machinery, the flat-combining shard queue, the read caches).
This is **distinct** from the protocol-level interleaving audit: here the "actors" are OS threads and
the objects are C++ mutexes, atomics, `std::function`s, `unique_ptr`s, and thread handles — the bug
classes protocol reasoning structurally cannot see (data races, lock inversion, use-after-free,
teardown ordering, unbounded in-memory growth).

Verdict legend: **BUG** (reachable), **LATENT** (real defect, currently masked by an unenforced
invariant/timing), **CLEAN** (verified safe), **GROWTH** (unbounded memory, not a race).

---

## 1. Inventory of shared concurrency state

**Threads**
- `MountLeaseKeeper` background renewer (one; started iff `background_watermark`). Runs `renewOnce`,
 and on failure `onRenewFailed → on_lost` = `{tripMountLost; scheduleRemount}`.
- `Store::remount_thread` — self-remount loop, spawned by `scheduleRemount` (from the keeper thread).
- GC scheduler thread (external, `CasGcScheduler`) — drives GC rounds; interacts with `Store` only via
 public methods and S3, out of this TU's shared memory.
- Foreground threads: query/insert threads calling `resolveRef`/`readManifest`, `mutateShard`
 (via `Build`/`Gc`), `startBuild`, etc.

**Mutexes (9 in `Store` + keeper's 2)**
`shard_queue_mutex`, `view_gate` (shared_mutex), `builds_mutex`, `remount_mutex`,
`remount_thread_mutex`, `remount_cv_mutex`, `shard_decode_cache_mutex`, `shard_inflight_mutex`,
`manifest_cache_mutex`; `RetireView::mutex` (shared_mutex); keeper `state_mutex`, `background_mutex`.

**Atomics**
`mount_fence.deadline_boot_ms` (u64), `mount_fence.lost` (bool), `live_writer_epoch` (u64),
`remount_running` (bool), `remount_stop` (bool).

**Condition variables**
`ShardMutationQueue::cv` (per queue), `remount_cv`, keeper `wakeup`.

**Non-atomic shared mutable state of interest**
`mount_keeper` (`unique_ptr`, reassigned by the remount thread), `event_sink_` (`std::function`, set
post-open), `process_epoch` (set once at open), `shard_write_seq` (map under cache mutex).

---

## 2. Lock-ordering graph — CLEAN

Observed acquisition orders:

```
view_gate(shared, whole mutateShard)
   └─▶ shard_queue_mutex ─▶ shard_decode_cache_mutex
   └─▶ RetireView::mutex           (isCondemnedToken / round)
refreshViewForBeat: view_gate(exclusive) ─▶ RetireView::mutex   (refresh)
coalescedReadShardDecoded: shard_inflight_mutex ─▶ shard_decode_cache_mutex
keeper: prepareRenew() [minActive→builds_mutex; refreshViewForBeat→view_gate] runs
        BEFORE state_mutex is taken (doStart/renewOnce), so state_mutex never nests Store locks
```

- The `view_gate → RetireView` order is the **same** on the writer (`mutateShard`) and beat
 (`refreshViewForBeat`) paths — no inversion. The code comment even pins it:
 *"Lock order (never inverted elsewhere): view_gate, then RetireView's internal mutex."*
- The keeper deliberately computes its renew payload **before** taking `state_mutex`
 (`doStart`/`renewOnce` — "never hold state_mutex across the subclass callback"), so the keeper's
 `state_mutex` is never held while entering `Store`'s `view_gate`/`builds_mutex`. This kills the
 classic keeper↔Store inversion.
- `stopBackground()` moves the thread handle out under `background_mutex` and joins **after**
 releasing it → no join-under-lock deadlock.

**No lock cycle found.** The deadlock "SAFE" verdict from the fault-injection audit is confirmed at
the code level.

---

## 3. Findings

### C1 — Teardown UAF / `std::terminate` race: keeper stopped *after* the remount thread is joined; `scheduleRemount` ignores `remount_stop` *(BUG, Med)*

`~Store` (order):
```
remount_stop.store(true); remount_cv.notify_all();
{ lock remount_thread_mutex; if (remount_thread.joinable()) remount_thread.join(); }   // (A)
...
if (mount_keeper) mount_keeper->stop();     // (B) — joins the keeper bg thread HERE
```
The keeper background thread is **still running between (A) and (B)**. `scheduleRemount` does **not**
check `remount_stop`:
```
void Store::scheduleRemount() {
    if (!config.background_watermark) return;
    if (remount_running.load()) return;
    std::lock_guard g(remount_thread_mutex);
    if (remount_running.load()) return;
    if (remount_thread.joinable()) remount_thread.join();
    remount_running.store(true);
    remount_thread = ThreadFromGlobalPool([this]{ ... });   // spawns on `this`
}
```

**Race trace.** During teardown, in window (A)→(B), the keeper thread's renew fails →
`onRenewFailed → on_lost → scheduleRemount()`. `background_watermark` is true, `remount_running` is
false, the original remount thread was already joined (non-joinable) → `scheduleRemount` **spawns a
NEW `remount_thread` bound to `this`**. The dtor has already passed its join at (A), so **nothing
joins this new thread.** The new thread body touches `this` (`remount_stop.load()`,
`remount_running.store(false)`) concurrently with the rest of `~Store` and after the `Store`'s
atomics are destroyed → **use-after-free**; and destroying the still-joinable `remount_thread`
member follows `std::thread` semantics → **`std::terminate`**.

Narrow (needs a renew failure precisely in the teardown window) but reachable, and it crashes on
shutdown — exactly when logs are least useful.

**Fix (either):** (a) `scheduleRemount` must early-return when `remount_stop.load()` is set; and/or
(b) `~Store` must stop the keeper (the *only* caller of `scheduleRemount`) **before** finalizing the
remount thread. (b) is the more robust ordering: stop keeper → set `remount_stop` → join remount
thread.

### C2 — `mount_keeper` (`unique_ptr`) reassigned without synchronization *(LATENT)*

`tryRemountOnce` (remount thread) does `mount_keeper->stopBackground(); mount_keeper = make_unique<…>();`
— destroying the old keeper and rebinding the pointer **with no lock on `mount_keeper` itself**.
`renewWatermarkOnce()` reads and dereferences `mount_keeper` on a *foreground* thread. If both ran
concurrently: a data race on the pointer plus a **use-after-free** (foreground calls `renewOnce()` on a
keeper the remount thread just freed).

Currently **not reachable** only because of an unenforced, config-based mutual exclusion:
- Production: `background_watermark = true` → the keeper renews itself on its own thread; the
 foreground `renewWatermarkOnce` is **not** wired (it's the test seam).
- Tests: `background_watermark = false` → `scheduleRemount` early-returns → **no remount thread** → no
 reassignment, and tests drive `renewWatermarkOnce` explicitly.

So the two mutators of `mount_keeper` never coexist — **by configuration, not by construction.** Nothing
documents or asserts this. Wiring `renewWatermarkOnce` into any foreground path with
`background_watermark` on would be an instant UAF. **Fix:** guard `mount_keeper` with a mutex (or an
`atomic<shared_ptr>`), or assert the invariant.

### C3 — `event_sink_` published after background threads may run (data race on `std::function`) *(LATENT)*

`Store::open()` starts the keeper background thread (when `background_watermark`) **inside** open;
the wiring calls `cas_store->setEventSink(...)` **after** open returns. The keeper's beat path
(`refreshViewForBeat`) calls `emitEvent`, which reads `event_sink_`. So `setEventSink` (main thread,
`std::function` move-assign) races the keeper thread's read of `event_sink_` — a data race on a
`std::function` (non-atomic; a torn read can call a half-assigned target → crash).

Masked only by **timing**: the keeper's first background beat is ~`mount_renew_period` (~10 s) after
start, long after `setEventSink` completes; and the synchronous `start()`-time beat runs on the opening
thread before the sink is set (sink null → no emit). There is **no happens-before** edge on
`event_sink_` between the two threads, though — TSan would flag it. **Fix:** set the sink **before**
starting any background thread, or protect `event_sink_` with the same discipline as other shared state.

### C4 — `shard_write_seq` grows unbounded (never pruned) *(GROWTH, Low)*

`shard_decode_cache` is bounded (wholesale clear at `SHARD_DECODE_CACHE_MAX_ENTRIES = 16384`) and
`dropNamespace` explicitly evicts a dropped namespace's decode-cache entries — **but the sibling map
`shard_write_seq` (under the same mutex) is never pruned.** `dropNamespace` erases
`shard_decode_cache[rootShardKey(ns,shard)]` for each shard but leaves `shard_write_seq` entries
behind:

```1447:1451:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Core/CasStore.cpp
    {
        std::lock_guard lock(shard_decode_cache_mutex);
        for (uint64_t shard = 0; shard < meta.root_shards; ++shard)
            shard_decode_cache.erase(pool_layout.rootShardKey(ns, shard));
    }
```

The header claims `shard_write_seq` is *"Bounded by distinct (namespace, shard) pairs"* — but that is
**all-time** distinct pairs, not **live** ones. A server with high namespace churn (temp tables,
per-backup shadow namespaces, `detached/ ` folds, TTL moves, frequent CREATE/DROP) accumulates a
`shard_write_seq` entry per `(namespace, shard)` it ever wrote and never releases them → a slow,
monotone heap leak keyed by lifetime table count. It is kept intentionally monotone across the decode
cache's wholesale clear, so it also escapes that bound. **Fix:** erase the matching `shard_write_seq`
entries in `dropNamespace` alongside the decode-cache eviction (and/or on the wholesale clear, migrate
the counters into the entry so they share the cache's bound).

---

## 4. Verified CLEAN (no action)

- **Lock ordering** — single consistent order, no cycle/inversion (§2).
- **Atomic memory orderings** — `live_writer_epoch` release/acquire; `mount_fence` publishes
 `deadline_boot_ms`(release) *before* `lost`(release) in `armMountFence`, and `mayMutate` reads
 `lost`(acquire) then `deadline`(acquire) — so observing `lost==false` implies the fresh deadline is
 visible. Correct release/acquire pairing throughout; the boot-clock choice (`CLOCK_BOOTTIME`) is the
 deliberate, correct one for the suspend-resume fence.
- **`remount_cv` predicate** — `wait_for` uses predicate `[]{return remount_stop.load();}` reading the
 atomic, and a bounded timeout; setting `remount_stop` without holding `remount_cv_mutex` cannot cause
 a lost-wakeup **hang** (predicate re-check + timeout). Safe.
- **`remount_running` re-entrancy guard** — the keeper thread's `on_lost → scheduleRemount` early-returns
 on `remount_running==true`, so it never blocks in `stopBackground` joining itself; no self-join
 deadlock between the remount thread and the keeper thread it is tearing down.
- **`stopBackground`/`doTerminate`** — join happens before `state_mutex`, and the handle is moved out
 under `background_mutex` then joined after release — no deadlock, no double-join.
- **Read caches** (`shard_decode_cache`, `manifest_cache`, `shard_inflight`) — all accesses under the
 correct mutex; cached objects are `const shared_ptr` (immutable, safely shared across threads);
 single-flight promise/future correctly erases the in-flight entry on both success and exception.
- **`flushShardBatch`** — per-closure snapshot rollback on throw; `done`/`error`/`committed_version`
 written under `shard_queue_mutex` before `cv.notify_all()`; no data on items touched outside the lock.
- **`enable_shared_from_this`** — `startBuild` calls `shared_from_this()` only while the `Store` is
 owned by a live `StorePtr` (Builds hold a `StorePtr`, keeping the `Store` alive), so the keeper's raw
 `Store*` (`raw`) stays valid for the keeper's whole lifetime **except** the C1 teardown window.

---

## 5. Summary

| # | Finding | Class | Severity | Reachable today? |
|---|---|---|---|---|
| C1 | Teardown spawns an unjoined remount thread on a destroying `Store` (`scheduleRemount` ignores `remount_stop`; keeper stopped after remount join) | UAF / terminate | **Med** | Yes (narrow race) |
| C2 | `mount_keeper` `unique_ptr` reassigned without synchronization vs `renewWatermarkOnce` | Data race / UAF | Low | No (config mutual-exclusion, unenforced) |
| C3 | `event_sink_` published after keeper thread start (`std::function` data race) | Data race | Low | No (timing-masked) |
| C4 | `shard_write_seq` never pruned on `dropNamespace` | Unbounded growth | Low | Yes (churny workloads) |

**Headline.** The steady-state concurrency is genuinely solid: one clean lock order, correct
release/acquire atomics, immutable shared cache payloads, and a keeper that carefully evaluates its
Store-touching callbacks off its own lock. The defects are all in **lifecycle**, not steady state —
which fits the earlier impression that the hard steady-state paths were reasoned about hardest. The one
worth fixing now is **C1** (a shutdown-time UAF/terminate whose trigger is a renew failure during
teardown); the fix is a one-liner (`scheduleRemount` checks `remount_stop`) plus reordering the dtor to
stop the keeper before finalizing the remount thread. **C4** is a slow leak worth a two-line fix in
`dropNamespace`. **C2/C3** are latent — safe today by unenforced invariants; cheap to make safe by
construction (guard `mount_keeper`, set `event_sink_` before starting threads).

## cas-coverage-map.md

Language: Markdown

# CAS Audit Coverage Map — What We Checked vs. What's Left

A read of the broader ClickHouse storage-touching surface (`IDisk`/`IMetadataStorage`/`IObjectStorage`
consumers) mapped against the 21 audit files produced so far. Goal: find subsystems that interact with a
disk and that **no audit has examined against CAS yet**.

Key structural fact grounding the gaps: **CAS is a MergeTree-shaped metadata storage.**
`ContentAddressedTransaction::writeFile` only handles (a) MergeTree part-file paths, (b) table-level
verbatim files (`format_version.txt`, `deduplication_logs/`), and (c) loose mountpoint probe files;
**anything else throws `NOT_IMPLEMENTED`**. `chmod`/`createMetadataFile`/`generateObjectKeyForPath` are
`notYet(...)`, `truncateFile` is a no-op, and append is emulated by read-modify-rewrite for verbatim
files only. So any consumer needing generic append/random-write/arbitrary-file semantics is out of scope
by construction — but **nothing guards against pointing such a consumer at a CAS disk.**

---

## Part A — What we already covered (21 files)

| # | Audit file | Scope |
|---|---|---|
| 1 | `cas-write-protocol-audit.md` | Write state-space + faults (W1–W2, W-N*) |
| 2 | `cas-read-protocol-audit.md` | Read state-space + faults (R1–R4, F-N*) |
| 3 | `cas-gc-protocol-audit.md` | GC state-space + faults (G-N*) |
| 4 | `cas-interleaving-audit.md` | 3-way write/read/GC interleaving (X1–X3) |
| 5 | `cas-jepsen-anomaly-audit.md` | Adya/Elle/session/SI anomalies (J1–J5) |
| 6 | `cas-security-audit.md` | STRIDE (SEC-1..7) |
| 7 | `cas-concurrency-audit.md` | C++ mutex/atomic/lifetime (C1–C4) |
| 8 | `cas-crash-consistency-audit.md` | Durability recovery matrix (DUR1) |
| 9 | `cas-upgrade-compat-audit.md` | Mixed-version / on-S3 format compat |
| 10 | `cas-idisk-contract-audit.md` | IDisk/IMetadataStorage conformance |
| 11 | `cas-performance-audit.md` | S3 request cost & scalability |
| 12 | `cas-test-coverage-fuzzing-audit.md` | Test gaps & decoder fuzzing |
| 13 | `cas-tla-fidelity-audit.md` | TLA+ spec-to-code fidelity |
| 14 | `cas-mergetree-part-support-audit.md` | Part types: wide/compact/patch/projection/detached/frozen |
| 15 | `cas-alter-merge-mutation-audit.md` | ALTER families, merges, mutations |
| 16 | `cas-datatype-agnosticism-audit.md` | All column data types |
| 17 | `cas-encryption-audit.md` | DiskEncrypted vs S3 SSE |
| 18 | `cas-tier1-audit.md` | Replication, lifecycle/reclamation, integrity, query-MVCC |
| 19 | `cas-tier2-audit.md` | System tables, FS cache, tiering/TTL, INSERT dedup |
| 20 | `cas-tier3-audit.md` | Merge engines, txns, BACKUP/RESTORE, startup, config |
| 21 | `cas-tier4-audit.md` | Object-store compat, error/stress, observability |

**Effectively fully covered:** the MergeTree *data-plane* (parts, merges, mutations, ALTERs, projections,
skip-index files as part files, replication relink, TTL, backup/freeze, GC, durability, formats,
concurrency, security, data types, encryption, perf, observability).

---

## Part B — Coverage map of ClickHouse storage consumers

Legend: ✅ covered · 🟡 partial · ❌ not audited · ⛔ out-of-scope-by-design but **ungated**

| Subsystem | Touches disk? | Status | Note |
|---|---|---|---|
| MergeTree part read/write/merge/mutate | yes | ✅ | audits 14–16, 18 |
| ReplicatedMergeTree fetch/queue/sync | yes | 🟡 | Tier 1 RPL-* (relink covered; sync/quorum/cloneReplica untested) |
| Projections / skip indexes (minmax/set/bloom) | yes (part files) | ✅ | part-support audit |
| **UniqueKey / upsert MergeTree (SSTIndex + DeleteBitmap)** | yes (mutable per-part bitmaps) | ❌ | **NEW GAP — see G1** |
| **Full-text / Text index (GIN), vector-similarity index** | yes (special index files) | ❌ | **NEW GAP — see G2** |
| **Cross-disk partition ops (MOVE/REPLACE/ATTACH ... TO DISK/VOLUME)** | yes | 🟡 | code says "cross-disk is a follow-up to verify"; **G3** |
| **Log family (StorageLog / StripeLog / TinyLog)** | yes (append .bin/.mrk) | ⛔❌ | **NEW GAP — G4** |
| **StorageSet / StorageJoin (persistent)** | yes (.bin on disk) | ⛔❌ | **NEW GAP — G4** |
| **StorageMemory (with disk persistence), StorageFile** | yes | ⛔❌ | **NEW GAP — G4** |
| **StorageEmbeddedRocksDB / StorageKeeperMap** | yes (RocksDB/local) | ⛔❌ | **NEW GAP — G4** |
| **Distributed engine async-insert spool** | yes (appended .bin) | ⛔❌ | **NEW GAP — G5** |
| **Temporary data on disk (external GROUP BY/ORDER BY/JOIN spill, `tmp` disk)** | yes | ⛔❌ | **NEW GAP — G6** |
| **System log tables (query_log, part_log, …) placed on CAS** | yes (MergeTree) | ❌ | tiny-part storm; **G7** |
| **Dictionaries with SSD/disk cache layout** | yes (random-write cache) | ⛔❌ | **G8** |
| **clickhouse-disks / clickhouse-local tooling** | yes (copy/link/write) | 🟡 | traversal supported per header; write/copy/link ops untested; **G9** |
| **Refreshable/Materialized View target swaps (EXCHANGE TABLES)** | yes | ❌ | atomic rename/exchange on CAS; **G10** |
| **Lightweight DELETE mask + DeleteBitmap apply-on-read** | yes | 🟡 | patch parts covered; delete-bitmap path not; **G1/G2** |
| **Atomic DB `store/ ` symlink layout & metadata_path** | DB metadata usually local | 🟡 | namespace mapping covered; DB-level .sql not on CAS |
| **DiskWeb / static read-only / cache-disk layering over CAS** | yes | ❌ | composition untested; **G11** |
| **RESTORE of Packed storage-type parts** | yes | ❌ | flagged in part-support; still untested; **G12** |
| **`SYSTEM` disk ops (RESTART DISK, DROP CACHE, SYNC FILE CACHE, UNFREEZE)** | yes | 🟡 | CAS GC/REBUILD covered; generic disk SYSTEM ops untested |

---

## Part C — Newly identified gaps (prioritized)

### G1 (High) — UniqueKey / upsert MergeTree: DeleteBitmap + SSTIndex
`src/Storages/MergeTree/UniqueKey/` implements primary-key upsert via an **SST primary-key index** and a
**per-part delete bitmap** that is **rewritten in place** (`DeleteBitmapFileOps.cpp`: write tmp →
`replaceFile(tmp, final)`) every time rows are deleted/superseded. On CAS the delete-bitmap file is **not**
in the mutable-per-part set (`{uuid.txt, txn_version.txt, metadata_version.txt}`), so each `replaceFile`
routes through the whole-part republish path → **a new manifest per delete-bitmap update**. This is a
hot-rewrite pattern CAS was not designed for:
- Correctness: does `replaceFile` of a committed content file correctly produce a new ref that still
 shares all *other* blobs? (Ties to the "surgical single committed-file unlink is a latent no-op"
 finding.) **Untested.**
- Perf: high-frequency upsert → manifest churn + GC pressure.
- The SST index file lifecycle (rebuild on merge) on CAS is likewise unexamined.
**This is the single most important uncovered MergeTree feature.**

### G2 (Med) — Full-text (Text/GIN) & vector-similarity indexes
`TextIndexUtils`/`TextIndexAnalyzer` (GIN posting lists) and vector indexes produce index files with their
own build/merge lifecycles and, for GIN, potentially large multi-file structures. They land as part files
(so *storage* likely works), but their build-during-merge, read-during-query, and MATERIALIZE INDEX paths
on CAS are untested — particularly whether posting-list/segment files exceed inline caps and stream as
blobs correctly, and whether they dedup sensibly.

### G3 (Med) — Cross-disk partition operations
`MergeTreeData.cpp` explicitly gates partition commands on CAS and **notes in-code**: "only same-disk
`MOVE ... TO TABLE` is verified here — cross-disk is a follow-up to verify." So `MOVE/REPLACE/ATTACH
PARTITION ... TO DISK/VOLUME` across disks (byte-copy `clonePart` path) is a **known-unverified** path.
Ties to Tier 2 TIER-1.

### G4 (Med, mostly out-of-scope but ungated) — Non-MergeTree table engines on a CAS disk
Log/StripeLog/TinyLog, Set, Join, persistent Memory, File, EmbeddedRocksDB, KeeperMap all issue generic
append/random-write/arbitrary-file operations that CAS answers with `NOT_IMPLEMENTED`/no-op/misroute.
There is **no guard** that stops an operator from putting such a table on a CAS disk (via `disk=` or a
storage policy) — it fails at runtime, possibly mid-write. **Recommendation: fail-closed at table
creation** if the engine is non-MergeTree and any target disk `isContentAddressed()`.

### G5 (Med, ungated) — Distributed engine async-insert spool
`StorageDistributed` spools pending rows to appended `.bin` files under the table's disk. On CAS this hits
the same append/arbitrary-file wall. Same guard recommendation as G4.

### G6 (Med, ungated) — Temporary data on disk (spill)
External GROUP BY / ORDER BY / JOIN spill and `tmp`/`temporary_data_in_cache` disks need
append/random-write scratch files. A CAS disk cannot serve as a `tmp` disk. **Recommendation: reject CAS
in `tmp_policy`/temporary-data disk configuration.**

### G7 (Low) — System log tables on CAS
Placing `query_log`/`part_log`/etc. (MergeTree) on a CAS disk works mechanically but produces a **tiny-part
storm** (frequent small inserts) → manifest/ref churn + GC load, and inflated logical `bytes_on_disk`
(SYS-1). Operationally discouraged; document.

### G8 (Low, ungated) — Dictionaries with SSD/disk cache
`SSDCacheDictionaryStorage` uses random-access cache files — incompatible with CAS. Ungated. Same guard
family as G4/G6.

### G9 (Low) — clickhouse-disks / clickhouse-local tooling
The metadata storage advertises top-down traversal support (`listLiveTreeChildren`) so read-only
navigation works, but tool-driven `write-file`/`copy`/`link`/`remove` operations on a CAS disk are
untested and will hit the same NOT_IMPLEMENTED surface for non-part shapes.

### G10 (Low) — MV target swaps / EXCHANGE TABLES / RENAME on CAS
`EXCHANGE TABLES` and MV target rotation rely on atomic rename/exchange. `republishRef`/`moveDirectory`
cover RENAME TABLE (DUR2 filed earlier); the *atomic two-table EXCHANGE* on CAS is not separately audited.

### G11 (Low) — Disk layering (cache/web/static over CAS)
Composing a `cache` disk or read-only/web wrapper *over* a CAS disk (vs S3 SSE / DiskEncrypted already
covered) is untested; the FS-cache-over-CAS composition (CACHE-1/2) is analyzed but not the full
wrapper-disk stack.

### G12 (Low) — RESTORE of Packed storage-type parts
Reiterated from the part-support audit: Packed-container parts arriving via RESTORE/ATTACH are untested on
CAS (CAS parts are always Full-storage).

---

## Bottom line

The **MergeTree data-plane is thoroughly audited.** The remaining gaps cluster into three themes:

1. **Newer MergeTree features with in-place-mutable files** — **UniqueKey/DeleteBitmap (G1)** is the
 standout (hot rewrite of non-mutable-set files), then full-text/vector indexes (G2). *These are true
 correctness gaps worth code-level auditing next.*
2. **Non-MergeTree / generic-disk consumers (G4–G6, G8)** — out of scope by design, but **ungated**, so
 the real action item is a *fail-closed guard* (reject non-MergeTree engines, `tmp` disks, and SSD-cache
 dictionaries on CAS disks at config/DDL time) rather than a deep audit.
3. **Known-unverified paths the code already flags (G3 cross-disk partition ops, G12 Packed RESTORE)** —
 finish the verification the authors deferred.

**Suggested next audit: G1 (UniqueKey/DeleteBitmap/SSTIndex on CAS)** — it's an active MergeTree feature,
uses a mutation pattern CAS explicitly does not optimize for, and has zero current coverage.

## cas-crash-consistency-audit.md

Language: Markdown

# CAS — Crash-Consistency & Durability Recovery Matrix

Scope: durability of each persisted object and crash-recovery behavior at **every step** of the write,
GC, mount, and RENAME flows, plus **orphan/leak reclamation completeness** (does everything that a
crash orphans eventually get reclaimed?). Method: per-step power-loss table (crash immediately after
each durable action) → recovery outcome → invariant preserved / leak / gap.

Durability model: every object is a **single S3 PUT** (atomic, durable once ACKed); there is no local
WAL. "Committed" = the conditional PUT returned `Committed`. Recovery is derived from durable S3 state
at the next `Store::open` / GC round — there is no crash-recovery log to replay.

Invariants: **INV_NO_DANGLE**, **INV_NO_LOSS**, **INV_OVER_COUNT_ONLY** (crash biases to leak, never
loss), **INV_COMMIT_ATOMIC** (per single-shard op).

---

## 1. Write flow — power-loss per step

Flow: `stageManifest(M) → precommitAdd → putBlob(B) → promote(ref R→M)`.

| Crash after… | Durable state | Next-open / GC recovery | Verdict |
|---|---|---|---|
| stageManifest(M) | orphan manifest body, no owner, no ref | orphan-manifest sweep reclaims once the build is watermark-dead | ✔ leak → reclaimed |
| precommitAdd | precommit binding in shard journal (+1 shields M's blobs) | if build never resumes, GC reclaims the precommit once the watermark proves it dead; blobs lose the +1 → condemned → reclaimed | ✔ leak → reclaimed |
| putBlob(B) | blob object durable (content-addressed); precommit +1 still shields | same as above; B reclaimed when unreferenced | ✔ leak → reclaimed |
| promote (CAS committed) | ref R→M durable, readable | fully committed; readable on reopen | ✔ committed |
| promote CAS **lost-ACK** | ref actually committed, client saw failure | retry re-reads, sees R present (its own commit); presence-asserting closure may misreport (**W-N1**); journal may double-append (**W-N2**) | ⚠ spurious error / bloat, no loss |

**No crash interleaving yields a dangle or a false commit.** The two-phase precommit→promote spine
means: crash before promote ⇒ orphan (reclaimable); crash after ⇒ committed readable ref. All
pre-promote debris is watermark/orphan-sweep reclaimable.

---

## 2. Multi-part commit — the atomicity gap

`ContentAddressedTransaction::commit()` publishes each staged part in a loop; **there is no multi-ref
atomic publish** (its own comment: B122). Two crash outcomes:

- **Exception mid-loop** → a compensating best-effort rollback drops the refs *this commit* created
 (only refs that were absent before), then rethrows. Restores all-or-nothing for the exception path.
- **Power-loss mid-loop** → **no rollback runs** (rollback is in the `catch`, not crash-durable). Some
 parts are durably published, others not → **partial commit** survives the crash.

**Verdict — DUR1 (Low–Med).** For a single-part INSERT (the common path) commit is effectively atomic
(one publish). For a transaction staging **multiple** parts (e.g. a multi-part write), a power-loss mid
`commit()` leaves a partial set: some parts committed, some absent. MergeTree tolerates missing parts
(treated as not-inserted), so this is closer to "fewer parts than intended" than corruption — but it
**diverges from the disk layer's all-or-nothing expectation** and is not self-healed. No dangle, no
corruption; a durability-atomicity gap.

---

## 3. RENAME TABLE / moveDirectory — the split-table gap

`moveDirectory` (RENAME TABLE, cross-engine move) is a **best-effort multi-op** with **no
cross-namespace atomicity** (B126): republish every ref into the destination namespace, then drop the
source. It is **re-drivable/idempotent** (`republishRef` no-ops on an already-moved source,
`putNamespaceFile` is last-writer-wins, `dropNamespace` of an empty/absent ns is a no-op).

| Crash point | Durable state | Recovery | Verdict |
|---|---|---|---|
| mid-republish | table SPLIT across old+new namespaces | **re-driving the same RENAME completes it**; but nothing auto-re-drives after a crash | ⚠ **DUR2** split table until re-issued |
| after all republish, before dropNamespace | dest complete, source refs linger | GC reclaims the tombstoned source; or re-drive | ✔ leak → reclaimed |

**Verdict — DUR2 (Med).** A power-loss mid-RENAME leaves a table whose parts are split between two
namespaces. There is **no durable move-journal** and **no automatic re-drive on restart** — recovery
relies on the operator/engine re-issuing the RENAME. Also surfaces as the fractured-read / partial-
transaction finding in the interleaving & security audits. This is the sharpest crash-consistency gap
(promote-overwrite leak **W1** rides here too when the destination pre-exists).

---

## 4. GC flow — power-loss per step

Flow: `floor → fold → pre-CAS deletes → outcome logs → retired publish → single gc/state CAS → cleanup`.

| Crash after… | Recovery | Verdict |
|---|---|---|
| pre-CAS `deleteExact` (some blobs deleted) | round not committed; next round re-derives from durable state; exact-token deletes are idempotent (NotFound-safe) | ✔ safe (only condemned-then-graduated objects deleted; INV_NO_DANGLE holds) |
| retired-list / outcome logs published | attempt-scoped prefix; a superseded attempt's artifacts are ignored/pruned | ✔ safe |
| **gc/state CAS committed** | round durable; next round continues from it | ✔ committed |
| gc/state CAS **lost-ACK** | leader treats round as ABORTED (**G-N3**); next round re-reads committed state; pre-CAS deletes were exact-token-safe | ✔ spurious ABORTED, no loss |
| mid-generation-prune | prune is best-effort, never throws on benign 404/TokenMismatch | ✔ leak → reclaimed next round |

**Two-phase graduation is the crash spine for GC:** a blob is only `deleteExact`'d a round *after* it
enters `delete_pending`, so a crash between condemn and delete simply re-derives; a crash between
`delete_pending` publish and the delete leaves the object for the next round. No crash deletes a live
object (exact-token + ack-floor + fold-barrier all bias to over-retain).

---

## 5. Mount / startup recovery — power-loss per step

| Scenario | Recovery | Verdict |
|---|---|---|
| Hard-kill leaves a stale mount lease | next open **waits out** the lease (bounded ttl+margin) then reclaims via `claimMountAwaitingExpiry` (token-guarded, S13); a genuinely live twin is reported LiveDoubleStart and open aborts | ✔ safe, fail-closed |
| Crash after `allocateWriterEpoch` bump, before mount claim | epoch **skips** a value (allocate-then-crash); all checks use `>`/equality, never `==prev+1` → gap tolerated | ✔ safe |
| Crash mid owner-anchor claim | owner anchor is first-writer-wins CAS; partial write never commits (single PUT atomic) | ✔ safe |
| `gc/state` lost/corrupt | GC wedges; recover via `SYSTEM CONTENT ADDRESSED GC REBUILD`; the baseline guard fails **closed** on trimmed history (never mass-condemns) | ✔ fail-closed → explicit recovery (**G-N2**) |

---

## 6. Orphan / leak reclamation completeness

Every crash-orphaned artifact class and its reclaimer:

| Orphan class | Produced by | Reclaimer | Complete? |
|---|---|---|---|
| never-precommitted manifest body | crash after stageManifest | `CasOrphanManifestSweep` (epoch-aware, watermark-gated, cursor-paced) | ✔ |
| precommitted-but-abandoned blob/manifest | crash before promote / abandon | GC fold (precommit reclaim once watermark-dead) → condemn → delete | ✔ |
| promote-overwritten prior manifest | RENAME/lost-ACK (**W1**) | **NOT reclaimed** — the old manifest keeps in-degree (unconditional `refs[R]=…`) | ✖ **permanent leak (W1)** |
| lingering source-namespace shards after RENAME | moveDirectory drop | GC empty-shard tombstone reclaim | ✔ |
| incomplete multipart upload | interrupted blob PUT | S3 lifecycle policy (external) | ✔ (needs lifecycle configured) |
| superseded GC generation artifacts | attempt races / supersession | `pruneSupersededGenerations` (retention = `gc_snap_generations_to_keep`) | ✔ |

**Completeness verdict:** every crash-orphan class is reclaimed **except W1** (promote-overwrite leaks
the displaced manifest + its blobs permanently — over-count, INV_OVER_COUNT_ONLY-safe). Multipart
cleanup depends on an S3 lifecycle rule being configured (a deployment prerequisite, not code).

---

## 7. Summary

| # | Finding | Severity | Class |
|---|---|---|---|
| DUR2 | RENAME/moveDirectory power-loss → split table, no durable move-journal / auto-re-drive | **Med** | Atomicity/recovery |
| DUR1 | Multi-part `commit()` power-loss → partial commit (no crash-durable rollback) | Low–Med | Atomicity |
| W1 | promote-overwrite orphans the prior manifest (only non-reclaimed orphan class) | Med | Permanent leak |
| (dep) | Multipart-upload cleanup requires an S3 lifecycle rule | Low | Deployment |

**Headline.** Crash-consistency of the **single-object** flows is excellent: single-PUT atomicity + the
two-phase precommit→promote (write) and condemn→pending→delete (GC) spines mean **no power-loss
interleaving produces a dangle, a false commit, or committed-data loss** — every crash biases to a
**reclaimable leak**, and every orphan class has a reclaimer **except W1**. The real gaps are the
**multi-object** flows that object storage cannot make atomic: **DUR2** (RENAME leaves a split table
with no durable move-journal or auto-re-drive) and **DUR1** (multi-part commit can be left partial by
power-loss). Both are recoverable by re-issuing the operation and neither corrupts data, but they
diverge from MergeTree's all-or-nothing expectation and warrant either a durable move-journal or
explicit operator-facing detection of split/partial state.

## cas-datatype-agnosticism-audit.md

Language: Markdown

# CAS — Data-Type Agnosticism & MergeTree Compatibility Audit

Question: build an exhaustive list of MergeTree data types and confirm whether CAS is **data-type
agnostic** — i.e. supports every possible MergeTree column type — and whether it is "100% MergeTree
compatible."

Grounded in `src/DataTypes/*`, `ISerialization::getFileNameForStream`, `escapeForFileName.cpp`,
`SerializationObject.cpp`, and the CAS `CasLayout.h` (`blobKey`) / `CasManifestCodec.h` (`ManifestEntry`).

---

## 1. Exhaustive MergeTree data-type list

| Family | Types |
|---|---|
| **Integers** | Int8/16/32/64/128/256, UInt8/16/32/64/128/256 |
| **Floating** | Float32, Float64, BFloat16 |
| **Decimal** | Decimal32/64/128/256 = `Decimal(P,S)` |
| **Boolean** | Bool (UInt8 domain) |
| **Date/Time** | Date, Date32, DateTime, DateTime64, Time, Time64 |
| **String** | String, FixedString(N) |
| **Enum** | Enum8, Enum16 |
| **Network/UUID** | UUID, IPv4, IPv6 |
| **Composite** | Array(T), Tuple(...), Map(K,V), Nested, Nullable(T), LowCardinality(T) |
| **Semi-structured / dynamic** | Variant(T…), Dynamic, JSON / Object('json') |
| **Aggregate** | AggregateFunction(f, T…), SimpleAggregateFunction(f, T…) |
| **Vector / specialized** | QBit (quantized vector) |
| **Geo (custom over composites)** | Point, Ring, LineString, MultiLineString, Polygon, MultiPolygon |
| **Interval** | Interval* (rarely persisted) |
| **Internal (not stored as MergeTree columns)** | Nothing, Set, Function |

---

## 2. Why CAS is data-type agnostic — three independent layers

CAS operates **strictly at the file/blob level**. It never parses, decodes, or reasons about column
values or types. Three independent facts guarantee agnosticism:

### Layer 1 — CAS stores files, not typed columns
A part is N files → one manifest → one ref. Each file is a `ManifestEntry`:
```22:32:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Core/CasManifestCodec.h
struct ManifestEntry
{
    String path;                     // the file name — an opaque string
    EntryPlacement placement = ...;  // Inline | Blob
    UInt128 blob_hash{};
    uint64_t blob_size = 0;
    String inline_bytes;
};
```
There is **no type field anywhere** in the manifest. Whatever bytes MergeTree's serialization writes to
`col.bin` / `col.null.bin` / `col.dict.bin` / `col..bin` are stored opaquely. The read path
(`getBlobViewPlan` → ranged GET) serves bytes back to MergeTree's reader without interpreting them.

### Layer 2 — file names never become S3 key segments
A blob's S3 key is derived **purely from its content hash**, not its file name:
```45:48:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Core/CasLayout.h
String blobKey(const BlobId & id) const
{
    return shardedKey("blobs", id.string());   // key = content hash, NOT the file name
}
```
The file name lives only as the `path` **string field inside the manifest protobuf**. Consequences:
- Arbitrarily long / weird column or dynamic-path names **cannot** exceed S3 key-length limits (they
 don't appear in keys; only the fixed-length content hash does).
- The number/shape of substreams a type produces only affects **manifest size**, never key validity.
- The only data-derived names that reach an S3 key are **table-level verbatim files**
 (`namespaceFileKey`), which explicitly reject `..`, empty, and leading/trailing `/` — and those are
 not column files.

### Layer 3 — all file names are normalized to a safe charset anyway
Every column and substream file name passes through `escapeForFileName`, which emits **only**
`[A-Za-z0-9_]` plus `%XX` hex escapes:
```8:31:src/Common/escapeForFileName.cpp
std::string escapeForFileName(const std::string & s)
{
    ...
        if (isWordCharASCII(c)) res += c;
        else { res += '%'; res += hexDigitUppercase(c/16); res += hexDigitUppercase(c%16); }
    ...
}
```
This applies to the **data-derived** names too: `ISerialization::getFileNameForStream` escapes the
column name, and `getNameForSubstreamPath` escapes **Variant element names** (`escapeForFileName(variant_element_name)`)
and **Object/JSON dynamic path names** (`escapeForFileName(object_path_name)`). So even a JSON key like
`"a/b..c@d e"` becomes a file name in `[A-Za-z0-9_%]` (with `.` only as literal substream separators).
Therefore a data value can **never** inject `/`, `..`, `@` (so it can't collide with CAS's `@cas@`
archive marker), spaces, or reserved dir names — the CAS path parser and key builder are safe for all
types by construction.

---

## 3. Substream → file mapping (what CAS actually stores per type)

| Type | Files (per column, escaped) | CAS handling |
|---|---|---|
| Scalar (Int/Float/Date/UUID/IP/Enum/Decimal/FixedString) | `col.bin` (+marks) | 1 blob/inline entry |
| String | `col.bin` (+marks) | blob/inline |
| Nullable(T) | `+ col.null.bin` | +1 entry |
| Array(T) | `+ col.size0.bin` | +1 entry |
| Map(K,V) | `col.size0.bin`, `col.keys…`, `col.values…` | multiple entries |
| Tuple(…) | `col..bin` per element (escaped) | N entries |
| LowCardinality(T) | `col.dict.bin`, `col.bin` | entries |
| Nested | separate `col.sub` columns | entries |
| **Variant(T…)** | `col.variant_discriminators.bin`, `col..bin` | entries (data-independent shape) |
| **Dynamic** | `col.dynamic_structure.bin` + variant substreams | entries |
| **JSON / Object** | `col.object_structure`, `col..bin` per typed/dynamic path, shared-data substreams | **many** entries, all escaped; path names in manifest strings |
| AggregateFunction / SimpleAggregateFunction | `col.bin` (serialized state) | blob/inline |
| Geo (Point/Polygon/…) | composite of Array/Tuple/Float substreams | entries |
| Skip indexes (incl. text index substreams) | `skp_idx_*.idx` (+ dictionary/postings) | entries |

The only type-related variability CAS sees is **how many entries** a part manifest has — Wide parts and
dynamic types (JSON with many paths) produce more entries; Compact parts fewer. That is a manifest-size
scaling factor, not a correctness dependency.

---

## 4. Edge cases considered (and why none breaks CAS)

| Edge | Concern | Resolution |
|---|---|---|
| JSON/Object with thousands of dynamic paths | thousands of column files | thousands of manifest entries — larger manifest, still one blob per file by content hash; no S3-key impact |
| Very long JSON path / column name | S3 key length (1024B) | file name is a manifest **string**, not a key segment → no limit hit |
| Data value contains `/`, `..`, `@`, spaces | path traversal / `@cas@` collision / S3-unsafe | `escapeForFileName` → `%XX`; literal `.` only as separators → impossible to inject |
| Variant/Dynamic subtype names | data-derived file names | escaped (`escape_variant_substreams`) → safe charset |
| Enum / Decimal / type parameters | type params in files | serialized as opaque bytes; type params live in table metadata + `columns.txt` (a stored file) |
| AggregateFunction state format | version-specific binary | opaque bytes to CAS; MergeTree owns the format |
| Two byte-identical column files across parts/types | dedup correctness | content addressing dedups them (correct — identical bytes are identical regardless of source type) |
| Mutable per-part files (`uuid/txn_version/metadata_version.txt`) | must not dedup-collapse | kept out of the content manifest (stored per-ref) — independent of column types |

---

## 5. Verdict

**Is CAS data-type agnostic? — YES, definitively.** CAS never interprets column data or types. It stores
whatever files the MergeTree serialization layer emits, keyed by content hash, with the file name held
as an opaque manifest string. The one place a data type *could* leak into CAS — file naming, including
data-derived dynamic paths (JSON/Object, Variant, Dynamic) — is neutralized twice over: (a) those names
are `escapeForFileName`-normalized to a safe charset that can't collide with any CAS reserved marker or
inject path traversal, and (b) they never become S3 key segments at all (blobs are content-hash keyed;
names live in the manifest protobuf). Complex/dynamic types simply yield more manifest entries.

**Does it support all MergeTree data types? — YES.** Every type in §1 — from Int8 to Decimal256, from
`Array`/`Map`/`Tuple`/`Nested` to `LowCardinality`, `Nullable`, `AggregateFunction`, and the newest
semi-structured `Variant` / `Dynamic` / `JSON(Object)` and vector `QBit` / Geo types — reduces to
"store these bytes under these (escaped) file names," which CAS handles uniformly. **No data type is
unsupported, and none requires type-specific CAS logic.**

**Is CAS "100% MergeTree compatible"? — Compatible on the data-type axis: YES. Overall: NO — for reasons
unrelated to data types.** The type dimension is complete and agnostic. But full MergeTree compatibility
is limited by the **feature/operational** gaps found in the other audits, none of which are type-
specific:
- BACKUP is Atomic-database-only (Ordinary DBs rejected); Packed-storage parts arriving via RESTORE/
 ATTACH are outside the tested envelope; cross-disk `MOVE PARTITION TO DISK/VOLUME` is unverified;
 non-allow-listed partition ops fail closed.
- Cross-cutting correctness findings apply to all parts regardless of type: J1 (writer-epoch fencing
 TOCTOU), R1/X1 (reader has no blob pin vs GC delete), DUR1/DUR2 (multi-part commit / RENAME not
 crash-atomic), W1 (promote-overwrite leak on RENAME/lost-ACK).

**Bottom line:** CAS is **fully data-type agnostic and supports 100% of MergeTree column types with no
type-specific handling**. It is *not* 100% MergeTree-feature-compatible, but every remaining gap is a
**feature/durability/operational** limitation — never a data-type one. If the question is strictly
"can any MergeTree column type be stored and read on CAS," the answer is an unqualified **yes**.

## cas-encryption-audit.md

Language: Markdown

# CAS — Disk Encryption Support & Behavior Audit

Question: MergeTree supports disk encryption — what does CAS support, and how does it behave?

Grounded in `DiskEncrypted.{h,cpp}`, `IO/FileEncryptionCommon.cpp` (`InitVector::random`, `Header`),
`IO/S3/Client.h` (`ServerSideEncryptionKMSConfig`), and the CAS backend
(`CasObjectStorageBackend.cpp` — no encryption code) / `CasLayout.h` / `CasManifestCodec.h`.

---

## 1. Two distinct encryption mechanisms in ClickHouse

| Mechanism | Layer | How it works |
|---|---|---|
| **A. `DiskEncrypted`** (client-side) | an IDisk **wrapper** (`type: encrypted, disk: `) | intercepts `writeFile`/`readFile`, prepends a per-file `Header` (`"ENC"` + version + algorithm + key fingerprint + **random IV**) and AES-CTR-encrypts the body; delegates all path/metadata ops to the wrapped disk |
| **B. S3 server-side encryption (SSE)** | the S3 client / bucket | `server_side_encryption_customer_key_base64` (SSE-C) or `ServerSideEncryptionKMSConfig` (SSE-KMS), or bucket-default SSE-S3; S3 encrypts **at rest**, transparent to the client |

**CAS itself has no encryption code** — `CasObjectStorageBackend.cpp` contains no AES/IV/encrypt logic.
CAS is **encryption-agnostic**: it stores whatever bytes it is handed and keys blobs by the content
hash of those bytes.

---

## 2. Behavior under S3 SSE (mechanism B) — the natural fit ✅

The CAS object-storage backend issues its PUT/GET/HEAD through the standard S3 client, which applies the
configured SSE headers per request. Therefore:
- **Transparent to CAS.** CAS sends and receives **plaintext** through the S3 API; S3 encrypts on the
 way in and decrypts on the way out. CAS never sees ciphertext.
- **Dedup fully preserved.** CAS content-addresses the plaintext, so identical part files still collapse
 to one blob — the core CAS value proposition is intact.
- **Encryption at rest.** All CAS objects — blobs, part manifests, ref shards, `gc/state`, retired
 sets, mount lease, owner/epoch — are encrypted at rest by S3, because they all go through the same
 encrypted bucket/client.
- **Zero-copy / fetch-by-relink unaffected** (operates on the plaintext-keyed content ids).

**Verdict: fully supported and recommended.** SSE is orthogonal to CAS and preserves every CAS property.
The only nuance: SSE-C/SSE-KMS apply one encryption context to the **whole pool**, which matches CAS's
single-trust-domain pool model (see the security audit); per-table key isolation is not available this
way.

---

## 3. Behavior under `DiskEncrypted` (mechanism A) — works mechanically but defeats CAS ⚠️

Composition would be `DiskEncrypted → wraps → DiskObjectStorage(metadata_type=content_addressed)`.
MergeTree writes a part file → `DiskEncrypted.writeFile` encrypts → `delegate.writeFile` hands the
**ciphertext** to the CAS transaction → CAS stores it as a content-addressed blob.

### E-1 — Content-addressed dedup is **defeated** (High impact on CAS value)
`DiskEncrypted` generates a **fresh random IV per file** (`InitVector::random()` → `RAND_bytes`), and
CAS content-addresses the resulting **ciphertext**. Consequences:
- Two files with **identical plaintext** encrypt to **different ciphertext** (different IV) → **different
 content hash** → **no dedup**. Every encrypted file becomes a unique blob.
- CAS's entire reason for existing — cross-part / cross-replica byte sharing — is **nullified** under
 `DiskEncrypted`. You pay CAS's protocol overhead (shards, GC, manifests) and get **zero dedup**.
- Re-materializing byte-identical output (a deterministic merge/mutation) yields new ciphertext (new
 IV) → a new blob, so even same-node re-writes don't dedup.

### E-2 — CAS metadata remains **plaintext** on S3 (Info/Med — metadata leakage)
`DiskEncrypted` only encrypts bytes that pass through its `writeFile` (the part **files**). CAS's own
control plane — part **manifests (including file names / paths), ref shards, sizes, the dedup/reference
graph, `gc/state`, mount lease** — is written by the CAS `Store` **directly** to the object-storage
backend, **not** through `DiskEncrypted.writeFile`. So under `DiskEncrypted`-only (no S3 SSE), the
column bytes are encrypted but the **structural metadata is stored in cleartext** on S3: an observer
with bucket read access sees file names (escaped column/JSON path names), part composition, sizes, and
the reference topology. (SSE would cover this; `DiskEncrypted` alone does not.)

### E-3 — Read-path composition is **untested** (Med — needs verification)
CAS's optimized read path (`getBlobViewPlan` → ranged `readBlobPayload`, and inline-in-manifest bytes)
runs **inside** `DiskObjectStorage::readFile` (the delegate). `DiskEncrypted.readFile` wraps
`delegate.readFile` with a decrypting buffer, so in principle the ciphertext buffer (blob view or
inline) is returned and decrypted on top — **but**:
- The encryption **header** (`kSize` bytes at file offset 0) shifts all offsets; `getEncryptedFileSize`
 vs CAS `getFileSize` and the `ReadBufferFromFileView` sub-range math must line up. Any MergeTree path
 that reads **storage objects directly** (bypassing `disk->readFile`) would read ciphertext without
 decrypting.
- **There is no CAS+encryption test** (no encrypted config in `utils/ca-soak/`, no gtest) and **no
 guard** rejecting the composition. So `DiskEncrypted`-over-CAS is an **unvalidated** stack.

### E-4 — Replication interaction (Low)
Fetch-by-relink copies the **sender's ciphertext blobs by reference**, so replication still works and is
consistent; but because each replica that writes a part **locally** uses its own random IVs, locally
produced parts don't share blobs across replicas (only relinked ones do) — another way E-1's lost dedup
manifests.

---

## 4. Findings

| # | Finding | Severity | Applies to |
|---|---|---|---|
| E-1 | `DiskEncrypted` random-IV ciphertext defeats content-addressed dedup (CAS gives no dedup benefit) | **High** (nullifies CAS) | DiskEncrypted-over-CAS |
| E-3 | `DiskEncrypted`-over-CAS read-path composition is untested; no guard | Med | DiskEncrypted-over-CAS |
| E-2 | CAS control-plane metadata (file names, sizes, ref graph) stays plaintext under DiskEncrypted-only | Info–Med | DiskEncrypted-over-CAS |
| E-4 | Locally-written parts don't cross-replica-dedup under encryption | Low | DiskEncrypted-over-CAS |
| — | S3 SSE preserves all CAS properties (dedup, at-rest encryption of all objects) | none | SSE (recommended) |

---

## 5. Verdict & recommendation

**What CAS supports:** CAS is **encryption-agnostic**. It has no encryption logic of its own and imposes
none. Encryption is available two ways, with very different outcomes:

- **S3 server-side encryption (SSE-S3 / SSE-KMS / SSE-C): fully supported and recommended.** It is
 transparent to CAS, encrypts **all** CAS objects at rest (blobs *and* metadata), and **preserves
 dedup** because CAS content-addresses plaintext. This is the correct way to encrypt a CAS pool.

- **`DiskEncrypted` (client-side per-file AES): mechanically composable but counterproductive and
 unvalidated.** Its per-file random IV makes every encrypted file a unique blob, so it **defeats
 CAS's dedup entirely** (E-1); it leaves CAS's structural metadata **in cleartext** unless SSE is also
 on (E-2); and the CAS optimized read path composed under encryption is **untested with no guard**
 (E-3). If client-side/customer-managed keys are a hard requirement, prefer **SSE-C or SSE-KMS**
 (server-side but customer/KMS keyed) over `DiskEncrypted`, so dedup and metadata-at-rest protection
 are retained.

**Recommendations:**
1. Document that CAS pools should be encrypted via **S3 SSE**, not `DiskEncrypted`.
2. Either **add a guard/warning** when a CAS-backed disk is wrapped by `DiskEncrypted` (it silently
 loses all dedup), or explicitly validate + test the composition if it must be allowed.
3. If metadata confidentiality matters, ensure **SSE covers the bucket** so CAS manifests/shards/GC
 state are encrypted at rest (DiskEncrypted alone will not encrypt them).

**Bottom line:** CAS *behaves correctly* with encryption in the sense that it stores/serves whatever
bytes it's given, but the **only encryption that keeps CAS worthwhile is server-side (SSE)**;
client-side `DiskEncrypted` technically layers on top but **cancels the dedup that CAS exists to
provide** and is currently untested and unguarded.

## cas-gc-protocol-audit.md

Language: Markdown

# CAS — GC Protocol Audit (state-space + logical fault injection)

Scope: the CAS garbage collector — leader election + lease, advisory heartbeat, and the one-pass
ack-floor round: **discover → fold (three-cursor merge) → pre-CAS deletes → outcome logs →
retired-list publish → single `gc/state` CAS → post-CAS cleanup**, plus two-phase graduation,
attempt-scoped generations, snap prune, and `rebuildBaseline` (cas-gc-rebuild). Method: state model +
reachable walk (fold vs concurrent writer/reader/crash/re-incarnation), then logical fault injection.

Safety invariants:
- **INV_NO_DANGLE** — never delete an object with a live edge.
- **INV_NO_RETURN** — a deleted/condemned token never returns (re-incarnation gets a fresh token).
- **INV_OVER_COUNT_ONLY** — GC may over-count (retain a garbage object), never under-count (delete a
 live one).
- **INV_ACK_MONOTONE** — `min_ack` never rises past what every live writer has provably observed.

---

## 1. State model

Per-round state:
- `round`, `snap_generation`, `attempt` (attempt-scoped generation prefix).
- **min_ack floor** — `min(live writers' observed_gc_round)` from `computeHeartbeatFloor`
 (latched **before** the fold cut — `CaGcAckFloorZombie` order invariant).
- **three-cursor merge** — simultaneously verifies old candidates, graduates safe ones
 (`condemn_round < min_ack`), condemns new zero-in-degree blobs.
- **two-phase graduation** — condemn → `delete_pending` (one floor pass) → `deleteExact` (next pass).
- **source-edge set** — blob in-degree as a set of owner edges (idempotent, not an integer refcount).
- **fold barrier / clamp** — a missing/absent-at-HEAD precommit body freezes the cursor;
 `suppress_destructive` halts destructive work pool-wide when any shard is clamped/anomalous.
- **exact-token delete** — `deleteExact(key, If-Match token)`; re-incarnation ⇒ `TokenMismatch` ⇒ skip.

The round is **idempotent and crash-safe**: a single `gc/state` CAS commits the round; pre-CAS deletes
are exact-token (safe to repeat/abort); attempt-scoped prefixes isolate concurrent leaders.

---

## 2. Reachable-state findings

### G-N1 — Pass-wide `suppress_destructive` can halt all reclamation *(Med-High, liveness/operability)*

`suppress_destructive` is **pool-wide**: if a single shard is persistently clamped (persistent
false-404, corrupt body, unreadable, or a stuck fold barrier), graduations and pending-deletes are
suppressed for the **entire pool**, not just the offending shard. Safety-preserving (it over-retains),
but an operational cliff — unbounded space growth with no self-heal until the bad shard is resolved.
**Fix:** scope suppression to the affected shard/namespace where sound, and surface a loud operational
signal + metric when suppression persists across rounds.

### G-N2 — Lost/corrupt GC-internal artifacts wedge GC until manual rebuild *(Low, by-design blast radius)*

Loss/corruption of GC-internal objects (`gc/state`, seals, run files) wedges GC. This is the explicit
design contract — the recovery is `SYSTEM CONTENT ADDRESSED GC REBUILD` (cas-gc-rebuild), which
fail-closes on trimmed history. Blast radius is by-design; noted so operators know GC is
fail-stop-then-recover, not self-healing, on internal-state loss.

### G-N4 — Mass-drop delta accumulation is a non-streaming memory point *(Low)*

A very large drop (e.g. `dropNamespace` on a huge table, or a mass RENAME) produces a large
in-memory delta during fold/merge. `rebuildBaseline` is explicitly batched (`rebuild_edge_budget`,
O(budget) memory), but the **regular round's** mass-drop delta is a non-streaming point. **Fix:** stream
the mass-drop delta with the same budget discipline as rebuild.

---

## 3. Logical fault injection (S3 interrupts, delays, lost ACKs, disk, memory, crash mid-delete)

### G-N3 — Lost ACK on the round `gc/state` CAS → spurious ABORTED, deletes safe *(Low, verified safe)*

If the ACK for the single `gc/state` CAS is lost, the leader treats the round as `ABORTED`; the next
round re-reads the committed state and proceeds. The **pre-CAS deletes are exact-token and idempotent**,
so a repeated/aborted round never mis-deletes. Safe — the only cost is a wasted round.

### Crash mid-delete — safe

`deleteExact(If-Match token)` is idempotent on `NotFound` and refuses on `TokenMismatch`. A crash
between deletes leaves a partially-progressed pending set; the next round re-derives and continues. No
double-delete of a re-incarnated object (exact-token protects it).

### S3 interrupt / delay during fold — safe (fail-closed over-protect)

A read failure/absence during discover or fold **clamps** the affected shard (forces Read, freezes the
cursor) rather than skipping it — the discover ambiguity guards force Read on any key seen zero or
multiple times across LIST pages. The bias is always toward **not** graduating (over-retain).

---

## 4. Verified SAFE

- **`min_ack` never rises under S3 faults.** `computeHeartbeatFloor` treats an unreadable/contended
 mount conservatively (contributes to `lagging`, holds the floor down); an expired-but-unfenced mount
 still contributes its `observed_gc_round`. The floor is **latched before the fold cut**
 (`CaGcAckFloorZombie`), so a post-cut writer commit can't float a graduation over itself.
- **`deleteExact` never misclassifies transient errors.** Only true `NotFound` → idempotent skip;
 `TokenMismatch` → refuse; other errors → fail the delete (retry next round). A network blip never
 deletes a live object.
- **`acquireOrRenewLease` is fail-closed.** Transient errors and `gc/state` absence are handled without
 fabricating leadership; a superseded leader's round-commit CAS fails.
- **Two-phase graduation is safe against zombie leaders.** The `delete_pending` state gives writers a
 round to observe the condemnation (refresh RetireView → commit gate re-uploads) before the exact-token
 delete; a zombie leader's stale-token delete misses on re-incarnation.
- **Attempt-scoped generations prevent orphaned-seal corruption.** Concurrent leaders write to distinct
 `gc/gen/ /attempt/ /…` prefixes; only the committed attempt's state survives.
- **Baseline guard prevents under-count.** A shard whose journal proves trimmed history with no sealed
 baseline → `CORRUPTED_DATA`, GC refuses (never mass-condemns lost-snapshot edges). Recovery is the
 explicit rebuild.
- **Clamp / fold-barrier over-protects.** A missing precommit body clamps `folded_cursor` below the live
 precommit, so reclaim guards block; the FULLY-FOLDED-BEFORE-RECLAIM constraint
 (`folded_cursor ≥ tombstone_version`) prevents phantom-in-degree leaks turning into premature deletes.
- **Run files fail closed on partial parse.** CRC + protobuf/framing on run/seal artifacts → a
 truncated/corrupt artifact is rejected, never partially applied.

---

## 5. Summary

| # | Finding | Severity | Class |
|---|---|---|---|
| G-N1 | Pass-wide `suppress_destructive` halts all reclamation on one persistent clamp | **Med-High** | Liveness/operability |
| G-N2 | Lost/corrupt GC-internal artifacts wedge GC until manual rebuild | Low | By-design blast radius |
| G-N4 | Mass-drop delta accumulation (regular round) is non-streaming memory | Low | Memory |
| G-N3 | Lost-ACK on round CAS → spurious ABORTED (deletes safe) | Low | Verified safe |

**Headline.** The GC safety core is the strongest part of the system: **`min_ack` monotonicity, the
ack-floor latched-before-cut order, two-phase graduation, exact-token deletes, attempt-scoped
generations, and the baseline guard** compose so that **no interleaving under-counts** — every crash,
lost-ACK, or S3 fault biases to **over-retain** (INV_OVER_COUNT_ONLY). There are **no reachable data-loss
findings** on the GC side. The real issues are **liveness/operability**: the pool-wide
`suppress_destructive` clamp (G-N1) can halt reclamation with no self-heal, and the regular-round
mass-drop delta (G-N4) is a memory point. Both are safe-but-brittle, not correctness bugs.

## cas-gc-rebuild-feature-audit.md

Language: Markdown

# cas-gc-rebuild — Dedicated Feature Audit

The origin of this whole engagement, finally audited on its own terms. Code-grounded in the baseline
**guard** (`CasGc.cpp` 706–725), **`rebuildBaseline`** (1404–1783), the operator command
(`programs/disks/CommandCaGcRebuild.cpp`), and the **11 gtests** in `src/Disks/tests/gtest_cas_gc_rebuild.cpp`.
Unlike the earlier GC-protocol/TLA audits, this reads the recovery algorithm and its command surface
directly.

---

## 1. What the feature is (as coded)

Two halves:
1. **Guard** (regular rounds): a shard with **no sealed cursor** whose journal **proves trimmed history**
 (`journal.front().transition_version > 1`, or empty journal with `shard_version > 0`) means the
 baseline that licensed the trim is gone. GC **throws `CORRUPTED_DATA` and refuses to run** — fail
 closed, *before* any destructive step. Recovery is the explicit rebuild.
2. **`rebuildBaseline(force)`**: health-check → lease → generation-above-debris → per-gc-shard
 attempt-iterated fold of `+1` edges from (committed refs) ∪ (live precommits with bodies) ∪
 (unowned-alive manifests) → "pipeline-blindness" zero-condemn of physically-present edge-less blobs →
 deterministic seal + single `gc/state` CAS. Writes **only** the GC plane; never touches refs, manifests,
 or blobs; never deletes.

Operator surface: `clickhouse-disks ca-gc-rebuild [--force]`, gated on `isReadOnly()` so it can only run
against a disk configured ` true `.

**Overall: this is the most carefully engineered piece of the whole CAS system.** Fail-closed everywhere,
force is narrowly scoped, and coverage is real. The findings below are edges, not a teardown.

---

## 2. Findings

**GCR-1 (High — single-writer safety is operator-discipline-only; the tool cannot detect a live remote
server).** The command's sole runtime guard against racing a live server is the **in-process**
`isReadOnly()` flag. That proves only that *this* invocation won't issue normal writes — it **cannot
detect another server that has the pool mounted read-write on a different host**. `rebuildBaseline`
acquires the **GC lease** (blocks concurrent GC, GCR test `LeaseConflictRefuses` ✅) but **never checks or
claims the mount lease**, so a concurrent **writer** is invisible to it: the writer doesn't touch
`gc/state`, so the final token-guarded CAS still commits. Consequence: if an operator runs rebuild against
a pool that is *actually live* (the exact panic scenario — "GC won't run, let me fix it"), the fold scans a
**moving universe** and can bless a baseline that **misses a concurrently-published ref's edges**; a
subsequent regular round then condemns and deletes **live** blobs → dangle/data loss. The design doc and
command comment name this as an operator obligation, but for a tool that *can write and licenses
deletion*, relying on human discipline is **fail-open**. **Fix:** refuse if any mount lease is fresh/live
(the data is already read in `computeHeartbeatFloor`); make it fail-closed instead of documented.

**GCR-2 (Med — the zero-condemn scan is O(total blobs) with a synchronous HEAD per candidate, unbudgeted).**
The "pipeline blindness repair" (1683–1716) LISTs the **entire** `blobs/` prefix and issues a `backend.head`
for **every** blob not in `edge_bearing`. The edge fold has a `rebuild_edge_budget`; this blob scan has
**no budget, no pagination cap on HEAD count**. On a large pool that is millions of LIST+HEAD round-trips —
hours of wall-clock and real S3 request cost — incurred **exactly when the pool is already in trouble** (DR
time). This is the scalability ceiling of the recovery path and it's the opposite of what you want during
an incident. **Fix:** budget/rate-limit the zero-condemn HEADs, or make it an optional second phase.

**GCR-3 (Low — an interrupted rebuild leaks GC-plane artifacts that are never reclaimed and monotonically
bump the generation).** Generation = `max_gen + 1` where `max_gen` scans surviving `gc/gen/*` prefixes. A
rebuild that crashes **after** `putDeterministicArtifact`(seal)/`putIfAbsent`(retired)/run writes but
**before** the `gc/state` CAS leaves those seal/run/retired objects as **ownerless debris**. A re-run
picks a *higher* generation (correct — avoids collision), but the orphan sweep targets manifests/blobs,
**not `gc/gen` artifacts**, so this debris accumulates permanently and each interrupted attempt ratchets
the generation counter. Bounded and benign, but it's an un-swept leak on the recovery path (which may be
retried several times during an incident).

**GCR-4 (Low — the healthy-path health check re-scans the universe and duplicates LISTs).** For a `gen-0`
state the health check (1427–1444) runs a **full `discoverUniverse()` + per-shard read** just to decide
`healthy`, and the rebuild proper calls `discoverUniverse()` **again** (1545). So a rebuild does 2–3 full
ref-shard LISTs plus redundant shard reads. Minor at small scale; compounds GCR-2 at large scale. Cosmetic
correctness, real cost.

**GCR-5 (Low — LIST consistency assumption is untested against real/weakly-consistent stores).** Every
discovery step (`discoverUniverse`, the manifest-prefix scan 1630, the blob scan 1689) assumes **read-
your-writes / strongly-consistent LIST**. On AWS S3 today that holds; on GCS/other stores or under LIST
lag, a missed shard/manifest under-protects (dangle) and a missed blob under-condemns (leak). All 11
gtests use `InMemoryBackend` (strongly consistent by construction), so **the consistency assumption the
recovery correctness rests on is never exercised against a store that could violate it** (ties OSC-1/2).

**GCR-6 (Info — `force` is correctly narrow: it bypasses ONLY the "healthy state" refusal ✅).** Verified in
code and by tests: `force` gates only line 1465. It does **not** bypass the lease-conflict refusal
(`LeaseConflictRefuses`), and it does **not** bypass the **missing-committed-manifest** refusal (1575,
unconditional) — so `--force` can never bless data loss (`MissingCommittedManifestRefuses` confirms a
refused rebuild adopts no baseline and leaves `snap_generation == 0`). This is exactly the right blast-
radius for a `--force` flag and a genuine design strength.

**GCR-7 (Info — the guard fires before any destructive step, proven by test ✅).**
`FreshStateOverTrimmedJournalsFailsClosed` asserts the blob still exists after the guard throws. The
ordering (health check before lease-acquire's bootstrap-body creation, 1415 comment) is correct and
prevents a lease acquire from masking scenario (а).

---

## 3. Test-coverage gaps (what the 11 gtests do NOT cover)

The suite is genuinely strong — guard fail-closed, scenarios (а)/(б), narrow force, missing-manifest
refusal, live-precommit edges, batched O(budget) fold, trimmed-but-live over-protection, lease conflict,
clamp-suppression regression. Uncovered:

- **GCR-1 scenario**: no test runs a concurrent **writer** (ref publish/drop) *during* `rebuildBaseline`
 to demonstrate the moving-universe hazard. This is the highest-value missing test.
- **GCR-2 scale**: no test exercises the zero-condemn full-blob scan at a size that would surface its
 cost/behaviour (all tests have ≤6 blobs).
- **GCR-3 interrupt**: no test crashes a rebuild mid-way (post-seal, pre-state-CAS) to assert re-run
 correctness and to document the artifact debris.
- **Command layer**: no test covers `CommandCaGcRebuild` itself — the `isReadOnly()` gate, the
 not-object-storage / not-content-addressed rejections, or the non-zero exit on refusal.
- **Multi-namespace / `gc_shards > 1` rebuild**: tests use a single namespace; the per-gc-shard routing
 and multi-shard seal assembly (`blobShard`, `flush_shard`) aren't tested with several namespaces.
- **Real-store LIST consistency** (GCR-5): InMemoryBackend only.

---

## 4. Verdict

The `cas-gc-rebuild` feature is **soundly designed and unusually well-tested** — fail-closed guard, a
narrowly-scoped `--force` that cannot bless data loss, and 11 targeted tests including a real
soak-discovered regression (clamp suppression). The one **substantive** gap is **GCR-1**: the tool is
*write-capable and deletion-licensing* yet its only live-server interlock is an in-process read-only flag
that cannot see a remote writer — a fail-open reliance on operator discipline that a mount-lease liveness
check would close. **GCR-2** (unbudgeted O(all-blobs) zero-condemn scan) is the recovery-time scalability
ceiling. Everything else is minor (interrupt debris, redundant LISTs, real-store consistency, command-layer
test coverage). Recommend: add the mount-lease refusal (GCR-1), budget the blob scan (GCR-2), and add the
concurrent-writer and command-layer tests.

---

## 5. Proof code for GCR-1

Two gtests, compile-ready against `src/Disks/tests/cas_test_helpers.h`, to be appended to
`src/Disks/tests/gtest_cas_gc_rebuild.cpp`. **Not yet compiled/run** — written against the exact helper
signatures (`openStoreForTest`, `writeBlobBody`, `writeManifestRaw`, `publishCommittedTransition`,
`currentRetiredSet`, `runRoundsUntilAbsent`, `renewWatermarkOnce`, `ref`, `kGc`).

### 5.1 Proof 1 — the missing interlock (fully deterministic)

Direct proof of the root claim ("`rebuildBaseline` never checks the mount lease"): a live server's mount
lease is present and fresh, yet the rebuild performs. Contrast the existing `LeaseConflictRefuses` test —
it *does* refuse on a GC-lease conflict, so the asymmetry (blind to a live *writer*) is the bug.

```cpp
/// GCR-1 (proof): rebuildBaseline has NO mount-lease interlock. A live server's mount lease is
/// present and fresh (renewWatermarkOnce just heartbeat it), yet the rebuild PERFORMS instead of
/// refusing. The tool's only live-server guard is the caller's isReadOnly() flag, which cannot see a
/// server mounted read-write on another host. Contrast LeaseConflictRefuses: it refuses on a GC-lease
/// conflict but is blind to a live *writer* — which is exactly the moving-universe hazard.
TEST(CasGcRebuild, GCR1_NoMountLeaseInterlock_RunsUnderLiveMount)
{
    auto backend = std::make_shared<InMemoryBackend>();
    auto store = openStoreForTest(backend);
    const RootNamespace ns{"00/aa@cas@"};
    const ManifestRef r = ref(1, 0xA1);
    writeBlobBody(*backend, store->layout(), DB::UInt128(1));
    writeManifestRaw(*backend, store->layout(), ns, r, {blobEntryFor("a", DB::UInt128(1))});
    publishCommittedTransition(*backend, store->layout(), ns, "tbl", std::nullopt, r);

    Gc gc(store, kGc);
    gc.runRegularRound();

    /// A LIVE server: fresh mount-lease heartbeat (this is what a mounted read-write server does
    /// every beat). The mount lease exists and is current at the instant we rebuild.
    store->renewWatermarkOnce();
    const auto mount_before = backend->head(store->layout().mountKey("test"));
    ASSERT_TRUE(mount_before.exists) << "a live server's mount lease must be present";

    /// Disaster path so a *plain* (non-force) rebuild is legitimately allowed by the health check:
    /// gc/state is lost. The point of this test is NOT whether rebuild is allowed — it's that a LIVE
    /// MOUNT does not stop it.
    const auto st = backend->head(store->layout().gcStateKey());
    ASSERT_TRUE(st.exists);
    ASSERT_EQ(backend->deleteExact(store->layout().gcStateKey(), st.token).kind, DeleteOutcome::Kind::Deleted);

    Gc gc2(store, hexToU128("000000000000000000000000000000f1"));
    const RebuildReport rep = gc2.rebuildBaseline(/*force*/ false);

    /// THE BUG: the rebuild ran while a live mount lease was present. It never consulted the mount
    /// lease for liveness — it only guards against a competing GC lease.
    EXPECT_TRUE(rep.performed)
        << "rebuildBaseline performed with a live mount present (refusal='" << rep.refusal << "')";
    EXPECT_TRUE(backend->head(store->layout().mountKey("test")).exists)
        << "the live mount lease was there the whole time";

    /// With GCR-1 FIXED this expectation flips: a fresh mount lease should make the rebuild
    /// fail closed, e.g.
    ///     EXPECT_FALSE(rep.performed);
    ///     EXPECT_NE(rep.refusal.find("mount"), String::npos);
}
```

### 5.2 Proof 2 — the consequence: rebuild condemns a blob a concurrent writer makes live

`rebuildBaseline` scans in two non-atomic S3 passes: the **universe scan** (ref shards) then the
**zero-condemn blob scan** (all blob bodies). A writer that uploaded a blob body (precommit-first: body
lands *before* the ref publish) but whose ref-publish isn't visible during the universe scan produces the
state below — the rebuild sees the body present with no edge and condemns it. The `currentRetiredSet`
assertion is the deterministic proof; the final deletion step is the empirical question.

```cpp
/// GCR-1 (consequence): the rebuild's universe scan and its zero-condemn blob scan are two separate,
/// non-atomic passes. A concurrent writer that uploaded a blob body (precommit-first: the body lands
/// BEFORE the ref publish) but whose ref-publish journal event is not yet visible to the universe scan
/// makes the rebuild see the body as edge-less and CONDEMN it. Modeled here: an anchor ref makes the
/// namespace discoverable; blob 2's body is present but its committing ref is not visible during scan.
TEST(CasGcRebuild, GCR1_CondemnsConcurrentlyReferencedBlob)
{
    auto backend = std::make_shared<InMemoryBackend>();
    auto store = openStoreForTest(backend);
    const RootNamespace ns{"00/aa@cas@"};

    /// Anchor: makes the namespace discoverable and is legitimately referenced (blob 1).
    const ManifestRef anchor = ref(1, 0xA1);
    writeBlobBody(*backend, store->layout(), DB::UInt128(1));
    writeManifestRaw(*backend, store->layout(), ns, anchor, {blobEntryFor("a", DB::UInt128(1))});
    publishCommittedTransition(*backend, store->layout(), ns, "anchor", std::nullopt, anchor);

    /// The in-flight writer has uploaded blob 2's BODY. Its ref-publish journal event is not visible
    /// to the rebuild's universe scan (it lands in the window between the universe scan and the CAS).
    writeBlobBody(*backend, store->layout(), DB::UInt128(2));

    /// gc/state absent (fresh) => plain rebuild allowed. The rebuild zero-condemns blob 2.
    Gc gc(store, hexToU128("000000000000000000000000000000f2"));
    const RebuildReport rep = gc.rebuildBaseline(/*force*/ false);
    ASSERT_TRUE(rep.performed) << rep.refusal;

    /// DETERMINISTIC PROOF: the rebuild put blob 2 into the retired (condemned) set, at its minted
    /// round, even though a writer was about to make it live.
    const RetiredSet retired = currentRetiredSet(*backend, store->layout(), /*shard*/ 0);
    const bool blob2_condemned = std::any_of(retired.entries.begin(), retired.entries.end(),
        [](const RetiredEntry & e) { return e.hash == DB::UInt128(2); });
    EXPECT_TRUE(blob2_condemned)
        << "the rebuild condemned blob 2 — a blob the concurrent writer is committing";
    /// Sanity: the anchor's blob (edge-bearing) was NOT condemned.
    EXPECT_FALSE(std::any_of(retired.entries.begin(), retired.entries.end(),
        [](const RetiredEntry & e) { return e.hash == DB::UInt128(1); }));

    /// The writer now COMPLETES the publish: blob 2 is LIVE (a committed ref points at it).
    const ManifestRef b = ref(2, 0xB2);
    writeManifestRaw(*backend, store->layout(), ns, b, {blobEntryFor("b", DB::UInt128(2))});
    publishCommittedTransition(*backend, store->layout(), ns, "tbl_b", std::nullopt, b);

    /// EMPIRICAL OUTCOME (run to observe): blob 2 was condemned by the rebuild at round R. Whether the
    /// subsequent regular rounds DELETE it (data loss + dangling ref) or the fold's re-verify spares it
    /// once the +1 delta lands is the thing this test settles when built and run. If it deletes:
    ///   -> data loss: a committed ref names a blob GC deleted.
    store->renewWatermarkOnce();
    const bool deleted = runRoundsUntilAbsent(store, gc, *backend, store->layout(), DB::UInt128(2));
    if (deleted)
        ADD_FAILURE() << "GCR-1 realized: GC deleted blob 2 while committed ref 'tbl_b' names it (dangle)";
    else
        RecordProperty("gcr1_selfhealed", "regular-round +1 delta spared the condemned blob");
}
```

### 5.3 What the proofs establish, and their limits

- **Proof 1 is the deterministic proof of GCR-1 as stated** ("does not acquire/verify the mount lease"):
 a fresh mount lease is present and the rebuild performs. The fix is the two commented lines (refuse on a
 live mount).
- **Proof 2 deterministically proves the rebuild condemns a blob whose ref is being published
 concurrently** (the `currentRetiredSet` assertion). The final deletion step is marked as the **empirical
 question** — whether a later regular round's re-verify spares the re-referenced blob or deletes it could
 not be settled by static reading; it needs execution.

**Caveats (not overclaiming):**
1. Both use `InMemoryBackend` (strongly consistent). The real race needs the two scans to observe
 different states — trivially true on real S3 across a live write, and modeled here by ordering, not a
 literal thread interleaving. A stronger version needs a test seam inside `rebuildBaseline` (a callback
 between the universe scan and the blob scan) to publish the ref mid-call; no such hook exists today.
2. **Not compiled.** Written against the exact helper signatures, but confirm by building the CAS gtest
 target.

## cas-idisk-contract-audit.md

Language: Markdown

# CAS — IDisk / IMetadataStorage Contract Conformance vs MergeTree Expectations

Scope: does the content-addressed `IMetadataStorage` / `IMetadataTransaction` implementation honor the
semantics MergeTree assumes of a disk? A POSIX/local disk gives MergeTree: atomic single-file/dir
rename, hardlinks (shared inode), per-file unlink, real mtime, chmod, and a removal model where the
disk layer frees bytes. CAS emulates all of this over object storage. This audit inventories each
surface method, the **adaptation**, and the **MergeTree invariant it leans on** — because every
adaptation is safe *only* under a stated assumption.

Grounded in `ContentAddressedMetadataStorage.cpp` and `ContentAddressedTransaction.cpp`.

---

## 1. Conformance matrix

| Surface method | POSIX contract | CAS behavior | Leans on | Verdict |
|---|---|---|---|---|
| `existsFile/Directory` | stat | resolve ref / list namespace | — | ✔ conformant |
| `getFileSize` | st_size | inline bytes size or manifest entry `blob_size` | — | ✔ conformant |
| `listDirectory` / `iterateDirectory` | readdir | reconstructed from refs + namespace files (`addFirstComponent` collapses to first segment) | — | ✔ conformant (emulated) |
| `getStorageObjects` | object keys | blob location(s) from manifest | — | ✔ conformant |
| `getLastModified` | real mtime | **derived** publish stamp (`published_at_ms`); epoch(0) for table-level/unstamped | mtime only feeds cleanup TTLs + `system.parts` | ⚠ **C-U2** approximate mtime |
| `setLastModified` | set mtime | **accept + ignore** | timestamps derived | ⚠ silent no-op |
| `createHardLink` | shared inode | **COPY**: mutable-by-value, content-by-reference/evidence | parts are **immutable** (never mutate one link and expect the other to change) | ✔ valid adaptation |
| `moveFile`/`replaceFile` (part files) | atomic rename | re-key staged entry / restage committed mutable bytes | single txn scope | ✔ conformant |
| `moveFile`/`replaceFile` (verbatim/mount) | atomic rename | **get→put→remove** (B123), no atomic rename | **single-writer contract** + idempotent re-drive | ⚠ **C-U3** non-atomic |
| `moveDirectory` (RENAME TABLE) | atomic dir rename | best-effort multi-op republish + drop (B126), **no cross-ns atomicity** | re-drivable/idempotent; single-writer | ⚠ **C-U1** non-atomic (split-table on crash) |
| `unlinkFile` (committed content file) | delete file | **deliberate NO-OP** (fail-open) | part-dir is the **indivisible removal unit** (`removeDirectory` frees the part) | ⚠ **C-U4** fail-open |
| `unlinkFile` (staged / committed mutable) | delete file | drop staged / stage removal via `updateRefPayload` | — | ✔ conformant |
| `removeDirectory` (part) | rmdir | **the real removal**: ref-drop of the whole-part manifest | — | ✔ conformant |
| `commit` | all-or-nothing | per-ref publish loop, **no multi-ref atomic publish**; best-effort rollback on exception | MergeTree tolerates missing parts | ⚠ **C-U5** partial on crash |
| `chmod` | set mode | **`notYet` → NOT_IMPLEMENTED (throws)** | MergeTree never chmods parts | ⚠ **C-U6** latent throw |
| `setReadOnly` | set ro flag | accept + ignore | no CA representation | ✔ (benign) |
| `generateObjectKeyForPath` | mint key | **`notYet` → throws** | callers on CA don't need it | ⚠ **C-U7** latent throw |
| `getSubmittedForRemovalBlobs` | blobs to free | **empty** (GC owns reclamation) | disk layer must NOT free CA blobs | ✔ by-design divergence |

---

## 2. The load-bearing adaptations (detail)

### C-U4 — per-file unlink of a committed content file is a NO-OP (fail-open)
MergeTree's fast-removal (`IMergeTreeDataPart::remove`) unlinks **every** part file one-by-one, then
calls `removeDirectory`. On CAS a committed part is **one atomic ref** (its manifest tree); the removal
unit is the whole-part ref-drop. So per-file unlinks **must** be no-ops, and `removeDirectory` frees the
part. The in-code comment is explicit that a blanket fail-closed assert here would fire on every normal
removal. **Cost:** a narrow fail-open — if any caller ever surgically deletes *one* committed content
file and relies on it being gone (without dropping the whole part), the bytes survive (a no-op), whereas
POSIX would delete them. **Not reachable in MergeTree today**; becomes a correctness bug if a future
code path deletes single committed content files.

### C-U1 / C-U3 / C-U5 — no atomic rename / no multi-object atomicity
Object storage has no atomic rename and no multi-key transaction. CAS emulates:
- **RENAME TABLE** (`moveDirectory`, C-U1): republish-all-then-drop; **re-drivable/idempotent** but a
 crash mid-way leaves a **split table** (also DUR2 in the crash audit).
- **verbatim/mount file rename** (`moveFile`, C-U3): get→put→remove; safe under the **single-writer
 contract** (only the owning server renames its own table-level/mount files, so the blind put's
 last-writer-wins can't race) + ENOENT-tolerant idempotent re-drive.
- **multi-part commit** (C-U5): per-ref publish loop with best-effort compensating rollback on
 exception; a crash leaves a partial commit.

All three are **safe under their stated assumptions** (single-writer + re-drive + MergeTree tolerating
missing parts) but each **diverges from the atomic-rename / all-or-nothing guarantee** MergeTree gets
from a local disk. The single-writer contract is enforced at runtime by the mount lease — so C-U3 is
sound as long as that fence holds (cf. the J1 fencing finding in the Jepsen audit: a zombie writer that
slips the fence could in principle race a blind `put`).

### createHardLink → copy (valid)
Hardlinks are used by MergeTree for FREEZE/backups, mutations (link unchanged columns), and part
clones. Because parts are immutable and blobs are content-addressed, "copy" is semantically identical
to a hardlink (nobody mutates a link) **and free** (dedup shares the bytes). Mutable per-part files are
copied by value — also correct. This is the *cleanest* CAS↔MergeTree impedance match.

### C-U6 / C-U7 — unimplemented surface
`chmod` and `generateObjectKeyForPath` throw (`notYet`). These are **latent**: no MergeTree path on a CA
disk calls them today, but a feature that does (e.g. a backup/restore or object-key API path) would hit
a hard `NOT_IMPLEMENTED`. Worth a documented capability matrix ("CAS does not support X") rather than a
raw throw at the call site.

### C-U2 — derived mtime
`getLastModified` returns the part's **publish wall-clock** (`published_at_ms`), or **epoch(0)** for
table-level/unstamped files. mtime feeds only cleanup TTLs and `system.parts.modification_time`, so
approximation is harmless — but epoch(0) on some paths could make a TTL-based "is this temp dir old
enough to reap?" check treat the object as ancient. Low impact given CAS temp handling, but a semantic
mismatch to note.

---

## 3. Summary

| # | Finding | Severity | MergeTree assumption relied on |
|---|---|---|---|
| C-U1 | RENAME TABLE non-atomic → split table on crash | Med | re-drive; single-writer |
| C-U5 | multi-part `commit` partial on crash (no atomic multi-ref) | Low–Med | tolerates missing parts |
| C-U4 | committed single-file unlink = no-op (fail-open) | Low–Med | part-dir is the removal unit |
| C-U3 | verbatim/mount rename non-atomic (get→put→remove) | Low | single-writer fence |
| C-U6/C-U7 | `chmod` / `generateObjectKeyForPath` throw NOT_IMPLEMENTED | Low (latent) | callers don't invoke on CA |
| C-U2 | derived/approximate mtime; epoch(0) fallback | Low | mtime only feeds TTLs/system tables |

**Headline.** CAS implements the full `IMetadataStorage`/`IDisk` surface, but it is a **semantic
adaptation layer**, not a drop-in POSIX disk. Every place where object storage cannot match a POSIX
guarantee (atomic rename, shared-inode hardlink, per-file unlink, real mtime, disk-owned reclamation)
is handled by a **documented adaptation that is correct only under an explicit MergeTree invariant**:
parts are immutable (⇒ hardlink-as-copy, per-file-unlink no-op), the part directory is the indivisible
removal unit (⇒ `removeDirectory` is the real free), and there is a single writer per server-root
(⇒ non-atomic get→put→remove renames are race-free). These invariants **hold for MergeTree today**, so
CAS is contract-conformant *for its intended workload*. The exposure is entirely in the **assumptions**:
a future MergeTree code path that surgically deletes one committed file (C-U4), relies on atomic
RENAME/commit (C-U1/C-U5), calls `chmod`/`generateObjectKeyForPath` (C-U6/C-U7), or a zombie writer that
defeats the single-writer fence (C-U3, tied to J1) would each break a currently-safe adaptation. The
right hardening is a **written capability/assumption matrix** enforced by tests, plus the J1 fencing
fix to keep the single-writer contract that C-U3 depends on airtight.

## cas-interleaving-audit.md

Language: Markdown

# CAS — Cross-Protocol Interleaving Audit (concurrent write ∥ read ∥ GC)

Scope: exhaustive state-transition tracing of the **three protocols running concurrently** on shared
state — a blob `B`, its owning manifest `M`, and the ref `R` in shard `S`. Method: take each protocol's
step sequence as a spine and, at every step boundary, ask *"what if a write / read / GC happens here?"*,
resolving each interleaving through the coupling mechanisms and reporting the reachable defects.

This audit builds on the per-protocol audits (`cas-write-protocol-audit.md`,
`cas-read-protocol-audit.md`, `cas-gc-protocol-audit.md`) and feeds the Jepsen and security audits.

---

## 1. Coupling vocabulary (every interleaving funnels through these)

- **CG** — commit gate: `observeAndAdmit` / `promote` check `RetireView::isCondemnedToken(hash, token)`
 before referencing a blob; condemned ⇒ `ABORTED` → re-upload from source / `copyForwardFromCondemned`
 (INV-1).
- **AF** — ack floor: GC `min_ack = min(live writers' observed_gc_round)`; graduation requires
 `condemn_round < min_ack`. A writer's ack advances **only after** `RetireView.refresh()` loads that
 round (drain under `view_gate` exclusive).
- **2P** — two-phase graduation: condemn → `delete_pending` (first floor pass) → `deleteExact` (next).
- **XT** — exact-token delete: `deleteExact(If-Match token)`; re-incarnation ⇒ `TokenMismatch` ⇒ no delete.
- **FB** — fold barrier / clamp / `suppress_destructive`: a missing/absent-at-HEAD body freezes the
 cursor and halts deletes pool-wide.
- **VG** — `view_gate`: `mutateShard` (shared) vs beat `RetireView.refresh` (exclusive) serialize, so an
 ack can't overtake an in-flight commit's gate evaluation.
- **INC** — incarnation-keyed fold cursor (ABA protection).
- **TTL / RYOW** — read `allow_stale` ~200 ms cache + `shard_write_seq` same-Store invalidation.
- **R1** — the reader's **unpinned** deferred blob-GET window (read audit R1).

---

## 2. Spine A — Writer dedup-references blob B (`build → precommit → putBlob(dedup B) → promote`)

| Point | GC here? | another WRITE here? | READ here? |
|---|---|---|---|
| A1 after stageManifest(M), before precommit | M is orphan (no owner); GC orphan sweep only reaps watermark-dead builds → our live build spared. ✔ | staging M' has distinct instance id, no collision. ✔ | no ref ⇒ resolveRef=∅ ⇒ FILE_DOESNT_EXIST (uncommitted). ✔ |
| A2 after precommitAdd | GC folds precommit +1 → B not zero-in-degree ⇒ never condemned (shield). ✔ | concurrent drop of another ref to B: our +1 holds ⇒ spared. ✔ | — |
| A3 putBlob(B): observeAndAdmit HEADs B (token T) | condemn race: CG fires if our view ≥ condemn round (re-upload); else AF holds B (our ack < r) until our +1 folds ⇒ **THM-NO-RETURN**. ✔ | two writers dedup B: set-based +1, union. ✔ | — |
| A4 B admitted, before promote | B has our folded +1 ⇒ not condemned; if precommit body missing at fold ⇒ FB clamp ⇒ no deletes. ✔ | — | — |
| A5 promote: HEAD each blob, journal owner-check, condemn re-check | precommit falsely reclaimed + B condemned ⇒ `copyForwardFromCondemned` displaces B to fresh token; GC pending `deleteExact(If-Match T)` ⇒ **XT mismatch** ⇒ no delete. ✔ | concurrent promote to same R (lost-ACK/cross-writer): unconditional `refs[R]=…` ⇒ **prior manifest leaked** (**W1 / X2**). ⚠ | mid-promote read sees old committed state, never half-promote. ✔ |
| A6 after promote commits | committed +1 folded; B permanently spared while R lives. ✔ | — | reader resolves R→M→B (Spine B). ✔ |

**Net:** dedup-reference-vs-condemn is closed by **CG ∨ AF**. The blemish is A5, where the
promote-overwrite leak (X2/W1) surfaces as a GC **blob/manifest leak** under RENAME/lost-ACK replay —
over-count, never dangle.

---

## 3. Spine B — Reader reads part P (`resolveRef(R) → readManifest(M) → locate(B) → [deferred] blob GET`)

| Point | WRITE here? | GC here? | another READ here? |
|---|---|---|---|
| B1 resolveRef(R) TTL/decode | same-Store publish/drop bumps `shard_write_seq` + evicts cache ⇒ RYOW; remote ⇒ ≤200 ms stale. ✔ | GC never mutates a live shard's refs/journal (only empty-shard tombstone reclaim). ✔ | single-flight coalescing (F-N1 convoy risk). ⚠ liveness |
| B2 hold M's manifest_ref, before readManifest | writer drops/republishes R; we still hold M's id (stale) → proceed. | GC hasn't folded the drop yet. | — |
| B3 readManifest(M) HEAD+GET | republish may have made M2 + dropped M; we read M (immutable, fine). | drop folded + `mfCleanup` deleted M ⇒ HEAD 404 ⇒ **FILE_DOESNT_EXIST INV-NO-DANGLE** (fail-closed). Bounded: drop→fold→delete lag ≫ 200 ms TTL. ✔ surfaced-as-error | — |
| B4 locate(B): pipeline holds only StoredObject(B); M discarded | — | — | — |
| B5 **deferred blob GET** (T_get ≫ T_plan) | writer drops R; nothing pins R/M/B. | **X1/R1:** R dropped ⇒ condemn→pending→`deleteExact(B)`; if the pipeline completes before T_get, GET ⇒ **NoSuchKey**. Same-node fenced by MergeTree part liveness; **ref-less/cross-node reader unprotected.** 2P+AF only bound the window (F-N2 delay widens it). ✖ | two readers share B's physical-key cache; no contamination. ✔ |

**Net:** committed-only resolution + INV-NO-DANGLE make B3 fail-closed; the real exposure is **B5** — no
reader pin across the deferred GET.

---

## 4. Spine C — GC condemns/deletes B (`floor → fold → condemn → pending → deleteExact`)

| Point | a WRITE here? | a READ here? | (GC internal) |
|---|---|---|---|
| C1 latch min_ack (before fold cut) | post-cut writer commit invisible this pass; its ack can't have advanced past its own commit (AF order, `CaGcAckFloorZombie`). ✔ | — | floor from live mounts' observed_gc_round |
| C2 fold shard S journal `(cursor, version]` | writer +1 in window ⇒ folded/spared; after ⇒ next delta; drop+recreate S ⇒ **INC** cursor reset, full re-fold. | reader invisible to fold (no edge) — why B5 is unprotected. | precommit +1 shields in-upload blobs |
| C3 condemn B: HEAD (token T), append `(B,T,r)` | writer refs B, view stale ⇒ admits T; AF holds B until writer acks r ⇒ then CG re-uploads (XT protects delete). View fresh ⇒ CG fires now. ✔ | reader with B located + GET pending: B only *condemned* (2P), GET still OK. ✔ | absent-at-HEAD ⇒ forget, never fabricate token |
| C4 graduate: `r < min_ack`? | any live writer ack < r ⇒ not graduated (held) ⇒ THM-NO-RETURN. ✔ | — | needs `!suppress_destructive` |
| C5 delete_pending published | writer sees `(B,T)` in refreshed RetireView ⇒ CG refuses ⇒ recreate. ✔ | reader that resolved B before condemn, GET now: B still exists (pending≠deleted). ✔ | terminal — no spare |
| C6 next pass `deleteExact(B,T)` | writer recreated B under T' between pending/delete ⇒ **XT mismatch** ⇒ B(T') survives. ✔ | **R1 window closes:** a ref-less reader still holding location{B,T} ⇒ **NoSuchKey**. ✖ | idempotent on NotFound |
| C7 single gc/state CAS | concurrent writer shard CAS on a different key (no contention); lost-ACK ⇒ spurious ABORTED (G-N3). ✔ | — | zombie leader's CAS fails |
| C-clamp any shard clamps | in-flight precommit body not yet uploaded ⇒ FB clamp ⇒ `suppress_destructive` ⇒ no deletes (protects the reference). Persistent ⇒ **G-N1** pool-wide halt. ✔ safety / ✖ liveness | reader unaffected. ✔ | pass-wide scope |

**Net:** every writer/GC interleaving around B is closed by **CG ∨ AF ∨ 2P ∨ XT** (no dangle, no
return). The reader participates in none of these ⇒ **C6 × B5** is the lone three-way dangle-to-reader.

---

## 5. Consolidated three-way invariant matrix

| Interleaving | Guard(s) | Verdict |
|---|---|---|
| Write dedup-refs B ∥ GC condemns B | CG ∨ AF (THM-NO-RETURN) | ✔ no dangle |
| Write refs B ∥ GC deletes B | CG + XT (copy-forward + token-mismatch) | ✔ no return |
| Write precommit-uploads B ∥ GC fold | precommit +1 ∥ FB clamp | ✔ shielded |
| Write promotes ∥ GC condemned a falsely-reclaimed precommit | promote reval → copy-forward + XT | ✔ |
| Write drop/rename R ∥ GC folds removal ∥ Read resolves R | INV-NO-DANGLE fail-closed at readManifest | ✔ surfaced-as-error |
| **Read deferred-GET(B) ∥ Write drop R ∥ GC delete B** | 2P + AF bound the window; **no reader pin** | ✖ **X1 dangle-to-ref-less-reader** (widened by F-N2) |
| Write promote-overwrite same R ∥ GC fold | INV_OVER_COUNT_ONLY | ⚠ **X2 manifest/blob leak** (=W1) |
| Any shard clamp ∥ all writers/readers | suppress_destructive | ✔ safety / ✖ **X3 pool-wide reclaim halt** (=G-N1) if persistent |
| Write commit after fold cut ∥ GC graduate | AF floor-latched-before-cut | ✔ (CaGcAckFloorZombie) |
| Read TTL-stale resolve ∥ remote write ∥ GC delete | TTL(200 ms) ≪ condemn→delete latency | ✔ (coupling unenforced — R3/F-N3) |
| Write mutable-file update ∥ Read force-fresh ∥ GC | RYOW (shard_write_seq); GC doesn't touch mutable_files | ✔ |

---

## 6. Findings (new / re-confirmed under three-way concurrency)

| # | Finding | Severity | Relation |
|---|---|---|---|
| X1 | Ref-less reader dangle: `deleteExact(B)` (C6) races the reader's unpinned deferred GET (B5) | **Med-High** | = read audit R1; the sole reachable cross-protocol dangle |
| X2 | `promote`-overwrite leaks the prior manifest under RENAME/lost-ACK replay (A5) | Med | = write audit W1 (confirmed reachable under concurrency) |
| X3 | Persistent shard clamp → pool-wide reclamation halt (C-clamp) | Med-High (liveness) | = GC audit G-N1 |

---

## 7. Headline

Every **write↔GC** interleaving around a shared blob is airtight: **CG ∨ AF ∨ 2P ∨ XT** compose so no
ordering yields a dangle or a returned token (**THM-NO-RETURN**), and every crash/lost-ACK biases to
**over-count** (leak), never data loss. The **reader** is the structural outlier — it registers no
reachability edge and holds no GC-honored token across its **deferred, unpinned** blob GET, so the one
genuinely reachable cross-protocol correctness defect is **X1**: `GC deleteExact(B)` racing a ref-less
reader's lazy blob fetch. Everything else degrades to **leaks** (X2, promote-overwrite) or
**liveness/operability cliffs** (X3, pool-wide clamp). The single highest-leverage fix is a reader pin
(close X1) — the only interleaving that loses committed data on the reader side.

## cas-jepsen-anomaly-audit.md

Language: Markdown

# CAS — Exhaustive Jepsen / Elle Anomaly Audit

Scope: the `metadata_type = content_addressed` MergeTree disk backend (CAS pool on S3).
Method: map CAS operations onto Jepsen/Elle abstractions, then walk **every** anomaly in the
supplied taxonomy and assign a verdict grounded in the code paths audited previously
(write, read, GC, three-way interleaving, and the J1–J5 fencing analysis).

Verdict legend:
- **IMMUNE** — impossible by construction (the abstraction doesn't exist, or the model forbids it).
- **SAFE** — reachable in principle but closed by a named mechanism.
- **BOUNDED** — cannot be fully prevented but is bounded (staleness window, over-count leak).
- **REACHABLE** — a real finding; cross-referenced to J1–J5 or prior write/read/GC findings.
- **BY-DESIGN** — allowed by the system's declared (non-serializable) contract.

Finding cross-refs used throughout:
- **J1** pause/TOCTOU zombie write — shard `casPut` fenced by content token, not `writer_epoch`.
- **J2** VM-clone split brain (same `server_uuid`), bounded by renew period.
- **J3** clock-skew reclaim — wall-clock lease expiry vs boot-clock local fence.
- **J5** lost-ACK shard-CAS replay → journal duplicate append (benign, set-idempotent).
- **X1 / R1** ref-less reader dangle — unpinned deferred blob GET vs GC delete.
- **W1** promote-overwrite manifest leak (RENAME/lost-ACK), over-count only.
- **W-N1** presence-asserting closure misreports lost-ACK-succeeded write as failure.
- **G-N1** persistent shard clamp → pool-wide reclamation halt.

---

## 0. Workload mapping (the bar we judge against)

| Jepsen abstraction | CAS realization |
|---|---|
| **Register** (compare-and-set) | A `RootShard` object at `cas/refs/ / `; `shard_version` is the version; S3 conditional PUT (`casPut(key, body, token)`) is the CAS. **Per-shard linearizable.** |
| **List-append log** | The `journal` inside each `RootShard` — an append-only vector of `RootOwnerEvent` (publish/drop/rename/tombstone). Directly a list-append workload. |
| **Set** | Blob **source-edge set** (in-degree as a set of `(kind,hash)→{owner}` edges); the `RetireView` condemned `(kind,hash)→[tokens]` map. Set semantics chosen deliberately for idempotency. |
| **Counter** | `writer_epoch` (durable monotone), `build_sequence` (per-process monotone), GC `round`, `shard_version`, `snap_generation`. |
| **Session / process** | A writer **incarnation** = `(server_uuid, writer_epoch)` from one `Store::open`; `process_epoch` identity; the mount lease is the session token. |
| **Real-time clock** | Two clocks: **wall-clock** (`system_clock`, mount lease `expires_at_ms`) and **boot-clock** (`bootMsNow`, local write fence). Split relevant to J3. |
| **Transaction** | **Single-shard only.** One part publish/drop/promote = one shard CAS = atomic. **Multi-shard ops are NOT transactional** (RENAME = create-dest-shard then drop-source-shard, two CAS). |

**Declared consistency contract:**
- **Single shard:** linearizable register + linearizable append log (S3 per-key conditional PUT).
- **Reads:** committed-read; `allow_stale` = bounded-stale (≤ ~200 ms TTL), force-fresh = current
 (modulo eventually-consistent backend, F-N3).
- **Cross-shard:** **no atomicity, no serializability guarantee** — best-effort per-object.
- **Blobs/manifests:** immutable, content-addressed → write-once, never mutated.
- **GC:** a background actor, not a client transaction; its safety contract is
 *no dangle, no returned token, over-count-not-under-count* (INV_NO_DANGLE / INV_NO_RETURN / INV_OVER_COUNT_ONLY).

The taxonomy below is designed for **multi-object serializable transactional stores**. CAS is a
**single-object linearizable store with a background collector**, so a large fraction of the
transactional anomalies are *IMMUNE by construction* (no multi-object transactions exist to exhibit
them). The interesting findings cluster in: **single-register linearizability under fencing failure
(J1–J3)**, **cross-shard non-atomicity (fractured/phantom, BY-DESIGN)**, **stale reads (BOUNDED)**,
and **the collector's interaction with reads (X1/R1)**.

---

## 1. Adya serialization anomalies

| Anomaly | Definition | CAS verdict | Rationale |
|---|---|---|---|
| **G0 — write cycle (dirty write)** | WW-cycle: `T1→T2→T1` via write-write deps | **IMMUNE** (single-shard) / **SAFE** (cross) | On one shard, `casPut` totally orders writes by `shard_version`; no WW cycle possible. Across shards there are no multi-object transactions, so no cross-object WW cycle can form. |
| **G1a — aborted read** | Read of a value from an aborted transaction | **SAFE** | Two-phase precommit→promote: a reader resolves **committed** refs only (`allow_stale=false` default on 2-arg `resolveRef`). An abandoned build's staged manifest has no ref → invisible. |
| **G1b — intermediate read** | Read of a non-final intermediate write of a txn | **IMMUNE** | A shard CAS publishes the **final** encoded body atomically; there is no intermediate state exposed. Manifests/blobs are immutable (single write). |
| **G1c — circular information flow** | WR+WW cycle among txns | **IMMUNE** (single) / **SAFE** (cross) | Per-shard linearizability gives an acyclic version order. No cross-shard read-from that could close a cycle (reads take a point-in-time shard snapshot). |
| **G-single — single anti-dependency cycle** | One RW edge closes a cycle (read-skew class) | **BY-DESIGN (cross-shard)** | Within a shard: none (linearizable). **Across shards** (e.g., a query reading two parts whose refs live in different shards while a RENAME/GC moves one) a reader can observe a state no serial order allows — but CAS never promised cross-shard serializability. See §5 read-skew. |
| **G2-item — item anti-dependency cycle** | RW cycle over concrete items | **BY-DESIGN (cross-shard)** | Same as G-single; only reachable across shards, which are independent registers. |
| **G2-element — predicate anti-dependency cycle** | RW cycle involving a predicate/range | **BY-DESIGN** | A "list all refs in namespace" spans shards read one-at-a-time; a concurrent publish to an unread shard is a phantom (predicate anti-dependency). By design — no snapshot across shards. |
| **G2 mixed cycles** | Mixed WW/WR/RW cycle | **SAFE (single)** / **BY-DESIGN (cross)** | No single-shard cycle exists; cross-shard "cycles" are the accepted non-serializable regime. |
| **Non-serializable execution** | Any of the above | **BY-DESIGN across shards** | CAS is per-object linearizable, **not** multi-object serializable. Documented contract, not a defect. |

**Edge types (what actually forms in CAS histories):**

| Edge | Present? | Notes |
|---|---|---|
| **WW (write-write)** | Yes, per shard | Totally ordered by `shard_version` (linearizable CAS). |
| **WR (write-read)** | Yes | Reader reads the committed shard body a writer produced. |
| **RW (anti-dependency)** | Yes, **cross-shard only** | The sole source of non-serializable cross-shard cycles (G-single/G2). Within a shard, reads see a consistent snapshot. |
| **PO (process order)** | Preserved per Store | Same-Store RYW via `shard_write_seq` bump + decode-cache erase (B157). |
| **RT (real-time order)** | Per shard: yes (linearizable). Cross-shard/stale-read: **violable** | `allow_stale` reads can return a value older than a completed write (bounded ≤ TTL) → RT violation under the stale-read mode; force-fresh restores RT modulo J1–J3 fencing and F-N3. |

---

## 2. Elle graph outcomes

| Outcome | CAS verdict |
|---|---|
| **Acyclic (valid)** | The expected outcome for any single-shard sub-history: `shard_version` yields a total order. |
| **Cyclic (invalid)** | Only constructible by spanning ≥2 shards (independent registers) or by an unfenced zombie write (J1) reordering a single shard's version line. |
| **G0 / G1a / G1b / G1c** | IMMUNE/SAFE as above. |
| **G-single / G2 / G2-item / G2-element** | Not exhibited within a shard; the cross-shard versions are BY-DESIGN (no serializability claim). |

---

## 3. Session guarantees

| Guarantee | Verdict | Mechanism / caveat |
|---|---|---|
| **Read Your Writes (RYW)** | **SAFE (same Store)** / **BOUNDED (cross-server)** | Same-Store: after `casPut` commits, `++shard_write_seq[key]` + `shard_decode_cache.erase(key)` under the cache lock fences in-flight readers (B157) → a subsequent same-Store read never serves the pre-write decode. Cross-server: another server's read can lag ≤ TTL (~200 ms) on the `allow_stale` path. |
| **Monotonic Reads (MR)** | **BOUNDED** | Same-Store reads are monotone (cache keyed by shard + write-seq). Across servers with independent TTL caches, a reader on server A then server B could see B's older cached shard → non-monotonic within ≤ TTL. Not enforced cross-server. |
| **Monotonic Writes (MW)** | **SAFE (per incarnation)** / **REACHABLE (J1)** | A single writer's shard writes are ordered by `shard_version` CAS. **J1**: a paused/superseded writer resuming can land a write *after* a fresh incarnation's writes if it hits an untouched shard — a monotonic-writes violation across the fencing boundary (zombie write). |
| **Writes Follow Reads (WFR)** | **SAFE (single shard)** / **BY-DESIGN (cross)** | A publish that depends on a prior read of the same shard is ordered after it (CAS token). Cross-shard causal ordering is not tracked. |

---

## 4. Causal consistency anomalies

| Anomaly | Verdict | Rationale |
|---|---|---|
| **Causal reverse** | **BY-DESIGN (cross-shard)** | No cross-shard causal metadata; effects on different shards have no enforced causal order. Within a shard, `shard_version` respects causality. |
| **Missing causal dependency** | **BOUNDED** | `allow_stale` read may miss a causally-prior remote write (≤ TTL). Force-fresh + same-Store RYW closes the same-session case. |
| **Causality violation** | **SAFE (single)** / **BY-DESIGN (cross)** | Single-shard `shard_version` is a Lamport-like per-object clock; cross-shard has none. |

---

## 5. Snapshot isolation anomalies

CAS provides **no multi-object snapshot**; each shard read is an independent point-in-time snapshot.

| Anomaly | Verdict | Rationale |
|---|---|---|
| **Write skew** | **IMMUNE** | Requires two transactions writing different objects based on a common read invariant. No multi-object transactions exist. Each publish is a single-shard CAS. |
| **Read skew** | **BY-DESIGN (cross-shard)** | A query reading part P1 (shard s1) and P2 (shard s2) can observe P1@v5 with P2@v2 if a writer/RENAME/GC moves P2 between the two shard reads. Accepted: no cross-shard snapshot. Same-shard: consistent. |
| **Fractured read** | **REACHABLE-BY-DESIGN (RENAME)** | `republishRef` (RENAME TABLE, DETACH/ATTACH) is **create-dest-shard then drop-source-shard** — two non-atomic CAS. A concurrent reader can see **both** old+new names or **neither** during the window. This is the sharpest cross-shard fracture; it is a *known consequence* of no cross-shard transaction, not a hidden bug. Bounded by the gap between the two CAS ops. |
| **Lost update** | **SAFE** | Concurrent updates to the same shard serialize via CAS (loser re-reads + replays closures). Set-based in-degree makes concurrent blob references a union, never a lost increment. |
| **Predicate anomaly / phantom** | **BY-DESIGN** | "All refs in namespace" enumerates shards sequentially; a publish to an already-passed/not-yet-read shard is a phantom. No predicate locking across shards. |
| **Inconsistent snapshot** | **BY-DESIGN (cross-shard)** | Same root cause as read skew. |

---

## 6. Read phenomena

| Phenomenon | Verdict | Rationale |
|---|---|---|
| **Dirty read** | **SAFE** | Reads resolve committed refs only; uncommitted (staged/precommit) manifests have no ref. The in-flight read-your-writes overlay (B59) exposes uncommitted data **only to the writing session itself** (projection spill-merge), never to other readers. |
| **Non-repeatable read** | **BOUNDED / BY-DESIGN** | Re-reading the same ref after a concurrent commit can return a newer manifest (expected for a mutable register). Immutable blobs/manifests are perfectly repeatable by content hash. |
| **Phantom read** | **BY-DESIGN** | Cross-shard enumeration (see predicate anomaly). |
| **Stale read** | **BOUNDED** | `allow_stale` path serves cached shard decode up to TTL (~200 ms). Bounded and intentional; force-fresh avoids it. Cross-server MR/RYW caveats as §3. |
| **Future read** | **IMMUNE** | A read can never observe a not-yet-committed write: `casPut` must complete before the body is fetchable; content-addressed keys can't be predicted. |
| **Missing read** | **REACHABLE (X1/R1)** | The ref-less reader dangle: reader resolves ref→manifest→blob-location at plan time, discards the manifest, then does the **deferred, unpinned** blob GET later. If the ref is dropped and GC completes condemn→pending→delete first, the deferred GET hits `NoSuchKey` → a *committed* datum becomes unreadable mid-query for ref-less/cross-node readers. **The one true read-side correctness hole.** |
| **Duplicate read** | **IMMUNE (content)** | Content-addressed GET is idempotent; two reads of the same key return identical bytes or fail — never a spurious duplicate row. |

---

## 7. Write phenomena

| Phenomenon | Verdict | Rationale |
|---|---|---|
| **Dirty write** | **SAFE** | Single-shard CAS + two-phase precommit→promote: no two writers overwrite each other's uncommitted state; the loser re-reads and replays. |
| **Lost write** | **SAFE (ref register)** / **REACHABLE-as-leak (W1)** | The **ref** is never lost (CAS-serialized). But **promote-overwrite (W1)**: re-publishing over an existing committed ref installs the new manifest *without releasing the old one* → the old manifest+blobs become an **orphaned (leaked)** write. Not a lost *ref*, but a lost-to-GC object (over-count, INV_OVER_COUNT_ONLY-safe). |
| **Overwritten write** | **REACHABLE-as-leak (W1)** | Exactly W1 — the overwritten manifest is orphaned rather than reclaimed. |
| **Write inversion** | **REACHABLE (J1)** | Two writes committing in an order inverse to real-time. Impossible within a live incarnation (CAS-ordered); reachable when a paused/superseded writer (J1) lands after a fresh incarnation on an untouched shard. |
| **Write reordering** | **REACHABLE (J1/J5)** | J1 zombie write reorders relative to the fencing boundary; J5 lost-ACK replay re-appends journal events out of their original position (benign, set-idempotent). |
| **Dirty write cycle (G0)** | **IMMUNE** | Per §1. |

---

## 8. Register checker anomalies

Register = a `RootShard` (its `refs` map + `shard_version`).

| Anomaly | Verdict | Rationale |
|---|---|---|
| **Invalid read** | **SAFE** | Decode is CRC + protobuf-framing + magic/version checked (`decodeRootShard`); a malformed body fails closed (`CORRUPTED_DATA`), never returns a fabricated value. |
| **Stale read** | **BOUNDED** | `allow_stale` TTL window (§6). |
| **Impossible value** | **IMMUNE** | A shard value is only ever a validly-encoded `RootShard` produced by a `casPut`; no partial/torn body (single-object PUT is atomic on S3). |
| **Missing write** | **REACHABLE (J1)** | A write that acknowledged success but is absent — the J1 zombie can be **superseded**: it commits, then a fresh incarnation's later CAS on the same shard overwrites without seeing it (it read before the zombie's late PUT). The zombie's write is then "missing" from the surviving line. Bounded to the pause window; content CAS makes it rare (requires exact-shard non-contention). |
| **Linearizability violation** | **REACHABLE (J1/J2/J3)** | Single-shard CAS is linearizable **only while single-writer holds**. J1 (pause), J2 (clone), J3 (clock skew) each create a dual-writer window where the shard register is momentarily non-linearizable (the store enforces a content token, not a `writer_epoch` fence). This is the headline register-level finding. |

---

## 9. List-append checker anomalies

List = the per-shard `journal` (append-only `RootOwnerEvent` vector). This is the richest mapping.

| Anomaly | Verdict | Rationale |
|---|---|---|
| **Lost element** | **SAFE** | Each journal append rides the same atomic shard CAS as the ref change; a committed event can't vanish (CAS-durable). A losing CAS discards and **replays** its append onto the winner's state. |
| **Duplicate element** | **REACHABLE (J5)** | Lost-ACK on the shard `casPut` → the writer replays and **re-appends** the publish/promote event → the journal contains a duplicate `RootOwnerEvent`. GC's set-based fold makes it **semantically idempotent** (in-degree is a set), so it's *journal bloat*, not incorrectness. Also **W-N2**. |
| **Unexpected element** | **SAFE** | Every appended event is one a real closure produced under the fence; the fold rejects malformed/incompatible events (`decodeRootShard` journal-integrity check → `CORRUPTED_DATA`). |
| **Reordered element** | **SAFE (within incarnation)** / **REACHABLE (J1)** | `transition_version` stamps each event with its committing `shard_version` → total order within a live writer. A J1 zombie could append with a `transition_version` that a fresh incarnation didn't expect (reorder across the fence). |
| **Forked history** | **REACHABLE (J1/J2)** | The literal split-brain outcome: two incarnations (J1 zombie / J2 clone) each believing they own the shard produce **divergent journal continuations** until content CAS re-converges them (the loser re-reads). Fork window bounded by CAS serialization + renew period. |
| **Missing prefix** | **SAFE** | GC trims journal **prefix** only up to a fully-folded, ack-floored watermark; the `cas-gc-rebuild` guard fails **closed** if it detects a trimmed prefix it can't account for (prevents under-count). A reader/folder never sees a gap it isn't allowed to see. |
| **Divergent prefix** | **SAFE** | The committed prefix is single-valued per shard (CAS); divergence is confined to the uncommitted fork tips (J1/J2) that CAS discards. |

---

## 10. Set checker anomalies

Sets = blob **source-edge (in-degree) set** and the **RetireView condemned set**.

| Anomaly | Verdict | Rationale |
|---|---|---|
| **Missing element** | **SAFE** | An edge (blob reference) added by a committed publish is durably in the shard journal; GC's fold reconstructs it. Precommit adds a `+1` edge that shields in-upload blobs. |
| **Unexpected element** | **SAFE** | Edges only come from real owner events; GC never fabricates an edge. |
| **Duplicate insertion** | **IMMUNE (by design)** | The in-degree is a **set** precisely so duplicate references (dedup, replay) collapse to one edge — duplicates are *defined away*, not an error. |
| **Lost insertion** | **SAFE (THM-NO-RETURN)** | A blob reference racing a condemn is caught by the commit gate (`observeAndAdmit`/`promote` → `isCondemnedToken`) → re-upload; or held by the ack floor until the writer's `+1` is folded. The edge is never lost under the write↔GC plane. |
| **Failed removal** | **BOUNDED-as-leak (W1)** | `dropRef` reliably removes the edge; **but** the promote-overwrite path (W1) fails to remove the *old manifest's* edges → they persist (leak). Over-count, never under-count. |
| **Zombie value** | **REACHABLE (J1)** | The exact Jepsen term for J1: a fenced/superseded writer's value (a shard edge) reappears/persists after its lease died — because the store has no `writer_epoch` fence on the CAS. Also the GC-side "zombie leader" is **SAFE** (exact-token `deleteExact` + `gc/state` CAS reject it). |

---

## 11. Counter checker anomalies

Counters: `writer_epoch`, `build_sequence`, GC `round`, `shard_version`, `snap_generation`.

| Anomaly | Verdict | Rationale |
|---|---|---|
| **Lost increment** | **SAFE** | `writer_epoch` bumps via CAS on a durable pool object (`allocateWriterEpoch`); a losing bump retries against the winner → no lost increment. `shard_version` increments ride the atomic shard CAS. |
| **Duplicate increment** | **SAFE / BOUNDED** | `writer_epoch` is strictly monotone (CAS) — no duplicate value handed out. `build_sequence` is per-process strictly increasing. (A J5 replay re-appends an event but does **not** re-mint an epoch.) |
| **Counter regression** | **SAFE** | All four counters are monotone by CAS/lock construction. `computeHeartbeatFloor` is *conservative* — `min_ack` **never rises** under S3 faults (it treats unreadable/contended mounts as lagging), so the GC round floor cannot regress into unsafety. |
| **Counter jump** | **SAFE (safe direction)** | `writer_epoch` may **skip** values across crashes (allocate-then-crash) — the design tolerates gaps (equality/`>` checks, never "== previous+1"). A jump is safe, not an anomaly here. |
| **Impossible counter value** | **SAFE** | Fail-closed decode guards reject a non-monotone/garbage counter (epoch reset hazard → guard aborts; `cas-gc-rebuild` baseline guard rejects an implausible round). |

---

## 12. Linearizability checker results

Object under test: a single `RootShard` register.

| Result | Verdict |
|---|---|
| **Linearizable** | **YES, single-shard, single-writer** — S3 per-key conditional PUT + content-token CAS give a linearizable register and append log. |
| **Not linearizable** | **REACHABLE (J1/J2/J3)** — dual-writer windows (pause / clone / clock skew) momentarily break linearizability because the CAS carries no fencing token. Also `allow_stale` reads are intentionally non-linearizable (bounded stale). |
| **Real-time order violation** | **REACHABLE** — `allow_stale` (bounded) always; J1–J3 (fencing) in the dual-writer window. |
| **Operation inversion** | **REACHABLE (J1)** — zombie write inverts real-time order across the fence. |
| **Impossible history** | **IMMUNE** — decode/CRC/framing guards mean no read ever returns a value no write produced. |

---

## 13. Sequential consistency

| Result | Verdict |
|---|---|
| **Sequential consistency violation** | **SAFE per shard** (PO preserved via `shard_write_seq`), **BY-DESIGN cross-shard** (no global order). J1 can break per-process order at the fence (see MW). |

---

## 14. Serializability

| Result | Verdict |
|---|---|
| **Serialization cycle / dependency cycle / anti-dependency cycle** | **IMMUNE within a shard** (single-object linearizable ⇒ acyclic). **BY-DESIGN across shards** — CAS does not offer multi-object serializability; cross-shard RW cycles (RENAME, cross-shard SELECT) are permitted by contract. |
| **Non-serializable execution** | **BY-DESIGN (cross-shard)** — documented limitation, not a defect. |

---

## 15. Strict serializability

| Result | Verdict |
|---|---|
| **Real-time serialization violation** | **BY-DESIGN cross-shard**; **REACHABLE (J1–J3)** for the single-shard real-time guarantee under fencing failure. CAS never claimed strict serializability across objects. |

---

## 16. Availability / liveness failures (operational, not consistency)

| Failure | Verdict | Rationale |
|---|---|---|
| **Timeout** | **BOUNDED** | S3 op timeouts surface as retryable errors; write path fails closed. **F-N1**: a coalesced shard read has **no deadline** → can stall all coalesced readers (reader convoy) — a real liveness finding. |
| **Indefinite block** | **REACHABLE (F-N1)** | Single-flight shard-read coalescing with no deadline → indefinite block of followers if the leader's GET hangs. |
| **Request dropped** | **SAFE** | Lost-ACK handled: writes fail closed or replay (idempotent); **W-N1** caveat — presence-asserting closures may misreport a *succeeded* dropped-ACK write as failure. |
| **Partition-induced unavailability** | **BOUNDED** | A partition from S3 halts writes/GC (fail-closed) but never corrupts; reads serve cache within TTL. |
| **Deadlock** | **SAFE** | Fixed lock order (`view_gate` → RetireView mutex; `shard_queue_mutex` discipline in flat-combining). No inversion found. |
| **Livelock** | **BOUNDED** | CAS contention retries are bounded (`MAX_CAS_ATTEMPTS` → ABORTED). Flat-combining convoy (**W-N3**) can amplify a slow leader into batch-wide retries under S3 stall. |
| **Crash / Fail-stop** | **SAFE** | Two-phase precommit→promote + durable epoch/owner/mount make crashes recoverable; a hard-killed mount is waited-out and reclaimed (`claimMountAwaitingExpiry`, S13). |
| **Recovery failure** | **BOUNDED (G-N1, G-N2)** | `cas-gc-rebuild` recovers lost `gc/state`; but a **persistent shard clamp halts all reclamation pool-wide (G-N1)**, and lost GC-internal artifacts wedge GC until manual rebuild (G-N2). Safety preserved, liveness/operability at risk. |

---

## 17. Data integrity failures

| Failure | Verdict | Rationale |
|---|---|---|
| **Data loss** | **SAFE (write/GC plane)** / **REACHABLE (X1/R1 read plane)** | Write↔GC composition (commit gate ∨ ack floor ∨ two-phase graduation ∨ exact-token delete) admits **no** committed-data loss. The lone data-loss path is **X1/R1**: a ref-less reader's unpinned deferred blob GET racing a GC delete → `NoSuchKey` mid-query. |
| **Data corruption** | **IMMUNE** | Content-addressed keys are self-verifying: `poolContentHash(payload)` is checked against the key on copy-forward/read; blobs/manifests/shards carry CRC + magic + version. A corrupt object fails the hash/CRC and is rejected, never served. |
| **Torn write** | **IMMUNE** | Every object (blob, manifest, shard) is written by a **single** PUT — S3 makes it all-or-nothing. No in-place mutation. |
| **Partial write** | **IMMUNE** | Same as torn write; a partially-uploaded multipart never becomes the live key (conditional PUT / assembly completes atomically or is abandoned as orphan debris — W-N4). |
| **Partial transaction** | **BY-DESIGN (cross-shard RENAME)** | A single-shard op is atomic. A multi-shard RENAME (`republishRef`) can be left half-done (dest created, source not dropped, or vice-versa) on crash → the fractured-read / manifest-leak (W1) consequence. Bounded, over-count. |
| **Orphaned transaction** | **BOUNDED (W-N4)** | Interrupted uploads leave orphan multipart uploads / ownerless manifest bodies; reclaimed by watermark sweep + lifecycle rules. Leak, not loss. |

---

## 18. Replication anomalies

("Replicas" here = independent servers mounting the same CAS pool, and S3's own replication.)

| Anomaly | Verdict | Rationale |
|---|---|---|
| **Replica divergence / divergent replicas** | **REACHABLE (J1/J2)** | Two writer incarnations forking a shard journal (split brain) diverge until content CAS re-converges. Bounded by CAS + renew period. |
| **Split brain** | **REACHABLE (J1/J2/J3)** | The central Jepsen finding: lease-as-mutex without a storage fencing token → pause / clone / clock-skew each open a dual-writer window. Fix = carry `writer_epoch` into the shard CAS precondition (as GC already does with exact-token deletes). |
| **Stale replica** | **BOUNDED** | Cross-server `allow_stale` reads lag ≤ TTL. On an eventually-consistent S3, even force-fresh can race a stale version (**F-N3**) — backend-conditional. |
| **Delayed convergence** | **BOUNDED** | View convergence is heartbeat-cadenced (`observed_gc_round` advances only after a `RetireView.refresh`); a slow beat delays convergence but never corrupts (drain under `view_gate`). |

---

## 19. Consensus failures

CAS uses **no quorum consensus** — it externalizes linearizable CAS to S3 conditional PUT and uses
leases for leadership. The taxonomy still maps:

| Failure | Verdict | Rationale |
|---|---|---|
| **Leader split / multiple leaders** | **Writer: REACHABLE (J1/J2/J3)** / **GC: SAFE** | Writer "leadership" = mount lease, split under J1–J3. **GC leadership** tolerates multiple leaders safely: attempt-scoped generations isolate their writes, exact-token `deleteExact` + the single `gc/state` CAS mean only one leader's round commits; a zombie leader is rejected. |
| **Lost commit** | **SAFE** | A committed shard CAS is durable; GC round commit is a single CAS (all-or-nothing). |
| **Double commit** | **SAFE / BOUNDED (J5)** | GC round is idempotent (attempt-scoped, exact-token). Writer J5 lost-ACK replay is a "double effect" on the journal (duplicate element), semantically idempotent. |
| **Forgotten commit** | **SAFE** | Post-CAS cleanup is derived from the committed `gc/state`; a crash after CAS re-derives on the next round (no forgotten state). |
| **Log divergence** | **REACHABLE (J1/J2)** | = forked journal history (§9). Bounded by CAS re-convergence. |

---

## 20. Consolidated findings (ranked)

| # | Anomaly class (Jepsen term) | CAS finding | Sev |
|---|---|---|---|
| 1 | **Split brain / linearizability violation / zombie value / forked history** | **J1** — shard `casPut` fenced by content token, not `writer_epoch`; pause/TOCTOU zombie write | **Med-High** |
| 2 | **Missing read / data loss** | **X1/R1** — ref-less reader's unpinned deferred blob GET vs GC delete → `NoSuchKey` | **Med-High** |
| 3 | **Split brain (identity)** | **J2** — VM clone/snapshot shares `server_uuid`; dual mount bounded by renew period | **Med** |
| 4 | **Split brain (clock)** | **J3** — wall-clock lease expiry vs boot-clock local fence → premature reclaim | **Med** |
| 5 | **Recovery failure / indefinite unavailability** | **G-N1** — persistent shard clamp halts reclamation pool-wide | **Med-High (liveness)** |
| 6 | **Overwritten write / failed removal (leak)** | **W1** — promote-overwrite orphans the old manifest | **Med (leak)** |
| 7 | **Indefinite block / timeout** | **F-N1** — coalesced shard read has no deadline (reader convoy) | **Med (liveness)** |
| 8 | **Request dropped (false negative)** | **W-N1** — presence-asserting closure misreports lost-ACK-succeeded write | **Med** |
| 9 | **Duplicate element / double effect** | **J5 / W-N2** — lost-ACK journal double-append (set-idempotent → bloat only) | **Low** |
| 10 | **Stale read / stale replica** | **F-N3** — force-fresh not fresh on eventually-consistent backend | **Low (backend-conditional)** |
| 11 | **Orphaned transaction** | **W-N4** — orphan multipart/manifests on interrupt | **Low (leak)** |
| 12 | **Fractured read / partial transaction / read skew** | RENAME (`republishRef`) cross-shard non-atomicity | **BY-DESIGN** |

## Headline

Judged against the **correct bar** — *per-object linearizable store + background collector*, not a
multi-object serializable DB — CAS is remarkably clean: the entire Adya G0/G1/G2 family, snapshot-isolation
family, torn/partial writes, data corruption, dirty/future reads, and counter regressions are **IMMUNE or
SAFE**. Cross-shard non-serializability (read skew, fractured read, phantoms) is **BY-DESIGN**.

Genuine reachable findings cluster in exactly two places:

1. **Fencing (J1/J2/J3 → split-brain / zombie-value / non-linearizable / forked-history / log-divergence):**
 the writer uses a lease for mutual exclusion but the shard `casPut` enforces only a **content token**,
 not the monotone `writer_epoch`. Every split-brain-class anomaly in the taxonomy traces to this single
 gap. **Fix:** carry `writer_epoch` into the shard-CAS precondition (reject-if-stale) — the exact pattern
 GC already uses on its `deleteExact` / `gc/state` CAS, which is why the GC leader is split-brain-**safe**.

2. **Reader participation (X1/R1 → missing-read / data-loss):** the reader registers no reachability edge and
 holds no GC-honored token across its **deferred, unpinned** blob GET, so a drop+GC delete can remove a
 committed datum mid-query for ref-less/cross-node readers. **Fix:** an ephemeral reader pin folded into
 the GC mark/ack-floor union, or bound query lifetime below the condemn→delete latency.

Everything else degrades to **leaks** (over-count, W1/W-N4), **liveness cliffs** (G-N1/F-N1), or
**benign duplicate effects** (J5/W-N2) — never silent committed-data loss on the write/GC plane.

## cas-mergetree-part-support-audit.md

Language: Markdown

# CAS — MergeTree Part-Type Support Map (what works / what's broken)

Scope: enumerate every kind of MergeTree part / part-storage feature, then map each to how the
content-addressed (CAS) metadata backend handles it and where it breaks. Grounded in
`MergeTreeDataPartType.h`, `MergeTreeData::choosePartFormat` / `checkAlterPartitionIsPossible` /
`checkContentAddressedDiskRestrictions`, `DataPartStorageOnDiskBase`, `DataPartsExchange.cpp`
(fetch-by-relink), `StorageReplicatedMergeTree.cpp`, and the CAS `PartPathParser` / transaction.

CAS's core model: **a part directory = one atomic unit** → one manifest tree → one ref. Every file in
the part is a manifest **entry** (inline for tiny files, blob for the rest); the three mutable per-part
files (`uuid.txt`, `txn_version.txt`, `metadata_version.txt`) are stored **per-ref** (excluded from
content identity so byte-identical parts still dedup). CAS is **path-shape driven**: `parsePartFilePath`
splits ` / /<file...>`, anchoring on the Atomic `<uuid[:3]>/ ` pair, else falling back
to `looksLikePartDir` (last 3 underscore groups numeric = `_min_max_level`).

---

## 1. The MergeTree part taxonomy (three orthogonal dimensions)

### Dimension A — data layout (`MergeTreeDataPartType`)
| Type | Layout | Notes |
|---|---|---|
| **Wide** | one file (+marks) **per column** | many manifest entries per part |
| **Compact** | all columns in one `data.bin` + `data.mrk3` | few entries |
| ~~InMemory~~ | — | **removed** from ClickHouse (enum is only Wide/Compact/Unknown) |

### Dimension B — storage container (`MergeTreeDataPartStorageType`)
| Type | Container | Notes |
|---|---|---|
| **Full** | a directory of individual files | what CAS models |
| **Packed** | all part files in **one** file + offset table | `DataPartStorageOnDiskPacked` |

### Dimension C — functional part categories
Regular · Merged · Mutation-result · **Projection** (nested `.proj/`) · **Patch** (lightweight
UPDATE) · Lightweight-delete artifacts (`_row_exists`) · Detached · Temporary (`tmp_*`) · **Frozen /
shadow** (FREEZE) · Broken · Empty.

---

## 2. Support map

| Part / feature | CAS status | Mechanism / where |
|---|---|---|
| **Wide part** | ✅ Supported | each column file → manifest entry (blob/inline) |
| **Compact part** | ✅ Supported | `data.bin`/`data.mrk3` → blob entries |
| **Full storage type** | ✅ Supported | the only type CAS models; `choosePartFormat` **always returns Full** |
| **Packed storage type** | ⚠️ **Not produced; untested on read/restore** | write path never emits Packed; a Packed part arriving via RESTORE/ATTACH from another disk is out of the tested envelope |
| **Projection part** | ✅ Supported | nested keys `.proj/ ` in the parent manifest; temp `.tmp_proj` rides the **parent whole-part transaction** (B58), re-keyed on rename |
| **Patch part** (lightweight UPDATE) | ✅ Supported | partition id `patch- - `; name still ends `_min_max_level` → recognized by parser; routes as a normal part |
| **Lightweight delete** | ✅ Supported | implemented as a mutation → new part with `_row_exists` (more entries) |
| **Merge / mutation result** | ✅ Supported | new whole-part ref; unchanged columns carried by hardlink=**copy-by-reference** (dedup → free) |
| **Detached part** | ✅ Supported | `detached/ ` refs inside the table's own namespace (kDetachedRefPrefix) |
| **Temporary part** (`tmp_insert_`, `tmp_merge_`, `delete_tmp_`) | ✅ Supported | suffix survives prefixes; Atomic anchor ignores prefix |
| **Frozen / shadow (FREEZE/UNFREEZE)** | ✅ Supported | each part published as a ref in the `shadow/` namespace sharing live blobs **zero-copy** (no byte copy); UNFREEZE drops those refs |
| **ReplicatedMergeTree** | ✅ Supported | B33 lifted; **fetch-by-relink** (same-pool fetch sends only `part_id`+mutable header, receiver publishes its own ref) — the CA analogue of zero-copy |
| **Zero-copy replication** | 🚫 **Disabled by design** | `supportZeroCopyReplication()==false`; `lock/unlockSharedData` are safe no-ops; replaced by content addressing + fetch-by-relink |
| **BACKUP (Atomic DB)** | ✅ Supported | pointer-holding path (`getStorageObjects`, `make_temporary_hard_links=false`) |
| **BACKUP (Ordinary / non-UUID DB)** | 🚫 **Rejected** | temporary-hard-link path → `SUPPORT_IS_DISABLED` (B16/B34) — "use an Atomic database instead" |
| **ALTER … PARTITION** (allow-listed) | ✅ Supported | DROP, DROP_DETACHED, FORGET, ATTACH, REPLACE, MOVE(same-disk→table), FETCH, FREEZE, FREEZE_ALL, UNFREEZE, UNFREEZE_ALL — via one whole-part CA transaction |
| **ALTER … PARTITION** (anything else) | 🚫 **Fail-closed** | throws `SUPPORT_IS_DISABLED` ("clones file-by-file with no transaction, would corrupt the clone") |
| **MOVE PARTITION … TO DISK/VOLUME** (cross-disk) | ⚠️ **Unverified** | byte-copy `clonePart` path; only same-disk `MOVE … TO TABLE` is verified — cross-disk is a stated "follow-up to verify" |
| **FETCH … TO DETACHED** | ⚠️ Works, sub-optimal | takes the byte-fetch path into `detached/` (relink-into-detached **deferred**, backlog) |

---

## 3. What's actually broken / limited (ranked)

### B-1 — BACKUP on Ordinary (non-UUID) databases: **rejected** (Med)
`DataPartStorageOnDiskBase` fails closed (`SUPPORT_IS_DISABLED`, B16/B34) when BACKUP uses the
**temporary-hard-link** path, which Ordinary/non-UUID databases use. The per-file `createHardLink`
autocommit with no enclosing transaction would publish a one-file ref per file (the B21 corruption
mode). **Atomic databases back up fine** (pointer-holding). *Impact:* native `BACKUP TABLE` is
Atomic-only on CAS; workaround is FREEZE (shadow refs) or an Atomic DB.

### B-2 — Cross-disk `MOVE PARTITION TO DISK/VOLUME`: **unverified** (Med)
The ALTER allow-list admits `MOVE_PARTITION`, but the check can't distinguish `MOVE … TO TABLE`
(same-disk, verified) from `MOVE … TO DISK/VOLUME` (cross-disk byte-copy `clonePart`). The comment
explicitly marks cross-disk as "a follow-up to verify." *Impact:* moving CAS parts to/from another disk
tier is not validated — potential correctness/format gap on tiered storage.

### B-3 — Packed storage-type parts: **outside the tested envelope** (Low–Med)
`choosePartFormat` **always returns `Full`**, so the CAS write path never creates Packed parts and
CAS's per-file manifest model is always exercised. But a **Packed** part can arrive via `RESTORE` /
`ATTACH` of data written on another disk. CAS has no code path modeling a single-file packed container,
so this is untested/unsupported. *Impact:* restoring/attaching packed parts from a non-CAS disk is not
covered.

### B-4 — Non-Atomic (Ordinary) layout depends on the `looksLikePartDir` heuristic (Low)
On Ordinary databases there is no ` ` anchor, so a part directory is recognized **only** by the
grammar "last 3 underscore groups are decimal" (`looksLikePartDir`). This holds for regular, patch
(`patch- - _min_max_level`), and temp parts. But it is a **grammar guess**, not a semantic
signal — any future part-naming scheme whose tail isn't `_ _ _ ` would be misclassified as a
verbatim table file (the B40 data-loss shape). Atomic databases (the norm) are immune (uuid anchor).
*Impact:* couples CAS correctness on Ordinary DBs to MergeTree part-naming grammar.

### B-5 — FETCH-to-detached relink deferred (Low)
A `to_detached` fetch content-addresses the downloaded bytes into the `detached/` namespace instead of
relinking to blobs already in the shared pool — correct but loses the dedup/zero-byte benefit for that
path. Backlog item.

### B-6 — Surgical single-file deletion on a committed part is a no-op (Latent, from C-U4)
`unlinkFile` on a committed **content** file is a deliberate no-op (the part directory is the removal
unit via `removeDirectory`). Not reachable today because CLEAR COLUMN / CLEAR INDEX / DROP PROJECTION
IN PARTITION all route through **mutations → new parts**, never in-place file deletion. Becomes a
correctness bug only if some future code path surgically deletes one committed file and relies on it
being gone. *Watch item.*

---

## 4. Non-issues (explicitly fine)
- **Wide vs Compact** — both are just "N files → N entries"; CAS is layout-agnostic.
- **Projections** — first-class (nested manifest keys + parent-transaction B58 handling verified across
 merge/mutate/write paths).
- **Patch parts / lightweight deletes** — ordinary parts to CAS; nothing special needed.
- **Immutability-dependent adaptations** — hardlink→copy-by-reference and part-dir-as-removal-unit are
 sound because MergeTree parts are immutable.
- **Zero-copy** — not "missing"; deliberately replaced by content addressing + fetch-by-relink.

---

## 5. Summary

| # | Item | Status | Severity |
|---|---|---|---|
| B-1 | BACKUP on Ordinary/non-UUID DB | Rejected (Atomic OK) | Med |
| B-2 | Cross-disk MOVE PARTITION TO DISK/VOLUME | Unverified | Med |
| B-3 | Packed storage-type parts (restore/attach) | Untested/unsupported | Low–Med |
| B-4 | Ordinary-layout part recognition via grammar heuristic | Fragile coupling | Low |
| B-5 | FETCH-to-detached relink | Deferred (works, sub-optimal) | Low |
| B-6 | Surgical single committed-file unlink | Latent no-op (not reachable today) | Low |

**Headline.** The CAS backend already supports the **full mainstream MergeTree part surface**: **Wide**
and **Compact** parts (always **Full** storage — `choosePartFormat` never emits Packed), **projections**
(nested manifest keys with parent-transaction handling), **patch parts** and **lightweight deletes**
(they're just ordinary parts/mutations to CAS), detached/temporary/frozen parts, **ReplicatedMergeTree**
(via fetch-by-relink, the content-addressed replacement for zero-copy), and the allow-listed ALTER
PARTITION operations, all funneled through the single **whole-part transaction** that makes a part one
atomic ref. The remaining gaps are at the edges, not the core: **BACKUP is Atomic-DB-only** (B-1, the
sharpest user-visible limit), **cross-disk MOVE PARTITION is unverified** (B-2), **Packed parts arriving
via restore/attach are outside the tested envelope** (B-3), and two structural couplings worth watching
— the Ordinary-layout part-name grammar heuristic (B-4) and the committed single-file-unlink no-op
(B-6). Zero-copy is intentionally disabled, not broken. Net: nothing in the *normal insert → merge →
mutate → replicate → freeze* lifecycle is broken; the actionable items are BACKUP-on-Ordinary and
cross-disk MOVE.

## cas-performance-audit.md

Language: Markdown

# CAS — Performance / S3 Request-Cost & Scalability Audit

Scope: S3 request-count and latency cost of each operation, hot spots, and scalability limits (as the
pool grows in tables, parts, shards, blobs, and servers). **Caveat:** a rigorous verdict needs runtime
measurement (request counters, latency histograms, `ProfileEvents`) under representative workloads —
this audit is a **static request-cost model + scalability reasoning**, and flags where measurement is
required. S3 pricing is dominated by **request count** (GET/PUT/LIST/HEAD are per-request billed) and
per-request latency (tens of ms), so request *count per logical op* is the primary metric.

---

## 1. Per-operation S3 request cost

### Read (cold): `resolveRef → readManifest → lookupPath → ranged GET blob`
| Step | S3 ops (cold) | S3 ops (warm) |
|---|---|---|
| resolve ref (read shard) | 1 HEAD + 1 GET shard | 0 (shard decode cache, TTL + token-validate) |
| read manifest | 1 GET part-manifest | 0 (`(ManifestId,Token)` manifest decode cache) |
| read blob payload | 1 ranged GET | 1 ranged GET (payload not cached at this layer) |
| **total** | **~3–4 requests** | **~1 request** |

- **Inline entries** (small files ≤ `blob_header_len` region) are served from the manifest bytes → the
 blob GET is **elided**. Big win for the many tiny MergeTree metadata files (`columns.txt`,
 `checksums.txt`, `count.txt`, primary index tails).
- The two decode caches make **warm reads ~1 request** (the blob GET), which is the theoretical floor.
- **P1 (Med):** the reader issues the deferred blob GET with **no pin** (R1/X1) — orthogonal to cost,
 but the lack of a pin also means no read-side blob cache coordination with GC. Repeated cold reads of
 the same blob re-GET each time unless a higher cache layer (page cache / disk cache) intercepts.

### Write: `build → precommit(CAS shard) → PUT blobs → promote(CAS shard)`
| Step | S3 ops |
|---|---|
| stage manifest | 1 PUT (part manifest) |
| precommit | 1 CAS (conditional PUT) on the shard — **batched** by flat-combining |
| upload N blobs | N PUTs (dedup: already-present blobs skipped after a HEAD/observe) |
| promote | 1 CAS on the shard — **batched** |
| **total** | **~2 CAS + (1 + N_new_blobs) PUTs** per part |

- **Flat-combining (`mutateShard`)** coalesces concurrent mutations to the same `(namespace, shard)`
 into **one** shard CAS — turning a thundering herd of part commits into one read-modify-write. This is
 the key write-scalability lever.
- **Dedup** means a re-inserted/identical blob costs a HEAD-class observe, not a PUT — content
 addressing pays off for repeated data.
- **P2 (Med, scalability):** shard CAS is a **read-modify-write on a single object**. Under high write
 concurrency to the **same shard**, throughput is bounded by CAS retry rounds (contention →
 conflict → re-read → retry). `root_shards` is the **pool-wide** parallelism knob (see §2).

### GC round: `discover(LIST) → fold(read shards) → deleteExact(condemned) → gc/state CAS`
| Step | S3 ops |
|---|---|
| discovery | LIST `cas/refs/` — **O(namespaces × shards)** keys paged |
| fold | GET each shard (or cached) + GET touched manifests |
| deletes | 1 `deleteExact` per graduated blob |
| outcome/retired/seal | a few PUTs per generation |
| gc/state | 1 CAS |
| heartbeat | periodic beat PUT/CAS on the mount lease |
| **total** | **O(shards) LISTs/GETs + O(condemned) DELETEs** per round |

---

## 2. Scalability limits

| Dimension | Cost driver | Limit / concern |
|---|---|---|
| **Write parallelism** | `root_shards` (pool-wide constant) | All tables share the same shard count. A **hot table** contends on its `shard = CityHash64(ref)%root_shards` slots; more tables → more aggregate write pressure on a **fixed** shard set. `root_shards` is fixed **at pool creation** and pool-authoritative (can't reshard live). **P3 (Med):** choosing `root_shards` is a one-shot capacity decision for the whole pool. |
| **GC discovery** | LIST over `cas/refs/` | Grows **O(namespaces × shards)**. On a pool with many tables, each GC round pages a large LIST → LIST request cost and round latency grow with the pool. **P4 (Med):** GC round cost scales with total pool size, not with churn — a mostly-idle huge pool still pays full-scan LIST per round. |
| **GC deletes** | condemned blob count | Proportional to actual garbage — scales with churn (good). |
| **Blob count** | flat blob keyspace | S3 handles arbitrary key counts; prefix hot-spotting is mitigated by content-hash-prefixed keys (naturally spread). ✔ |
| **Fan-in per shard** | flat-combining | Coalescing caps per-shard CAS rate; a single extremely hot shard is still one-object-serialized. |
| **Metadata files** | inline placement | tiny files inlined into the manifest → **no per-file blob** → huge request-count reduction for MergeTree's many small files. ✔ strong |

---

## 3. Cost anti-patterns to watch (need measurement)

1. **Warm-cache hit ratio (P1).** The shard/manifest decode caches determine whether reads cost ~1 or
 ~4 requests. Under a cache-hostile workload (huge working set, short TTL, high churn invalidating
 tokens) reads degrade toward cold cost. **Measure** cache hit ratio and shard-decode TTL churn.
2. **Shard CAS conflict rate (P2).** Measure CAS retry counts per shard under concurrent commits; a
 high retry rate signals `root_shards` is too small or a table is skewed onto few shards.
3. **GC round LIST cost (P4).** Measure LIST request count + round wall-time as a function of
 namespace count. A large idle pool may spend most of GC on discovery.
4. **Deferred blob GET amplification (P1).** Without a read-side blob cache, repeated scans of the same
 cold parts re-GET blobs; verify the page/disk cache above CAS absorbs this.
5. **Heartbeat/lease traffic.** Each mounted server beats its lease periodically — O(servers) steady
 background PUT/CAS traffic independent of workload. Bound-check the beat interval vs request budget.

---

## 4. Summary

| # | Finding | Severity | Kind |
|---|---|---|---|
| P3 | `root_shards` is a fixed pool-wide, create-time constant — one-shot write-parallelism decision, no live reshard | Med | Scalability |
| P4 | GC discovery LIST is O(namespaces×shards) — round cost scales with pool size, not churn | Med | Scalability |
| P2 | Same-shard write concurrency bounded by single-object CAS retries (mitigated by flat-combining) | Med | Throughput |
| P1 | Reads have no read-side blob cache/pin — cold reads re-GET; hit ratio depends on decode caches | Med | Latency/cost |

**Headline (with measurement caveat).** The design has the **right cost levers**: warm reads collapse
to ~1 S3 request via two decode caches, tiny MergeTree files are **inlined** (eliminating per-file blob
GETs — a large request-count win), writes are **coalesced** by flat-combining into one shard CAS, and
content addressing turns re-inserted data into HEAD-class dedup instead of PUTs. The scalability
ceilings are structural rather than bugs: **`root_shards` is a fixed pool-wide constant** (P3 — one
shard set shared by all tables, no live reshard), and **GC discovery scales with total pool size**
(P4 — LIST over all namespaces×shards every round, regardless of churn). Same-shard write concurrency is
ultimately single-object-CAS-bound (P2), and reads lack a blob-level cache/pin (P1). None of these are
correctness issues; they are capacity-planning constraints. **A rigorous verdict requires runtime
measurement** — instrument S3 request counters/latency (`ProfileEvents`, per-op request histograms),
decode-cache hit ratios, shard-CAS retry rates, and GC LIST cost vs namespace count — before making
`root_shards` sizing guidance or GC-cadence recommendations.

## cas-read-protocol-audit.md

Language: Markdown

# CAS — Read Protocol Audit (state-space + logical fault injection)

Scope: the CAS read path — `resolveRef → readManifest → lookupPath/listDirectory → locate/
getBlobViewPlan → readBlobPayload (ranged S3 GET) → ReadBufferFromFileView`, plus the decode caches
(shard TTL + token-validate; `(ManifestId, Token)` manifest cache), the single-flight coalescing, and
the in-flight read-your-writes overlay (B59). Method: transition table + reachable-interleaving walk
(reader vs concurrent writer / GC / re-incarnation), then logical fault injection.

Read-safety invariants:
- **INV_NO_DANGLE (read)** — a committed ref naming a missing body/blob fails **closed**
 (`FILE_DOESNT_EXIST` / `CORRUPTED_DATA`), never returns empty or wrong bytes.
- **INV_FRESH** — a force-fresh (`allow_stale=false`) read reflects the latest committed write
 (modulo backend consistency).
- **INV_RYOW** — a reader sees its own Store's prior committed writes.

---

## 1. State model

Read pipeline stages and their pinned state:
- **resolveRef(ns, name, allow_stale)** — TTL fast-path (allow_stale) or HEAD-validated decode →
 `manifest_ref`. Two-arg calls default `allow_stale=false` (force-fresh).
- **readManifest(id)** — HEAD (token validate) + GET on miss → decoded `PartManifest`; INV-NO-DANGLE
 checks (`refMatchesBody`, `manifestNamespaceMatches`).
- **lookupPath / listDirectory** — locate the `ManifestEntry` (inline / mutable / blob-backed).
- **locate / getBlobViewPlan** — map entry → `BlobLocation{key, offset, length}`.
- **readBlobPayload** — ranged S3 GET wrapped in `ReadBufferFromFileView` (sub-range of a shared blob).

**Critical structural fact:** after `locate`, the pipeline holds only a `StoredObject(blob_key,…)`.
The manifest is discarded and the reader holds **no pin** on the ref/manifest/blob. The actual blob
GET is **deferred** to query execution (T_get ≫ T_plan).

---

## 2. Reachable-interleaving findings

### R1 — Reader holds no pin across the deferred blob GET *(Med-High)*

The reader resolves ref→manifest→location at plan time, then does the blob GET later, registering **no
reachability edge** and holding **no GC-honored token**. If the ref is dropped and a GC round completes
condemn → `delete_pending` → `deleteExact(blob)` before the deferred GET, the reader hits **`NoSuchKey`
mid-query.** Same-node readers are incidentally fenced by MergeTree DataPart liveness
(`old_parts_lifetime`); **ref-less / cross-node readers are unprotected.** Two-phase graduation + ack
floor only *bound* the window. This is the sharpest read-side interleaving hole (re-confirmed in the
cross-protocol audit as the sole reader-visible dangle). **Fix:** an ephemeral reader pin folded into
GC's mark/ack-floor union, or bound query lifetime below the condemn→delete latency.

### R2 — Manifest decode cache keyed by `(ManifestId, Token)` — correct but non-sharing *(Info/Low)*

Each publish has a unique `ManifestId`, so the manifest cache never shares across ids; a re-incarnation
under the same id fails closed via the Token component. Correct (no stale/cross-id serve), but the lack
of content-sharing means repeated reads of *equivalent* manifests re-decode — intentional per spec, a
memory/CPU trade, not a correctness issue.

### R3 — TTL freshness coupling is unenforced *(Low)*

The `allow_stale` decode TTL (~200 ms) is decoupled from the GC condemn→delete latency; correctness
relies on TTL ≪ that latency. True today, but the coupling is a convention, not an invariant — a
future TTL increase or a faster GC cadence could let a stale resolve outlive its target.

### R4 — No coalescing / negative-caching on manifest reads *(Low)*

`readManifest` HEAD+GET is not coalesced (unlike shard reads) and absence is not negatively cached, so
concurrent reads of the same part manifest under throttling can produce a HEAD+GET storm.

---

## 3. Logical fault injection (S3 interrupts, delays, lost ACKs, disk, memory)

### F-N1 — Coalesced shard read has no deadline (reader convoy) *(Med, liveness)*

`coalescedReadShardDecoded` single-flights concurrent readers of the same shard onto one leader GET.
The leader's GET has **no deadline**; if it hangs (S3 stall), **all coalesced followers block
indefinitely** on the shared future. Correctness-safe, liveness cliff. **Fix:** bound the leader read;
on timeout, fail the followers (retryable) rather than wedge them.

### F-N2 — Network delay widens the unpinned read window *(Med, interaction)*

A slow deferred blob GET (F-N2) directly widens R1's exposure: transient S3 slowness increases the odds
that a drop+GC delete completes before the GET lands, converting a transient fault into a **permanent
404** for a ref-less reader. Amplifier for R1.

### F-N3 — Force-fresh read isn't fresh on eventually-consistent backends *(Low, backend-conditional)*

`allow_stale=false` HEAD-then-GET assumes read-after-write. On an eventually-consistent object store
(some S3-compatible backends), the GET can still fetch a stale version after a HEAD saw the new token →
a decode/token mismatch (caught, retried) or a stale serve on non-strict backends. Backend-conditional.

### F-N4 — HEAD+GET storm under throttling *(Low, robustness)* — see R4.

---

## 4. Verified SAFE

- **Transient network errors are not misclassified as "absent."** `isObjectNotFound`/`isNotFoundError`
 classify only true 404s as absent; 5xx/timeouts propagate as retryable errors — a network blip never
 looks like a deleted object (so it never fabricates an INV-NO-DANGLE violation).
- **Truncated / corrupted reads fail closed.** Manifest/shard decode validates magic + version + CRC +
 framing (`decodePartManifest`, `decodeRootShard`) → `CORRUPTED_DATA`; a short/garbled body never
 yields partial rows.
- **INV-NO-DANGLE surfaced as an error.** A committed ref whose manifest body is missing throws
 `FILE_DOESNT_EXIST`; a body whose `ref`/`root_namespace_id` mismatches the id throws `CORRUPTED_DATA`
 — never empty data.
- **Idempotent GET/HEAD.** Reads are side-effect-free and content-addressed; retries are always safe.
- **RYOW same-Store.** A committed write bumps `shard_write_seq` + erases the decode cache under the
 same lock (B157), so a same-Store reader never serves a pre-write decode via the TTL fast-path.
- **Immutable cached payloads.** Decode caches hold `const shared_ptr ` — safely shared across
 reader threads, never mutated.

---

## 5. Summary

| # | Finding | Severity | Class |
|---|---|---|---|
| R1 | Reader holds no pin across the deferred blob GET → dangle to ref-less reader | **Med-High** | Data loss (reader) |
| F-N1 | Coalesced shard read has no deadline (reader convoy) | Med | Liveness |
| F-N2 | Network delay widens R1's unpinned window (transient → permanent 404) | Med | Interaction |
| R3 | TTL↔condemn-latency coupling unenforced | Low | Latent |
| F-N3 | Force-fresh not fresh on eventually-consistent backends | Low | Backend-conditional |
| R4 / F-N4 | No coalescing/negative-caching on manifest reads (HEAD+GET storm) | Low | Robustness |
| R2 | Manifest cache non-sharing (by design) | Info | Trade-off |

**Headline.** The read path fails **closed** on every corruption/absence/transient-fault axis — no
stale-as-absent misclassification, no partial rows, RYOW preserved. The one real correctness hole is
**R1**: the reader participates in none of the write/GC safety mechanisms (no edge, no token) across its
**deferred, unpinned** blob GET, so a drop + full GC round can delete a committed blob out from under a
ref-less/cross-node reader — amplified by network delay (F-N2). The rest are **liveness** (F-N1) or
**robustness** issues that degrade gracefully. Fixing R1 (a reader pin) closes the only reader-visible
data-loss path.

## cas-security-audit.md

Language: Markdown

# CAS — Exhaustive Security Audit

Feature under review: `cas-gc-rebuild` (branch) and the CAS `metadata_type = content_addressed`
MergeTree backend it lives in. Method: threat-model the trust boundaries, run STRIDE across every
interface, and enumerate findings grounded in code. Because the rebuild command operates *inside* the
CAS pool, the audit covers the whole pool attack surface and then dedicates §7 to the rebuild feature.

Severity scale: **Critical / High / Med / Low / Info**. Each finding states the **trust assumption**
it depends on — most CAS "vulnerabilities" are only reachable *if* the pool spans trust domains.

---

## 1. Trust model (the framing that determines every severity)

CAS's security posture rests on **one boundary: the S3 bucket credentials.**

- Every server that mounts the pool shares the **same bucket credentials** and can read/write **any**
 key: `blobs/*`, `cas/refs/*`, `cas/manifests/*`, `gc/*`, `_pool_meta`, `gc/server-roots/*/{owner,epoch,mount}`.
- There is **no intra-pool authentication or authorization.** Objects are not signed; identities
 (`server_uuid`, `writer_epoch`, `server_id`, provenance) are **self-asserted** in object bodies.
- **Blobs are shared pool-wide by content hash.** `blobKey(id) = /blobs/<2char>/ ` —
 there is **no namespace in the blob key**. Two different tables/namespaces/databases that write
 identical content **dedup to the same physical blob**. Namespacing (`server_root_id/ `) applies
 only to *refs/manifests*, not to *content*.
- Confidentiality (encryption at rest / in transit) is **delegated to S3** (SSE + TLS + bucket policy);
 CAS stores table bytes in plaintext blobs.

**Consequence — blast radius:** a single compromised mounting server, or anyone with the bucket
write credential, has **total control** of the pool: forge mounts, tamper `gc/state`, poison blobs,
delete anything. cas-gc-rebuild is a *recovery* tool for accidental `gc/state` loss — it is **not** a
defense against an active in-pool adversary, and should not be marketed as one.

**Realistic adversaries (in decreasing privilege):**
1. **Bucket-credential holder / compromised peer server** — game over by design (SEC-3).
2. **SQL user** with INSERT/SELECT/DDL on a CAS-backed table (RBAC-limited). The *interesting*
 adversary — can they cross a namespace/tenant boundary within one pool? (SEC-1, SEC-2).
3. **Operator** invoking `SYSTEM CONTENT ADDRESSED GC REBUILD` (SYSTEM-privileged). (§7).
4. **Network attacker** (MITM, NTP) — TLS covers transit; NTP feeds J3. (SEC-7).

---

## 2. Trust boundaries

```
 SQL user ──INSERT/SELECT/DDL──▶ ClickHouse (RBAC) ──▶ CAS Store ──▶ S3 bucket
                                                          ▲              ▲
                              peer servers (shared creds) ┘              │
                                        operator ──SYSTEM ... GC REBUILD─┘
```

- **SQL ↔ CAS:** RBAC gates *which tables* a user reads/writes. But content written to a CAS table
 becomes a **pool-global blob**. The RBAC boundary does **not** extend to the content plane.
- **CAS ↔ S3:** no per-object auth; the credential is the boundary.
- **peer ↔ peer:** mutual trust assumed; enforced only by conventions (mount lease, epoch) that a
 malicious peer can forge.

---

## 3. STRIDE summary

| Threat | Vector | Verdict | Ref |
|---|---|---|---|
| **Spoofing** | Forge mount lease / owner anchor / self-asserted `server_id`/provenance | **Reachable if pool-write** (no signing) | SEC-3 |
| **Tampering (content)** | CityHash128 collision → poison a shared blob via dedup | **High if untrusted writers + shared pool** | SEC-1 |
| **Tampering (control)** | Overwrite `gc/state`, `_pool_meta`, shards | **Reachable if pool-write** | SEC-3 |
| **Repudiation** | Actions attributable? | Provenance + CasEvent log exist but **self-asserted** (forgeable by pool-write) | SEC-8 |
| **Information disclosure** | Dedup existence oracle across tenants; plaintext blobs | **Med** (side-channel) / delegated (encryption) | SEC-2 |
| **Denial of Service** | Crafted oversized/valid-CRC object → OOM; clamp-wedge; rebuild amplification | **Med** | SEC-4, SEC-6 |
| **Elevation of privilege** | SQL user crossing namespace via content plane; key injection | **Content-plane crossing real (SEC-1/2); path injection defended** | SEC-1, SEC-5 |

---

## 4. Findings

### SEC-1 — Non-cryptographic content hash (CityHash128) enables collision-based blob poisoning across a shared pool *(High — trust-dependent)*

**Fact.** Content keys are `poolContentHash(payload)` = **CityHash128** (streamed via `HashingReadBuffer`;
confirmed by the code comment "a one-shot `CityHash128` diverges…"). The envelope header carries
`hash_algo = 1`. **Normal reads never re-hash the payload** — "the core otherwise NEVER re-hashes
payloads; copy-forward is the one sanctioned re-verification." Dedup is HEAD-first: if `blobKey(H)`
exists, the body PUT is skipped (`CasBlobBodyPutAvoided`).

**Attack.** CityHash is **not collision-resistant**. An adversary who can (a) get bytes stored in the
pool and (b) produce a CityHash128 collision can poison content:
- *Pre-seed poisoning:* attacker stores `B_evil` under key `H = CityHash128(B_benign) = CityHash128(B_evil)`.
 Later a victim writes `B_benign` → HEAD-first sees `H` present → **skips the upload** → the victim's
 part now resolves `H` to `B_evil`. On read the victim gets attacker bytes. **All CRC checks pass**
 (CRC is over the poisoned bytes; the key matches by collision), and reads never re-hash → **silent
 integrity break**.
- Because blobs are **pool-global** (no namespace in `blobKey`), the victim can be a **different table /
 database / tenant** sharing the pool. This turns a low-privilege INSERT into cross-namespace data
 corruption of tables the attacker cannot even read.

**Trust dependency.** Only reachable if untrusted parties can influence stored bytes **and** the pool
is shared across trust domains. In a single-operator, single-trust-domain deployment (the likely design
assumption) it is latent. It becomes real for: multi-tenant pools, pools shared across DBs with
differing RBAC, or any path where user-controlled bytes reach a CAS blob shared with higher-trust data.

**Mitigations present.** `domain_id = pool_id` in the header prevents *cross-pool* confusion;
`hash_algo` allows a future upgrade; copy-forward re-verifies. **Gap:** the steady-state read path
trusts key=content without verification, and the hash is not collision-resistant.

**Recommendation.** Offer a **cryptographic content-hash mode** (BLAKE3/SHA-256 truncated to the key
width, selected via `hash_algo`) for pools that span trust domains; and/or **namespace-scope the blob
key** (or bind blobs to a tenant) so cross-domain dedup cannot poison. At minimum, document the
single-trust-domain assumption explicitly.

### SEC-2 — Dedup existence side-channel (cross-tenant confirmation oracle) *(Med — privacy)*

HEAD-first dedup makes a body PUT **observably cheaper** when the content already exists
(`CasBlobBodyPutAvoided`, timing, request-count, billing). An attacker who can insert candidate content
can therefore **test whether specific content already exists in the pool** — a classic content-addressed
confirmation attack (e.g., "does any table in this pool contain this exact document/row?"). Works across
namespaces because dedup is pool-global. **Recommendation:** for multi-tenant pools, disable
cross-tenant dedup or scope dedup per trust domain; treat dedup timing as a documented information leak.

### SEC-3 — No intra-pool authorization; identities are self-asserted *(High — architectural / by-design)*

All mounters share bucket creds; object bodies carry **unsigned, self-asserted** identity
(`server_uuid`, `writer_epoch`, `server_id`, provenance). A pool-write-capable adversary can:
- **Forge a mount lease** (`gc/server-roots/ /mount`) with any uuid/epoch → fence out the real
 writer (`tripMountLost` on its next renew) → **DoS**, or manufacture a **split-brain** window.
- **Rewrite `gc/state`** → induce mass condemn / under-count → **data loss** (only bounded by the
 writer-side commit gate + ack floor, which themselves read pool objects the attacker controls).
- **Poison/delete blobs, shards, `_pool_meta`.**

This is the **fundamental trust model**, not a bug — but it must be stated: **the bucket credential is
the entire security perimeter; least-privilege bucket IAM + per-pool credential isolation are the real
controls.** cas-gc-rebuild cannot recover from adversarial (as opposed to accidental) state loss because
it rebuilds *from the very owner state* the adversary can also tamper.

### SEC-4 — Crafted-object decode / resource-exhaustion DoS *(Med)*

The write path bounds object sizes (`manifest_hard_limit`, `kMaxLargestInlineEntryBytes = 1 MiB`,
backpressure). But a party with pool-write access (SEC-3) — or, more benignly, a corrupt/huge object —
can place a **valid-CRC, valid-framing but enormous** shard/manifest directly in S3. Decoders
(`decodeRootShard`, `decodePartManifest`) validate magic/version/CRC/journal-integrity but a *valid*
giant body still allocates on decode → **OOM in readers and the GC folder** (GC folds whole journals;
mass-drop delta is already a non-streaming memory point, G-N4). **Recommendation:** enforce
**absolute decode-side size/element caps** independent of the write path (defense in depth), and stream
large journals in the fold.

### SEC-5 — Key/path construction: injection **defended**, one latent assumption *(Low)*

Key builders route through `checkNamespace` (rejects empty segments and the reserved `_files` /
`_manifests` / `_precommits`), `namespaceFileKey` and `mountpointObjectKey` reject `..`, leading/trailing
`/`, and `//`. Namespaces are `<server_root_id>/<table_uuid>` — **not** free-form user input from SQL, so
a SQL user cannot inject control-plane prefixes. **Latent assumption:** `checkNamespace` itself does
**not** reject a `..` *segment* — this is safe **only** because the backend is an object store with
**literal (non-normalized) keys** (`srv1/../gc` is a distinct key, not traversal). A filesystem-backed or
path-normalizing backend would traverse. **Recommendation:** reject `..` in `checkNamespace` too, so the
invariant does not silently depend on backend key semantics.

### SEC-6 — Rebuild as a DoS / amplification vector *(Low–Med)* — see §7

### SEC-7 — Fencing gaps (J1/J2/J3) have a security dimension *(Med)*

The write/GC audit's fencing findings are attacker-amplifiable:
- **J3 (clock skew):** the cross-server mount-lease expiry decision uses **wall-clock** `expires_at_ms`.
 An attacker who can skew a victim's clock (**NTP spoofing / MITM on unauthenticated NTP**) can force a
 premature lease reclaim → **induced split-brain** → zombie writes. TLS protects S3 transit but **NTP is
 typically unauthenticated.**
- **J1 (pause):** an attacker who can induce a long STW pause (resource-exhaustion, cgroup throttling)
 widens the unfenced `mayMutate()`→`casPut` window (the shard CAS carries a **content token, not
 `writer_epoch`**), enabling a zombie write.
**Recommendation:** carry `writer_epoch` into the shard-CAS precondition (kills the primitive J1/J2/J3
exploit — the store, not a clock, enforces the fence); require authenticated time (NTS/authenticated NTP)
in the deployment guidance.

### SEC-8 — Repudiation / forensics *(Info)*

Provenance (`server_id`, timestamp, op, `build_id`) and the `CasEvent` sink give a useful audit trail,
but everything is **self-asserted and forgeable** by a pool-write adversary — good for debugging and
honest-fault forensics, **not** an integrity/attribution control against a malicious insider.

### SEC-9 — Confidentiality of blob content *(Info / delegated)*

Blobs are plaintext table bytes; confidentiality relies entirely on **S3 SSE + bucket policy + TLS**.
Content-addressing also means **content equality is externally observable** (same content → same key),
which is inherent to the design (relates to SEC-2). Deployments with confidential data across tenants in
one pool should assume equality-leakage.

---

## 5. What is genuinely well-defended (credit where due)

- **Path traversal** into control-plane prefixes — reserved-segment + `..`/slash rejection (SEC-5).
- **Torn/partial/corrupt objects** — magic + version + CRC + protobuf framing → fail-closed
 `CORRUPTED_DATA`, never a fabricated value (defends decode integrity, though not collisions).
- **Fresh-pool / lost-state confusion** — the baseline guard fails **closed** on trimmed history
 rather than mass-condemning (the core of the rebuild feature, §7).
- **GC destructive ops are exact-token** (`deleteExact` If-Match) + single `gc/state` CAS → a *zombie
 or forged* GC leader cannot delete live data (unlike the writer path, SEC-7).
- **Capability probe + `_pool_meta` authority** — fail-closed on backends lacking conditional writes,
 so the CAS safety primitives can't silently degrade.

---

## 6. Consolidated findings

| # | Finding | Class (STRIDE) | Severity | Trust dependency |
|---|---|---|---|---|
| SEC-1 | CityHash128 content hash → collision poisoning via pool-global dedup; reads never re-verify | Tampering / EoP | **High** | untrusted writers + shared pool |
| SEC-3 | No intra-pool authz; self-asserted identities; bucket cred = whole perimeter | Spoofing/Tampering | **High** | architectural (by-design) |
| SEC-2 | Dedup existence side-channel (cross-tenant confirmation oracle) | Info disclosure | **Med** | multi-tenant pool |
| SEC-4 | Crafted valid-CRC oversized object → OOM on decode/fold | DoS | **Med** | pool-write or corrupt input |
| SEC-7 | Fencing gaps amplifiable via NTP skew (J3) / induced pause (J1) → split-brain zombie write | Spoofing/Tampering | **Med** | clock/pause influence |
| SEC-6 | Rebuild DoS/amplification + FORCE blast radius | DoS | **Low–Med** | SYSTEM privilege |
| SEC-5 | `checkNamespace` doesn't reject `..` (safe only for literal-key backends) | EoP (latent) | **Low** | non-object-store backend |
| SEC-8 | Self-asserted provenance — not an attribution control | Repudiation | **Info** | — |
| SEC-9 | Plaintext blobs; content-equality observable | Info disclosure | **Info** | delegated to S3 |

---

## 7. Feature deep-dive: `SYSTEM CONTENT ADDRESSED GC REBUILD` (cas-gc-rebuild)

**What it is.** `Gc::rebuildBaseline(bool force)` — operator recovery for a lost/corrupt/regressed
`gc/state`. It re-derives the GC baseline (per-shard fold cursors + blob in-degree) from **owner state**
(the ref shards and their journals) using the same primitives as a normal round (`discoverUniverse`,
fold), then installs a fresh `gc/state`.

**Authorization.** It is a `SYSTEM` statement → gated by ClickHouse RBAC `SYSTEM`-level grants. Correct
placement: destructive recovery must be operator-only. *Verify* the grant is a **dedicated**
privilege (not bundled into a broad `SYSTEM` that ordinary power-users hold).

**Safety guards (strong):**
- **Refuse-unless-FORCE:** if `gc/state` and every referenced artifact are **healthy**, rebuild refuses
 (`"a rebuild would discard live bookkeeping; re-run with FORCE"`). Prevents casual/accidental runs.
- **Baseline guard (the heart):** a shard whose **journal proves trimmed history**
 (`journal.front().transition_version > 1` with no sealed baseline covering it) → **`CORRUPTED_DATA`,
 fail closed.** This is the anti-under-count control: without it, folding a trimmed journal from scratch
 would **mass-condemn** every blob whose edges lived only in the lost snapshot → data loss. The guard
 refuses rather than under-count. Same probe is re-run inside rebuild's gen-0 health check.

**Security analysis of the feature:**

| Concern | Verdict |
|---|---|
| **Can rebuild directly delete live data?** | **No.** It re-derives in-degree conservatively and installs state; deletions still flow through the normal round's ack-floor + two-phase + exact-token path. |
| **Can a crafted/tampered owner state make rebuild under-count → data loss?** | **Only with pool-write access (SEC-3).** An adversary who crafts an *internally consistent* owner state (all shards present, journals starting at v1, but with refs silently removed) could get rebuild to compute a baseline missing those edges → later GC reclaims still-referenced blobs. **But** producing that state requires full owner-plane write access, which is already total compromise (SEC-3). The **trimmed-history guard closes the naive path** (truncating a journal is detected and fails closed). So rebuild **adds no attack surface beyond SEC-3**, and defends the accidental-loss case well. |
| **FORCE blast radius** | FORCE only skips the *healthy* check; the rebuild itself remains conservative (guard still fires). Risk is operational (running FORCE on a healthy pool discards live counters and recomputes), not a bypass of the safety guard. |
| **DoS / amplification (SEC-6)** | Rebuild does a **full-universe discover + fold** — O(all shards + all journals). An attacker with SYSTEM (or who can trigger repeated failures that tempt operators to rebuild) can make rebuild an expensive, pool-wide, memory-heavy sweep (shares SEC-4's decode/fold exhaustion). Bounded by SYSTEM gating; recommend rate-limiting / single-flight on the command and streaming the fold. |
| **Interaction with a live writer/GC during rebuild** | Rebuild installs `gc/state` via the same CAS discipline; a concurrent GC leader's round CAS and rebuild's install contend on `gc/state` (one wins). Verify rebuild takes/*respects* GC leadership (lease) so a rebuild and a live round can't both install divergent baselines — if rebuild bypasses the lease, that's a **split-baseline** risk worth confirming. |

**Feature verdict:** cas-gc-rebuild is **well-designed for its threat (accidental state loss)** — it is
fail-closed, refuse-by-default, and cannot be coerced into under-counting without pool-write access that
already implies total compromise. Its residual security items are (a) confirm the RBAC grant is
dedicated/narrow, (b) confirm it runs under GC leadership so it can't race a live round into a
split-baseline, and (c) the shared SEC-4 decode/fold exhaustion surface (bound + stream + rate-limit).

---

## 8. Prioritized recommendations

1. **SEC-1 (High):** add a cryptographic `hash_algo` option and/or namespace-scope blob keys for
 multi-trust-domain pools; document the single-trust-domain assumption prominently.
2. **SEC-3 (High, architectural):** document the bucket-credential-is-the-perimeter model; ship
 least-privilege IAM guidance and per-pool credential isolation as the primary control.
3. **SEC-7 (Med):** carry `writer_epoch` into the shard-CAS precondition (also fixes J1/J2/J3 from the
 Jepsen audit — one change, two audits); require authenticated time in deployment guidance.
4. **SEC-4 (Med):** absolute decode-side size/element caps + streaming fold, independent of the write path.
5. **SEC-2 (Med):** per-trust-domain dedup scoping for multi-tenant pools; document the dedup oracle.
6. **§7 follow-ups:** confirm the REBUILD RBAC grant is dedicated; confirm rebuild runs under GC
 leadership; rate-limit/single-flight the command.
7. **SEC-5 (Low):** reject `..` in `checkNamespace` for backend-agnostic safety.

## Headline

Against its **actual** threat model — **one operator, one trusted bucket, one trust domain** — CAS is
sound: control objects are CRC/framing-validated and fail closed, GC's destructive ops are exact-token
(so a forged GC leader can't delete live data), path traversal is blocked, and **cas-gc-rebuild is a
fail-closed, refuse-by-default recovery tool that cannot be coerced into under-counting without
already-total pool-write access.**

The security story changes materially the moment a pool spans **trust domains** (multi-tenant, mixed-RBAC
databases sharing one pool). Then the two structural properties that are *features* become *risks*:
**pool-global content-addressed dedup on a non-cryptographic hash** (SEC-1 poisoning, SEC-2 oracle) and
**no intra-pool authorization** (SEC-3). Those, plus the NTP/pause-amplifiable fencing gap (SEC-7), are
the real findings; everything else is defense-in-depth hardening. The single highest-leverage code change
is the same one the Jepsen audit surfaced — **`writer_epoch`-fenced shard CAS** — and the single most
important *deployment* rule is **never share a CAS pool across trust domains** until SEC-1/SEC-2/SEC-3 are
addressed.

## cas-test-coverage-fuzzing-audit.md

Language: Markdown

# CAS — Test-Coverage Gaps & Decoder Fuzzing Audit

Scope: how well is CAS tested, and where are the gaps — especially **coverage-guided fuzzing** of the
decoders that parse untrusted bytes from a shared S3 pool, and coverage of the specific findings raised
in the earlier audits (read-side dangle, fencing, crash-atomicity, rolling upgrade). Grounded in
`src/Disks/tests/gtest_cas_*` (~43 files), the `utils/ca-soak/` harness, and `src/*/fuzzers/`.

---

## 1. Existing coverage (strong)

**Unit (gtest), ~43 files** covering essentially every component:
- **Codecs / formats:** `gtest_cas_codecs`, `gtest_cas_envelope`, `gtest_cas_format`,
 `gtest_cas_manifest_codec`, `gtest_cas_manifest_id`, `gtest_cas_gc_formats`, `gtest_cas_run_file`,
 `gtest_cas_ids`, `gtest_cas_layout`.
- **Backend contract:** `gtest_cas_backend`, `gtest_cas_backend_contract`,
 `gtest_cas_backend_generation` (conditional-PUT / CAS semantics — the substrate everything relies on).
- **Write path:** `gtest_cas_build`, `gtest_cas_build_root_dangle`, `gtest_cas_inline_placement`,
 `gtest_cas_store`, `gtest_cas_protocol_scenarios`, `gtest_cascade_and_memory_write_buffer`.
- **GC (deep):** `gc_round`, `gc_fold`, `gc_ack_floor`, `gc_attempt`, `gc_leak`, `gc_log`, `gc_resume`,
 `gc_rebuild`, `gc_shard_incarnation`, `gc_shard_plan`, `gc_source_edge`, `gc_token_diff`,
 `gc_undercount_repro`, `blob_indegree`, `generation_seal`, `retire_view`, `truncate_reclaim`.
- **Mount / lease / identity:** `gtest_cas_mount`, `gtest_cas_heartbeat`.
- **Recovery / integrity:** `gtest_cas_orphan_manifest_sweep`, `gtest_cas_fsck`, `gtest_cas_probe`,
 `gtest_cas_event_log`.
- **Safety regressions:** `gtest_cas_b140_dangle`, `gtest_cas_gc_undercount_repro`,
 `gtest_cas_build_root_dangle` — named regression tests for specific proven-hard bugs (excellent
 practice: each formal/found hazard has a repro test).

**Integration / soak — `utils/ca-soak/`:** a real docker-compose harness across **multiple object
stores** (local, AWS S3, GCS, rustfs), **2- and 10-replica** clusters, and **matrix configs**
(`gc_shards2`, `small_dedup_cache`), with `scenarios/`, `scripts/`, `soak/`, `tests/`, and a
`test_model.py`. This is a serious multi-backend concurrency/soak layer beyond unit tests.

**Verdict:** coverage of the write/GC/mount/codec **core** is genuinely strong — arguably best-in-class
for a storage backend, with formal models (TLA+) *and* regression repros *and* multi-backend soak.

---

## 2. THE gap: no decoder fuzzing (FZ1, High for a shared-pool threat model)

Every object CAS reads is **attacker-influenceable bytes in a shared pool** (see the security audit:
same-pool tenants, no intra-pool authz). The decoders that parse those bytes are:

| Decoder | Parses | Untrusted source | Fuzzed? |
|---|---|---|---|
| `decodePoolMeta` (CasPoolMeta) | pool meta protobuf | pool object | ✖ |
| `CasEnvelope` decode | binary hashed-envelope header + body | every blob/hashed object | ✖ |
| `CasRootShardCodec` decode | root/ref shard protobuf + journal | ref shards | ✖ |
| `CasManifestCodec` decode | part manifest protobuf (entries, blobs) | part manifests | ✖ |
| `CasGcFormats` decode | gc state / retired set / outcomes / fold seal | GC objects | ✖ |
| `CasRunFile` decode | dense block-framed sorted binary run | GC run files | ✖ |
| Owner / ServerEpoch / MountLease decode | control objects | server-root control plane | ✖ |

ClickHouse **already has the fuzzing harness pattern** — `src/Compression/fuzzers/*_decompress_fuzzer`,
`src/DataTypes/fuzzers/data_type_deserialization_fuzzer`, `src/Formats/fuzzers/format_fuzzer`, and
notably **`src/Storages/fuzzers/mergetree_checksum_fuzzer.cpp`** (fuzzing a binary MergeTree decoder) —
but **there is no `src/Disks/fuzzers/` and no CAS decoder fuzz target.** The codec gtests are
**example-based**, not coverage-guided: they exercise well-formed and a few hand-picked malformed
inputs, not the adversarial input space (truncation, length-field overflow, oversized counts, deep
nesting, integer overflow in `blob_header_len`/offsets, malformed protobuf wire types, magic/version
edge values).

This gap **directly amplifies** security findings: the decoders are the first code to touch adversarial
bytes, and `RunFile` / envelope / manifest use length/offset framing where a bad length field is the
classic OOB-read / allocation-bomb vector. `CasRunFile`'s block framing and `CasEnvelope`'s
`blob_header_len`-driven layout are the highest-risk targets.

---

## 3. Coverage gaps mapped to prior findings

| Prior finding | Covered by a test? | Gap |
|---|---|---|
| **R1 / X1** reader-pin dangle (read races GC condemn→delete) | **No read-protocol gtest exists** (no `gtest_cas_read`); GC dangle tests are write/GC-side only | ✖ **T-G1**: no test drives resolve→manifest→(delay)→blob-GET against a concurrent GC delete |
| **J1** fencing TOCTOU (`mayMutate()` at flush-top, content-token-only `casPut`) | `gtest_cas_mount`/`heartbeat` test lease acquisition, not the check→CAS gap under a paused writer | ✖ **T-G2**: no test injects a stale-epoch writer between `mayMutate()` and `casPut` |
| **DUR2 / C-U1** RENAME split table (crash mid-`moveDirectory`) | `protocol_scenarios` covers moves, but re-drive-after-crash / split-state not clearly asserted | ⚠ **T-G3**: assert split-then-re-drive completeness |
| **DUR1 / C-U5** multi-part commit partial on crash | commit rollback-on-exception likely tested; **power-loss** mid-loop not | ⚠ **T-G4** |
| **UPG1** rolling upgrade across a format gen | `gtest_cas_format` tests gating at `G_BUILD=1` only | ✖ **T-G5**: no two-generation compat test (and write-down-to-floor is unimplemented) |
| **C1–C4** teardown UAF / thread-shutdown races | no TSan/dtor-race stress test visible | ✖ **T-G6**: add a ThreadSanitizer stress for Store open/close + remount |
| GC safety core (fold, ack-floor, incarnation, dangle, undercount) | extensively covered + regression repros | ✔ |

---

## 4. Recommendations (priority order)

1. **FZ1 — add `src/Disks/fuzzers/` CAS decoder fuzzers** (mirror `mergetree_checksum_fuzzer`):
 one `LLVMFuzzerTestOneInput` per decoder — envelope, run-file, manifest, root-shard, gc-formats,
 pool-meta. Assert **no crash / no OOB / bounded allocation** on arbitrary bytes. Highest ROI given
 the shared-pool threat model; the framing-based decoders (RunFile, Envelope) first.
2. **T-G1 — read-protocol concurrency test:** drive `resolveRef → readManifest → (inject delay) →
 blob GET` against a concurrent `dropRef` + GC condemn→delete; today R1/X1 is only reasoned, not
 tested. This is the single most valuable new *functional* test.
3. **T-G2 — fencing test:** simulate a paused/superseded writer that passes `mayMutate()` then issues
 `casPut` after a newer epoch mounted; assert the shard CAS rejects it (this test **fails today**,
 which is the point — it pins J1).
4. **T-G5 — two-generation compat test** once write-down-to-floor lands (UPG1): a gen-N reader must read
 a gen-N+1 additive object and refuse a breaking one.
5. **T-G6 — TSan stress** for Store teardown/remount (C1–C4).
6. **T-G3/T-G4 — crash-mid-RENAME and power-loss-mid-commit** repros in the soak harness (kill a node
 mid-multi-op, assert re-drive completes / no dangle).

---

## 5. Summary

| # | Finding | Severity |
|---|---|---|
| FZ1 | No coverage-guided fuzzing of any CAS decoder (untrusted shared-pool bytes) | **High** (shared-pool) |
| T-G1 | No read-protocol concurrency test → R1/X1 dangle untested | Med |
| T-G2 | No fencing TOCTOU test → J1 untested | Med |
| T-G5 | No cross-generation rolling-upgrade test → UPG1 untested | Med (latent) |
| T-G6 | No TSan teardown-race stress → C1–C4 untested | Low–Med |
| T-G3/T-G4 | Crash-mid-RENAME / partial-commit recovery not asserted | Low–Med |

**Headline.** The functional test story is excellent: ~43 unit suites covering every codec and every GC
sub-mechanism, **named regression repros** for the hardest proven bugs (`b140_dangle`,
`gc_undercount_repro`, `build_root_dangle`), a **multi-backend docker soak harness** (S3/GCS/rustfs, up
to 10 replicas), *and* TLA+ models on top. The gaps are concentrated exactly where the other audits
found risk and where example-based tests can't reach: (1) **no decoder fuzzing** despite untrusted
shared-pool bytes and an existing ClickHouse fuzz-harness pattern (FZ1 — the top recommendation); and
(2) the **findings that live in gaps between components are also gaps in tests** — the read-side dangle
(R1/X1), the fencing TOCTOU (J1), rolling-upgrade compat (UPG1), and teardown races (C1–C4) each lack a
test that would fail today. Adding those tests (especially a fencing test and a read-vs-GC race test
that *fail* on the current code) would convert the audit findings into enforced regressions.

## cas-tier1-audit.md

Language: Markdown

# CAS — Tier 1 Audit: Replication, Lifecycle/Reclamation, Integrity, Query-MVCC

Four correctness-critical, CAS-specific areas that prior audits only touched tangentially. Grounded in
`DataPartsExchange.cpp`, `ContentAddressedExchange.h`, `ContentAddressedMetadataStorage.{h,cpp}`,
`ContentAddressedTransaction.cpp`, `Core/CasStore.cpp` (`dropNamespace`/`listNamespaces`),
`Core/CasEnvelope.cpp`, and `Core/CasFsck.{h,cpp}`.

Severity: **High** = data-loss/leak/incorrect-result risk; **Med** = correctness gap under specific
conditions; **Low/Info** = operational or defense-in-depth.

---

## 1. ReplicatedMergeTree deep-dive

### How it works on CAS
Replication is driven by the ZooKeeper log; the storage disk is asked to *materialize* parts. The only
CAS-specific replication seam is **fetch-by-relink** (`IContentAddressedExchange`, wired in
`DataPartsExchange.cpp`):

- **Sender** (`Service::processQuery`): if the part is on a CA disk and the receiver advertised a
 matching `content_addressed_pool_uuid`, the sender transmits **only the encoded `PartManifest` body +
 `metadata_version`** (no file bytes) and sets the `content_addressed_relink=part_manifest_v1` cookie.
- **Receiver** (`Fetcher::fetchSelectedPart` → `relinkPartToDisk` → `adoptPartFromManifest`): decodes the
 body, **ignores sender identity** (ManifestRef/root_namespace_id/payload_digest are non-authoritative),
 runs a **local build over shared-pool blobs (adopt-by-hash, no bytes fetched)**, and promotes a fresh
 **receiver-local** ManifestId in the receiver's own namespace. On any missing/condemned blob it returns
 `false` and the caller **falls back to a byte fetch** (re-request with relink disabled).

### Findings

**RPL-1 (Info — sound by design).** The relink contract is well-constructed: pool identity is gated on
`PoolMeta::pool_id` equality (not endpoint string-matching — the comment explicitly rejects prefix
matching as unsafe), sender identity is non-authoritative, and the receiver revalidates every blob
fail-closed inside `promote`. A different-pool false-positive (cheap pre-filter let it through) degrades
to a correct byte fetch. **No divergence risk from relink itself.**

**RPL-2 (Med — ZK/CAS ref divergence on partial commit).** ReplicatedMergeTree treats ZooKeeper as the
source of truth for the *part set*; CAS refs are the source of truth for *bytes*. These are two
independent commit points with **no cross-transaction**. If a replica adds the part to ZK but crashes
before the CAS ref promote durably lands (or vice versa), the two registries disagree:
- ZK-has / CAS-missing: on restart the part is "known" but `resolveRef` returns absent → the part loads
 broken / triggers a re-fetch. Recoverable (re-fetch from another replica), but this is the storage
 face of the previously filed **DUR1 partial-commit** gap, now confirmed to also apply to the
 *replicated* add path.
- CAS-has / ZK-missing: an orphaned live ref (a promoted manifest ZK never learned about). It is
 reachable (keeps its blobs alive) but invisible to the table → a **silent storage leak** until DROP
 TABLE reclaims the whole namespace. Not data loss, but unbounded if it recurs.

**RPL-3 (Med — relink races GC in the shared pool).** `adoptPartFromManifest` adopts blobs by hash and
revalidates in `promote`; but between the sender encoding the manifest and the receiver's promote, GC on
the shared pool can condemn a blob that *was* live via the sender's ref. The design handles the common
case (missing/condemned → return false → byte fetch). The residual risk is a **TOCTOU inside promote**:
if a blob passes `observeAndAdmit` but is condemned/deleted before the ref shard CAS commits, the
receiver could publish a ref to a to-be-deleted blob. This is the same window as the general **J1
zombie-writer / X1 reader-pin** class; relink inherits it rather than introducing a new one. Mitigated in
practice by GC's two-phase graduation (`delete_pending` before `deleteExact`) + copy-forward, but not
*provably* closed for the relink promote path — **no dedicated test**.

**RPL-4 (Med — `to_detached` relink is disabled; FETCH PARTITION ... always streams bytes).** The
receiver only advertises relink when `try_zero_copy && !to_detached`. So `ALTER TABLE ... FETCH PARTITION`
(into `detached/`) and the byte-fetch fallback **never relink** — they stream full bytes even within the
same pool, then content-address+dedup on landing. Correct, but a **perf cliff**: cross-replica FETCH of a
large partition transfers full bytes despite the blobs already being in the shared pool. Explicitly
deferred in code ("Relink-into-detached is a deferred optimization").

**RPL-5 (Low — quorum/`SYNC REPLICA`/`cloneReplica` untested on CAS).** Quorum inserts, `SYSTEM SYNC
REPLICA`, lost-replica recovery (`cloneReplica`), and `REPLACE_RANGE`/`DROP_RANGE` log entries all reduce
to sequences of fetch (relink or byte) + drop, which individually work. But there is **no integration
test** exercising them against a CA disk, and `cloneReplica` (which can enqueue a large fan-out of GETs
that each *should* relink) crosses RPL-3/RPL-4. Behavior is *expected-correct* but *unverified*.

---

## 2. Table lifecycle & storage reclamation

### How it works on CAS
DROP/TRUNCATE/DETACH map through `ContentAddressedTransaction::removeRecursive`/`removeDirectory`:
- **DROP TABLE** (table dir) → `dropNamespace(liveNamespace(uuid))` — tombstones every present shard,
 appends one ref-removal journal event per ref + a `is_tombstone` event, clears refs. Blobs are **not**
 deleted here; GC reclaims them once unreachable (empty + tombstoned + fully folded → `deleteExact`).
- **Single part drop** (merge source, mutation, TTL) → `removeDirectory()` → `dropRefIfPresent`.
- **DROP DETACHED / detach-all** → iterate `detachedRefNames` → drop each.
- **FREEZE shadow / UNFREEZE** → shadow-namespace drops.
- Detached parts are **folded into the table namespace** as `detached/`-prefixed refs (B181), so DROP
 TABLE reclaims live + detached in one `dropNamespace`.

### Findings

**LC-1 (Med — reclamation is GC-deferred; DROP TABLE frees no bytes synchronously).** `dropNamespace`
only tombstones/clears refs; the actual S3 object deletion depends on a subsequent GC round observing the
tombstone folded through the three-cursor merge. Consequences:
- **`DROP TABLE` returns success while 100% of the bytes remain in S3**, billed, until GC catches up
 (interval default 60s but a full reclaim needs discover→fold→graduate→delete across rounds).
- If **GC is disabled** (`gc_enabled=false`, read-only disk, or a pool whose only writer is gone), a
 dropped table's blobs are **leaked permanently**. There is no synchronous/foreground reclaim path.
- Operators expecting `DROP TABLE` to free storage (quota relief, cost) will be surprised. **Needs
 documentation** and ideally a `SYSTEM ... GC` nudge in the drop path or a metric for "bytes pending
 reclaim".

**LC-2 (Med — orphaned namespaces after crash between metadata drop and `dropNamespace`).** DROP TABLE in
ClickHouse first removes the table metadata (`.sql`) / detaches, then removes data. If the server crashes
after the table is gone from the catalog but before/within `removeRecursive`, the CAS namespace's shards
are **left present with live refs** and **no owning table** to ever call `dropNamespace` again. Result: a
permanently orphaned namespace whose blobs stay reachable → **permanent leak**, invisible to any table.
`listNamespaces` can *enumerate* them but nothing *reconciles* catalog-vs-pool. There is no
"orphan-namespace sweep" analogous to `CasOrphanManifestSweep` (which only handles pre-precommit manifest
debris, not fully-committed orphaned refs).

**LC-3 (Low — cross-pool DROP is per-server).** In a shared pool, DROP TABLE from one `server_root_id`
tombstones only that namespace. Blobs shared (deduped) with another server's still-live ref correctly
survive (source-edge set semantics). Correct — noted for completeness.

**LC-4 (Info — TRUNCATE = drop all part refs, keep namespace).** TRUNCATE removes part refs but the
namespace/table survives; same GC-deferred reclaim as LC-1. No new issue.

---

## 3. Data integrity (CHECK TABLE, corruption/bit-rot, fsck)

### How it works on CAS
- **MergeTree `CHECK TABLE`** (`checkDataPart.cpp`) reads each part file *through the disk* and re-hashes
 against `checksums.txt`. On CAS this transparently pulls blob payloads via the ranged-GET read path —
 so **CHECK TABLE works** and provides the primary integrity guarantee, exactly as on a plain S3 disk.
- **CAS envelope** (`CasEnvelope.cpp`) verifies on read: magic, `compatibility_version` gate, `header_len`
 bounds, the **header hash** (CityHash64 over the 94-byte core header), and **size arithmetic**
 (`header_len + logical_size == object_size`). Critical-TLV unknown → fail closed.
- **`CasFsck::runFsck`** independently recomputes reachability from authoritative refs (never from
 `gc/snap`) and diffs against a raw object listing, classifying Reachable / **Dangling (INV-NO-LOSS
 violation)** / Unreachable / PendingGc / AwaitingGc / Unaccounted.

### Findings

**INT-1 (High — blob payload is NOT verified against its content hash on read).** The envelope stores
`logical_hash` (the payload's content hash) and CAS keys the blob by it, but the read path **only
verifies the header hash and size**, never re-hashes the payload region against `logical_hash`. So
**silent S3 bit-rot / truncation inside the payload is undetected by CAS**. The header-hash comment even
says it is "a diagnostics-quality check, not a safety dependency." Integrity therefore rests **entirely
on MergeTree's own layer** (compressed-block checksums during read when enabled, and `checksums.txt` on
CHECK TABLE). Implications:
- A corrupted blob is caught **only** if the reader validates MergeTree checksums (not all read paths do,
 e.g. some raw/asynchronous prefetch paths), or on an explicit CHECK TABLE.
- CAS's strongest available integrity signal (content == hash) is computed at write but **thrown away at
 read**. A cheap `logical_hash` re-verification (at least optionally, or on CHECK TABLE / fsck) would
 make CAS self-verifying. Currently fsck checks *presence/reachability*, **not content correctness**.

**INT-2 (Med — dedup trusts the hash: a hash collision or a mis-keyed blob silently shares wrong bytes).**
Because dedup is by content hash (CityHash128 pool content hash — non-cryptographic, per SEC-1), two
distinct payloads that collide would be treated as one blob. Combined with INT-1 (no read-time payload
verification), a collision is **undetectable at the CAS layer**. MergeTree checksums would still catch a
wrong-bytes read for the *victim* part, but attribution would be baffling. Low probability, high blast
radius (a shared blob feeds *every* ref that adopted it). Cross-references SEC-1/INT-1.

**INT-3 (Med — a Dangling classification means data is already lost, not preventable).** `runFsck`
reports Dangling (reachable-from-live-ref but object MISSING) as an INV-NO-LOSS violation, i.e. the part
is **already unreadable**. Fsck is a **detector, not a repair** tool; there is no automated
re-fetch-from-replica on dangling detection. On a ReplicatedMergeTree table recovery is possible manually
(another replica has the blobs); on a non-replicated CA table a dangling blob = permanent part loss. No
guardrail forces periodic fsck.

**INT-4 (Low — no proactive scrubbing).** Nothing periodically re-reads/re-hashes cold blobs. Bit-rot on
rarely-read cold data accumulates undetected until a query or CHECK TABLE touches it. Standard for
object-store-backed MergeTree, but worth stating given CAS holds *shared* blobs (one rotted blob damages
every ref that deduped onto it).

---

## 4. Query-layer read correctness & MVCC

### How it works on CAS
Query snapshot isolation is a **MergeTree-level** property: a running SELECT pins its `DataPart` objects
(`shared_ptr`) and its already-opened file readers; the part lifecycle Active→Outdated→removal only
`dropRef`s a part after it is no longer Active **and** `old_parts_lifetime` elapsed with no query holding
it. So the *ref* survives as long as the query's part does.

### Findings

**MVCC-1 (Med — the storage-level dangle window (R1/X1) is the real MVCC risk).** The MergeTree pin keeps
the *part* alive, but the previously-filed **R1/X1** finding shows a window where a reader holding an open
blob view can race a `dropRef` + GC reclaim of the underlying blob (reader has no CAS-level *pin* on the
blob, only an S3 object handle). Under normal `old_parts_lifetime` this is comfortably avoided; under an
aggressive GC + very long-running query + a part that went Outdated mid-query, a ranged GET can hit a
deleted object → query error (not wrong results — fail-loud). This is **the** query-MVCC exposure and it
is a **storage dangle**, not a snapshot-isolation logic bug. No new anomaly beyond R1/X1.

**MVCC-2 (Info — no wrong-results anomaly).** Because CAS is content-addressed and immutable, a query
either reads the exact committed bytes of the parts it pinned or fails loudly (missing object). There is
**no** dirty-read / non-repeatable-read / phantom risk introduced by CAS itself — those remain governed
by MergeTree's part-set snapshot, unchanged from plain S3. Consistent with the Jepsen audit's verdict.

**MVCC-3 (Low — `FINAL` / parallel-replicas / patch-apply-on-read unverified on CAS).** `FINAL` (merge
engines), parallel-replica reads, and lightweight-update patch-apply-on-read all issue *more* concurrent
ranged GETs against pinned parts. Logically identical to reading normal parts, but the **read
amplification** and the interaction with the decode caches (shard/manifest) under `FINAL`'s wide part
fan-in is untested for correctness-under-concurrent-merge. Expected-correct, unverified.

---

## Summary table

| ID | Sev | Area | One-liner |
|----|-----|------|-----------|
| RPL-1 | Info | Replication | Relink contract is sound; false-positive degrades to correct byte fetch |
| RPL-2 | Med | Replication | ZK part-set vs CAS ref can diverge on partial commit (DUR1 face) |
| RPL-3 | Med | Replication | Relink promote inherits J1/X1 blob TOCTOU vs shared-pool GC; untested |
| RPL-4 | Med | Replication | `FETCH PARTITION ... TO detached` / fallback never relink → full byte transfer |
| RPL-5 | Low | Replication | Quorum / SYNC REPLICA / cloneReplica correct-by-composition but untested |
| LC-1 | Med | Lifecycle | DROP TABLE frees zero bytes synchronously; GC-deferred; leaks if GC off |
| LC-2 | Med | Lifecycle | Crash between catalog drop and `dropNamespace` → permanently orphaned namespace, no sweeper |
| LC-3 | Low | Lifecycle | Cross-pool DROP correctly preserves shared blobs |
| LC-4 | Info | Lifecycle | TRUNCATE = drop refs, keep namespace; same deferred reclaim |
| INT-1 | High | Integrity | Blob payload never re-hashed vs `logical_hash` on read; bit-rot undetected by CAS |
| INT-2 | Med | Integrity | Non-crypto content hash + no read verify → collision/mis-key silently shares wrong bytes |
| INT-3 | Med | Integrity | fsck detects Dangling (=already lost); no auto-repair; no forced cadence |
| INT-4 | Low | Integrity | No proactive scrubbing; one rotted shared blob damages every deduped ref |
| MVCC-1 | Med | Query/MVCC | R1/X1 storage dangle is the real MVCC exposure (fail-loud, not wrong results) |
| MVCC-2 | Info | Query/MVCC | No dirty/non-repeatable/phantom introduced by CAS; snapshot stays MergeTree's |
| MVCC-3 | Low | Query/MVCC | FINAL / parallel-replicas / patch-apply-on-read untested under concurrent merge |

## Highest-priority recommendations
1. **INT-1**: add optional read-time (or CHECK TABLE / fsck) payload re-verification against
 `logical_hash` so CAS becomes self-verifying instead of delegating all integrity to MergeTree.
2. **LC-2**: add an orphan-*namespace* reconciliation sweep (catalog-vs-pool), analogous to
 `CasOrphanManifestSweep`, to bound permanent leaks from crash-during-drop.
3. **LC-1**: document that reclamation is GC-deferred and expose a "bytes pending reclaim" metric;
 consider nudging GC on DROP.
4. **RPL-2/RPL-3**: add integration tests for the replicated add path crash-consistency and for
 relink-vs-GC in a shared pool.

## cas-tier2-audit.md

Language: Markdown

# CAS — Tier 2 Audit: System Tables, Filesystem Cache, Storage Policy/TTL Moves, INSERT Dedup

Integration & operational surfaces. Grounded in `DiskObjectStorage.cpp` (`prepareRead`,
`getStorageObjects`, space reporting), `ContentAddressedMetadataStorage.cpp` (`getStorageObjects`,
`tryGetInManifestBytes`), `PartPathParser.{h,cpp}` (`deduplication_logs`), and
`ContentAddressedTransaction.cpp` (`createHardLink`/`moveFile`).

---

## 1. System tables / introspection

### How it works
`system.parts.bytes_on_disk`, `system.remote_data_paths`, `system.disks` free-space, etc. are computed
from `getStorageObjects(path)` and disk space APIs. On CAS a blob-backed part file returns
`StoredObject(blob_key, path, payload_length)`; a mutable/in-manifest file returns a **sized empty-key
placeholder** `StoredObject("", path, size)`; free-space comes from the object-storage disk (effectively
unbounded for S3).

### Findings

**SYS-1 (Med — `bytes_on_disk` is LOGICAL, over-reports physical usage).** Each part reports the sum of
its file **payload lengths**. Because CAS deduplicates, a blob shared by N part files is counted **N
times** across `system.parts`. So `SUM(bytes_on_disk)` >> actual S3 bytes — often dramatically for
merge/mutation-heavy tables (hardlink-unchanged becomes copy-by-reference, so the "copy" is free on disk
but still counted). Operators sizing storage or cost from `system.parts` will **massively overestimate**.
The true physical figure lives only in `CasFsck` (`physical_bytes` vs `referenced_logical_bytes`,
`dedupRatio()`), which is not surfaced as a system table. **Recommend a `system` view exposing physical
vs logical + dedup ratio.**

**SYS-2 (Low — `system.remote_data_paths` shows empty remote path for in-manifest files).** Mutable
per-part files (`metadata_version.txt`, `uuid.txt`, `txn_version.txt`, `columns.txt` bytes,
`deduplication_logs`) have `StoredObject("", …)` — no remote object. In `system.remote_data_paths` these
render with an **empty `remote_path`**, which can confuse tooling that treats the table as (local →
remote) 1:1. Not wrong (there genuinely is no object), but undocumented.

**SYS-3 (Info — dedup makes `remote_data_paths` many-to-one).** Many local part-file paths (across parts,
tables, even replicas) map to the **same blob key**. This is accurate and actually useful (you can see
sharing), but any consumer assuming remote paths are unique-per-file will miscount.

**SYS-4 (Low — `system.disks` free/total space is object-storage placeholder).** Free space is not a real
CAS quota; reservation logic (`getAvailableSpace` in `reserve`) uses the object-storage number. TTL/move
decisions based on `move_factor` and free space therefore behave as on any S3 disk (effectively never
"full"), which may defeat free-space-driven tiering heuristics. Standard object-store behavior, noted.

**SYS-5 (Low — `system.mutations`/`part_log`/`replicated_fetches` unverified for CAS-specific fields).**
These populate from MergeTree bookkeeping and should be engine-agnostic, but CAS-specific paths (relink
fetches showing 0 bytes transferred in `system.replicated_fetches`; `part_log` `bytes_uncompressed` vs
deduped physical) are untested for sensible values.

---

## 2. Filesystem cache composition (cache disk over CAS)

### How it works
`DiskObjectStorage::prepareRead` composes the **standard** pipeline for a CA blob-backed file:
`needGather` → `storage->prepareRead` (adds `needFilesystemCache` when the object storage is a
`CachedObjectStorage`) → optional distributed/page cache → async prefetch → **`needFileView` last**
(bounds the chain to the payload window, skipping the CHCA envelope header). The FS cache is keyed by the
**object's remote path = the content-hash blob key**.

### Findings

**CACHE-1 (Info — content-addressed keys make the FS cache ideal ✅).** Blob keys are stable, immutable,
and content-defined, so:
- **No invalidation needed** — a blob never changes, so a cache entry is never stale (unlike random-key
 disks where a rewritten file needs cache eviction).
- **Cache-level dedup** — identical content across parts/tables/replicas shares **one** cache entry
 (same blob key), multiplying effective cache capacity.
This is a genuine CAS advantage; the composition looks correct.

**CACHE-2 (Med — FileView-after-cache: cache granularity is the whole blob, offset by envelope).** The
FS cache caches ranges of the **full blob object** (envelope + payload); the FileView window is applied
*above* the cache. So cached byte ranges are in blob coordinates, and every logical read is shifted by
`payload_offset`. This is correct but has two consequences worth testing:
- Cache segment boundaries don't align to the logical file start (they align to blob start), so the
 first cached segment of every file includes/straddles the envelope header region. Benign but means the
 header bytes occupy cache.
- If a future change ever **packs multiple part-files into one blob**, they'd share cache segments — fine
 for read, but cache accounting/eviction would be per-blob not per-file. Currently one blob = one
 payload, so not an issue today.

**CACHE-3 (Low — cache observability is by blob key, not part path).** `system.filesystem_cache` shows
blob keys; correlating a hot cache entry back to a table/part requires a `remote_data_paths` join. Minor.

---

## 3. Storage policy / tiered storage / TTL moves

### How it works
CAS is one disk/volume in a storage policy. Cross-disk data movement (`MOVE PARTITION TO DISK/VOLUME`,
TTL-to-cold, `move_factor` background moves) goes through the generic move path, which **reads bytes from
the source disk and writes them to the destination**. `createHardLink` on CAS is copy-by-reference but
**only within the same CAS disk/pool**; there is no cross-disk relink in the move path.

### Findings

**TIER-1 (Med — cross-disk MOVE is a full byte copy, even CAS→CAS same-pool).** Moving a partition from a
hot local/S3 disk **onto** CAS writes new content-addressed blobs (correct, and dedups against existing
pool content — a nice property). Moving **off** CAS (or between two CAS disks even on the *same pool*)
reads every byte and rewrites it on the target — there is **no move-path relink** analogous to the
replication fetch-by-relink. So same-pool tiering between two CAS volumes needlessly transfers full
bytes. This is the "cross-disk MOVE unverified/byte-copy" item from the part-support audit, now confirmed
as a **byte copy with no CAS shortcut** and, for CAS→CAS same-pool, a missed optimization.

**TIER-2 (Med — TTL move + GC-deferred reclaim double-bills storage transiently).** After a TTL move
*off* CAS, the source part's ref is dropped but its blobs persist until GC reclaims (LC-1). During that
window the data exists on **both** tiers → transient double storage cost, longer than on a plain disk
where the source is deleted synchronously. For a large TTL-move wave this can be significant.

**TIER-3 (Low — move correctness under concurrent GC untested).** A cross-disk move reads source bytes
(ranged GETs against pinned blobs) while GC may be reclaiming a just-dropped source ref — same R1/X1
dangle class. Expected fail-loud, unverified.

**TIER-4 (Info — `move_factor`/free-space heuristics are inert on CAS source).** Because CAS free space
is a placeholder (SYS-4), free-space-triggered background moves from CAS effectively never fire; only
explicit/TTL moves apply. Noted.

---

## 4. INSERT block-deduplication

### How it works
- **Non-replicated** (`non_replicated_deduplication_window`): block hashes are kept in
 `deduplication_logs/` files, which CAS stores as **verbatim table-level files** (recognized by
 `kDeduplicationLogsDirName` in `PartPathParser`; written/removed as namespace files).
- **Replicated**: block hashes live in **ZooKeeper**, orthogonal to the disk.

### Findings

**DEDUP-1 (Info — CAS content-dedup and MergeTree block-dedup are complementary, no conflict).**
MergeTree block-dedup prevents a *duplicate part from being created*; CAS content-dedup collapses
*identical blobs* regardless. If block-dedup misses (window rolled, different insert boundaries producing
byte-identical files), CAS still collapses the bytes. They compose cleanly; no double-counting bug at the
storage layer.

**DEDUP-2 (Low — non-replicated dedup log durability rides mutable-file semantics).** The
`deduplication_logs/` verbatim files are updated as CAS namespace files (last-writer-wins, no sidecar
object). Their durability/consistency inherits the mutable-file commit path; a crash mid-update could
lose the most recent window entries → a spurious re-insert of a just-inserted block is *possible* (a
duplicate part), which CAS would then content-dedup at the blob level anyway. Effect is bounded to a
duplicate *part* (extra ref, same blobs), not data loss. Untested.

**DEDUP-3 (Info — replicated dedup is disk-agnostic).** ZK-based dedup is unaffected by CAS. No issue.

---

## Summary table

| ID | Sev | Area | One-liner |
|----|-----|------|-----------|
| SYS-1 | Med | System tables | `bytes_on_disk` is logical; over-reports physical usage N× under dedup; no physical/dedup system view |
| SYS-2 | Low | System tables | In-manifest files show empty `remote_path` in `system.remote_data_paths` |
| SYS-3 | Info | System tables | Dedup makes remote paths many-to-one (accurate, can confuse counters) |
| SYS-4 | Low | System tables | `system.disks` free space is placeholder; free-space tiering heuristics inert |
| SYS-5 | Low | System tables | mutations/part_log/replicated_fetches CAS-specific fields unverified |
| CACHE-1 | Info | FS cache | Content-addressed keys ⇒ no invalidation + cache-level dedup (CAS advantage) |
| CACHE-2 | Med | FS cache | Cache caches whole-blob ranges; FileView applied above — correct, test envelope-offset alignment |
| CACHE-3 | Low | FS cache | Cache observability by blob key, not part path |
| TIER-1 | Med | Tiering | Cross-disk MOVE is full byte copy; no relink even CAS→CAS same-pool |
| TIER-2 | Med | Tiering | TTL move off CAS double-bills storage until GC reclaims source |
| TIER-3 | Low | Tiering | Move vs concurrent GC untested (R1/X1 class) |
| TIER-4 | Info | Tiering | `move_factor` free-space heuristics inert on CAS source |
| DEDUP-1 | Info | INSERT dedup | Block-dedup and CAS content-dedup complementary; no conflict |
| DEDUP-2 | Low | INSERT dedup | Non-replicated dedup-log durability rides mutable-file commit; bounded to duplicate part |
| DEDUP-3 | Info | INSERT dedup | Replicated ZK dedup disk-agnostic |

## Highest-priority recommendations
1. **SYS-1**: expose a system view with physical bytes / referenced-logical bytes / dedup ratio (from the
 fsck numbers) so operators can size and bill correctly.
2. **TIER-1**: implement move-path relink for CAS→CAS same-pool moves (reuse the replication relink) to
 avoid full byte transfers during tiering.
3. **CACHE-2**: add a test asserting FS-cache-over-CAS returns correct bytes with the envelope offset and
 FileView bounds under partial-cache-hit conditions.

## cas-tier3-audit.md

Language: Markdown

# CAS — Tier 3 Audit: Merge Engines, Transactions, BACKUP/RESTORE, Startup Load, Async Insert, Config

Feature-completeness & edge cases. Grounded in `PartPathParser.{h,cpp}` (reserved mutable files,
`deduplication_logs`, shadow/backup shapes), `ContentAddressedMetadataStorage.{h,cpp}`
(`tryGetInManifestBytes` force-fresh txn_version, listing surface), `ContentAddressedTransaction.cpp`
(`createHardLink`), and the CAS core codecs. Cross-references the part-support and ALTER/merge/mutation
audits.

---

## 1. Special merge engines (Replacing / Collapsing / Summing / Aggregating / VersionedCollapsing / Graphite)

### How it works
All of these differ from plain MergeTree only in their **merge-time row-collapsing logic**, executed by
`MergeTask`. The *output* is always a normal whole part written through the standard CA write transaction
(one new ref, content-addressed blobs). `FINAL` and the implicit merge semantics run in the query/merge
pipeline, above the storage layer.

### Findings

**ENG-1 (Info — storage-transparent, fully supported).** Because the engine-specific behavior is purely
merge logic producing ordinary parts, CAS stores them identically to plain MergeTree parts. No
engine-specific CAS code, no engine-specific storage bug. ✅

**ENG-2 (Low — `FINAL` read amplification & concurrent-merge correctness unverified).** `FINAL` (and
`SELECT ... FINAL`-style dedup on read) fans in many parts, issuing more concurrent ranged GETs against
pinned parts and stressing the shard/manifest decode caches. Logically identical to normal reads, but
untested for correctness under a concurrent merge that drops source parts (the MVCC-1 / R1 dangle class).
Expected-correct, unverified. Same as Tier 1 MVCC-3.

**ENG-3 (Info — Graphite/Aggregating rollup produce smaller parts → better dedup).** Rollup merges shrink
data; no CAS concern beyond ENG-1.

---

## 2. MergeTree experimental transactions (MVCC via `txn_version.txt`)

### How it works
Transactional MVCC uses per-part `txn_version.txt` (creation/removal TID+CSN). CAS treats
`txn_version.txt` as a **reserved mutable per-part file** (`kMutablePerPartFiles`), stored in
`RefPayload.mutable_files`, and — crucially — reads it **force-fresh** (`tryGetInManifestBytes` calls
`resolveRef` bypassing the TTL shard decode cache) so a stale manifest can never serve an old visibility
state. Updates go through `updateRefPayload`.

### Findings

**TXN-1 (Med — mechanically supported but experimental & untested on CAS).** The read-freshness handling
is deliberately correct (the code comment: "Force-fresh (Pillar B): MVCC txn_version … must not serve a
TTL-stale manifest"). Mechanically, per-part TID/CSN read+write works. **But** MergeTree transactions are
an experimental feature and there is **no test** exercising multi-statement transactions, rollback, or
`system.transactions` against a CA disk. Risk is not a known bug but *unvalidated composition* of two
experimental subsystems.

**TXN-2 (Med — multi-part atomic visibility depends on MergeTree, and inherits DUR1).** A transaction
committing several parts flips visibility by writing `txn_version.txt` on each. CAS updates each ref
independently (no cross-ref atomic commit). If the server crashes mid-commit, some parts' `txn_version`
land and others don't → the same **partial-commit (DUR1)** exposure, now at *transaction* granularity.
MergeTree's own crash recovery (CSN log) is the backstop; whether it correctly reconciles against
partially-updated CA mutable files is untested.

**TXN-3 (Low — rollback = drop refs, GC-deferred).** Transaction rollback drops the newly-created part
refs; blobs reclaim via GC (LC-1). No new issue beyond deferred reclaim.

---

## 3. BACKUP / RESTORE and FREEZE

### How it works
- **FREEZE / UNFREEZE** map to **shadow namespaces** (`shadowNamespace(shadow_table_dir)`), bijective with
 the disk path for both Atomic and non-Atomic layouts; FREEZE creates shadow refs (copy-by-reference,
 no byte duplication — a genuine CAS win), UNFREEZE drops them.
- **BACKUP** uses temporary hard links then reads the part files; on CAS `createHardLink` is
 copy-by-reference but requires **two well-formed part-file paths**.
- **RESTORE** writes parts back through the normal write path (content-addressed on landing).

### Findings

**BAK-1 (Med — BACKUP restricted to Atomic/UUID databases).** As found in the part-support audit,
`createHardLink`'s path-shape requirements + the temporary-hard-link BACKUP flow break on Ordinary /
non-UUID database layouts (the `looksLikePartDir` heuristic and UUID-derived namespace mapping). BACKUP
of a CA table on an Ordinary database is effectively unsupported/rejected. Atomic databases (the default)
work.

**BAK-2 (Info — FREEZE is essentially free on CAS ✅).** Because FREEZE shadow refs are copy-by-reference
over shared blobs, freezing a large table adds refs (metadata), not bytes. Excellent CAS property.
UNFREEZE drops shadow refs; blobs reclaim via GC only if no live ref remains.

**BAK-3 (Med — incremental BACKUP dedup semantics unverified).** ClickHouse incremental backups dedup at
the backup layer by file checksum/size. CAS already deduped identical blobs; the backup layer sees
logical files (via the read path). Whether incremental backup correctly avoids re-copying blobs that are
byte-identical across parts (and how it interacts with the empty-key placeholders for mutable files) is
untested. Risk: over-copy (safe but wasteful) or, worse, a mutable-file (`metadata_version.txt`) being
mis-handled by a backup that keys on remote object identity (empty key).

**BAK-4 (Low — RESTORE round-trip correctness untested).** RESTORE writes normal parts; expected-correct,
but a full BACKUP→drop→RESTORE→CHECK TABLE round-trip on CAS is not in the test suite. Packed
storage-type parts arriving via RESTORE remain the untested case flagged in the part-support audit.

---

## 4. Startup / part loading & recovery

### How it works
On startup MergeTree enumerates parts via `listDirectory`/`iterateDirectory` on the table dir; CAS serves
these from `listLiveTreeChildren` / ref enumeration (LIST over `cas/refs/ /` + verbatim `roots/`
files). `format_version.txt` is a table-level verbatim file. Broken/outdated parts are detected by
MergeTree's normal load logic reading `checksums.txt`/`columns.txt` (served from `mutable_files` or blob
payloads).

### Findings

**BOOT-1 (Med — part enumeration authority is S3 LIST; needs read-your-writes LIST).** Startup part
discovery relies on `listNamespaces`/`listLiveTreeChildren`, which the code notes **requires strongly
consistent, read-your-writes LIST** (guaranteed on S3 since 2021; "RustFS: to confirm in soak"). On a
backend with eventually-consistent LIST, a just-committed part could be **missing at startup** → a
"lost" part until the next reconciliation. This is a hard dependency worth calling out per-backend (ties
to the Tier 4 object-store compat matrix).

**BOOT-2 (Med — orphaned refs surface as phantom parts at startup).** The RPL-2 / LC-2 orphaned refs
(committed on CAS but unknown to ZK/catalog) will be **enumerated by `listDirectory` at startup**.
MergeTree may then either load them as unexpected parts (and detach/remove) or ignore them. Behavior of
MergeTree's "unexpected part" handling against CA-enumerated orphans is untested; worst case is repeated
detach churn.

**BOOT-3 (Low — broken-part detection depends on MergeTree, given INT-1).** Since CAS does not verify
blob payloads against `logical_hash` on read (Tier 1 INT-1), a corrupted part is only flagged broken at
startup if MergeTree validates checksums during load. Load-time validation is not always full, so a
subtly-corrupt cold part can load "OK" and fail later. Ties to INT-1.

**BOOT-4 (Info — `format_version.txt` as verbatim file works).** Confirmed as a table-level verbatim
file; startup reads it fine.

---

## 5. Async inserts / buffer flush

**ASYNC-1 (Info — produce normal parts; no CAS concern).** Async inserts and Buffer-table flushes
accumulate rows in memory and flush a normal part through the standard write path. CAS sees an ordinary
part write. No async-specific storage issue. Deduplication of async-insert blocks rides the same
`deduplication_logs` path (Tier 2 DEDUP). Untested but structurally safe.

---

## 6. Configuration surface & footguns

**CFG-1 (Med — `root_shards` is a pool-wide, creation-time constant).** Set once at pool creation
(`PoolMeta::createOrValidate`); every table in the pool shares the same shard fanout. Too low → write
contention hotspots across all tables (single shard per namespace batched via flat-combining); too high →
many tiny shard objects + more GC work. **Cannot be changed after creation** — a sizing decision baked in
forever. Needs prominent documentation and a sizing guide.

**CFG-2 (Med — `server_root_id` operational uniqueness is operator-owned).** Uniqueness is enforced at
runtime by the owner anchor + mount lease (fail-closed), but the *value* is operator-configured. Two
servers accidentally sharing a `server_root_id` will contend on the mount lease (one fails closed) —
correct but a confusing outage if misconfigured. Reusing a retired `server_root_id` string for a new
server is a footgun (inherits the old owner anchor / epoch). Needs documentation.

**CFG-3 (Low — GC cadence / retention knobs interact with reclaim latency).** `gc_interval`,
`gc_snap_generations_to_keep`, manifest sweep budgets, and `dedup_cache_bytes` all tune the
reclaim/perf tradeoff. Defaults are reasonable, but LC-1 (deferred reclaim) means a long `gc_interval`
directly delays storage reclamation after DROP. Should be documented alongside the reclaim-latency
expectation.

**CFG-4 (Low — read-only disk / `gc_enabled=false` silently disables reclaim).** A read-only CA disk or
`gc_enabled=false` disables the GC scheduler entirely, so drops/mutations leak forever (LC-1). This is by
design (read replicas) but is a silent leak if set unintentionally on the writer.

---

## Summary table

| ID | Sev | Area | One-liner |
|----|-----|------|-----------|
| ENG-1 | Info | Merge engines | Special engines storage-transparent; fully supported |
| ENG-2 | Low | Merge engines | FINAL read-amp + concurrent-merge correctness unverified (MVCC-3) |
| ENG-3 | Info | Merge engines | Rollup engines produce smaller parts; better dedup |
| TXN-1 | Med | Transactions | txn_version mechanically supported (force-fresh) but experimental & untested on CAS |
| TXN-2 | Med | Transactions | Multi-part atomic commit inherits DUR1 partial-commit at txn granularity |
| TXN-3 | Low | Transactions | Rollback = drop refs, GC-deferred |
| BAK-1 | Med | Backup | BACKUP restricted to Atomic/UUID DBs; Ordinary breaks on hardlink path |
| BAK-2 | Info | Backup | FREEZE is copy-by-reference — essentially free on CAS |
| BAK-3 | Med | Backup | Incremental BACKUP dedup + empty-key mutable-file handling unverified |
| BAK-4 | Low | Backup | Full BACKUP→RESTORE→CHECK round-trip (+Packed parts) untested |
| BOOT-1 | Med | Startup | Part enumeration = S3 LIST; requires read-your-writes LIST (per-backend) |
| BOOT-2 | Med | Startup | Orphaned refs (RPL-2/LC-2) enumerate as phantom parts at startup; handling untested |
| BOOT-3 | Low | Startup | Broken-part detection depends on MergeTree checksums given INT-1 |
| BOOT-4 | Info | Startup | `format_version.txt` verbatim file works |
| ASYNC-1 | Info | Async insert | Produce normal parts; no CAS concern |
| CFG-1 | Med | Config | `root_shards` pool-wide creation-time constant; unchangeable; sizing footgun |
| CFG-2 | Med | Config | `server_root_id` uniqueness operator-owned; reuse/collision footguns |
| CFG-3 | Low | Config | GC cadence/retention knobs gate reclaim latency (LC-1) |
| CFG-4 | Low | Config | Read-only / gc_enabled=false silently disables reclaim → leaks |

## Highest-priority recommendations
1. **CFG-1/CFG-2**: publish a sizing + naming guide for `root_shards` and `server_root_id` (both are
 permanent/operational footguns).
2. **BAK-1/BAK-3**: document BACKUP limitations on CAS (Atomic-only) and add an incremental
 BACKUP→RESTORE→CHECK round-trip test.
3. **BOOT-1**: make the read-your-writes-LIST requirement explicit per backend and gate/warn on backends
 that don't guarantee it.
4. **TXN-1**: either document experimental-transactions-on-CAS as unsupported/untested or add a
 validation test.

## cas-tier4-audit.md

Language: Markdown

# CAS — Tier 4 Audit: Object-Store Compatibility, Error/Stress Handling, Observability

Environmental & hardening surfaces. Grounded in `Core/CasObjectStorageBackend.cpp`
(`checkStorePreconditions`, `nativeConditionalPut`, `finalizeConditionalWrite`, Native/Emulated modes),
`S3ObjectStorage.{h,cpp}` (`conditionalOpsUseGenerationTokens`, `isBucketVersioningEnabled`),
`Core/CasInstrumentedBackend.cpp` + `Core/CasEvent.{h,cpp}` (event sink), and `CasGcScheduler.cpp`.

---

## 1. Object-store compatibility matrix

### The core requirement
CAS's entire safety model rests on **atomic conditional writes**:
- `putIfAbsent` = create-if-absent (`If-None-Match: *`).
- `casPut` = compare-and-swap on a token (`If-Match: `).
- token-exact `deleteExact` for GC reclaim.

Two backend modes exist:
- **Native** — the condition rides on the object write's `WriteSettings`; the precondition loss surfaces
 from `finalize()` as a typed `S3Exception` (`PreconditionFailed` / `NoSuchKey` / SDK `NO_SUCH_KEY`),
 mapped to `PreconditionFailed`. **Fail-safe direction**: a misread error becomes a retryable
 conflict, never a false success.
- **Emulated (single-process/Local)** — atomicity via an in-process `emu_mutex`; for tests / local disks.

### Matrix

| Backend | Mode | Conditional write | GC-critical caveat | Test status |
|---|---|---|---|---|
| **AWS S3** | Native | `If-None-Match`/`If-Match` (S3 supports since 2024) | none known | **not end-to-end tested** (see OSC-1) |
| **GCS** (S3-compat) | Native, **generation tokens** | via generation preconditions | **bucket versioning MUST be off** (OSC-2) | gen-binding plan exists |
| **RustFS / MinIO** | Native | supported | none known | **the only end-to-end tested Native backend** |
| **Azure Blob** | — | `conditionalOpsUseGenerationTokens`/`isBucketVersioningEnabled` **not implemented** | likely unsupported for CAS | **untested / unsupported** |
| **Local filesystem** | Emulated | `emu_mutex` | single-process only | unit-test path |

### Findings

**OSC-1 (High — the Native conditional-write path is NOT end-to-end tested on real S3/GCS).** The code's
own **HONEST NOTE**: "the Native conditional-write paths are exercised end-to-end only at M-W against
RustFS; unit coverage is the Emulated mode, the typed-catch compile path, and the classifier itself." So
the *production* target (AWS S3, GCS) runs a conditional-write + error-classification path validated only
against RustFS + emulation. Any divergence in how AWS/GCS report a 412/404 (error ` ` string, SDK
enum, multipart-complete vs put) could flip a conflict into an unexpected throw or — the feared case — a
false success. The classifier is written fail-safe, but **this is the single most safety-critical
untested seam in the whole system.** Needs real-S3 and real-GCS conditional-write integration tests.

**OSC-2 (High — GCS bucket versioning silently breaks GC reclaim; only partially guarded).**
`checkStorePreconditions` refuses to mount (`NOT_IMPLEMENTED`) if it *confirms* GCS bucket versioning is
enabled, because a token-exact DELETE on a versioned bucket **archives a noncurrent generation instead of
freeing storage → GC silently stops reclaiming**. BUT if the versioning check **cannot be verified**
(permissions, unsupported), it **proceeds assuming versioning is OFF** (logged warning, not fail-closed).
So a locked-down GCS deployment with versioning actually ON but an un-queryable versioning API would
mount and **leak all reclaimable storage forever**, with only a startup WARNING. The tradeoff is
documented in-code as intentional (don't over-fail on inconclusive), but the failure mode is severe
(unbounded silent leak). Consider a config to force fail-closed on inconclusive for GCS.

**OSC-3 (Med — Azure and other non-S3 object storages are effectively unsupported for Native CAS).**
`conditionalOpsUseGenerationTokens` / `isBucketVersioningEnabled` are implemented **only in
`S3ObjectStorage`**. Azure Blob (which does support ETag/If-None-Match conditional writes) is not wired
into the CAS conditional-write contract, so a CAS pool on Azure would fall to Emulated (single-process,
unsafe for multi-node) or fail. **The supported universe is S3-family only** — worth stating explicitly
in docs. Multi-writer CAS on Azure is not available.

**OSC-4 (Med — read-your-writes LIST is a hard, per-backend assumption).** `listNamespaces` (startup part
discovery, `dropNamespace` enumeration) requires strongly-consistent read-your-writes LIST — guaranteed
on S3, "to confirm in soak" for RustFS, unstated for GCS/others. A backend with lagging LIST loses
just-committed parts at startup (BOOT-1) or under-enumerates on drop (leaving orphaned shards). Ties to
BOOT-1.

---

## 2. Error handling under stress

### How it works
Non-precondition errors (network, auth, **throttle**, corruption) **propagate unchanged — fail-closed**
(backend comment line 292). The underlying ClickHouse S3 client provides its own retry/backoff for
transient errors; CAS's own retry loops are the CAS-conflict loops (`casPut`/`mutateShard` re-read on
`PreconditionFailed`), which are distinct from network retries.

### Findings

**ERR-1 (Med — throttling/429/SlowDown storms amplify the CAS-conflict retry loop).** Under S3 request
throttling, `mutateShard`/`casPut` conflict-retries and the S3 client's network retries **compound**: a
hot shard already retrying on token conflicts, now also retrying on 429s, multiplies request volume
exactly when the store is rate-limited → potential retry storm / latency collapse. The flat-combining
queue mitigates conflict volume, but there is no CAS-level adaptive backoff on throttle (it relies on the
S3 client's). Untested under sustained 429.

**ERR-2 (Med — disk-full / quota / write failure mid-build leaves debris, reclaimed only by sweeps).** A
write that fails after uploading some blobs but before promote leaves pre-precommit blobs/manifests;
these are the "reclaimable/in-flight" debris that `CasOrphanManifestSweep` + GC clean up. Correct by
design (no dangling ref published), but a storm of failed builds (e.g. repeated OOM/disk-full) can
accumulate debris faster than sweeps clear it → transient bloat. No backpressure specific to failure
rate.

**ERR-3 (Low — partial multipart upload interrupted by crash).** A crash mid-multipart-upload leaves an
incomplete multipart upload (S3 charges for these until aborted by lifecycle policy). CAS doesn't
proactively abort orphaned MPUs; relies on a bucket lifecycle rule. Standard object-store hygiene, noted.

**ERR-4 (Info — fail-closed direction is correct).** The consistent "propagate/fail-closed" stance on
ambiguous errors (never a false success) is the right safety posture and is applied uniformly. ✅

---

## 3. Observability

### How it works
- **`CasEvent` sink** (`makeCasEventSink`) → `system.content_addressed_log`: one row per content-addressed
 decision (via `CasInstrumentedBackend`).
- **`GcRoundLogger`** (`makeGcRoundLogger`) → `system.content_addressed_garbage_collection_log`: Start /
 Finish per GC round.
- **`CasFsck`** report (physical vs logical bytes, dedup ratio, dangling count) — on demand, not a table.

### Findings

**OBS-1 (Med — no physical-storage / dedup-ratio metric surfaced continuously).** The most operationally
valuable CAS numbers (physical bytes, referenced-logical bytes, dedup ratio, dangling count) exist only
in an **on-demand fsck**, which is a full pool scan (expensive). There's no cheap continuously-exported
gauge for "physical bytes", "pending-reclaim bytes", or "dedup ratio". Operators can't cheaply answer
"how much am I actually storing / saving?" or "is GC keeping up?" without a scan. Ties to SYS-1. **Add
ProfileEvents/metrics for these.**

**OBS-2 (Med — GC health is per-round logs, not an alertable metric).** GC progress is in
`content_addressed_garbage_collection_log` rows. There is no exported "rounds since last successful
reclaim", "reclaim backlog", or "GC leader present" gauge, so a **silently stalled GC** (e.g. OSC-2 GCS
versioning, or lease starvation) is only discoverable by log-diving. Given how many findings terminate in
"GC silently stops reclaiming", a **GC-liveness metric is important**.

**OBS-3 (Low — relink vs byte-fetch not distinguished in metrics).** `system.replicated_fetches` shows
bytes; a relink transfers ~0 bytes, so relink fetches look like near-instant/zero-byte fetches with no
explicit "relinked" flag. Hard to measure relink hit-rate (which drives the RPL-4 perf story). Add a
counter.

**OBS-4 (Info — the event log is comprehensive but high-volume).** The per-decision `CasEvent` log is
excellent for debugging but can be voluminous; ensure it is sampling/level-gated in production (it is
best-effort append, context-gated). Noted.

---

## Summary table

| ID | Sev | Area | One-liner |
|----|-----|------|-----------|
| OSC-1 | High | Compat | Native conditional-write path NOT end-to-end tested on real S3/GCS (only RustFS+emu) |
| OSC-2 | High | Compat | GCS versioning breaks GC reclaim; guarded only when versioning API is queryable, else proceeds |
| OSC-3 | Med | Compat | Azure/non-S3 effectively unsupported for Native CAS (S3-family only) |
| OSC-4 | Med | Compat | Read-your-writes LIST is a hard per-backend assumption (S3 ok, others unconfirmed) |
| ERR-1 | Med | Stress | Throttle/429 storms compound with CAS-conflict retries; no CAS-level adaptive backoff |
| ERR-2 | Med | Stress | Failed-build debris reclaimed only by sweeps; failure storms cause transient bloat |
| ERR-3 | Low | Stress | Crash mid-MPU leaves incomplete uploads; relies on bucket lifecycle rule |
| ERR-4 | Info | Stress | Fail-closed-on-ambiguous is the correct posture, applied uniformly |
| OBS-1 | Med | Observability | No continuous physical/dedup/pending-reclaim metric (only expensive fsck) |
| OBS-2 | Med | Observability | GC health is logs, not an alertable liveness/backlog metric |
| OBS-3 | Low | Observability | Relink vs byte-fetch indistinguishable in fetch metrics |
| OBS-4 | Info | Observability | Per-decision event log comprehensive but high-volume; ensure gated |

## Highest-priority recommendations
1. **OSC-1**: add real-S3 and real-GCS conditional-write + error-classification integration tests — this
 is the most safety-critical untested seam.
2. **OSC-2**: offer a config to fail-closed on inconclusive GCS versioning checks (avoid silent
 unbounded leak).
3. **OBS-1/OBS-2**: export continuous metrics for physical/logical/dedup bytes, pending-reclaim, and
 GC liveness/backlog — most findings ("GC silently stops reclaiming") are undetectable today without a
 scan.
4. **OSC-3**: document the supported-backend universe (S3-family Native; Local Emulated) explicitly.

## cas-tla-fidelity-audit.md

Language: Markdown

# CAS — TLA+ Spec-to-Code Fidelity Audit

Scope: do the TLA+ models faithfully cover the implementation — and, crucially, **do the earlier
findings live inside or outside the modeled state space?** A model can be *correct* (TLC finds no
violation) yet *unfaithful* (its abstraction assumes away the very interleaving that breaks the code).
This audit maps each spec to what it proves, then locates every prior finding (J1–J3, R1/X1, W1, G-N1,
C1–C4) relative to the model boundary.

Grounded in `docs/superpowers/models/*.tla` (18 specs), with `CaCasMountCore.tla` read in full.

---

## 1. Spec inventory & methodology

| Spec | Models | Guards / invariants |
|---|---|---|
| `CaCasMountCore` | mount ownership + server-root identity + epoch | owner sticky, no foreign mount, epoch monotone-unique, superseded writer makes no mutation |
| `CaGcLeaseCore` | GC leader lease + heartbeat | single active leader, lease safety |
| `CaGcAckFloorCore` / `CaGcAckFloorZombie` | ack-floor computation + zombie leader | floor never over-advances; zombie can't under-count |
| `CaGcCore` | GC round core | no live object condemned |
| `CaGcIndegRefoldCore` | in-degree refold (three-cursor merge) | over-count-only |
| `CaB140Dangle` / `…Merge` / `…Faithful` | the B140 dangle hazard | INV_NO_DANGLE |
| `CaIncarnationCore` / `…ProofCore` / `CaGcShardIncarnationCore` | writer/shard incarnation, ABA | dead token never returns |
| `CaBuildWatermark` / `…Num` | build watermark / min-active floor | precommit not reclaimed while in-flight |
| `CaBuildRootPrecommit` | precommit→promote spine | no premature reclaim |
| `CaGcRootLocalPartManifestCore` | root-local part manifest redesign | reachability correctness |
| `CaResurrectLiveness` | revival liveness | a revived namespace eventually reclaimable |
| `Apalache` | Apalache type/stub harness | — |

**Methodology (excellent).** Two techniques stand out:
- **Sabotage constants** (`Sab*` booleans): each invariant is paired with a sabotage switch that, when
 TRUE, *reproduces the guarded-against bad state*, so TLC confirms the invariant is **load-bearing**
 (not vacuously true). E.g. `SabSupersededWrites` drops the epoch-match conjunct → TLC flags
 `SupersededWriterMakesNoMutation` violated. This proves each guard actually catches its hazard.
- **Liveness witnesses as invariants** (`W_SameUuidReclaimsExpired`): asserted so TLC reports "VIOLATED"
 when the *good* state is reachable — a reachability check.

**Coverage verdict:** the **write/GC/mount/incarnation safety core is faithfully and rigorously
modeled.** This is why that core is airtight in every prior audit — the hard invariants (no-dangle,
over-count-only, epoch monotonicity, dead-token-never-returns, single-leader) are all formally checked
*and* sabotage-validated.

---

## 2. Where the findings live relative to the model

### TLA-F1 — the atomic-fenced `Write` hides J1 (the fencing TOCTOU). **Headline.**
`CaCasMountCore.Write(a)` is a **single atomic action** whose *guard* includes the full fence:
```
Write(a) == ... /\ mount # None /\ mount.uuid = a /\ mount.deadline > clock
                /\ ~localLost[a] /\ mount.epoch = localEpoch[a]
                /\ wrote' = wrote \union {<<a, localEpoch[a]>>}
```
So in the model, checking liveness+ownership+epoch and *performing the mutation* are **indivisible** —
`SupersededWriterMakesNoMutation` holds **by construction**.

The **code does not do this atomically.** `mayMutate()` (checks `~lost && bootMsNow() < deadline`) is
evaluated at the **top of `flushShardQueue`**, and the actual `casPut(key, body, token)` happens much
later, conditioned **only on the content token/ETag — not on `writer_epoch` and not re-checking the
lease**. A writer that passes `mayMutate()`, then pauses (process freeze / VM stall) past lease expiry
while a new epoch mounts, can still land its `casPut` — a **zombie write**. This is exactly **J1**.

**The model cannot find J1 because it fused the check and the write into one step.** The abstraction is
where the fidelity breaks: the spec proves the fence *correct under the assumption that it gates the
write atomically*, an assumption the implementation violates. **This is the single most important
fidelity gap** — the formal "superseded writer makes no mutation" guarantee does **not** transfer to
the code.

### TLA-F2 — the reader is unmodeled → R1 / X1 invisible.
No spec models the read path (`resolveRef → readManifest → lookupPath → deferred blob GET`). The dangle
specs (`CaB140Dangle*`) model **GC-side** merge/reachability dangles, not a **reader-observed** dangle.
So the sole reachable cross-protocol dangle — a reader holding no pin across the deferred blob GET while
a `dropRef` + GC condemn→delete completes (R1/X1) — is **entirely outside the modeled state space**.
The formal envelope is a *writer/GC* envelope; the SELECT reader is not a first-class actor anywhere.

### TLA-F3 — a single global clock hides J3 (clock skew).
`CaCasMountCore` has one `clock` variable advanced uniformly by `Tick`; lease deadlines and expiry are
compared against that same clock. The **code uses two clocks**: wall-clock for the lease deadline
(`gc/server-roots/ /mount`) and **boot/steady-clock** for the local `mayMutate()` fence. These can
**skew** (NTP step, VM migration). The one-clock model assumes them equal, so **J3** (clock-skew reclaim
where the lease looks expired to a reclaimer while the local fence still thinks it's live, or vice
versa) is abstracted away.

### TLA-F4 — the distinct-UUID assumption excludes J2 (VM clone / split-brain).
The model declares "two server Actors (A,B), each a distinct fixed ServerUUID." The mount safety
argument leans on **UUID uniqueness**. **J2** is precisely the case where a VM clone/snapshot produces
**two live servers sharing one `server_uuid`** — which the model *assumes cannot happen*. So J2 is
outside the state space **by assumption**, not by proof. The model is faithful *given* unique UUIDs; the
deployment can break that premise.

### TLA-F5 — GC reclamation liveness (G-N1) not modeled as a checked property.
`CaResurrectLiveness` checks *revival* liveness; there is no liveness property asserting "a persistently
clamped shard does not halt reclamation pool-wide." **G-N1** (a single anomalous shard tripping
`suppress_destructive` and stalling all graduations/deletes) is an operability/liveness concern that
the safety specs, by design, don't flag (halting reclamation is *safe*, just not *live*).

### TLA-F6 — C++ concurrency / memory (C1–C4) out of scope by construction.
TLA models the **protocol**, not threads, `unique_ptr` lifetimes, destructor ordering, or atomic memory
orderings. C1 (teardown UAF / `std::terminate` race), C2/C3 (latent UAF / data race), C4 (unbounded
`shard_write_seq`) are **inherently outside** any protocol-level model. This is correct scoping, not a
defect — but it means "TLA-verified" says nothing about the C++ shutdown/lifetime hazards.

### W1 (promote-overwrite leak) — within spec, correctly not a violation.
The safety direction is `INV_OVER_COUNT_ONLY` / no-dangle (no *under*-count). A leaked manifest is an
**over-count**, which the model **permits**. So W1 being invisible to TLC is *correct* classification,
not a fidelity gap — the model faithfully allows leaks.

---

## 3. Fidelity map (summary)

| Finding | Relative to model | Why the model doesn't catch it |
|---|---|---|
| **J1** fencing TOCTOU | **Inside scope, hidden by abstraction** | `Write` fuses fence-check + mutation atomically; code splits them (content-token-only CAS) — **TLA-F1** |
| **R1/X1** read-vs-GC dangle | **Outside scope** | reader is unmodeled — **TLA-F2** |
| **J3** clock-skew reclaim | **Outside scope (abstraction)** | single global clock; code has wall+boot clocks — **TLA-F3** |
| **J2** VM-clone split-brain | **Outside scope (assumption)** | model assumes distinct ServerUUIDs — **TLA-F4** |
| **G-N1** pool-wide reclaim halt | **Outside scope (liveness)** | no reclamation-liveness property — **TLA-F5** |
| **C1–C4** C++ threading/memory | **Outside scope (by construction)** | protocol model, not implementation — **TLA-F6** |
| **W1** promote-overwrite leak | **Inside scope, permitted** | over-count is allowed by INV_OVER_COUNT_ONLY (correct) |

---

## 4. Recommendations

1. **TLA-F1 (highest value):** split `Write` into two actions — `PrepareWrite` (records that a writer
 passed `mayMutate()` at its current epoch) and `CommitWrite` (the CAS, gated **only** on the content
 token, as the code does) — and add a `SabFenceAtFlushOnly` constant. TLC will then **find J1**:
 `SupersededWriterMakesNoMutation` becomes violable because a prepared-then-superseded writer commits.
 This turns the model into a driver for the fix (carry `writer_epoch` into the shard CAS precondition,
 re-checking makes the invariant hold again).
2. **TLA-F2:** add a `Reader` actor (resolve → read-manifest → deferred blob-read as separate steps)
 and a `NoReaderObservesDeletedBlob` invariant; it will surface R1/X1 and let you validate a reader-pin
 fix.
3. **TLA-F3:** model **two clocks** (a wall clock and a per-actor boot clock with a bounded skew Δ);
 assert the fence is safe for all Δ. Reproduces J3.
4. **TLA-F4:** relax the distinct-UUID assumption (allow two actors to share a UUID) to model J2, and
 check whether mount safety still holds; if not, it motivates the fencing-token fix (which also fixes
 J1/J2 together).
5. **TLA-F5:** add a GC-reclamation-liveness witness (a clamped shard must not prevent progress on
 other shards) to surface G-N1 as a modeled liveness property.

---

## 5. Summary

**Headline.** The TLA+ suite is unusually strong *for what it covers*: 18 specs with **sabotage-constant
validation** (each invariant proven load-bearing) and **liveness witnesses**, covering the entire
write/GC/mount/incarnation **safety core** — which is exactly why that core survived every earlier
audit unscathed. The fidelity risk is **not** in what the specs prove but in the **boundary between
model and code**. The most important gap is **TLA-F1**: `CaCasMountCore.Write` fuses the fence-check and
the mutation into one atomic action, so it proves "a superseded writer makes no mutation" **by
construction** — a guarantee the implementation does **not** honor, because it checks `mayMutate()` at
flush-top and later issues a `casPut` fenced only by a content token (no `writer_epoch`). That single
abstraction is why the formal model is silent on **J1**. Beyond it, the reader is entirely unmodeled
(**TLA-F2** → R1/X1 invisible), the single-clock and distinct-UUID abstractions assume away **J3** and
**J2**, GC-reclamation liveness (**G-N1**) is unmodeled, and C++ threading/lifetime (**C1–C4**) is out
of scope by construction. W1 is correctly *permitted* (over-count is within spec). The fix is
mechanical and high-value: **de-atomize `Write` and add a reader actor + two-clock + shared-UUID
sabotage cases**, which would let TLC rediscover J1/J2/J3/R1 and validate the fencing-token remedy that
resolves most of them at once.

## cas-upgrade-compat-audit.md

Language: Markdown

# CAS — Mixed-Version / Rolling-Upgrade & On-S3 Format-Compatibility Audit

Scope: what happens when ClickHouse binaries of **different versions** share one CAS pool (rolling
upgrade, mixed cluster, downgrade), and how the **on-S3 object formats** evolve. Grounded in
`CasFormat.{h,cpp}`, `CasPoolMeta.cpp`, `CasEnvelope`, and `Proto/cas_format.proto`.

---

## 1. The format-versioning machinery (what exists)

Every persisted object carries a `CasHeader { magic, writer_version, compatibility_version }`:

- **`magic`** — 4 ASCII bytes per class (`FormatId`): `CABL` blob, `CARS` manifest shard, `CAPT` part
 manifest, `CAPM` pool meta, `CAGT` gc state, `CART` retired set, `CAOW` owner, `CAEP` epoch,
 `CAML` mount, etc. A wrong magic → `CORRUPTED_DATA`.
- **`writer_version`** — the generation of the writer (`G_BUILD`).
- **`compatibility_version`** — the **minimum reader generation** required to read this object.
- **`G_BUILD`** — the highest generation this build understands (**currently `= 1`**).

**THE reader rule** (`checkCompatibility` / `gateOnRead`):
```
if (compatibility_version > G_BUILD) throw UNKNOWN_FORMAT_VERSION;   // never misread a future object
```
Plus a **pool-level startup gate**: `PoolMeta.min_reader_generation > G_BUILD` ⇒ the binary is too old
to open the pool at all (`decodePoolMeta`).

**Change-point model** (`FormatChangePoint {generation, min_reader}`): additive change ⇒ append
`{gen, prior_min_reader}` (old readers still read new objects); breaking change ⇒ append `{gen, gen}`
(old readers refuse). A build "keeps every decoder for generations `1..G_BUILD`" (new code always reads
old).

This is a **well-designed, fail-closed forward-compat scheme.** New readers read old objects; old
readers refuse objects that declare a higher required generation rather than misparsing them.

---

## 2. The load-bearing gap: `compatibility_version` is always stamped at the writer's generation

```74:83:src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Core/CasFormat.cpp
uint32_t currentCompatibilityVersion()
{
    /// Pre-roster: stamp G_BUILD as the compatibility floor on every object written.
    return G_BUILD;
}
```

The comment names the deferral: *"the write-down-to-floor branch defers until a roster is available."*
Today `currentCompatibilityVersion()` **always returns `G_BUILD`**, i.e. every object is stamped
"requires a reader of my own generation," **even for additive changes** that older readers could in
fact parse.

**UPG1 (High, latent until the first generation bump).** The moment `G_BUILD` advances to 2 without the
write-down-to-floor (roster) logic:
- A gen-2 writer stamps `compatibility_version = 2` on **every** object it writes — blobs, shards, part
 manifests, gc/state, mounts.
- Any gen-1 reader hits `compatibility_version(2) > G_BUILD(1)` → **`UNKNOWN_FORMAT_VERSION`** on those
 objects, **even when the change was additive and the object is actually readable.**
- Because blobs/shards/manifests are **pool-global and shared**, a gen-1 node reading a gen-2 node's
 freshly-written shard/part **fails closed** → reads break for the older half of a mixed cluster.

So **rolling upgrade across a format bump is currently broken by construction**: as soon as one node
upgrades and writes anything, the not-yet-upgraded nodes can't read it. The safe-direction fail-closed
means **no corruption**, but it is a **hard availability break** for the old nodes until the whole
cluster is upgraded. The design anticipates this (the roster / write-down-to-floor mechanism) but that
mechanism is **not yet implemented** — the compat scheme is currently "big-bang upgrade only."

**Note:** pre-release, `G_BUILD = 1` for all classes and `PoolMeta.min_reader_generation = 0`, so the
gap is **latent** today. It becomes real at the first real generation increment.

---

## 3. Mixed-version scenarios

| Scenario | Behavior | Verdict |
|---|---|---|
| **Same generation, different patch** (no format change) | identical `G_BUILD`; all objects mutually readable | ✔ safe (the pre-release norm) |
| **Rolling upgrade across a gen bump** (some nodes gen-1, some gen-2, shared pool) | gen-2 writes stamp `compat=2` → gen-1 nodes get `UNKNOWN_FORMAT_VERSION` on new objects (UPG1) | ✖ **old nodes lose read access** until fully upgraded |
| **New reader, old objects** | new build keeps decoders `1..G_BUILD` → reads old objects fine | ✔ safe (forward-only) |
| **Downgrade** (gen-2 → gen-1 binary on a pool written by gen-2) | `PoolMeta.min_reader_generation` (if raised on a breaking change) blocks open; else per-object `UNKNOWN_FORMAT_VERSION` | ✔ fail-closed (no misread), but a downgrade may be **blocked/broken** |
| **Config drift** (`root_shards` / `blob_header_len` differ between nodes) | pool is **authoritative on reopen**; a node's differing config is **ignored** (`createOrValidate` returns the persisted meta) | ✔ safe — no reshard, no split |
| **Two writers different generation** both mounting one server_root | mount lease + owner anchor enforce single writer regardless of version; the loser is fenced | ✔ (version-independent) |

---

## 4. Protobuf schema evolution

`Proto/cas_format.proto` is the wire schema. Protobuf gives field-level compat **iff** the discipline
holds: only **append** fields with new tags, never renumber/repurpose/change types, keep `CasHeader`
as field 1. Two layered gates apply:
- protobuf unknown-field handling makes purely additive proto fields transparently
 forward/backward-compatible at the parse level;
- but the **`compatibility_version` gate sits on top** and can fail-closed even when protobuf could
 parse (UPG1). So the effective compat is the *stricter* of the two.

**UPG2 (Info/Low).** Retired `FormatId`s (Tree=2, GcSnap=4, Watermark=7, RootsRegistry=10,
CompletionSeal=15) were removed with the note "no on-disk compat to honor (CA pre-release)." This is
fine **only because the feature is pre-release** (no deployed pools carry those objects). Once GA, no
`FormatId` numeric value may ever be reused and no retired object shape may reappear — worth a written
guardrail, since the enum values are load-bearing identifiers.

---

## 5. Recommendations

1. **UPG1 (before GA / before any format bump):** implement the **write-down-to-floor** logic so
 additive changes stamp the *true* min-reader (`prior_min_reader` from the change-point table), not
 `G_BUILD`. Without it, every future upgrade is big-bang. Add an explicit **rolling-upgrade test**:
 two `Store`s at generation N and N+1 sharing an in-memory backend, asserting the N node still reads
 the N+1 node's additive objects.
2. **Document the upgrade contract:** until write-down-to-floor lands, state that CAS pools require
 **all nodes upgraded together** across a format generation, and that **downgrade across a breaking
 generation is unsupported** (fail-closed).
3. **UPG2:** freeze the `FormatId` enum values and retired-shape reservations with a comment/test at GA.
4. **Version skew observability:** log `writer_version`/`compatibility_version` mismatches so operators
 can see a mixed-generation pool before reads start failing.

---

## 6. Summary

| # | Finding | Severity | Reachable |
|---|---|---|---|
| UPG1 | `compatibility_version` always stamped at `G_BUILD` (no write-down-to-floor) → rolling upgrade breaks at the first format bump; old nodes fail-closed on new objects | **High** (latent) | At first gen increment |
| UPG2 | Retired `FormatId` values / shapes rely on "pre-release, nothing deployed" | Info/Low | At GA if reused |

**Headline.** The format machinery is genuinely well-built — self-describing magic + a
`compatibility_version` gate that is **fail-closed** (a reader never misparses a future object) + an
additive/breaking change-point model + a pool-level min-reader startup gate + a pool-authoritative
config so `root_shards`/`blob_header_len` drift can't split a cluster. **New-reads-old always works.**
The one material gap is that the **write-down-to-floor** half is unimplemented: `compatibility_version`
is always the writer's own generation, so the *first* format-generation bump will make a mixed-version
cluster's older nodes fail-closed on the newer nodes' (shared, pool-global) objects — i.e. **rolling
upgrade across a format change is currently big-bang-only**. It is safe (no corruption, no misread),
latent while `G_BUILD = 1`, and squarely fixable before GA by implementing the deferred roster / floor
stamping and adding a two-generation compatibility test.

## cas-write-protocol-audit.md

Language: Markdown

# CAS — Write Protocol Audit (state-space + logical fault injection)

Scope: the CAS write path — `startBuild → stageManifest → precommitAdd → putBlob → promote`, plus
`dropRef`, `republishRef` (RENAME/DETACH-ATTACH), `abandon`, and the flat-combining `mutateShard`
CAS loop. Method: build a transition table + reachable-state walk under concurrency and crash, then
overlay logical fault injection (S3 network interrupts, long delays, lost ACKs, disk, memory).

Invariants under test:
- **INV_NO_LOSS** — a committed ref is always readable.
- **INV_NO_DANGLE** — no live edge points at a deleted object.
- **INV_COMMIT_FAILCLOSED** — a non-precondition error never yields a false commit.
- **INV_OVER_COUNT_ONLY** — errors bias toward leaks (over-count), never data loss (under-count).

---

## 1. State model

State variables per in-flight write:
- `phase ∈ {building, staged, precommitted, uploaded, promoted, abandoned}`
- `manifest_body` present/absent (immutable once written)
- `blob set` admitted (content-addressed, token per incarnation)
- `precommit owner` binding present in the shard journal
- `ref[name] → manifest_ref` (committed edge), `shard_version`, `journal`
- `build_seq ∈ active_build_seqs` (watermark), `writer_epoch` (fencing token)

Key transitions:
- **stageManifest** — write immutable manifest body (orphan until precommit); no ref.
- **precommitAdd** — append precommit `new_binding` to the shard journal (GC folds +1 → shields blobs).
- **putBlob** — content-addressed conditional PUT / dedup HEAD-first; `observeAndAdmit` gates on the
 condemned-token set.
- **promote** — journal owner-check (precommit still live?) + per-blob revalidation → atomic owner move
 precommit→ref (single shard CAS).
- **abandon** — append precommit-removal event; body left for GC; retire `build_seq`.
- **mutateShard** — flat-combining batch → single conditional `casPut(key, body, token)`.

The two-phase **precommit→promote** is the crash-safety spine: a crash before promote leaves an
orphan (reclaimable), never a dangle; a crash after promote leaves a committed, readable ref.

---

## 2. Reachable-state findings

### W1 — `promote` overwrite leaks the prior committed manifest *(Med-High)*

`promote` sets `root.refs[name] = manifest_ref` **unconditionally**. When `name` already holds a
committed ref (the destination already exists), the old manifest is overwritten with **no release** of
the previous manifest to GC. Because GC reconstructs in-degree from the journal, the leaked manifest
keeps its blobs' in-degree ≥ 1 forever → **manifest + blobs leak permanently**.

**Reachability.** Not merely theoretical: `republishRef` (RENAME TABLE, DETACH/ATTACH) creates the
destination manifest then drops the source — a **crash/retry between the two** (or a lost-ACK replay)
re-runs the promote-over-existing case. So a partial RENAME leaks the pre-existing destination
manifest.

**Verdict.** INV_OVER_COUNT_ONLY-safe (leak, never dangle/loss), but a real permanent leak.
**Fix:** on overwrite, release the displaced manifest (`−old` removal event) so GC folds it.

### W2 — `abandon` retires `build_seq` before appending the precommit-removal event *(Low)*

`Build::abandon` removes `build_seq` from `active_build_seqs` (lowering the watermark) **before** it
appends the precommit-removal journal event. This opens a window where the watermark says the build is
dead while the precommit binding still names it — a fragile double-removal shape.

**Verdict.** Currently safe **only** because in-degree is a set (idempotent removal). **Fix:** retire
`build_seq` **after** the precommit-removal event is durable.

---

## 3. Logical fault injection

### W-N1 — Presence-asserting closures misreport a lost-ACK-succeeded write as failure *(Med)*

`dropRef` (and similar closures that assert the pre-state, e.g. "ref must exist") on a **lost ACK**:
the `casPut` actually committed, but the client didn't hear it; the bounded retry re-reads, finds the
ref already gone (its own committed drop), and the closure's presence assertion throws
`FILE_DOESNT_EXIST` → a **spurious failure reported for an operation that in fact succeeded.**
**Fix:** make presence-asserting closures tolerate "already in the intended post-state" as success.

### W-N2 — Lost-ACK replay double-appends journal events *(Low)*

For publish/promote, a lost ACK → retry re-applies the closure onto the freshly-read winner state and
**re-appends** the owner event → journal bloat. Set-based in-degree keeps the graph semantically
correct; only the journal grows (later trimmed). Benign but noted.

### W-N3 — Flat-combining leader convoy + batch-wide failure amplification *(Med)*

Under an S3 stall, the `mutateShard` flat-combining leader holds the batch; a single slow/failed
`casPut` fails the **whole carved batch** (all co-batched writers get the leader's error), and
followers are serialized behind the stalled leader. Correctness-safe, but a latency/availability
amplifier — one slow shard write stalls many writers.

### W-N4 — Orphaned multipart uploads and orphan manifests on interrupt/lost-ACK *(Low)*

An interrupted blob upload can leave an incomplete multipart upload; an interrupted build leaves an
ownerless (never-precommitted) manifest body. Both are reclaimed (S3 lifecycle for multipart; the
watermark/orphan sweep for manifests) → leaks, not loss.

---

## 4. Verified SAFE

- **No false commit** — a conditional PUT that returns a non-precondition error is never treated as a
 commit (INV_COMMIT_FAILCLOSED); only `Committed` advances state.
- **Content-addressed idempotency** — re-uploading identical bytes is a no-op dedup; the key = content
 binding makes retries safe.
- **Atomic conditional PUT** — the shard body is written whole (all-or-nothing); no torn/partial shard.
- **Two-phase crash safety** — crash before promote ⇒ orphan (reclaimable); crash after ⇒ committed
 readable ref. No interleaving yields a dangle.
- **Monotone epoch skip-tolerance** — `writer_epoch` may skip on crashes; all checks use equality/`>`,
 never "== previous+1", so gaps are safe.
- **Fail-closed on non-precondition errors** — network/5xx/timeout on the write path aborts the write
 rather than fabricating success.
- **promote owner-check** — replays the journal to confirm the precommit is still the live owner before
 the owner move; a reclaimed/superseded precommit fails closed (build restarts).

---

## 5. Summary

| # | Finding | Severity | Class |
|---|---|---|---|
| W1 | `promote` overwrite leaks the prior committed manifest (RENAME/lost-ACK) | **Med-High** | Leak (over-count) |
| W-N1 | Presence-asserting closure misreports lost-ACK-succeeded write as failure | Med | False-negative |
| W-N3 | Flat-combining convoy + batch-wide failure amplification under S3 stall | Med | Liveness |
| W2 | `abandon` retires `build_seq` before the precommit-removal event | Low | Fragile ordering |
| W-N2 | Lost-ACK replay double-appends journal events | Low | Journal bloat |
| W-N4 | Orphan multipart uploads / manifests on interrupt | Low | Leak |

**Headline.** The write path's safety core is airtight: the two-phase precommit→promote, content
addressing, and fail-closed conditional PUTs admit **no false commit and no dangle** under any
crash/concurrency interleaving. Every fault degrades to a **leak** (W1, W-N4 — over-count) or a
**spurious retryable error** (W-N1) or **latency** (W-N3). The one worth fixing is **W1** (promote
overwrite leak, reachable through RENAME) — a permanent, if bounded-severity, object leak.

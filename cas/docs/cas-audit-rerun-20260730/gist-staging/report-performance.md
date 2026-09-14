# cas-performance-audit — re-run 2026-07-30

Static re-verification of the performance/scale audit against current PR HEAD
(`altinity/cas-gc-rebuild`, worktree `cas-audit-20260730`). Scope: CAS-006, CAS-049,
CAS-050, CAS-053, CAS-083, CAS-086, CAS-089, CAS-100, CAS-109, CAS-116.

## Scope in current code
- Files/dirs walked:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/` (whole tree)
  - `Backend/CasRequestControl.{h,cpp}`, `Backend/CasObjectStorageBackend.cpp`
  - `Pool/CasRefLedger.{h,cpp}`, `Pool/CasManifestReader.{h,cpp}`, `Pool/CasPartWriteTxn.cpp`,
    `Pool/CasPool.{h,cpp}`, `Pool/CasBlobUploadPool.{h,cpp}`
  - `Formats/CasPartManifestFormat.{h,cpp}`, `Formats/CasFormat.cpp`
  - `Gc/CasGc.{h,cpp}`, `Gc/CasGcScheduler.{h,cpp}`
  - `Parts/PartFolderAccess.{h,cpp}`, `Parts/PartPathParser.cpp`
  - `ContentAddressedTransaction.{h,cpp}`, `ContentAddressedMetadataStorage.{h,cpp}`,
    `ContentAddressedSettings.cpp`

## Findings still present

### 🔴 CAS-006 — CAS durable publish runs synchronously per part inside the caller's lock
- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedTransaction.cpp:435` (`commit(...)`), publish loop at `:485-500`; per-part `publishStaging` at `:313`.
- Trigger: `IMergeTreeDataPart` commit calls `ContentAddressedTransaction::commit` while
  the enclosing MergeTree lock (`DataPartsLock`) is held; each part is published
  SERIALLY inside the loop, each `publishStaging` doing blob PUTs + `precommitAdd` +
  `promoteBuild`, each with retries (`CasRequestController` backoff, `CasBlobUploadPool`).
- Evidence quote (`:480-484`): *"Parts are published SERIALLY by the loop that follows;
  only the blob uploads within each part fan out (`fanOutBlobUploads`). … Concurrent
  cross-part publication is future scope and is NOT done here."*
- Notes: No async-publish path landed. S3 stall or throttling under load blocks the
  writer thread while `DataPartsLock` is held → table-wide writer/DDL stall. BC7-1..5
  root cause unchanged.

### 🔴 CAS-049 — Decode-cache eviction cliff (partially mitigated, count-cliff still latent)
- Anchor: `Pool/CasManifestReader.cpp:37-40`; setting `Pool/CasPool.h:70-78`;
  `ContentAddressedSettings.cpp:89` (`manifest_decode_cache_bytes` default `128 MiB`).
- Trigger: The manifest decode cache now has a byte budget (`128 MiB` default) AND a
  hard `max_count=16384`. The byte budget is enforced by `LRUWithSizeAndCountWeightBase`
  (LRU). But the count cap is a **hard cliff** — once 16384 entries are cached, LRU by
  count kicks in even with byte budget available; more critically, a workload with many
  tiny inline-heavy manifests hits the count cap first while the byte accounting is
  nowhere near full → the cache wholesale-evicts old entries (still LRU, but the count
  gate is a bare constant not derived from the byte budget).
- Evidence quote (`CasManifestReader.cpp:40`): `manifest_decode_cache_bytes, /*max_count=*/16384, ManifestDecodeCache::DEFAULT_SIZE_RATIO`.
- Notes: Wholesale-clear ("no LRU") behavior described in the original audit is FIXED
  (now real LRU); the residual is that the count cap is still a fixed constant with no
  per-tenant fairness, and there is no equivalent bytes+count for the **shard decode
  cache** (grep found none — the shard TTL-decoded cache lives elsewhere and was not
  refactored under this settings surface). Cliff softened, not eliminated.

### 🔴 CAS-050 — `GC REBUILD` orphan sweep does synchronous HEAD per blob, unbudgeted
- Anchor: `Gc/CasGc.cpp:2756-2769` (rebuild's `forEachListedKey` over `blobsPrefix()`
  inside `rebuildBaseline`).
- Trigger: The rebuild loops over EVERY listed blob and does `backend.head(k.key)`
  synchronously for every non-edge-bearing blob (`:2764`). No parallelism, no request
  budget, no rate limit. On a large pool (millions of blobs) this is millions of
  serial HEADs exactly at DR time.
- Evidence quote (`:2751-2770`): the loop with `const HeadResult hr = backend.head(k.key)`
  and the comment "*the rebuild is an offline/administrative path — no bounded-pool
  async model here*" (`:2776-2777`).
- Notes: Original finding fully reproduces. Also compounds with SEC-6 (rebuild
  amplification).

### 🔴 CAS-053 — Throttle/429/SlowDown storms compound with CAS-conflict retries
- Anchor: `Backend/CasRequestControl.cpp:43-62` (`classifyConditionalWriteResult`),
  `:205-244` (`backoffBeforeAttempt` / `pauseBeforeReissue`).
- Trigger: The classifier lumps `PreconditionFailed` (CAS conflict), `NoSuchKey`,
  `RequestTimeout`, `InternalError`, `ServiceUnavailable`, and `SlowDown` **all into
  the same `Unresolved` bucket** (`:46-56`). The retry loop then applies a single
  capped-exponential backoff (`retry_initial_backoff_ms`, doubling to
  `retry_max_backoff_ms`) with no distinction between "the server is telling me to
  slow down" and "a peer beat me to the CAS token". Under a throttling event, every
  in-flight writer treats its 503 identically to a CAS conflict and re-races
  immediately after backoff, so the recovering backend is hit by the same fleet the
  moment the backoff expires. There is no adaptive rate limiter, no jitter beyond
  what the shared backoff computes, no per-endpoint throttle observation.
- Evidence quote (`:46-50`): *"`PreconditionFailed`/`NoSuchKey` … any 5xx
  (InternalError/ServiceUnavailable/SlowDown/RequestTimeout), and any S3 error this
  function does not recognize all fall through to the fail-safe default below:
  Unresolved."*
- Notes: `CasPartWriteTxn.cpp:511` still admits *"a transient transport error
  (SlowDown/429/5xx) within its own budget — this outer loop reacts"* — outer retry
  loops multiply, no debounce. Original ERR-1 finding unchanged.

### 🔴 CAS-083 — Flat-combining leader convoy + batch-wide failure amplification
- Anchor: `Pool/CasRefLedger.cpp:1131-1206` (leader election + `runRefQueueLeader`
  path); `:1152-1170` (owned_items carving).
- Trigger: One per-namespace leader synchronously drives the S3 CAS on
  `roots/<shard>` for the whole owned batch. If S3 stalls, every appender queued on
  that namespace waits on the leader's single in-flight I/O (no per-item
  parallelism; leader's OWN item + carved followers all held under the same
  `leader_active` gate). A batch-level fault (`flush_exception`) is propagated to
  every owned item via `completeOwnedItemsAndReleaseLeadership` — one bad-batch
  amplifies to N reported failures.
- Evidence quote (`:1131-1146`): comment describes the leader carve; `:1178-1185`
  documents that a throw during flush is delivered to *every* owned item.
- Notes: No adaptive tenure, no fault isolation between owned items, no leader
  handoff on prolonged stall. Original W-N3 unchanged.

### 🔴 CAS-086 — `readManifest` HEAD+GET storm (partially mitigated at a higher layer)
- Anchor: HEAD+GET at `Pool/CasManifestReader.cpp:63-92` (mandatory HEAD even on
  cache hit; GET on miss); no coalescing/negative caching inside the reader itself.
- Trigger: Under throttling or a hot cold manifest, N concurrent readers each issue
  their own HEAD (mandatory, `:63-65`) and, on cache miss, their own GET. The
  reader-level cache is byte-budgeted (`:37-40`) but there is no single-flight
  around the `head()`+`get()` pair, and absence is not negatively cached
  (`FILE_DOESNT_EXIST` throws immediately with no debounce).
- Evidence quote (`:63-65`): *"`HEAD` is mandatory even on a cache hit."*
- Mitigation: `Parts/PartFolderAccess.h:381-389` adds a **`PartRefKey`-keyed
  single-flight** around `buildView` (`inflight` `shared_future` map), so
  concurrent same-key cold builders share one manifest read. This closes the
  common in-process fan-in but does NOT coalesce (a) different `PartRefKey`s that
  happen to resolve to the same `ManifestId`, (b) cross-node fan-in, or (c) the
  HEAD-even-on-hit cost on warm reads.
- Notes: Original R4/F-N4 hazard is materially reduced for same-key concurrency
  but still present for the general case; the mandatory HEAD makes even the warm
  path throttle-sensitive.

### 🔴 CAS-089 — Regular-round mass-drop delta is non-streaming (in-memory point)
- Anchor: `Gc/CasGc.cpp:1362` (`std::vector<BlobDelta> deltas;` in a regular round
  fold), `:1512` (`log_deltas`), and `:1880` (`std::vector<std::vector<BlobDelta>>
  buckets(state.gc_shards)`), all materialized whole before flush.
- Trigger: A mass-drop (`DROP TABLE`, `TRUNCATE`, large `DROP PARTITION`) produces
  one `BlobDelta` per graduated edge; the regular round accumulates the whole
  vector before routing to per-shard buckets, then flushes shard-by-shard from the
  bucket. Rebuild has been refactored to also use `flush_shard(shard)` per shard
  (`:2827`) BUT `buckets` at `:2599` is still one giant `std::vector<std::vector<BlobDelta>>`
  materialized in memory before any flush. So the regular round is still a
  non-streaming memory point on very large deltas.
- Evidence quote (`:1362`, `:2599`): explicit `std::vector<BlobDelta>` /
  `std::vector<std::vector<BlobDelta>>` accumulators; no chunked streaming
  primitive.
- Notes: Original G-N4 finding still holds. OOM risk on catastrophic drop; the
  fold's own tight loop is streaming (`:1292` comment "*fold's tight streaming
  loop*"), but the delta assembly upstream is not.

### 🔴 CAS-100 — Manifest soft-limit backpressure delays but can't prevent hard-limit wedge; no per-tenant quota
- Anchor: Manifest hard-limit at `Pool/CasPartWriteTxn.cpp:53-55`
  (`kMaxManifestEncodedBytes = 256 MiB`, `kMaxManifestInlineBytesTotal = 16 MiB`,
  `kMaxLargestInlineEntryBytes = 1 MiB`); snapshot-log soft backpressure at
  `Pool/CasPool.h:173-183` (`snapshot_log_count_threshold=256`,
  `snapshot_log_bytes_threshold=1 MiB`, `snapshot_publish_backoff_initial_ms=200`,
  `snapshot_publish_backoff_max_ms=30000`).
- Trigger: Soft-limit backoff is bounded to `snapshot_publish_backoff_max_ms=30s`
  and is per-table. It doubles on publish failure and resets on success — no
  admission control on the WRITER side once the snapshot publisher can't keep up.
  The hard cap (`kMaxManifestEncodedBytes = 256 MiB`) is a fail-closed rejection,
  not a wait-and-retry. Grep for `tenant|quota|per.*namespace.*limit|fairness`
  returns only the `CasBlobUploadPool`'s intra-uploader fairness (`CasBlobUploadPool.h:70`),
  not a per-tenant/per-namespace admission gate.
- Evidence: `Pool/CasPool.h:176-183` documents the bounded backoff; no
  cross-tenant fair-share is defined anywhere in the tree.
- Notes: Original RES-6/RES-7 unchanged. Shared-pool tenant fairness is still
  absent — one hot writer can saturate the snapshot publisher and force other
  tenants' writers to wait behind its backoff.

### 🔴 CAS-109 — System-log tables produce a tiny-part storm on CAS (untested/undocumented)
- Anchor: No CAS-specific accommodation for system-log tables. Search across the
  CAS tree for `system.*log|part_log|SystemLog` returns no CAS-side gating,
  batching, or coalescing hook. Standard MergeTree flush cadence applies, so each
  small flush = one full write path: one part manifest PUT, one shard CAS
  precommit + promote, blob PUTs, and journal churn.
- Trigger: Any high-frequency system log (`query_log`, `metric_log`,
  `part_log`, `trace_log`) on a CAS disk drives a steady stream of tiny parts, each
  triggering the full CAS-006 publish chain per commit.
- Evidence: absence of any batching primitive keyed on `SystemLog`; the manifest
  hard-limit and inline-placement (`Pool/CasPartWriteTxn.cpp:53-55`) mitigate size
  but not COUNT/RATE.
- Notes: Original G7/G9/G10/G11 finding unchanged. No `EXCHANGE TABLES` /
  `clickhouse-disks` CAS wiring found; cache-over-CAS/web-over-CAS layering also
  ungated.

## Findings fixed / no longer reproducible

### ✅ CAS-116 — `lookupPath` / `listDirectory` no longer O(entries²)
- Anchor for fix: `Formats/CasPartManifestFormat.cpp:329-336` (`findEntry`) and
  `:338-351` (`entryRange`).
- Both now use `std::lower_bound` on the sorted `entries` vector — O(log N)
  lookup and O(log N + k) range scan (instead of the old linear scan). A whole-part
  read of a wide part is now O(N log N) instead of O(N²).
- Evidence quote (`:331`): `const auto it = std::lower_bound(entries.begin(), entries.end(), path, ...)`.
- Note: the fix is `std::lower_bound` on the existing sorted vector, not a hash
  index — still cache-friendly and adequate. Original STORE-3 closed.

## New findings (not in original audit)

### NEW-perf-1 — Mandatory HEAD on every warm manifest-cache hit (throttle-sensitive warm path) *(Med)*
- Anchor: `Pool/CasManifestReader.cpp:63-65`, `:83-85`.
- Trigger: Warm manifest reads are documented as "~1 request" in the original
  audit, but the reader performs a HEAD **before** the cache lookup on every call
  ("*HEAD is mandatory even on a cache hit*") to validate the token. Under a
  read-heavy workload of hot manifests, the HEAD-per-hit is the dominant S3
  cost, not the GET. Combined with the throttle-lumping in CAS-053, a 503-storm
  wave on the warm read path is not distinguished from a CAS retry cycle.
- Note: This is either by-design (fresh-token invariant) or an unaddressed cost
  in the original scalability model — flagging for measurement. If freshness can
  be relaxed for cached hits (TTL-guarded), warm-read S3 cost drops from
  HEAD+cache to cache-only.

### NEW-perf-2 — Rebuild `writeCondemnedMeta` sweep is also unbatched *(Low-Med, DR path only)*
- Anchor: `Gc/CasGc.cpp:2783-2800`.
- Trigger: After the O(all blobs) HEAD sweep (CAS-050), the rebuild issues one
  synchronous `writeCondemnedMeta` PUT per zero-condemned blob, per shard, in a
  simple `for` loop. No parallelism, no request budget — millions of serial PUTs
  on a large pool during DR. Same class as CAS-050 but on the write side.
- Note: DR-only path but amplifies the DR blast radius.

### NEW-perf-3 — `snapshot_publish_backoff_max_ms=30s` can bound-below throttle recovery on very slow backends *(Low)*
- Anchor: `Pool/CasPool.h:182-183`.
- Trigger: Cap of 30s on snapshot publish backoff means under a prolonged
  outage/throttle, the publisher retries every 30s — potentially adding to a
  throttling storm rather than backing off further. Combined with CAS-053's
  undifferentiated retry classification, the effective throttle floor can be
  quite low.
- Note: Configurable, but the default may want tuning; noted for measurement.

## By-design / N/A / info
- **Content-hash-prefixed blob keys** (natural S3 prefix spread) still confirmed
  (`Formats/CasLayout.h` blob key shape) — no hot-prefix scalability issue.
- **Inline-placement of small files** (`kMaxLargestInlineEntryBytes = 1 MiB`,
  `Pool/CasPartWriteTxn.cpp:55`) still present — the big request-count win for
  tiny MergeTree metadata is intact.
- **`root_shards` fixed at pool creation** — see the separate CAS-056 audit; not
  a bug per se, capacity-planning constraint.
- **GC `discoverUniverse` LIST cost** (CAS-057, P4) O(namespaces × shards) —
  `Gc/CasGc.cpp:2393` `discoverUniverse` unchanged; not in this audit's scope
  (covered under its own CAS-id).

## Verdict summary table

| CAS-id  | Old severity | Status         | Evidence anchor |
|---------|--------------|----------------|-----------------|
| CAS-006 | Med (Liveness/Perf) | 🔴 still-present | `ContentAddressedTransaction.cpp:435, 485-500`; `:480-484` "serially" |
| CAS-049 | Med (Perf/Scale)    | 🟡 mitigated, residual cliff | `Pool/CasManifestReader.cpp:37-40` (bytes+count LRU; count cap = fixed 16384) |
| CAS-050 | Med (Perf/Scale)    | 🔴 still-present | `Gc/CasGc.cpp:2756-2769` per-blob synchronous HEAD; `:2776-2777` "no bounded-pool async" |
| CAS-053 | Med (Liveness)      | 🔴 still-present | `Backend/CasRequestControl.cpp:46-56` lumps 429/5xx with `PreconditionFailed` |
| CAS-083 | Med (Liveness)      | 🔴 still-present | `Pool/CasRefLedger.cpp:1131-1206` leader convoy + batch-wide failure |
| CAS-086 | Low (Perf)          | 🟡 mitigated at view layer, reader-level unchanged | `Pool/CasManifestReader.cpp:63-92`; `Parts/PartFolderAccess.h:381-389` (view single-flight) |
| CAS-089 | Med (Perf/Scale)    | 🔴 still-present | `Gc/CasGc.cpp:1362, 2599` full `vector<BlobDelta>` materialized before flush |
| CAS-100 | Med (Scale)         | 🔴 still-present | `Pool/CasPool.h:173-183` bounded per-table backoff; no per-tenant quota anywhere |
| CAS-109 | Med (Perf)          | 🔴 still-present | no CAS-side gating for `SystemLog`; standard write path per flush |
| CAS-116 | Med (Perf/Scale)    | ✅ fixed | `Formats/CasPartManifestFormat.cpp:329-336, 338-351` `std::lower_bound` |

### Counts

- Findings still present: **8** (CAS-006, CAS-050, CAS-053, CAS-083, CAS-089, CAS-100, CAS-109, plus CAS-053-adjacent CAS-086 general path)
- Findings mitigated (residual): **2** (CAS-049 wholesale-clear→LRU; CAS-086 view-layer single-flight)
- Findings fixed: **1** (CAS-116)
- New findings: **3** (NEW-perf-1 mandatory HEAD on warm hit; NEW-perf-2 rebuild write-side unbatched; NEW-perf-3 snapshot backoff cap)

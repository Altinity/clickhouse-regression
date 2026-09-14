# ad5-resource-exhaustion — re-run 2026-07-30

Re-verifies AD-5 (RES-1..RES-8 / `CAS-008, CAS-049, CAS-084, CAS-092, CAS-100`) against the current PR code at `/Volumes/workspace/ClickHouse` (branch `cas-audit-20260730`). Original AD-5 was grounded in a `CasStore.h` / `CasStore.cpp` root-shard model with a 16 MiB soft / 64 MiB hard **encoded root-shard body** limit, per-flush backpressure delay ≤ 1 s, a 16384-entry **wholesale-clear** shard/manifest decode cache, and a `shard_write_seq` map per (namespace, shard). **None of those symbols exist in the current tree** — the root-shard/journal write-availability model has been replaced by a per-namespace ref-ledger (`CasRefLedger`) with a hard-sized ref-log txn cap (`ref_txn_max_bytes = 20 MiB`) and a hard-sized ref-snapshot / removal cap (`ref_snapshot_max_bytes = ref_removal_max_bytes = 64 MiB`), plus a manifest **decode cache with real LRU eviction** and a global **ref-table cache with LRU eviction** (`ref_table_cache_bytes = 256 MiB`).

## Scope in current code

- Files/dirs walked:
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPartWriteTxn.cpp` (backpressure caps in `stageManifest`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasPool.h`, `CasPool.cpp` (`dedup_cache_bytes`, `manifest_decode_cache_bytes`, `ref_table_cache_bytes`, `snapshot_log_bytes_threshold`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.h`, `CasManifestReader.cpp` (manifest decode cache: LRU, byte-budgeted, `max_count=16384`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.h`, `CasRefLedger.cpp` (`enforceRefTableCacheBudget`, per-table budgets, `dropNamespace`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefProtocol.h` (`ref_table_cache_bytes`, `snapshot_log_bytes_threshold`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasRefLogFormat.h` (`ref_txn_max_bytes`, `ref_removal_max_bytes`, `ref_op_max_bytes`, `ref_txn_max_ops`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasRefSnapshotFormat.h` (`ref_snapshot_max_bytes`)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasFormat.cpp` (`RefLog` / `RefSnapshot` 64 MiB decompressed decode ceilings)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedSettings.cpp` (setting defaults)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp` (multipart handling; no MPU abort)
  - `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Gc/CasGc.{h,cpp}` (`root_shards` = discovered namespace universe, not a pool-wide parallelism fanout)

## Findings still present

### `CAS-008` / RES-1 — 🔴 **Reshaped, still present.** Ref-log admission caps can wedge writes to a namespace under sustained churn, keeping the write-availability↔GC-progress coupling alive (in a new shape).

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Formats/CasRefLogFormat.h:68-79` (`ref_txn_max_ops = 5000`, `ref_txn_max_bytes = 20 MiB`, `ref_removal_max_bytes = 64 MiB`, `ref_op_max_bytes = 4096`) and `Pool/CasRefLedger.cpp:572-577` (`snapshot_budget`, `removal_budget`, `kRefAdmissionSafetyMargin`)
- Trigger: high mutation rate on a single ref table (one namespace = one CAS table). A normal-class ref-log transaction is capped at 20 MiB and 5000 ops; complete-table admission for the snapshot / removal path is capped at 64 MiB. If the working set of committed rows + precommits + ops does not compact fast enough (snapshot publish latency governed by `snapshot_log_bytes_threshold = 1 MiB` in `CasPool.h:174` plus per-table LRU eviction of the base state), an operator hitting the removal-class 64 MiB ceiling triggers `LIMIT_EXCEEDED` in `stageManifest` / append paths.
- Evidence quote (`Formats/CasRefLogFormat.h`):
  > "Normal transactions have an operation-count limit, a byte limit, and a per-op size limit. A transaction containing `RemoveNamespace` is 'removal-class': it shares the larger complete-table byte budget and has neither a separate operation-count cap nor a per-op cap … `ref_txn_max_bytes = 20 * 1024 * 1024; ref_removal_max_bytes = 64 * 1024 * 1024;`"
- Notes: **The 64 MiB is no longer per-(namespace, root-shard) encoded body of a journal that can only be trimmed by GC**; it is a per-namespace snapshot / removal byte budget. The RES-1 shape ("hot table wedges at hard limit because GC is not folding fast enough") is much smaller under this model — snapshot compaction happens inside `CasRefLedger` on the append lane, not on `CasGc` — but it is not zero. In particular, `enforceRefTableCacheBudget` (`Pool/CasRefLedger.cpp:762-810`) can evict a hot table's state under pool-wide memory pressure and force re-hydration from the ref log; a large tail of unpublished ops between snapshots interacting with the removal / snapshot 64 MiB byte cap is the residual liveness risk. Sev downgraded from High → Med.

### `CAS-092` / RES-4 — ✅ **fixed / no longer reproducible.** `shard_write_seq` is gone; per-namespace state is under LRU.

- Anchor for the fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.cpp:762-810` (`enforceRefTableCacheBudget`), `Pool/CasPool.h:204` (`ref_table_cache_bytes = 256ULL << 20`).
- Grep for `shard_write_seq` / `writeSeq` / `WriteSeq` across the CAS tree returns zero matches; the per-(namespace, shard) monotonic map the original audit called out (CAS-092) does not exist in the current design. Long-lived state per namespace is instead the cached `RefTableState`, which is bounded by `ref_table_cache_bytes` and evicted LRU (`enforceRefTableCacheBudget`). Verdict: **fixed** in the sense that the specific leak shape flagged in the original AD-5 (RES-4) is no longer reachable in this code.

### `CAS-049` / RES-3 — ✅ **fixed / no longer reproducible.** Decode caches are LRU with a byte budget; no wholesale-clear cliff at 16384.

- Anchor for the fix: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasManifestReader.cpp:37-40`:
  > `manifest_cache = std::make_unique<ManifestDecodeCache>("LRU", …, manifest_decode_cache_bytes, /*max_count=*/16384, ManifestDecodeCache::DEFAULT_SIZE_RATIO);`
  Default byte budget `manifest_decode_cache_bytes = 128 MiB` (`Pool/CasPool.h:78`). The 16384 is now a **count cap on the LRU policy**, not a wholesale-clear trigger.
- The original CAS-049's "shard decode cache" no longer exists as a separately-managed 16384-entry table; the manifest decode cache is byte-budgeted with proper LRU eviction. The dedup known-present cache continues to use `CacheBase` LRU (`Pool/CasPool.cpp:208-211`).

### `CAS-100` / RES-6 & RES-7 — 🔴 **still present (RES-7); RES-6 no longer applicable in its 1 s / per-flush form.**

- RES-6 anchor: the current write path has **no** `manifest_soft_limit` / `manifest_max_delay_ms` linear backpressure. `stageManifest` (`Pool/CasPartWriteTxn.cpp:824-872`) is **hard fail-closed only** — `LIMIT_EXCEEDED` when entries / inline-total / manifest-ordinal / encoded-manifest caps are exceeded (`kMaxManifestEntries = 1_048_576`, `kMaxManifestInlineBytesTotal = 16 MiB`, `kMaxLargestInlineEntryBytes = 1 MiB`, `kMaxManifestEncodedBytes = 256 MiB`). The "shock absorber" the original audit worried was too small (≤ 1 s) has been **removed rather than fixed**; the write path now throws immediately on the caps and relies on the caller / ref-ledger append lane for smoothing (see NEW-1 below).
- RES-7 anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Pool/CasRefLedger.cpp:1208` (`Fairness baton pass`) is per-flush fairness inside one table's queue; and `Pool/CasBlobUploadPool.h:54` (`Fairness rule: overweight (exclusive) acquirers take PRIORITY over normal acquirers`) is intra-pool fairness across weight classes. There is **no per-`server_root_id` / per-tenant quota on ref-log bytes, blob bytes, namespace count, or on-disk footprint** in a shared CAS pool. Grep for `quota` / `per_tenant` / `per_server_root` across the tree returns zero matches. A runaway tenant can still consume pool storage and inflate everyone's LIST / GC cost.
- Verdict: **RES-7 still-present**, unchanged in substance from the original audit.

### `CAS-084` / orphan MPUs — 🔴 **still present.** CAS backend still neither aborts in-flight multipart uploads nor lists / reports them.

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/Backend/CasObjectStorageBackend.cpp` (only reference to multipart is a note that GCS `checkStorePreconditions` forces single-PUT for conditional writes; grep for `abortMultipart` / `AbortMultipart` / `removeIncompleteMultipart` / `abort_multipart` across the CAS tree returns zero matches).
- Trigger: any interrupted upload (crash, kill, S3 retry giving up mid-multipart) leaves an incomplete MPU in the bucket. CAS is unaware and there is no code path to reclaim it or surface it. Reclamation still depends entirely on an operator-configured `AbortIncompleteMultipartUpload` bucket lifecycle rule (which the AD-6 safe-bucket contract classifies as "the one lifecycle rule that IS safe/helpful"), and no `CasFsck` / `CasDecommission` step lists / accounts for them either.
- Verdict: **still-present**; severity unchanged from the original AD-5 finding (LEAK / DAY2).

## Findings fixed / no longer reproducible

- `CAS-049` / RES-3 — decode cache wholesale-clear cliff. Fixed by switching to LRU with a byte budget + count cap: `Pool/CasManifestReader.cpp:37-40`.
- `CAS-092` / RES-4 — `shard_write_seq` unbounded growth on `dropNamespace`. Fixed structurally: the map is gone; long-lived per-namespace state is the LRU-evictable `RefTableState` under `ref_table_cache_bytes` (`Pool/CasRefLedger.cpp:762-810`, `Pool/CasPool.h:204`).
- RES-6 in its original 1 s / per-flush shape — removed; write path is hard fail-closed only (see NEW-1 for the replacement concern).

## New findings (not in original audit)

- **NEW-ad5-1 (Med — the manifest write path is hard fail-closed only; no smoothing at all near the caps).** `Pool/CasPartWriteTxn.cpp:824-872` enforces `kMaxManifestEntries = 1_048_576`, `kMaxManifestInlineBytesTotal = 16 MiB`, `kMaxLargestInlineEntryBytes = 1 MiB`, `kMaxManifestEncodedBytes = 256 MiB` as unconditional `LIMIT_EXCEEDED` throws. The original AD-5 recommended a governor + surfaced distance-to-hard-limit metric so an operator could see the wedge coming; the current design has **neither** the ≤ 1 s soft-limit backpressure nor a "distance-to-cap" metric. Under sustained churn, the first sign of trouble is a failed write, not a warned-and-throttled one. Severity: Med (scalability / DoS ergonomics).
  - Anchor: `Pool/CasPartWriteTxn.cpp:824-872` (`stageManifest`) — no soft-limit path; `Pool/CasPool.h:174` (`snapshot_log_bytes_threshold = 1 MiB`) is a snapshot-publish trigger, not a mutation-side warning.

- **NEW-ad5-2 (Low — `enforceRefTableCacheBudget` LRU-evicts a namespace's cached state; a hot table churning enough to force re-hydration under memory pressure pays repeated recovery cost.)** `Pool/CasRefLedger.cpp:762-810` walks all cached tables and evicts the LRU non-`keep_ns` entries until the total is ≤ `ref_table_cache_bytes` (default 256 MiB, `Pool/CasPool.h:204`). At extreme multi-tenancy (many active namespaces, each with large committed / owned_manifests state), this can become a re-recovery hot loop: table evicted → next touch triggers `stateFromSnapshot` + tail replay + `materializeCommitted` (`Pool/CasRefLedger.cpp:560-577`), which is O(N) per table. Not a leak, but a soft scale cliff distinct from the original RES-3.
  - Anchor: `Pool/CasRefLedger.cpp:762-810` (eviction loop) + `560-577` (materialize cost).

- **NEW-ad5-3 (Low — `RefLog` / `RefSnapshot` seal-decode ceilings are 64 MiB decompressed, and this is enforced at decode, but the encode-side complete-table admission uses the same 64 MiB budget with only `kRefAdmissionSafetyMargin` headroom, i.e. essentially zero real slack.)** `Formats/CasFormat.cpp:98-99` gives the RefLog and RefSnapshot 64 MiB decompressed decode ceilings; `Pool/CasRefLedger.cpp:572-577` pre-subtracts `4 + ns.size() + kRefAdmissionSafetyMargin` and clamps to zero. A namespace with a very long name plus a snapshot right at the budget can be admissible on the encode side yet fail at decode on the next mount if any per-field overhead grew after encode (e.g., codec change bumping framing). Belt-and-suspenders concern, low severity, but worth logging because the encode / decode budgets are the exact same number.
  - Anchor: `Formats/CasFormat.cpp:98-99` + `Formats/CasRefSnapshotFormat.h:67` (`ref_snapshot_max_bytes = ref_removal_max_bytes`) + `Pool/CasRefLedger.cpp:572-577`.

## By-design / N/A / info

- RES-2 (`root_shards` as a fixed pool-wide parallelism ceiling) — **N/A in current code.** `root_shards` in the current tree (`Gc/CasGc.h:341`, `Gc/CasGc.cpp:1060`) is the *discovered universe of namespaces* enumerated by `discoverUniverse`, not a static fanout set at pool creation. Grep for the original `root_shards` sizing knob turns up no configurable pool-wide parallelism cap; per-namespace writes fan out through the ref lane's leader / follower discipline (see `CasRefLedger.cpp` around lines 1650-2050). The specific concern in the original RES-2 (permanent, unforgiving sizing decision) is gone with the design.
- RES-5 (LIST / HEAD cost scales with namespace / blob count) — **still true, but not CAS-code-anchored.** `Tools/CasFsck.cpp:314`, `Tools/CasDecommission.cpp:116-131`, and `Pool/CasPool.cpp:1321` all use `listNamespaces` for full-scan discovery; no sharded / parallel LIST. Behavioral, not a defect anchor per se — noted for completeness.
- RES-8 (blob-level scaling is S3-native and fine) — unchanged; ⚪ info.
- The manifest decode cache still uses `max_count = 16384` (`Pool/CasManifestReader.cpp:40`), but as a count cap **on top of** LRU eviction. Not a cliff.

## Verdict summary table

| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-008 (RES-1) | High | 🔴 still-present (reshaped, Med) — ref-log / snapshot 64 MiB caps replace the root-shard journal 64 MiB cap; write availability still coupled to admission-budget compaction / eviction. | `Formats/CasRefLogFormat.h:68-79`, `Pool/CasRefLedger.cpp:572-577`, `Pool/CasPartWriteTxn.cpp:824-872` |
| CAS-049 (RES-3) | Med | ✅ fixed — decode cache is byte-budgeted LRU (not wholesale-clear). | `Pool/CasManifestReader.cpp:37-40`, `Pool/CasPool.h:78` |
| CAS-084 (orphan MPU) | Med (LEAK/DAY2) | 🔴 still-present — CAS backend still does not abort / list / report incomplete multipart uploads. | `Backend/CasObjectStorageBackend.cpp` (no `abortMultipart*` symbol anywhere in CAS tree) |
| CAS-092 (RES-4) | Med | ✅ fixed — `shard_write_seq` symbol removed; per-namespace state is LRU-bounded. | `Pool/CasRefLedger.cpp:762-810`, `Pool/CasPool.h:204` |
| CAS-100 (RES-6, RES-7) | Low / Low | 🔴 RES-7 still-present (no per-tenant quota in shared pool); RES-6 removed in original shape but replaced by hard fail-closed only writes (see NEW-ad5-1). | `Pool/CasRefLedger.cpp:1208`, `Pool/CasBlobUploadPool.h:54`, `Pool/CasPartWriteTxn.cpp:824-872` |
| NEW-ad5-1 | — | 🛠 new (Med) — write path is hard fail-closed with no soft-limit / no distance-to-cap metric. | `Pool/CasPartWriteTxn.cpp:824-872` |
| NEW-ad5-2 | — | ⚪ new (Low) — LRU eviction of `RefTableState` under memory pressure can force repeated O(N) re-hydration at extreme multi-tenancy. | `Pool/CasRefLedger.cpp:560-577`, `Pool/CasRefLedger.cpp:762-810` |
| NEW-ad5-3 | — | ⚪ new (Low) — RefLog / RefSnapshot encode admission budget == decode ceiling (64 MiB) with only a nominal safety margin. | `Formats/CasFormat.cpp:98-99`, `Formats/CasRefSnapshotFormat.h:67`, `Pool/CasRefLedger.cpp:572-577` |

**Counts:** 5 original findings audited (CAS-008, CAS-049, CAS-084, CAS-092, CAS-100) → 3 still-present (CAS-008 reshaped + downgraded, CAS-084 unchanged, CAS-100 RES-7 only); 2 fixed (CAS-049, CAS-092); 3 new findings (NEW-ad5-1 Med, NEW-ad5-2 Low, NEW-ad5-3 Low).

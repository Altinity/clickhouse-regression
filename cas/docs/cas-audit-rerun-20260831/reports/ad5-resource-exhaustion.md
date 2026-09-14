# ad5-resource-exhaustion -- fresh audit 2026-08-31

## Scope
- Files/dirs examined: `Gc/CasGc.cpp` (fold `deltas`, `gc_shards` buckets); `Formats/CasTextFormat.cpp` (`openObject`); `Formats/CasFormat.cpp` (object caps); `Formats/CasRefLogFormat.h:100` / `CasRefSnapshotFormat.h:65` (64 MiB); `Pool/CasRefLedger.cpp` (`enforceRefTableCacheBudget`, `CasRefCatalog::read` on positive append, recovery epoch-seal loop); `Parts/PartFolderAccess.cpp` (view weight); `ContentAddressedSettings.cpp` (`cas_gc_shards`); `Pool/CasPool.cpp:504` (shards overwrite); `Pool/CasPool.h` (`ref_table_cache_bytes`).
- Explicitly out of scope: local scratch uncapped (bc2 / CAS-046); blob-upload pool blocking (performance).

## Findings
### ad5-1 -- GC fold intake still materializes an unbounded in-memory delta vector (Medium)
- Anchor: `Gc/CasGc.cpp:1791` (`std::vector<BlobDelta> deltas`); `:1222` / `:2472` (push per manifest edge); `:3044` (per-shard copies when `gc_shards > 1`); no intake budget on `logs_applied` (`:1807`, `:2488`).
- Trigger: GC leader gap, `cas_gc_enabled=false` then re-enable, or commit rate above cleanup. The next folding round absorbs the backlog.
- Evidence: wired budgets (`cas_gc_round_*`) cap output (graduate/redelete/sweep), not GET/decode/delta intake. `rebuild_edge_budget` exists only on rebuild. Peak is the delta vector plus `stable_sort`. Fail-closed is process OOM, not a loud admission error. Scale/cost; not silent corruption.
- Notes: CAS-035.

### ad5-2 -- `Backend::get` materializes the control object before `object_cap` is checked (Low)
- Anchor: `Backend/CasObjectStorageBackend.cpp:565-601` (`nativeHead` then `readObjectRanged` into `gr.bytes`); `Formats/CasTextFormat.cpp:384-403` (`openObject` checks `object_cap` on the already-buffered `stored`).
- Trigger: a trusted bucket principal writes an oversized zstd/control object under a CAS key.
- Evidence: the cap throws `CORRUPTED_DATA` after the GET. The holder of the bucket credential is the trust boundary. Loud refusal. Transient allocation equals the object size.
- Notes: CAS-036 residual.

### ad5-3 -- `cas_gc_shards` has no upper bound; a local value is silently replaced by `_pool_meta` (Low)
- Anchor: `ContentAddressedSettings.cpp:226-229` (`>= 1` only); `Pool/CasPool.cpp:504` (`config.gc_shards = meta.gc_shards`); `Gc/CasGc.cpp:3044-3051` (one vector-of-vectors of size `gc_shards`); `docs/en/antalya/cas/configuration.md:96` (claims mismatch is refused — that is false).
- Trigger: first mounter records a huge `cas_gc_shards`, or a later node sets 8 and the pool already has 1.
- Evidence: create-time value is stored; later configs are overwritten with no log. A huge value fails closed on allocation. Docs disagree with code.
- Notes: CAS-039 residual.

### ad5-4 -- per-namespace 64 MiB snapshot/removal cap permanently refuses further writes (Medium)
- Anchor: `Formats/CasRefLogFormat.h:100` (`ref_removal_max_bytes = 64 MiB`); `Formats/CasRefSnapshotFormat.h:65`; admission in `CasRefLedger` / `CasRefProtocol` (`LIMIT_EXCEEDED` before any object).
- Trigger: one table accumulating ~0.5–0.9M committed refs.
- Evidence: loud, pre-write, non-retryable. Recovery is DROP parts. No approaching-cap metric.
- Notes: CAS-111.

### ad5-5 -- every positive ref-log append re-GETs the whole `ref_catalog` (Medium)
- Anchor: `Pool/CasRefLedger.cpp:3315-3320` (`positive_append` → `CasRefCatalog::read`); linear `find_if` over entries.
- Trigger: ordinary part commit (precommit + commit each take this path when the chunk is a positive append).
- Evidence: no catalog cache. Cost scales with namespace count, not with the table being written. Correctness is the point of the re-read (Removing race). Residual is request amplification.
- Notes: CAS-112 residual.

### ad5-6 -- recovery still writes one durable epoch-seal per skipped writer epoch (Medium)
- Anchor: `Pool/CasRefLedger.cpp:1074-1150` (dead epoch, unclosed → `makeEpochSealTxn` + `slotOccupy` + `publish_recovered_frontier`); loop `++epoch` until `epoch >= live_epoch` (`:1074`).
- Trigger: first touch of a long-idle table after many remounts (writer_epoch is pool-wide, seal chain is per namespace).
- Evidence: each skipped epoch is a seal PUT plus a checkpoint publish. Protocol forces per-epoch occupancy; the step's cost is unbounded in mount count. Loud and correct; availability/latency on first access.
- Notes: CAS-114.

### ad5-7 -- part-folder cache weight is still 256 bytes because both `Resolved` producers hardcode `manifest_size = 0` (Medium)
- Anchor: `Pool/CasRefLedger.cpp:349-353` and `:381-385` (`manifest_size = 0`); `Parts/PartFolderAccess.cpp:138-140` (`return 256 + manifest_size`).
- Trigger: default `cas_part_folder_cache_bytes` / `cas_part_folder_cache_max_entry_bytes`.
- Evidence: the byte budget and oversized-bypass threshold never see a real manifest size. Entry-count cap (`cas_part_folder_cache_max_entries`, default 10_000) still bounds cardinality. Memory can exceed the advertised byte budget by the size of cached views.
- Notes: CAS-045.

## By-design / info / non-actionable
- `enforceRefTableCacheBudget` now runs after a newly materialized table (`CasRefLedger.cpp:1612-1616`), not only as a named recovery helper. It still cannot evict `use_count() != 1` / leader / pending tables, so concurrent writers pin the 256 MiB encoded-byte budget. Soft ceiling; correctness unaffected (CAS-053 residual).
- Dedup presence cache / constant-64 `DedupWeight` is gone. `ensureBlobPresent` always HEADs. Closes previous ad5-6.
- Write availability is not coupled to GC liveness: the 64 MiB cap is a ref-table encoder budget.

## Closed-since-2026-08-12
- Dedup cache under-count (previous ad5-6 / CAS-115 half): symbol gone after the HEAD-then-publish rewrite.
- "Budget enforced only at recovery" as a sole call site: a post-materialize call exists (`:1616`). Residual is in-use skip, not a missing call.

## Coverage
- Reviewed: GC fold memory; control-object cap order; gc_shards bound/override; 64 MiB ref cap; catalog GET; recovery epoch seals; part-folder weights; ref-table cache enforcement site.
- N-A: runtime RSS measurement.
- Deferred: blob-upload pool (performance).

# Hybrid Table Engine — Testing Matrix & Suite Plan

**Status:** living plan (revamp in progress)  
**Suite home:** `iceberg/tests/hybrid`  
**ALIAS matrix:** `alias_testing_matrix.md` / `hybrid_alias/` (separate Feature)  

This document is the master plan for a robust Hybrid regression suite. It
merges engine docs, product architecture, Distributed execution branches, and
the end-to-end Antalya cold-tier story into one implementable matrix.

---

## 0. Sources of truth

| Source | What it contributes |
|--------|---------------------|
| `iceberg/requirements/hybrid.md` | **SRS-048** — Hybrid engine semantics as `RQ.ClickHouse.Hybrid.*` SHALL requirements (paired with `hybrid.py` + `@Requirements` on suite Features) |
| [Altinity blog — Hybrid Tables](https://altinity.com/blog/introducing-hybrid-tables-transparent-query-on-clickhouse-mergetree-and-iceberg-data) | Why Hybrid exists; VIEW/Merge failures; hot/cold + EXPORT PART; type seams; swarm; Antalya-only |
| [RFC gist — Hybrid MergeTree ↔ Iceberg E2E](https://gist.github.com/filimonov/a2bf4f2758de421c569ba8af898b656e) | Full pipeline design context; failure modes; schema validation track. **Ignore TTL EXPORT and named-scalar pieces for now** (not implemented) |
| [`hybrid_additional_notes.md`](./hybrid_additional_notes.md) | Distributed path branches; suite relocation; extend query fuzzing with upstream queries |
| Existing suite under `iceberg/tests/hybrid` | Baseline after Phase 0 move (mostly ALIAS on MT↔MT + smoke) |

**Product framing (blog + RFC):** Hybrid is a `Distributed`-shaped head that
fans one logical query across *different* backends with per-segment predicates
(“watermarks”). The flagship use case is hot `ReplicatedMergeTree` + cold
Iceberg/Parquet, with INSERT always hitting the first segment.

**Why not VIEW / Merge (must not regress into these):**

- VIEW + `UNION ALL`: type-supertype failures (`UInt64` vs `Int64` →
  `NO_COMMON_TYPE`); aggregations not pushed into subqueries.
- `Merge` + `_table` filter: no pushdown of agg / LIMIT / projections →
  severe analytical regression.
- Hybrid must preserve Distributed pushdowns (conditions, aggregations,
  limits, joins) across heterogeneous segments.

---

## 1. Suite placement and ownership

| Item | Choice | Rationale |
|------|--------|-----------|
| Home suite | **`iceberg/`** | Flagship path is MT + Iceberg; catalogs, Iceberg engine, EXPORT PARTITION, swarm helpers already live here |
| Module path | `iceberg/tests/hybrid/` | Mirrors other iceberg features; wire from `iceberg/regression.py` |
| Requirements | **`iceberg/requirements/hybrid.md`** | Shared iceberg requirements path |
| Steps | `iceberg/tests/steps/hybrid.py` (new) | Replace thin `ice/steps/hybrid.py`; reuse iceberg + export helpers |
| ALIAS | Keep all modules; **separate Feature** | Runtime control independent of core Hybrid engine tests |
| First segment form | Always `cluster(...)` or `remote(...)` (etc.) | Engine requires a Distributed-instantiating table function |
| `ice/` role after move | Ice tool / EXPORT PART CLI only | May call hybrid helpers for ice-specific workflows; must not own the engine suite |

**Dependency on sibling suites (do not re-implement):**

- `iceberg/tests/export_partition/` — EXPORT PARTITION correctness, catalogs,
  casting, truncate, ZK coordination.
- `iceberg/tests/iceberg_engine/` — Iceberg table engine, swarm /
  `object_storage_cluster`.
- ALIAS suite — expression coverage; remains a Hybrid *feature* folder, not
  the general engine matrix.

---

## 2. Current coverage baseline (as of revamp start)

| Area | State | Notes |
|------|-------|-------|
| ALIAS columns on `remote(MT)` + `remote(MT)` | **Large** (~276 modules) | Expression matrix; date / alias watermarks; some query_context |
| Smoke create + SELECT | **Done (Phase 0)** | `smoke.py` — `remote()` first segment |
| Dropped segment + restart | **Disabled** | `hybrid_dropped_segment_repro.py` (#1347); commented out in `feature.py` |
| MergeTree + `icebergCluster` query fuzzing | **Phase 4** | `fuzzing/hybrid_queries.py` + SQL; upstream-derived additive |
| EXPORT → watermark / Distributed replace | **Phase 3** | `lifecycle/export_then_watermark.py`, `lifecycle/replace_distributed_head.py` |
| Topology DoD (remoteSecure / 3-seg / Dist²) | **Phase 4** | `core/topology.py` |
| Schema variety / ops / PyIceberg interop | **Phase 5** | `schema/variety.py`, `operational.py`, `external_reader.py` |
| Named-scalar dynamic watermark | **Out of scope** | Planned in RFC only — **not implemented**; ignore for now |
| TTL `EXPORT TO` | **Out of scope** | Pretend it does not exist; do not sketch or scaffold |
| Upstream query fuzzing | **Not started** | **Additional** fuzz coverage from upstream stateless/stateful/integration; does not replace existing Hybrid fuzz SQL |

---

## 3. Architecture under test (layers)

Test the stack as three layers. Lower layers gate upper ones.

```
L1  Hybrid engine core (Distributed fan-out + predicates)
      segments, DDL, INSERT routing, static watermarks, query shapes,
      Distributed execution branches

L2  Heterogeneous storage (MT ↔ Iceberg / S3 / icebergCluster)
      type alignment, auto-cast, object_storage_cluster, catalogs

L3  Operational watermark lifecycle
      CREATE OR REPLACE; EXPORT PARTITION then advance static watermark;
      Hybrid replaces Distributed; overlap window (manual delete only after W moves)
```

**Out of scope for this suite (RFC future only — do not implement or stub):**

- `SHARED NAMED SCALAR` / dynamic watermark (planned, not in product yet)
- `TTL … EXPORT TO` (pretend absent)

**RFC / product component status (what we do use):**

| Component | Status | Suite implication |
|-----------|--------|-------------------|
| Hybrid engine | Shipped (experimental) | L1–L2 primary work |
| EXPORT PART / PARTITION | Shipped (experimental); covered heavily in `export_partition` | Hybrid suite *consumes* it for L3, does not re-test exporter internals |
| Iceberg mirror (`AS mt ENGINE = Iceberg…`) | Shipped; hardening incomplete | Hybrid L2/L3 must include schema variety + round-trip |

---

## 4. Required and execution settings

### 4.1 Hard requirements

| Setting | Value | Notes |
|---------|-------|-------|
| `allow_experimental_hybrid_table` | `1` | CREATE TABLE gate |
| `enable_analyzer` | `1` | **Only** supported analyzer mode for Hybrid |

Also enable as needed by segment type:

| Setting | When |
|---------|------|
| `allow_experimental_insert_into_iceberg` | Iceberg writes / mirrors |
| `allow_experimental_export_merge_tree_part` / partition feature | L3 EXPORT → watermark flows |
| Swarm / object storage cluster settings | Iceberg + swarm segments |

### 4.2 Execution-path settings (must combinatorial-cover)

These are independent code paths. Bugs often appear only at merge of local
vs remote results (notes + `hybrid.md`).

| Setting | Values | Effect |
|---------|--------|--------|
| `prefer_localhost_replica` | `1` (default), `0` | `0` forces local shard through remote path |
| `serialize_query_plan` | `0` (default), `1` | SQL subquery vs JSON plan fragment to remotes; `1` likely future default |
| `hybrid_table_auto_cast_columns` | `0` (default), `1` | Auto CAST at segment boundary; needs analyzer |
| `skip_unused_shards` | on / off | Predicate pruning / unused segment skip |
| `object_storage_cluster_join_mode` | default / `'local'` | JOINs involving object-storage segments |

### 4.3 Distributed subquery stages (SQL-to-shard path)

When remotes receive SQL, stage depends on query shape. Intentionally hit all:

| Stage | Trigger queries (examples) |
|-------|----------------------------|
| `complete` | `SELECT * FROM h WHERE d = '…'` |
| `with_mergeable_state` | `SELECT count() FROM h` |
| `with_mergeable_state_after_aggregation` | `SELECT d, count() FROM h GROUP BY d` |
| `with_mergeable_state_after_aggregation_and_limit` | `… GROUP BY d ORDER BY d LIMIT 10` |

Also cover HAVING, DISTINCT, and GLOBAL JOIN as stage-adjacent shapes.

### 4.4 Settings matrix (minimum)

Run the **core query pack** (§7) under each row:

| # | prefer_localhost_replica | serialize_query_plan | hybrid_table_auto_cast_columns | Priority |
|---|--------------------------|----------------------|--------------------------------|----------|
| A | 1 | 0 | 0 | P0 baseline |
| B | 0 | 0 | 0 | P0 all-remote |
| C | 1 | 1 | 0 | P1 serialized plan |
| D | 0 | 1 | 0 | P1 serialized + all-remote |
| E | 1 | 0 | 1 | P0 when type mismatch present |
| F | 0 | 0 | 1 | P1 |
| G | 1 | 1 | 1 | P2 |
| H | 0 | 1 | 1 | P2 |

`enable_analyzer=0` is **negative-only**: expect clear failure / unsupported;
do not expand functional coverage there.

---

## 5. Segment topology matrix

### 5.1 Argument rules (from engine docs)

- **First segment:** always a table function that instantiates Distributed
  storage — require `remote` / `remoteSecure` / `cluster` /
  `clusterAllReplicas` wrappers in every test (never a bare local table name
  as the first argument).
- **Further segments:** same family of table functions, `s3` / `s3Cluster`,
  `iceberg` / `icebergCluster` (as enabled), or `database.table`
  (MergeTree-family or Iceberg).
- **INSERT:** always first segment only.

### 5.2 Priority segment pairs

| P | Left (first / INSERT) | Right | Why |
|---|----------------------|-------|-----|
| P0 | `cluster('{cluster}', … MT)` | Iceberg table / IcebergS3 | Blog canonical |
| P0 | `remote('localhost', … MT)` | `remote(… MT)` | Alias suite + Distributed baseline |
| P0 | `cluster(… MT)` | `remote(… MT)` | Multi-shard hot + single remote |
| P1 | `cluster(… MT)` | `icebergCluster(...)` | Swarm / object_storage_cluster |
| P1 | `remote(… MT)` | `s3(...)` / `s3Cluster(...)` | Parquet cold tier (docs example) |
| P1 | `cluster(… RMT)` | Iceberg via DataLakeCatalog (`ice` / `glue` / none) | Catalog modes |
| P2 | `clusterAllReplicas(...)` | Iceberg / MT | Read-mostly topologies |
| P2 | `remoteSecure(...)` | Iceberg / MT | TLS path |
| P2 | `cluster(…)` | `database.table` Hybrid | Nested Hybrid (if supported) |
| P2 | Distributed table as segment | MT / Iceberg | Distributed-over-Distributed (multi-shard + replicas; not a Cisco replica) |

### 5.3 Segment count

| # | Layout | Priority |
|---|--------|----------|
| 1 | Two segments (hot/cold) | P0 |
| 2 | Three segments (hot / warm / cold) | P2 |
| 3 | 5+ segments | P3 stress |

### 5.4 Schema definition modes

| # | Mode | Priority |
|---|------|----------|
| 1 | Explicit columns on Hybrid | P0 |
| 2 | `CREATE TABLE … AS source` (blog/RFC pattern) | P0 |
| 3 | Schema inferred from first table function (no column list) | P1 |

---

## 6. Watermarks and predicates

### 6.1 Static predicates (L1)

| Dimension | Cases |
|-----------|-------|
| Column types | `Date`, `DateTime`/`DateTime64`, integer, string |
| Expressions | `>=`/`<`, `BETWEEN`, `IN`, `LIKE`, AND/OR, function-based (`toYear`), `1=1` catch-all |
| Exclusivity | Mutually exclusive (no dupes); overlapping (expected dupes); gap (expected missing); identical (full dupe) |
| Updates | `CREATE OR REPLACE` forward / backward; concurrent SELECT during replace (atomicity) |

### 6.2 Dynamic watermark (named scalar) — out of scope

RFC describes `SHARED NAMED SCALAR` + `getSharedNamedScalar*`. That is
**planned only and not implemented**. Do not write tests, stubs, or
feature-gates for it. Use **static** watermarks (`CREATE OR REPLACE` with
literal predicates) for all L3 lifecycle work.

### 6.3 Predicate pruning

Always **hard-assert result correctness** when `WHERE` is disjoint from a
segment predicate (no rows from the excluded segment; hashes/counts match
the reference). Do not soften this for object-storage segments up front.

If a case fails in a way that looks like a product bug (e.g. cold S3 still
contributing rows, or surprising `EXPLAIN` behavior), triage that failure
case-by-case later — do not pre-bake soft checks into the suite policy.

`EXPLAIN` / pipeline checks may still be added where useful; they do not
replace result assertions.

---

## 7. Core query pack (correctness oracle)

Every L1/L2 configuration runs this pack against Hybrid and a **reference**:

```sql
-- Reference construction (exclusive watermarks):
(SELECT * FROM left  WHERE <left_predicate>)
UNION ALL
(SELECT * FROM right WHERE <right_predicate>)
```

Prefer comparing Hybrid vs reference with the same settings matrix row.

### 7.1 Query categories

| Category | Must-have shapes |
|----------|------------------|
| Projection | `SELECT *`, column lists, `DISTINCT` |
| Filter | equality, range, `BETWEEN`, `IN`, `LIKE`, NULL, complex boolean; segment-local vs cross-segment |
| Aggregation | `count`, `sum`, `avg`, `min`, `max`, `uniq`/`uniqExact`, `quantile`, `*If`, `groupBitXor(cityHash64(*))` |
| GROUP BY | single, multi, expression, `HAVING`, `WITH TOTALS` / `ROLLUP` / `CUBE` (P2) |
| ORDER / LIMIT | ASC/DESC, multi-key, `LIMIT`/`OFFSET`, LIMIT without ORDER |
| JOIN | INNER/LEFT/RIGHT/FULL vs MT; vs Iceberg; GLOBAL JOIN; self-join; `object_storage_cluster_join_mode` |
| Subquery / CTE | scalar, IN, EXISTS, derived table, multi-CTE |
| Set ops | `UNION ALL` / `DISTINCT`, INTERSECT/EXCEPT where supported |
| Window | `ROW_NUMBER`, `RANK`, running aggregates |
| EXPLAIN | plan shows segments; pruning case; `EXPLAIN PIPELINE` |
| INSERT | VALUES / SELECT → first segment only; readable via Hybrid; not present on second unless also written there |

### 7.2 Correctness checks

| Check | Use |
|-------|-----|
| `count()` | Sanity |
| `groupBitXor(cityHash64(*))` or stable per-column hashes | Full result equality |
| `sum` / `min` / `max` / `uniqExact` | Aggregate path (pushdown) |
| Ordered row dump (small sets) | Debugging |
| Dupe / gap assertions | Watermark exclusivity |

**Critical blog bug class:** aggregation must run with Distributed-style
partial aggregation + merge — not “union then aggregate”. Prefer checks that
would fail if pushdown were lost (compare timings only as secondary; primary
is result equality under path matrix).

---

## 8. Type compatibility and auto-cast (L2)

Iceberg/Parquet often cannot preserve ClickHouse unsigned / specialty types.
Blog failure: `UInt64` + `Int64` → `NO_COMMON_TYPE` on naive UNION.

### 8.1 Mismatch cases

| MergeTree | Iceberg / Parquet side | auto-cast=0 | auto-cast=1 |
|-----------|------------------------|-------------|-------------|
| `UInt64` | `Int64` / widened signed | Error expected | Query succeeds |
| `UInt32/16/8` | signed counterpart | Error / succeed per rules | Succeed |
| `FixedString(N)` | `String` | Often needs cast | Auto or explicit |
| `Decimal(P,S)` | narrower / int mapping | Document | Cast safety |
| `DateTime64(p1)` | `DateTime64(p2)` | Precision | |
| `Enum*` | `String` | | |
| `LowCardinality(T)` | `T` | | |
| Nested: `Array` / `Map` / `Tuple` / `Nullable` composites | per Iceberg mapping | Align with export_partition casting | |

Also test **aggregate state merge** across mismatched physical types
(`uniq()` on UInt64 vs Int64) — blog calls this incompletely solved without
auto-cast before aggregation.

### 8.2 Schema evolution across the seam (RFC §8.2)

| Change | Hybrid expectation |
|--------|--------------------|
| ADD / DROP COLUMN | User propagates to Iceberg + Hybrid; missing columns not invented by auto-cast |
| MODIFY type | May break EXPORT until Iceberg evolved; auto-cast bridges modest drift |
| RENAME | Treat as unsupported across seam |
| After segment schema change | `DETACH/ATTACH` or `CREATE OR REPLACE` Hybrid to refresh headers |

---

## 9. DDL, lifecycle, and edge cases

| Area | Scenarios |
|------|-----------|
| DDL | CREATE, IF NOT EXISTS, OR REPLACE (watermark move), DROP, SHOW CREATE, DESCRIBE, `system.tables` engine=`Hybrid` |
| Persistence | DETACH/ATTACH; server restart; table loads |
| Broken segments | Drop segment table then query; drop then restart (existing repro); invalid TF; bad predicate; missing column in predicate |
| Empty segments | Left empty / right empty / both empty |
| NULL watermark column | NULLs excluded from comparison predicates |
| Concurrency | Multi-session reads; reads during OR REPLACE |
| Single-segment CREATE | Error or documented minimum (engine requires ≥1 pair; docs say ≥2 args) |
| Teardown | Drop Hybrid, restore Distributed head (RFC §8.3) — no data loss in segments |

---

## 10. End-to-end product scenarios

### 10.1 Hot / cold tiered storage (P0)

1. Create RMT/MT hot table + Iceberg cold mirror (compatible schema).
2. Hybrid: `cluster(hot), d >= W` + `ice, d < W` (static W first).
3. INSERT via Hybrid → hot only.
4. Query spanning both tiers → matches reference.
5. `EXPORT PARTITION` old partitions to Iceberg (use export_partition helpers).
6. `CREATE OR REPLACE` Hybrid with advanced W (static literal predicates).
7. Optionally delete exported range from MT **only after** W advanced
   (manual / explicit DELETE — not TTL EXPORT).
8. Re-verify counts / hashes; no dupes; no gaps.

### 10.2 Hybrid replaces Distributed (P0/P1)

1. Baseline: `Distributed` head over `*_local`.
2. Capture reference query results / hashes.
3. Replace head with Hybrid (`cluster(…_local)` + Iceberg segment).
4. Same queries, same results under settings matrix A/B at minimum.
5. INSERT path unchanged (still local/RMT).

### 10.3 Zero-downtime migration / resharding (P1)

Old cluster/table + new cluster/table; watermark advances as days are
copied; assert no loss/duplication at each step.

### 10.4 Cache layer (P2)

Iceberg full set + MT subset for hot keys/dates; Hybrid routes accordingly.

### 10.5 Canary / partial traffic (P2)

Route a predicate slice (`region`, tenant, sample) to alternate cluster.

### 10.6 Distributed-over-Distributed (P2)

Exercise a Hybrid (or Distributed) segment that itself reads through
Distributed — enough shards and replicas in the existing iceberg compose
topology. **Do not** try to mirror a customer-specific (e.g. Cisco) layout;
multi-shard + multi-replica is sufficient.

---

## 11. Query fuzzing

All broad query-driving coverage lives under **fuzzing**: the existing Hybrid
fuzz SQL plus new upstream-derived queries. Same harness, same Feature area.

### 11.1 Existing Hybrid fuzz SQL (keep)

Retain `hybrid_query_fuzzing.py` and `hybrid_query_fuzzing_queries.sql`
(~120 curated Hybrid queries: SELECT, aggs, JOIN, UNION, window, CTE, etc.
on MergeTree + `icebergCluster`).

Revamp work on this path:

- Move with the suite to `iceberg/tests/hybrid`.
- Remove interactive `pause()`; enable from `feature.py`.
- Parameterize settings matrix rows where useful.
- Classify outcomes: pass / known xfail / crash / wrong result vs reference.
- Keep extending this SQL file as Hybrid-specific cases appear.

### 11.2 Upstream queries (add)

**Additional** fuzz inputs from ClickHouse upstream
`tests/queries/0_stateless` (and selected stateful / integration tests),
filtered to statements meaningful on a single table / Distributed-like head.

This does **not** replace §11.1 — it widens shape coverage with real upstream
query patterns the existing Hybrid fuzz SQL does not already cover.

Also include a small hand-written set for Distributed stage modes (§4.3) and
pruning if those are not already hit by §11.1 / upstream picks.

### 11.3 Harness requirements

- Non-interactive.
- Shared table-name / placeholder substitution.
- Run on at least: MT+MT and MT+Iceberg (or `icebergCluster`) topologies.
- Optional TE/xfail list tied to GitHub issues (as ice regression already does
  for some alias query_context cases).
- Existing Hybrid SQL and upstream-derived SQL can be separate scenarios under
  the same fuzzing Feature so either can be run/skipped independently.

---

## 12. Schema / dataset validation track (RFC §12)

Parallel to unit-style tests; gates “production ready” claims.

### 12.1 Schema shapes

| Shape | Stresses |
|-------|----------|
| Wide flat numeric (~50 cols) | Baseline |
| Telemetry: `Map`, `LowCardinality`, `DateTime64` | Type mapping |
| Logs: `String`, `Array`, attrs `Map` | Nested |
| Financial: `Decimal(38,18)`, `FixedString`, `Enum8` | Soft spots in RFC §4 |
| MV target table | Writes vs export interleaving |
| Multi-shard skewed key | Routing / correctness with uneven shard data |

### 12.2 Scale targets (soak / nightly, not every PR)

- ≥ 100M rows hot steady state (where CI allows a labeled job)
- Large partition counts (≥ 50 exported) on a dedicated job
- PR jobs use reduced cardinalities with same *shapes*

### 12.3 Checks

Round-trip hashes; Spark/DuckDB/PyIceberg read of cold tier where
environment allows; P50/P95 Hybrid vs former Distributed (track, don’t
fail PR on soft perf unless budget agreed); operational drills (§10.6).

---

## 13. Proposed module layout (`iceberg/tests/hybrid/`)

```
hybrid/
  feature.py                 # entry; enable gates
  steps/                     # or iceberg/tests/steps/hybrid*.py
  docs/
    hybrid_testing_matrix.md # this file (move with suite)
    alias_testing_matrix.md
  core/                      # L1
    ddl_lifecycle.py
    insert_routing.py
    watermarks_static.py
    predicate_pruning.py
    query_pack.py            # shared scenarios
    execution_paths.py       # settings matrix × stage modes
    distributed_over_distributed.py
  storage/                   # L2
    mergetree_mergetree.py
    mergetree_iceberg.py     # catalogs parametrized
    mergetree_s3.py
    mergetree_iceberg_cluster.py
    type_autocast.py
  lifecycle/                 # L3
    export_then_watermark.py
    replace_distributed_head.py
    common.py
    feature.py
  fuzzing/                   # §11 — Hybrid fuzz SQL + upstream-derived queries
    hybrid_queries.py
    hybrid_query_fuzzing_queries.sql
    upstream_queries.py
    upstream_queries.sql
    common.py
    feature.py
  schema/                    # Phase 5 — variety / ops / PyIceberg interop
    variety.py
    operational.py
    external_reader.py
    common.py
    feature.py
  alias/                       # moved hybrid_alias — separate Feature
  edge/
    dropped_segment_restart.py
```

Parametrize catalogs (`no` / `ice` / `glue`) and source engines
(`MergeTree` / `ReplicatedMergeTree`) the same way `export_partition` does.

Core topology DoD (Phase 4): `core/topology.py` — secure cluster,
`clusterAllReplicas`, three-segment Hybrid, Distributed-over-Distributed.

---

## 14. Implementation phases

### Phase 0 — Move and skeleton (P0) ✅

- [x] Create `iceberg/tests/hybrid`, wire `Feature` in `iceberg/regression.py`.
- [x] Move `hybrid.md` → `iceberg/requirements/hybrid.md`.
- [x] Move ALIAS suite as its **own Feature**; move edge repro; fix imports;
  enable experimental gates in profile.
- [x] Port hybrid steps to `iceberg/tests/steps/hybrid.py`; thin-wrap
  `ice/steps/hybrid.py`; remove `ice/tests/hybrid`.
- [x] Smoke: `smoke.py` — Hybrid with `remote()` first segment + SELECT count();
  `analyzer_required` proves `enable_analyzer=0` fails / `=1` succeeds.

### Phase 1 — Engine core + execution paths (P0) ✅ implemented

Modules under `iceberg/tests/hybrid/core/`:

- [x] Core query pack on MT+MT (`query_pack.py`) — settings A/B
- [x] Settings matrix A/B + E (`execution_paths.py`, `type_autocast.py`)
- [x] All four Distributed stages × A/B (`execution_paths.py`)
- [x] INSERT routing (`insert_routing.py`)
- [x] Static watermark exclusivity / overlap / OR REPLACE (`watermarks.py`)
- [x] Predicate pruning with hard result assertions (`predicate_pruning.py`)
- [x] `cluster(MT)+IcebergS3` correctness (`mergetree_iceberg.py`) — settings A/B

### Phase 2 — Storage matrix + auto-cast (P0/P1) ✅ implemented

Modules under `iceberg/tests/hybrid/storage/`:

- [x] Catalog-param Iceberg destinations (`no` / `ice` / `glue`) — `mergetree_iceberg_catalog.py`
- [x] `icebergCluster` + `object_storage_cluster_join_mode` — `mergetree_iceberg_cluster.py`
- [x] S3 / s3Cluster Parquet segment — `mergetree_s3.py`
- [x] Type mismatch on MT↔Iceberg (UInt64/Int64, UInt32/Int32) + `uniq` — `type_autocast_iceberg.py`
- [x] Schema header refresh (ADD COLUMN + CREATE OR REPLACE) — `schema_refresh.py`

Still deferred (later / Phase 3+):

- [ ] Full §8 type table (FixedString, Decimal, DateTime64, Enum, LowCardinality, nested)
  — partial: Phase 5 `schema/variety.py` covers PR-scale shapes; Iceberg rejects
  FixedString/Decimal/Enum/LC natively (MT+MT + FixedString↔String seam covered)
- [ ] DETACH/ATTACH Hybrid persistence; dropped-segment hardening (#1347)

### Phase 3 — Lifecycle with EXPORT (P1) ✅ implemented

Modules under `iceberg/tests/hybrid/lifecycle/`:

- [x] Export partition(s) → advance **static** watermark via OR REPLACE → verify —
  `export_then_watermark.py`
- [x] Hybrid replaces Distributed recipe — `replace_distributed_head.py`
- [x] Overlap window discipline (export before manual delete / gap if W advances
  without export) — `export_then_watermark.py`
- [ ] Dropped-segment / restart hardening beyond single repro — still deferred
  (`hybrid_dropped_segment_repro.py`, #1347)

### Phase 4 — Fuzzing + DoD (P1/P2) ✅ implemented

- [x] Harden and enable existing Hybrid query fuzzing (no `pause()`, wired) —
  `fuzzing/hybrid_queries.py` + `fuzzing/hybrid_query_fuzzing_queries.sql`
- [x] Upstream-derived queries under the same fuzzing Feature —
  `fuzzing/upstream_queries.py` + `fuzzing/upstream_queries.sql`
- [x] Distributed-over-Distributed — `core/topology.py`
- [x] Three-segment Hybrid — `core/topology.py`
- [x] remoteSecure / clusterAllReplicas smoke — `core/topology.py`

### Phase 5 — Schema variety + soak (P2/P3) ✅ PR-scale implemented

Modules under `iceberg/tests/hybrid/schema/`:

- [x] Schema variety track (reduced scale) — `variety.py`
  (financial / telemetry / logs MT+MT; Iceberg-compatible nested; FixedString↔String seam)
- [x] Operational drills (EXPORT lag / Iceberg unreachable, static W) — `operational.py`
- [x] External PyIceberg read of exported cold tier — `external_reader.py`
  (catalog destination + `schema.name-mapping.default`; EXPORT Parquet has no field-ids)
- [ ] Large soak (100M+ / multi-TB) nightly — deferred (optional job, not PR)
- [ ] Spark/DuckDB parity job — deferred (PyIceberg covered for PR)

### Phase notes

## 15. Priority checklist (quick view)

### P0 — Must have for revamp MVP

- [x] Suite under `iceberg/tests/hybrid` wired into iceberg regression
- [x] MT+MT and `cluster(MT)+Iceberg` with exclusive date watermark
- [x] Smoke: Hybrid `remote()` + SELECT (Phase 0)
- [x] Core SELECT / WHERE / GROUP BY / ORDER BY LIMIT / basic aggs
- [x] INSERT → first segment only
- [x] Settings: `prefer_localhost_replica` 0/1; auto-cast with UInt/Int seam
- [x] CREATE / DROP / CREATE OR REPLACE watermark move
- [x] Hash/count correctness vs reference
- [x] Analyzer required — `smoke.analyzer_required` (`enable_analyzer=0` fails)

### P1 — Should have next

- [x] `serialize_query_plan` 0/1 × localhost preference (Phase 1 `execution_paths.py`)
- [x] All four remote aggregation stages (Phase 1 `execution_paths.py`)
- [ ] JOINs, subqueries, CTE, UNION, window (subset)
- [x] icebergCluster path (Phase 2 `mergetree_iceberg_cluster.py`)
- [x] EXPORT PARTITION then static watermark advance E2E
- [x] Hybrid replaces Distributed
- [x] Catalog modes for Iceberg segment (Phase 2 `mergetree_iceberg_catalog.py`)
- [x] S3 / s3Cluster Parquet cold segment (Phase 2 `mergetree_s3.py`)
- [x] Existing hybrid query fuzzing enabled (non-interactive)
- [x] Upstream-derived fuzz queries v1 (additive; under same fuzzing Feature)
- [ ] Dropped-segment / restart hardening (#1347)

### P2 — Expand

- [x] S3 Parquet segments; secure cluster / clusterAllReplicas (`core/topology.py`)
- [x] Distributed-over-Distributed (multi-shard + replicas; not customer-specific)
- [ ] Overlapping predicates / dupes; pruning with hard result assertions
- [ ] ROLLUP/CUBE/TOTALS; nested Hybrid
- [x] Three-segment Hybrid (`core/topology.py`)
- [ ] Concurrent OR REPLACE; schema evolution cases
- [x] Schema-variety validation job (reduced scale) — `schema/variety.py`
- [x] Operational drills EXPORT lag / Iceberg unreachable — `schema/operational.py`
- [x] PyIceberg external read of exported cold tier — `schema/external_reader.py`

### P3 — Optional soak / interop

- [ ] Large soak (100M+ / multi-TB) nightly
- [ ] External Spark/DuckDB parity job
- [ ] Perf budgets vs Distributed baseline
- [x] PyIceberg cold-tier interop (Phase 5 `schema/external_reader.py`)

---

## 16. Out of scope (explicit)

- Re-testing full EXPORT PARTITION internals (owned by `export_partition`).
- Two-way Iceberg → MergeTree sync; import-parts-from-Iceberg (RFC future).
- Hybrid-side merge-on-read / cross-segment dedup.
- Making Hybrid work with `enable_analyzer=0`.
- Upstream ClickHouse builds without Antalya Hybrid (skip / ffail suite).
- **`SHARED NAMED SCALAR` / dynamic watermarks** — planned only, not implemented.
- **`TTL … EXPORT TO`** — pretend it does not exist; no tests or stubs.

---

## 17. Decisions (resolved)

| # | Topic | Decision |
|---|-------|----------|
| 1 | Named scalars | Out of scope — design-only, not in implementation. Static watermarks only. |
| 2 | Predicate pruning assertions | Always hard-assert **result correctness**. No soft carve-outs for object storage. Triage surprising failures case-by-case if they look like product bugs. |
| 3 | First segment | Always require `cluster()` / `remote()` / `remoteSecure()` / `clusterAllReplicas()` wrapper. |
| 4 | Alias suite | Keep all modules; run as a **separate Feature**. |
| 5 | Requirements | Place `hybrid.md` under `iceberg/requirements/`. |
| 6 | Distributed-over-Distributed | Multi-shard + multi-replica in existing env is enough; do not emulate a specific customer topology. |
| 7 | TTL EXPORT | Ignore entirely for this suite. |

---

## 18. Traceability

| Plan section | Primary source |
|--------------|----------------|
| §0–1 placement, Distributed branches | `hybrid_additional_notes.md`, team decision |
| §4 execution paths / stages | notes + `hybrid.md` “Distributed execution and testing” |
| §5–9 engine matrix | `hybrid.md` + prior matrix |
| §8 types / aggs | blog (VIEW failure + partial agg states) |
| §10 E2E (static W + EXPORT PARTITION) | blog + RFC gist (minus named scalar / TTL EXPORT) |
| §11 fuzzing | notes — keep Hybrid fuzz SQL; **add** upstream under fuzzing |
| §12 validation shapes | RFC §12 (scale/jobs optional) |
| §2 baseline | `iceberg/tests/hybrid` inventory after Phase 0 |
| §17 decisions | this conversation |

When product behavior changes, update this file in the same PR as the tests.

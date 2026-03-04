# Hybrid Table Engine — General Testing Matrix

## Overview

This document defines all parameter dimensions and test scenarios for the Hybrid
table engine. ALIAS column tests are maintained separately in
`hybrid_alias/` and `alias_testing_matrix.md`.

The Hybrid engine builds on top of the Distributed engine, exposing multiple data
sources as a single logical table with per-segment predicates. It inherits
Distributed's query execution infrastructure and all its code-path variations.

**References:**
- `ice/requirements/hybrid.md` — engine documentation
- [Altinity blog post](https://altinity.com/blog/introducing-hybrid-tables-transparent-query-on-clickhouse-mergetree-and-iceberg-data) — design rationale and architecture

---

## 1. Required Settings

The Hybrid engine requires certain settings to be enabled.

| Setting | Required Value | Notes |
|---------|---------------|-------|
| `allow_experimental_hybrid_table` | `1` | Must be set before CREATE TABLE |
| `enable_analyzer` | `1` | The **only** supported mode for Hybrid; formerly `allow_experimental_analyzer` |

**Optional settings that affect behavior:**

| Setting | Default | Notes |
|---------|---------|-------|
| `hybrid_table_auto_cast_columns` | `0` | Auto-insert CAST for type mismatches between segments; requires `enable_analyzer=1` |
| `prefer_localhost_replica` | `1` | Controls local vs remote execution path |
| `serialize_query_plan` | `0` | Send serialized plan instead of SQL to remote shards |
| `skip_unused_shards` | varies | Distributed optimization for predicate pruning |
| `object_storage_cluster_join_mode` | varies | Affects JOIN behavior with object storage segments |

---

## 2. Segment Configurations

The first argument must be a table function that instantiates Distributed storage
(`remote`, `cluster`, etc.). Subsequent segments can be table functions or fully
qualified table names.

### 2.1 Allowed Segment Types (Left / Right)

The Hybrid engine definition in `ice/requirements/hybrid.md` constrains segment
types as follows:

- The **left segment (first argument)** must be a table function that
  instantiates `Distributed` storage, for example:
  - `remote(cluster, db, table)`
  - `remoteSecure(cluster, db, table)`
  - `cluster(cluster_name, db, table)`
  - `clusterAllReplicas(cluster_name, db, table)`
- Each **right segment (second and subsequent arguments)** must be either:
  - A table function:
    - `remote(...)`
    - `remoteSecure(...)`
    - `cluster(...)`
    - `clusterAllReplicas(...)`
    - `s3('s3://...')`
    - `s3Cluster('cluster', 's3://...')`
    - `icebergCluster(...)` (if enabled)
  - A fully qualified table name:
    - `database.table` using a MergeTree-family engine
    - `database.table` using the Iceberg engine

### 2.2 Representative Left/Right Combinations

The following table enumerates representative Hybrid configurations built from
the allowed segment types above.

| # | Left Segment (first) | Right Segment | Use Case |
|---|----------------------|--------------|----------|
| 1 | `remote(... MergeTree)` | `remote(... MergeTree)` | Resharding / migration between clusters |
| 2 | `remote(... MergeTree)` | `cluster(... MergeTree)` | Migration from single remote to multi-shard cluster |
| 3 | `remote(... MergeTree)` | `clusterAllReplicas(... MergeTree)` | Migration to all-replicas cluster |
| 4 | `remote(... MergeTree)` | `remoteSecure(... MergeTree)` | Migration to secure remote |
| 5 | `remote(... MergeTree)` | `s3('s3://...')` | Tiered: hot MergeTree + cold S3 Parquet |
| 6 | `remote(... MergeTree)` | `s3Cluster('cluster', 's3://...')` | Tiered: hot MergeTree + cold S3 with parallel reads |
| 7 | `remote(... MergeTree)` | Iceberg table (`database.table`) | Tiered: hot MergeTree + cold Iceberg |
| 8 | `remote(... MergeTree)` | `icebergCluster(...)` | Tiered: hot MergeTree + cold Iceberg with swarm |
| 9 | `cluster(... MergeTree)` | `remote(... MergeTree)` | Multi-shard cluster reading from single remote |
| 10 | `cluster(... MergeTree)` | `cluster(... MergeTree)` | Cluster-to-cluster migration |
| 11 | `cluster(... MergeTree)` | `clusterAllReplicas(... MergeTree)` | Migration to all-replicas cluster |
| 12 | `cluster(... MergeTree)` | `remoteSecure(... MergeTree)` | Secure read-back from remote |
| 13 | `cluster(... MergeTree)` | `s3('s3://...')` | Multi-shard cluster + S3 |
| 14 | `cluster(... MergeTree)` | `s3Cluster('cluster', 's3://...')` | Multi-shard cluster + parallel S3 reads |
| 15 | `cluster(... MergeTree)` | Iceberg table | Multi-shard cluster + Iceberg |
| 16 | `cluster(... MergeTree)` | `icebergCluster(...)` | Multi-shard cluster + Iceberg cluster |
| 17 | `clusterAllReplicas(... MergeTree)` | `remote(... MergeTree)` | Read-mostly cluster over single remote |
| 18 | `clusterAllReplicas(... MergeTree)` | `cluster(... MergeTree)` | All-replicas over standard cluster |
| 19 | `clusterAllReplicas(... MergeTree)` | Iceberg table | All-replicas cluster + Iceberg |
| 20 | `remoteSecure(... MergeTree)` | `remote(... MergeTree)` | Secure primary + non-secure secondary |
| 21 | `remoteSecure(... MergeTree)` | `s3('s3://...')` | Secure connection + S3 |
| 22 | `remoteSecure(... MergeTree)` | Iceberg table | Secure connection + Iceberg |
| 23 | `remote(... MergeTree)` | `database.table` (MergeTree) | Remote hot + local MergeTree |
| 24 | `cluster(... MergeTree)` | `database.table` (MergeTree) | Cluster hot + local MergeTree |
| 25 | `remote(... MergeTree)` | `database.table` (Hybrid) | Hybrid-over-Hybrid, if supported |
| 26 | `cluster(... MergeTree)` | `database.table` (Hybrid) | Cluster reading from nested Hybrid table |

### 2.2 Number of Segments

| # | Scenario | Notes |
|---|----------|-------|
| 1 | Two segments (minimum) | Standard hot/cold split |
| 2 | Three segments | e.g., hot + warm + cold tiers |
| 3 | Many segments (5+) | Stress test for segment routing |

### 2.3 Schema Definition

| # | Scenario | Notes |
|---|----------|-------|
| 1 | Explicit column definition in CREATE TABLE | Full control over schema |
| 2 | Schema auto-detected from first table function | `CREATE TABLE ... ENGINE = Hybrid(...)` without columns |
| 3 | `CREATE TABLE ... AS source_table` | Schema copied from existing table |

---

## 3. Watermark / Predicate Patterns

Predicates are SQL expressions AND-ed into each segment's query. They determine
which rows are served from which segment.

### 3.1 Predicate Column Types

| # | Predicate Type | Example |
|---|---------------|---------|
| 1 | Date column | `date >= '2025-01-01'` / `date < '2025-01-01'` |
| 2 | DateTime column | `timestamp >= '2025-01-01 00:00:00'` |
| 3 | Integer column | `id >= 10000` / `id < 10000` |
| 4 | String column | `region = 'US'` / `region != 'US'` |

### 3.2 Predicate Expression Types

| # | Expression | Example |
|---|-----------|---------|
| 1 | Simple comparison (`>=`, `<`) | `date >= '2025-01-01'` |
| 2 | BETWEEN | `id BETWEEN 10 AND 15` |
| 3 | IN list | `region IN ('US', 'EU')` |
| 4 | LIKE | `name LIKE 'A%'` |
| 5 | Complex AND/OR | `(date >= '2025-01-01' AND region = 'US')` |
| 6 | Function-based | `toYear(date) >= 2025` |
| 7 | Always-true (`1=1`) | All rows from this segment (useful as catch-all) |

### 3.3 Predicate Exclusivity

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | Mutually exclusive predicates | Each row from exactly one segment, no duplicates |
| 2 | Overlapping predicates | Rows matching both predicates returned from both segments (duplicates) |
| 3 | Gap in predicates | Some rows not matched by any predicate (data loss for those rows) |
| 4 | Identical predicates on both segments | Full duplication |

### 3.4 Watermark Updates

| # | Scenario | Notes |
|---|----------|-------|
| 1 | `CREATE OR REPLACE TABLE` to move watermark forward | Atomic — queries see new watermark immediately |
| 2 | `CREATE OR REPLACE TABLE` to move watermark backward | |
| 3 | Concurrent reads during watermark update | Verify atomicity |

---

## 4. Distributed Execution Paths

Since the Hybrid engine reuses Distributed's query infrastructure, there are
several important code-path branching points. **Each combination can surface
different bugs.**

### 4.1 Local vs Remote Execution (`prefer_localhost_replica`)

| # | Setting | Behavior |
|---|---------|----------|
| 1 | `prefer_localhost_replica=1` (default) | Local shard executes locally; remote shards via network |
| 2 | `prefer_localhost_replica=0` | **All** shards treated as remote, even local ones |

When `prefer_localhost_replica=1`, the initiator merges results from a **local
execution plan** with results from **remote shard execution** — these are
completely different code paths. Problems often arise at the merge point.

### 4.2 Query Plan Serialization (`serialize_query_plan`)

| # | Setting | Behavior |
|---|---------|----------|
| 1 | `serialize_query_plan=0` (default) | ClickHouse constructs a SQL subquery and sends it to the remote shard |
| 2 | `serialize_query_plan=1` | ClickHouse serializes the execution plan as a JSON graph and sends it instead |

These are fundamentally different execution paths. The serialized plan path is
expected to become the default in the future.

### 4.3 Distributed Subquery Execution Modes

When sending queries to shards as SQL, ClickHouse selects one of four modes
depending on the query type. Each mode determines how much partial processing is
done on the shard.

| # | Mode | Triggered By | Behavior |
|---|------|-------------|----------|
| 1 | `complete` | Simple `SELECT` | Shard executes full query, returns final results |
| 2 | `with_mergeable_state` | `SELECT` with aggregation | Shard returns intermediate aggregate states |
| 3 | `with_mergeable_state_after_aggregation` | `SELECT` with `GROUP BY` | Shard aggregates, returns mergeable states |
| 4 | `with_mergeable_state_after_aggregation_and_limit` | `SELECT` with `GROUP BY` + `ORDER BY ... LIMIT` | Shard aggregates + applies LIMIT before returning |

**Test queries to trigger each mode:**
- Mode 1: `SELECT * FROM hybrid_table WHERE date = '2025-01-01'`
- Mode 2: `SELECT count() FROM hybrid_table`
- Mode 3: `SELECT date, count() FROM hybrid_table GROUP BY date`
- Mode 4: `SELECT date, count() FROM hybrid_table GROUP BY date ORDER BY date LIMIT 10`

### 4.4 Distributed-over-Distributed

| # | Scenario | Notes |
|---|----------|-------|
| 1 | Hybrid segment is a Distributed table | Distributed-over-distributed topology |
| 2 | Hybrid segment is another Hybrid table | Nested Hybrid tables (if supported) |

Example:
```sql
CREATE TABLE inner_distributed AS inner_local
ENGINE = Distributed('{cluster}', currentDatabase(), 'inner_local', rand());

CREATE TABLE hybrid_dod ENGINE = Hybrid(
    remote('localhost', currentDatabase(), 'hot_local'), date >= '2025-01-15',
    inner_distributed, date < '2025-01-15'
);
```

### 4.5 Combined Execution Path Matrix

The most thorough testing crosses all execution path dimensions:

| prefer_localhost_replica | serialize_query_plan | Query Type | Priority |
|------------------------|---------------------|------------|----------|
| 1 (default) | 0 (default) | Simple SELECT | High |
| 1 (default) | 0 (default) | GROUP BY | High |
| 1 (default) | 0 (default) | GROUP BY + ORDER BY LIMIT | High |
| 0 | 0 | Simple SELECT | High |
| 0 | 0 | GROUP BY | High |
| 1 (default) | 1 | Simple SELECT | Medium |
| 1 (default) | 1 | GROUP BY | Medium |
| 0 | 1 | Simple SELECT | Medium |
| 0 | 1 | GROUP BY | Medium |
| 0 | 1 | GROUP BY + ORDER BY LIMIT | Medium |

---

## 5. Query Types

All query types should be tested against the Hybrid table and compared against a
reference MergeTree table containing the same data.

### 5.1 Basic SELECT

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `SELECT * FROM hybrid LIMIT N` | |
| 2 | `SELECT col1, col2 FROM hybrid` | Column projection |
| 3 | `SELECT DISTINCT col FROM hybrid` | Deduplication |
| 4 | `SELECT * FROM hybrid ORDER BY col LIMIT N OFFSET M` | Pagination |

### 5.2 WHERE Clause

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `WHERE col = value` | Equality |
| 2 | `WHERE col > value AND col < value` | Range |
| 3 | `WHERE col BETWEEN a AND b` | BETWEEN |
| 4 | `WHERE col IN (...)` | IN list |
| 5 | `WHERE col LIKE 'pattern'` | Pattern match |
| 6 | `WHERE col IS NULL` / `IS NOT NULL` | NULL handling |
| 7 | `WHERE col1 > col2` | Cross-column comparison |
| 8 | `WHERE NOT condition` | Negation |
| 9 | `WHERE (cond1 OR cond2) AND cond3` | Complex boolean |
| 10 | `WHERE` hits only left segment | Predicate pruning |
| 11 | `WHERE` hits only right segment | Predicate pruning |
| 12 | `WHERE` hits both segments | Full fan-out |

### 5.3 Aggregations

| # | Function | Notes |
|---|----------|-------|
| 1 | `COUNT(*)`, `COUNT(col)` | |
| 2 | `SUM(col)` | |
| 3 | `AVG(col)` | |
| 4 | `MIN(col)`, `MAX(col)` | |
| 5 | `uniq(col)`, `uniqExact(col)` | |
| 6 | `quantile(level)(col)` | |
| 7 | `argMin(col, col2)`, `argMax(col, col2)` | |
| 8 | `any(col)`, `anyLast(col)` | |
| 9 | `topK(N)(col)` | |
| 10 | `groupArray(col)`, `groupUniqArray(col)` | |
| 11 | `groupBitXor(cityHash64(*))` | Full-table hash for correctness |
| 12 | `countIf(col, cond)`, `sumIf(col, cond)`, `avgIf(col, cond)` | Conditional aggregates |

### 5.4 GROUP BY

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `GROUP BY single_col` | |
| 2 | `GROUP BY col1, col2` | Multiple columns |
| 3 | `GROUP BY expr` (e.g., `toYear(date)`) | Expression grouping |
| 4 | `GROUP BY ... HAVING condition` | Post-aggregation filter |
| 5 | `GROUP BY ... WITH TOTALS` | Totals row |
| 6 | `GROUP BY ... WITH ROLLUP` | Rollup aggregation |
| 7 | `GROUP BY ... WITH CUBE` | Cube aggregation |

### 5.5 ORDER BY / LIMIT

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `ORDER BY col ASC` | |
| 2 | `ORDER BY col DESC` | |
| 3 | `ORDER BY col1, col2` | Multi-column sort |
| 4 | `ORDER BY col LIMIT N` | Top-N |
| 5 | `ORDER BY col LIMIT N OFFSET M` | Pagination |
| 6 | `LIMIT N` without ORDER BY | Arbitrary limit |

### 5.6 JOINs

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `INNER JOIN` with MergeTree table | |
| 2 | `LEFT JOIN` with MergeTree table | |
| 3 | `RIGHT JOIN` with MergeTree table | |
| 4 | `FULL OUTER JOIN` with MergeTree table | |
| 5 | `INNER JOIN` with Iceberg table | |
| 6 | `INNER JOIN` with another Hybrid table | |
| 7 | Self-JOIN of hybrid table | |
| 8 | JOIN with `GLOBAL` keyword | Global JOIN pushdown |
| 9 | JOIN with `object_storage_cluster_join_mode = 'local'` | |

### 5.7 Subqueries

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `WHERE col > (SELECT AVG(col) FROM hybrid)` | Scalar subquery |
| 2 | `WHERE col IN (SELECT col FROM other_table)` | IN subquery |
| 3 | `WHERE EXISTS (SELECT 1 FROM other WHERE ...)` | EXISTS subquery |
| 4 | `SELECT * FROM (SELECT ... FROM hybrid GROUP BY ...)` | Derived table |

### 5.8 UNION

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `UNION ALL` with MergeTree table | |
| 2 | `UNION DISTINCT` with MergeTree table | |
| 3 | `UNION ALL` with Iceberg table | |
| 4 | Triple UNION (hybrid + MergeTree + Iceberg) | |

### 5.9 CTEs (Common Table Expressions)

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `WITH cte AS (SELECT ... FROM hybrid) SELECT * FROM cte` | |
| 2 | Multiple CTEs with JOINs | |

### 5.10 Window Functions

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `ROW_NUMBER() OVER (PARTITION BY col ORDER BY col)` | |
| 2 | `RANK() OVER (ORDER BY col)` | |
| 3 | `SUM(col) OVER (PARTITION BY col)` | Partitioned window aggregate |
| 4 | `AVG(col) OVER (PARTITION BY col ORDER BY col)` | Running average |

### 5.11 EXPLAIN

| # | Query Pattern | Notes |
|---|--------------|-------|
| 1 | `EXPLAIN SELECT * FROM hybrid` | Verify plan shows both segments |
| 2 | `EXPLAIN SELECT * FROM hybrid WHERE <hits_one_segment>` | Verify segment pruning |
| 3 | `EXPLAIN PIPELINE SELECT ... FROM hybrid` | Verify pipeline structure |

---

## 6. INSERT Behavior

INSERT statements are **always forwarded to the first segment only**.

| # | Scenario | Expected |
|---|----------|----------|
| 1 | `INSERT INTO hybrid VALUES (...)` | Data goes to first segment |
| 2 | `INSERT INTO hybrid SELECT * FROM source` | Data goes to first segment |
| 3 | Verify data is NOT in second segment after INSERT | |
| 4 | Verify data IS readable via Hybrid table after INSERT | |
| 5 | INSERT with data matching second segment's predicate | Data still goes to first segment |
| 6 | Bulk INSERT (large number of rows) | |

---

## 7. DDL Operations

| # | Scenario | Expected |
|---|----------|----------|
| 1 | `CREATE TABLE ... ENGINE = Hybrid(...)` | Table created |
| 2 | `CREATE TABLE IF NOT EXISTS ...` | Idempotent create |
| 3 | `CREATE OR REPLACE TABLE ...` | Atomic replacement (watermark update) |
| 4 | `DROP TABLE hybrid_table` | Clean drop |
| 5 | `DETACH TABLE` / `ATTACH TABLE` | Survives detach/attach cycle |
| 6 | Server restart with Hybrid table | Table loads correctly on startup |
| 7 | Drop a segment table, then restart server | Hybrid table should handle gracefully |
| 8 | `SHOW CREATE TABLE hybrid_table` | Correct engine definition shown |
| 9 | `DESCRIBE TABLE hybrid_table` | Correct columns and types shown |
| 10 | `SELECT * FROM system.tables WHERE engine = 'Hybrid'` | System table reflects Hybrid engine |

---

## 8. Data Type Compatibility Across Segments

Segments can have different physical types for the same logical column. This is
common when one segment is MergeTree and the other is Iceberg/Parquet.

### 8.1 Common Type Mismatches

| # | MergeTree Type | Iceberg/Parquet Type | Needs auto-cast | Notes |
|---|---------------|---------------------|-----------------|-------|
| 1 | `UInt64` | `Int64` | Yes | Iceberg has no unsigned integers |
| 2 | `UInt32` | `Int32` | Yes | Same |
| 3 | `UInt16` | `Int16` | Yes | Same |
| 4 | `UInt8` | `Int8` | Yes | Same |
| 5 | `FixedString(N)` | `String` | Yes | Parquet stores as String |
| 6 | `Decimal(P,S)` | `Int64` | Yes | Precision loss risk |
| 7 | `DateTime64(9)` | `DateTime64(6)` | Depends | Different precision |
| 8 | `Enum8(...)` | `String` | Yes | Enum stored as string in Parquet |
| 9 | `LowCardinality(String)` | `String` | Depends | |

### 8.2 Auto-Cast Settings

| # | Setting | Behavior |
|---|---------|----------|
| 1 | `hybrid_table_auto_cast_columns=0` (default) | Type mismatches cause `CANNOT_CONVERT_TYPE` errors |
| 2 | `hybrid_table_auto_cast_columns=1` | Engine auto-inserts CAST; requires `enable_analyzer=1` |

### 8.3 Aggregate State Compatibility

When segments have different physical types, aggregate functions produce
incompatible intermediate states. For example, `uniq()` on `UInt64` vs `Int64`
produces different state formats that cannot be merged.

| # | Scenario | Notes |
|---|----------|-------|
| 1 | Aggregation with same types across segments | Should work |
| 2 | Aggregation with different types, auto-cast enabled | CAST applied before aggregation |
| 3 | Aggregation with different types, auto-cast disabled | Error expected |

---

## 9. Predicate Pruning and Optimization

The Hybrid engine should leverage Distributed optimizations to avoid scanning
segments that cannot match the query's WHERE clause.

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Query WHERE fully matches left segment predicate | Only left segment scanned |
| 2 | Query WHERE fully matches right segment predicate | Only right segment scanned |
| 3 | Query WHERE overlaps both segments | Both segments scanned |
| 4 | Query without WHERE | Both segments scanned |
| 5 | `skip_unused_shards=1` with prunable predicate | Segment skipped (verify via EXPLAIN) |

---

## 10. Data Correctness Validation

Every test should compare Hybrid table results against a reference. The reference
can be constructed by manually applying predicates to each segment table and
combining with UNION ALL.

| # | Validation Method | Notes |
|---|------------------|-------|
| 1 | Row count: `COUNT(*)` matches reference | Basic sanity |
| 2 | Full hash: `groupBitXor(cityHash64(*))` matches | Byte-level correctness |
| 3 | Per-column aggregates match (`SUM`, `MIN`, `MAX`) | Column-level correctness |
| 4 | Row-by-row comparison with `ORDER BY` | Strongest validation |
| 5 | No duplicate rows when predicates are mutually exclusive | |
| 6 | Expected duplicates when predicates overlap | |

---

## 11. Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | Empty left segment (no rows match predicate) | Results come only from right segment |
| 2 | Empty right segment (no rows match predicate) | Results come only from left segment |
| 3 | Both segments empty | Empty result set |
| 4 | NULL values in predicate column | NULLs don't match comparison predicates |
| 5 | Very large result set (millions of rows) | Performance, no OOM |
| 6 | Segment table dropped before query | Error handling |
| 7 | Segment table dropped before server restart | Graceful handling (see `hybrid_dropped_segment_repro.py`) |
| 8 | Concurrent reads from multiple sessions | No data races |
| 9 | Concurrent reads during watermark update | Atomic transition |
| 10 | Segment with no matching table function | Error at CREATE TABLE |
| 11 | Invalid predicate expression | Error at CREATE TABLE |
| 12 | Predicate referencing non-existent column | Error at CREATE TABLE or query time |
| 13 | Single segment (only one table_function + predicate) | Minimum valid configuration |

---

## 12. Use-Case Scenarios

End-to-end workflows that validate real-world usage patterns.

### 12.1 Hot/Cold Tiered Storage

1. Create MergeTree table (hot)
2. Create Iceberg/S3 table (cold)
3. Create Hybrid table with date watermark
4. INSERT new data into Hybrid (goes to hot)
5. Verify queries spanning both tiers return correct results
6. EXPORT PART from hot to cold
7. Update watermark via `CREATE OR REPLACE TABLE`
8. Verify queries still return correct results from the new routing

### 12.2 Zero-Downtime Migration

1. Create old MergeTree table with data
2. Create new MergeTree table (different cluster or schema)
3. Create Hybrid table routing old/new by date
4. Migrate data batch by batch, moving watermark each time
5. Verify no data loss or duplication during migration

### 12.3 Resharding

1. Old cluster with N shards
2. New cluster with M shards (M > N)
3. Hybrid table routes by date: old cluster for old data, new cluster for new
4. Re-shard historical data day by day
5. Move watermark forward after each day is resharded

### 12.4 Cache Layer

1. Iceberg table with large dataset
2. MergeTree table with frequently accessed subset
3. Hybrid table routes hot range to MergeTree, rest to Iceberg
4. Verify reads from both tiers are correct and performant

---

## 13. Test Priority Matrix

Combining dimensions into a prioritized test plan.

### Priority 1 (Must Have)

- MergeTree + MergeTree with date watermark, mutually exclusive predicates
- MergeTree + Iceberg with date watermark
- Basic SELECT, WHERE, GROUP BY, ORDER BY, LIMIT
- COUNT, SUM, AVG, MIN, MAX aggregations
- INSERT goes to first segment only
- `prefer_localhost_replica=0` and `=1`
- `hybrid_table_auto_cast_columns` with type mismatches
- CREATE TABLE / DROP TABLE / CREATE OR REPLACE TABLE
- Data correctness via hash comparison

### Priority 2 (Should Have)

- MergeTree + S3 Parquet
- MergeTree + icebergCluster
- `serialize_query_plan=0` and `=1`
- All four distributed subquery execution modes
- JOINs (INNER, LEFT, RIGHT, FULL OUTER)
- Subqueries, UNION ALL, CTEs
- Window functions
- HAVING, DISTINCT
- Overlapping predicates (duplicate detection)
- DETACH/ATTACH cycle
- Server restart with Hybrid table
- EXPLAIN plan verification

### Priority 3 (Nice to Have)

- Three+ segments
- Distributed-over-distributed
- Complex predicate expressions (BETWEEN, IN, LIKE, function-based)
- Concurrent access during watermark update
- Segment table dropped edge cases
- Very large datasets
- remoteSecure, clusterAllReplicas
- WITH ROLLUP, WITH CUBE, WITH TOTALS
- Nested Hybrid tables

---

## 14. Combined Settings Matrix

The full combinatorial space of settings that should be tested (at minimum for
key query types).

| enable_analyzer | prefer_localhost_replica | serialize_query_plan | hybrid_table_auto_cast_columns | Notes |
|----------------|------------------------|---------------------|-------------------------------|-------|
| 1 | 1 (default) | 0 (default) | 0 | Baseline (default settings) |
| 1 | 0 | 0 | 0 | All-remote execution path |
| 1 | 1 | 1 | 0 | Serialized plan, local+remote mix |
| 1 | 0 | 1 | 0 | Serialized plan, all-remote |
| 1 | 1 | 0 | 1 | Auto-cast enabled |
| 1 | 0 | 0 | 1 | Auto-cast + all-remote |
| 1 | 1 | 1 | 1 | All features enabled |
| 1 | 0 | 1 | 1 | All features enabled + all-remote |

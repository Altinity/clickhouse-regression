---
description: 'Hybrid unions multiple data sources behind per-segment predicates so queries behave like a single table while data is migrated or tiered.'
slug: /engines/table-engines/special/hybrid
title: 'Hybrid Table Engine'
sidebar_label: 'Hybrid'
sidebar_position: 11
---

# Hybrid table engine

`Hybrid` builds on top of the [Distributed](./distributed.md) table engine. It lets you expose several data sources as one logical table and assign every source its own predicate.
The engine rewrites incoming queries so that each segment receives the original query plus its predicate. This keeps all of the Distributed optimisations (remote aggregation, `skip_unused_shards`,
global JOIN pushdown, and so on) while you duplicate or migrate data across clusters, storage types, or formats.

It keeps the same execution pipeline as `engine=Distributed` but can read from multiple underlying sources simultaneously—similar to `engine=Merge`—while still pushing logic down to each source.

Typical use cases include:

- Zero-downtime migrations where "old" and "new" replicas temporarily overlap.
- Tiered storage, for example fresh data on a local cluster and historical data in S3.
- Gradual roll-outs where only a subset of rows should be served from a new backend.

By giving mutually exclusive predicates to the segments (for example, `date < watermark` and `date >= watermark`), you ensure that each row is read from exactly one source.

## How it works

The Hybrid engine extends the `Distributed` table engine to support multiple heterogeneous data sources (segments) with per-segment predicates. When a query is executed:

1. **Query Rewrite**: The engine rewrites the incoming query once per segment, replacing the Hybrid table reference with the segment's underlying table function and adding the segment's predicate to the WHERE clause with an `AND` operator.

2. **Parallel Execution**: Each rewritten query is executed independently, maintaining all Distributed optimizations:
   - Remote aggregation (GROUP BY pushdown)
   - ORDER BY pushdown
   - `skip_unused_shards` optimization
   - JOIN pushdown
   - Global query optimizations

3. **Result Union**: Results from all segments are combined (using a UnionStep), producing a single result set as if querying a single distributed table.

### Query Rewrite Example

Given a Hybrid table:
```sql
ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'
)
```

A user query:
```sql
SELECT user_id, sum(bytes) FROM hybrid
WHERE date >= '2025-02-01'
GROUP BY user_id;
```

Is rewritten for each segment:

**Segment 1 (hot):**
```sql
SELECT user_id, sum(bytes)
FROM remote('hot_cluster', 'db', 'table')
WHERE (date >= '2025-01-01') AND (date >= '2025-02-01')
GROUP BY user_id;
```

**Segment 2 (cold):**
```sql
SELECT user_id, sum(bytes)
FROM s3Cluster('cold_cluster', 's3://bucket/path')
WHERE (date < '2025-01-01') AND (date >= '2025-02-01')
GROUP BY user_id;
```

The second segment's query is automatically pruned because the WHERE clause contradicts the predicate (no rows can satisfy both `date < '2025-01-01'` and `date >= '2025-02-01'`).


## Enable the engine

The Hybrid engine is experimental. Enable it per session (or in the user profile) before creating tables:

```sql
SET allow_experimental_hybrid_table = 1;
```

### Automatic Type Alignment

Hybrid segments can evolve independently, so the same logical column may use different physical types across segments. For example:
- MergeTree segment: `UInt64`
- Iceberg segment: `Decimal128`

When `hybrid_table_auto_cast_columns = 1` is enabled (requires `allow_experimental_analyzer = 1`), the engine automatically inserts the necessary `CAST` operations into each rewritten query so every shard receives the schema defined by the Hybrid table. This prevents header mismatches without having to edit each query.

**How it works:**
1. The engine compares column types across all segments
2. For mismatched columns, it identifies the target type from the Hybrid table definition
3. It injects `CAST(column AS target_type)` into the query tree for each segment
4. All segments return compatible types, allowing seamless UNION

**Example:**
```sql
-- Hybrid table defines: value UInt64
-- Segment 1 (MergeTree): value UInt64
-- Segment 2 (Iceberg): value Decimal128

-- With auto-cast enabled, Segment 2 query becomes:
SELECT CAST(value AS UInt64) AS value FROM iceberg_segment ...
```

**Important Notes:**
- Auto-casting requires the analyzer (`allow_experimental_analyzer = 1`)
- Casts are applied to both sides when types differ (even if one side already has the correct type)
- For aggregate functions, casts must be applied before aggregation, not after
- Manual casts in your SQL queries will still work but may result in double-casting

**When to use:**
- Enable when segments have different physical types but represent the same logical data
- Disable if you prefer explicit casts in your queries or if analyzer is not available


## Engine definition

```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name
(
    column1 type1,
    column2 type2,
    ...
)
ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_2, predicate_2 ...])
```

You must pass at least two arguments – the first table function and its predicate. Additional sources are appended as `table_function, predicate` pairs. The first table function is also used for `INSERT` statements.

You can also skip the column definition:
```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name
ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_2, predicate_2 ...])
```

In this case, the engine will automatically detect the columns and types from the first table function.

### Arguments and behaviour

- `table_function_n` must be a valid table function (for example `remote`, `remoteSecure`, `cluster`, `clusterAllReplicas`, `s3Cluster`) or a fully qualified table name (`database.table`). The first argument must be a table function—such as `remote` or `cluster`—because it instantiates the underlying `Distributed` storage.
- `predicate_n` must be an expression that can be evaluated on the table columns. The engine adds it to the segment's query with an additional `AND`, so expressions like `event_date >= '2025-09-01'` or `id BETWEEN 10 AND 15` are typical.
- The query planner picks the same processing stage for every segment as it does for the base `Distributed` plan, so remote aggregation, ORDER BY pushdown, `skip_unused_shards`, and the legacy/analyzer execution modes behave the same way.
- Align schemas across the segments. ClickHouse builds a common header; if the physical types differ you may need to add casts on one side or in the query, just as you would when reading from heterogeneous replicas.


## Watermark and data lifecycle

Hybrid tables use a **watermark** pattern to determine which segment serves each row. The watermark is a deterministic rule encoded in the segment predicates.

### Typical Pattern

The most common pattern uses a date-based watermark:

```sql
ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'
)
```

- **Hot data** (`date >= '2025-01-01'`) → Served from MergeTree cluster for low-latency queries
- **Cold data** (`date < '2025-01-01'`) → Served from object storage (S3/Iceberg) for cost efficiency

### Data Migration Timeline

```
Time →
MergeTree (hot)        Warm copy zone           Iceberg (cold)
│───────────│──────────────│─────────────────────────────────
keep ~5 days   export 5→7d     persistent archive
                  ↑
             watermark moves
```

### How to update the watermark

Use `CREATE OR REPLACE TABLE` to update the watermark of the Hybrid table definition:

```sql
-- Original table with watermark at '2025-01-01'
CREATE TABLE hybrid_table ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'
) AS source_table;

-- After exporting data from hot to cold storage, update watermark to '2025-02-01'
CREATE OR REPLACE TABLE hybrid_table ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-02-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-02-01'
) AS source_table;
```

The `CREATE OR REPLACE` operation is atomic—all queries immediately see the new watermark after the statement completes. There's no window where queries might see inconsistent routing or read from both segments for the same data range.



## INSERT behavior

`INSERT` statements into a Hybrid table are **always forwarded to the first segment only**. This design choice:

- Supports double-write scenarios where you write to hot storage and later export to cold
- Enables cache-layer setups where writes go to a fast layer
- Avoids ambiguous write targets when multiple segments could match

**Example:**
```sql
-- All inserts go to the first (hot) segment
INSERT INTO hybrid VALUES (...);

-- For multi-destination writes, use explicit inserts:
INSERT INTO hot_table VALUES (...);
INSERT INTO cold_table VALUES (...);
```

**Best Practice**: Design your data pipeline so that:
1. New data is inserted into the first (hot) segment
2. A background process exports data from hot to cold storage
3. After verification, update the Hybrid table watermark to route queries to cold storage for older data


## Example: local cluster plus S3 historical tier

The following commands illustrate a two-segment layout. Hot data stays on a local ClickHouse cluster, while historical rows come from public S3 Parquet files.

```sql
-- Local MergeTree table that keeps current data
CREATE OR REPLACE TABLE btc_blocks_local
(
    `hash` FixedString(64),
    `version` Int64,
    `mediantime` DateTime64(9),
    `nonce` Int64,
    `bits` FixedString(8),
    `difficulty` Float64,
    `chainwork` FixedString(64),
    `size` Int64,
    `weight` Int64,
    `coinbase_param` String,
    `number` Int64,
    `transaction_count` Int64,
    `merkle_root` FixedString(64),
    `stripped_size` Int64,
    `timestamp` DateTime64(9),
    `date` Date
)
ENGINE = MergeTree
ORDER BY (timestamp)
PARTITION BY toYYYYMM(date);

-- Hybrid table that unions the local shard with historical data in S3
CREATE OR REPLACE TABLE btc_blocks ENGINE = Hybrid(
    remote('localhost:9000', currentDatabase(), 'btc_blocks_local'), date >= '2025-09-01',
    s3('s3://aws-public-blockchain/v1.0/btc/blocks/**.parquet', NOSIGN), date < '2025-09-01'
) AS btc_blocks_local;

-- Writes target the first (remote) segment
INSERT INTO btc_blocks
SELECT *
FROM s3('s3://aws-public-blockchain/v1.0/btc/blocks/**.parquet', NOSIGN)
WHERE date BETWEEN '2025-09-01' AND '2025-09-30';

-- Reads seamlessly combine both predicates
SELECT * FROM btc_blocks WHERE date = '2025-08-01'; -- data from s3
SELECT * FROM btc_blocks WHERE date = '2025-09-05'; -- data from MergeTree (TODO: still analyzes s3)
SELECT * FROM btc_blocks WHERE date IN ('2025-08-31','2025-09-01') -- data from both sources, single copy always


-- Run analytic queries as usual
SELECT
    date,
    count(),
    uniqExact(CAST(hash, 'Nullable(String)')) AS hashes,
    sum(CAST(number, 'Nullable(Int64)')) AS blocks_seen
FROM btc_blocks
WHERE date BETWEEN '2025-08-01' AND '2025-09-30'
GROUP BY date
ORDER BY date;
```

Because the predicates are applied inside every segment, queries such as `ORDER BY`, `GROUP BY`, `LIMIT`, `JOIN`, and `EXPLAIN` behave as if you were reading from a single `Distributed` table. When sources expose different physical types (for example `FixedString(64)` versus `String` in Parquet), add explicit casts during ingestion or in the query, as shown above.

## Best practices

### Schema Design

1. **Align schemas across segments**: While auto-casting can handle differences, matching schemas eliminates overhead and potential issues.

2. **Use mutually exclusive predicates**: Ensure predicates don't overlap to prevent reading the same row from multiple segments:
   ```
   -- Good: Mutually exclusive
   1. date >= '2025-01-01' - first segment
   2. date < '2025-01-01' - second segment
   
   -- Bad: Overlapping (may cause duplicates)
   1. date >= '2025-01-01' - first segment
   2. date >= '2025-01-15' - second segment
   ```

3. **Choose appropriate watermark column**: Use a column that:
   - Exists in all segments
   - Represents a natural data boundary (date, timestamp, etc.)


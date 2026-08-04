# SRS-048 ClickHouse Hybrid Table Engine
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Engine Definition](#engine-definition)
    * 2.1 [RQ.ClickHouse.Hybrid.Create](#rqclickhousehybridcreate)
    * 2.2 [RQ.ClickHouse.Hybrid.FirstSegment](#rqclickhousehybridfirstsegment)
    * 2.3 [RQ.ClickHouse.Hybrid.AdditionalSegments](#rqclickhousehybridadditionalsegments)
    * 2.4 [RQ.ClickHouse.Hybrid.SchemaInference](#rqclickhousehybridschemainference)
    * 2.5 [RQ.ClickHouse.Hybrid.ExperimentalGate](#rqclickhousehybridexperimentalgate)
    * 2.6 [RQ.ClickHouse.Hybrid.AnalyzerRequired](#rqclickhousehybridanalyzerrequired)
* 3 [Segment Predicates (Watermarks)](#segment-predicates-watermarks)
    * 3.1 [RQ.ClickHouse.Hybrid.Watermark.Exclusive](#rqclickhousehybridwatermarkexclusive)
    * 3.2 [RQ.ClickHouse.Hybrid.Watermark.Overlap](#rqclickhousehybridwatermarkoverlap)
    * 3.3 [RQ.ClickHouse.Hybrid.Watermark.Replace](#rqclickhousehybridwatermarkreplace)
    * 3.4 [RQ.ClickHouse.Hybrid.PredicatePruning](#rqclickhousehybridpredicatepruning)
* 4 [INSERT Behavior](#insert-behavior)
    * 4.1 [RQ.ClickHouse.Hybrid.Insert.FirstSegmentOnly](#rqclickhousehybridinsertfirstsegmentonly)
* 5 [Automatic Type Alignment](#automatic-type-alignment)
    * 5.1 [RQ.ClickHouse.Hybrid.AutoCast](#rqclickhousehybridautocast)
    * 5.2 [RQ.ClickHouse.Hybrid.TypeSeams](#rqclickhousehybridtypeseams)
* 6 [Query Semantics](#query-semantics)
    * 6.1 [RQ.ClickHouse.Hybrid.QueryShapes](#rqclickhousehybridqueryshapes)
    * 6.2 [RQ.ClickHouse.Hybrid.CorrectnessVsUnion](#rqclickhousehybridcorrectnessvsunion)
* 7 [Distributed Execution Paths](#distributed-execution-paths)
    * 7.1 [RQ.ClickHouse.Hybrid.LocalVsRemote](#rqclickhousehybridlocalvsremote)
    * 7.2 [RQ.ClickHouse.Hybrid.SerializeQueryPlan](#rqclickhousehybridserializequeryplan)
    * 7.3 [RQ.ClickHouse.Hybrid.AggregationStages](#rqclickhousehybridaggregationstages)
    * 7.4 [RQ.ClickHouse.Hybrid.DistributedOverDistributed](#rqclickhousehybriddistributedoverdistributed)
* 8 [Segment Storage Types](#segment-storage-types)
    * 8.1 [RQ.ClickHouse.Hybrid.Segment.MergeTree](#rqclickhousehybridsegmentmergetree)
    * 8.2 [RQ.ClickHouse.Hybrid.Segment.Iceberg](#rqclickhousehybridsegmenticeberg)
    * 8.3 [RQ.ClickHouse.Hybrid.Segment.IcebergCatalogs](#rqclickhousehybridsegmenticebergcatalogs)
    * 8.4 [RQ.ClickHouse.Hybrid.Segment.IcebergCluster](#rqclickhousehybridsegmenticebergcluster)
    * 8.5 [RQ.ClickHouse.Hybrid.Segment.S3Parquet](#rqclickhousehybridsegments3parquet)
* 9 [Schema Variety and Refresh](#schema-variety-and-refresh)
    * 9.1 [RQ.ClickHouse.Hybrid.SchemaVariety](#rqclickhousehybridschemavariety)
    * 9.2 [RQ.ClickHouse.Hybrid.SchemaRefresh](#rqclickhousehybridschemarefresh)
* 10 [Topology](#topology)
    * 10.1 [RQ.ClickHouse.Hybrid.Topology.SecureCluster](#rqclickhousehybridtopologysecurecluster)
    * 10.2 [RQ.ClickHouse.Hybrid.Topology.ClusterAllReplicas](#rqclickhousehybridtopologyclusterallreplicas)
    * 10.3 [RQ.ClickHouse.Hybrid.Topology.ThreeSegments](#rqclickhousehybridtopologythreesegments)
* 11 [Lifecycle and Tiered Storage](#lifecycle-and-tiered-storage)
    * 11.1 [RQ.ClickHouse.Hybrid.Lifecycle.ExportThenWatermark](#rqclickhousehybridlifecycleexportthenwatermark)
    * 11.2 [RQ.ClickHouse.Hybrid.Lifecycle.OverlapDiscipline](#rqclickhousehybridlifecycleoverlapdiscipline)
    * 11.3 [RQ.ClickHouse.Hybrid.Lifecycle.ReplaceDistributed](#rqclickhousehybridlifecyclereplacedistributed)
* 12 [Operational Behavior](#operational-behavior)
    * 12.1 [RQ.ClickHouse.Hybrid.Operational.UnreachableCold](#rqclickhousehybridoperationalunreachablecold)
    * 12.2 [RQ.ClickHouse.Hybrid.Operational.ExportLag](#rqclickhousehybridoperationalexportlag)
* 13 [External Readers](#external-readers)
    * 13.1 [RQ.ClickHouse.Hybrid.ExternalReader.Iceberg](#rqclickhousehybridexternalreadericeberg)
* 14 [Query Fuzzing Coverage](#query-fuzzing-coverage)
    * 14.1 [RQ.ClickHouse.Hybrid.QueryFuzzing](#rqclickhousehybridqueryfuzzing)

## Introduction

The Hybrid table engine builds on top of the Distributed table engine. It allows exposing several data sources as one logical table and assigning every source its own predicate. This keeps all of the Distributed optimisations (`remote aggregation`, `skip_unused_shards`, global JOIN pushdown, and so on) while copying or migrating data across clusters, storage types, or formats.

Typical use cases include:

* Zero-downtime migrations where "old" and "new" replicas temporarily overlap
* Tiered storage, for example fresh data on a local cluster and historical data in S3 / Iceberg
* Gradual roll-outs where only a subset of rows should be served from a new backend

By giving mutually exclusive predicates to the segments (for example, `date < watermark` and `date >= watermark`), each row is read from exactly one source.

This specification defines the normative requirements for Hybrid. Behavior with `enable_analyzer = 0`, `SHARED NAMED SCALAR` / dynamic watermarks, and `TTL … EXPORT TO` is out of scope.

[ClickHouse]: https://clickhouse.com

## Engine Definition

### RQ.ClickHouse.Hybrid.Create
version: 1.0

[ClickHouse] SHALL support creating Hybrid tables with the following SQL syntax:

```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name
(
    column1 type1,
    column2 type2,
    ...
)
ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_2, predicate_2 ...])
```

[ClickHouse] SHALL require at least one `table_function, predicate` pair. Additional sources are appended as further `table_function, predicate` pairs.

### RQ.ClickHouse.Hybrid.FirstSegment
version: 1.0

[ClickHouse] SHALL require `table_function_1` to be a table function that instantiates underlying Distributed storage, such as:
* `remote`
* `remoteSecure`
* `cluster`
* `clusterAllReplicas`

The first table function SHALL also be the target of `INSERT` statements.

### RQ.ClickHouse.Hybrid.AdditionalSegments
version: 1.0

[ClickHouse] SHALL accept subsequent segments as either:
* A valid table function (for example `remote`, `remoteSecure`, `cluster`, `clusterAllReplicas`, `s3`, `s3Cluster`, `icebergCluster`), or
* A fully qualified table name (`database.table`)

Each `predicate_n` SHALL be an expression evaluated on the table columns. The engine SHALL add it to the segment’s query with an additional `AND` (for example `event_date >= '2025-09-01'` or `id BETWEEN 10 AND 15`).

### RQ.ClickHouse.Hybrid.SchemaInference
version: 1.0

[ClickHouse] SHALL support omitting the explicit column list:

```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name
ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_n, predicate_n ...])
```

In this case, [ClickHouse] SHALL detect columns and types from the first table function (including `CREATE … AS source_table` style definitions).

### RQ.ClickHouse.Hybrid.ExperimentalGate
version: 1.0

The Hybrid engine is experimental. [ClickHouse] SHALL gate Hybrid DDL behind `allow_experimental_hybrid_table`. When the setting is disabled, creating a Hybrid table SHALL fail. When enabled (session or profile), Hybrid DDL SHALL succeed:

```sql
SET allow_experimental_hybrid_table = 1;
```

### RQ.ClickHouse.Hybrid.AnalyzerRequired
version: 1.0

[ClickHouse] SHALL support Hybrid only with `enable_analyzer = 1` (formerly `allow_experimental_analyzer = 1`). Behavior with `enable_analyzer = 0` is not supported.

## Segment Predicates (Watermarks)

A **watermark** is a routing rule that determines which segments serve each row. In Hybrid tables, the watermark is encoded as predicates (SQL expressions) assigned to each segment. When a query executes, the engine evaluates each row against all segment predicates. A row that matches a predicate is served from that segment’s underlying storage.

**Predicate expression** examples: `date >= '2025-01-01'`, `id BETWEEN 10 AND 15`, `region = 'US'`.

The most common pattern uses a date-based watermark:

```sql
ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'
)
```

* **Hot data** (`date >= '2025-01-01'`) → MergeTree / cluster for low-latency queries
* **Cold data** (`date < '2025-01-01'`) → Object storage (S3 / Iceberg) for cost efficiency

### RQ.ClickHouse.Hybrid.Watermark.Exclusive
version: 1.0

[ClickHouse] SHALL support mutually exclusive segment predicates such that each logical row is read from exactly one segment, and Hybrid query results match an exclusive `UNION ALL` reference over the same segments and predicates (no duplicates, no gaps for rows present in the covered dataset).

Example of mutually exclusive predicates:
* `date >= '2025-01-01'` — first segment
* `date < '2025-01-01'` — second segment

### RQ.ClickHouse.Hybrid.Watermark.Overlap
version: 1.0

[ClickHouse] SHALL allow overlapping predicates. A single row may match multiple predicates and be served from multiple segments, which MAY produce duplicate rows in query results relative to a distinct exclusive reference.

Example of overlapping predicates (may cause duplicates):
* `date >= '2025-01-01'` — first segment
* `date >= '2025-01-15'` — second segment

### RQ.ClickHouse.Hybrid.Watermark.Replace
version: 1.0

[ClickHouse] SHALL support updating Hybrid watermarks via `CREATE OR REPLACE TABLE` with new static predicates. The replace operation SHALL be atomic: after the statement completes, all queries SHALL see the new watermark with no window of inconsistent routing for the same data range.

```sql
-- Original watermark at '2025-01-01'
CREATE TABLE hybrid_table ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'
) AS source_table;

-- Advance watermark to '2025-02-01' after exporting hot → cold
CREATE OR REPLACE TABLE hybrid_table ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-02-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-02-01'
) AS source_table;
```

### RQ.ClickHouse.Hybrid.PredicatePruning
version: 1.0

[ClickHouse] SHALL prune segments that cannot contribute rows when a query’s `WHERE` clause is exclusive to one watermark band, while still returning results identical to the exclusive reference for that band.

## INSERT Behavior

### RQ.ClickHouse.Hybrid.Insert.FirstSegmentOnly
version: 1.0

[ClickHouse] SHALL forward every `INSERT INTO` a Hybrid table exclusively to the first segment, including rows whose values would match a later segment’s predicate.

This design:
* Supports double-write scenarios where data is written to hot storage and later exported to cold
* Enables cache-layer setups where writes go to a fast layer
* Avoids ambiguous write targets when multiple segments could match

```sql
-- All inserts go to the first (hot) segment
INSERT INTO hybrid VALUES (...);

-- For multi-destination writes, use explicit inserts:
INSERT INTO hot_table VALUES (...);
INSERT INTO cold_table VALUES (...);
```

## Automatic Type Alignment

Segments can evolve independently, so the same logical column may use different physical types across segments (for example MergeTree `Decimal` vs Iceberg `Int`, or MergeTree `FixedString` vs Parquet `String`).

### RQ.ClickHouse.Hybrid.AutoCast
version: 1.0

When `hybrid_table_auto_cast_columns = 1` is enabled (requires `enable_analyzer = 1`), [ClickHouse] SHALL insert the necessary `CAST` operations so every shard / segment receives the schema defined by the Hybrid table header, preventing `CANNOT_CONVERT_TYPE` / `NO_COMMON_TYPE` failures for modest type seams.

Manual casts in user SQL remain allowed but MAY result in double-casting.

### RQ.ClickHouse.Hybrid.TypeSeams
version: 1.0

With auto-cast enabled, [ClickHouse] SHALL support Hybrid queries across at least the following seams when headers are declared appropriately:
* Unsigned integer vs signed counterpart (for example `UInt64` ↔ `Int64`, `UInt32` ↔ `Int32`) on MergeTree↔MergeTree and MergeTree↔Iceberg
* `FixedString(N)` ↔ `String`
* Aggregate paths such as `uniq` across those seams

When auto-cast is disabled, [ClickHouse] MAY reject incompatible seams.

## Query Semantics

Because predicates are applied inside every segment, Hybrid queries behave as if reading from a single Distributed table for shapes such as `ORDER BY`, `GROUP BY`, `LIMIT`, `JOIN`, and `EXPLAIN`.

Illustrative two-segment layout (hot MergeTree + historical S3 Parquet):

```sql
CREATE OR REPLACE TABLE btc_blocks_local
(
    `hash` FixedString(64),
    `number` Int64,
    `date` Date
    -- ...
)
ENGINE = MergeTree
ORDER BY (date)
PARTITION BY toYYYYMM(date);

CREATE OR REPLACE TABLE btc_blocks ENGINE = Hybrid(
    remote('localhost:9000', currentDatabase(), 'btc_blocks_local'), date >= '2025-09-01',
    s3('s3://aws-public-blockchain/v1.0/btc/blocks/**.parquet', NOSIGN), date < '2025-09-01'
) AS btc_blocks_local;
```

When sources expose different physical types (for example `FixedString(64)` versus `String` in Parquet), use auto-cast and/or explicit casts during ingestion or in the query.

### RQ.ClickHouse.Hybrid.QueryShapes
version: 1.0

[ClickHouse] SHALL support core analytic query shapes on Hybrid tables, including:
* Filtered `SELECT`
* `GROUP BY` aggregates (`count`, `sum`, `min`, `max`, and similar)
* `ORDER BY` / `LIMIT`
* Multi-segment scans that combine hot and cold predicates

### RQ.ClickHouse.Hybrid.CorrectnessVsUnion
version: 1.0

For mutually exclusive watermarks, [ClickHouse] SHALL return Hybrid results that match an exclusive `UNION ALL` reference constructed from the same segments and predicates (stable fingerprints / aggregates), including under Distributed path settings exercised by the suite.

## Distributed Execution Paths

Because Hybrid builds on Distributed, it inherits independent execution paths that SHALL all produce correct results.

### RQ.ClickHouse.Hybrid.LocalVsRemote
version: 1.0

[ClickHouse] SHALL produce correct Hybrid results for both:
* Local execution of subquery plans on the initiator (`prefer_localhost_replica = 1`)
* Forcing remote treatment of the local replica (`prefer_localhost_replica = 0`)

### RQ.ClickHouse.Hybrid.SerializeQueryPlan
version: 1.0

[ClickHouse] SHALL produce correct Hybrid results when remote work is sent as:
* SQL text (`serialize_query_plan = 0`, default), and
* A serialized query plan (`serialize_query_plan = 1`)

### RQ.ClickHouse.Hybrid.AggregationStages
version: 1.0

[ClickHouse] SHALL produce correct Hybrid aggregation results across remote aggregation stages, including:
* `complete`
* `with_mergeable_state`
* `with_mergeable_state_after_aggregation`
* `with_mergeable_state_after_aggregation_and_limit`

### RQ.ClickHouse.Hybrid.DistributedOverDistributed
version: 1.0

[ClickHouse] SHALL support Hybrid layouts where the first segment reads through a Distributed table (Distributed-over-Distributed), preserving fingerprint equality versus an exclusive reference.

## Segment Storage Types

### RQ.ClickHouse.Hybrid.Segment.MergeTree
version: 1.0

[ClickHouse] SHALL support Hybrid segments backed by MergeTree-family tables accessed via `remote` / `cluster` / `clusterAllReplicas`.

### RQ.ClickHouse.Hybrid.Segment.Iceberg
version: 1.0

[ClickHouse] SHALL support Hybrid cold (or other) segments backed by Iceberg tables / IcebergS3 destinations with exclusive watermarks and correct query results versus the exclusive reference.

### RQ.ClickHouse.Hybrid.Segment.IcebergCatalogs
version: 1.0

[ClickHouse] SHALL support Hybrid Iceberg segments under at least the following catalog modes:
* No external catalog (IcebergS3 / path-based)
* Iceberg REST catalog
* Glue catalog

### RQ.ClickHouse.Hybrid.Segment.IcebergCluster
version: 1.0

[ClickHouse] SHALL support Hybrid segments using `icebergCluster(...)`, including settings such as `object_storage_cluster_join_mode = 'local'` where applicable, with correct query results.

### RQ.ClickHouse.Hybrid.Segment.S3Parquet
version: 1.0

[ClickHouse] SHALL support Hybrid segments backed by `s3(...)` and `s3Cluster(...)` Parquet sources with correct query results versus the exclusive reference.

## Schema Variety and Refresh

### RQ.ClickHouse.Hybrid.SchemaVariety
version: 1.0

[ClickHouse] SHALL support Hybrid correctness for reduced-scale schema variety shapes that stress type mapping, including:
* Financial: `Decimal`, `FixedString`, `Enum8`
* Telemetry: `LowCardinality`, `DateTime64`, `Map`
* Logs: `String`, `Array`
* Iceberg-compatible nested types (`DateTime64`, `Array`, `Map`) on MergeTree + Iceberg

### RQ.ClickHouse.Hybrid.SchemaRefresh
version: 1.0

After a segment schema change such as `ADD COLUMN`, [ClickHouse] SHALL allow refreshing the Hybrid table header via `CREATE OR REPLACE` (including `ON CLUSTER` when the left segment is cluster-scoped) so subsequent queries see the updated columns.

## Topology

### RQ.ClickHouse.Hybrid.Topology.SecureCluster
version: 1.0

[ClickHouse] SHALL support Hybrid first segments over TLS-secured remote server configurations (secure cluster entries / `remoteSecure` path as configured in the deployment).

### RQ.ClickHouse.Hybrid.Topology.ClusterAllReplicas
version: 1.0

[ClickHouse] SHALL support Hybrid segments using `clusterAllReplicas(...)` with correct results versus the exclusive reference.

### RQ.ClickHouse.Hybrid.Topology.ThreeSegments
version: 1.0

[ClickHouse] SHALL support Hybrid tables with three or more exclusive predicate bands (for example hot / warm / cold) and return results matching the corresponding multi-way exclusive `UNION ALL` reference.

## Lifecycle and Tiered Storage

Recommended pipeline:
1. Insert new data into the first (hot) segment
2. Background process exports data from hot to cold storage (for example `EXPORT PARTITION`)
3. After verification, `CREATE OR REPLACE` the Hybrid table to advance the static watermark
4. Optionally delete the exported range from MergeTree **only after** the watermark has advanced

### RQ.ClickHouse.Hybrid.Lifecycle.ExportThenWatermark
version: 1.0

[ClickHouse] SHALL support the end-to-end tiered lifecycle:
* Hybrid over exportable MergeTree + Iceberg with a static watermark
* `EXPORT PARTITION` of cold bands into Iceberg
* `CREATE OR REPLACE` advancing the static watermark
* Delete of the exported range from MergeTree after the watermark advances

with Hybrid results matching the exclusive reference (no gaps, no duplicates for the covered dataset).

### RQ.ClickHouse.Hybrid.Lifecycle.OverlapDiscipline
version: 1.0

[ClickHouse] SHALL leave a detectable gap (missing newly cold rows) if the watermark is advanced without exporting the newly cold range into the cold segment first.

### RQ.ClickHouse.Hybrid.Lifecycle.ReplaceDistributed
version: 1.0

[ClickHouse] SHALL allow replacing a Distributed head over local MergeTree with a Hybrid head (`cluster(...)` + Iceberg or equivalent) such that:
* Query fingerprints match the prior Distributed baseline under localhost preference settings
* `INSERT` continues to land on the local / first-segment storage

## Operational Behavior

### RQ.ClickHouse.Hybrid.Operational.UnreachableCold
version: 1.0

When the cold Iceberg segment is dropped or otherwise unreachable, [ClickHouse] SHALL still serve queries whose predicates are exclusive to the hot watermark band. Full scans that require the missing cold segment MAY error or return an incomplete set.

### RQ.ClickHouse.Hybrid.Operational.ExportLag
version: 1.0

While the cold Iceberg segment is empty and the static watermark already routes a date band to cold, [ClickHouse] SHALL return only the hot-band rows for full Hybrid scans. After `EXPORT PARTITION` fills that cold band, Hybrid SHALL cover the full exclusive dataset.

## External Readers

### RQ.ClickHouse.Hybrid.ExternalReader.Iceberg
version: 1.0

After cold data has been exported into the Iceberg segment used by Hybrid, an external Iceberg reader (for example PyIceberg) SHALL observe the same cold-band row count as ClickHouse when reading that destination.

## Query Fuzzing Coverage

### RQ.ClickHouse.Hybrid.QueryFuzzing
version: 1.0

[ClickHouse] SHALL successfully execute a broad, non-interactive set of Hybrid query shapes (including curated Hybrid SQL and upstream-derived patterns such as windows, `LIMIT BY`, CTEs, and `GLOBAL IN`) against Hybrid topologies that combine MergeTree and Iceberg / `icebergCluster` segments.

Known Distributed / Hybrid limitations that are not Hybrid regressions (for example correlated subqueries on remote tables, and Nullable null-map access on some remote Iceberg paths) MAY be excluded until product support exists.

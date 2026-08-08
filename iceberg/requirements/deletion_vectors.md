# SRS-048 ClickHouse Iceberg v3 Deletion Vectors Read Support
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Scope](#feature-scope)
    * 2.1 [RQ.Iceberg.DeletionVectors.Read](#rqicebergdeletionvectorsread)
    * 2.2 [RQ.Iceberg.DeletionVectors.ReadOnly](#rqicebergdeletionvectorsreadonly)
    * 2.3 [RQ.Iceberg.DeletionVectors.AccessForms](#rqicebergdeletionvectorsaccessforms)
    * 2.4 [RQ.Iceberg.DeletionVectors.StorageBackends](#rqicebergdeletionvectorsstoragebackends)
* 3 [Producing Operations](#producing-operations)
    * 3.1 [RQ.Iceberg.DeletionVectors.WriterOperations](#rqicebergdeletionvectorswriteroperations)
* 4 [Vector Content Shapes](#vector-content-shapes)
    * 4.1 [RQ.Iceberg.DeletionVectors.EmptyVector](#rqicebergdeletionvectorsemptyvector)
    * 4.2 [RQ.Iceberg.DeletionVectors.AllRowsDeleted](#rqicebergdeletionvectorsallrowsdeleted)
    * 4.3 [RQ.Iceberg.DeletionVectors.BoundaryPositions](#rqicebergdeletionvectorsboundarypositions)
    * 4.4 [RQ.Iceberg.DeletionVectors.RowGroupBoundaries](#rqicebergdeletionvectorsrowgroupboundaries)
    * 4.5 [RQ.Iceberg.DeletionVectors.SharedPuffinFile](#rqicebergdeletionvectorssharedpuffinfile)
* 5 [Coexistence With Other Delete Formats](#coexistence-with-other-delete-formats)
    * 5.1 [RQ.Iceberg.DeletionVectors.Coexistence.AcrossDataFiles](#rqicebergdeletionvectorscoexistenceacrossdatafiles)
    * 5.2 [RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes](#rqicebergdeletionvectorscoexistencesupersedespositiondeletes)
    * 5.3 [RQ.Iceberg.DeletionVectors.Coexistence.EqualityDeletes](#rqicebergdeletionvectorscoexistenceequalitydeletes)
    * 5.4 [RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError](#rqicebergdeletionvectorscoexistencemultiplevectorserror)
    * 5.5 [RQ.Iceberg.DeletionVectors.Coexistence.FormatVersionUpgrade](#rqicebergdeletionvectorscoexistenceformatversionupgrade)
* 6 [Query Semantics](#query-semantics)
    * 6.1 [RQ.Iceberg.DeletionVectors.QuerySemantics.OperatorIndependence](#rqicebergdeletionvectorsquerysemanticsoperatorindependence)
    * 6.2 [RQ.Iceberg.DeletionVectors.QuerySemantics.ProjectionIndependence](#rqicebergdeletionvectorsquerysemanticsprojectionindependence)
    * 6.3 [RQ.Iceberg.DeletionVectors.QuerySemantics.CombinedFilters](#rqicebergdeletionvectorsquerysemanticscombinedfilters)
    * 6.4 [RQ.Iceberg.DeletionVectors.QuerySemantics.SchemaEvolution](#rqicebergdeletionvectorsquerysemanticsschemaevolution)
* 7 [Snapshots and Time Travel](#snapshots-and-time-travel)
    * 7.1 [RQ.Iceberg.DeletionVectors.TimeTravel](#rqicebergdeletionvectorstimetravel)
    * 7.2 [RQ.Iceberg.DeletionVectors.TimeTravel.MultipleGenerations](#rqicebergdeletionvectorstimetravelmultiplegenerations)
    * 7.3 [RQ.Iceberg.DeletionVectors.SnapshotRefresh](#rqicebergdeletionvectorssnapshotrefresh)
    * 7.4 [RQ.Iceberg.DeletionVectors.SequenceNumbers](#rqicebergdeletionvectorssequencenumbers)
    * 7.5 [RQ.Iceberg.DeletionVectors.Compaction](#rqicebergdeletionvectorscompaction)
* 8 [Partitioning and Pruning](#partitioning-and-pruning)
    * 8.1 [RQ.Iceberg.DeletionVectors.Partitioning](#rqicebergdeletionvectorspartitioning)
    * 8.2 [RQ.Iceberg.DeletionVectors.Partitioning.PruningSkipsVectorLoad](#rqicebergdeletionvectorspartitioningpruningskipsvectorload)
* 9 [Count Paths](#count-paths)
    * 9.1 [RQ.Iceberg.DeletionVectors.Count.TrivialCountOptimization](#rqicebergdeletionvectorscounttrivialcountoptimization)
    * 9.2 [RQ.Iceberg.DeletionVectors.Count.CountOnlyFastPath](#rqicebergdeletionvectorscountcountonlyfastpath)
    * 9.3 [RQ.Iceberg.DeletionVectors.Count.CountFromFilesCache](#rqicebergdeletionvectorscountcountfromfilescache)
* 10 [Error Handling](#error-handling)
    * 10.1 [RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob](#rqicebergdeletionvectorserrorhandlingmalformedblob)
    * 10.2 [RQ.Iceberg.DeletionVectors.ErrorHandling.BlobMetadata](#rqicebergdeletionvectorserrorhandlingblobmetadata)
    * 10.3 [RQ.Iceberg.DeletionVectors.ErrorHandling.BlobBounds](#rqicebergdeletionvectorserrorhandlingblobbounds)
    * 10.4 [RQ.Iceberg.DeletionVectors.ErrorHandling.ManifestConsistency](#rqicebergdeletionvectorserrorhandlingmanifestconsistency)
    * 10.5 [RQ.Iceberg.DeletionVectors.ErrorHandling.ResourceLimits](#rqicebergdeletionvectorserrorhandlingresourcelimits)
    * 10.6 [RQ.Iceberg.DeletionVectors.ErrorHandling.NonParquetDataFiles](#rqicebergdeletionvectorserrorhandlingnonparquetdatafiles)
* 11 [Distributed Reads](#distributed-reads)
    * 11.1 [RQ.Iceberg.DeletionVectors.Distributed.ClusterFunctions](#rqicebergdeletionvectorsdistributedclusterfunctions)
    * 11.2 [RQ.Iceberg.DeletionVectors.Distributed.ProtocolFailClosed](#rqicebergdeletionvectorsdistributedprotocolfailclosed)
    * 11.3 [RQ.Iceberg.DeletionVectors.Distributed.SplitDataFile](#rqicebergdeletionvectorsdistributedsplitdatafile)
* 12 [Puffin Files Cache](#puffin-files-cache)
    * 12.1 [RQ.Iceberg.DeletionVectors.Cache.Setting](#rqicebergdeletionvectorscachesetting)
    * 12.2 [RQ.Iceberg.DeletionVectors.Cache.ServerSettings](#rqicebergdeletionvectorscacheserversettings)
    * 12.3 [RQ.Iceberg.DeletionVectors.Cache.Invalidation](#rqicebergdeletionvectorscacheinvalidation)
    * 12.4 [RQ.Iceberg.DeletionVectors.Cache.EtagBypass](#rqicebergdeletionvectorscacheetagbypass)
    * 12.5 [RQ.Iceberg.DeletionVectors.Cache.Eviction](#rqicebergdeletionvectorscacheeviction)
    * 12.6 [RQ.Iceberg.DeletionVectors.Cache.DropStatement](#rqicebergdeletionvectorscachedropstatement)
    * 12.7 [RQ.Iceberg.DeletionVectors.Cache.RBAC](#rqicebergdeletionvectorscacherbac)
    * 12.8 [RQ.Iceberg.DeletionVectors.Cache.Observability](#rqicebergdeletionvectorscacheobservability)
    * 12.9 [RQ.Iceberg.DeletionVectors.Cache.Concurrency](#rqicebergdeletionvectorscacheconcurrency)
    * 12.10 [RQ.Iceberg.DeletionVectors.Cache.EntryIsolation](#rqicebergdeletionvectorscacheentryisolation)

## Introduction

Apache Iceberg tables are built on immutable data files in object storage, so a row can never be
deleted in place. In **merge-on-read** (MoR) mode, a writer records deleted rows in small side
files instead of rewriting data files, and every reader must apply those side files to
reconstruct the logical table. **Deletion vectors** are the Iceberg v3 replacement for position
delete files: the deleted row positions of one data file are stored as a compressed roaring
bitmap blob inside a `Puffin` file, with at most one deletion vector per data file per snapshot.

This specification covers ClickHouse **read** support for Iceberg v3 deletion vectors. The
realistic setup is a lakehouse where an external engine (Spark, Trino, Flink, or a
catalog-managed service) is the writer: it commits `DELETE` / `UPDATE` / `MERGE` operations that
produce deletion vectors, and ClickHouse must return exactly the rows the writer's own engine
would return. ClickHouse never produces deletion vectors itself.

For a writer to produce deletion vectors, the table must be Iceberg format version 3 with
merge-on-read write modes:

```sql
CREATE TABLE catalog.db.table (...)
TBLPROPERTIES (
    'format-version' = '3',
    'write.delete.mode' = 'merge-on-read',
    'write.update.mode' = 'merge-on-read',
    'write.merge.mode'  = 'merge-on-read'
)
```

Without these properties the writer silently uses copy-on-write, no deletion vector is produced,
and a test exercises nothing. Tests relying on writer-produced vectors must verify that at least
one `*.puffin` file exists under the table location before asserting results.

Negative requirements in this specification name the expected error code, because several failure
paths are distinguishable only by their code:

| Code | Meaning |
|---|---|
| `ICEBERG_SPECIFICATION_VIOLATION` | The Iceberg metadata layer is internally inconsistent (manifest ↔ data file ↔ deletion vector). |
| `BAD_ARGUMENTS` | The `Puffin` file or the deletion-vector blob inside it is malformed. |
| `NOT_IMPLEMENTED` | A valid Iceberg construct that this implementation does not support. |
| `UNKNOWN_PROTOCOL` | A cluster worker is too old to receive the deletion state safely. |

Out of scope: writing deletion vectors from ClickHouse, blob types other than
`deletion-vector-v1`, and the standalone `Puffin` input format (`SELECT ... FROM file(...,
Puffin)`), which belongs to format-level requirements rather than Iceberg table reads.

[ClickHouse]: https://clickhouse.com

## Feature Scope

### RQ.Iceberg.DeletionVectors.Read
version: 1.0

[ClickHouse] SHALL support reading Iceberg format version 3 tables whose row-level deletes are
stored as deletion vectors (`deletion-vector-v1` blobs in `Puffin` files). For every data file,
[ClickHouse] SHALL exclude exactly the row positions recorded in that file's deletion vector, so
the query result matches the logical table state committed by the writer.

```sql
SELECT * FROM icebergS3('http://minio:9000/warehouse/data/', 'minio', 'minio123');
```

### RQ.Iceberg.DeletionVectors.ReadOnly
version: 1.0

Deletion vector support SHALL be read-only. [ClickHouse] SHALL NOT produce, modify, or delete
deletion vectors or `Puffin` files under any operation.

### RQ.Iceberg.DeletionVectors.AccessForms
version: 1.0

[ClickHouse] SHALL apply deletion vectors identically across all Iceberg access forms:

* Table functions: `icebergS3`, `icebergAzure`, `icebergLocal`
* The `Iceberg` table engine
* Tables from an Iceberg REST-catalog database (`DataLakeCatalog` engine)

The same table read through any form SHALL return the same logical row set.

### RQ.Iceberg.DeletionVectors.StorageBackends
version: 1.0

[ClickHouse] SHALL support deletion vectors on tables stored in S3, Azure, and local filesystem
storage. Correctness SHALL NOT depend on the storage backend. Cache-related requirements
(section 12) apply only to S3 and Azure, because the `Puffin` cache is keyed partly on the object
etag and local filesystem objects have none.

## Producing Operations

### RQ.Iceberg.DeletionVectors.WriterOperations
version: 1.0

[ClickHouse] SHALL correctly read deletion vectors regardless of which external SQL operation
produced them: `DELETE`, `UPDATE`, or `MERGE` (including `MERGE` statements combining
`WHEN MATCHED THEN UPDATE`, `WHEN MATCHED THEN DELETE`, and `WHEN NOT MATCHED THEN INSERT`).
Once a snapshot with valid metadata is committed, the producing operation is irrelevant to the
read path: row counts, exact surviving rows, updated values, and inserted rows SHALL match the
writer engine's own result.

## Vector Content Shapes

### RQ.Iceberg.DeletionVectors.EmptyVector
version: 1.0

[ClickHouse] SHALL accept a deletion vector with `cardinality = 0` and no positions as valid.
The referenced data file SHALL contribute all of its rows; the empty vector SHALL NOT hide the
file and SHALL NOT fail the query. Repeated reads SHALL neither fail nor re-fetch the `Puffin`
file when the cache is enabled.

### RQ.Iceberg.DeletionVectors.AllRowsDeleted
version: 1.0

[ClickHouse] SHALL support a deletion vector that deletes every row of its data file. The file
SHALL contribute zero rows without being physically removed, and the query SHALL remain valid:

```text
file A → 100 rows, deletion vector deletes positions 0..99 → contributes 0 rows
file B → 50 rows,  no deletion vector                      → contributes 50 rows
table  → 50 rows visible
```

`SELECT *`, `SELECT count()`, aggregates, and filtered reads SHALL all reflect the empty
contribution.

### RQ.Iceberg.DeletionVectors.BoundaryPositions
version: 1.0

Deletion-vector positions are zero-based within the referenced data file. For a data file with
`record_count = N`, [ClickHouse] SHALL:

* apply position `0` (first row) and position `N - 1` (last row) correctly;
* reject a position `>= N` with `ICEBERG_SPECIFICATION_VIOLATION`;
* reject a declared cardinality `> N` with `ICEBERG_SPECIFICATION_VIOLATION`, before any
  `Puffin` I/O is performed.

### RQ.Iceberg.DeletionVectors.RowGroupBoundaries
version: 1.0

[ClickHouse] SHALL interpret deletion-vector positions as absolute row numbers within the
referenced Parquet file, never relative to a row group. For a file with row groups of 100 rows
each and a vector deleting `{99, 100, 199, 200}`, exactly those four rows SHALL disappear —
when all row groups are read, when some are pruned by a predicate, and when row groups are
processed by parallel readers.

### RQ.Iceberg.DeletionVectors.SharedPuffinFile
version: 1.0

One `Puffin` file may hold several `deletion-vector-v1` blobs, each bound by its own
`content_offset` / `content_size_in_bytes` from the manifest and carrying its own
`referenced-data-file` property. [ClickHouse] SHALL apply to each data file only its own blob —
no union and no cross-file contamination — both when all referenced files are read together and
when a filter causes only one of them to be read.

## Coexistence With Other Delete Formats

Iceberg v3 tables may simultaneously carry deletion vectors, Parquet position-delete files
(inherited from v2), and equality-delete files. ClickHouse already reads the two older formats;
this section defines how the three interact.

### RQ.Iceberg.DeletionVectors.Coexistence.AcrossDataFiles
version: 1.0

Within one snapshot, different data files may independently use a deletion vector, a Parquet
position delete, an equality delete, or no delete at all. [ClickHouse] SHALL compute each data
file's result from its own delete metadata only.

### RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes
version: 1.0

When a deletion vector matches a data file, [ClickHouse] SHALL NOT apply Parquet position-delete
files for that same data file (the Iceberg v3 supersession rule). Consequently:

* a row present both in an old position-delete file and in a newer deletion vector SHALL be
  removed exactly once;
* a row present only in a superseded position-delete file SHALL remain visible unless the
  deletion vector also covers it.

### RQ.Iceberg.DeletionVectors.Coexistence.EqualityDeletes
version: 1.0

Equality deletes SHALL apply independently of, and in addition to, a deletion vector on the same
data file. The final result SHALL be as if the deletion-vector filter ran first (on absolute row
positions) and the equality-delete predicate ran on the surviving rows.

### RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError
version: 1.0

If more than one live deletion-vector manifest entry references the same data file in one
snapshot, [ClickHouse] SHALL fail the query with `ICEBERG_SPECIFICATION_VIOLATION`
("Multiple deletion vectors match data file ..."). It SHALL NOT pick one of them and SHALL NOT
union them.

### RQ.Iceberg.DeletionVectors.Coexistence.FormatVersionUpgrade
version: 1.0

For an Iceberg v2 table with Parquet position deletes that is upgraded to format version 3:

* the query result SHALL be identical immediately before and after the upgrade — previously
  deleted rows SHALL NOT resurface;
* after the first v3 delete produces a deletion vector, rows deleted before the upgrade SHALL
  remain absent and newly deleted rows SHALL become absent, regardless of whether the writer
  folded the old position deletes into the vector or kept both (the supersession rule of
  RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes guarantees no double
  application either way).

## Query Semantics

### RQ.Iceberg.DeletionVectors.QuerySemantics.OperatorIndependence
version: 1.0

Deletion vectors SHALL be applied at the source, before any SQL operator runs, so the visible row
set is fixed for the whole query. Every relational operator SHALL observe exactly that set,
including:

* `ORDER BY ... LIMIT n` (deleted rows straddling the limit boundary must not shrink the result)
* `DISTINCT` (a value whose only occurrence is deleted disappears; a value with a deleted
  duplicate remains)
* `JOIN` against non-Iceberg tables (a deleted row must not join or affect join cardinality)
* subqueries, CTEs, and derived tables (identical to a direct read)
* `PREWHERE` (rows filtered before the deletion-vector transform must still map back to correct
  absolute file row positions)

### RQ.Iceberg.DeletionVectors.QuerySemantics.ProjectionIndependence
version: 1.0

Row visibility SHALL be independent of the projected column list, because a deletion vector
addresses physical row positions, not predicate values. When the writer executed
`DELETE FROM t WHERE customer_id = 100`, a ClickHouse query selecting only other columns
(`SELECT amount FROM ...`) SHALL still exclude the deleted rows without re-evaluating the
original predicate.

### RQ.Iceberg.DeletionVectors.QuerySemantics.CombinedFilters
version: 1.0

When a user predicate is combined with a deletion vector and an equality delete, the result SHALL
be equivalent to applying, in order:

```text
physical data → deletion-vector visibility → other Iceberg delete semantics → user predicate
```

A row removed by any one of the three SHALL be absent; a row matched by several SHALL be absent
exactly once; a row matched by none SHALL survive. The same result SHALL hold when the user
predicate is expressed as `WHERE` and as `PREWHERE`.

### RQ.Iceberg.DeletionVectors.QuerySemantics.SchemaEvolution
version: 1.0

A deletion vector attached to a data file SHALL remain valid after schema evolution of the table,
including `ADD COLUMN`, column rename, and column drop (both resolved by field id in Iceberg).
Row visibility SHALL be identical for any projection over old or new columns, and values of a
column added after the data file was written SHALL follow normal Iceberg schema-evolution
semantics (`NULL` unless a default is defined) for the surviving rows.

## Snapshots and Time Travel

### RQ.Iceberg.DeletionVectors.TimeTravel
version: 1.0

Deletion vectors SHALL be discovered from the manifests of the selected snapshot only. A vector
introduced in snapshot B SHALL be invisible when reading an earlier snapshot A, for both
time-travel forms:

```sql
SELECT count() FROM iceberg_table SETTINGS iceberg_snapshot_id = <snapshot_a_id>;
SELECT count() FROM iceberg_table SETTINGS iceberg_timestamp_ms = <before_delete_ms>;
```

With 100 rows inserted in snapshot A and 5 rows deleted via a deletion vector in snapshot B: the
current read SHALL return 95 rows, snapshot A SHALL return the original 100 rows, and snapshot B
read explicitly SHALL return 95 — as exact row sets, not merely counts.

### RQ.Iceberg.DeletionVectors.TimeTravel.MultipleGenerations
version: 1.0

Across several snapshots whose deletion-vector state differs (for example A: no vector,
B: deletes `{1, 5}`, C: deletes `{1, 5, 9}`), each snapshot SHALL expose its own logical state
regardless of the order in which snapshots are queried and regardless of caching: a vector
cached while reading one snapshot SHALL never affect the result of another.

### RQ.Iceberg.DeletionVectors.SnapshotRefresh
version: 1.0

After an external engine commits a `DELETE` producing a deletion vector, the next ClickHouse
query SHALL observe the new snapshot without a server restart, without
`SYSTEM DROP PUFFIN FILES CACHE`, and without dropping any other cache — with all caches at
their default settings. This SHALL hold for both the table function and the `Iceberg` table
engine.

### RQ.Iceberg.DeletionVectors.SequenceNumbers
version: 1.0

[ClickHouse] SHALL honor Iceberg sequence-number rules when matching deletion vectors to data
files:

* a deletion vector committed at sequence number `N` SHALL NOT affect data files added after `N`,
  even when the newer files contain rows with the same values;
* a deletion vector referencing a data file no longer present in the snapshot SHALL be ignored,
  not treated as an error.

### RQ.Iceberg.DeletionVectors.Compaction
version: 1.0

After external data-file compaction (for example Spark's `rewrite_data_files`), deletion vectors
that referenced the pre-compaction files SHALL NOT be applied to the rewritten files, and the
logical query result SHALL be identical before and after the compaction.

## Partitioning and Pruning

### RQ.Iceberg.DeletionVectors.Partitioning
version: 1.0

[ClickHouse] SHALL apply deletion vectors correctly on partitioned tables, including identity,
bucket, and other transform partitioning. A query touching only a deletion-vector-bearing
partition SHALL have the vector applied to it.

### RQ.Iceberg.DeletionVectors.Partitioning.PruningSkipsVectorLoad
version: 1.0

When partition pruning eliminates a data file from a query, [ClickHouse] SHALL also skip loading
that file's deletion vector — no `Puffin` read SHALL occur for a pruned file (observable via the
`PuffinFilesRead` profile event). Min/max pruning of delete files SHALL never prune a delete file
that is actually needed for a data file being read.

## Count Paths

`SELECT count()` on an Iceberg table can be answered three ways: a metadata shortcut that sums
manifest row counts, a count-only fast path that skips column decoding, and a full scan. All
three must agree in the presence of deletion vectors.

### RQ.Iceberg.DeletionVectors.Count.TrivialCountOptimization
version: 1.0

The metadata count shortcut SHALL fail closed in the presence of any live delete entries
(a `Puffin` deletion vector is a position-delete entry): [ClickHouse] SHALL fall back to a real
scan rather than answering from manifest sums. `SELECT count()` SHALL return the same value with
`optimize_trivial_count_query = 1` and `= 0`, and both SHALL equal
`SELECT count() FROM (SELECT * FROM table)`.

When the snapshot summary's `total-records` disagrees with the manifest sum on a table without
deletes, the manifest sum SHALL win and a warning SHALL be logged.

### RQ.Iceberg.DeletionVectors.Count.CountOnlyFastPath
version: 1.0

The count-only fast path (`need_only_count`) SHALL be disabled for any data file with an attached
deletion vector, position delete, or equality delete. Counts SHALL be identical with and without
`PREWHERE`, with and without a filter, and for data files split across multiple row groups.

### RQ.Iceberg.DeletionVectors.Count.CountFromFilesCache
version: 1.0

The count-from-files cache (`use_cache_for_count_from_files`) SHALL NOT be used or populated for
data files that have delete entries attached, because its key (file path + modification time)
does not change when a delete file is added or compacted away. In particular:

```text
1. SET use_cache_for_count_from_files = 1
2. SELECT count() → N
3. external DELETE producing a deletion vector
4. SELECT count() → must be N - deleted, not the cached N
```

The reverse direction SHALL also hold: a count taken while deletes exist SHALL NOT be served
stale after the deletes are compacted away.

## Error Handling

Any structural defect in a `Puffin` file or deletion-vector blob must fail the query with an
explicit error. It must never be silently ignored or partially applied — a silently dropped
vector would make deleted rows reappear. Tests SHALL assert both the error code and a
distinguishing fragment of the message, since a bare "query failed" can pass for the wrong
reason.

### RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob
version: 1.0

[ClickHouse] SHALL reject a structurally invalid deletion-vector blob payload with
`BAD_ARGUMENTS` and a specific message, including at least:

| Defect | Expected message fragment |
|---|---|
| CRC32 does not match the payload | `Deletion vector CRC mismatch` |
| wrong 4-byte magic | `Invalid deletion vector magic` |
| declared combined length inconsistent with the blob length | `does not match combined length` |
| blob shorter than 12 bytes | `Deletion vector blob is too small` |
| bitmap header shorter than 8 bytes | `Deletion vector bitmap is too small` |
| bitmap truncated mid-key | `truncated while reading key` |
| roaring container extends past the blob | `exceeds blob size` |
| roaring bitmap fails internal validation | `failed internal validation` |
| bitmap keys not strictly ascending | `must be sorted in ascending order` |
| bitmap key negative or `> INT32_MAX - 1` | `Invalid deletion vector bitmap key` |
| bitmap count negative or `> INT32_MAX` | `Invalid deletion vector bitmap count` |
| trailing bytes after the last container | `trailing bytes` |
| deserialized cardinality ≠ declared cardinality | `does not match deserialized row count` |
| running cardinality exceeds the declared one mid-parse | `exceeds declared cardinality` |
| a position exceeds the maximum representable position | `is out of supported range` |

### RQ.Iceberg.DeletionVectors.ErrorHandling.BlobMetadata
version: 1.0

[ClickHouse] SHALL validate the `Puffin` footer metadata of a deletion-vector blob and reject
invalid metadata with `BAD_ARGUMENTS`, including at least:

| Defect | Expected message fragment |
|---|---|
| blob `type` is not `deletion-vector-v1` | `expected deletion-vector-v1` |
| `compression-codec` present and non-empty | `must omit compression-codec` |
| `referenced-data-file` missing or empty | `missing required property 'referenced-data-file'` |
| `referenced-data-file` ≠ the data file being read | `does not match expected data file` |
| `cardinality` missing or empty | `missing required property 'cardinality'` |
| `cardinality` not an unsigned integer | `must be an unsigned integer` |
| `cardinality` ≠ the manifest `record_count` | `does not match expected cardinality` |
| no blob at the manifest's `(offset, length)` | `No Puffin footer blob at offset` |
| two blobs at the same `(offset, length)` | `Multiple Puffin blobs claim offset` |

### RQ.Iceberg.DeletionVectors.ErrorHandling.BlobBounds
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a manifest-declared blob location that does not
fit inside the `Puffin` file: negative offset or length, offset or length beyond the file size,
and `offset + length` overflowing or exceeding the file size.

### RQ.Iceberg.DeletionVectors.ErrorHandling.ManifestConsistency
version: 1.0

[ClickHouse] SHALL reject internally inconsistent Iceberg metadata with
`ICEBERG_SPECIFICATION_VIOLATION`, including at least:

* a deletion-vector manifest entry without `referenced_data_file` (position-delete lower/upper
  bounds SHALL NOT be used as a fallback for deletion vectors);
* a deletion-vector manifest entry with a negative `record_count`;
* a data-file manifest entry missing `record_count` (required to bound vector positions) or with
  a negative `record_count`;
* a deletion-vector `record_count` greater than the data file's `record_count` (rejected before
  any I/O);
* two deletion vectors referencing the same data file (see
  RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError).

### RQ.Iceberg.DeletionVectors.ErrorHandling.ResourceLimits
version: 1.0

[ClickHouse] SHALL enforce hard resource limits on deletion vectors, failing with
`BAD_ARGUMENTS`:

```text
blob length > 2 GiB                → "exceeds absolute limit"
declared cardinality > 100,000,000 → "exceeds materialization limit"
```

The cardinality limit SHALL be checked before the `Puffin` file is opened, so a hostile or
corrupt manifest cannot force a large allocation — `PuffinFilesRead` SHALL NOT increase for such
a query.

### RQ.Iceberg.DeletionVectors.ErrorHandling.NonParquetDataFiles
version: 1.0

Deletion vectors require file-relative row numbers, which only the Parquet readers provide. A
deletion vector attached to a data file in any other format (ORC, Avro) SHALL fail with
`NOT_IMPLEMENTED` and a message naming both the feature and the actual format: "Deletion vectors
are only supported for data files of Parquet format in Iceberg, but got <format>".

## Distributed Reads

### RQ.Iceberg.DeletionVectors.Distributed.ClusterFunctions
version: 1.0

For every single-node requirement in this specification, the corresponding `*Cluster` table
function read (for example `icebergS3Cluster`) SHALL return an identical result. Deletion-vector
positions are resolved on the initiator and shipped to workers as part of the cluster read task.

### RQ.Iceberg.DeletionVectors.Distributed.ProtocolFailClosed
version: 1.0

A cluster worker whose protocol version is too old to carry the deletion state SHALL cause an
explicit `UNKNOWN_PROTOCOL` failure with no rows returned — never a silent read without deletes:

* a worker without `excluded_rows` support (protocol < 5) would otherwise drop deletion vectors
  and return deleted rows;
* a worker without `iceberg_info` support (protocol < 3) would otherwise skip position/equality
  delete transforms;
* a worker without `file_bucket_info` support (protocol < 4) would otherwise read whole files
  per bucket task and duplicate rows.

### RQ.Iceberg.DeletionVectors.Distributed.SplitDataFile
version: 1.0

When a single Parquet data file is split by row group across parallel threads or cluster nodes,
each read task SHALL apply the deletion vector to the correct absolute positions in its range.
For a file with deletions in every row group:

```text
single-threaded read == multi-threaded read == cluster read == count()
```

and all of them SHALL equal the writer-engine result, for any `max_threads` value and cluster
size.

## Puffin Files Cache

Parsed deletion vectors are cached in memory so repeated queries do not re-fetch and re-decode
`Puffin` blobs. The cache entry key includes the `Puffin` object path and etag, the blob offset
and length, the referenced data file, and the expected cardinalities — so a new Iceberg commit
(new `Puffin` path) or replaced object content (new etag) can never be served a stale vector.

Cache requirements SHALL be verified on S3 or Azure storage (local files have no etag and bypass
the cache), and profile events SHALL be read from `system.query_log` per `query_id` so
concurrent tests cannot perturb the counts.

### RQ.Iceberg.DeletionVectors.Cache.Setting
version: 1.0

[ClickHouse] SHALL provide the session setting `use_puffin_files_cache`, default `1`. With the
cache enabled, a repeated query SHALL be served from cache (`PuffinFilesCacheHits` increases,
`PuffinFilesRead` stays at 0). With `use_puffin_files_cache = 0`, every read SHALL re-fetch and
re-parse the vector (`PuffinFilesRead` increases on every query) and results SHALL remain
correct.

### RQ.Iceberg.DeletionVectors.Cache.ServerSettings
version: 1.0

[ClickHouse] SHALL provide the server settings `puffin_files_cache_policy` (default `SLRU`),
`puffin_files_cache_size` (default 512 MiB, `0` disables), `puffin_files_cache_max_entries`
(default 5000, `0` disables), and `puffin_files_cache_size_ratio` (default 0.5). Results SHALL
remain correct with the cache disabled by server setting even when `use_puffin_files_cache = 1`,
and `puffin_files_cache_size` SHALL be changeable without a restart with the live value
reported.

### RQ.Iceberg.DeletionVectors.Cache.Invalidation
version: 1.0

The cache SHALL never serve a stale deletion vector across Iceberg commits:

* a new commit produces a new `Puffin` path → new cache key → new load; a previously cached
  vector for the old path SHALL NOT be consulted;
* if a `Puffin` object at the same path is replaced with different content, the changed etag
  SHALL produce a different cache key;
* `SYSTEM DROP PUFFIN FILES CACHE` SHALL never be required for correctness after a normal
  Iceberg commit.

### RQ.Iceberg.DeletionVectors.Cache.EtagBypass
version: 1.0

When the storage object has no etag (for example local filesystem), [ClickHouse] SHALL bypass the
cache and read the vector fresh on every query. Results SHALL remain correct and
`PuffinFilesCacheHits` SHALL stay at 0.

### RQ.Iceberg.DeletionVectors.Cache.Eviction
version: 1.0

With a cache deliberately smaller than the working set, [ClickHouse] SHALL evict entries
(`PuffinFilesCacheWeightLost` increases) while query results remain correct. Empty deletion
vectors SHALL be cached as explicit entries with minimal weight.

### RQ.Iceberg.DeletionVectors.Cache.DropStatement
version: 1.0

[ClickHouse] SHALL support the statement:

```sql
SYSTEM DROP PUFFIN FILES CACHE;
```

It SHALL clear the cache so the next query records misses and re-reads the `Puffin` files, with
an unchanged logical result.

### RQ.Iceberg.DeletionVectors.Cache.RBAC
version: 1.0

`SYSTEM DROP PUFFIN FILES CACHE` SHALL require the `SYSTEM DROP PUFFIN FILES CACHE` privilege
(`GLOBAL` level, child of `SYSTEM DROP CACHE`). A user without it SHALL be denied; a user with
the parent `SYSTEM DROP CACHE` privilege SHALL be allowed; `SHOW PRIVILEGES` SHALL list the
privilege.

### RQ.Iceberg.DeletionVectors.Cache.Observability
version: 1.0

[ClickHouse] SHALL expose cache state via the asynchronous metrics `PuffinFilesCacheBytes` and
`PuffinFilesCacheFiles`, and per-query activity via the profile events `PuffinFilesRead`,
`PuffinFileReadMicroseconds`, `PuffinFilesCacheHits`, `PuffinFilesCacheMisses`, and
`PuffinFilesCacheWeightLost`. After a cold read of a table with deletion vectors: misses and
reads increase, read time is non-zero, and the metrics reflect the resident entries. On a warm
read: hits increase and `PuffinFilesRead` stays at 0.

```sql
SELECT ProfileEvents['PuffinFilesCacheHits'], ProfileEvents['PuffinFilesRead']
FROM system.query_log
WHERE type = 'QueryFinish' AND query_id = '...';
```

### RQ.Iceberg.DeletionVectors.Cache.Concurrency
version: 1.0

Two concurrent queries over the same cold deletion vector SHALL both return correct results, and
the vector SHALL be loaded once (`PuffinFilesRead` totals 1 for that blob across both queries).
A `SYSTEM DROP PUFFIN FILES CACHE` racing with an in-flight load SHALL NOT produce a wrong
result — the load is discarded and recorded as a miss rather than being served stale.

### RQ.Iceberg.DeletionVectors.Cache.EntryIsolation
version: 1.0

A cache hit SHALL return a copy of the stored bitmap so that no query can mutate another query's
cached state. Many concurrent queries with different filters over the same deletion vector SHALL
each return the same result as the equivalent single query.

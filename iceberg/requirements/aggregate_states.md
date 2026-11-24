# SRS-051 ClickHouse Aggregate Function States in Parquet and Iceberg
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
    * 1.1 [Terminology](#terminology)
* 2 [Setting](#setting)
    * 2.1 [RQ.Iceberg.AggregateStates.Setting](#rqicebergaggregatestatessetting)
* 3 [Parquet](#parquet)
    * 3.1 [RQ.Iceberg.AggregateStates.Parquet.Write](#rqicebergaggregatestatesparquetwrite)
    * 3.2 [RQ.Iceberg.AggregateStates.Parquet.Write.Disabled](#rqicebergaggregatestatesparquetwritedisabled)
    * 3.3 [RQ.Iceberg.AggregateStates.Parquet.ColumnTypesMetadata](#rqicebergaggregatestatesparquetcolumntypesmetadata)
    * 3.4 [RQ.Iceberg.AggregateStates.Parquet.SchemaInference](#rqicebergaggregatestatesparquetschemainference)
    * 3.5 [RQ.Iceberg.AggregateStates.Parquet.SchemaInference.Disabled](#rqicebergaggregatestatesparquetschemainferencedisabled)
    * 3.6 [RQ.Iceberg.AggregateStates.Parquet.ExplicitStructure](#rqicebergaggregatestatesparquetexplicitstructure)
    * 3.7 [RQ.Iceberg.AggregateStates.Parquet.SimpleAggregateFunction](#rqicebergaggregatestatesparquetsimpleaggregatefunction)
* 4 [Iceberg Schema](#iceberg-schema)
    * 4.1 [RQ.Iceberg.AggregateStates.Iceberg.TypeMapping](#rqicebergaggregatestatesicebergtypemapping)
    * 4.2 [RQ.Iceberg.AggregateStates.Iceberg.Annotation](#rqicebergaggregatestatesicebergannotation)
    * 4.3 [RQ.Iceberg.AggregateStates.Iceberg.Annotation.Mismatch](#rqicebergaggregatestatesicebergannotationmismatch)
    * 4.4 [RQ.Iceberg.AggregateStates.Iceberg.Annotation.Missing](#rqicebergaggregatestatesicebergannotationmissing)
* 5 [Iceberg Setting Gate](#iceberg-setting-gate)
    * 5.1 [RQ.Iceberg.AggregateStates.Iceberg.Gate.Create](#rqicebergaggregatestatesiceberggatecreate)
    * 5.2 [RQ.Iceberg.AggregateStates.Iceberg.Gate.AlterAddColumn](#rqicebergaggregatestatesiceberggatealteraddcolumn)
    * 5.3 [RQ.Iceberg.AggregateStates.Iceberg.Gate.Read](#rqicebergaggregatestatesiceberggateread)
    * 5.4 [RQ.Iceberg.AggregateStates.Iceberg.Gate.TableFunctionScope](#rqicebergaggregatestatesiceberggatetablefunctionscope)
    * 5.5 [RQ.Iceberg.AggregateStates.Iceberg.Gate.TableEngineScope](#rqicebergaggregatestatesiceberggatetableenginescope)
    * 5.6 [RQ.Iceberg.AggregateStates.Iceberg.Gate.InsertWriter](#rqicebergaggregatestatesiceberggateinsertwriter)
* 6 [Iceberg Round Trip](#iceberg-round-trip)
    * 6.1 [RQ.Iceberg.AggregateStates.Iceberg.MergeEquivalence](#rqicebergaggregatestatesicebergmergeequivalence)
    * 6.2 [RQ.Iceberg.AggregateStates.Iceberg.InsertSelectFromAggregatingMergeTree](#rqicebergaggregatestatesiceberginsertselectfromaggregatingmergetree)
* 7 [Interoperability](#interoperability)
    * 7.1 [RQ.Iceberg.AggregateStates.Interop.ExternalReaders](#rqicebergaggregatestatesinteropexternalreaders)
    * 7.2 [RQ.Iceberg.AggregateStates.Interop.CreateThroughCatalog](#rqicebergaggregatestatesinteropcreatethroughcatalog)
    * 7.3 [RQ.Iceberg.AggregateStates.Interop.ExternalCommit](#rqicebergaggregatestatesinteropexternalcommit)
    * 7.4 [RQ.Iceberg.AggregateStates.Interop.ExternalSchemaEvolution](#rqicebergaggregatestatesinteropexternalschemaevolution)
* 8 [Export](#export)
    * 8.1 [RQ.Iceberg.AggregateStates.Export.Part](#rqicebergaggregatestatesexportpart)
    * 8.2 [RQ.Iceberg.AggregateStates.Export.Partition](#rqicebergaggregatestatesexportpartition)
    * 8.3 [RQ.Iceberg.AggregateStates.Export.Partition.Manifest](#rqicebergaggregatestatesexportpartitionmanifest)
    * 8.4 [RQ.Iceberg.AggregateStates.Export.Gate](#rqicebergaggregatestatesexportgate)

## Introduction

Neither Parquet nor Apache Iceberg has a type for a [ClickHouse] aggregate function state. This
specification covers storing `AggregateFunction(f, T...)` and `SimpleAggregateFunction(f, T)`
columns in Parquet files and Iceberg tables so that a partition of pre-aggregated states, for
example from an `AggregatingMergeTree` table, can be moved into a data lake without finalizing it
and merged later with the same result as in [ClickHouse].

A state is stored as opaque binary, the same bytes the `-State` combinator produces, and the
[ClickHouse] type name is recorded next to the data:

* in Parquet, in the file-level key-value metadata key `clickhouse.column_types`, a versioned JSON
  object whose `columns` member maps column name to [ClickHouse] type name;
* in Iceberg, in the table property `clickhouse.type.<field-id>.<schema-id>`.

Other engines ignore both keys and see a plain binary column, or a column of the storage type `T`
for `SimpleAggregateFunction`.

The behaviour is gated by the setting `allow_experimental_aggregate_function_states_in_open_formats`
(default `0`). With the setting enabled, the stored type name, not the query, chooses which
deserializer reads the stored bytes.

The realistic setup is a shared lakehouse: [ClickHouse] writes the states, other engines read the
table and commit to it through a catalog, and [ClickHouse] merges the states later. Several
requirements below are therefore judged by what an external Iceberg client and the catalog leave
in the metadata, not only by what [ClickHouse] reports.

Regression tests live under the TestFlows package `iceberg.tests.iceberg_engine.aggregate_states`
and run as `/iceberg/aggregate states`. The export requirements are covered by the module
`iceberg.tests.export_partition.aggregate_states` of the `/iceberg/export partition` suite.

Implemented in [Altinity/ClickHouse#2680](https://github.com/Altinity/ClickHouse/pull/2680), requested
in [Altinity/ClickHouse#2206](https://github.com/Altinity/ClickHouse/issues/2206).

### Terminology

* **State column** - a column of type `AggregateFunction(f, T...)`.
* **Simple column** - a column of type `SimpleAggregateFunction(f, T)`.
* **Annotation** - the Iceberg table property `clickhouse.type.<field-id>.<schema-id>` that records
  the [ClickHouse] type of a field. It holds from that schema id until the next such property of the
  same field, and an empty value records no type.
* **External engine** - any Iceberg client that is not [ClickHouse] (PyIceberg, Spark, a REST
  catalog server).

## Setting

### RQ.Iceberg.AggregateStates.Setting
version: 1.0

[ClickHouse] SHALL provide the query setting
`allow_experimental_aggregate_function_states_in_open_formats` (`Bool`, default `0`) and SHALL list
it in `system.settings`.

## Parquet

### RQ.Iceberg.AggregateStates.Parquet.Write
version: 1.0

With the setting enabled, [ClickHouse] SHALL write a state column to Parquet as a `BYTE_ARRAY`
column without a `STRING`/`UTF8` logical or converted type, holding for each row the bytes the
`-State` combinator produces. A Parquet reader that is not [ClickHouse] SHALL read the column as
binary.

### RQ.Iceberg.AggregateStates.Parquet.Write.Disabled
version: 1.0

With the setting disabled, writing a state column to Parquet SHALL fail with `UNKNOWN_TYPE` and no
file SHALL be written.

### RQ.Iceberg.AggregateStates.Parquet.ColumnTypesMetadata
version: 1.0

A Parquet file [ClickHouse] writes with a state or simple column SHALL carry the key
`clickhouse.column_types` in its file-level key-value metadata: a JSON object with the member
`version` set to `1` and the member `columns`, an object that maps the name of every such column to
its [ClickHouse] type name. Columns of other types MAY be absent from `columns`.

For example:

```json
{"version": 1, "columns": {"u": "AggregateFunction(uniq, UInt64)", "s": "SimpleAggregateFunction(sum, Int64)"}}
```

### RQ.Iceberg.AggregateStates.Parquet.SchemaInference
version: 1.0

With the setting enabled, schema inference of a Parquet file with `clickhouse.column_types` SHALL
report the recorded types, so `DESCRIBE` shows `AggregateFunction(...)` and
`SimpleAggregateFunction(...)`, and the `-Merge` combinator over a state column SHALL return the
same result as the aggregate function over the original rows.

### RQ.Iceberg.AggregateStates.Parquet.SchemaInference.Disabled
version: 1.0

With the setting disabled, schema inference of a Parquet file whose `clickhouse.column_types`
names an `AggregateFunction` SHALL fail, and SHALL NOT silently report the column as `String`.

### RQ.Iceberg.AggregateStates.Parquet.ExplicitStructure
version: 1.0

An explicit structure given to the `file`, `s3` or `url` table function SHALL override
`clickhouse.column_types` regardless of the setting, so a state column can be read as `String` and
cast back with `CAST(column AS AggregateFunction(...))`.

### RQ.Iceberg.AggregateStates.Parquet.SimpleAggregateFunction
version: 1.0

A simple column SHALL be written as an ordinary value of its storage type `T` whether or not the
setting is enabled, and reading it back SHALL NOT require the setting.

## Iceberg Schema

### RQ.Iceberg.AggregateStates.Iceberg.TypeMapping
version: 1.0

[ClickHouse] SHALL map a state column to the Iceberg type `binary` and a simple column
`SimpleAggregateFunction(f, T)` to the Iceberg type `T` maps to.

### RQ.Iceberg.AggregateStates.Iceberg.Annotation
version: 1.0

For every Iceberg schema field [ClickHouse] writes for a state or simple column, the table metadata
SHALL carry an annotation in effect for that schema with the [ClickHouse] type name, as the table
property `clickhouse.type.<field-id>.<schema-id>`. Fields of other types SHALL NOT be annotated. The
schema fields themselves SHALL NOT carry a `clickhouse.type` key. With the setting enabled,
[ClickHouse] SHALL report an annotated field with the annotated type.

### RQ.Iceberg.AggregateStates.Iceberg.Annotation.Mismatch
version: 1.0

Reading an Iceberg table whose annotation does not describe the field's Iceberg type, for example
`AggregateFunction(...)` on a `long` field, SHALL fail with `ICEBERG_SPECIFICATION_VIOLATION`. An
annotation that is not a valid [ClickHouse] type name SHALL fail the read.

### RQ.Iceberg.AggregateStates.Iceberg.Annotation.Missing
version: 1.0

A field without an annotation SHALL be read with the type derived from its Iceberg type, so a
state column whose annotation was removed reads as `String` without the setting, and casting it to
the original `AggregateFunction` type SHALL return the original states.

## Iceberg Setting Gate

### RQ.Iceberg.AggregateStates.Iceberg.Gate.Create
version: 1.0

With the setting disabled, `CREATE TABLE` of an Iceberg table with a state or simple column SHALL
fail with a message naming the setting, and SHALL NOT write any object to the table location.

### RQ.Iceberg.AggregateStates.Iceberg.Gate.AlterAddColumn
version: 1.0

With the setting disabled, `ALTER TABLE ... ADD COLUMN` of a state or simple column to an Iceberg
table SHALL fail with a message naming the setting, and the table schema SHALL stay unchanged.

### RQ.Iceberg.AggregateStates.Iceberg.Gate.Read
version: 1.0

With the setting disabled, every query that reads an Iceberg schema with a field annotated as
`AggregateFunction`, including `SELECT`, `DESCRIBE`, `INSERT` and `ALTER TABLE ... EXPORT PART`,
SHALL fail with `SUPPORT_IS_DISABLED` and a message naming the setting. A table whose only
annotated fields are simple columns SHALL be readable without the setting.

### RQ.Iceberg.AggregateStates.Iceberg.Gate.TableFunctionScope
version: 1.0

The `iceberg*` table functions SHALL apply the setting of the query that uses them, so on the same
table one query with the setting succeeds and the next query without it fails.

### RQ.Iceberg.AggregateStates.Iceberg.Gate.TableEngineScope
version: 1.0

An Iceberg table engine SHALL apply the setting of each query that reads the schema, including
when an earlier query has already parsed and cached that schema. A query with the setting SHALL
NOT let a later query without it read states, and a refused query SHALL NOT stop a later query
with the setting from reading them. `DETACH TABLE` and `ATTACH TABLE` SHALL NOT change this.

### RQ.Iceberg.AggregateStates.Iceberg.Gate.InsertWriter
version: 1.0

For `INSERT` into an Iceberg table engine, the Parquet writer SHALL take the setting from the
format settings frozen at `CREATE TABLE`, that is the server settings and the `SETTINGS` clause of
the `CREATE TABLE` query. The setting given only on the `INSERT` or as a query setting of the
`CREATE TABLE` SHALL NOT enable writing state columns.

## Iceberg Round Trip

### RQ.Iceberg.AggregateStates.Iceberg.MergeEquivalence
version: 1.0

States written to an Iceberg table SHALL merge exactly as in an `AggregatingMergeTree` table: for
every aggregate function, the `-Merge` combinator over the stored states, across any number of
inserts and data files, SHALL return the same result as the aggregate function over the original
rows, and a simple column SHALL aggregate with its function to the same result.

### RQ.Iceberg.AggregateStates.Iceberg.InsertSelectFromAggregatingMergeTree
version: 1.0

`INSERT INTO <iceberg table> SELECT * FROM <AggregatingMergeTree table>` SHALL copy the states
unchanged, so merging them on both sides returns the same result.

## Interoperability

### RQ.Iceberg.AggregateStates.Interop.ExternalReaders
version: 1.0

An external engine reading a [ClickHouse]-written Iceberg table SHALL see a state column as
`binary` holding the same bytes [ClickHouse] reports with `hex()`, and a simple column as its
storage type with the same values.

### RQ.Iceberg.AggregateStates.Interop.CreateThroughCatalog
version: 1.0

When an Iceberg table with state or simple columns is created through a `DataLakeCatalog`
database, the metadata file the catalog registers SHALL carry the annotations, and [ClickHouse]
SHALL report the annotated types when it reads the table through the catalog.

### RQ.Iceberg.AggregateStates.Interop.ExternalCommit
version: 1.0

After an external engine commits to a table with annotated fields (an append, a compaction, a
snapshot expiry), the current schema of the metadata file the catalog registers SHALL still carry
the annotations, and [ClickHouse] SHALL merge the states written by both [ClickHouse] and the
external engine to the same result as over the original rows.

### RQ.Iceberg.AggregateStates.Interop.ExternalSchemaEvolution
version: 1.0

After an external engine evolves the schema of a table with annotated fields, for example by
adding a column, the fields carried over into the new current schema SHALL keep their annotations.

## Export

### RQ.Iceberg.AggregateStates.Export.Part
version: 1.0

`ALTER TABLE ... EXPORT PART` from an `AggregatingMergeTree` table into an Iceberg table with
matching state and simple columns SHALL complete when the `ALTER` query has the setting enabled,
and merging the exported states SHALL return the same result as merging them in the source.

### RQ.Iceberg.AggregateStates.Export.Partition
version: 1.0

`ALTER TABLE ... EXPORT PARTITION` from a `ReplicatedAggregatingMergeTree` table into an Iceberg
table with matching state and simple columns SHALL complete when the `ALTER` query has the setting
enabled, and merging the exported states SHALL return the same result as merging them in the
source.

### RQ.Iceberg.AggregateStates.Export.Partition.Manifest
version: 1.0

`EXPORT PARTITION` SHALL record the setting of the `ALTER` query in its task manifest in [Keeper]
as `allow_aggregate_function_states_in_open_formats`, and every replica executing the task SHALL
apply the recorded value in place of its own profile.

### RQ.Iceberg.AggregateStates.Export.Gate
version: 1.0

With the setting disabled on the `ALTER` query, `EXPORT PART` and `EXPORT PARTITION` into an
Iceberg table with an annotated `AggregateFunction` field SHALL fail with a message naming the
setting, and no rows SHALL be committed to the destination.

[ClickHouse]: https://clickhouse.com
[Keeper]: https://clickhouse.com/docs/en/guides/sre/keeper/clickhouse-keeper

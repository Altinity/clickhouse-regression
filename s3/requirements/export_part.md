# SRS-015 ClickHouse Export Part to S3
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Basic Export Functionality](#basic-export-functionality)
    * 2.1 [RQ.ClickHouse.ExportPart.S3](#rqclickhouseexportparts3)
    * 2.2 [RQ.ClickHouse.ExportPart.EmptyTable](#rqclickhouseexportpartemptytable)
    * 2.3 [RQ.ClickHouse.ExportPart.SQLCommand](#rqclickhouseexportpartsqlcommand)
* 3 [Source Table Support](#source-table-support)
    * 3.1 [RQ.ClickHouse.ExportPart.SourceEngines](#rqclickhouseexportpartsourceengines)
    * 3.2 [RQ.ClickHouse.ExportPart.StoragePolicies](#rqclickhouseexportpartstoragepolicies)
* 4 [Schema and Partition Compatibility](#schema-and-partition-compatibility)
    * 4.1 [RQ.ClickHouse.ExportPart.SchemaCompatibility](#rqclickhouseexportpartschemacompatibility)
    * 4.2 [RQ.ClickHouse.ExportPart.PartitionKeyTypes](#rqclickhouseexportpartpartitionkeytypes)
* 5 [Part Types and Content](#part-types-and-content)
    * 5.1 [RQ.ClickHouse.ExportPart.PartTypes](#rqclickhouseexportpartparttypes)
    * 5.2 [RQ.ClickHouse.ExportPart.DeletedRows](#rqclickhouseexportpartdeletedrows)
    * 5.3 [RQ.ClickHouse.ExportPart.SchemaChangeIsolation](#rqclickhouseexportpartschemachangeisolation)
    * 5.4 [RQ.ClickHouse.ExportPart.LargeParts](#rqclickhouseexportpartlargeparts)
    * 5.5 [RQ.ClickHouse.ExportPart.ColumnTypes.Alias](#rqclickhouseexportpartcolumntypesalias)
    * 5.6 [RQ.ClickHouse.ExportPart.ColumnTypes.Materialized](#rqclickhouseexportpartcolumntypesmaterialized)
    * 5.7 [RQ.ClickHouse.ExportPart.ColumnTypes.Default](#rqclickhouseexportpartcolumntypesdefault)
    * 5.8 [RQ.ClickHouse.ExportPart.ColumnTypes.Ephemeral](#rqclickhouseexportpartcolumntypesephemeral)
    * 5.9 [RQ.ClickHouse.ExportPart.ColumnTypes.JSON](#rqclickhouseexportpartcolumntypesjson)
    * 5.10 [RQ.ClickHouse.ExportPart.ColumnTypes.Nested](#rqclickhouseexportpartcolumntypesnested)
* 6 [Export Operation Restrictions](#export-operation-restrictions)
    * 6.1 [RQ.ClickHouse.ExportPart.Restrictions.SameTable](#rqclickhouseexportpartrestrictionssametable)
    * 6.2 [RQ.ClickHouse.ExportPart.Restrictions.LocalTable](#rqclickhouseexportpartrestrictionslocaltable)
    * 6.3 [RQ.ClickHouse.ExportPart.Restrictions.PartitionKey](#rqclickhouseexportpartrestrictionspartitionkey)
    * 6.4 [RQ.ClickHouse.ExportPart.Restrictions.SourcePart](#rqclickhouseexportpartrestrictionssourcepart)
    * 6.5 [RQ.ClickHouse.ExportPart.Restrictions.RemovedPart](#rqclickhouseexportpartrestrictionsremovedpart)
    * 6.6 [RQ.ClickHouse.ExportPart.Restrictions.OutdatedParts](#rqclickhouseexportpartrestrictionsoutdatedparts)
    * 6.7 [RQ.ClickHouse.ExportPart.Restrictions.SimultaneousExport](#rqclickhouseexportpartrestrictionssimultaneousexport)
* 7 [Table Function Destinations](#table-function-destinations)
    * 7.1 [RQ.ClickHouse.ExportPart.TableFunction.Destination](#rqclickhouseexportparttablefunctiondestination)
    * 7.2 [RQ.ClickHouse.ExportPart.TableFunction.ExplicitSchema](#rqclickhouseexportparttablefunctionexplicitschema)
    * 7.3 [RQ.ClickHouse.ExportPart.TableFunction.SchemaInheritance](#rqclickhouseexportparttablefunctionschemainheritance)
* 8 [Export Operation Failure Handling](#export-operation-failure-handling)
    * 8.1 [RQ.ClickHouse.ExportPart.FailureHandling](#rqclickhouseexportpartfailurehandling)
    * 8.2 [RQ.ClickHouse.ExportPart.FailureHandling.PartCorruption](#rqclickhouseexportpartfailurehandlingpartcorruption)
* 9 [Network Resilience](#network-resilience)
    * 9.1 [RQ.ClickHouse.ExportPart.NetworkResilience.PacketIssues](#rqclickhouseexportpartnetworkresiliencepacketissues)
    * 9.2 [RQ.ClickHouse.ExportPart.NetworkResilience.DestinationInterruption](#rqclickhouseexportpartnetworkresiliencedestinationinterruption)
    * 9.3 [RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption](#rqclickhouseexportpartnetworkresiliencenodeinterruption)
* 10 [Export Operation Concurrency](#export-operation-concurrency)
    * 10.1 [RQ.ClickHouse.ExportPart.Concurrency](#rqclickhouseexportpartconcurrency)
    * 10.2 [RQ.ClickHouse.ExportPart.Concurrency.NonBlocking](#rqclickhouseexportpartconcurrencynonblocking)
    * 10.3 [RQ.ClickHouse.ExportPart.Concurrency.ConcurrentAlters](#rqclickhouseexportpartconcurrencyconcurrentalters)
    * 10.4 [RQ.ClickHouse.ExportPart.Concurrency.PendingMutations](#rqclickhouseexportpartconcurrencypendingmutations)
* 11 [Cluster and Node Support](#cluster-and-node-support)
    * 11.1 [RQ.ClickHouse.ExportPart.ClustersNodes](#rqclickhouseexportpartclustersnodes)
    * 11.2 [RQ.ClickHouse.ExportPart.Shards](#rqclickhouseexportpartshards)
* 12 [Export Operation Idempotency](#export-operation-idempotency)
    * 12.1 [RQ.ClickHouse.ExportPart.Idempotency](#rqclickhouseexportpartidempotency)
* 13 [Export Operation Logging](#export-operation-logging)
    * 13.1 [RQ.ClickHouse.ExportPart.Logging](#rqclickhouseexportpartlogging)
* 14 [Monitoring Export Operations](#monitoring-export-operations)
    * 14.1 [RQ.ClickHouse.ExportPart.SystemTables.Exports](#rqclickhouseexportpartsystemtablesexports)
    * 14.2 [RQ.ClickHouse.ExportPart.Metrics.Export](#rqclickhouseexportpartmetricsexport)
* 15 [Settings and Configuration](#settings-and-configuration)
    * 15.1 [RQ.ClickHouse.ExportPart.Settings.AllowExperimental](#rqclickhouseexportpartsettingsallowexperimental)
    * 15.2 [RQ.ClickHouse.ExportPart.Settings.FileAlreadyExistsPolicy](#rqclickhouseexportpartsettingsfilealreadyexistspolicy)
    * 15.3 [RQ.ClickHouse.ExportPart.Settings.MaxBytesPerFile](#rqclickhouseexportpartsettingsmaxbytesperfile)
    * 15.4 [RQ.ClickHouse.ExportPart.Settings.MaxRowsPerFile](#rqclickhouseexportpartsettingsmaxrowsperfile)
    * 15.5 [RQ.ClickHouse.ExportPart.Settings.ThrowOnPendingMutations](#rqclickhouseexportpartsettingsthrowonpendingmutations)
    * 15.6 [RQ.ClickHouse.ExportPart.Settings.ThrowOnPendingPatchParts](#rqclickhouseexportpartsettingsthrowonpendingpatchparts)
    * 15.7 [RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth](#rqclickhouseexportpartserversettingsmaxbandwidth)
    * 15.8 [RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize](#rqclickhouseexportpartserversettingsbackgroundmovepoolsize)
* 16 [Export Operation Security](#export-operation-security)
    * 16.1 [RQ.ClickHouse.ExportPart.Security](#rqclickhouseexportpartsecurity)
    * 16.2 [RQ.ClickHouse.ExportPart.QueryCancellation](#rqclickhouseexportpartquerycancellation)

## Introduction

This specification defines requirements for exporting individual MergeTree data parts to S3-compatible object storage.

## Basic Export Functionality

### RQ.ClickHouse.ExportPart.S3
version: 1.0

[ClickHouse] SHALL support exporting data parts from MergeTree engine tables to S3 object storage.

### RQ.ClickHouse.ExportPart.EmptyTable
version: 1.0

[ClickHouse] SHALL support exporting from empty tables by:
* Completing export operations successfully when the source table contains no parts
* Resulting in an empty destination table when exporting from an empty source table
* Not creating any files in destination storage when there are no parts to export
* Handling empty tables gracefully without errors

### RQ.ClickHouse.ExportPart.SQLCommand
version: 1.0

[ClickHouse] SHALL support the following SQL command syntax for exporting MergeTree data parts to object storage tables:

```sql
ALTER TABLE [database.]source_table_name 
EXPORT PART 'part_name' 
TO TABLE [database.]destination_table_name
```

**Parameters:**
* `source_table_name`: Name of the source MergeTree table
* `part_name`: Name of the specific part to export (string literal)
* `destination_table_name`: Name of the destination object storage table

## Source Table Support

### RQ.ClickHouse.ExportPart.SourceEngines
version: 1.0

[ClickHouse] SHALL support exporting from the following source table engines:
* `MergeTree` - Base MergeTree engine
* `ReplicatedMergeTree` - Replicated MergeTree engine with ZooKeeper coordination
* `SummingMergeTree` - MergeTree with automatic summation of numeric columns
* `AggregatingMergeTree` - MergeTree with pre-aggregated data
* `CollapsingMergeTree` - MergeTree with row versioning for updates
* `VersionedCollapsingMergeTree` - CollapsingMergeTree with version tracking
* `GraphiteMergeTree` - MergeTree optimized for Graphite data
* `ReplacingMergeTree` - MergeTree with automatic deduplication
* All other MergeTree family engines that inherit from `MergeTreeData`

### RQ.ClickHouse.ExportPart.StoragePolicies
version: 1.0

[ClickHouse] SHALL support exporting parts from tables using different storage policies, where storage policies are composed of volumes which are composed of disks, including:
* **JBOD Volumes**: Just a Bunch Of Disks volumes with multiple disks
* **External Volumes**: Volumes using external storage systems
* **Tiered Storage Policies**: Storage policies with multiple volumes for hot/cold data tiers
* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)
* **Cached Disks**: Parts stored with filesystem cache enabled
* **Custom Storage Policies**: Any storage policy configuration composed of volumes and disks
* Exporting parts regardless of which volume or disk within the storage policy contains the part
* Maintaining data integrity when exporting from parts stored on any volume or disk in the storage policy

## Schema and Partition Compatibility

### RQ.ClickHouse.ExportPart.SchemaCompatibility
version: 1.0

[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:
* Identical physical column schemas between source and destination
* The same partition key expression in both tables
* Compatible data types for all columns
* Matching column order and names

### RQ.ClickHouse.ExportPart.PartitionKeyTypes
version: 1.0

[ClickHouse] SHALL support export operations for tables with partition key types that are compatible with Hive partitioning, as shown in the following table:

| Partition Key Type | Supported | Examples | Notes |
|-------------------|------------|----------|-------|
| **Integer Types** | ✅ Yes | `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64` | All integer types supported |
| **Date/DateTime Types** | ✅ Yes | `Date`, `Date32`, `DateTime`, `DateTime64` | All date/time types supported |
| **String Types** | ✅ Yes | `String`, `FixedString` | All string types supported |
| **No Partition Key** | ✅ Yes | Tables without `PARTITION BY` clause | Unpartitioned tables supported |

[ClickHouse] SHALL automatically extract partition values from source parts and use them to create proper Hive partitioning structure in destination storage, but only for partition key types that are compatible with Hive partitioning requirements.

[ClickHouse] SHALL require destination tables to support Hive partitioning, which limits the supported partition key types to Integer, Date/DateTime, and String types. Complex expressions that result in unsupported types are not supported for export operations.

## Part Types and Content

### RQ.ClickHouse.ExportPart.PartTypes
version: 1.0

[ClickHouse] SHALL support export operations for all valid MergeTree part types and their contents, including:

| Part Type | Supported | Description | Special Features |
|-----------|------------|-------------|------------------|
| **Wide Parts** | ✅ Yes | Data of each column stored in separate files with marks | Standard format for most parts |
| **Compact Parts** | ✅ Yes | All column data stored in single file with single marks file | Optimized for small parts |

### RQ.ClickHouse.ExportPart.DeletedRows
version: 1.0

[ClickHouse] SHALL correctly handle parts containing deleted rows during export operations by:

* Automatically applying delete masks (`_row_exists` column) when exporting parts that contain rows marked as deleted via lightweight DELETE (`DELETE FROM ... WHERE ...`)
* Excluding rows marked as deleted from exported data, ensuring only visible rows (`_row_exists = 1`) are exported
* Supporting export of parts where rows have been physically removed via ALTER DELETE (`ALTER TABLE ... DELETE WHERE ...`)
* Maintaining data consistency between source and destination tables after export, where destination contains only non-deleted rows from source

### RQ.ClickHouse.ExportPart.SchemaChangeIsolation
version: 1.0

[ClickHouse] SHALL ensure exported data is isolated from subsequent schema changes by:
* Preserving exported data exactly as it was at the time of export
* Not being affected by schema changes (column drops, renames, type changes) that occur after export
* Maintaining data integrity in destination storage regardless of mutations applied to the source table after export
* Ensuring exported data reflects the source table state at the time of export, not the current state

### RQ.ClickHouse.ExportPart.LargeParts
version: 1.0

[ClickHouse] SHALL support exporting large parts by:
* Handling parts with large numbers of rows (e.g., 100 million or more)
* Processing large data volumes efficiently during export
* Maintaining data integrity when exporting large parts
* Completing export operations successfully regardless of part size

### RQ.ClickHouse.ExportPart.ColumnTypes.Alias
version: 1.0

[ClickHouse] SHALL support exporting parts containing tables with ALIAS columns by:
* Computing ALIAS column values on-the-fly from expressions during export (ALIAS columns are not stored in parts)
* Exporting ALIAS column values as regular columns in the destination table
* Requiring destination tables to have matching regular columns (not ALIAS) for exported ALIAS columns
* Materializing ALIAS column values during export and writing them as regular column data

ALIAS columns are computed from expressions (e.g., `arr_1 ALIAS arr[1]`). During export, the system SHALL compute the ALIAS column values and export them as regular column data to the destination table.

### RQ.ClickHouse.ExportPart.ColumnTypes.Materialized
version: 1.0

[ClickHouse] SHALL support exporting parts containing tables with MATERIALIZED columns by:
* Reading MATERIALIZED column values from storage during export (MATERIALIZED columns are stored in parts and computed from expressions)
* Exporting MATERIALIZED column values as regular columns in the destination table
* Requiring destination tables to have matching regular columns (not MATERIALIZED) for exported MATERIALIZED columns

MATERIALIZED columns are stored in parts and computed from expressions (e.g., `value * 3`). During export, the system SHALL read the stored MATERIALIZED column values and export them as regular column data to the destination table.

### RQ.ClickHouse.ExportPart.ColumnTypes.Default
version: 1.0

[ClickHouse] SHALL support exporting parts containing tables with DEFAULT columns by:
* Requiring the destination table to have a matching column that is NOT tagged as DEFAULT (must be a regular column)
* Materializing the source DEFAULT column values during export (using either the default value or explicit value provided during INSERT)
* Exporting the materialized values as a regular column to the destination table
* Correctly handling both cases:
  * When default values are used (no explicit value provided during INSERT)
  * When explicit non-default values are provided during INSERT

The destination table schema SHALL require a regular column (not DEFAULT) that matches the source DEFAULT column's name and data type. During export, the system SHALL compute the actual values for DEFAULT columns (default or explicit) and export them as regular column data. This allows users to export parts from source tables with DEFAULT columns to destination object storage tables that do not support DEFAULT columns.

DEFAULT columns have default values (e.g., `status String DEFAULT 'active'`). The system SHALL materialize these values during export and write them as regular columns to the destination.

### RQ.ClickHouse.ExportPart.ColumnTypes.Ephemeral
version: 1.0

[ClickHouse] SHALL support exporting parts containing tables with EPHEMERAL columns by:
* Completely ignoring EPHEMERAL columns during export (EPHEMERAL columns are not stored and cannot be read from parts)
* NOT exporting EPHEMERAL columns to the destination table
* Requiring destination tables to NOT have matching columns for EPHEMERAL columns from the source table
* Allowing EPHEMERAL columns to be used in DEFAULT column expressions, where the DEFAULT column values (computed from EPHEMERAL values) SHALL be exported correctly

EPHEMERAL columns are not stored and are only used for DEFAULT column computation. During export, EPHEMERAL columns SHALL be completely ignored and SHALL NOT appear in the destination table schema.

### RQ.ClickHouse.ExportPart.ColumnTypes.JSON
version: 1.0

[ClickHouse] SHALL support exporting parts containing tables with JSON columns by:
* Exporting JSON column values as JSON columns in the destination table
* Preserving JSON structure and nested data during export
* Supporting JSON columns with type hints (e.g., `JSON(a.b UInt32, a.c String)`)
* Maintaining data integrity for complex JSON structures including nested objects and arrays

JSON columns store semi-structured data. During export, the system SHALL preserve the JSON column values and structure in the destination table.

### RQ.ClickHouse.ExportPart.ColumnTypes.Nested
version: 1.0

[ClickHouse] SHALL support exporting parts containing tables with Nested columns by:
* Exporting Nested column values as Nested columns in the destination table
* Preserving the nested structure with all sub-columns during export
* Supporting complex Nested columns containing arrays within nested structures
* Maintaining data integrity for all nested sub-columns (e.g., `nested_data.key`, `nested_data.value`)

Nested columns store structured arrays with multiple named sub-columns. During export, the system SHALL preserve the Nested column structure and all sub-column values in the destination table.

## Export Operation Restrictions

### RQ.ClickHouse.ExportPart.Restrictions.SameTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to the same table as the source by:
* Validating that source and destination table identifiers are different
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Exporting to the same table is not allowed" when source and destination are identical
* Performing this validation before any export processing begins

### RQ.ClickHouse.ExportPart.Restrictions.LocalTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to local MergeTree tables by:
* Rejecting export operations where the destination table uses a MergeTree engine
* Throwing a `NOT_IMPLEMENTED` exception (error code 48) with message "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning" when attempting to export to a local table
* Performing this validation during the initial export setup phase

### RQ.ClickHouse.ExportPart.Restrictions.PartitionKey
version: 1.0

[ClickHouse] SHALL validate that source and destination tables have the same partition key expression by:
* Checking that the partition key expression matches between source and destination tables
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Tables have different partition key" when partition keys differ
* Performing this validation during the initial export setup phase

### RQ.ClickHouse.ExportPart.Restrictions.SourcePart
version: 1.0

[ClickHouse] SHALL validate source part availability by:
* Checking that the specified part exists in the source table
* Verifying the part name format is valid
* Throwing a `BAD_DATA_PART_NAME` exception (error code 233) with message containing "Unexpected part name" when the part name is invalid
* Performing this validation before creating the export manifest

### RQ.ClickHouse.ExportPart.Restrictions.RemovedPart
version: 1.0

[ClickHouse] SHALL handle attempts to export parts that have been removed from the source table by:
* Detecting when a part has been detached or dropped before export completes
* Throwing a `NO_SUCH_DATA_PART` exception (error code 232) when attempting to export a removed part
* Handling both detached parts and dropped parts/partitions correctly
* Performing this validation during export execution

### RQ.ClickHouse.ExportPart.Restrictions.OutdatedParts
version: 1.0

[ClickHouse] SHALL prevent exporting parts that are in the outdated state by:
* Rejecting export operations for parts with `active = 0` (outdated parts)
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message indicating the part is in the outdated state and cannot be exported
* Performing this validation before any export processing begins

### RQ.ClickHouse.ExportPart.Restrictions.SimultaneousExport
version: 1.0

[ClickHouse] SHALL prevent exporting the same part simultaneously to different locations by:
* Uniquely identifying part exports by part name
* Rejecting attempts to export a part that is already being exported to another location
* Returning an error when attempting to export the same part to multiple destinations concurrently

The system SHALL track active exports by part name and SHALL NOT allow the same part to be exported to different destinations at the same time.

## Table Function Destinations

### RQ.ClickHouse.ExportPart.TableFunction.Destination
version: 1.0

[ClickHouse] SHALL support exporting parts to table functions as destinations using the following syntax:

```sql
ALTER TABLE source_table 
EXPORT PART 'part_name' 
TO TABLE FUNCTION s3(...)
PARTITION BY ...
```

The system SHALL support table functions (e.g., `s3`) as export destinations, allowing parts to be exported directly to object storage without requiring a pre-existing table.

### RQ.ClickHouse.ExportPart.TableFunction.ExplicitSchema
version: 1.0

[ClickHouse] SHALL support exporting parts to table functions with an explicit schema/structure parameter by:
* Accepting a `structure` parameter in the table function definition that explicitly defines column names and types
* Using the provided structure when exporting parts to the table function
* Verifying that the exported data matches the specified structure

When a `structure` parameter is provided, the system SHALL use it to define the destination schema for the exported data.

### RQ.ClickHouse.ExportPart.TableFunction.SchemaInheritance
version: 1.0

[ClickHouse] SHALL support exporting parts to table functions with schema inheritance by:
* Automatically inheriting the schema from the source table when no `structure` parameter is provided
* Matching column names between source and destination
* Exporting data that matches the source table structure

When no `structure` parameter is provided, the system SHALL automatically infer the schema from the source table and use it for the table function destination.

## Export Operation Failure Handling

### RQ.ClickHouse.ExportPart.FailureHandling
version: 1.0

[ClickHouse] SHALL handle export operation failures in the following ways:
* **Stateless Operation**: Export operations are stateless and ephemeral
* **No Recovery**: If an export fails, it fails completely with no retry mechanism
* **No State Persistence**: No export manifests or state are preserved across server restarts
* **Simple Failure**: Export operations either succeed completely or fail with an error message
* **No Partial Exports**: Failed exports leave no partial or corrupted data in destination storage
* **Error Logging**: Failed exports are logged in `system.part_log` with error status

### RQ.ClickHouse.ExportPart.FailureHandling.PartCorruption
version: 1.0

[ClickHouse] SHALL handle corrupted source parts during export by:
* Detecting corruption when reading part data during export
* Failing the export operation with an appropriate error code
* Logging the failure in `system.part_log` with error status
* Not exporting corrupted parts to destination storage
* Allowing non-corrupted parts to export successfully even when other parts are corrupted

## Network Resilience

### RQ.ClickHouse.ExportPart.NetworkResilience.PacketIssues
version: 1.0

[ClickHouse] SHALL handle network packet issues during export operations by:
* Tolerating packet delay without data corruption or loss
* Handling packet loss and retransmitting data as needed
* Detecting and handling packet corruption to ensure data integrity
* Managing packet duplication without data duplication in destination
* Handling packet reordering to maintain correct data sequence
* Operating correctly under packet rate limiting constraints
* Completing exports successfully despite network impairments

### RQ.ClickHouse.ExportPart.NetworkResilience.DestinationInterruption
version: 1.0

[ClickHouse] SHALL handle destination storage interruptions during export operations by:
* Detecting when destination storage becomes unavailable during export
* Failing export operations gracefully when destination storage is unavailable
* Logging failed exports in the `system.events` table with `PartsExportFailures` counter
* Not leaving partial or corrupted data in destination storage when exports fail due to destination unavailability
* Allowing exports to complete successfully once destination storage becomes available again
* Handling interruptions at different stages: before export starts, during export, after export completes

### RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption
version: 1.0

[ClickHouse] SHALL handle ClickHouse node interruptions during export operations by:
* Handling node restarts gracefully during export operations
* Not leaving partial or corrupted data in destination storage when node restarts occur
* With safe shutdown, ensuring exports complete successfully before node shutdown
* With unsafe shutdown, allowing partial exports to complete successfully after node restart
* Maintaining data integrity in destination storage regardless of node interruption type
* Handling interruptions at different stages: before export starts, during export, after export completes

## Export Operation Concurrency

### RQ.ClickHouse.ExportPart.Concurrency
version: 1.0

[ClickHouse] SHALL support concurrent export operations by:
* Allowing multiple exports to run simultaneously without interference
* Processing export operations asynchronously in the background
* Preventing race conditions and data corruption during concurrent operations
* Supporting concurrent exports of different parts to different destinations
* Supporting concurrent exports from multiple source tables to the same destination
* Preventing concurrent exports of the same part to the same destination
* Maintaining separate progress tracking and state for each concurrent operation
* Ensuring thread safety across all concurrent export operations

### RQ.ClickHouse.ExportPart.Concurrency.NonBlocking
version: 1.0

[ClickHouse] SHALL ensure that export operations do not block other operations on the source table by:
* Allowing SELECT queries to execute concurrently with exports without blocking
* Allowing INSERT operations to execute concurrently with exports without blocking
* Allowing MERGE operations to execute concurrently with exports without blocking
* Ensuring that reads and writes to the source table are not blocked by active export operations
* Maintaining data consistency for concurrent operations

### RQ.ClickHouse.ExportPart.Concurrency.ConcurrentAlters
version: 1.0

[ClickHouse] SHALL support concurrent ALTER operations on the source table during export by:
* Allowing ALTER operations to execute concurrently with exports
* Ensuring exported data reflects the source table state at the time export was initiated
* Supporting ALTER operations before export (export uses post-ALTER schema)
* Supporting ALTER operations after export (exported data unaffected)
* Supporting ALTER operations during export (export uses pre-ALTER schema snapshot)
* Maintaining data integrity when ALTER operations occur concurrently with exports
* Handling various ALTER operations: add/drop columns, modify columns, rename columns, add/drop constraints, TTL modifications, partition operations, mutations, etc.

### RQ.ClickHouse.ExportPart.Concurrency.PendingMutations
version: 1.0

[ClickHouse] SHALL ignore pending mutations during export operations by:

* Capturing a snapshot of the part at the time of export execution
* Exporting the part data as it exists at the time of execution, without applying pending mutations on the fly
* Maintaining data consistency where exported data reflects the source table state at the moment the export reads the part

For example, if an `ALTER TABLE ... DELETE WHERE ...` mutation is pending when an export starts, the exported data SHALL reflect the part state at the time the export reads it. Pending mutations are not applied during the export operation - the export takes a snapshot of the part as it currently exists.

## Cluster and Node Support

### RQ.ClickHouse.ExportPart.ClustersNodes
version: 1.0

[ClickHouse] SHALL support exporting parts from multiple nodes in a cluster to the same destination storage, ensuring that:
* Each node can independently export parts from its local storage to the shared destination
* Exported data from different nodes is correctly aggregated in the destination
* All nodes in the cluster can read the same exported data from the destination
* Supporting various cluster configurations: sharded, replicated, one-shard clusters

### RQ.ClickHouse.ExportPart.Shards
version: 1.0

[ClickHouse] SHALL support exporting parts from sharded tables using Distributed engine, ensuring that:
* Parts can be exported from local tables on each shard independently
* Data distributed across multiple shards via Distributed table is correctly aggregated in the destination
* Export operations work correctly with Distributed tables that use sharding keys for data distribution
* Exported data from all shards matches the complete data view from the Distributed table
* Distributed tables with multiple shards require a sharding key for inserts (error code 55: STORAGE_REQUIRES_PARAMETER)
* Invalid sharding keys in Distributed table definitions are rejected (error code 47: UNKNOWN_IDENTIFIER)
* Distributed tables pointing to non-existent local tables fail when inserting (error code 60: UNKNOWN_TABLE)

## Export Operation Idempotency

### RQ.ClickHouse.ExportPart.Idempotency
version: 1.0

[ClickHouse] SHALL handle duplicate export operations by:
* Detecting when an export operation attempts to export a part that already exists in the destination
* Supporting configurable policies for handling file conflicts: `skip`, `error`, `overwrite`
* With `skip` policy: Logging duplicate attempts in `system.events` with `PartsExportDuplicated` counter, not incrementing `PartsExportFailures`, treating as success
* With `error` policy: Logging duplicate attempts in `system.events` with both `PartsExportDuplicated` and `PartsExportFailures` counters, failing the export
* With `overwrite` policy: Overwriting existing files, logging as successful export, not incrementing duplicate or failure counters
* Ensuring that destination data matches source data without duplication when the same part is exported multiple times with `skip` policy
* Logging duplicate export attempts in the `system.events` table with the `PartsExportDuplicated` counter

## Export Operation Logging

### RQ.ClickHouse.ExportPart.Logging
version: 1.0

[ClickHouse] SHALL provide detailed logging for export operations by:
* Logging all export operations (both successful and failed) with timestamps and details
* Recording the specific part name in the `system.part_log` table for all operations
* Logging export events in the `system.events` table, including:
  * `PartsExports` - Number of successful part exports
  * `PartsExportFailures` - Number of failed part exports
  * `PartsExportDuplicated` - Number of part exports that detected existing files
  * `PartsExportTotalMilliseconds` - Total time spent exporting
* Writing operation information to the `system.part_log` table with `event_type` set to `EXPORT_PART`
* Logging failed exports with error status and error details in `system.part_log`
* Providing sufficient detail for monitoring and troubleshooting export operations

## Monitoring Export Operations

### RQ.ClickHouse.ExportPart.SystemTables.Exports
version: 1.0

[ClickHouse] SHALL provide a `system.exports` table that allows users to monitor active export operations with at least the following columns:
* `source_table` - source table identifier
* `destination_table` - destination table identifier
* `part_name` - name of the part being exported
* Additional metadata about the export operation

The table SHALL track export operations before they complete and SHALL be empty after all exports complete.

### RQ.ClickHouse.ExportPart.Metrics.Export
version: 1.0

[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing exports.

## Settings and Configuration

### RQ.ClickHouse.ExportPart.Settings.AllowExperimental
version: 1.0

[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export part functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PART ...` commands. The default value SHALL be `0` (turned off).

[ClickHouse] SHALL reject export operations when this setting is disabled, throwing an exception (error code 88) with message "Exporting merge tree part is experimental".

### RQ.ClickHouse.ExportPart.Settings.FileAlreadyExistsPolicy
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_file_already_exists_policy` setting that controls behavior when exporting a part that already exists in the destination. The setting SHALL accept the following values:
* `skip` (default) - Skip the export if file already exists, log as duplicate, treat as success
* `error` - Fail the export if file already exists, log as duplicate and failure
* `overwrite` - Overwrite existing file, proceed with export

### RQ.ClickHouse.ExportPart.Settings.MaxBytesPerFile
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_max_bytes_per_file` setting that controls the maximum size of individual files created during export operations. When a part export exceeds this size limit, [ClickHouse] SHALL automatically split the exported data into multiple files, each not exceeding the specified byte limit.

[ClickHouse] SHALL:
* Split exported parts into multiple files when the export size exceeds `export_merge_tree_part_max_bytes_per_file`
* Name split files with numeric suffixes (e.g., `part_name.1.parquet`, `part_name.2.parquet`) to distinguish them
* Ensure all split files are readable by the destination S3 table engine
* Maintain data integrity across all split files, ensuring the sum of rows in all split files equals the total rows in the source part

### RQ.ClickHouse.ExportPart.Settings.MaxRowsPerFile
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_max_rows_per_file` setting that controls the maximum number of rows in individual files created during export operations. When a part export exceeds this row limit, [ClickHouse] SHALL automatically split the exported data into multiple files, each containing no more than the specified number of rows.

[ClickHouse] SHALL:
* Split exported parts into multiple files when the export row count exceeds `export_merge_tree_part_max_rows_per_file`
* Name split files with numeric suffixes (e.g., `part_name.1.parquet`, `part_name.2.parquet`) to distinguish them
* Ensure all split files are readable by the destination S3 table engine
* Maintain data integrity across all split files, ensuring the sum of rows in all split files equals the total rows in the source part

### RQ.ClickHouse.ExportPart.Settings.ThrowOnPendingMutations
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_throw_on_pending_mutations` setting that controls whether export operations throw an error when pending mutations exist. The setting SHALL:
* Default to `true` - throw an error when pending mutations exist
* When set to `false` - allow exports to proceed with pending mutations, exporting the part as it exists at export time without applying mutations
* Throw a `PENDING_MUTATIONS_NOT_ALLOWED` exception (error code 237) when set to `true` and pending mutations exist

### RQ.ClickHouse.ExportPart.Settings.ThrowOnPendingPatchParts
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_throw_on_pending_patch_parts` setting that controls whether export operations throw an error when pending patch parts exist. The setting SHALL:
* Default to `true` - throw an error when pending patch parts exist
* When set to `false` - allow exports to proceed with pending patch parts, exporting the part as it exists at export time without applying patches
* Throw a `PENDING_MUTATIONS_NOT_ALLOWED` exception (error code 237) when set to `true` and pending patch parts exist

### RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth
version: 1.0

[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.

### RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize
version: 1.0

[ClickHouse] SHALL support the `background_move_pool_size` server setting to control the maximum number of threads that will be used for executing export operations in the background. The default value SHALL be `8`. This is a server-level setting configured in the server configuration file.

## Export Operation Security

### RQ.ClickHouse.ExportPart.Security
version: 1.0

[ClickHouse] SHALL enforce security requirements for export operations:
* **RBAC**: Users must have the following privileges:
  * **Source Table**: `ALTER` privilege on the source table to initiate export operations
  * **Destination Table**: `INSERT` privilege on the destination table to write exported data
* **Data Encryption**: All data in transit to destination storage must be encrypted using TLS/SSL
* **Network Security**: Export operations must use secure connections to destination storage (HTTPS for S3, secure protocols for other storage)
* **Credential Management**: Export operations must use secure credential storage and avoid exposing credentials in logs

### RQ.ClickHouse.ExportPart.QueryCancellation
version: 1.0

[ClickHouse] SHALL support cancellation of `EXPORT PART` queries using the `KILL QUERY` command before the query returns.

The system SHALL:
* Stop exporting parts that have not yet begun exporting when the query is killed
* Handle query cancellation gracefully without breaking the system or corrupting data

[ClickHouse]: https://clickhouse.com

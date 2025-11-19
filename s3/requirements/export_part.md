# SRS-015 ClickHouse Export Part to S3
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Exporting Parts to S3](#exporting-parts-to-s3)
    * 2.1 [RQ.ClickHouse.ExportPart.S3](#rqclickhouseexportparts3)
    * 2.2 [RQ.ClickHouse.ExportPart.EmptyTable](#rqclickhouseexportpartemptytable)
* 3 [SQL command support](#sql-command-support)
    * 3.1 [RQ.ClickHouse.ExportPart.SQLCommand](#rqclickhouseexportpartsqlcommand)
* 4 [Supported source table engines](#supported-source-table-engines)
    * 4.1 [RQ.ClickHouse.ExportPart.SourceEngines](#rqclickhouseexportpartsourceengines)
* 5 [Cluster and node support](#cluster-and-node-support)
    * 5.1 [RQ.ClickHouse.ExportPart.ClustersNodes](#rqclickhouseexportpartclustersnodes)
* 6 [Supported source part storage types](#supported-source-part-storage-types)
    * 6.1 [RQ.ClickHouse.ExportPart.SourcePartStorage](#rqclickhouseexportpartsourcepartstorage)
* 7 [Storage policies and volumes](#storage-policies-and-volumes)
    * 7.1 [RQ.ClickHouse.ExportPart.StoragePolicies](#rqclickhouseexportpartstoragepolicies)
* 8 [Supported destination table engines](#supported-destination-table-engines)
    * 8.1 [RQ.ClickHouse.ExportPart.DestinationEngines](#rqclickhouseexportpartdestinationengines)
* 9 [Schema compatibility](#schema-compatibility)
    * 9.1 [RQ.ClickHouse.ExportPart.SchemaCompatibility](#rqclickhouseexportpartschemacompatibility)
* 10 [Partition key types support](#partition-key-types-support)
    * 10.1 [RQ.ClickHouse.ExportPart.PartitionKeyTypes](#rqclickhouseexportpartpartitionkeytypes)
* 11 [Part types and content support](#part-types-and-content-support)
    * 11.1 [RQ.ClickHouse.ExportPart.PartTypes](#rqclickhouseexportpartparttypes)
    * 11.2 [RQ.ClickHouse.ExportPart.SchemaChangeIsolation](#rqclickhouseexportpartschemachangeisolation)
    * 11.3 [RQ.ClickHouse.ExportPart.LargeParts](#rqclickhouseexportpartlargeparts)
* 12 [Export operation failure handling](#export-operation-failure-handling)
    * 12.1 [RQ.ClickHouse.ExportPart.FailureHandling](#rqclickhouseexportpartfailurehandling)
* 13 [Network resilience](#network-resilience)
    * 13.1 [RQ.ClickHouse.ExportPart.NetworkResilience.PacketIssues](#rqclickhouseexportpartnetworkresiliencepacketissues)
    * 13.2 [RQ.ClickHouse.ExportPart.NetworkResilience.DestinationInterruption](#rqclickhouseexportpartnetworkresiliencedestinationinterruption)
    * 13.3 [RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption](#rqclickhouseexportpartnetworkresiliencenodeinterruption)
* 14 [Export operation restrictions](#export-operation-restrictions)
    * 14.1 [Preventing same table exports](#preventing-same-table-exports)
        * 14.1.1 [RQ.ClickHouse.ExportPart.Restrictions.SameTable](#rqclickhouseexportpartrestrictionssametable)
    * 14.2 [Local table restriction](#local-table-restriction)
        * 14.2.1 [RQ.ClickHouse.ExportPart.Restrictions.LocalTable](#rqclickhouseexportpartrestrictionslocaltable)
    * 14.3 [Partition key compatibility](#partition-key-compatibility)
        * 14.3.1 [RQ.ClickHouse.ExportPart.Restrictions.PartitionKey](#rqclickhouseexportpartrestrictionspartitionkey)
    * 14.4 [Source part availability](#source-part-availability)
        * 14.4.1 [RQ.ClickHouse.ExportPart.Restrictions.SourcePart](#rqclickhouseexportpartrestrictionssourcepart)
* 15 [Export operation concurrency](#export-operation-concurrency)
    * 15.1 [RQ.ClickHouse.ExportPart.Concurrency](#rqclickhouseexportpartconcurrency)
* 16 [Export operation idempotency](#export-operation-idempotency)
    * 16.1 [RQ.ClickHouse.ExportPart.Idempotency](#rqclickhouseexportpartidempotency)
* 17 [Export operation logging](#export-operation-logging)
    * 17.1 [RQ.ClickHouse.ExportPart.Logging](#rqclickhouseexportpartlogging)
* 18 [Monitoring export operations](#monitoring-export-operations)
    * 18.1 [RQ.ClickHouse.ExportPart.SystemTables.Exports](#rqclickhouseexportpartsystemtablesexports)
* 19 [Enabling export functionality](#enabling-export-functionality)
    * 19.1 [RQ.ClickHouse.ExportPart.Settings.AllowExperimental](#rqclickhouseexportpartsettingsallowexperimental)
* 20 [Handling file conflicts during export](#handling-file-conflicts-during-export)
    * 20.1 [RQ.ClickHouse.ExportPart.Settings.OverwriteFile](#rqclickhouseexportpartsettingsoverwritefile)
* 21 [Controlling export performance](#controlling-export-performance)
    * 21.1 [RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth](#rqclickhouseexportpartserversettingsmaxbandwidth)
    * 21.2 [RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize](#rqclickhouseexportpartserversettingsbackgroundmovepoolsize)
    * 21.3 [RQ.ClickHouse.ExportPart.Metrics.Export](#rqclickhouseexportpartmetricsexport)
* 22 [Export operation security](#export-operation-security)
    * 22.1 [RQ.ClickHouse.ExportPart.Security](#rqclickhouseexportpartsecurity)

## Introduction

This specification defines requirements for exporting individual MergeTree data parts to S3-compatible object storage.

## Exporting Parts to S3

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

## SQL command support

### RQ.ClickHouse.ExportPart.SQLCommand
version: 1.0

[ClickHouse] SHALL support the following SQL command syntax for exporting MergeTree data parts to object storage tables:

```sql
ALTER TABLE [database.]source_table_name 
EXPORT PART 'part_name' 
TO TABLE [database.]destination_table_name
```

**Parameters:**
- `source_table_name`: Name of the source MergeTree table
- `part_name`: Name of the specific part to export (string literal)
- `destination_table_name`: Name of the destination object storage table

## Supported source table engines

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
* All other MergeTree family engines that inherit from `MergeTreeData`

## Cluster and node support

### RQ.ClickHouse.ExportPart.ClustersNodes
version: 1.0

[ClickHouse] SHALL support exporting parts from multiple nodes in a cluster to the same destination storage, ensuring that:
* Each node can independently export parts from its local storage to the shared destination
* Exported data from different nodes is correctly aggregated in the destination
* All nodes in the cluster can read the same exported data from the destination

## Supported source part storage types

### RQ.ClickHouse.ExportPart.SourcePartStorage
version: 1.0

[ClickHouse] SHALL support exporting data parts regardless of the underlying storage type where the source parts are stored, including:
* **Local Disks**: Parts stored on local filesystem
* **S3/Object Storage**: Parts stored on S3 or S3-compatible object storage
* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)
* **Cached Disks**: Parts stored with filesystem cache enabled
* **Remote Disks**: Parts stored on HDFS, Azure Blob Storage, or Google Cloud Storage
* **Tiered Storage**: Parts stored across multiple storage tiers (hot/cold)
* **Zero-Copy Replication Disks**: Parts stored with zero-copy replication enabled

## Storage policies and volumes

### RQ.ClickHouse.ExportPart.StoragePolicies
version: 1.0

[ClickHouse] SHALL support exporting parts from tables using different storage policies, where storage policies are composed of volumes which are composed of disks, including:
* **JBOD Volumes**: Just a Bunch Of Disks volumes with multiple disks
* **External Volumes**: Volumes using external storage systems
* **Tiered Storage Policies**: Storage policies with multiple volumes for hot/cold data tiers
* **Custom Storage Policies**: Any storage policy configuration composed of volumes and disks
* Exporting parts regardless of which volume or disk within the storage policy contains the part
* Maintaining data integrity when exporting from parts stored on any volume or disk in the storage policy

## Supported destination table engines

### RQ.ClickHouse.ExportPart.DestinationEngines
version: 1.0

[ClickHouse] SHALL support exporting to destination tables that:
* Support object storage engines including:
  * `S3` - Amazon S3 and S3-compatible storage
  * `StorageObjectStorage` - Generic object storage interface
  * `HDFS` - Hadoop Distributed File System (with Hive partitioning)
  * `Azure` - Microsoft Azure Blob Storage (with Hive partitioning)
  * `GCS` - Google Cloud Storage (with Hive partitioning)

## Schema compatibility

### RQ.ClickHouse.ExportPart.SchemaCompatibility
version: 1.0

[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:
* Identical physical column schemas between source and destination
* The same partition key expression in both tables
* Compatible data types for all columns
* Matching column order and names

## Partition key types support

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

## Part types and content support

### RQ.ClickHouse.ExportPart.PartTypes
version: 1.0

[ClickHouse] SHALL support export operations for all valid MergeTree part types and their contents, including:

| Part Type | Supported | Description | Special Features |
|-----------|------------|-------------|------------------|
| **Wide Parts** | ✅ Yes | Data of each column stored in separate files with marks | Standard format for most parts |
| **Compact Parts** | ✅ Yes | All column data stored in single file with single marks file | Optimized for small parts |

[ClickHouse] SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL handle all part metadata including checksums, compression information, serialization details, mutation history, schema changes, and structural modifications to maintain data integrity in the destination storage.

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

## Export operation failure handling

### RQ.ClickHouse.ExportPart.FailureHandling
version: 1.0

[ClickHouse] SHALL handle export operation failures in the following ways:
* **Stateless Operation**: Export operations are stateless and ephemeral
* **No Recovery**: If an export fails, it fails completely with no retry mechanism
* **No State Persistence**: No export manifests or state are preserved across server restarts
* **Simple Failure**: Export operations either succeed completely or fail with an error message
* **No Partial Exports**: Failed exports leave no partial or corrupted data in destination storage

## Network resilience

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

### RQ.ClickHouse.ExportPart.NetworkResilience.NodeInterruption
version: 1.0

[ClickHouse] SHALL handle ClickHouse node interruptions during export operations by:
* Handling node restarts gracefully during export operations
* Not leaving partial or corrupted data in destination storage when node restarts occur
* With safe shutdown, ensuring exports complete successfully before node shutdown
* With unsafe shutdown, allowing partial exports to complete successfully after node restart
* Maintaining data integrity in destination storage regardless of node interruption type

## Export operation restrictions

### Preventing same table exports

#### RQ.ClickHouse.ExportPart.Restrictions.SameTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to the same table as the source by:
* Validating that source and destination table identifiers are different
* Throwing a `BAD_ARGUMENTS` exception with message "Exporting to the same table is not allowed" when source and destination are identical
* Performing this validation before any export processing begins

### Local table restriction

#### RQ.ClickHouse.ExportPart.Restrictions.LocalTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to local MergeTree tables by:
* Rejecting export operations where the destination table uses a MergeTree engine
* Throwing a `NOT_IMPLEMENTED` exception (error code 48) with message "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning" when attempting to export to a local table
* Performing this validation during the initial export setup phase

### Partition key compatibility

#### RQ.ClickHouse.ExportPart.Restrictions.PartitionKey
version: 1.0

[ClickHouse] SHALL validate that source and destination tables have the same partition key expression by:
* Checking that the partition key expression matches between source and destination tables
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Tables have different partition key" when partition keys differ
* Performing this validation during the initial export setup phase

### Source part availability

#### RQ.ClickHouse.ExportPart.Restrictions.SourcePart
version: 1.0

[ClickHouse] SHALL validate source part availability by:
* Checking that the specified part exists in the source table
* Verifying the part is in an active state (not detached or missing)
* Throwing an exception with message containing "Unexpected part name" when the part is not found
* Performing this validation before creating the export manifest

## Export operation concurrency

### RQ.ClickHouse.ExportPart.Concurrency
version: 1.0

[ClickHouse] SHALL support concurrent export operations by:

* Allowing multiple exports to run simultaneously without interference
* Processing export operations asynchronously in the background
* Preventing race conditions and data corruption during concurrent operations
* Supporting concurrent exports of different parts to different destinations
* Preventing concurrent exports of the same part to the same destination
* Maintaining separate progress tracking and state for each concurrent operation
* Ensuring thread safety across all concurrent export operations

## Export operation idempotency

### RQ.ClickHouse.ExportPart.Idempotency
version: 1.0

[ClickHouse] SHALL handle duplicate export operations by:
* Preventing duplicate data from being exported when the same part is exported multiple times to the same destination
* Detecting when an export operation attempts to export a part that already exists in the destination
* Logging duplicate export attempts in the `system.events` table with the `PartsExportDuplicated` counter
* Ensuring that destination data matches source data without duplication when the same part is exported multiple times

## Export operation logging

### RQ.ClickHouse.ExportPart.Logging
version: 1.0

[ClickHouse] SHALL provide detailed logging for export operations by:
* Logging all export operations (both successful and failed) with timestamps and details
* Recording the specific part name in the `system.part_log` table for all operations
* Logging export events in the `system.events` table, including:
  * `PartsExports` - Number of successful part exports
  * `PartsExportFailures` - Number of failed part exports
  * `PartsExportDuplicated` - Number of part exports that failed because target already exists
* Writing operation information to the `system.part_log` table with `event_type` set to `EXPORT_PART`
* Providing sufficient detail for monitoring and troubleshooting export operations

## Monitoring export operations

### RQ.ClickHouse.ExportPart.SystemTables.Exports
version: 1.0

[ClickHouse] SHALL provide a `system.exports` table that allows users to monitor active export operations with at least the following columns:
* `source_table` - source table identifier
* `destination_table` - destination table identifier

The table SHALL track export operations before they complete and SHALL be empty after all exports complete.

## Enabling export functionality

### RQ.ClickHouse.ExportPart.Settings.AllowExperimental
version: 1.0

[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export part functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PART ...` commands. The default value SHALL be `0` (turned off).

## Handling file conflicts during export

### RQ.ClickHouse.ExportPart.Settings.OverwriteFile
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_overwrite_file_if_exists` setting that controls whether to overwrite files if they already exist when exporting a merge tree part. The default value SHALL be `0` (turned off).

## Controlling export performance

### RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth
version: 1.0

[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.

### RQ.ClickHouse.ExportPart.ServerSettings.BackgroundMovePoolSize
version: 1.0

[ClickHouse] SHALL support the `background_move_pool_size` server setting to control the maximum number of threads that will be used for executing export operations in the background. The default value SHALL be `8`. This is a server-level setting configured in the server configuration file.

### RQ.ClickHouse.ExportPart.Metrics.Export
version: 1.0

[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing exports.

## Export operation security

### RQ.ClickHouse.ExportPart.Security
version: 1.0

[ClickHouse] SHALL enforce security requirements for export operations:
* **RBAC**: Users must have the following privileges:
  * **Source Table**: `SELECT` privilege on the source table to read data parts
  * **Destination Table**: `INSERT` privilege on the destination table to write exported data
  * **Database Access**: `SHOW` privilege on both source and destination databases
  * **System Tables**: `SELECT` privilege on `system.tables` to validate table existence
  * **Query Management**: `KILL QUERY` privilege to terminate export operations, allowing users to kill their own export queries and administrators to kill any export query
* **Data Encryption**: All data in transit to destination storage must be encrypted using TLS/SSL
* **Network Security**: Export operations must use secure connections to destination storage (HTTPS for S3, secure protocols for other storage)
* **Credential Management**: Export operations must use secure credential storage and avoid exposing credentials in logs


[ClickHouse]: https://clickhouse.com

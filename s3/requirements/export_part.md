# SRS-015 ClickHouse Export Part to S3
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Exporting Parts to S3](#exporting-parts-to-s3)
    * 2.1 [RQ.ClickHouse.ExportPart.S3](#rqclickhouseexportparts3)
* 3 [SQL command support](#sql-command-support)
    * 3.1 [RQ.ClickHouse.ExportPart.SQLCommand](#rqclickhouseexportpartsqlcommand)
* 4 [Supported source table engines](#supported-source-table-engines)
    * 4.1 [RQ.ClickHouse.ExportPart.SourceEngines](#rqclickhouseexportpartsourceengines)
* 5 [Supported destination table engines](#supported-destination-table-engines)
    * 5.1 [RQ.ClickHouse.ExportPart.DestinationEngines](#rqclickhouseexportpartdestinationengines)
* 6 [Destination setup and file management](#destination-setup-and-file-management)
    * 6.1 [RQ.ClickHouse.ExportPart.DestinationSetup](#rqclickhouseexportpartdestinationsetup)
* 7 [Export data preparation](#export-data-preparation)
    * 7.1 [RQ.ClickHouse.ExportPart.DataPreparation](#rqclickhouseexportpartdatapreparation)
* 8 [Schema compatibility](#schema-compatibility)
    * 8.1 [RQ.ClickHouse.ExportPart.SchemaCompatibility](#rqclickhouseexportpartschemacompatibility)
* 9 [Partition key types support](#partition-key-types-support)
    * 9.1 [RQ.ClickHouse.ExportPart.PartitionKeyTypes](#rqclickhouseexportpartpartitionkeytypes)
* 10 [Part types and content support](#part-types-and-content-support)
    * 10.1 [RQ.ClickHouse.ExportPart.PartTypes](#rqclickhouseexportpartparttypes)
* 11 [Export operation failure recovery](#export-operation-failure-recovery)
    * 11.1 [RQ.ClickHouse.ExportPart.FailureRecovery](#rqclickhouseexportpartfailurerecovery)
* 12 [Export operation restrictions](#export-operation-restrictions)
    * 12.1 [Preventing same table exports](#preventing-same-table-exports)
        * 12.1.1 [RQ.ClickHouse.ExportPart.Restrictions.SameTable](#rqclickhouseexportpartrestrictionssametable)
    * 12.2 [Destination table compatibility](#destination-table-compatibility)
        * 12.2.1 [RQ.ClickHouse.ExportPart.Restrictions.DestinationSupport](#rqclickhouseexportpartrestrictionsdestinationsupport)
    * 12.3 [Source part availability](#source-part-availability)
        * 12.3.1 [RQ.ClickHouse.ExportPart.Restrictions.SourcePart](#rqclickhouseexportpartrestrictionssourcepart)
* 13 [Export operation concurrency](#export-operation-concurrency)
    * 13.1 [RQ.ClickHouse.ExportPart.Concurrency](#rqclickhouseexportpartconcurrency)
* 14 [Export operation idempotency](#export-operation-idempotency)
    * 14.1 [RQ.ClickHouse.ExportPart.Idempotency](#rqclickhouseexportpartidempotency)
* 15 [Export operation error recovery](#export-operation-error-recovery)
    * 15.1 [Graceful failure handling](#graceful-failure-handling)
        * 15.1.1 [RQ.ClickHouse.ExportPart.ErrorRecovery.GracefulFailure](#rqclickhouseexportparterrorrecoverygracefulfailure)
    * 15.2 [Automatic cleanup on failure](#automatic-cleanup-on-failure)
        * 15.2.1 [RQ.ClickHouse.ExportPart.ErrorRecovery.AutomaticCleanup](#rqclickhouseexportparterrorrecoveryautomaticcleanup)
* 16 [Export operation logging](#export-operation-logging)
    * 16.1 [RQ.ClickHouse.ExportPart.Logging](#rqclickhouseexportpartlogging)
* 17 [Monitoring export operations](#monitoring-export-operations)
    * 17.1 [RQ.ClickHouse.ExportPart.SystemTables.Exports](#rqclickhouseexportpartsystemtablesexports)
* 18 [Enabling export functionality](#enabling-export-functionality)
    * 18.1 [RQ.ClickHouse.ExportPart.Settings.AllowExperimental](#rqclickhouseexportpartsettingsallowexperimental)
* 19 [Handling file conflicts during export](#handling-file-conflicts-during-export)
    * 19.1 [RQ.ClickHouse.ExportPart.Settings.OverwriteFile](#rqclickhouseexportpartsettingsoverwritefile)
* 20 [Export operation configuration](#export-operation-configuration)
    * 20.1 [RQ.ClickHouse.ExportPart.ParallelFormatting](#rqclickhouseexportpartparallelformatting)
* 21 [Controlling export performance](#controlling-export-performance)
    * 21.1 [RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth](#rqclickhouseexportpartserversettingsmaxbandwidth)
* 22 [Monitoring export performance metrics](#monitoring-export-performance-metrics)
    * 22.1 [RQ.ClickHouse.ExportPart.Events](#rqclickhouseexportpartevents)
    * 22.2 [RQ.ClickHouse.ExportPart.Metrics.Export](#rqclickhouseexportpartmetricsexport)

## Introduction

This software requirements specification covers requirements related to
exporting MergeTree engine data parts to S3 object storage.

## Exporting Parts to S3

### RQ.ClickHouse.ExportPart.S3
version: 1.0

[ClickHouse] SHALL support exporting data parts from MergeTree engine tables to S3 object storage.

## SQL command support

### RQ.ClickHouse.ExportPart.SQLCommand
version: 1.0

[ClickHouse] SHALL support the 

```sql
ALTER TABLE ... EXPORT PART ... TO TABLE ...
```

SQL command syntax for exporting MergeTree data parts to object storage tables.

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

## Supported destination table engines

### RQ.ClickHouse.ExportPart.DestinationEngines
version: 1.0

[ClickHouse] SHALL support exporting to destination tables that:
* Use Hive partitioning strategy (`partition_strategy = 'hive'`)
* Support object storage engines including:
  * `S3` - Amazon S3 and S3-compatible storage
  * `StorageObjectStorage` - Generic object storage interface
  * `HDFS` - Hadoop Distributed File System (with Hive partitioning)
  * `Azure` - Microsoft Azure Blob Storage (with Hive partitioning)
  * `GCS` - Google Cloud Storage (with Hive partitioning)
* Implement the `supportsImport()` method and return `true`

## Destination setup and file management

### RQ.ClickHouse.ExportPart.DestinationSetup
version: 1.0

[ClickHouse] SHALL handle destination setup and file management by:
* Creating appropriate import sinks for destination storage systems
* Generating unique file names in the format `{part_name}_{checksum_hex}` to avoid conflicts
* Allowing destination storage to determine the final file path based on Hive partitioning
* Creating files in the destination storage that users can observe and access
* Providing the final destination file path in the `system.exports` table for monitoring
* Ensuring file naming consistency and uniqueness across export operations

## Export data preparation

### RQ.ClickHouse.ExportPart.DataPreparation
version: 1.0

[ClickHouse] SHALL prepare data for export by:
* Automatically selecting all physical columns from source table metadata
* Extracting partition key values for proper Hive partitioning in destination
* Applying any pending schema changes to ensure data consistency
* Ensuring data integrity and schema compatibility throughout the export process

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
| **Date/DateTime Types** | ✅ Yes | `Date`, `DateTime`, `DateTime64` | All date/time types supported |
| **String Types** | ✅ Yes | `String`, `FixedString` | All string types supported |
| **Date Functions** | ✅ Yes | `toYYYYMM(date_col)`, `toMonday(date_col)`, `toYear(date_col)` | Result in supported types |
| **Mathematical Expressions** | ✅ Yes | `column1 + column2`, `column * 1000` | If result is supported type |
| **String Functions** | ✅ Yes | `substring(column, 1, 4)` | Result in String type |
| **Tuple Expressions** | ✅ Yes | `(toMonday(StartDate), EventType)` | If all elements are supported types |
| **No Partition Key** | ✅ Yes | Tables without `PARTITION BY` clause | Unpartitioned tables supported |
| **UUID Types** | ❌ No | `UUID` | Not supported by Hive partitioning |
| **Enum Types** | ❌ No | `Enum8`, `Enum16` | Not supported by Hive partitioning |
| **Floating-point Types** | ❌ No | `Float32`, `Float64` | Not supported by Hive partitioning |
| **Hash Functions** | ❌ No | `intHash32(column)`, `cityHash64(column)` | Result in unsupported types |

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
| **Regular Parts** | ✅ Yes | Standard data parts created by inserts, merges, mutations | Full data content |
| **Patch Parts** | ✅ Yes | Lightweight update parts containing only changed columns | Applied during export |
| **Active Parts** | ✅ Yes | Currently active data parts | Primary export target |
| **Outdated Parts** | ✅ Yes | Parts that have been replaced by newer versions | Can be exported for backup |

[ClickHouse] SHALL handle all special columns and metadata present in parts during export:

| Column Type | Supported | Description | Export Behavior |
|-------------|------------|-------------|-----------------|
| **Physical Columns** | ✅ Yes | User-defined table columns | All physical columns exported |
| **RowExistsColumn (_row_exists)** | ✅ Yes | Lightweight delete mask showing row existence | Exported to maintain delete state |
| **BlockNumberColumn (_block_number)** | ✅ Yes | Original block number from insert | Exported for row identification |
| **BlockOffsetColumn (_block_offset)** | ✅ Yes | Original row offset within block | Exported for row identification |
| **PartDataVersionColumn (_part_data_version)** | ✅ Yes | Data version for mutations | Exported for version tracking |
| **Virtual Columns** | ✅ Yes | Runtime columns like _part, _partition_id | Generated during export |
| **System Metadata** | ✅ Yes | Checksums, compression info, serialization | Preserved in export |

[ClickHouse] SHALL handle all mutation and schema change information present in parts:

| Mutation/Schema Type | Supported | Description | Export Behavior |
|---------------------|------------|-------------|-----------------|
| **Mutation Commands** | ✅ Yes | DELETE, UPDATE, MATERIALIZE_INDEX, DROP_COLUMN, RENAME_COLUMN | Applied during export |
| **Alter Conversions** | ✅ Yes | Column renames, type changes, schema modifications | Applied during export |
| **Patch Parts** | ✅ Yes | Lightweight updates with only changed columns | Applied during export |
| **Mutation Versions** | ✅ Yes | Version tracking for applied mutations | Preserved in export |
| **Schema Changes** | ✅ Yes | ALTER MODIFY, ALTER DROP, ALTER RENAME | Applied during export |
| **TTL Information** | ✅ Yes | Time-to-live settings and expiration data | Preserved in export |
| **Index Information** | ✅ Yes | Primary key, secondary indices, projections | Preserved in export |
| **Statistics** | ✅ Yes | Column statistics and sampling information | Preserved in export |

[ClickHouse] SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL handle all part metadata including checksums, compression information, serialization details, mutation history, schema changes, and structural modifications to maintain data integrity in the destination storage.

## Export operation failure recovery

### RQ.ClickHouse.ExportPart.FailureRecovery
version: 1.0

[ClickHouse] SHALL provide comprehensive failure recovery for export operations across all failure scenarios:

| Failure Type | Recovery Behavior | User Impact | Retry Capability |
|--------------|-------------------|-------------|------------------|
| **Source Part Failures** | ✅ Yes | Part not found, corrupted, or inaccessible | Export fails gracefully with clear error message |
| **Destination Storage Failures** | ✅ Yes | S3/object storage unavailable, network issues | Export fails with retry recommendation |
| **Server Resource Failures** | ✅ Yes | Out of memory, disk space, CPU limits | Export fails with resource error |
| **Server Restart Failures** | ✅ Yes | Graceful or abrupt server shutdown | Active exports are lost, can be retried |
| **Network Interruptions** | ✅ Yes | Connection timeouts, network errors | Export fails with retry capability |
| **Concurrent Operation Failures** | ✅ Yes | Part locked by other operations | Export fails with lock error |
| **Schema Change Failures** | ✅ Yes | Table structure changed during export | Export fails with schema mismatch error |

[ClickHouse] SHALL handle server restart scenarios by:
* **Graceful Shutdown**: All active export operations are properly terminated and cleaned up
* **Abrupt Shutdown**: Export manifests are preserved for recovery on restart
* **Restart Recovery**: Failed exports can be identified and retried after server restart
* **State Consistency**: No partial or corrupted exports remain after restart

[ClickHouse] SHALL handle resource constraint failures by:
* **Memory Exhaustion**: Export fails with clear memory error and retry recommendation
* **Disk Space**: Export fails when insufficient disk space for temporary files
* **CPU Limits**: Export respects server CPU limits and throttling
* **Network Bandwidth**: Export respects bandwidth limits and throttling

[ClickHouse] SHALL handle destination storage failures by:
* **S3/Object Storage Unavailable**: Export fails with storage error and retry recommendation
* **Network Timeouts**: Export fails with timeout error and retry capability
* **Authentication Failures**: Export fails with authentication error
* **Permission Denied**: Export fails with permission error

## Export operation restrictions

### Preventing same table exports

### RQ.ClickHouse.ExportPart.Restrictions.SameTable
version: 1.0

[ClickHouse] SHALL prevent exporting parts to the same table as the source by:
* Validating that source and destination table identifiers are different
* Throwing a `BAD_ARGUMENTS` exception with message "Exporting to the same table is not allowed" when source and destination are identical
* Performing this validation before any export processing begins

### Destination table compatibility

### RQ.ClickHouse.ExportPart.Restrictions.DestinationSupport
version: 1.0

[ClickHouse] SHALL validate destination table compatibility by:

* Checking that the destination storage supports importing MergeTree parts
* Verifying that the destination uses Hive partitioning strategy (`partition_strategy = 'hive'`)
* Throwing a `NOT_IMPLEMENTED` exception with message "Destination storage {} does not support MergeTree parts or uses unsupported partitioning" when requirements are not met
* Performing this validation during the initial export setup phase

### Source part availability

### RQ.ClickHouse.ExportPart.Restrictions.SourcePart
version: 1.0

[ClickHouse] SHALL validate source part availability by:

* Checking that the specified part exists in the source table
* Verifying the part is in an active state (not detached or missing)
* Throwing a `NO_SUCH_DATA_PART` exception with message "No such data part '{}' to export in table '{}'" when the part is not found
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

[ClickHouse] SHALL ensure export operations are idempotent by:

* Allowing the same part to be exported multiple times safely without data corruption
* Supporting file overwrite control through the `export_merge_tree_part_overwrite_file_if_exists` setting
* Generating unique file names using part name and checksum to avoid conflicts
* Maintaining export state consistency across retries

## Export operation error recovery

### Graceful failure handling

### RQ.ClickHouse.ExportPart.ErrorRecovery.GracefulFailure
version: 1.0

[ClickHouse] SHALL handle export failures gracefully by:
* Allowing users to retry failed export operations
* Maintaining system stability even when exports fail
* Not corrupting source data when export operations fail
* Continuing to process other export operations when one fails

### Automatic cleanup on failure

### RQ.ClickHouse.ExportPart.ErrorRecovery.AutomaticCleanup
version: 1.0

[ClickHouse] SHALL automatically clean up failed export operations by:
* Removing export manifests from the system when operations fail
* Cleaning up any partial data written to destination storage
* Releasing system resources (memory, file handles) used by failed exports
* Updating export status to reflect the failure state
* Allowing the system to recover and process other export operations

## Export operation logging

### RQ.ClickHouse.ExportPart.Logging
version: 1.0

[ClickHouse] SHALL provide detailed logging for export operations by:
* Logging all export operations (both successful and failed) with timestamps and details
* Recording the specific part name and destination for all operations
* Including execution time and progress information for all operations
* Writing operation information to the `system.part_log` table with the following columns:
  * `event_type` - Set to `EXPORT_PART` for export operations
  * `event_time` - Timestamp when the export operation occurred
  * `table` - Source table name
  * `part_name` - Name of the part being exported
  * `path_on_disk` - Path to the part in source storage
  * `duration_ms` - Execution time in milliseconds
  * `error` - Error message if the export failed (empty for successful exports)
  * `thread_id` - Thread ID performing the export
* Providing sufficient detail for monitoring and troubleshooting export operations

## Monitoring export operations

### RQ.ClickHouse.ExportPart.SystemTables.Exports
version: 1.0

[ClickHouse] SHALL provide a `system.exports` table that allows users to monitor active and completed export operations, track progress metrics, performance statistics, and troubleshoot export issues with the following columns:

* `source_database`, `source_table` - source table identifiers
* `destination_database`, `destination_table` - destination table identifiers  
* `create_time` - when export was submitted
* `part_name` - name of the exported part
* `destination_file_path` - path in destination storage
* `elapsed` - execution time in seconds
* `rows_read`, `total_rows_to_read` - progress metrics
* `total_size_bytes_compressed`, `total_size_bytes_uncompressed` - size metrics
* `bytes_read_uncompressed` - bytes processed
* `memory_usage`, `peak_memory_usage` - memory consumption

## Enabling export functionality

### RQ.ClickHouse.ExportPart.Settings.AllowExperimental
version: 1.0

[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export part functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PART ...` commands. The default value SHALL be `0` (turned off).

## Handling file conflicts during export

### RQ.ClickHouse.ExportPart.Settings.OverwriteFile
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_overwrite_file_if_exists` setting that controls whether to overwrite files if they already exist when exporting a merge tree part. The default value SHALL be `0` (turned off).

## Export operation configuration

### RQ.ClickHouse.ExportPart.ParallelFormatting
version: 1.0

[ClickHouse] SHALL support parallel formatting for export operations by:
* Automatically enabling parallel formatting for large export operations to improve performance
* Using the `output_format_parallel_formatting` setting to control parallel formatting behavior
* Optimizing data processing based on export size and system resources
* Providing consistent formatting performance across different export scenarios

## Controlling export performance

### RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth
version: 1.0

[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.

## Monitoring export performance metrics

### RQ.ClickHouse.ExportPart.Events
version: 1.0

[ClickHouse] SHALL provide the following export-related events in the `system.events` table:
* `PartsExports` - Number of successful part exports
* `PartsExportFailures` - Number of failed part exports  
* `PartsExportDuplicated` - Number of part exports that failed because target already exists
* `PartsExportTotalMilliseconds` - Total time spent on part export operations in milliseconds
* `ExportsThrottlerBytes` - Bytes passed through the exports throttler
* `ExportsThrottlerSleepMicroseconds` - Total time queries were sleeping to conform to export bandwidth throttling

### RQ.ClickHouse.ExportPart.Metrics.Export
version: 1.0

[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing exports.


[ClickHouse]: https://clickhouse.com
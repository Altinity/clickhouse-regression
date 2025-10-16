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
* 6 [Schema compatibility](#schema-compatibility)
    * 6.1 [RQ.ClickHouse.ExportPart.SchemaCompatibility](#rqclickhouseexportpartschemacompatibility)
* 7 [Export operation restrictions](#export-operation-restrictions)
    * 7.1 [Preventing same table exports](#preventing-same-table-exports)
        * 7.1.1 [RQ.ClickHouse.ExportPart.Restrictions.SameTable](#rqclickhouseexportpartrestrictionssametable)
    * 7.2 [Destination table compatibility](#destination-table-compatibility)
        * 7.2.1 [RQ.ClickHouse.ExportPart.Restrictions.DestinationSupport](#rqclickhouseexportpartrestrictionsdestinationsupport)
    * 7.3 [Source part availability](#source-part-availability)
        * 7.3.1 [RQ.ClickHouse.ExportPart.Restrictions.SourcePart](#rqclickhouseexportpartrestrictionssourcepart)
* 8 [Export operation concurrency](#export-operation-concurrency)
    * 8.1 [RQ.ClickHouse.ExportPart.Concurrency](#rqclickhouseexportpartconcurrency)
* 9 [Export operation idempotency](#export-operation-idempotency)
    * 9.1 [RQ.ClickHouse.ExportPart.Idempotency](#rqclickhouseexportpartidempotency)
* 10 [Export operation error recovery](#export-operation-error-recovery)
    * 10.1 [Graceful failure handling](#graceful-failure-handling)
        * 10.1.1 [RQ.ClickHouse.ExportPart.ErrorRecovery.GracefulFailure](#rqclickhouseexportparterrorrecoverygracefulfailure)
    * 10.2 [Automatic cleanup on failure](#automatic-cleanup-on-failure)
        * 10.2.1 [RQ.ClickHouse.ExportPart.ErrorRecovery.AutomaticCleanup](#rqclickhouseexportparterrorrecoveryautomaticcleanup)
* 11 [Export operation logging](#export-operation-logging)
    * 11.1 [RQ.ClickHouse.ExportPart.Logging](#rqclickhouseexportpartlogging)
* 12 [Monitoring export operations](#monitoring-export-operations)
    * 12.1 [RQ.ClickHouse.ExportPart.SystemTables.Exports](#rqclickhouseexportpartsystemtablesexports)
* 13 [Enabling export functionality](#enabling-export-functionality)
    * 13.1 [RQ.ClickHouse.ExportPart.Settings.AllowExperimental](#rqclickhouseexportpartsettingsallowexperimental)
* 14 [Handling file conflicts during export](#handling-file-conflicts-during-export)
    * 14.1 [RQ.ClickHouse.ExportPart.Settings.OverwriteFile](#rqclickhouseexportpartsettingsoverwritefile)
* 15 [Controlling export performance](#controlling-export-performance)
    * 15.1 [RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth](#rqclickhouseexportpartserversettingsmaxbandwidth)
* 16 [Monitoring export performance metrics](#monitoring-export-performance-metrics)
    * 16.1 [RQ.ClickHouse.ExportPart.Events](#rqclickhouseexportpartevents)
    * 16.2 [RQ.ClickHouse.ExportPart.Metrics.Export](#rqclickhouseexportpartmetricsexport)

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

## Schema compatibility

### RQ.ClickHouse.ExportPart.SchemaCompatibility
version: 1.0

[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:
* Identical physical column schemas between source and destination
* The same partition key expression in both tables
* Compatible data types for all columns
* Matching column order and names

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
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
    * 7.1 [RQ.ClickHouse.ExportPart.Restrictions](#rqclickhouseexportpartrestrictions)
* 8 [Monitoring export operations](#monitoring-export-operations)
    * 8.1 [RQ.ClickHouse.ExportPart.SystemTables.Exports](#rqclickhouseexportpartsystemtablesexports)
* 9 [Enabling export functionality](#enabling-export-functionality)
    * 9.1 [RQ.ClickHouse.ExportPart.Settings.AllowExperimental](#rqclickhouseexportpartsettingsallowexperimental)
* 10 [Handling file conflicts during export](#handling-file-conflicts-during-export)
    * 10.1 [RQ.ClickHouse.ExportPart.Settings.OverwriteFile](#rqclickhouseexportpartsettingsoverwritefile)
* 11 [Controlling export performance](#controlling-export-performance)
    * 11.1 [RQ.ClickHouse.ExportPart.ServerSettings.MaxBandwidth](#rqclickhouseexportpartserversettingsmaxbandwidth)
* 12 [Monitoring export performance metrics](#monitoring-export-performance-metrics)
    * 12.1 [RQ.ClickHouse.ExportPart.Events](#rqclickhouseexportpartevents)
    * 12.2 [RQ.ClickHouse.ExportPart.Metrics.Export](#rqclickhouseexportpartmetricsexport)

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

### RQ.ClickHouse.ExportPart.Restrictions
version: 1.0

[ClickHouse] SHALL enforce the following restrictions:
* Cannot export to the same table as the source
* Destination must support imports and use Hive partitioning
* Source part must exist and be accessible
* Export operation must be idempotent for the same part

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
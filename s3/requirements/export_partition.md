# SRS-016 ClickHouse Export Partition to S3
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Exporting Partitions to S3](#exporting-partitions-to-s3)
    * 2.1 [RQ.ClickHouse.ExportPartition.S3](#rqclickhouseexportpartitions3)
    * 2.2 [RQ.ClickHouse.ExportPartition.EmptyPartition](#rqclickhouseexportpartitionemptypartition)
* 3 [SQL command support](#sql-command-support)
    * 3.1 [RQ.ClickHouse.ExportPartition.SQLCommand](#rqclickhouseexportpartitionsqlcommand)
* 4 [Supported source table engines](#supported-source-table-engines)
    * 4.1 [RQ.ClickHouse.ExportPartition.SourceEngines](#rqclickhouseexportpartitionsourceengines)
* 5 [Cluster and node support](#cluster-and-node-support)
    * 5.1 [RQ.ClickHouse.ExportPartition.ClustersNodes](#rqclickhouseexportpartitionclustersnodes)
* 6 [Supported source part storage types](#supported-source-part-storage-types)
    * 6.1 [RQ.ClickHouse.ExportPartition.SourcePartStorage](#rqclickhouseexportpartitionsourcepartstorage)
* 7 [Storage policies and volumes](#storage-policies-and-volumes)
    * 7.1 [RQ.ClickHouse.ExportPartition.StoragePolicies](#rqclickhouseexportpartitionstoragepolicies)
* 8 [Supported destination table engines](#supported-destination-table-engines)
    * 8.1 [RQ.ClickHouse.ExportPartition.DestinationEngines](#rqclickhouseexportpartitiondestinationengines)
* 9 [Schema compatibility](#schema-compatibility)
    * 9.1 [RQ.ClickHouse.ExportPartition.SchemaCompatibility](#rqclickhouseexportpartitionschemacompatibility)
* 10 [Partition key types support](#partition-key-types-support)
    * 10.1 [RQ.ClickHouse.ExportPartition.PartitionKeyTypes](#rqclickhouseexportpartitionpartitionkeytypes)
* 11 [Partition content support](#partition-content-support)
    * 11.1 [RQ.ClickHouse.ExportPartition.PartitionContent](#rqclickhouseexportpartitionpartitioncontent)
    * 11.2 [RQ.ClickHouse.ExportPartition.SchemaChangeIsolation](#rqclickhouseexportpartitionschemachangeisolation)
    * 11.3 [RQ.ClickHouse.ExportPartition.LargePartitions](#rqclickhouseexportpartitionlargepartitions)
* 12 [Export operation failure handling](#export-operation-failure-handling)
    * 12.1 [RQ.ClickHouse.ExportPartition.RetryMechanism](#rqclickhouseexportpartitionretrymechanism)
    * 12.2 [RQ.ClickHouse.ExportPartition.Settings.MaxRetries](#rqclickhouseexportpartitionsettingsmaxretries)
    * 12.3 [RQ.ClickHouse.ExportPartition.ResumeAfterFailure](#rqclickhouseexportpartitionresumeafterfailure)
    * 12.4 [RQ.ClickHouse.ExportPartition.PartialProgress](#rqclickhouseexportpartitionpartialprogress)
    * 12.5 [RQ.ClickHouse.ExportPartition.Cleanup](#rqclickhouseexportpartitioncleanup)
    * 12.6 [RQ.ClickHouse.ExportPartition.Settings.ManifestTTL](#rqclickhouseexportpartitionsettingsmanifestttl)
* 13 [Network resilience](#network-resilience)
    * 13.1 [RQ.ClickHouse.ExportPartition.NetworkResilience.PacketIssues](#rqclickhouseexportpartitionnetworkresiliencepacketissues)
    * 13.2 [RQ.ClickHouse.ExportPartition.NetworkResilience.DestinationInterruption](#rqclickhouseexportpartitionnetworkresiliencedestinationinterruption)
    * 13.3 [RQ.ClickHouse.ExportPartition.NetworkResilience.NodeInterruption](#rqclickhouseexportpartitionnetworkresiliencenodeinterruption)
* 14 [Export operation restrictions](#export-operation-restrictions)
    * 14.1 [Preventing same table exports](#preventing-same-table-exports)
        * 14.1.1 [RQ.ClickHouse.ExportPartition.Restrictions.SameTable](#rqclickhouseexportpartitionrestrictionssametable)
    * 14.2 [Destination table compatibility](#destination-table-compatibility)
        * 14.2.1 [RQ.ClickHouse.ExportPartition.Restrictions.DestinationSupport](#rqclickhouseexportpartitionrestrictionsdestinationsupport)
    * 14.3 [Local table restriction](#local-table-restriction)
        * 14.3.1 [RQ.ClickHouse.ExportPartition.Restrictions.LocalTable](#rqclickhouseexportpartitionrestrictionslocaltable)
    * 14.4 [Partition key compatibility](#partition-key-compatibility)
        * 14.4.1 [RQ.ClickHouse.ExportPartition.Restrictions.PartitionKey](#rqclickhouseexportpartitionrestrictionspartitionkey)
    * 14.5 [Source partition availability](#source-partition-availability)
        * 14.5.1 [RQ.ClickHouse.ExportPartition.Restrictions.SourcePartition](#rqclickhouseexportpartitionrestrictionssourcepartition)
* 15 [Export operation concurrency](#export-operation-concurrency)
    * 15.1 [RQ.ClickHouse.ExportPartition.Concurrency](#rqclickhouseexportpartitionconcurrency)
* 16 [Export operation idempotency](#export-operation-idempotency)
    * 16.1 [RQ.ClickHouse.ExportPartition.Idempotency](#rqclickhouseexportpartitionidempotency)
    * 16.2 [RQ.ClickHouse.ExportPartition.Settings.ForceExport](#rqclickhouseexportpartitionsettingsforceexport)
* 17 [Export operation logging](#export-operation-logging)
    * 17.1 [RQ.ClickHouse.ExportPartition.Logging](#rqclickhouseexportpartitionlogging)
* 18 [Monitoring export operations](#monitoring-export-operations)
    * 18.1 [RQ.ClickHouse.ExportPartition.SystemTables.Exports](#rqclickhouseexportpartitionsystemtablesexports)
* 19 [Enabling export functionality](#enabling-export-functionality)
    * 19.1 [RQ.ClickHouse.ExportPartition.Settings.AllowExperimental](#rqclickhouseexportpartitionsettingsallowexperimental)
* 20 [Handling file conflicts during export](#handling-file-conflicts-during-export)
    * 20.1 [RQ.ClickHouse.ExportPartition.Settings.OverwriteFile](#rqclickhouseexportpartitionsettingsoverwritefile)
* 21 [Export operation configuration](#export-operation-configuration)
    * 21.1 [RQ.ClickHouse.ExportPartition.ParallelFormatting](#rqclickhouseexportpartitionparallelformatting)
* 22 [Controlling export performance](#controlling-export-performance)
    * 22.1 [RQ.ClickHouse.ExportPartition.ServerSettings.MaxBandwidth](#rqclickhouseexportpartitionserversettingsmaxbandwidth)
    * 22.2 [RQ.ClickHouse.ExportPartition.ServerSettings.BackgroundMovePoolSize](#rqclickhouseexportpartitionserversettingsbackgroundmovepoolsize)
    * 22.3 [RQ.ClickHouse.ExportPartition.Metrics.Export](#rqclickhouseexportpartitionmetricsexport)
* 23 [Export operation security](#export-operation-security)
    * 23.1 [RQ.ClickHouse.ExportPartition.Security.RBAC](#rqclickhouseexportpartitionsecurityrbac)
    * 23.2 [RQ.ClickHouse.ExportPartition.Security.DataEncryption](#rqclickhouseexportpartitionsecuritydataencryption)
    * 23.3 [RQ.ClickHouse.ExportPartition.Security.Network](#rqclickhouseexportpartitionsecuritynetwork)
    * 23.4 [RQ.ClickHouse.ExportPartition.Security.CredentialManagement](#rqclickhouseexportpartitionsecuritycredentialmanagement)

## Introduction

This specification defines requirements for exporting partitions (all parts within a partition) from ReplicatedMergeTree tables to S3-compatible object storage. This feature enables users to export entire partitions containing multiple data parts across cluster nodes.

## Exporting Partitions to S3

### RQ.ClickHouse.ExportPartition.S3
version: 1.0

[ClickHouse] SHALL support exporting partitions (all parts within a partition) from ReplicatedMergeTree engine tables to S3 object storage. The export operation SHALL export all parts that belong to the specified partition ID, ensuring complete partition data is transferred to the destination.

### RQ.ClickHouse.ExportPartition.EmptyPartition
version: 1.0

[ClickHouse] SHALL support exporting from empty partitions by:
* Completing export operations successfully when the specified partition contains no parts
* Resulting in an empty destination partition when exporting from an empty source partition
* Not creating any files in destination storage when there are no parts to export in the partition
* Handling empty partitions gracefully without errors

## SQL command support

### RQ.ClickHouse.ExportPartition.SQLCommand
version: 1.0

[ClickHouse] SHALL support the following SQL command syntax for exporting partitions from ReplicatedMergeTree tables to object storage tables:

```sql
ALTER TABLE [database.]source_table_name 
EXPORT PARTITION ID 'partition_id' 
TO TABLE [database.]destination_table_name
SETTINGS allow_experimental_export_merge_tree_part = 1
```

**Parameters:**
- `source_table_name`: Name of the source ReplicatedMergeTree table
- `partition_id`: The partition ID to export (string literal), which identifies all parts belonging to that partition
- `destination_table_name`: Name of the destination object storage table
- `allow_experimental_export_merge_tree_part`: Setting that must be set to `1` to enable this experimental feature

This command allows users to export entire partitions in a single operation, which is more efficient than exporting individual parts and ensures all data for a partition is exported together.

## Supported source table engines

### RQ.ClickHouse.ExportPartition.SourceEngines
version: 1.0

[ClickHouse] SHALL support exporting partitions from the following source table engines:
* `ReplicatedMergeTree` - Replicated MergeTree engine (primary use case)
* `ReplicatedSummingMergeTree` - Replicated MergeTree with automatic summation
* `ReplicatedAggregatingMergeTree` - Replicated MergeTree with pre-aggregated data
* `ReplicatedCollapsingMergeTree` - Replicated MergeTree with row versioning
* `ReplicatedVersionedCollapsingMergeTree` - Replicated CollapsingMergeTree with version tracking
* `ReplicatedGraphiteMergeTree` - Replicated MergeTree optimized for Graphite data
* All other ReplicatedMergeTree family engines

Export partition functionality manages export operations across multiple replicas in a cluster, ensuring that parts are exported correctly and avoiding conflicts.

## Cluster and node support

### RQ.ClickHouse.ExportPartition.ClustersNodes
version: 1.0

[ClickHouse] SHALL support exporting partitions from multiple nodes in a ReplicatedMergeTree cluster to the same destination storage, ensuring that:
* Each replica in the cluster can independently export parts from the partition that it owns locally
* All parts within a partition are exported exactly once, even when distributed across multiple replicas
* Exported data from different replicas is correctly aggregated in the destination storage
* All nodes in the cluster can read the same exported partition data from the destination
* Export operations continue to make progress even if some replicas are temporarily unavailable

In a replicated cluster, different parts of the same partition may exist on different replicas. The system must coordinate exports across all replicas to ensure complete partition export without duplication.

## Supported source part storage types

### RQ.ClickHouse.ExportPartition.SourcePartStorage
version: 1.0

[ClickHouse] SHALL support exporting partitions regardless of the underlying storage type where the source parts are stored, including:
* **Local Disks**: Parts stored on local filesystem
* **S3/Object Storage**: Parts stored on S3 or S3-compatible object storage
* **Encrypted Disks**: Parts stored on encrypted disks (disk-level encryption)
* **Cached Disks**: Parts stored with filesystem cache enabled
* **Remote Disks**: Parts stored on HDFS, Azure Blob Storage, or Google Cloud Storage
* **Tiered Storage**: Parts stored across multiple storage tiers (hot/cold)
* **Zero-Copy Replication Disks**: Parts stored with zero-copy replication enabled

Users should be able to export partitions regardless of where the source data is physically stored, providing flexibility in storage configurations.

## Storage policies and volumes

### RQ.ClickHouse.ExportPartition.StoragePolicies
version: 1.0

[ClickHouse] SHALL support exporting partitions from tables using different storage policies, where storage policies are composed of volumes which are composed of disks, including:
* **JBOD Volumes**: Just a Bunch Of Disks volumes with multiple disks
* **External Volumes**: Volumes using external storage systems
* **Tiered Storage Policies**: Storage policies with multiple volumes for hot/cold data tiers
* **Custom Storage Policies**: Any storage policy configuration composed of volumes and disks
* Exporting all parts in a partition regardless of which volume or disk within the storage policy contains each part
* Maintaining data integrity when exporting from parts stored on any volume or disk in the storage policy

Users may have partitions with parts distributed across different storage tiers or volumes, and the export should handle all parts regardless of their storage location.

## Supported destination table engines

### RQ.ClickHouse.ExportPartition.DestinationEngines
version: 1.0

[ClickHouse] SHALL support exporting to destination tables that:
* Support object storage engines including:
  * `S3` - Amazon S3 and S3-compatible storage
  * `StorageObjectStorage` - Generic object storage interface
  * `HDFS` - Hadoop Distributed File System (with Hive partitioning)
  * `Azure` - Microsoft Azure Blob Storage (with Hive partitioning)
  * `GCS` - Google Cloud Storage (with Hive partitioning)

Export partition is designed to move data from local or replicated storage to object storage systems for long-term storage, analytics, or data sharing purposes.

## Schema compatibility

### RQ.ClickHouse.ExportPartition.SchemaCompatibility
version: 1.0

[ClickHouse] SHALL require source and destination tables to have compatible schemas for successful export operations:
* Identical physical column schemas between source and destination
* The same partition key expression in both tables
* Compatible data types for all columns
* Matching column order and names

Schema compatibility ensures that exported data can be correctly read from the destination table without data loss or corruption.

## Partition key types support

### RQ.ClickHouse.ExportPartition.PartitionKeyTypes
version: 1.0

[ClickHouse] SHALL support export operations for tables with partition key types that are compatible with Hive partitioning, as shown in the following table:

| Partition Key Type      | Supported | Examples                                                                 | Notes                          |
|-------------------------|-----------|--------------------------------------------------------------------------|--------------------------------|
| **Integer Types**       | ✅ Yes     | `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64` | All integer types supported    |
| **Date/DateTime Types** | ✅ Yes     | `Date`, `Date32`, `DateTime`, `DateTime64`                               | All date/time types supported  |
| **String Types**        | ✅ Yes     | `String`, `FixedString`                                                  | All string types supported     |
| **No Partition Key**    | ✅ Yes     | Tables without `PARTITION BY` clause                                     | Unpartitioned tables supported |

[ClickHouse] SHALL automatically extract partition values from source parts and use them to create proper Hive partitioning structure in destination storage, but only for partition key types that are compatible with Hive partitioning requirements.

[ClickHouse] SHALL require destination tables to support Hive partitioning, which limits the supported partition key types to Integer, Date/DateTime, and String types. Complex expressions that result in unsupported types are not supported for export operations.

Hive partitioning is a standard way to organize data in object storage systems, making exported data compatible with various analytics tools and systems.

## Partition content support

### RQ.ClickHouse.ExportPartition.PartitionContent
version: 1.0

[ClickHouse] SHALL support export operations for partitions containing all valid MergeTree part types and their contents, including:

| Part Type         | Supported | Description                                                  | Special Features               |
|-------------------|-----------|--------------------------------------------------------------|--------------------------------|
| **Wide Parts**    | ✅ Yes     | Data of each column stored in separate files with marks      | Standard format for most parts |
| **Compact Parts** | ✅ Yes     | All column data stored in single file with single marks file | Optimized for small parts      |

[ClickHouse] SHALL export all parts within the specified partition, regardless of their type. The system SHALL automatically apply lightweight delete masks during export to ensure only non-deleted rows are exported, and SHALL maintain data integrity in the destination storage.

Partitions may contain a mix of different part types, and the export must handle all of them correctly to ensure complete partition export.

### RQ.ClickHouse.ExportPartition.SchemaChangeIsolation
version: 1.0

[ClickHouse] SHALL ensure exported partition data is isolated from subsequent schema changes by:
* Preserving exported data exactly as it was at the time of export
* Not being affected by schema changes (column drops, renames, type changes) that occur after export
* Maintaining data integrity in destination storage regardless of mutations applied to the source table after export
* Ensuring exported data reflects the source table state at the time of export, not the current state

Once a partition is exported, the exported data should remain stable and not be affected by future changes to the source table schema.

### RQ.ClickHouse.ExportPartition.LargePartitions
version: 1.0

[ClickHouse] SHALL support exporting large partitions by:
* Handling partitions with large numbers of parts (e.g., hundreds or thousands of parts)
* Processing partitions with large numbers of rows (e.g., billions of rows)
* Processing large data volumes efficiently during export
* Maintaining data integrity when exporting large partitions
* Completing export operations successfully regardless of partition size
* Allowing export operations to continue over extended periods of time for very large partitions

Production systems often have partitions containing very large amounts of data, and the export must handle these efficiently without timeouts or memory issues.

## Export operation failure handling

### RQ.ClickHouse.ExportPartition.RetryMechanism
version: 1.0

[ClickHouse] SHALL automatically retry failed part exports within a partition up to a configurable maximum retry count. If all retry attempts are exhausted for a part, the entire partition export operation SHALL be marked as failed.

Unlike single-part exports, partition exports involve multiple parts and may take significant time. Retry mechanisms ensure that temporary failures don't require restarting the entire export operation.

### RQ.ClickHouse.ExportPartition.Settings.MaxRetries
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_partition_max_retries` setting that controls the maximum number of retries for exporting a merge tree part in an export partition task. The default value SHALL be `3`.

This setting allows users to control how many times the system will retry exporting a part before marking it as failed.

### RQ.ClickHouse.ExportPartition.ResumeAfterFailure
version: 1.0

[ClickHouse] SHALL allow export operations to resume after node failures or restarts. The system SHALL track which parts have been successfully exported and SHALL not re-export parts that were already successfully exported.

### RQ.ClickHouse.ExportPartition.PartialProgress
version: 1.0

[ClickHouse] SHALL allow export operations to make partial progress, with successfully exported parts remaining in the destination even if other parts fail. Users SHALL be able to see which parts have been successfully exported and which parts have failed.

### RQ.ClickHouse.ExportPartition.Cleanup
version: 1.0

[ClickHouse] SHALL automatically clean up failed or completed export operations after a configurable TTL period.

### RQ.ClickHouse.ExportPartition.Settings.ManifestTTL
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_partition_manifest_ttl` setting that determines how long the export manifest will be retained. This setting prevents the same partition from being exported twice to the same destination within the TTL period. The default value SHALL be `180` seconds.

This setting only affects completed export operations and does not delete in-progress tasks. It allows users to control how long export history is maintained to prevent duplicate exports.

## Network resilience

### RQ.ClickHouse.ExportPartition.NetworkResilience.PacketIssues
version: 1.0

[ClickHouse] SHALL handle network packet issues during export operations by:
* Tolerating packet delay without data corruption or loss
* Handling packet loss and retransmitting data as needed
* Detecting and handling packet corruption to ensure data integrity
* Managing packet duplication without data duplication in destination
* Handling packet reordering to maintain correct data sequence
* Operating correctly under packet rate limiting constraints
* Completing exports successfully despite network impairments

Network issues are common in distributed systems, and export operations must be resilient to ensure data integrity.

### RQ.ClickHouse.ExportPartition.NetworkResilience.DestinationInterruption
version: 1.0

[ClickHouse] SHALL handle destination storage interruptions during export operations by:
* Detecting when destination storage becomes unavailable during export
* Retrying failed part exports when destination storage becomes available again
* Logging failed exports in the `system.events` table with appropriate counters
* Not leaving partial or corrupted data in destination storage when exports fail due to destination unavailability
* Allowing exports to complete successfully once destination storage becomes available again
* Resuming export operations from the last successfully exported part

Destination storage systems may experience temporary outages, and the export should automatically recover when service is restored.

### RQ.ClickHouse.ExportPartition.NetworkResilience.NodeInterruption
version: 1.0

[ClickHouse] SHALL handle ClickHouse node interruptions during export operations by:
* Allowing export operations to resume after node restart without data loss or duplication
* Allowing other replicas to continue or complete export operations if a node fails
* Not leaving partial or corrupted data in destination storage when node restarts occur
* With safe shutdown, ensuring exports complete successfully before node shutdown when possible
* With unsafe shutdown, allowing export operations to resume from the last checkpoint after node restart
* Maintaining data integrity in destination storage regardless of node interruption type
* Ensuring that parts already exported are not re-exported after node restart

Node failures are common in distributed systems, and export operations must be able to recover and continue without data loss or duplication.

## Export operation restrictions

### Preventing same table exports

#### RQ.ClickHouse.ExportPartition.Restrictions.SameTable
version: 1.0

[ClickHouse] SHALL prevent exporting partitions to the same table as the source by:
* Validating that source and destination table identifiers are different
* Throwing a `BAD_ARGUMENTS` exception with message "Exporting to the same table is not allowed" when source and destination are identical
* Performing this validation before any export processing begins

Exporting to the same table would be redundant and could cause data duplication or conflicts.

### Destination table compatibility

#### RQ.ClickHouse.ExportPartition.Restrictions.DestinationSupport
version: 1.0

[ClickHouse] SHALL validate destination table compatibility by:

* Checking that the destination storage supports importing MergeTree parts
* Verifying that the destination uses Hive partitioning strategy (`partition_strategy = 'hive'`)
* Throwing a `NOT_IMPLEMENTED` exception with message "Destination storage {} does not support MergeTree parts or uses unsupported partitioning" when requirements are not met
* Performing this validation during the initial export setup phase

The destination must support the format and partitioning strategy required for exported data.

### Local table restriction

#### RQ.ClickHouse.ExportPartition.Restrictions.LocalTable
version: 1.0

[ClickHouse] SHALL prevent exporting partitions to local MergeTree tables by:
* Rejecting export operations where the destination table uses a MergeTree engine
* Throwing a `NOT_IMPLEMENTED` exception (error code 48) with message "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning" when attempting to export to a local table
* Performing this validation during the initial export setup phase

Export partition is designed to move data to object storage, not to local MergeTree tables.

### Partition key compatibility

#### RQ.ClickHouse.ExportPartition.Restrictions.PartitionKey
version: 1.0

[ClickHouse] SHALL validate that source and destination tables have the same partition key expression by:
* Checking that the partition key expression matches between source and destination tables
* Throwing a `BAD_ARGUMENTS` exception (error code 36) with message "Tables have different partition key" when partition keys differ
* Performing this validation during the initial export setup phase

Matching partition keys ensure that exported data is organized correctly in the destination storage.

### Source partition availability

#### RQ.ClickHouse.ExportPartition.Restrictions.SourcePartition
version: 1.0

[ClickHouse] SHALL validate source partition availability by:
* Checking that the specified partition ID exists in the source table
* Verifying that the partition contains at least one active part (not detached or missing)
* Throwing an exception with an appropriate error message when the partition is not found or is empty
* Performing this validation before any export processing begins

The system must verify that the partition exists and contains data before attempting to export it.

## Export operation concurrency

### RQ.ClickHouse.ExportPartition.Concurrency
version: 1.0

[ClickHouse] SHALL support concurrent export operations by:
* Allowing multiple partition exports to run simultaneously without interference
* Supporting concurrent exports of different partitions to different destinations
* Preventing concurrent exports of the same partition to the same destination
* Allowing different replicas to export different parts of the same partition concurrently
* Maintaining separate progress tracking for each concurrent operation

Multiple users may want to export different partitions simultaneously, and the system must coordinate these operations to prevent conflicts while maximizing parallelism.

## Export operation idempotency

### RQ.ClickHouse.ExportPartition.Idempotency
version: 1.0

[ClickHouse] SHALL handle duplicate export operations by:
* Preventing duplicate data from being exported when the same partition is exported multiple times to the same destination
* Detecting when a partition export is already in progress or completed
* Detecting when an export operation attempts to export a partition that already exists in the destination
* Logging duplicate export attempts in the `system.events` table with appropriate counters
* Ensuring that destination data matches source data without duplication when the same partition is exported multiple times
* Allowing users to force re-export of a partition if needed (e.g., after TTL expiration or manual cleanup)

Users may accidentally trigger the same export multiple times, and the system should prevent duplicate data while allowing legitimate re-exports when needed.

### RQ.ClickHouse.ExportPartition.Settings.ForceExport
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_partition_force_export` setting that allows users to ignore existing partition export entries and force a new export operation. The default value SHALL be `false` (turned off).

When set to `true`, this setting allows users to overwrite existing export entries and force re-export of a partition, even if a previous export operation exists for the same partition and destination.

## Export operation logging

### RQ.ClickHouse.ExportPartition.Logging
version: 1.0

[ClickHouse] SHALL provide detailed logging for export operations by:
* Logging all export operations (both successful and failed) with timestamps and details
* Recording the specific partition ID in the `system.part_log` table for all operations
* Logging export events in the `system.events` table, including:
  * `PartsExports` - Number of successful part exports (within partitions)
  * `PartsExportFailures` - Number of failed part exports
  * `PartsExportDuplicated` - Number of part exports that failed because target already exists
* Writing operation information to the `system.part_log` table with `event_type` set to `EXPORT_PARTITION`
* Providing sufficient detail for monitoring and troubleshooting export operations
* Logging per-part export status within partition exports

Detailed logging helps users monitor export progress, troubleshoot issues, and audit export operations.

## Monitoring export operations

### RQ.ClickHouse.ExportPartition.SystemTables.Exports
version: 1.0

[ClickHouse] SHALL provide a `system.replicated_partition_exports` table that allows users to monitor active partition export operations with at least the following columns:
* `source_table` - source table identifier
* `destination_table` - destination table identifier
* `partition_id` - the partition ID being exported
* `status` - current status of the export operation (e.g., PENDING, IN_PROGRESS, COMPLETED, FAILED)
* `parts_total` - total number of parts in the partition
* `parts_processed` - number of parts successfully exported
* `parts_failed` - number of parts that failed to export
* `create_time` - when the export operation was created
* `update_time` - last update time of the export operation

The table SHALL track export operations before they complete and SHALL show completed or failed exports until they are cleaned up (based on TTL).

Users need visibility into export operations to monitor progress, identify issues, and understand export status across the cluster.

## Enabling export functionality

### RQ.ClickHouse.ExportPartition.Settings.AllowExperimental
version: 1.0

[ClickHouse] SHALL support the `allow_experimental_export_merge_tree_part` setting that SHALL gate the experimental export partition functionality, which SHALL be set to `1` to enable `ALTER TABLE ... EXPORT PARTITION ID ...` commands. The default value SHALL be `0` (turned off).

This setting allows administrators to control access to experimental functionality and ensures users are aware they are using a feature that may change.

## Handling file conflicts during export

### RQ.ClickHouse.ExportPartition.Settings.OverwriteFile
version: 1.0

[ClickHouse] SHALL support the `export_merge_tree_part_overwrite_file_if_exists` setting that controls whether to overwrite files if they already exist when exporting a partition. The default value SHALL be `0` (turned off), meaning exports will fail if files already exist in the destination.

This setting allows users to control whether to overwrite existing data in the destination, providing safety by default while allowing overwrites when needed.

## Export operation configuration

### RQ.ClickHouse.ExportPartition.ParallelFormatting
version: 1.0

[ClickHouse] SHALL support parallel formatting for export operations by:
* Automatically enabling parallel formatting for large export operations to improve performance
* Using the `output_format_parallel_formatting` setting to control parallel formatting behavior
* Optimizing data processing based on export size and system resources
* Providing consistent formatting performance across different export scenarios
* Allowing parallel processing of multiple parts within a partition when possible

Parallel formatting improves export performance, especially for large partitions with many parts.

## Controlling export performance

### RQ.ClickHouse.ExportPartition.ServerSettings.MaxBandwidth
version: 1.0

[ClickHouse] SHALL support the `max_exports_bandwidth_for_server` server setting to limit the maximum read speed of all exports on the server in bytes per second, with `0` meaning unlimited bandwidth. The default value SHALL be `0`. This is a server-level setting configured in the server configuration file.

Administrators need to control export bandwidth to avoid impacting other operations on the server.

### RQ.ClickHouse.ExportPartition.ServerSettings.BackgroundMovePoolSize
version: 1.0

[ClickHouse] SHALL support the `background_move_pool_size` server setting to control the maximum number of threads that will be used for executing export operations in the background. The default value SHALL be `8`. This is a server-level setting configured in the server configuration file.

This setting allows administrators to balance export performance with other system operations.

### RQ.ClickHouse.ExportPartition.Metrics.Export
version: 1.0

[ClickHouse] SHALL provide the `Export` current metric in `system.metrics` table that tracks the number of currently executing partition exports.

This metric helps monitor system load from export operations.

## Export operation security

### RQ.ClickHouse.ExportPartition.Security.RBAC
version: 1.0

[ClickHouse] SHALL enforce role-based access control (RBAC) for export operations. Users must have the following privileges to perform export operations:
* **Source Table**: `SELECT` privilege on the source table to read data parts
* **Destination Table**: `INSERT` privilege on the destination table to write exported data
* **Database Access**: `SHOW` privilege on both source and destination databases
* **System Tables**: `SELECT` privilege on `system.tables` and `system.replicated_partition_exports` to validate table existence and monitor exports

Export operations move potentially sensitive data, and proper access controls ensure only authorized users can export partitions.

### RQ.ClickHouse.ExportPartition.Security.DataEncryption
version: 1.0

[ClickHouse] SHALL encrypt all data in transit to destination storage using TLS/SSL during export operations.

Data encryption protects sensitive information from being intercepted or accessed during transmission to destination storage.

### RQ.ClickHouse.ExportPartition.Security.Network
version: 1.0

[ClickHouse] SHALL use secure connections to destination storage during export operations. For S3-compatible storage, connections must use HTTPS. For other storage types, secure protocols appropriate to the storage system must be used.

Secure network connections prevent unauthorized access and ensure data integrity during export operations.

### RQ.ClickHouse.ExportPartition.Security.CredentialManagement
version: 1.0

[ClickHouse] SHALL use secure credential storage for export operations and SHALL avoid exposing credentials in logs or error messages.

Proper credential management prevents unauthorized access to destination storage systems and protects sensitive authentication information.


[ClickHouse]: https://clickhouse.com


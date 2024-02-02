# SRS-038 ClickHouse Disk Object Storage VFS
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
  * 4.1 [Replicas](#replicas)
    * 4.1.1 [RQ.SRS-038.DiskObjectStorageVFS.Replica.NoDataDuplication](#rqsrs-038diskobjectstoragevfsreplicanodataduplication)
    * 4.1.2 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Add](#rqsrs-038diskobjectstoragevfsreplicaadd)
    * 4.1.3 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Remove](#rqsrs-038diskobjectstoragevfsreplicaremove)
    * 4.1.4 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Offline](#rqsrs-038diskobjectstoragevfsreplicaoffline)
    * 4.1.5 [RQ.SRS-038.DiskObjectStorageVFS.Replica.Stale](#rqsrs-038diskobjectstoragevfsreplicastale)
  * 4.2 [Settings](#settings)
    * 4.2.1 [RQ.SRS-038.DiskObjectStorageVFS.Settings.Disk](#rqsrs-038diskobjectstoragevfssettingsdisk)
    * 4.2.2 [RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible](#rqsrs-038diskobjectstoragevfssettingszerocopyincompatible)
    * 4.2.3 [RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared](#rqsrs-038diskobjectstoragevfssettingsshared)
    * 4.2.4 [RQ.SRS-038.DiskObjectStorageVFS.Settings.Reload](#rqsrs-038diskobjectstoragevfssettingsreload)
    * 4.2.5 [RQ.SRS-038.DiskObjectStorageVFS.Settings.VFSToggled](#rqsrs-038diskobjectstoragevfssettingsvfstoggled)
  * 4.3 [System](#system)
    * 4.3.1 [RQ.SRS-038.DiskObjectStorageVFS.System.Delete](#rqsrs-038diskobjectstoragevfssystemdelete)
    * 4.3.2 [RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption](#rqsrs-038diskobjectstoragevfssystemconnectioninterruption)
    * 4.3.3 [RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption.FaultInjection](#rqsrs-038diskobjectstoragevfssystemconnectioninterruptionfaultinjection)
    * 4.3.4 [RQ.SRS-038.DiskObjectStorageVFS.System.AddKeeper](#rqsrs-038diskobjectstoragevfssystemaddkeeper)
    * 4.3.5 [RQ.SRS-038.DiskObjectStorageVFS.System.RemoveKeeper](#rqsrs-038diskobjectstoragevfssystemremovekeeper)
    * 4.3.6 [RQ.SRS-038.DiskObjectStorageVFS.System.CompactWideParts](#rqsrs-038diskobjectstoragevfssystemcompactwideparts)
    * 4.3.7 [RQ.SRS-038.DiskObjectStorageVFS.System.Optimize](#rqsrs-038diskobjectstoragevfssystemoptimize)
    * 4.3.8 [RQ.SRS-038.DiskObjectStorageVFS.System.Transactions](#rqsrs-038diskobjectstoragevfssystemtransactions)
  * 4.4 [Alter](#alter)
    * 4.4.1 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Fetch](#rqsrs-038diskobjectstoragevfsalterfetch)
    * 4.4.2 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Detach](#rqsrs-038diskobjectstoragevfsalterdetach)
    * 4.4.3 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Drop](#rqsrs-038diskobjectstoragevfsalterdrop)
    * 4.4.4 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Attach](#rqsrs-038diskobjectstoragevfsalterattach)
    * 4.4.5 [RQ.SRS-038.DiskObjectStorageVFS.Alter.AttachFrom](#rqsrs-038diskobjectstoragevfsalterattachfrom)
    * 4.4.6 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Replace](#rqsrs-038diskobjectstoragevfsalterreplace)
    * 4.4.7 [RQ.SRS-038.DiskObjectStorageVFS.Alter.MoveToTable](#rqsrs-038diskobjectstoragevfsaltermovetotable)
    * 4.4.8 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Freeze](#rqsrs-038diskobjectstoragevfsalterfreeze)
    * 4.4.9 [RQ.SRS-038.DiskObjectStorageVFS.Alter.MovePart](#rqsrs-038diskobjectstoragevfsaltermovepart)
    * 4.4.10 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Index](#rqsrs-038diskobjectstoragevfsalterindex)
    * 4.4.11 [RQ.SRS-038.DiskObjectStorageVFS.Alter.OrderBy](#rqsrs-038diskobjectstoragevfsalterorderby)
    * 4.4.12 [RQ.SRS-038.DiskObjectStorageVFS.Alter.SampleBy](#rqsrs-038diskobjectstoragevfsaltersampleby)
    * 4.4.13 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Projections](#rqsrs-038diskobjectstoragevfsalterprojections)
    * 4.4.14 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Column](#rqsrs-038diskobjectstoragevfsaltercolumn)
    * 4.4.15 [RQ.SRS-038.DiskObjectStorageVFS.Alter.Update](#rqsrs-038diskobjectstoragevfsalterupdate)
  * 4.5 [Table](#table)
    * 4.5.1 [RQ.SRS-038.DiskObjectStorageVFS.Table.TableOperations](#rqsrs-038diskobjectstoragevfstabletableoperations)
    * 4.5.2 [RQ.SRS-038.DiskObjectStorageVFS.Table.BackgroundCollapse](#rqsrs-038diskobjectstoragevfstablebackgroundcollapse)
    * 4.5.3 [RQ.SRS-038.DiskObjectStorageVFS.Table.Migration](#rqsrs-038diskobjectstoragevfstablemigration)
    * 4.5.4 [RQ.SRS-038.DiskObjectStorageVFS.Table.TTLMove](#rqsrs-038diskobjectstoragevfstablettlmove)
    * 4.5.5 [RQ.SRS-038.DiskObjectStorageVFS.Table.TTLDelete](#rqsrs-038diskobjectstoragevfstablettldelete)
    * 4.5.6 [RQ.SRS-038.DiskObjectStorageVFS.Table.Detach](#rqsrs-038diskobjectstoragevfstabledetach)
    * 4.5.7 [RQ.SRS-038.DiskObjectStorageVFS.Table.StoragePolicy](#rqsrs-038diskobjectstoragevfstablestoragepolicy)
  * 4.6 [Combinatoric](#combinatoric)
    * 4.6.1 [Supported Table Configurations](#supported-table-configurations)
    * 4.6.2 [Supported Operations](#supported-operations)
    * 4.6.3 [RQ.SRS-038.DiskObjectStorageVFS.Combinatoric](#rqsrs-038diskobjectstoragevfscombinatoric)
    * 4.6.4 [RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert](#rqsrs-038diskobjectstoragevfscombinatoricinsert)
  * 4.7 [Performance](#performance)
    * 4.7.1 [RQ.SRS-038.DiskObjectStorageVFS.Performance](#rqsrs-038diskobjectstoragevfsperformance)
  * 4.8 [Object Storage Providers](#object-storage-providers)
    * 4.8.1 [RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration](#rqsrs-038diskobjectstoragevfsprovidersconfiguration)
    * 4.8.2 [RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS](#rqsrs-038diskobjectstoragevfsprovidersaws)
    * 4.8.3 [RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO](#rqsrs-038diskobjectstoragevfsprovidersminio)
    * 4.8.4 [RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS](#rqsrs-038diskobjectstoragevfsprovidersgcs)
* 5 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control
management software hosted in a [GitHub Repository]. All the updates are tracked
using the [Revision History].

## Introduction

[ClickHouse] supports using a virtual file system on AWS [S3] and S3-compatible object storage.

The virtual file system allows replicas to store table data and metadata on a single shared filesystem.

This is only available in versions 23.12 and later.

## Terminology

* **Replicated Table** - A table whose metadata and data exists in multiple locations
* **Zero Copy Replication** - A replication mode where each server keeps a copy of the metadata, but shares the data on external storage
* **0-copy** - Shorthand for Zero Copy Replication
* **VFS** - Virtual File System
* **S3** - Object Storage provided by [AWS]. Also used to refer to any S3-compatible object storage.
* **DiskObjectStorageVFS** - The specific VFS implementation used by [ClickHouse] for object storage

## Requirements

[ClickHouse] SHALL use DiskObjectStorageVFS when the `allow_vfs`
parameter is set to 1. This is only available in versions 23.12 and later.

### Replicas

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.NoDataDuplication
version: 1.0

[ClickHouse] SHALL support VFS such that data is not
duplicated in [S3] storage during any operations on replicated tables (ALTER,
SELECT, INSERT, etc...).

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Add
version: 1.0

[ClickHouse] SHALL support adding a replica of an existing replicated table
with no changes to data in any tables on the other replicating instances.

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Remove
version: 1.0

[ClickHouse] SHALL support removing a replicated table on a [ClickHouse] instance
with no changes to data in any tables on the other replicating instances.

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Offline
version: 1.0

[ClickHouse] SHALL support stopping and starting an instance of [ClickHouse]
with no changes to data in replicated tables. If the table is altered while
an instance is offline, [ClickHouse] SHALL update the table from [S3] when
that instance restarts.

#### RQ.SRS-038.DiskObjectStorageVFS.Replica.Stale
version: 0.0

stale replica

### Settings

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Disk
version: 1.0

[ClickHouse] SHALL support the `<allow_vfs>` setting in the
`<disks>` section of the config.xml file or an xml file in
the config.d directory to configure the vfs for a disk.

Example:

```xml
<yandex>
  <storage_configuration>
    <disks>
      <external>
        <allow_vfs>1</allow_vfs>
      </external>
  </storage_configuration>
</yandex>
```

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.ZeroCopyIncompatible
version: 1.0

[ClickHouse] SHALL return an error if both `<allow_s3_zero_copy_replication>`
and `<allow_vfs>` are enabled at the same time.

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Shared
version: 0.0

[ClickHouse] SHALL respect the following settings when`<allow_vfs>` is enabled.

| Setting                                                        | Component             | Support |
| -------------------------------------------------------------- | --------------------- | ------- |
| remote_fs_execute_merges_on_single_replica_time_threshold      | MergeTree             | yes     |
| zero_copy_concurrent_part_removal_max_split_times              | MergeTree             | yes     |
| zero_copy_concurrent_part_removal_max_postpone_ratio           | MergeTree             | yes     |
| zero_copy_merge_mutation_min_parts_size_sleep_before_lock      | MergeTree             | yes     |
| perform_ttl_move_on_insert                                     | storage_policies      | yes     |
| s3_truncate_on_insert                                          | Core                  |         |
| s3_create_new_file_on_insert                                   | Core                  |         |
| s3_skip_empty_files                                            | Core                  |         |
| schema_inference_use_cache_for_s3                              | Core                  |         |
| merge_tree_min_rows_for_concurrent_read_for_remote_filesystem  | Core                  |         |
| merge_tree_min_bytes_for_concurrent_read_for_remote_filesystem | Core                  |         |
| remote_fs_read_backoff_threshold                               | storage_configuration |         |
| remote_fs_read_backoff_max_tries                               | storage_configuration |         |

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.Reload
version: 0.0

[ClickHouse] SHALL reload the vfs configuration when the `SYSTEM RELOAD CONFIG` command is run.

#### RQ.SRS-038.DiskObjectStorageVFS.Settings.VFSToggled
version: 1.0

When the value of the `<allow_vfs>` parameter is changed
from 0 to 1 or 1 to 0 and [ClickHouse] is restarted,
[ClickHouse] SHALL ensure that data is still accessible.

### System

#### RQ.SRS-038.DiskObjectStorageVFS.System.Delete
version: 1.0

[ClickHouse] SHALL ensure disused files in S3 are eventually removed when `<allow_vfs>` is enabled.

#### RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption
version: 0.0

[ClickHouse] SHALL be robust against the following types of connection interruptions.

| Interruption                    |
| ------------------------------- |
| Unstable connection             |
| Unfinished API requests (stuck) |
| Interrupted API requests        |
| Slow connection                 |
| Lost connection to Keeper       |
| Lost connection to Replica      |
| insert_keeper_fault_injection   |

#### RQ.SRS-038.DiskObjectStorageVFS.System.ConnectionInterruption.FaultInjection
version: 0.0

[ClickHouse] SHALL be robust against faults created by `insert_keeper_fault_injection`.

#### RQ.SRS-038.DiskObjectStorageVFS.System.AddKeeper
version: 0.0

[ClickHouse] Replicated tables SHALL continue to operate without issue when a keeper node is added to the cluster.

#### RQ.SRS-038.DiskObjectStorageVFS.System.RemoveKeeper
version: 0.0

[ClickHouse] Replicated tables SHALL continue to operate without issue when a keeper node is removed from the cluster.
This does not apply if there is only one keeper node.

#### RQ.SRS-038.DiskObjectStorageVFS.System.CompactWideParts
version: 1.0

[ClickHouse] SHALL support [S3] external storage of data parts as Wide parts,
Compact parts, or a combination of both types. The user may view the full storage
of data parts in the system.parts table.

#### RQ.SRS-038.DiskObjectStorageVFS.System.Optimize
version: 0.0

[ClickHouse] SHALL support manually triggering merges with `OPTIMIZE [FINAL]`.

#### RQ.SRS-038.DiskObjectStorageVFS.System.Transactions
version: 0.0

[ClickHouse] SHALL produce a reasonable number of Zookeeper transactions when tables are updated with VFS enabled.

### Alter

[ClickHouse] SHALL update all replicas when the following operations on parts are performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Fetch
version: 0.0

[ClickHouse] SHALL update all replicas when FETCH PARTITION/PART is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Detach
version: 0.0

[ClickHouse] SHALL update all replicas when DETACH PARTITION/PART is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Drop
version: 0.0

[ClickHouse] SHALL update all replicas when DROP PARTITION/PART is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Attach
version: 0.0

[ClickHouse] SHALL update all replicas when ATTACH PARTITION/PART is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.AttachFrom
version: 0.0

[ClickHouse] SHALL update all replicas when ATTACH PARTITION FROM is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Replace
version: 0.0

[ClickHouse] SHALL update all replicas when REPLACE PARTITION is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.MoveToTable
version: 0.0

[ClickHouse] SHALL update all replicas when MOVE PARTITION TO TABLE is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Freeze
version: 0.0

[ClickHouse] SHALL update all replicas when FREEZE/UNFREEZE PARTITION is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.MovePart
version: 0.0

[ClickHouse] SHALL update all replicas when MOVE PARTITION/PART is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Index
version: 0.0

[ClickHouse] SHALL update all replicas when the following index manipulations are performed.

| Index Operations  |
| ----------------- |
| ADD INDEX         |
| DROP INDEX        |
| MATERIALIZE INDEX |
| CLEAR INDEX       |

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.OrderBy
version: 0.0

[ClickHouse] SHALL update all replicas when MODIFY ORDER BY is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.SampleBy
version: 0.0

[ClickHouse] SHALL update all replicas when MODIFY SAMPLE BY is performed.

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Projections
version: 0.0

[ClickHouse] SHALL update all replicas when the following projection manipulations are performed.

| Projection Operations  |
| ---------------------- |
| ADD PROJECTION         |
| DROP PROJECTION        |
| MATERIALIZE PROJECTION |
| CLEAR PROJECTION       |

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Column
version: 0.0

[ClickHouse] SHALL update all replicas when the following column manipulations are performed.

| Column Operation     | Description                                                       |
| -------------------- | ----------------------------------------------------------------- |
| ADD COLUMN           | Adds a new column to the table.                                   |
| DROP COLUMN          | Deletes the column.                                               |
| RENAME COLUMN        | Renames an existing column.                                       |
| CLEAR COLUMN         | Resets column values.                                             |
| COMMENT COLUMN       | Adds a text comment to the column.                                |
| MODIFY COLUMN        | Changes column's type, default expression and TTL.                |
| MODIFY COLUMN REMOVE | Removes one of the column properties.                             |
| MATERIALIZE COLUMN   | Materializes the column in the parts where the column is missing. |
| ADD CONSTRAINT       |                                                                   |

#### RQ.SRS-038.DiskObjectStorageVFS.Alter.Update
version: 0.0

[ClickHouse] SHALL update all replicas when the following update manipulations are performed.

| Operation    |
| ------------ |
| DELETE FROM  |
| ALTER DELETE |
| ALTER UPDATE |

### Table

#### RQ.SRS-038.DiskObjectStorageVFS.Table.TableOperations

| Table Operations |
| ---------------- |
| DROP             |
| UNDROP           |
| TRUNCATE         |

#### RQ.SRS-038.DiskObjectStorageVFS.Table.BackgroundCollapse
version: 0.0

[ClickHouse] SHALL support collapsing MergeTree engines and their replicated versions.

| Collapsing Engines                   |
| ------------------------------------ |
| (Replicated)CollapsingMergeTree      |
| (Replicated)ReplacingMergeTree       |
| (Replicated)VersionedCollapsingMerge |
| (Replicated)SummingMergeTree         |

#### RQ.SRS-038.DiskObjectStorageVFS.Table.Migration
version: 1.0

[ClickHouse] SHALL provide commands to migrate table data between any pair of "replicated",
"0-copy" and "vfs" table configurations.

| From       | To         | Command |
| ---------- | ---------- | ------- |
| vfs        | replicated |         |
| vfs        | 0-copy     |         |
| 0-copy     | replicated |         |
| 0-copy     | vfs        |         |
| replicated | 0-copy     |         |
| replicated | vfs        |         |

#### RQ.SRS-038.DiskObjectStorageVFS.Table.TTLMove
version: 1.0

[ClickHouse] SHALL support TTL moves to other hard disks or [S3] disks when VFS
is used with the MergeTree engine. When TTL moves are used, data will not be
duplicated in [S3]. All objects in a table SHALL be accessible with no errors,
even if they have been moved to a different disk.

#### RQ.SRS-038.DiskObjectStorageVFS.Table.TTLDelete
version: 1.0

[ClickHouse] SHALL support TTL object deletion when VFS is used with the MergeTree engine.
When objects are removed, all other objects SHALL be accessible with no errors.

#### RQ.SRS-038.DiskObjectStorageVFS.Table.Detach
version: 1.0

[ClickHouse] SHALL support detaching and attaching tables on VFS disks.
Should the detached table on a replica become corrupted,
[ClickHouse] SHALL ensure that other replicas are not affected.

#### RQ.SRS-038.DiskObjectStorageVFS.Table.StoragePolicy
version: 0.0

[ClickHouse] SHALL support the following storage policy arrangements with VFS

| Policy                             |
| ---------------------------------- |
| Tiered storage                     |
| Single or multiple S3 buckets      |
| Single or multiple object storages |

### Combinatoric

#### Supported Table Configurations

| Engine                       | Replicated | # Columns | Storage Policy |
| ---------------------------- | :--------- | --------- | -------------- |
| MergeTree                    | Yes        | 10        | S3             |
| ReplacingMergeTree           | No         | 100       | Tiered         |
| CollapsingMergeTree          |            | 1000      |                |
| VersionedCollapsingMergeTree |            | 2000      |                |
| AggregatingMergeTree         |            |           |                |
| SummingMergeTree             |            |           |                |

#### Supported Operations

| Simple | TABLE          |     |
| ------ | -------------- | --- |
| INSERT | DROP TABLE     |     |
| DELETE | UNDROP TABLE   |     |
| UPDATE | TRUNCATE TABLE |     |
| SELECT |                |     |

#### RQ.SRS-038.DiskObjectStorageVFS.Combinatoric
version: 0.0

[Clickhouse]  SHALL support any sequence of [supported operations](#supported-operations)
on a table configured with any combination of
[supported table combinations](#supported-table-configurations).

#### RQ.SRS-038.DiskObjectStorageVFS.Combinatoric.Insert
version: 1.0

[Clickhouse]  SHALL support insert operations on a table configured with
any combination of  [supported table combinations](#supported-table-configurations).

### Performance

#### RQ.SRS-038.DiskObjectStorageVFS.Performance
version: 1.0

[Clickhouse] DiskObjectStorageVFS shares performance requirements with
[RQ.SRS-015.S3.Performance](https://github.com/Altinity/clickhouse-regression/blob/main/s3/requirements/requirements.md#performance)

### Object Storage Providers

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.Configuration
version: 1.0

[ClickHouse] SHALL support configuration of object storage disks from a
supported provider with syntax similar to the following:

``` xml
<yandex>
  <storage_configuration>
    <disks>
      <minio>
        <type>s3</type>
        <endpoint>http://minio:9000/my-bucket/object-key/</endpoint>
        <access_key_id>*****</access_key_id>
        <secret_access_key>*****</secret_access_key>
      </minio>
    </disks>
...
</yandex>
```

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.AWS
version: 1.0

[ClickHouse] SHALL support VFS on object storage using AWS [S3].

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.MinIO
version: 1.0

[ClickHouse] SHALL support VFS on object storage using [MinIO].

#### RQ.SRS-038.DiskObjectStorageVFS.Providers.GCS
version: 1.0

[ClickHouse] SHALL support VFS on object storage using [Google Cloud Storage].

## References

* **AWS:** <https://en.wikipedia.org/wiki/Amazon_Web_Services>
* **S3:** <https://en.wikipedia.org/wiki/Amazon_S3>
* **ClickHouse:** <https://clickhouse.tech>
* **GitHub Repository:** <https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs>
* **Revision History:** <https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md>

[S3]: https://en.wikipedia.org/wiki/Amazon_S3
[ClickHouse]: https://clickhouse.tech
[Git]: https://git-scm.com/
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/tree/vfs_object_storage_testing/object_storage_vfs
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/vfs_object_storage_testing/object_storage_vfs/requirements/requirements.md
[Google Cloud Storage]: https://en.wikipedia.org/wiki/Google_Cloud_Storage
[MinIO]: https://en.wikipedia.org/wiki/MinIO

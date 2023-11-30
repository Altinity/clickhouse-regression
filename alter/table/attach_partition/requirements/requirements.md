# SRS034 ClickHouse Alter Table Attach Partition
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Attach Partition|Part](#attach-partitionpart)
    * 3.1 [Flowchart](#flowchart)
    * 3.2 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart](#rqsrs-034clickhousealtertableattachpartitionpart)
    * 3.3 [Reflect Changes in Table Partitions Inside the System Table  ](#reflect-changes-in-table-partitions-inside-the-system-table-)
        * 3.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.System.Parts](#rqsrs-034clickhousealtertableattachpartitionpartsystemparts)
    * 3.4 [Table Engines on Which Attach Partition|Part Can Be Performed](#table-engines-on-which-attach-partitionpart-can-be-performed)
        * 3.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.Supported.Engines](#rqsrs-034clickhousealtertableattachpartitionpartsupportedengines)
    * 3.5 [Table That Is Stored on S3  ](#table-that-is-stored-on-s3-)
        * 3.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.S3  ](#rqsrs-034clickhousealtertableattachpartitionparts3-)
    * 3.6 [Table That Is Stored on Tiered Storage  ](#table-that-is-stored-on-tiered-storage-)
        * 3.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.TieredStorage](#rqsrs-034clickhousealtertableattachpartitionparttieredstorage)
        * 3.6.2 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.PartitionTypes](#rqsrs-034clickhousealtertableattachpartitionpartpartitiontypes)
    * 3.7 [Corrupted Parts on a Specific Partition  ](#corrupted-parts-on-a-specific-partition-)
        * 3.7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.Corrupted](#rqsrs-034clickhousealtertableattachpartitionpartcorrupted)
    * 3.8 [Conditions  ](#conditions-)
    * 3.9 [Role Based Access Control  ](#role-based-access-control-)
        * 3.9.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.RBAC  ](#rqsrs-034clickhousealtertableattachpartitionrbac-)
* 4 [Attach Partition From](#attach-partition-from)
    * 4.1 [Definitions](#definitions)
    * 4.2 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom](#rqsrs-034clickhousealtertableattachpartitionfrom)
    * 4.3 [Reflect Changes in Table Partitions Inside the System Table](#reflect-changes-in-table-partitions-inside-the-system-table)
        * 4.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.System.Parts](#rqsrs-034clickhousealtertableattachpartitionfromsystemparts)
    * 4.4 [Table Engines on Which Attach Partition From Can Be Performed](#table-engines-on-which-attach-partition-from-can-be-performed)
        * 4.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Supported.Engines](#rqsrs-034clickhousealtertableattachpartitionfromsupportedengines)
    * 4.5 [Keeping Data on the Source Table After Attach Partition From](#keeping-data-on-the-source-table-after-attach-partition-from)
        * 4.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData](#rqsrs-034clickhousealtertableattachpartitionfromkeepdata)
    * 4.6 [Table That Is Stored on S3](#table-that-is-stored-on-s3)
        * 4.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.S3](#rqsrs-034clickhousealtertableattachpartitionfroms3)
    * 4.7 [Table That Is Stored on Tiered Storage](#table-that-is-stored-on-tiered-storage)
        * 4.7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.TieredStorage](#rqsrs-034clickhousealtertableattachpartitionfromtieredstorage)
* 5 [Destination Table That Is on a Different Replica](#destination-table-that-is-on-a-different-replica)
    * 5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas](#rqsrs-034clickhousealtertableattachpartitionfromreplicas)
    * 5.2 [Destination Table That Is on a Different Shard](#destination-table-that-is-on-a-different-shard)
    * 5.3 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards](#rqsrs-034clickhousealtertableattachpartitionfromshards)
    * 5.4 [Tables With Different Partition Types](#tables-with-different-partition-types)
        * 5.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.PartitionTypes](#rqsrs-034clickhousealtertableattachpartitionfrompartitiontypes)
    * 5.5 [Corrupted Parts on a Specific Partition](#corrupted-parts-on-a-specific-partition)
        * 5.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Corrupted](#rqsrs-034clickhousealtertableattachpartitionfromcorrupted)
    * 5.6 [Conditions](#conditions)
    * 5.7 [Role Based Access Control](#role-based-access-control)
        * 5.7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.RBAC](#rqsrs-034clickhousealtertableattachpartitionrbac)
* 6 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository]. All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statement in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partitionpart
- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partition-from

## Test Analysis

...

## Attaching Partitions or Parts

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition

[ClickHouse] SHALL support the following queries for attaching partition or part to the table
either from the `detached` directory or from another table.

```sql
ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION|PART partition_expr
ALTER TABLE table2 [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM table1
```

## Supported Table Engines

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines
version: 1.0

[ClickHouse] SHALL support the following table engines for the `ATTACH PARTITION|PART` queries:

|       Supported Engines        |
|:------------------------------:|
|          `MergeTree`           | 
|      `ReplacingMergeTree`      |
|     `AggregatingMergeTree`     |
|     `CollapsingMergeTree`      |
| `VersionedCollapsingMergeTree` |
|      `GraphiteMergeTree`       |
|      `SummingMergeTree`        |

and their `Replicated` versions.

## Storage Policies

### Tiered Storage

### Object Storage
....

## Attach Partition or Part From the Detached Folder

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart
version: 1.0

[ClickHouse] SHALL support `ATTACH PARTITION|PART` ALTER query.

This query SHALL allow the user to add data, either a full PARTITITION or a single PART to the table from the `detached` directory. 

```sql
ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION|PART partition_expr
```

After the query is executed the data SHALL be immediately available for querying.

After the query is executed the changes to the table SHALL be present in the `system.parts` table. 

```sql
SELECT partition, part_type
FROM system.parts
WHERE table = 'table_1'
```

## Partition Types

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartitionTypes
version: 1.0

| Partition Types                               |
|-----------------------------------------------|
| Partition with only compact parts             |
| Partition with only wide parts                |
| Partition with compact and wide parts (mixed) |
| Partition with no parts                       |
| Partition with empty parts                    |

The `ATTACH PARTITION` SHALL work for any partition type.

## Corrupted Parts


----------------------------------------------

### Table That Is Stored on S3  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.S3  
version: 1.0

[ClickHouse] SHALL support using `ATTACH PARTITION|PART` to attach partitions on tables that are stored inside the S3 storage.

### Table That Is Stored on Tiered Storage  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.TieredStorage
version: 1.0

[ClickHouse] SHALL support using `ATTACH PARTITION|PART` to attach partitions on tables that are stored inside the tiered storage.



### Corrupted Parts on a Specific Partition  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionPart.Corrupted
version: 1.0

[ClickHouse] SHALL output an error when trying to `ATTACH PARTITION` when parts of a specific partition are corrupted.

Possible partition types that can be corrupted are,

| Partition Types                               |
|-----------------------------------------------|
| Partition with compact parts                  |
| Partition with wide parts                     |
| Partition with compact and wide parts (mixed) |

### Conditions  
ToDo

### Role Based Access Control  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.RBAC  
version: 1.0

The `ATTACH PARTITION` SHALL only work when the user has the following privileges for table:

| Table priviliges     |
|----------------------|
| CREATE               |

## Attach Partition From

### Definitions

Source Table - The table from which a partition is taken.
Destination Table - The table in which a specific partition is going to be attached.

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom
version: 1.0

To facilitate efficient data management in [ClickHouse], the features `ATTACH PARTITION FROM`  SHALL be supported. This feature allows user to copy data partition from one table to another using the `ATTACH PARTITION FROM` command.

The following SQL command exemplifies this feature:
```sql
ALTER TABLE table2 [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM table1
```

### Reflect Changes in Table Partitions Inside the System Table

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.System.Parts
version: 1.0

[ClickHouse] SHALL reflect the changes in `system.parts` table, when the `ATTACH PARTITION FROM` is executed on the `destination table`. 

For example,

```sql
SELECT partition, part_type
FROM system.parts
WHERE table = 'table_1'
```

### Table Engines on Which Attach Partition From Can Be Performed

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Supported.Engines
version: 1.0

[ClickHouse] SHALL limit the use of the `ATTACH PARTITION FROM` feature to table engines belonging to the MergeTree family. This requirement ensures compatibility and optimal performance. 

The table engines that support `ATTACH PARTITION FROM` include:

|       Supported Engines        |
|:------------------------------:|
|          `MergeTree`           |   |
|      `ReplacingMergeTree`      |
|     `AggregatingMergeTree`     |
|     `CollapsingMergeTree`      |
| `VersionedCollapsingMergeTree` |
|      `GraphiteMergeTree`       |
|      `SummingMergeTree`        |

### Keeping Data on the Source Table After Attach Partition From

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData
version: 1.0

[ClickHouse] SHALL keep the data of the table from which the partition is copied from.

### Temporary Tables

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.

### Table That Is Stored on S3

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.S3
version: 1.0

[ClickHouse] SHALL support using `ATTACH PARTITION FROM` to attach partitions on tables that are stored inside the S3 storage.

### Table That Is Stored on Tiered Storage

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.TieredStorage
version: 1.0

[ClickHouse] SHALL support using `ATTACH PARTITION FROM` to attach partitions on tables that are stored inside the tiered storage.

## Destination Table That Is on a Different Replica

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas
version: 1.0

[ClickHouse] SHALL support using `ATTACH PARTITION FROM` to attach partitions on a destination table that is on a different replica than the source table.

### Destination Table That Is on a Different Shard

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards
version: 1.0

[ClickHouse] SHALL support using `ATTACH PARTITION FROM` to attach partitions on tables that are on different shards.

### Tables With Different Partition Types

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.PartitionTypes
version: 1.0

| Partition Types                               |
|-----------------------------------------------|
| Partition with only compact parts             |
| Partition with only wide parts                |
| Partition with compact and wide parts (mixed) |
| Partition with no parts                       |
| Partition with empty parts                    |

The `ATTACH PARTITION` SHALL work for any partition type.

### Corrupted Parts on a Specific Partition

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Corrupted
version: 1.0

[ClickHouse] SHALL output an error when trying to `ATTACH PARTITION FROM` when parts of a specific partition are corrupted.

Possible partition types that can be corrupted are,

| Partition Types                               |
|-----------------------------------------------|
| Partition with compact parts                  |
| Partition with wide parts                     |
| Partition with compact and wide parts (mixed) |

### Conditions

#### Rules for Attach Partition From

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `ATTACH PARTITION FROM` only when,

* Both tables have the same structure.
* Both tables have the same `ORDER BY` key, and the same primary key.
* Both tables have the same storage policy.

#### Tables With Different Structure

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Structure
version: 1.0

[ClickHouse] SHALL not support the usage of `ATTACH PARTITION FROM` when tables have different structure.

### Role Based Access Control

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.RBAC
version: 1.0

The `ATTACH PARTITION` SHALL only work when the user has the following privileges for table:

| Table priviliges     |
|----------------------|
| CREATE               |


## References
* [ClickHouse]

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[GitHub]: https://github.com

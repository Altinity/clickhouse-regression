# SRS034 ClickHouse Alter Table Attach Partition
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Attaching Partitions or Parts](#attaching-partitions-or-parts)
    * 3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition](#rqsrs-034clickhousealtertableattachpartition)
* 4 [Supported Table Engines](#supported-table-engines)
        * 4.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines](#rqsrs-034clickhousealtertableattachpartitionsupportedtableengines)
* 5 [Storage Policies](#storage-policies)
    * 5.1 [Table That Is Stored on S3  ](#table-that-is-stored-on-s3-)
        * 5.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.S3  ](#rqsrs-034clickhousealtertableattachpartitions3-)
    * 5.2 [Table That Is Stored on Tiered Storage  ](#table-that-is-stored-on-tiered-storage-)
        * 5.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TieredStorage](#rqsrs-034clickhousealtertableattachpartitiontieredstorage)
* 6 [Partition Types](#partition-types)
        * 6.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartitionTypes](#rqsrs-034clickhousealtertableattachpartitionpartitiontypes)
* 7 [Corrupted Parts on a Specific Partition  ](#corrupted-parts-on-a-specific-partition-)
        * 7.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.Corrupted](#rqsrs-034clickhousealtertableattachpartitioncorrupted)
* 8 [Attach Partition or Part From the Detached Folder](#attach-partition-or-part-from-the-detached-folder)
    * 8.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart](#rqsrs-034clickhousealtertableattachpartitionorpart)
    * 8.2 [Reflect Changes in Table Partitions Inside the System Table  ](#reflect-changes-in-table-partitions-inside-the-system-table-)
        * 8.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.System.Parts](#rqsrs-034clickhousealtertableattachpartitionorpartsystemparts)
    * 8.3 [Conditions for Attaching Partition or Part from the Detached Folder](#conditions-for-attaching-partition-or-part-from-the-detached-folder)
    * 8.4 [Role Based Access Control  ](#role-based-access-control-)
        * 8.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionorPart.RBAC  ](#rqsrs-034clickhousealtertableattachpartitionorpartrbac-)
* 9 [Attach Partition From Another Table](#attach-partition-from-another-table)
    * 9.1 [Definitions](#definitions)
    * 9.2 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom](#rqsrs-034clickhousealtertableattachpartitionfrom)
    * 9.3 [Reflect Changes in Table Partitions Inside the System Table](#reflect-changes-in-table-partitions-inside-the-system-table)
        * 9.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.System.Parts](#rqsrs-034clickhousealtertableattachpartitionfromsystemparts)
    * 9.4 [Keeping Data on the Source Table ](#keeping-data-on-the-source-table-)
        * 9.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData](#rqsrs-034clickhousealtertableattachpartitionfromkeepdata)
    * 9.5 [Temporary Tables](#temporary-tables)
        * 9.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable](#rqsrs-034clickhousealtertableattachpartitionfromfromtemporarytable)
    * 9.6 [Destination Table That Is on a Different Replica](#destination-table-that-is-on-a-different-replica)
        * 9.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas](#rqsrs-034clickhousealtertableattachpartitionfromreplicas)
    * 9.7 [Destination Table That Is on a Different Shard](#destination-table-that-is-on-a-different-shard)
        * 9.7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards](#rqsrs-034clickhousealtertableattachpartitionfromshards)
    * 9.8 [Conditions](#conditions)
        * 9.8.1 [Tables With Different Structure](#tables-with-different-structure)
            * 9.8.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Structure](#rqsrs-034clickhousealtertableattachpartitionfromconditionsdifferentstructure)
        * 9.8.2 [Tables With Different `ORDER BY` Key](#tables-with-different-order-by-key)
            * 9.8.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Key.OrderByKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionsdifferentkeyorderbykey)
        * 9.8.3 [Tables With Different Primary Key](#tables-with-different-primary-key)
            * 9.8.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Key.PrimaryKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionsdifferentkeyprimarykey)
        * 9.8.4 [Tables With Different Storage Policy](#tables-with-different-storage-policy)
            * 9.8.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertableattachpartitionfromconditionsdifferentstoragepolicy)
        * 9.8.5 [Tables With Different Indices and Projections](#tables-with-different-indices-and-projections)
            * 9.8.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.IndicesAndProjections](#rqsrs-032clickhousealtertableattachpartitionfromconditionsdifferentindicesandprojections)
        * 9.8.6 [Tables With Different Partition Key](#tables-with-different-partition-key)
            * 9.8.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Key.PartitionKey](#rqsrs-032clickhousealtertableattachpartitionfromconditionsdifferentkeypartitionkey)
    * 9.9 [Role Based Access Control](#role-based-access-control)
        * 9.9.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.RBAC](#rqsrs-034clickhousealtertableattachpartitionrbac)
* 10 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository]. All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statement in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partitionpart
- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partition-from

## Attaching Partitions or Parts

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition

[ClickHouse] SHALL support the following statements for attaching partition or part to the table
either from the `detached` directory or from another table.

```sql
ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION|PART partition_expr
ALTER TABLE table2 [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM table1
```

## Supported Table Engines

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines
version: 1.0

[ClickHouse] SHALL support the following table engines for the `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements:

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

### Table That Is Stored on S3  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.S3  
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements with tables that are stored inside the S3 storage.

### Table That Is Stored on Tiered Storage  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TieredStorage
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements with tables that are stored inside the tiered storage.

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

The `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements SHALL work for any partition type.

## Corrupted Parts on a Specific Partition  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.Corrupted
version: 1.0

[ClickHouse] SHALL output an error when trying to `ATTACH PARTITION` when parts of a specific partition are corrupted.

Possible partition types that can be corrupted are,

| Partition Types                               |
|-----------------------------------------------|
| Partition with compact parts                  |
| Partition with wide parts                     |
| Partition with compact and wide parts (mixed) |

## Attach Partition or Part From the Detached Folder

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ATTACH PARTITION|PART` statement.

This statement SHALL allow the user to add data, either a full `PARTITITION` or a single `PART` to the table from the `detached` directory. 

```sql
ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION|PART [partition_expr]
```

After the query is executed the data SHALL be immediately available for querying on the specified table.

### Reflect Changes in Table Partitions Inside the System Table  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.System.Parts

version: 1.0

[ClickHouse] SHALL reflect the changes in `system.parts` table, when the `ALTER TABLE ATTACH PARTITION|PART` is executed. 

For example,

```sql
SELECT partition, part_types
FROM system.parts
WHERE table = 'table_1'
```

### Conditions for Attaching Partition or Part from the Detached Folder

...

### Role Based Access Control  

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionorPart.RBAC  
version: 1.0

The `ALTER TABLE ATTACH PARTITION|PART` SHALL only work when the user has the following privileges for table:

| Table priviliges     |
|----------------------|
| CREATE               |

## Attach Partition From Another Table

### Definitions

Source Table - The table from which a partition is taken.
Destination Table - The table in which a specific partition is going to be attached.

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ATTACH PARTITION FROM` statement. This feature SHALL allow the user to copy data partition from `source table` to `destination table`.

```sql
ALTER TABLE dest_table [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM src_table
```

### Reflect Changes in Table Partitions Inside the System Table

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.System.Parts
version: 1.0

[ClickHouse] SHALL reflect the changes in `system.parts` table, when the `ALTER TABLE ATTACH PARTITION FROM` is executed on the `destination table`. 

For example,

```sql
SELECT partition, part_type
FROM system.parts
WHERE table = 'table_1'
```

### Keeping Data on the Source Table 

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData
version: 1.0

[ClickHouse] SHALL keep the data of the `source table` from which the partition is copied from.

### Temporary Tables

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.


### Destination Table That Is on a Different Replica

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION FROM` to attach partitions on a destination table that is on a different replica than the source table.

### Destination Table That Is on a Different Shard

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION FROM` to attach partitions on tables that are on different shards.

### Conditions

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` only when,

* Both tables have the same structure.
* Both tables have the same `ORDER BY` key.
* Both tables have the same primary key.
* Both tables have the same storage policy.
* Both tables have the same indices and projections.
* Both tabels have the same partition key or the source table has more granular partitioning

#### Tables With Different Structure

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Structure
version: 1.0

[ClickHouse] SHALL not support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have different structure.

#### Tables With Different `ORDER BY` Key

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Key.OrderByKey
version: 1.0

[ClickHouse] SHALL not support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have different `ORDER BY` key.

#### Tables With Different Primary Key

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Key.PrimaryKey
version: 1.0

[ClickHouse] SHALL not support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have different primary key.

#### Tables With Different Storage Policy

##### RQ.SRS-032.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.StoragePolicy
version: 1.0

[ClickHouse] SHALL not support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have different storage
policy.

#### Tables With Different Indices and Projections

##### RQ.SRS-032.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.IndicesAndProjections
version: 1.0

[ClickHouse] SHALL not support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have different indices and projections.

#### Tables With Different Partition Key

##### RQ.SRS-032.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Different.Key.PartitionKey
version: 1.0

[ClickHouse] SHALL not support the usage of `ALTER TABLE ATTACH PARTITION FROM` when the target table has more granular partitioning than the source table. 
Is is allowed to attach partition from the table with different partition expression when destination partition expression does not re-partition.

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
[partition_expr]: https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#how-to-set-partition-expression

# SRS034 ClickHouse Alter Table Attach Partition
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Definitions](#definitions)
    * 3.1 [Source Table](#source-table)
    * 3.2 [Destination Table](#destination-table)
* 4 [Attaching Partitions or Parts](#attaching-partitions-or-parts)
    * 4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition](#rqsrs-034clickhousealtertableattachpartition)
* 5 [Supported Table Engines](#supported-table-engines)
    * 5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines](#rqsrs-034clickhousealtertableattachpartitionsupportedtableengines)
* 6 [Storage Policies](#storage-policies)
    * 6.1 [Table That Is Stored on S3  ](#table-that-is-stored-on-s3-)
        * 6.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.S3  ](#rqsrs-034clickhousealtertableattachpartitions3-)
    * 6.2 [Table That Is Stored on Tiered Storage  ](#table-that-is-stored-on-tiered-storage-)
        * 6.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TieredStorage](#rqsrs-034clickhousealtertableattachpartitiontieredstorage)
* 7 [Partition Types](#partition-types)
    * 7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartitionTypes](#rqsrs-034clickhousealtertableattachpartitionpartitiontypes)
* 8 [Corrupted Parts on a Specific Partition  ](#corrupted-parts-on-a-specific-partition-)
    * 8.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.Corrupted](#rqsrs-034clickhousealtertableattachpartitioncorrupted)
* 9 [Attach Partition or Part From the Detached Folder](#attach-partition-or-part-from-the-detached-folder)
    * 9.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart](#rqsrs-034clickhousealtertableattachpartitionorpart)
    * 9.2 [Conditions for Attaching Partition or Part from the Detached Folder](#conditions-for-attaching-partition-or-part-from-the-detached-folder)
    * 9.3 [Role Based Access Control When Attach Partition or Part From the Detached Folder](#role-based-access-control-when-attach-partition-or-part-from-the-detached-folder)
        * 9.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.RBAC  ](#rqsrs-034clickhousealtertableattachpartitionorpartrbac-)
* 10 [Attach Partition From Another Table](#attach-partition-from-another-table)
    * 10.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom](#rqsrs-034clickhousealtertableattachpartitionfrom)
    * 10.2 [Validation of Partition Expression](#validation-of-partition-expression)
    * 10.3 [Keeping Data on the Source Table ](#keeping-data-on-the-source-table-)
        * 10.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData](#rqsrs-034clickhousealtertableattachpartitionfromkeepdata)
    * 10.4 [Temporary Tables](#temporary-tables)
        * 10.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable](#rqsrs-034clickhousealtertableattachpartitionfromfromtemporarytable)
    * 10.5 [Destination Table That Is on a Different Replica](#destination-table-that-is-on-a-different-replica)
        * 10.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas](#rqsrs-034clickhousealtertableattachpartitionfromreplicas)
    * 10.6 [Destination Table That Is on a Different Shard](#destination-table-that-is-on-a-different-shard)
        * 10.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards](#rqsrs-034clickhousealtertableattachpartitionfromshards)
    * 10.7 [Conditions when Attach Partition From Another Table](#conditions-when-attach-partition-from-another-table)
        * 10.7.1 [Tables With Same Structure](#tables-with-same-structure)
            * 10.7.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestructure)
        * 10.7.2 [Tables With Same `ORDER BY` Key](#tables-with-same-order-by-key)
            * 10.7.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyorderbykey)
        * 10.7.3 [Tables With Same Primary Key](#tables-with-same-primary-key)
            * 10.7.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyprimarykey)
        * 10.7.4 [Tables With Same Storage Policy](#tables-with-same-storage-policy)
            * 10.7.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestoragepolicy)
        * 10.7.5 [Tables With Same Indices and Projections](#tables-with-same-indices-and-projections)
            * 10.7.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections](#rqsrs-034clickhousealtertableattachpartitionfromconditionssameindicesandprojections)
        * 10.7.6 [Tables With Same Partition Key](#tables-with-same-partition-key)
            * 10.7.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PartitionKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeypartitionkey)
    * 10.8 [Role Based Access Control when Attach Partition From Another Table](#role-based-access-control-when-attach-partition-from-another-table)
        * 10.8.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC](#rqsrs-034clickhousealtertableattachpartitionfromrbac)
* 11 [References](#references)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository]. All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statement in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partitionpart
- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partition-from

## Definitions

### Source Table

The table from which a partition or part is taken.

### Destination Table

The table to which a partition or part is going to be attached.

## Attaching Partitions or Parts

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition

[ClickHouse] SHALL support the following statements for attaching partition or part to the table
either from the `detached` directory or from another table.

```sql
ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION|PART partition_expr
ALTER TABLE table2 [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM table1
```

## Supported Table Engines

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines
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

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartitionTypes
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

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.Corrupted
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

[ClickHouse] SHALL reflect the changes in `system.parts` table, when the `ALTER TABLE ATTACH PARTITION|PART` is executed. 

### Conditions for Attaching Partition or Part from the Detached Folder

...

### Role Based Access Control When Attach Partition or Part From the Detached Folder

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.RBAC  
version: 1.0

The `ALTER TABLE ATTACH PARTITION|PART` SHALL only work when the user has the following privileges for table:

| Table priviliges     |
|----------------------|
| CREATE               |

## Attach Partition From Another Table

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom
version: 1.0

[ClickHouse] SHALL support `ALTER TABLE ATTACH PARTITION FROM` statement. This feature SHALL allow the user to copy data partition from [source table] to [destination table].

```sql
ALTER TABLE dest_table [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM src_table
```

[ClickHouse] SHALL reflect the changes in `system.parts` table, when the `ALTER TABLE ATTACH PARTITION FROM` is executed on the [destination table]. 

### Validation of Partition Expression

- Valid or not
- partition exists or not
- partition exists but no right to access files

### Keeping Data on the Source Table 

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData
version: 1.0

[ClickHouse] SHALL keep the data of the [source table] from which the partition is copied from.

### Temporary Tables

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.


### Destination Table That Is on a Different Replica

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION FROM` to attach partitions on a [destination table] that is on a different replica than the [source table].

### Destination Table That Is on a Different Shard

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION FROM` to attach partitions on tables that are on different shards.

### Conditions when Attach Partition From Another Table

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` only when,

* Both tables have the same structure.
* Both tables have the same `ORDER BY` key.
* Both tables have the same primary key.
* Both tables have the same storage policy.
* Both tables have the same indices and projections.
* Both tabels have the same partition key or the [source table] has more granular partitioning

#### Tables With Same Structure

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have same structure.

#### Tables With Same `ORDER BY` Key

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have same `ORDER BY` key.

#### Tables With Same Primary Key

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have same primary key.

#### Tables With Same Storage Policy

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have same storage
policy.

#### Tables With Same Indices and Projections

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have same indices and projections.

#### Tables With Same Partition Key

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PartitionKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when the [source table] has more granular partitioning than the [desctination table]. 
Is is allowed to attach partition from the table with different partition expression when destination partition expression does not re-partition.
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when attaching from partitioned table to unpartitioned table.  

### Role Based Access Control when Attach Partition From Another Table

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC
version: 1.0

The `ATTACH PARTITION` SHALL only work when the user has the following privileges for table:

| Table priviliges     |
|----------------------|
| CREATE               |


## References
* [ClickHouse]

[Git]: https://git-scm.com/
[source table]: #source-table
[destination table]: #destination-table
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[GitHub]: https://github.com
[partition_expr]: https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#how-to-set-partition-expression

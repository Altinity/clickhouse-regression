# SRS034 ClickHouse Alter Table Attach Partition
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Definitions](#definitions)
    * 3.1 [Source Table](#source-table)
    * 3.2 [Destination Table](#destination-table)
    * 3.3 [Compact part_type](#compact-part_type)
    * 3.4 [Wide part_type](#wide-part_type)
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
* 8 [Corrupted Parts ](#corrupted-parts-)
    * 8.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.CorruptedParts](#rqsrs-034clickhousealtertableattachpartitioncorruptedparts)
* 9 [Table names](#table-names)
    * 9.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TableName](#rqsrs-034clickhousealtertableattachpartitiontablename)
* 10 [Attach Partition or Part From the Detached Folder](#attach-partition-or-part-from-the-detached-folder)
    * 10.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart](#rqsrs-034clickhousealtertableattachpartitionorpart)
    * 10.2 [Conditions for Attaching Partition or Part from the Detached Folder](#conditions-for-attaching-partition-or-part-from-the-detached-folder)
    * 10.3 [Role-Based Access Control When Attach Partition or Part From the Detached Folder](#role-based-access-control-when-attach-partition-or-part-from-the-detached-folder)
        * 10.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.RBAC](#rqsrs-034clickhousealtertableattachpartitionorpartrbac)
* 11 [Attach Partition From Another Table](#attach-partition-from-another-table)
    * 11.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom](#rqsrs-034clickhousealtertableattachpartitionfrom)
    * 11.2 [Validation of Partition Expression](#validation-of-partition-expression)
    * 11.3 [Keeping Data on the Source Table ](#keeping-data-on-the-source-table-)
        * 11.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData](#rqsrs-034clickhousealtertableattachpartitionfromkeepdata)
    * 11.4 [Temporary Tables](#temporary-tables)
        * 11.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable](#rqsrs-034clickhousealtertableattachpartitionfromfromtemporarytable)
    * 11.5 [Destination Table That Is on a Different Replica](#destination-table-that-is-on-a-different-replica)
        * 11.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas](#rqsrs-034clickhousealtertableattachpartitionfromreplicas)
    * 11.6 [Destination Table That Is on a Different Shard](#destination-table-that-is-on-a-different-shard)
        * 11.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards](#rqsrs-034clickhousealtertableattachpartitionfromshards)
    * 11.7 [Conditions when Attach Partition From Another Table](#conditions-when-attach-partition-from-another-table)
        * 11.7.1 [Tables With The Same Structure](#tables-with-the-same-structure)
            * 11.7.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestructure)
        * 11.7.2 [Tables With The Same `ORDER BY` Key](#tables-with-the-same-order-by-key)
            * 11.7.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyorderbykey)
        * 11.7.3 [Tables With The Same Primary Key](#tables-with-the-same-primary-key)
            * 11.7.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyprimarykey)
        * 11.7.4 [Tables With The Same Storage Policy](#tables-with-the-same-storage-policy)
            * 11.7.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestoragepolicy)
        * 11.7.5 [Tables With The Same Indices and Projections](#tables-with-the-same-indices-and-projections)
            * 11.7.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections](#rqsrs-034clickhousealtertableattachpartitionfromconditionssameindicesandprojections)
        * 11.7.6 [Partition Key Condtitions](#partition-key-condtitions)
            * 11.7.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkey)
    * 11.8 [Role-Based Access Control when Attach Partition From Another Table](#role-based-access-control-when-attach-partition-from-another-table)
        * 11.8.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC](#rqsrs-034clickhousealtertableattachpartitionfromrbac)
* 12 [References](#references)



## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository]. All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for the `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partitionpart
- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#attach-partition-from

## Definitions

### Source Table

The table from which a partition or part is taken.

### Destination Table

The table to which a partition or part is going to be attached.

### Compact part_type

All columns are stored in one file in a filesystem.

### Wide part_type

Each column is stored in a separate file in a filesystem.

Data storing format is controlled by the min_bytes_for_wide_part and min_rows_for_wide_part settings of the MergeTree table.

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

| Partition Types                                   |
|---------------------------------------------------|
| Partition with only [compact] parts               |
| Partition with only [wide] parts                  |
| Partition with [compact] and [wide] parts (mixed) |
| Partition with empty parts                        |

The `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements SHALL work for any partition type.

## Corrupted Parts 

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.CorruptedParts
version: 1.0

[ClickHouse] SHALL output an error when trying to `ATTACH PARTITION` when parts of a specific partition are corrupted.

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` when parts have correct checksums.

Possible partition types that can be corrupted are,

| Partition Types                               |
|-----------------------------------------------|
| Partition with compact parts                  |
| Partition with wide parts                     |
| Partition with compact and wide parts (mixed) |

## Table names

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TableName
version: 1.0

The `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements SHALL only work when the table names are valid.

## Attach Partition or Part From the Detached Folder

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart
version: 1.0

[ClickHouse] SHALL support the `ALTER TABLE ATTACH PARTITION|PART` statement.

This statement SHALL allow the user to add data, either a full `PARTITITION` or a single `PART` to the table from the `detached` directory. 

```sql
ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION|PART [partition_expr]
```

After the query is executed the data SHALL be immediately available for querying on the specified table.

[ClickHouse] SHALL reflect the changes in the `system.parts` table, when the `ALTER TABLE ATTACH PARTITION|PART` is executed. 

### Conditions for Attaching Partition or Part from the Detached Folder

...

### Role-Based Access Control When Attach Partition or Part From the Detached Folder

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.RBAC
version: 1.0

The `ALTER TABLE ATTACH PARTITION|PART` SHALL only work when the user has the following privileges for the table:

| Table priviliges     |
|----------------------|
| CREATE               |

## Attach Partition From Another Table

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom
version: 1.0

[ClickHouse] SHALL support the`ALTER TABLE ATTACH PARTITION FROM` statement. This feature SHALL allow the user to copy data partition from [source table] to [destination table].

```sql
ALTER TABLE dest_table [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM src_table
```

[ClickHouse] SHALL reflect the changes in the `system.parts` table, when the `ALTER TABLE ATTACH PARTITION FROM` is executed on the [destination table]. 

### Validation of Partition Expression

- Valid or not
- partition exists or not
- partition exists but no right to access files

### Keeping Data on the Source Table 

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData
version: 1.0

[ClickHouse] SHALL keep the data of the [source table] from which the partition is copied.

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
* Both tables have the same partition key or the [source table] has more granular partitioning

#### Tables With The Same Structure

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same structure.

#### Tables With The Same `ORDER BY` Key

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same `ORDER BY` key.

#### Tables With The Same Primary Key

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same primary key.

#### Tables With The Same Storage Policy

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same storage
policy.

#### Tables With The Same Indices and Projections

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same indices and projections.

#### Partition Key Condtitions

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when the [source table] has more granular partitioning than the [desctination table]. 
It is allowed to attach a partition from the table with different partition expression when the destination partition expression does not re-partition.
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when attaching from a partitioned table to an unpartitioned table.  

### Role-Based Access Control when Attach Partition From Another Table

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC
version: 1.0

The `ATTACH PARTITION` SHALL only work when the user has the following privileges for the table:

| Table priviliges     |
|----------------------|
| CREATE               |


## References
* [ClickHouse]

[Git]: https://git-scm.com/
[source table]: #source-table
[destination table]: #destination-table
[compact]: #compact-part_type
[wide]: #wide-part_type
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[GitHub]: https://github.com
[partition_expr]: https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#how-to-set-partition-expression

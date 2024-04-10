# SRS034 ClickHouse Alter Table Attach Partition
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Definitions](#definitions)
    * 3.1 [Source Table](#source-table)
    * 3.2 [Destination Table](#destination-table)
    * 3.3 [Compact Part Type](#compact-part-type)
    * 3.4 [Wide Part Type](#wide-part-type)
* 4 [Attaching Partitions or Parts](#attaching-partitions-or-parts)
    * 4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition](#rqsrs-034clickhousealtertableattachpartition)
* 5 [Supported Table Engines](#supported-table-engines)
    * 5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines](#rqsrs-034clickhousealtertableattachpartitionsupportedtableengines)
* 6 [Storage Policies](#storage-policies)
    * 6.1 [Table That Is Stored on S3  ](#table-that-is-stored-on-s3-)
        * 6.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.S3](#rqsrs-034clickhousealtertableattachpartitions3)
    * 6.2 [Table That Is Stored on Tiered Storage  ](#table-that-is-stored-on-tiered-storage-)
        * 6.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TieredStorage](#rqsrs-034clickhousealtertableattachpartitiontieredstorage)
* 7 [Partition Types](#partition-types)
    * 7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartitionTypes](#rqsrs-034clickhousealtertableattachpartitionpartitiontypes)
* 8 [Corrupted Parts ](#corrupted-parts-)
    * 8.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.CorruptedParts](#rqsrs-034clickhousealtertableattachpartitioncorruptedparts)
* 9 [Part Names](#part-names)
    * 9.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.ChunkLevelReset](#rqsrs-034clickhousealtertableattachpartitionpartnameschunklevelreset)
    * 9.2 [Change of Chunk Level During Attach Partition From](#change-of-chunk-level-during-attach-partition-from)
        * 9.2.1 [Variables that are used in `ATTACH PARTITION FROM` statement:](#variables-that-are-used-in-attach-partition-from-statement)
        * 9.2.2 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.MergeIncrement](#rqsrs-034clickhousealtertableattachpartitionpartnamesmergeincrement)
        * 9.2.3 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.EqualToLegacyMaxLevel](#rqsrs-034clickhousealtertableattachpartitionpartnamesequaltolegacymaxlevel)
        * 9.2.4 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.GreaterThanLegacyMaxLevel](#rqsrs-034clickhousealtertableattachpartitionpartnamesgreaterthanlegacymaxlevel)
        * 9.2.5 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.Replication](#rqsrs-034clickhousealtertableattachpartitionpartnamesreplication)
* 10 [Table Names](#table-names)
    * 10.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TableName](#rqsrs-034clickhousealtertableattachpartitiontablename)
* 11 [Attach Partition or Part From the Detached Folder](#attach-partition-or-part-from-the-detached-folder)
    * 11.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart](#rqsrs-034clickhousealtertableattachpartitionorpart)
    * 11.2 [Conditions for Attaching Partition or Part from the Detached Folder](#conditions-for-attaching-partition-or-part-from-the-detached-folder)
    * 11.3 [Role-Based Access Control When Attach Partition or Part From the Detached Folder](#role-based-access-control-when-attach-partition-or-part-from-the-detached-folder)
        * 11.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.RBAC](#rqsrs-034clickhousealtertableattachpartitionorpartrbac)
* 12 [Attach Partition From Another Table](#attach-partition-from-another-table)
    * 12.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom](#rqsrs-034clickhousealtertableattachpartitionfrom)
    * 12.2 [Validation of Partition Expression](#validation-of-partition-expression)
    * 12.3 [Keeping Data on the Source Table ](#keeping-data-on-the-source-table-)
        * 12.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData](#rqsrs-034clickhousealtertableattachpartitionfromkeepdata)
    * 12.4 [Temporary Tables](#temporary-tables)
        * 12.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable](#rqsrs-034clickhousealtertableattachpartitionfromfromtemporarytable)
    * 12.5 [Destination Table That Is on a Different Replica](#destination-table-that-is-on-a-different-replica)
        * 12.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas](#rqsrs-034clickhousealtertableattachpartitionfromreplicas)
    * 12.6 [Destination Table That Is on a Different Shard](#destination-table-that-is-on-a-different-shard)
        * 12.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards](#rqsrs-034clickhousealtertableattachpartitionfromshards)
    * 12.7 [Conditions when Attach Partition From Another Table](#conditions-when-attach-partition-from-another-table)
        * 12.7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions](#rqsrs-034clickhousealtertableattachpartitionfromconditions)
        * 12.7.2 [Tables With The Same Structure](#tables-with-the-same-structure)
            * 12.7.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestructure)
        * 12.7.3 [Tables With The Same `ORDER BY` Key](#tables-with-the-same-order-by-key)
            * 12.7.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyorderbykey)
        * 12.7.4 [Tables With The Same Primary Key](#tables-with-the-same-primary-key)
            * 12.7.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyprimarykey)
        * 12.7.5 [Tables With The Same Storage Policy](#tables-with-the-same-storage-policy)
            * 12.7.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestoragepolicy)
        * 12.7.6 [Tables With The Same Indices and Projections](#tables-with-the-same-indices-and-projections)
            * 12.7.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections](#rqsrs-034clickhousealtertableattachpartitionfromconditionssameindicesandprojections)
        * 12.7.7 [Partition Key Conditions](#partition-key-conditions)
            * 12.7.7.1 [Partition Key](#partition-key)
                * 12.7.7.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.Different](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkeydifferent)
                * 12.7.7.1.2 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.Unpartitioned](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkeyunpartitioned)
            * 12.7.7.2 [Possible Partition Expressions](#possible-partition-expressions)
                * 12.7.7.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.Column](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkeycolumn)
                * 12.7.7.2.2 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.FunctionsOfColumns](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkeyfunctionsofcolumns)
                * 12.7.7.2.3 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.ExpressionsInvolvingMultipleColumns](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkeyexpressionsinvolvingmultiplecolumns)
                * 12.7.7.2.4 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.TupleOfExpressions](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkeytupleofexpressions)
                * 12.7.7.2.5 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.UDFs](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkeyudfs)
    * 12.8 [Role-Based Access Control when Attach Partition From Another Table](#role-based-access-control-when-attach-partition-from-another-table)
        * 12.8.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC](#rqsrs-034clickhousealtertableattachpartitionfromrbac)
* 13 [References](#references)


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

### Compact Part Type

All columns are stored in one file in a filesystem.

### Wide Part Type

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

## Part Names

The part name contains information about the partition name where the part is located, the minimum and maximum number of data blocks, chunk level (part level), and the mutation version. For example, let's break down the name of the part `201901_1_9_2_11`:

- 201901 is the partition name.
- 1 is the minimum number of the data block.
- 9 is the maximum number of the data block.
- 2 is the chunk level (the depth of the merge tree from which it is formed).
- 11 is the mutation version (if the part has mutated).

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.ChunkLevelReset
version: 1.0

[ClickHouse] SHALL reset chunk level upon `ATTACH PART|PARTITION` to (Replicated-)MergeTree table. For MergeTree table engines it is supported from version 24.3.

**Example**:
```sql
CREATE TABLE t (id Int32) engine=MergeTree ORDER BY id PARTITION BY id;
INSERT INTO t VALUES (1), (2), (3);
SELECT name, active FROM system.parts WHERE table='t' AND active;
```
|part_name| active|
|---------|-------|
|1_1_1_0  |	1     |
|2_2_2_0  |	1     |
|3_3_3_0  |	1     |

```sql
OPTIMIZE TABLE t FINAL; --increases chunk level
OPTIMIZE TABLE t FINAL; --increases chunk level
SELECT name, active FROM system.parts WHERE table='t' AND active;
```
|part_name| active|
|---------|-------|
|1_1_1_2  |	1     |
|2_2_2_2  |	1     |
|3_3_3_2  |	1     |

```sql
ALTER TABLE t DETACH PART '1_1_1_2';
ALTER TABLE t DETACH PART '2_2_2_2';

ALTER TABLE t ATTACH PART '1_1_1_2'; or ALTER TABLE t ATTACH PARTITION 1;
ALTER TABLE t ATTACH PART '2_2_2_2'; or ALTER TABLE t ATTACH PARTITION 2;
```
```sql
SELECT name, active FROM system.parts WHERE table='t' AND active;
```
|part_name| active|
|---------|-------|
|1_4_4_0  |	1     |
|2_5_5_0  |	1     |
|3_3_3_2  |	1     |

Parts that were DETACHED and ATTACHED back have 0 chunk level.

### Change of Chunk Level During Attach Partition From

#### Variables that are used in `ATTACH PARTITION FROM` statement:
```yaml 
Destination Table - where partiton will be attached:
    - empty destination table
    - non-empty destination table
    
Part/Partition In Destination Table (if non-empty):
    Same partition as in source table and the same chunk level:
        - source chunk level equals to destination chunk level
    Same partition as in source table but different chunk level:
        - source chunk level is greater than destination chunk level
        - source chunk level is lower than destination chunk level

Source And Destination Table Engines:  
    -MergeTree       
    -ReplacingMergeTree  
    -AggregatingMergeTree     
    -CollapsingMergeTree      
    -VersionedCollapsingMergeTree
    -GraphiteMergeTree
    -SummingMergeTree        
    and their Replicated- versions 
    -SharedMergeTree

Partition Keys:
    - source and destination table are both unpartitioned
    - source and destination table have same partition key
    - source and destination table have different partition keys

Chunk Levels:
    - equal to MAX_LEVEL = 999999999
    - greater than MAX_LEVEL
    - less than MAX_LEVEL
    - equal to LEGACY_MAX_LEVEL = 2^32
    - greater than LEGACY_MAX_LEVEL = 2^32
```

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.MergeIncrement
version: 1.0

[ClickHouse] SHALL increment chunk level by 1 from highest chunk level of parts that are merged after `ATTACH PARTITION FROM` 
when merging two or more parts in one part. All engines in the MergeTree family should be supported. 

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.EqualToLegacyMaxLevel
version: 1.0

[ClickHouse] SHALL set chunk level to MAX_LEVEL=999999999 when chunck level is LEGACY_MAX_LEVEL = 2^32. All engines in the MergeTree family should be supported.

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.GreaterThanLegacyMaxLevel
version: 1.0

[ClickHouse] SHALL not attach partition or part from disk when part's chunk level is greater than LEGACY_MAX_LEVEL = 2^32. All engines in the MergeTree family should be supported.

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartNames.Replication
version: 1.0

[ClickHouse] SHALL guarantee that all replicas of a given table contain identical data when replication_queue is empty.


## Table Names

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TableName
version: 1.0

The `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements SHALL only work when the table names are valid.

## Attach Partition or Part From the Detached Folder

### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart
version: 1.0

[ClickHouse] SHALL support the `ALTER TABLE ATTACH PARTITION|PART` statement.

This statement SHALL allow the user to add data, either a full `PARTITION` or a single `PART` to the table from the `detached` directory. 

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

| Privileges     |
|----------------|
| No privileges  |
| SELECT         |
| INSERT         |
| ALTER          |
| ALTER TABLE    |

The `ATTACH PARTITION|PART` SHALL only work when the user has the following privileges for the table:

| Table Privilege |
|-----------------|
| INSERT          |


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

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions
version: 1.0

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

#### Partition Key Conditions

##### Partition Key

###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.Different
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when the [source table] has more granular partitioning than the [destination table]. 
It is allowed to attach a partition from the table with different partition expression when the destination partition expression does not re-partition.

###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.Unpartitioned
version: 1.0
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when attaching from a partitioned table to an unpartitioned table.  

##### Possible Partition Expressions
The partition key in ClickHouse can be any expression derived from the table columns, including various types of partition expressions that are listed below.

###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.Column
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` with a column (of any type) as the partition expression.

###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.FunctionsOfColumns
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` with functions of columns as the partition expression.

**It includes:**
* ###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.FunctionsOfColumns.DateTime
    * Date and Time Functions: Such as toYYYYMM(dateColumn), toMonday(dateColumn) or toStartOfMonth(dateColumn)
* ###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.FunctionsOfColumns.HashingFunctions
    * Hashing Functions: Such as cityHash64(userID) or intHash32(status)
* ###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.FunctionsOfColumns.MathFunctions
    * Mathematical Functions: Such as intDiv(number, N) or number % N
* ###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.FunctionsOfColumns.StringFunctions
    * String Functions: Such as substring(stringColumn, 1, N)
* ###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.FunctionsOfColumns.ComplexFunctions
    * Complex Expressions: Such as combinations of functions and operations, e.g., toYYYYMM(dateColumn) * 100 + intDiv(numberColumn, 1000)

###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.ExpressionsInvolvingMultipleColumns
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` with expressions involving multiple columns as the partition expression.
    * Example: toYYYYMMDD(dateColumn) + intDiv(numberColumn, 100) or (dateColumn, eventType) 

###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.TupleOfExpressions
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` with tuple of expressions as the partition expression.
    * Example: (CounterID, StartDate, intHash32(UserID))

###### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey.UDFs
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` with user-defined functions as the partition expression.

By default, the floating-point partition key is not supported. To use it enable the setting allow_floating_point_partition_key.

### Role-Based Access Control when Attach Partition From Another Table

#### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC
version: 1.0

| Privileges     |
|----------------|
| No privileges  |
| SELECT         |
| INSERT         |
| ALTER          |
| ALTER TABLE    |

The `ATTACH PARTITION FROM` SHALL only work when the user has the following privileges for the source and destination tables:

| Source | Destination          |
|--------|----------------------|
| SELECT | ALTER TABLE, INSERT  |
| SELECT | ALTER, INSERT        |


## References
* [ClickHouse]

[Git]: https://git-scm.com
[source table]: #source-table
[destination table]: #destination-table
[compact]: #compact-part_type
[wide]: #wide-part_type
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/attach_partition/alter/table/attach_partition/requirements/requirements.md
[GitHub]: https://github.com
[partition_expr]: https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#how-to-set-partition-expression

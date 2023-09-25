# SRS032 ClickHouse Alter Table statement

# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [User Actions](#user-actions)
* 4 [REPLACE PARTITION](#replace-partition)
  * 4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition](#rqsrs-032clickhousealtertablereplacepartition)
  * 4.2 [Replace Partition Between Tables](#replace-partition-between-tables)
    * 4.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData](#rqsrs-032clickhousealtertablereplacepartitionreplacedata)
      * 4.2.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditions)
      * 4.2.1.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.KeepTable](#rqsrs-032clickhousealtertablereplacepartitionreplacedatakeeptable)
      * 4.2.1.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable](#rqsrs-032clickhousealtertablereplacepartitionreplacedatatemporarytable)
      * 4.2.1.4 [Conditions Not Satisfied](#conditions-not-satisfied)
        * 4.2.1.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstructure)
        * 4.2.1.4.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentkey)
        * 4.2.1.4.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstoragepolicy)
  * 4.3 [New Data](#new-data)
    * 4.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NewData](#rqsrs-032clickhousealtertablereplacepartitionnewdata)
  * 4.4 [Storage Engine](#storage-engine)
    * 4.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.StorageEngine](#rqsrs-032clickhousealtertablereplacepartitionstorageengine)
  * 4.5 [Partition Key](#partition-key)
    * 4.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionKey](#rqsrs-032clickhousealtertablereplacepartitionpartitionkey)
  * 4.6 [Replace Multiple Partitions](#replace-multiple-partitions)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MultiplePartitions](#rqsrs-032clickhousealtertablereplacepartitionmultiplepartitions)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE` statement in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#replace-partition

  GNU nano 6.2                                                                                         asd *                                                                                                
## User Actions


| **Action**                  | **Description**                                                                                                              |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `DETACH PARTITION/PART`     | `ALTER TABLE table_name [ON CLUSTER cluster] DETACH PARTITION/PART partition_expr`                                           |
| `DROP PARTITION/PART`       | `ALTER TABLE table_name [ON CLUSTER cluster] DROP PARTITION/PART partition_expr`                                             |                                          >
| `DROP DETACHED PARTITION`   | `ALTER TABLE table_name [ON CLUSTER cluster] DROP DETACHED PARTITION/PART partition_expr`                                    |
| `ATTACH PARTITION`          | `ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION/PART partition_expr`                                           |
| `ATTACH PARTITION FROM`     | `ALTER TABLE table2 [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM table1`                                        |
| `REPLACE PARTITION`         | `ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1`                                       |
| `MOVE PARTITION TO TABLE`   | `ALTER TABLE table_source [ON CLUSTER cluster] MOVE PARTITION partition_expr TO TABLE table_dest`                            |
| `CLEAR COLUMN IN PARTITION` | `ALTER TABLE table_name [ON CLUSTER cluster] CLEAR COLUMN column_name IN PARTITION partition_expr`                           |
| `FREEZE PARTITION`          | `ALTER TABLE table_name [ON CLUSTER cluster] FREEZE [PARTITION partition_expr] [WITH NAME 'backup_name']`                    |
| `UNFREEZE PARTITION`        | `ALTER TABLE table_name [ON CLUSTER cluster] UNFREEZE [PARTITION 'part_expr'] WITH NAME 'backup_name'`                       |
| `CLEAR INDEX IN PARTITION`  | `ALTER TABLE table_name [ON CLUSTER cluster] CLEAR INDEX index_name IN PARTITION partition_expr`                             |
| `FETCH PARTITION`           | `ALTER TABLE table_name [ON CLUSTER cluster] FETCH PARTITION/PART partition_expr FROM 'path-in-zookeeper'`                   |
| `MOVE PARTITION`            | `ALTER TABLE table_name [ON CLUSTER cluster] MOVE PARTITION/PART partition_expr TO DISK/VOLUME 'disk_name'`                  |
| `UPDATE IN PARTITION`       | `ALTER TABLE [db.]table [ON CLUSTER cluster] UPDATE column1 = expr1 [, ...] [IN PARTITION partition_expr] WHERE filter_expr` |
| `DELETE IN PARTITION`       | `ALTER TABLE [db.]table [ON CLUSTER cluster] DELETE [IN PARTITION partition_expr] WHERE filter_expr`                         |


## REPLACE PARTITION

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`.

### Replace Partition Between Tables

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData
version: 1.0

[ClickHouse] SHALL support the ability to add a new partition to a table, replacing an existing one.

For example,

This query copies the data partition from the `table1` to `table2` and replaces existing partition in the `table2`.

```sql
ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1
```

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` between two tables when,

* Both Table have the same structure.
* Both tables have the same partition key, the same `ORDER BY` key and the same primary key.
* Both tables must have the same storage policy.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.KeepTable
version: 1.0

[ClickHouse] SHALL keep the data of the table from which the partition is copied from.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.

##### Conditions Not Satisfied

###### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different structure.

###### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different partition
key, `ORDER BY` key andprimary key.

###### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different storage
policy.

### New Data

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NewData
version: 1.0

[ClickHouse] SHALL support replace an existing partition with new data using `ATTACH`.

For example,

```sql
ALTER TABLE my_table REPLACE PARTITION 202301 WITH ATTACH 'path_to_new_data';
```

### Storage Engine

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.StorageEngine
version: 1.0

[ClickHouse] SHALL support replacing the storage engine used for a specific partition.

For example,

```sql
ALTER TABLE my_table REPLACE PARTITION 202302
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_id);
```

### Partition Key

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionKey
version: 1.0

[ClickHouse] SHALL support replacing the partitioning key for a specific partition.

For example,

```sql
ALTER TABLE my_table REPLACE PARTITION 202303
PARTITION BY toYYYY(event_date)
ORDER BY (event_date, event_id);
```

### Replace Multiple Partitions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MultiplePartitions
version: 1.0

[ClickHouse] SHALL support replacing multiple partitions with new data or different configurations in a single command.

For example,

```sql
ALTER TABLE my_table REPLACE PARTITION 202305, 202306, 202307
WITH ATTACH 'path_to_new_data';
```

[ClickHouse]: https://clickhouse.com

[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md

[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md

[Git]: https://git-scm.com/

[GitHub]: https://github.com

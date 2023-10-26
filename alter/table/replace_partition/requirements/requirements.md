# SRS032 ClickHouse Alter Table Replace Partition

# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Flowchart](#flowchart)
* 4 [Definitions](#definitions)
* 5 [User Actions](#user-actions)
* 6 [Replace Partition](#replace-partition)
    * 6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition](#rqsrs-032clickhousealtertablereplacepartition)
    * 6.2 [Changes In Table Partitions](#changes-in-table-partitions)
        * 6.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.System.Parts](#rqsrs-032clickhousealtertablereplacepartitionsystemparts)
* 7 [Keeping Data on the Source Table After Replace Partition](#keeping-data-on-the-source-table-after-replace-partition)
    * 7.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData](#rqsrs-032clickhousealtertablereplacepartitionkeepdata)
* 8 [Table With Non-Existent Partition](#table-with-non-existent-partition)
    * 8.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NonExistentPartition](#rqsrs-032clickhousealtertablereplacepartitionnonexistentpartition)
* 9 [From Temporary Table](#from-temporary-table)
    * 9.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.FromTemporaryTable](#rqsrs-032clickhousealtertablereplacepartitionfromtemporarytable)
* 10 [From Temporary Table To Temporary Table](#from-temporary-table-to-temporary-table)
    * 10.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTables](#rqsrs-032clickhousealtertablereplacepartitiontemporarytables)
* 11 [Using Into Outfile Clause With Replace Partition Clause](#using-into-outfile-clause-with-replace-partition-clause)
    * 11.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.IntoOutfile](#rqsrs-032clickhousealtertablereplacepartitionintooutfile)
* 12 [Using The Format Clause With Replace Partition Clause](#using-the-format-clause-with-replace-partition-clause)
    * 12.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Format](#rqsrs-032clickhousealtertablereplacepartitionformat)
* 13 [Using Settings With Replace Partition Clause](#using-settings-with-replace-partition-clause)
    * 13.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Settings](#rqsrs-032clickhousealtertablereplacepartitionsettings)
* 14 [Table Is on a Separate Disk](#table-is-on-a-separate-disk)
    * 14.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Disks](#rqsrs-032clickhousealtertablereplacepartitiondisks)
* 15 [Table That Is Stored on S3](#table-that-is-stored-on-s3)
    * 15.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.S3](#rqsrs-032clickhousealtertablereplacepartitions3)
* 16 [Destination Table That Is on a Different Replica](#destination-table-that-is-on-a-different-replica)
    * 16.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Replicas](#rqsrs-032clickhousealtertablereplacepartitionreplicas)
* 17 [Destination Table That Is on a Different Shard](#destination-table-that-is-on-a-different-shard)
    * 17.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Shards](#rqsrs-032clickhousealtertablereplacepartitionshards)
* 18 [Table That Is Stored on a Server With Different ClickHouse Version](#table-that-is-stored-on-a-server-with-different-clickhouse-version)
    * 18.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Versions](#rqsrs-032clickhousealtertablereplacepartitionversions)
* 19 [Table That Has a Different Encoding](#table-that-has-a-different-encoding)
    * 19.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encodings](#rqsrs-032clickhousealtertablereplacepartitionencodings)
* 20 [Encrypted Tables And Unencrypted Tables](#encrypted-tables-and-unencrypted-tables)
    * 20.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encryption](#rqsrs-032clickhousealtertablereplacepartitionencryption)
* 21 [Deduplication Tables](#deduplication-tables)
    * 21.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Deduplication](#rqsrs-032clickhousealtertablereplacepartitiondeduplication)
* 22 [Tables With Different Partition Types](#tables-with-different-partition-types)
    * 22.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionTypes](#rqsrs-032clickhousealtertablereplacepartitionpartitiontypes)
* 23 [Corrupted Parts on a Specific Partition](#corrupted-parts-on-a-specific-partition)
    * 23.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted](#rqsrs-032clickhousealtertablereplacepartitioncorrupted)
* 24 [Conditions](#conditions)
    * 24.1 [Rules for Replacing Partitions on Tables](#rules-for-replacing-partitions-on-tables)
        * 24.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions](#rqsrs-032clickhousealtertablereplacepartitionconditions)
    * 24.2 [Tables With Different Structure](#tables-with-different-structure)
        * 24.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentstructure)
    * 24.3 [Tables With Different Partition Key](#tables-with-different-partition-key)
        * 24.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentkey)
    * 24.4 [Tables With Different Storage Policy](#tables-with-different-storage-policy)
        * 24.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentstoragepolicy)
* 25 [Prohibited Actions After From Clause](#prohibited-actions-after-from-clause)
    * 25.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited](#rqsrs-032clickhousealtertablereplacepartitionprohibited)
    * 25.2 [Using Order By and Partition By](#using-order-by-and-partition-by)
        * 25.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.OrderAndPartition](#rqsrs-032clickhousealtertablereplacepartitionprohibitedorderandpartition)
    * 25.3 [Table Functions](#table-functions)
        * 25.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.TableFunctions](#rqsrs-032clickhousealtertablereplacepartitionprohibitedtablefunctions)
    * 25.4 [Subquery](#subquery)
        * 25.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Subquery](#rqsrs-032clickhousealtertablereplacepartitionprohibitedsubquery)
    * 25.5 [Join Clause](#join-clause)
        * 25.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Join](#rqsrs-032clickhousealtertablereplacepartitionprohibitedjoin)
    * 25.6 [Replace Partition From Tables That Do Not Have Partitions](#replace-partition-from-tables-that-do-not-have-partitions)
        * 25.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.IncorrectTableEngines](#rqsrs-032clickhousealtertablereplacepartitionprohibitedincorrecttableengines)
* 26 [Replacing Partitions During Ongoing Merges and Mutations](#replacing-partitions-during-ongoing-merges-and-mutations)
    * 26.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent](#rqsrs-032clickhousealtertablereplacepartitionconcurrent)
    * 26.2 [Staring New Merges With Ongoing Replace Partition](#staring-new-merges-with-ongoing-replace-partition)
        * 26.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Merges](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmerges)
    * 26.3 [Staring New Mutations With Ongoing Replace Partition](#staring-new-mutations-with-ongoing-replace-partition)
        * 26.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Mutations](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmutations)
    * 26.4 [Insert Into Table](#insert-into-table)
        * 26.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Insert](#rqsrs-032clickhousealtertablereplacepartitionconcurrentinsert)
    * 26.5 [Delete Table](#delete-table)
        * 26.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Delete](#rqsrs-032clickhousealtertablereplacepartitionconcurrentdelete)
    * 26.6 [Attach Table](#attach-table)
        * 26.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Attach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentattach)
    * 26.7 [Detach Table](#detach-table)
        * 26.7.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Detach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentdetach)
    * 26.8 [Optimize Table](#optimize-table)
        * 26.8.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Optimize](#rqsrs-032clickhousealtertablereplacepartitionconcurrentoptimize)
    * 26.9 [Alter](#alter)
        * 26.9.1 [Add Column](#add-column)
            * 26.9.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Add](#rqsrs-032clickhousealtertablereplacepartitionconcurrentalteradd)
        * 26.9.2 [Drop Column](#drop-column)
            * 26.9.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Drop](#rqsrs-032clickhousealtertablereplacepartitionconcurrentalterdrop)
        * 26.9.3 [Clear Column](#clear-column)
            * 26.9.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Clear](#rqsrs-032clickhousealtertablereplacepartitionconcurrentalterclear)
        * 26.9.4 [Modify Column](#modify-column)
            * 26.9.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Modify](#rqsrs-032clickhousealtertablereplacepartitionconcurrentaltermodify)
        * 26.9.5 [Modify Column Remove](#modify-column-remove)
            * 26.9.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.ModifyRemove](#rqsrs-032clickhousealtertablereplacepartitionconcurrentaltermodifyremove)
        * 26.9.6 [Materialize](#materialize)
            * 26.9.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Materialize](#rqsrs-032clickhousealtertablereplacepartitionconcurrentaltermaterialize)
    * 26.10 [Manipulating Partitions](#manipulating-partitions)
        * 26.10.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitions)
        * 26.10.2 [Detach](#detach)
            * 26.10.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Detach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsdetach)
        * 26.10.3 [Drop](#drop)
            * 26.10.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Drop](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsdrop)
        * 26.10.4 [Attach](#attach)
            * 26.10.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Attach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsattach)
        * 26.10.5 [Attach From](#attach-from)
            * 26.10.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.AttachFrom](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsattachfrom)
        * 26.10.6 [Replace](#replace)
            * 26.10.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Replace](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsreplace)
        * 26.10.7 [Move To Table](#move-to-table)
            * 26.10.7.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.MoveToTable](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsmovetotable)
        * 26.10.8 [Clear Column In Partition](#clear-column-in-partition)
            * 26.10.8.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearColumnInPartition](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsclearcolumninpartition)
        * 26.10.9 [Freeze](#freeze)
            * 26.10.9.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Freeze](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsfreeze)
        * 26.10.10 [Unfreeze](#unfreeze)
            * 26.10.10.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Unfreeze](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsunfreeze)
        * 26.10.11 [Clear Index](#clear-index)
            * 26.10.11.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearIndex](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsclearindex)
        * 26.10.12 [Fetch](#fetch)
            * 26.10.12.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Fetch](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsfetch)
        * 26.10.13 [Move](#move)
            * 26.10.13.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Move](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsmove)
        * 26.10.14 [Update In](#update-in)
            * 26.10.14.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.UpdateInPartition](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsupdateinpartition)
        * 26.10.15 [Delete In](#delete-in)
            * 26.10.15.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.DeleteInPartition](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsdeleteinpartition)
* 27 [Role Based Access Control](#role-based-access-control)
    * 27.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.RBAC](#rqsrs-032clickhousealtertablereplacepartitionrbac)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE REPLACE PARTITION` in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#replace-partition

## Flowchart

```mermaid
graph TD;
subgraph Replace Partition Flow
  A[Start]
  A -->|1. User Initiates| B(Execute ALTER TABLE REPLACE PARTITION)
  B -->|2. Specify Tables| C{Are table names valid?}
  C -->|Yes| D[Retrieve table schema]
  C -->|No| E[Show error message]
  D -->|3. Validate Structure| F{Same structure in both tables?}
  F -->|No| G[Show error message]
  F -->|Yes| H[Validate Keys]
  H -->|4. Validate Keys| I{Same partition, order by, and primary keys?}
  I -->|No| J[Show error message]
  I -->|Yes| K[Retrieve partition data]
  K -->|5. Replace Partition| L[Update table2 with data from table1]
  L -->|6. Update Metadata| M[Update partition metadata in table2]
  M -->|7. Complete| N[REPLACE PARTITION completed successfully]
  E -->|Error| Z[Handle Error]
  G -->|Error| Z[Handle Error]
  J -->|Error| Z[Handle Error]
  Z --> N
end


```

## Definitions

Source Table - The table from which a partition is taken.
Destination Table - The table in which a specific partition is going to be replaced..


## User Actions

| **Action**                     | **Description**                                                                                                              |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `DETACH PARTITION/PART`        | `ALTER TABLE table_name [ON CLUSTER cluster] DETACH PARTITION/PART partition_expr`                                           |
| `DROP PARTITION/PART`          | `ALTER TABLE table_name [ON CLUSTER cluster] DROP PARTITION/PART partition_expr`                                             |                                          >
| `DROP DETACHED PARTITION/PART` | `ALTER TABLE table_name [ON CLUSTER cluster] DROP DETACHED PARTITION/PART partition_expr`                                    |
| `ATTACH PARTITION/PART`        | `ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION/PART partition_expr`                                           |
| `ATTACH PARTITION FROM`        | `ALTER TABLE table2 [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM table1`                                        |
| `REPLACE PARTITION`            | `ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1`                                       |
| `MOVE PARTITION TO TABLE`      | `ALTER TABLE table_source [ON CLUSTER cluster] MOVE PARTITION partition_expr TO TABLE table_dest`                            |
| `CLEAR COLUMN IN PARTITION`    | `ALTER TABLE table_name [ON CLUSTER cluster] CLEAR COLUMN column_name IN PARTITION partition_expr`                           |
| `FREEZE PARTITION`             | `ALTER TABLE table_name [ON CLUSTER cluster] FREEZE [PARTITION partition_expr] [WITH NAME 'backup_name']`                    |
| `UNFREEZE PARTITION`           | `ALTER TABLE table_name [ON CLUSTER cluster] UNFREEZE [PARTITION 'part_expr'] WITH NAME 'backup_name'`                       |
| `CLEAR INDEX IN PARTITION`     | `ALTER TABLE table_name [ON CLUSTER cluster] CLEAR INDEX index_name IN PARTITION partition_expr`                             |
| `FETCH PARTITION/PART`         | `ALTER TABLE table_name [ON CLUSTER cluster] FETCH PARTITION/PART partition_expr FROM 'path-in-zookeeper'`                   |
| `MOVE PARTITION/PART`          | `ALTER TABLE table_name [ON CLUSTER cluster] MOVE PARTITION/PART partition_expr TO DISK/VOLUME 'disk_name'`                  |
| `UPDATE IN PARTITION`          | `ALTER TABLE [db.]table [ON CLUSTER cluster] UPDATE column1 = expr1 [, ...] [IN PARTITION partition_expr] WHERE filter_expr` |
| `DELETE IN PARTITION`          | `ALTER TABLE [db.]table [ON CLUSTER cluster] DELETE [IN PARTITION partition_expr] WHERE filter_expr`                         |
| `ADD COLUMN`                   | `ALTER TABLE alter_test ADD COLUMN Added1 UInt32 FIRST;`                                                                     |
| `DROP COLUMN`                  | `ALTER TABLE visits DROP COLUMN browser`                                                                                     |
| `CLEAR COLUMN`                 | `ALTER TABLE visits CLEAR COLUMN browser IN PARTITION tuple()`                                                               |
| `MODIFY COLUMN`                | `ALTER COLUMN [IF EXISTS] name TYPE [type] [default_expr] [codec] [TTL] [AFTER name_after]`                                  |
| `MODIFY COLUMN REMOVE`         | `ALTER TABLE table_name MODIFY COLUMN column_name REMOVE property;`                                                          |
| `MATERIALIZE COLUMN`           | `ALTER TABLE [db.]table [ON CLUSTER cluster] MATERIALIZE COLUMN col [IN PARTITION partition];`                               |
| `INSERT INTO TABLE`            | `INSERT INTO [TABLE] [db.]table [(c1, c2, c3)] VALUES (v11, v12, v13), (v21, v22, v23), ...`                                 |
| `DELETE FROM`                  | `DELETE FROM [db.]table [ON CLUSTER cluster] WHERE expr`                                                                     |
| `ATTACH TABLE`                 | `ATTACH TABLE [IF NOT EXISTS] [db.]name [ON CLUSTER cluster] ...`                                                            |
| `DETACH TABLE`                 | `DETACH TABLE [IF EXISTS] [db.]name [ON CLUSTER cluster] [PERMANENTLY] [SYNC]`                                               |
| `DROP TABLE`                   | `DROP [TEMPORARY] TABLE [IF EXISTS] [IF EMPTY] [db.]name [ON CLUSTER cluster] [SYNC]`                                        |
| `KILL QUERY`                   | `KILL QUERY WHERE user='username' SYNC`                                                                                      |
| `RENAME COLUMN`                | `RENAME COLUMN [IF EXISTS] name to new_name`                                                                                 |
| `OPTIMIZE`                     | `OPTIMIZE TABLE [db.]name [ON CLUSTER cluster] [PARTITION partition] [FINAL] [DEDUPLICATE [BY expression]]`                  |

## Replace Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`. The `REPLACE PARTITION` copies the data partition from the `source table` to `destination table` and replaces existing partition in the `destination table`.

For example,

```sql
ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1
```

### Changes In Table Partitions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.System.Parts
version: 1.0

[ClickHouse] SHALL reflect the changes in `system.parts` table, when the `REPLACE PARTITION` is executed on the `destination table`. 

For example,

```sql
SELECT partition, part_types
FROM system.parts
WHERE table = 'table_1'
```

## Keeping Data on the Source Table After Replace Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData
version: 1.0

[ClickHouse] SHALL keep the data of the table from which the partition is copied from.

## Table With Non-Existent Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NonExistentPartition
version: 1.0

[ClickHouse] SHALL keep the data of the destination table when replacing partition form the non-existent partition of a source table.

For example,

If we try to copy the data partition from the `table1` to `table2` and replace existing partition in the `table2` on partition number `21` but this partition does not exist on `table1`.

```sql
ALTER TABLE table2 REPLACE PARTITION 21 FROM table1
```

The data on `table2` should not be deleted and an exception should be raised.

## From Temporary Table

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.FromTemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.

> A table that disappears when the session ends, including if the connection is lost, is considered a temporary table.

For example,

Let's say we have a MergeTree table named `destination`. If we create a temporary table and insert some values into it.

```sql
CREATE TEMPORARY TABLE temporary_table (p UInt64, k String, d UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY k;

INSERT INTO temporary_table VALUES (0, '0', 1);
INSERT INTO temporary_table VALUES (1, '0', 1);
INSERT INTO temporary_table VALUES (1, '1', 1);
INSERT INTO temporary_table VALUES (2, '0', 1);
INSERT INTO temporary_table VALUES (3, '0', 1);
INSERT INTO temporary_table VALUES (3, '1', 1);
```

We can use `REPLACE PARTITION` on the `destinaton` table from `temporary_table`,

```sql
ALTER TABLE destinaton REPLACE PARTITION 1 FROM temporary_table;
```

## From Temporary Table To Temporary Table

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTables
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table into another temporary table.

## Using Into Outfile Clause With Replace Partition Clause

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.IntoOutfile
version: 1.0

[ClickHouse] SHALL support the usage of the `INTO OUTFILE` with `REPLACE PARTITION` and SHALL not output any errors.

## Using The Format Clause With Replace Partition Clause

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Format
version: 1.0

[ClickHouse] SHALL support the usage of the `FORMAT` with `REPLACE PARTITION` and SHALL not output any errors.

## Using Settings With Replace Partition Clause

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Settings
version: 1.0

[ClickHouse] SHALL support the usage of the `SETTINGS` with `REPLACE PARTITION` and SHALL not output any errors.

## Table Is on a Separate Disk

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Disks
version: 1.0

[ClickHouse] SHALL support Replacing partitions from the source table that is on one disk to the destination table that is on another disk.

## Table That Is Stored on S3

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.S3
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions on tables that are stored inside the S3 storage.

## Destination Table That Is on a Different Replica

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Replicas
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions on a destination table that is on a different replica than the source table.

## Destination Table That Is on a Different Shard

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Shards
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions on tables that are on different shards.

## Table That Is Stored on a Server With Different ClickHouse Version

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Versions
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions on tables that are stored on servers with different clickhouse versions.

> Users can create a new database with the target version and use `REPLACE PARTITION` to transfer data from the 
> old database to the new one.

## Table That Has a Different Encoding

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encodings
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions on tables with different encodings.

## Encrypted Tables And Unencrypted Tables

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encryption
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions on encrypted and not encrypted tables.

## Deduplication Tables

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Deduplication
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace data to a deduplication table, where duplicates are identified and eliminated.

## Tables With Different Partition Types

In ClickHouse, a physical file on a disk that stores a portion of the table’s data is called a “part”. There are two types of parts
* `Wide Parts` - Each column is stored in a separate file in a filesystem.
* `Compact Parts` - All columns are stored in one file in a filesystem.

```mermaid
graph LR
    subgraph Part Types
        subgraph Wide
        A1[ClickHouse Table] -->|Partition| B1[Parts]
        B1 --> C1{File system}
        C1 --> |Column| D1[fas:fa-file File1]
        C1 --> |Column| E1[fas:fa-file File2]
        C1 --> |Column| F1[fas:fa-file File3]
        end

        subgraph Compact
        A2[ClickHouse Table] -->|Partition| B2[Parts]
        B2 --> C2{File system}
        C2 --> |All Columns| D2[fas:fa-file File]
        end
    end
```

Data storing format is controlled by the `min_bytes_for_wide_part` and `min_rows_for_wide_part` settings of the `MergeTree` table.

When a specific part is less than the values of `min_bytes_for_wide_part` or `min_rows_for_wide_part`, then it's considered a compact part.


### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionTypes
version: 1.0

The `REPLACE PARTITION` command works with both source and destination tables. Each table can have its own partition type.

| Partition Types                               |
|-----------------------------------------------|
| Partition with only compact parts             |
| Partition with only wide parts                |
| Partition with compact and wide parts (mixed) |
| Partition with no parts                       |
| Partition with empty parts                    |

The `REPLACE PARTITION` SHALL work for any combination of partition types on both destination and source tables.

## Corrupted Parts on a Specific Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted
version: 1.0

[ClickHouse] SHALL output an error when trying to `REPLACE PARTITION` when parts of a specific partition are corrupted for a destination table or a source table.

Possible partition types that can be corrupted are,

| Partition Types                               |
|-----------------------------------------------|
| Partition with compact parts                  |
| Partition with wide parts                     |
| Partition with compact and wide parts (mixed) |

## Conditions

### Rules for Replacing Partitions on Tables

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` only when,

* Both tables have the same structure.
* Both tables have the same partition key, the same `ORDER BY` key, and the same primary key.
* Both tables have the same storage policy.

### Tables With Different Structure

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` when tables have different structure.

### Tables With Different Partition Key

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` when tables have different partition
key, `ORDER BY` key and primary key.

### Tables With Different Storage Policy

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` when tables have different storage
policy.

## Prohibited Actions After From Clause

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited
version: 1.0

[ClickHouse] SHALL only support replacing partition from the table that has partitions. Trying to replace partition from anything else SHALL output an exception. 

### Using Order By and Partition By

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.OrderAndPartition
version: 1.0

[ClickHouse] SHALL output an error when executing `ORDER BY` or `PARTITION BY` with the `REPLACE PARTITION` clause.

### Table Functions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.TableFunctions
version: 1.0

[ClickHouse] SHALL output an error when trying to use table functions after the `FROM` clause to replace partition of a table.

For Example,

```sql
ALTER TABLE table_1 REPLACE PARTITION 2 FROM file(table_2.parquet)
```

The list of possible table functions,

| Table Engines             |
|---------------------------|
| `azureBlobStorage`        |
| `cluster`                 |
| `deltaLake`               |
| `dictionary`              |
| `executable`              |
| `azureBlobStorageCluster` |
| `file`                    |
| `format`                  |
| `gcs`                     |
| `generateRandom`          |
| `hdfs`                    |
| `hdfsCluster`             |
| `hudi`                    |
| `iceberg`                 |
| `input`                   |
| `jdbc`                    |
| `merge`                   |
| `mongodb`                 |
| `mysql`                   |
| `null function`           |
| `numbers`                 |
| `odbc`                    |
| `postgresql`              |
| `redis`                   |
| `remote`                  |
| `s3`                      |
| `s3Cluster`               |
| `sqlite`                  |
| `url`                     |
| `urlCluster`              |
| `view`                    |


### Subquery

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Subquery
version: 1.0

[ClickHouse] SHALL output an error when trying to use subquery after the `FROM` clause to replace partition of a table.

### Join Clause

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Join
version: 1.0

[ClickHouse] SHALL output an error when trying to use the `JOIN` clause after the `FROM` clause to replace partition of a table.

### Replace Partition From Tables That Do Not Have Partitions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.IncorrectTableEngines
version: 1.0

[ClickHouse] SHALL output an error when trying to replace partition on the destination table from the table that does not have partitions.

Table engines that have partitions,

|            Engines             |
|:------------------------------:|
|          `MergeTree`           |
|     `ReplicatedMergeTree`      |
|      `ReplacingMergeTree`      |
|     `AggregatingMergeTree`     |
|     `CollapsingMergeTree`      |
| `VersionedCollapsingMergeTree` |
|      `GraphiteMergeTree`       |
|       `DistributedTable`       |
|       `MaterializedView`       |


## Replacing Partitions During Ongoing Merges and Mutations

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent
version: 1.0

[ClickHouse] SHALL make `REPLACE PARTITION` to wait for the ongoing mutations and partitions if they are running on the same partition as executed `REPLACE PARTITION`.

For example,

If we have two tables `table_1` and `table_2` and we populate them with columns `p` and `i`.

```sql
CREATE TABLE table_1
(
    `p` UInt8,
    `i` UInt64
)
ENGINE = MergeTree
PARTITION BY p
ORDER BY tuple();
```

Run the `INESRT` that will result in two partitions.

```sql
INSERT INTO table_1 VALUES (1, 1), (2, 2);
```

If a lot of merges or mutations happen on partition number one and in the meantime we do `REPLACE PARTITION` on partition number two.

> In this case partition number one is values (1, 1) and number two (2, 2) inside the `table_1`.

```sql
INSERT INTO table_1 (p, i) SELECT 1, number FROM numbers(100);
ALTER TABLE table_1 ADD COLUMN make_merge_slower UInt8 DEFAULT sleepEachRow(0.03);

ALTER TABLE table_1 REPLACE PARTITION id '2' FROM t2;
```

`REPLACE PARTITION` SHALL complete right away since there are no merges happening on this partition at the moment.

### Staring New Merges With Ongoing Replace Partition

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Merges
version: 1.0

[ClickHouse] SHALL output an error when trying to run any merges before the executed `REPLACE PARTITION` is finished.

### Staring New Mutations With Ongoing Replace Partition

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Mutations
version: 1.0

[ClickHouse] SHALL output an error when trying to run any mutations before the executed `REPLACE PARTITION` is finished.

### Insert Into Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Insert
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `INSERT INTO TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Delete Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Delete
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DELETE FROM` is used on, when `REPLACE PARTITION` is executed on this partition.

### Attach Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Attach
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `ATTACH TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Detach Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Detach
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `DETACH TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Optimize Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Optimize
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `OPTIMIZE TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Alter

#### Add Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Add
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `ADD COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Drop Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Drop
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DROP COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Clear Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Clear
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DROP COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Modify Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Modify
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MODIFY COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Modify Column Remove

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.ModifyRemove
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MODIFY COLUMN REMOVE` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Materialize

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Materialize
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MATERIALIZE REMOVE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Manipulating Partitions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish when another operation related to partition manipulation is being executed.

#### Detach

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Detach
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DETACH PARTITION` on the same partition.

#### Drop

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Drop
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DROP PARTITION` on the same partition.

#### Attach

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Attach
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `ATTACH PARTITION` on the same partition.

#### Attach From

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.AttachFrom
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `ATTACH PARTITION FROM` on the same partition.

#### Replace

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Replace
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing another `REPLACE PARTITION` on the same partition.

For example,

> If we run `REPLACE PARTITION` to replace the data partition from the `table1` to `table2` and replaces existing partition in the `table2`, 
> but at the same time try to replace partition of another table from `table2`, the first process should finish and only after that the second `REPLACE PARTITION` SHALL be executed.

#### Move To Table

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.MoveToTable
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `MOVE PARTITION TO TABLE` on the same partition.

#### Clear Column In Partition

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearColumnInPartition
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `CLEAR COLUMN IN PARTITION` on the same partition.

#### Freeze

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Freeze
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `FREEZE PARTITION` on the same partition.

#### Unfreeze

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Unfreeze
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `UNFREEZE PARTITION` on the same partition.

#### Clear Index

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearIndex
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `CLEAR INDEX IN PARTITION` on the same partition.

#### Fetch

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Fetch
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `FETCH PARTITION` on the same partition.

#### Move

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Move
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `MOVE PARTITION` on the same partition.

#### Update In

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.UpdateInPartition
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `UPDATE IN PARTITION` on the same partition.

#### Delete In

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.DeleteInPartition
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DELETE IN PARTITION` on the same partition.


## Role Based Access Control

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.RBAC
version: 1.0

The `REPLACE PARTITION` command works with both source and destination tables. Each table can have its own privileges.

```sql
ALTER TABLE table2 REPLACE PARTITION 21 FROM table1
```

| Privileges     |
|----------------|
| No privileges  |
| SELECT         |
| INSERT         |
| ALTER          |
| ALTER TABLE    |


The `REPLACE PARTITION` SHALL only work when the user has the following privileges for the source and destination tables:

| Source | Destination          |
|--------|----------------------|
| SELECT | ALTER DELETE, INSERT |
| SELECT | ALTER, INSERT        |

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com

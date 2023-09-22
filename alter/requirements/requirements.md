# SRS032 ClickHouse Alter statement
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Working with ALTER statement](#working-with-alter-statement)
  * 3.1 [REPLACE PARTITION](#replace-partition)
    * 3.1.1 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition](#rqsrs-032clickhousealterreplacepartition)
    * 3.1.2 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.ReplaceData](#rqsrs-032clickhousealterreplacepartitionreplacedata)
    * 3.1.3 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.NewData](#rqsrs-032clickhousealterreplacepartitionnewdata)
    * 3.1.4 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.StorageEngine](#rqsrs-032clickhousealterreplacepartitionstorageengine)
    * 3.1.5 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.PartitionKey](#rqsrs-032clickhousealterreplacepartitionpartitionkey)
    * 3.1.6 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.MultiplePartitions](#rqsrs-032clickhousealterreplacepartitionmultiplepartitions)
    * 3.1.7 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.KeepTable](#rqsrs-032clickhousealterreplacepartitionaddnewpartitionkeeptable)
    * 3.1.8 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.TemporaryTable](#rqsrs-032clickhousealterreplacepartitionaddnewpartitiontemporarytable)
    * 3.1.9 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.Conditions](#rqsrs-032clickhousealterreplacepartitionaddnewpartitionconditions)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER` statement in [ClickHouse].

The documentation used:
- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#replace-partition

## Working with ALTER statement

[ClickHouse] SHALL support the usage of the `ALTER` statement.

### REPLACE PARTITION

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`.

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.ReplaceData
version: 1.0

[ClickHouse] SHALL support the ability to add a new partition to a table, replacing an existing one.

For example,

This query copies the data partition from the `table1` to `table2` and replaces existing partition in the `table2`.

```sql
ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1
```

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.NewData
version: 1.0

[ClickHouse] SHALL support replace an existing partition with new data using `ATTACH`.

For example,
```sql
ALTER TABLE my_table REPLACE PARTITION 202301 WITH ATTACH 'path_to_new_data';
```

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.StorageEngine
version: 1.0

[ClickHouse] SHALL support replacing the storage engine used for a specific partition.

For example,
```sql
ALTER TABLE my_table REPLACE PARTITION 202302
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_id);
```

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.PartitionKey
version: 1.0

[ClickHouse] SHALL support replacing the partitioning key for a specific partition.

For example,
```sql
ALTER TABLE my_table REPLACE PARTITION 202303
PARTITION BY toYYYY(event_date)
ORDER BY (event_date, event_id);
```

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.MultiplePartitions
version: 1.0

[ClickHouse] SHALL support replacing multiple partitions with new data or different configurations in a single command.

For example,
```sql
ALTER TABLE my_table REPLACE PARTITION 202305, 202306, 202307
WITH ATTACH 'path_to_new_data';
```

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.KeepTable
version: 1.0

[ClickHouse] SHALL keep the data of the table from which the partition is copied from.

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.TemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` when,

* Both Table have the same structure.
* Both tables have the same partition key, the same `ORDER BY` key and the same primary key.
* Both tables must have the same storage policy.



[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com

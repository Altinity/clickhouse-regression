# SRS032 ClickHouse Alter statement
# Software Requirements Specification

## Table of Contents

* 1 [Working with ALTER statement](#working-with-alter-statement)
  * 1.1 [RQ.SRS-032.ClickHouse.Alter](#rqsrs-032clickhousealter)
  * 1.2 [REPLACE PARTITION](#replace-partition)
    * 1.2.1 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition](#rqsrs-032clickhousealterreplacepartition)
    * 1.2.2 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition](#rqsrs-032clickhousealterreplacepartitionaddnewpartition)
    * 1.2.3 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.KeepTable](#rqsrs-032clickhousealterreplacepartitionaddnewpartitionkeeptable)
    * 1.2.4 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.TemporaryTable](#rqsrs-032clickhousealterreplacepartitionaddnewpartitiontemporarytable)
    * 1.2.5 [RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.Conditions](#rqsrs-032clickhousealterreplacepartitionaddnewpartitionconditions)



## Working with ALTER statement

### RQ.SRS-032.ClickHouse.Alter
version: 1.0

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

#### RQ.SRS-032.ClickHouse.Alter.ReplacePartition.AddNewPartition.NewData
version: 1.0

[ClickHouse] SHALL support replace an existing partition with new data.

For example,
```sql
ALTER TABLE my_table REPLACE PARTITION 202301 WITH ATTACH 'path_to_new_data';
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

# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230315.1003122.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`.\n" "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the ability to add a new partition to a table, replacing an existing one.\n"
        "\n"
        "For example,\n"
        "\n"
        "This query copies the data partition from the `table1` to `table2` and replaces existing partition in the `table2`.\n"
        "\n"
        "```sql\n"
        "ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.2.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `REPLACE PARTITION` between two tables when,\n"
        "\n"
        "* Both Table have the same structure.\n"
        "* Both tables have the same partition key, the same `ORDER BY` key and the same primary key.\n"
        "* Both tables must have the same storage policy.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.1.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_KeepTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.KeepTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep the data of the table from which the partition is copied from.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.1.2",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_TemporaryTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support copying the data partition from the temporary table.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.1.3",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Structure = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different structure.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.2.1.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Key = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different partition key, `ORDER BY` key andprimary key.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.2.1.4.2",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_StoragePolicy = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different storage policy.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=5,
    num="3.2.1.4.3",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NewData = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NewData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support replace an existing partition with new data using `ATTACH`.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202301 WITH ATTACH 'path_to_new_data';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.3.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_StorageEngine = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.StorageEngine",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support replacing the storage engine used for a specific partition.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202302\n"
        "ENGINE = MergeTree()\n"
        "PARTITION BY toYYYYMM(event_date)\n"
        "ORDER BY (event_date, event_id);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionKey = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support replacing the partitioning key for a specific partition.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202303\n"
        "PARTITION BY toYYYY(event_date)\n"
        "ORDER BY (event_date, event_id);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="3.5.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_MultiplePartitions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MultiplePartitions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support replacing multiple partitions with new data or different configurations in a single command.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202305, 202306, 202307\n"
        "WITH ATTACH 'path_to_new_data';\n"
        "```\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=3,
    num="3.6.1",
)

SRS032_ClickHouse_Alter_Table_statement = Specification(
    name="SRS032 ClickHouse Alter Table statement",
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Revision History", level=1, num="1"),
        Heading(name="Introduction", level=1, num="2"),
        Heading(name="REPLACE PARTITION", level=1, num="3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition",
            level=2,
            num="3.1",
        ),
        Heading(name="Replace Partition Between Tables", level=2, num="3.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData",
            level=3,
            num="3.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions",
            level=4,
            num="3.2.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.KeepTable",
            level=4,
            num="3.2.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable",
            level=4,
            num="3.2.1.3",
        ),
        Heading(name="Conditions Not Satisfied", level=4, num="3.2.1.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure",
            level=5,
            num="3.2.1.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key",
            level=5,
            num="3.2.1.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy",
            level=5,
            num="3.2.1.4.3",
        ),
        Heading(name="New Data", level=2, num="3.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NewData",
            level=3,
            num="3.3.1",
        ),
        Heading(name="Storage Engine", level=2, num="3.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.StorageEngine",
            level=3,
            num="3.4.1",
        ),
        Heading(name="Partition Key", level=2, num="3.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionKey",
            level=3,
            num="3.5.1",
        ),
        Heading(name="Replace Multiple Partitions", level=2, num="3.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MultiplePartitions",
            level=3,
            num="3.6.1",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_KeepTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_TemporaryTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Structure,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Key,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_StoragePolicy,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NewData,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_StorageEngine,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionKey,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_MultiplePartitions,
    ),
    content="""
# SRS032 ClickHouse Alter Table statement
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [REPLACE PARTITION](#replace-partition)
  * 3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition](#rqsrs-032clickhousealtertablereplacepartition)
  * 3.2 [Replace Partition Between Tables](#replace-partition-between-tables)
    * 3.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData](#rqsrs-032clickhousealtertablereplacepartitionreplacedata)
      * 3.2.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditions)
      * 3.2.1.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.KeepTable](#rqsrs-032clickhousealtertablereplacepartitionreplacedatakeeptable)
      * 3.2.1.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable](#rqsrs-032clickhousealtertablereplacepartitionreplacedatatemporarytable)
      * 3.2.1.4 [Conditions Not Satisfied](#conditions-not-satisfied)
        * 3.2.1.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstructure)
        * 3.2.1.4.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentkey)
        * 3.2.1.4.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstoragepolicy)
  * 3.3 [New Data](#new-data)
    * 3.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NewData](#rqsrs-032clickhousealtertablereplacepartitionnewdata)
  * 3.4 [Storage Engine](#storage-engine)
    * 3.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.StorageEngine](#rqsrs-032clickhousealtertablereplacepartitionstorageengine)
  * 3.5 [Partition Key](#partition-key)
    * 3.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionKey](#rqsrs-032clickhousealtertablereplacepartitionpartitionkey)
  * 3.6 [Replace Multiple Partitions](#replace-multiple-partitions)
    * 3.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MultiplePartitions](#rqsrs-032clickhousealtertablereplacepartitionmultiplepartitions)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE` statement in [ClickHouse].

The documentation used:
- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#replace-partition

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

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different partition key, `ORDER BY` key andprimary key.

###### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different storage policy.


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
""",
)

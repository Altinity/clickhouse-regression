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
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`.\n"
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
    level=2,
    num="6.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_KeepData = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData",
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
    level=2,
    num="6.2",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support copying the data partition from the temporary table.\n"
        "\n"
        "For example,\n"
        "\n"
        "A table that disappears when the session ends, including if the connection is lost, is considered a temporary table. To create such a table the following query can be run.\n"
        "\n"
        "```sql\n"
        "CREATE TEMPORARY TABLE [IF NOT EXISTS] table_name\n"
        "(\n"
        "    name1 [type1] [DEFAULT|MATERIALIZED|ALIAS expr1],\n"
        "    name2 [type2] [DEFAULT|MATERIALIZED|ALIAS expr2],\n"
        "    ...\n"
        ") [ENGINE = engine]\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.3",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `REPLACE PARTITION` between two tables only when,\n"
        "\n"
        "* Both tables have the same structure.\n"
        "* Both tables have the same partition key, the same `ORDER BY` key, and the same primary key.\n"
        "* Both tables have the same storage policy.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Structure = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure",
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
    level=2,
    num="7.2",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Key = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different partition\n"
        "key, `ORDER BY` key and primary key.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.3",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_StoragePolicy = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different storage\n"
        "policy.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.4",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TableEngines = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TableEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `REPLACE PARTITION` for the following table engines,\n"
        "\n"
        "| Engines                        |\n"
        "|--------------------------------|\n"
        "| `MergeTree`                    |\n"
        "| `ReplicatedMergeTree`          |\n"
        "| `ReplacingMergeTree`           |\n"
        "| `AggregatingMergeTree`         |\n"
        "| `CollapsingMergeTree`          |\n"
        "| `VersionedCollapsingMergeTree` |\n"
        "| `GraphiteMergeTree`            |\n"
        "| `DistributedTable`             |\n"
        "| `MaterializedView`             |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support concurrent merges/mutations that happen on the same partition at the same time.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_MergesAndMutations = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL cancel only for mutations/merges that are scheduled/already operating on target partition. \n"
        "And wait ONLY for those cancelled merges/mutations (on target partition) to wrap up.\n"
        "\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md\n"
        "\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md\n"
        "\n"
        "[Git]: https://git-scm.com/\n"
        "\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=2,
    num="9.2",
)

SRS032_ClickHouse_Alter_Table_Replace_Partition = Specification(
    name="SRS032 ClickHouse Alter Table Replace Partition",
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
        Heading(name="Software Requirements Specification", level=0, num=""),
        Heading(name="Table of Contents", level=1, num="1"),
        Heading(name="Revision History", level=1, num="2"),
        Heading(name="Introduction", level=1, num="3"),
        Heading(name="Flowchart", level=1, num="4"),
        Heading(name="User Actions", level=1, num="5"),
        Heading(name="Replace Partition", level=1, num="6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition",
            level=2,
            num="6.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData",
            level=2,
            num="6.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTable",
            level=2,
            num="6.3",
        ),
        Heading(name="Conditions", level=1, num="7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions",
            level=2,
            num="7.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure",
            level=2,
            num="7.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key",
            level=2,
            num="7.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy",
            level=2,
            num="7.4",
        ),
        Heading(name="Table Engines", level=1, num="8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TableEngines",
            level=2,
            num="8.1",
        ),
        Heading(name="Concurrent Actions", level=1, num="9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent",
            level=2,
            num="9.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations",
            level=2,
            num="9.2",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_KeepData,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Structure,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Key,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_StoragePolicy,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TableEngines,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_MergesAndMutations,
    ),
    content="""
# SRS032 ClickHouse Alter Table Replace Partition

# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Flowchart](#flowchart)
* 4 [User Actions](#user-actions)
* 5 [Replace Partition](#replace-partition)
  * 5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition](#rqsrs-032clickhousealtertablereplacepartition)
  * 5.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData](#rqsrs-032clickhousealtertablereplacepartitionkeepdata)
  * 5.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTable](#rqsrs-032clickhousealtertablereplacepartitiontemporarytable)
* 6 [Conditions](#conditions)
  * 6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions](#rqsrs-032clickhousealtertablereplacepartitionconditions)
  * 6.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentstructure)
  * 6.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentkey)
  * 6.4 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentstoragepolicy)
* 7 [Table Engines](#table-engines)
  * 7.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TableEngines](#rqsrs-032clickhousealtertablereplacepartitiontableengines)
* 8 [Concurrent Actions](#concurrent-actions)
  * 8.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent](#rqsrs-032clickhousealtertablereplacepartitionconcurrent)
  * 8.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations](#rqsrs-032clickhousealtertablereplacepartitionmergesandmutations)

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

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION`.

For example,

This query copies the data partition from the `table1` to `table2` and replaces existing partition in the `table2`.

```sql
ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1
```

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData
version: 1.0

[ClickHouse] SHALL keep the data of the table from which the partition is copied from.

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.

For example,

A table that disappears when the session ends, including if the connection is lost, is considered a temporary table. To create such a table the following query can be run.

```sql
CREATE TEMPORARY TABLE [IF NOT EXISTS] table_name
(
    name1 [type1] [DEFAULT|MATERIALIZED|ALIAS expr1],
    name2 [type2] [DEFAULT|MATERIALIZED|ALIAS expr2],
    ...
) [ENGINE = engine]
```

## Conditions

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` between two tables only when,

* Both tables have the same structure.
* Both tables have the same partition key, the same `ORDER BY` key, and the same primary key.
* Both tables have the same storage policy.

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different structure.

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different partition
key, `ORDER BY` key and primary key.

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different storage
policy.

## Table Engines

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TableEngines
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` for the following table engines,

| Engines                        |
|--------------------------------|
| `MergeTree`                    |
| `ReplicatedMergeTree`          |
| `ReplacingMergeTree`           |
| `AggregatingMergeTree`         |
| `CollapsingMergeTree`          |
| `VersionedCollapsingMergeTree` |
| `GraphiteMergeTree`            |
| `DistributedTable`             |
| `MaterializedView`             |


## Concurrent Actions

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent
version: 1.0

[ClickHouse] SHALL support concurrent merges/mutations that happen on the same partition at the same time.


### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations
version: 1.0

[ClickHouse] SHALL cancel only for mutations/merges that are scheduled/already operating on target partition. 
And wait ONLY for those cancelled merges/mutations (on target partition) to wrap up.



[ClickHouse]: https://clickhouse.com

[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md

[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md

[Git]: https://git-scm.com/

[GitHub]: https://github.com
""",
)

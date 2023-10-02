# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230315.1003122.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_UserActions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.UserActions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| **Action**                     | **Description**                                                                                                              |\n"
        "|--------------------------------|------------------------------------------------------------------------------------------------------------------------------|\n"
        "| `DETACH PARTITION/PART`        | `ALTER TABLE table_name [ON CLUSTER cluster] DETACH PARTITION/PART partition_expr`                                           |\n"
        "| `DROP PARTITION/PART`          | `ALTER TABLE table_name [ON CLUSTER cluster] DROP PARTITION/PART partition_expr`                                             |                                          >\n"
        "| `DROP DETACHED PARTITION/PART` | `ALTER TABLE table_name [ON CLUSTER cluster] DROP DETACHED PARTITION/PART partition_expr`                                    |\n"
        "| `ATTACH PARTITION/PART`        | `ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION/PART partition_expr`                                           |\n"
        "| `ATTACH PARTITION FROM`        | `ALTER TABLE table2 [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM table1`                                        |\n"
        "| `REPLACE PARTITION`            | `ALTER TABLE table2 [ON CLUSTER cluster] REPLACE PARTITION partition_expr FROM table1`                                       |\n"
        "| `MOVE PARTITION TO TABLE`      | `ALTER TABLE table_source [ON CLUSTER cluster] MOVE PARTITION partition_expr TO TABLE table_dest`                            |\n"
        "| `CLEAR COLUMN IN PARTITION`    | `ALTER TABLE table_name [ON CLUSTER cluster] CLEAR COLUMN column_name IN PARTITION partition_expr`                           |\n"
        "| `FREEZE PARTITION`             | `ALTER TABLE table_name [ON CLUSTER cluster] FREEZE [PARTITION partition_expr] [WITH NAME 'backup_name']`                    |\n"
        "| `UNFREEZE PARTITION`           | `ALTER TABLE table_name [ON CLUSTER cluster] UNFREEZE [PARTITION 'part_expr'] WITH NAME 'backup_name'`                       |\n"
        "| `CLEAR INDEX IN PARTITION`     | `ALTER TABLE table_name [ON CLUSTER cluster] CLEAR INDEX index_name IN PARTITION partition_expr`                             |\n"
        "| `FETCH PARTITION/PART`         | `ALTER TABLE table_name [ON CLUSTER cluster] FETCH PARTITION/PART partition_expr FROM 'path-in-zookeeper'`                   |\n"
        "| `MOVE PARTITION/PART`          | `ALTER TABLE table_name [ON CLUSTER cluster] MOVE PARTITION/PART partition_expr TO DISK/VOLUME 'disk_name'`                  |\n"
        "| `UPDATE IN PARTITION`          | `ALTER TABLE [db.]table [ON CLUSTER cluster] UPDATE column1 = expr1 [, ...] [IN PARTITION partition_expr] WHERE filter_expr` |\n"
        "| `DELETE IN PARTITION`          | `ALTER TABLE [db.]table [ON CLUSTER cluster] DELETE [IN PARTITION partition_expr] WHERE filter_expr`                         |\n"
        "| `INSERT INTO TABLE`            | ``                                                                                                                           |\n"
        "| `DELETE FROM`                  | ``                                                                                                                           |\n"
        "| `ATTACH TABLE`                 | ``                                                                                                                           |\n"
        "| `DETACH TABLE`                 | ``                                                                                                                           |\n"
        "| `DROP TABLE`                   | ``                                                                                                                           |\n"
        "| `KILL QUERY`                   | ``                                                                                                                           |\n"
        "| `ADD COLUMN`                   | ``                                                                                                                           |\n"
        "| `DROP COLUMN`                  | ``                                                                                                                           |\n"
        "| `RENAME COLUMN`                | ``                                                                                                                           |\n"
        "| `CLEAR COLUMN`                 | ``                                                                                                                           |\n"
        "| `MODIFY COLUMN`                | ``                                                                                                                           |\n"
        "| `MODIFY COLUMN REMOVE`         | ``                                                                                                                           |\n"
        "| `MATERIALIZE COLUMN`           | ``                                                                                                                           |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

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
    num="4.3",
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
    num="4.4.1",
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
    num="4.4.1.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartitionDistributedTable_ReplaceData_KeepTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartitionDistributedTable.ReplaceData.KeepTable",
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
    num="4.4.1.2",
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
    num="4.4.1.3",
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
    num="4.4.1.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Key = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key",
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
    level=5,
    num="4.4.1.4.2",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_StoragePolicy = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy",
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
    level=5,
    num="4.4.1.4.3",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_MergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `MergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_ReplicatedMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplicatedMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `ReplicatedMergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.2",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_ReplacingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplacingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `ReplacingMergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.3",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_AggregatingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.AggregatingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `AggregatingMergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.4",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_CollapsingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.CollapsingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `CollapsingMergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.5",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_VersionedCollapsingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.VersionedCollapsingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `VersionedCollapsingMergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.6",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_GraphiteMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.GraphiteMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `GraphiteMergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.1.7",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_DistributedTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.DistributedTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `DistributedTable` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.2.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_MaterializedView = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MaterializedView",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `MaterializedView` engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.5.3.1",
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
    level=3,
    num="4.6.1",
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
    level=3,
    num="4.6.2",
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
        Heading(name="REPLACE PARTITION", level=1, num="4"),
        Heading(name="Flowchart", level=2, num="4.1"),
        Heading(name="User Actions", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.UserActions",
            level=3,
            num="4.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition",
            level=2,
            num="4.3",
        ),
        Heading(name="Replace Partition Between Tables", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData",
            level=3,
            num="4.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions",
            level=4,
            num="4.4.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartitionDistributedTable.ReplaceData.KeepTable",
            level=4,
            num="4.4.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable",
            level=4,
            num="4.4.1.3",
        ),
        Heading(name="Conditions Not Satisfied", level=4, num="4.4.1.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure",
            level=5,
            num="4.4.1.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key",
            level=5,
            num="4.4.1.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy",
            level=5,
            num="4.4.1.4.3",
        ),
        Heading(name="Table Engines", level=2, num="4.5"),
        Heading(name="MergeTree", level=3, num="4.5.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MergeTree",
            level=4,
            num="4.5.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplicatedMergeTree",
            level=4,
            num="4.5.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplacingMergeTree",
            level=4,
            num="4.5.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.AggregatingMergeTree",
            level=4,
            num="4.5.1.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.CollapsingMergeTree",
            level=4,
            num="4.5.1.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.VersionedCollapsingMergeTree",
            level=4,
            num="4.5.1.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.GraphiteMergeTree",
            level=4,
            num="4.5.1.7",
        ),
        Heading(name="DistributedTable", level=3, num="4.5.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.DistributedTable",
            level=4,
            num="4.5.2.1",
        ),
        Heading(name="MaterializedView", level=3, num="4.5.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MaterializedView",
            level=4,
            num="4.5.3.1",
        ),
        Heading(name="Concurrent Actions", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent",
            level=3,
            num="4.6.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations",
            level=3,
            num="4.6.2",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_UserActions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartitionDistributedTable_ReplaceData_KeepTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_TemporaryTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Structure,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Key,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_StoragePolicy,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_MergeTree,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_ReplicatedMergeTree,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_ReplacingMergeTree,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_AggregatingMergeTree,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_CollapsingMergeTree,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_VersionedCollapsingMergeTree,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_GraphiteMergeTree,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_DistributedTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ZooKeeper_TableEngines_MaterializedView,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_MergesAndMutations,
    ),
    content="""
# SRS032 ClickHouse Alter Table Replace Partition

# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [REPLACE PARTITION](#replace-partition)
  * 3.1 [Flowchart](#flowchart)
  * 3.2 [User Actions](#user-actions)
    * 3.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.UserActions](#rqsrs-032clickhousealtertablereplacepartitionuseractions)
  * 3.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition](#rqsrs-032clickhousealtertablereplacepartition)
  * 3.4 [Replace Partition Between Tables](#replace-partition-between-tables)
    * 3.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData](#rqsrs-032clickhousealtertablereplacepartitionreplacedata)
      * 3.4.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditions)
      * 3.4.1.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartitionDistributedTable.ReplaceData.KeepTable](#rqsrs-032clickhousealtertablereplacepartitiondistributedtablereplacedatakeeptable)
      * 3.4.1.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable](#rqsrs-032clickhousealtertablereplacepartitionreplacedatatemporarytable)
      * 3.4.1.4 [Conditions Not Satisfied](#conditions-not-satisfied)
        * 3.4.1.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstructure)
        * 3.4.1.4.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentkey)
        * 3.4.1.4.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstoragepolicy)
  * 3.5 [Table Engines](#table-engines)
    * 3.5.1 [MergeTree](#mergetree)
      * 3.5.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesmergetree)
      * 3.5.1.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplicatedMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesreplicatedmergetree)
      * 3.5.1.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplacingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesreplacingmergetree)
      * 3.5.1.4 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.AggregatingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesaggregatingmergetree)
      * 3.5.1.5 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.CollapsingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginescollapsingmergetree)
      * 3.5.1.6 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.VersionedCollapsingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesversionedcollapsingmergetree)
      * 3.5.1.7 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.GraphiteMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesgraphitemergetree)
    * 3.5.2 [DistributedTable](#distributedtable)
      * 3.5.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.DistributedTable](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesdistributedtable)
    * 3.5.3 [MaterializedView](#materializedview)
      * 3.5.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MaterializedView](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesmaterializedview)
  * 3.6 [Concurrent Actions](#concurrent-actions)
    * 3.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent](#rqsrs-032clickhousealtertablereplacepartitionconcurrent)
    * 3.6.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations](#rqsrs-032clickhousealtertablereplacepartitionmergesandmutations)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE` statement in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#replace-partition

## REPLACE PARTITION

### Flowchart

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

### User Actions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.UserActions
version: 1.0


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
| `INSERT INTO TABLE`            | ``                                                                                                                           |
| `DELETE FROM`                  | ``                                                                                                                           |
| `ATTACH TABLE`                 | ``                                                                                                                           |
| `DETACH TABLE`                 | ``                                                                                                                           |
| `DROP TABLE`                   | ``                                                                                                                           |
| `KILL QUERY`                   | ``                                                                                                                           |
| `ADD COLUMN`                   | ``                                                                                                                           |
| `DROP COLUMN`                  | ``                                                                                                                           |
| `RENAME COLUMN`                | ``                                                                                                                           |
| `CLEAR COLUMN`                 | ``                                                                                                                           |
| `MODIFY COLUMN`                | ``                                                                                                                           |
| `MODIFY COLUMN REMOVE`         | ``                                                                                                                           |
| `MATERIALIZE COLUMN`           | ``                                                                                                                           |

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

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartitionDistributedTable.ReplaceData.KeepTable
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
key, `ORDER BY` key and primary key.

###### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different storage
policy.

### Table Engines

#### MergeTree

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MergeTree
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `MergeTree` engine.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `ReplicatedMergeTree` engine.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `ReplacingMergeTree` engine.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.AggregatingMergeTree
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `AggregatingMergeTree` engine.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.CollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `CollapsingMergeTree` engine.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.VersionedCollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `VersionedCollapsingMergeTree` engine.

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.GraphiteMergeTree
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `GraphiteMergeTree` engine.

#### DistributedTable

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.DistributedTable
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `DistributedTable` engine.

#### MaterializedView

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MaterializedView
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `MaterializedView` engine.

### Concurrent Actions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent
version: 1.0

[ClickHouse] SHALL support concurrent merges/mutations that happen on the same partition at the same time.


#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations
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

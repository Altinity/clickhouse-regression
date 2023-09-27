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
    num="5.2",
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
    num="5.3.1",
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
    num="5.3.1.1",
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
    num="5.3.1.2",
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
    num="5.3.1.3",
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
    num="5.3.1.4.1",
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
    num="5.3.1.4.2",
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
    num="5.3.1.4.3",
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
        "\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202301 WITH ATTACH 'path_to_new_data';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.4.1",
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
        "\n"
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
    num="5.5.1",
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
        "\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202303\n"
        "PARTITION BY toYYYY(event_date)\n"
        "ORDER BY (event_date, event_id);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.6.1",
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
        "\n"
        "```sql\n"
        "ALTER TABLE my_table REPLACE PARTITION 202305, 202306, 202307\n"
        "WITH ATTACH 'path_to_new_data';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.7.1",
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
    num="5.8.1.1",
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
    num="5.8.1.2",
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
    num="5.8.1.3",
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
    num="5.8.1.4",
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
    num="5.8.1.5",
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
    num="5.8.1.6",
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
    num="5.8.1.7",
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
    num="5.8.1.8",
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
    num="5.8.1.9",
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
    num="5.9.1",
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
    num="5.9.2",
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
        Heading(name="Software Requirements Specification", level=0, num=""),
        Heading(name="Table of Contents", level=1, num="1"),
        Heading(name="Revision History", level=1, num="2"),
        Heading(name="Introduction", level=1, num="3"),
        Heading(name="User Actions", level=1, num="4"),
        Heading(name="REPLACE PARTITION", level=1, num="5"),
        Heading(name="Flowchart", level=2, num="5.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition",
            level=2,
            num="5.2",
        ),
        Heading(name="Replace Partition Between Tables", level=2, num="5.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData",
            level=3,
            num="5.3.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions",
            level=4,
            num="5.3.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartitionDistributedTable.ReplaceData.KeepTable",
            level=4,
            num="5.3.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable",
            level=4,
            num="5.3.1.3",
        ),
        Heading(name="Conditions Not Satisfied", level=4, num="5.3.1.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure",
            level=5,
            num="5.3.1.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key",
            level=5,
            num="5.3.1.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy",
            level=5,
            num="5.3.1.4.3",
        ),
        Heading(name="New Data", level=2, num="5.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NewData",
            level=3,
            num="5.4.1",
        ),
        Heading(name="Storage Engine", level=2, num="5.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.StorageEngine",
            level=3,
            num="5.5.1",
        ),
        Heading(name="Partition Key", level=2, num="5.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionKey",
            level=3,
            num="5.6.1",
        ),
        Heading(name="Replace Multiple Partitions", level=2, num="5.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MultiplePartitions",
            level=3,
            num="5.7.1",
        ),
        Heading(name="ZooKeeper", level=2, num="5.8"),
        Heading(name="Table Engines", level=3, num="5.8.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MergeTree",
            level=4,
            num="5.8.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplicatedMergeTree",
            level=4,
            num="5.8.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplacingMergeTree",
            level=4,
            num="5.8.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.AggregatingMergeTree",
            level=4,
            num="5.8.1.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.CollapsingMergeTree",
            level=4,
            num="5.8.1.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.VersionedCollapsingMergeTree",
            level=4,
            num="5.8.1.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.GraphiteMergeTree",
            level=4,
            num="5.8.1.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.DistributedTable",
            level=4,
            num="5.8.1.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MaterializedView",
            level=4,
            num="5.8.1.9",
        ),
        Heading(name="Concurrent Actions", level=2, num="5.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent",
            level=3,
            num="5.9.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations",
            level=3,
            num="5.9.2",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartitionDistributedTable_ReplaceData_KeepTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_TemporaryTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Structure,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_Key,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ReplaceData_Conditions_Different_StoragePolicy,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NewData,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_StorageEngine,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionKey,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_MultiplePartitions,
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
# SRS032 ClickHouse Alter Table statement

# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [User Actions](#user-actions)
* 4 [REPLACE PARTITION](#replace-partition)
  * 4.1 [Flowchart](#flowchart)
  * 4.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition](#rqsrs-032clickhousealtertablereplacepartition)
  * 4.3 [Replace Partition Between Tables](#replace-partition-between-tables)
    * 4.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData](#rqsrs-032clickhousealtertablereplacepartitionreplacedata)
      * 4.3.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditions)
      * 4.3.1.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartitionDistributedTable.ReplaceData.KeepTable](#rqsrs-032clickhousealtertablereplacepartitiondistributedtablereplacedatakeeptable)
      * 4.3.1.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.TemporaryTable](#rqsrs-032clickhousealtertablereplacepartitionreplacedatatemporarytable)
      * 4.3.1.4 [Conditions Not Satisfied](#conditions-not-satisfied)
        * 4.3.1.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Structure](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstructure)
        * 4.3.1.4.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.Key](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentkey)
        * 4.3.1.4.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ReplaceData.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertablereplacepartitionreplacedataconditionsdifferentstoragepolicy)
  * 4.4 [New Data](#new-data)
    * 4.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NewData](#rqsrs-032clickhousealtertablereplacepartitionnewdata)
  * 4.5 [Storage Engine](#storage-engine)
    * 4.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.StorageEngine](#rqsrs-032clickhousealtertablereplacepartitionstorageengine)
  * 4.6 [Partition Key](#partition-key)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionKey](#rqsrs-032clickhousealtertablereplacepartitionpartitionkey)
  * 4.7 [Replace Multiple Partitions](#replace-multiple-partitions)
    * 4.7.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MultiplePartitions](#rqsrs-032clickhousealtertablereplacepartitionmultiplepartitions)
  * 4.8 [ZooKeeper](#zookeeper)
    * 4.8.1 [Table Engines](#table-engines)
      * 4.8.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesmergetree)
      * 4.8.1.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplicatedMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesreplicatedmergetree)
      * 4.8.1.3 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.ReplacingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesreplacingmergetree)
      * 4.8.1.4 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.AggregatingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesaggregatingmergetree)
      * 4.8.1.5 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.CollapsingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginescollapsingmergetree)
      * 4.8.1.6 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.VersionedCollapsingMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesversionedcollapsingmergetree)
      * 4.8.1.7 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.GraphiteMergeTree](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesgraphitemergetree)
      * 4.8.1.8 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.DistributedTable](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesdistributedtable)
      * 4.8.1.9 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.MaterializedView](#rqsrs-032clickhousealtertablereplacepartitionzookeepertableenginesmaterializedview)
  * 4.9 [Concurrent Actions](#concurrent-actions)
    * 4.9.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent](#rqsrs-032clickhousealtertablereplacepartitionconcurrent)
    * 4.9.2 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.MergesAndMutations](#rqsrs-032clickhousealtertablereplacepartitionmergesandmutations)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `ALTER TABLE` statement in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#replace-partition
 
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

### ZooKeeper

#### Table Engines

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

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.ZooKeeper.TableEngines.DistributedTable
version: 1.0

[ClickHouse] SHALL support the usage of the `REPLACE PARTITION` on the table with `DistributedTable` engine.

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

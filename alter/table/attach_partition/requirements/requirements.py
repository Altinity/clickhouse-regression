# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.231023.1135725.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_SupportedTableEngines = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following table engines for the `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements:\n"
        "\n"
        "|       Supported Engines        |\n"
        "|:------------------------------:|\n"
        "|          `MergeTree`           | \n"
        "|      `ReplacingMergeTree`      |\n"
        "|     `AggregatingMergeTree`     |\n"
        "|     `CollapsingMergeTree`      |\n"
        "| `VersionedCollapsingMergeTree` |\n"
        "|      `GraphiteMergeTree`       |\n"
        "|      `SummingMergeTree`        |\n"
        "\n"
        "and their `Replicated` versions.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_S3 = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements with tables that are stored inside the S3 storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="6.1.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TieredStorage = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TieredStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements with tables that are stored inside the tiered storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="6.2.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartitionTypes = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartitionTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Partition Types                                   |\n"
        "|---------------------------------------------------|\n"
        "| Partition with only [compact] parts               |\n"
        "| Partition with only [wide] parts                  |\n"
        "| Partition with [compact] and [wide] parts (mixed) |\n"
        "| Partition with empty parts                        |\n"
        "\n"
        "The `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements SHALL work for any partition type.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_CorruptedParts = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.CorruptedParts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to `ATTACH PARTITION` when parts of a specific partition are corrupted.\n"
        "\n"
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` when parts have correct checksums.\n"
        "\n"
        "Possible partition types that can be corrupted are,\n"
        "\n"
        "| Partition Types                               |\n"
        "|-----------------------------------------------|\n"
        "| Partition with compact parts                  |\n"
        "| Partition with wide parts                     |\n"
        "| Partition with compact and wide parts (mixed) |\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TableName = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TableName",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `ALTER TABLE ATTACH PARTITION|PART` and `ALTER TABLE ATTACH PARTITION FROM` statements SHALL only work when the table names are valid.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionOrPart = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `ALTER TABLE ATTACH PARTITION|PART` statement.\n"
        "\n"
        "This statement SHALL allow the user to add data, either a full `PARTITITION` or a single `PART` to the table from the `detached` directory. \n"
        "\n"
        "```sql\n"
        "ALTER TABLE table_name [ON CLUSTER cluster] ATTACH PARTITION|PART [partition_expr]\n"
        "```\n"
        "\n"
        "After the query is executed the data SHALL be immediately available for querying on the specified table.\n"
        "\n"
        "[ClickHouse] SHALL reflect the changes in the `system.parts` table, when the `ALTER TABLE ATTACH PARTITION|PART` is executed. \n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionOrPart_RBAC = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.RBAC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Privileges     |\n"
        "|----------------|\n"
        "| No privileges  |\n"
        "| SELECT         |\n"
        "| INSERT         |\n"
        "| ALTER          |\n"
        "| ALTER TABLE    |\n"
        "\n"
        "The `ATTACH PARTITION FROM` SHALL only work when the user has the following privileges for the source and destination tables:\n"
        "\n"
        "| Source | Destination          |\n"
        "|--------|----------------------|\n"
        "| SELECT | ALTER TABLE, INSERT  |\n"
        "| SELECT | ALTER, INSERT        |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the`ALTER TABLE ATTACH PARTITION FROM` statement. This feature SHALL allow the user to copy data partition from [source table] to [destination table].\n"
        "\n"
        "```sql\n"
        "ALTER TABLE dest_table [ON CLUSTER cluster] ATTACH PARTITION partition_expr FROM src_table\n"
        "```\n"
        "\n"
        "[ClickHouse] SHALL reflect the changes in the `system.parts` table, when the `ALTER TABLE ATTACH PARTITION FROM` is executed on the [destination table]. \n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_KeepData = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep the data of the [source table] from which the partition is copied.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.3.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_FromTemporaryTable = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support copying the data partition from the temporary table.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.4.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION FROM` to attach partitions on a [destination table] that is on a different replica than the [source table].\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.5.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Shards = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE ATTACH PARTITION FROM` to attach partitions on tables that are on different shards.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.6.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` only when,\n"
        "\n"
        "* Both tables have the same structure.\n"
        "* Both tables have the same `ORDER BY` key.\n"
        "* Both tables have the same primary key.\n"
        "* Both tables have the same storage policy.\n"
        "* Both tables have the same indices and projections.\n"
        "* Both tables have the same partition key or the [source table] has more granular partitioning\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.7.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Structure = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same structure.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="11.7.2.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Key_OrderByKey = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same `ORDER BY` key.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="11.7.3.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Key_PrimaryKey = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same primary key.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="11.7.4.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_StoragePolicy = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same storage\n"
        "policy.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="11.7.5.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_IndicesAndProjections = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when tables have the same indices and projections.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="11.7.6.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when the [source table] has more granular partitioning than the [desctination table]. \n"
        "It is allowed to attach a partition from the table with different partition expression when the destination partition expression does not re-partition.\n"
        "[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when attaching from a partitioned table to an unpartitioned table.  \n"
        "\n"
    ),
    link=None,
    level=4,
    num="11.7.7.1",
)

RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_RBAC = Requirement(
    name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Privileges     |\n"
        "|----------------|\n"
        "| No privileges  |\n"
        "| SELECT         |\n"
        "| INSERT         |\n"
        "| ALTER          |\n"
        "| ALTER TABLE    |\n"
        "\n"
        "The `ATTACH PARTITION` SHALL only work when the user has the following privileges for the table:\n"
        "\n"
        "| Table Privilege |\n"
        "|-----------------|\n"
        "| INSERT          |\n"
        "\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.8.1",
)

SRS034_ClickHouse_Alter_Table_Attach_Partition = Specification(
    name="SRS034 ClickHouse Alter Table Attach Partition",
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
        Heading(name="Definitions", level=1, num="3"),
        Heading(name="Source Table", level=2, num="3.1"),
        Heading(name="Destination Table", level=2, num="3.2"),
        Heading(name="Compact part_type", level=2, num="3.3"),
        Heading(name="Wide part_type", level=2, num="3.4"),
        Heading(name="Attaching Partitions or Parts", level=1, num="4"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition", level=2, num="4.1"
        ),
        Heading(name="Supported Table Engines", level=1, num="5"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.SupportedTableEngines",
            level=2,
            num="5.1",
        ),
        Heading(name="Storage Policies", level=1, num="6"),
        Heading(name="Table That Is Stored on S3  ", level=2, num="6.1"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.S3",
            level=3,
            num="6.1.1",
        ),
        Heading(name="Table That Is Stored on Tiered Storage  ", level=2, num="6.2"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TieredStorage",
            level=3,
            num="6.2.1",
        ),
        Heading(name="Partition Types", level=1, num="7"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.PartitionTypes",
            level=2,
            num="7.1",
        ),
        Heading(name="Corrupted Parts ", level=1, num="8"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.CorruptedParts",
            level=2,
            num="8.1",
        ),
        Heading(name="Table names", level=1, num="9"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.TableName",
            level=2,
            num="9.1",
        ),
        Heading(
            name="Attach Partition or Part From the Detached Folder", level=1, num="10"
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart",
            level=2,
            num="10.1",
        ),
        Heading(
            name="Conditions for Attaching Partition or Part from the Detached Folder",
            level=2,
            num="10.2",
        ),
        Heading(
            name="Role-Based Access Control When Attach Partition or Part From the Detached Folder",
            level=2,
            num="10.3",
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionOrPart.RBAC",
            level=3,
            num="10.3.1",
        ),
        Heading(name="Attach Partition From Another Table", level=1, num="11"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom",
            level=2,
            num="11.1",
        ),
        Heading(name="Validation of Partition Expression", level=2, num="11.2"),
        Heading(name="Keeping Data on the Source Table ", level=2, num="11.3"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.KeepData",
            level=3,
            num="11.3.1",
        ),
        Heading(name="Temporary Tables", level=2, num="11.4"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.FromTemporaryTable",
            level=3,
            num="11.4.1",
        ),
        Heading(
            name="Destination Table That Is on a Different Replica", level=2, num="11.5"
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Replicas",
            level=3,
            num="11.5.1",
        ),
        Heading(
            name="Destination Table That Is on a Different Shard", level=2, num="11.6"
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Shards",
            level=3,
            num="11.6.1",
        ),
        Heading(
            name="Conditions when Attach Partition From Another Table",
            level=2,
            num="11.7",
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions",
            level=3,
            num="11.7.1",
        ),
        Heading(name="Tables With The Same Structure", level=3, num="11.7.2"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure",
            level=4,
            num="11.7.2.1",
        ),
        Heading(name="Tables With The Same `ORDER BY` Key", level=3, num="11.7.3"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey",
            level=4,
            num="11.7.3.1",
        ),
        Heading(name="Tables With The Same Primary Key", level=3, num="11.7.4"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey",
            level=4,
            num="11.7.4.1",
        ),
        Heading(name="Tables With The Same Storage Policy", level=3, num="11.7.5"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy",
            level=4,
            num="11.7.5.1",
        ),
        Heading(
            name="Tables With The Same Indices and Projections", level=3, num="11.7.6"
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections",
            level=4,
            num="11.7.6.1",
        ),
        Heading(name="Partition Key Condtitions", level=3, num="11.7.7"),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey",
            level=4,
            num="11.7.7.1",
        ),
        Heading(
            name="Role-Based Access Control when Attach Partition From Another Table",
            level=2,
            num="11.8",
        ),
        Heading(
            name="RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.RBAC",
            level=3,
            num="11.8.1",
        ),
        Heading(name="References", level=1, num="12"),
    ),
    requirements=(
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_SupportedTableEngines,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_S3,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TieredStorage,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartitionTypes,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_CorruptedParts,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_TableName,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionOrPart,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionOrPart_RBAC,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_KeepData,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_FromTemporaryTable,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Replicas,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Shards,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Structure,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Key_OrderByKey,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_Key_PrimaryKey,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_StoragePolicy,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Same_IndicesAndProjections,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_Conditions_Key_PartitionKey,
        RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_RBAC,
    ),
    content="""
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
        * 6.1.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartition.S3](#rqsrs-034clickhousealtertableattachpartitions3)
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
        * 11.7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions](#rqsrs-034clickhousealtertableattachpartitionfromconditions)
        * 11.7.2 [Tables With The Same Structure](#tables-with-the-same-structure)
            * 11.7.2.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Structure](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestructure)
        * 11.7.3 [Tables With The Same `ORDER BY` Key](#tables-with-the-same-order-by-key)
            * 11.7.3.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.OrderByKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyorderbykey)
        * 11.7.4 [Tables With The Same Primary Key](#tables-with-the-same-primary-key)
            * 11.7.4.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.Key.PrimaryKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamekeyprimarykey)
        * 11.7.5 [Tables With The Same Storage Policy](#tables-with-the-same-storage-policy)
            * 11.7.5.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.StoragePolicy](#rqsrs-034clickhousealtertableattachpartitionfromconditionssamestoragepolicy)
        * 11.7.6 [Tables With The Same Indices and Projections](#tables-with-the-same-indices-and-projections)
            * 11.7.6.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Same.IndicesAndProjections](#rqsrs-034clickhousealtertableattachpartitionfromconditionssameindicesandprojections)
        * 11.7.7 [Partition Key Condtitions](#partition-key-condtitions)
            * 11.7.7.1 [RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey](#rqsrs-034clickhousealtertableattachpartitionfromconditionskeypartitionkey)
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

#### Partition Key Condtitions

##### RQ.SRS-034.ClickHouse.Alter.Table.AttachPartitionFrom.Conditions.Key.PartitionKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when the [source table] has more granular partitioning than the [desctination table]. 
It is allowed to attach a partition from the table with different partition expression when the destination partition expression does not re-partition.
[ClickHouse] SHALL support the usage of `ALTER TABLE ATTACH PARTITION FROM` when attaching from a partitioned table to an unpartitioned table.  

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

The `ATTACH PARTITION` SHALL only work when the user has the following privileges for the table:

| Table Privilege |
|-----------------|
| INSERT          |



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
""",
)

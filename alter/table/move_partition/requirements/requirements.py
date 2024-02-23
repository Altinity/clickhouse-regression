# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.240111.1210833.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_SupportedTableEngines = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.SupportedTableEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following table engines for the `ALTER TABLE MOVE PARTITION TO TABLE` statement:\n"
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

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_S3 = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` statement with tables that are stored inside the S3 storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="6.1.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_TieredStorage = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TieredStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` statement with tables that are stored inside the tiered storage.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="6.2.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_PartitionTypes = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.PartitionTypes",
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
        "The `ALTER TABLE MOVE PARTITION TO TABLE` statement SHALL work for any partition type.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_CorruptedParts = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.CorruptedParts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to `MOVE PARTITION` when parts of a specific partition are corrupted.\n"
        "\n"
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when parts have correct checksums.\n"
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

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_TableName = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TableName",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `ALTER TABLE MOVE PARTITION TO TABLE` statement SHALL only work when the table names are valid.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_DeleteData = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.DeleteData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL delete the data from the [source table] from which the partition is moved.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.3.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_FromTemporaryTable = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.FromTemporaryTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support moving the data partition from the temporary table.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Replicas = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Replicas",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` to move a partition to a [destination table] that is on a different replica than the [source table].\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.5.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Shards = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Shards",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` with tables that are on different shards.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.6.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` only when,\n"
        "\n"
        "* Both tables must have the same structure.\n"
        "* Both tables must have the same order by key and the same primary key.\n"
        "* Both tables must have the same indices and projections.\n"
        "* Both tables must have the same storage policy.\n"
        "* Both tables must be the same engine family (replicated or non-replicated).\n"
        "\n"
        "* Both tables have the same partition key or the [source table] has more granular partitioning.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.7.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_Structure = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Structure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same structure.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.7.2.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_Key_OrderByKey = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.OrderByKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same `ORDER BY` key.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.7.3.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_Key_PrimaryKey = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.PrimaryKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same primary key.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.7.4.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_StoragePolicy = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.StoragePolicy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same storage\n"
        "policy.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.7.5.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_IndicesAndProjections = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.IndicesAndProjections",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same indices and projections.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.7.6.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Key_PartitionKey = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Key.PartitionKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when the [source table] has more granular partitioning than the [desctination table]. \n"
        "It is allowed to move a partition from the table with different partition expression when the destination partition expression does not re-partition.\n"
        "[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when moving from a partitioned table to an unpartitioned table.  \n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.7.7.1",
)

RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_RBAC = Requirement(
    name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.RBAC",
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
        "The `MOVE PARTITION` SHALL only work when the user has the following privileges for the destination table:\n"
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
    num="9.8.1",
)

SRS038_ClickHouse_Alter_Table_Move_Partition = Specification(
    name="SRS038 ClickHouse Alter Table Move Partition",
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
        Heading(name="Move Partition", level=1, num="4"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition", level=2, num="4.1"
        ),
        Heading(name="Supported Table Engines", level=1, num="5"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.SupportedTableEngines",
            level=2,
            num="5.1",
        ),
        Heading(name="Storage Policies", level=1, num="6"),
        Heading(name="Table That Is Stored on S3  ", level=2, num="6.1"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.S3",
            level=3,
            num="6.1.1",
        ),
        Heading(name="Table That Is Stored on Tiered Storage  ", level=2, num="6.2"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TieredStorage",
            level=3,
            num="6.2.1",
        ),
        Heading(name="Partition Types", level=1, num="7"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.PartitionTypes",
            level=2,
            num="7.1",
        ),
        Heading(name="Corrupted Parts ", level=1, num="8"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.CorruptedParts",
            level=2,
            num="8.1",
        ),
        Heading(name="Table names", level=1, num="9"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TableName",
            level=2,
            num="9.1",
        ),
        Heading(name="Validation of Partition Expression", level=2, num="9.2"),
        Heading(name="Keeping Data on the Source Table ", level=2, num="9.3"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.DeleteData",
            level=3,
            num="9.3.1",
        ),
        Heading(name="Temporary Tables", level=2, num="9.4"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.FromTemporaryTable",
            level=3,
            num="9.4.1",
        ),
        Heading(
            name="Destination Table That Is on a Different Replica", level=2, num="9.5"
        ),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Replicas",
            level=3,
            num="9.5.1",
        ),
        Heading(
            name="Destination Table That Is on a Different Shard", level=2, num="9.6"
        ),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Shards",
            level=3,
            num="9.6.1",
        ),
        Heading(name="Conditions when Move Partition ", level=2, num="9.7"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions",
            level=3,
            num="9.7.1",
        ),
        Heading(name="Tables With The Same Structure", level=3, num="9.7.2"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Structure",
            level=4,
            num="9.7.2.1",
        ),
        Heading(name="Tables With The Same `ORDER BY` Key", level=3, num="9.7.3"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.OrderByKey",
            level=4,
            num="9.7.3.1",
        ),
        Heading(name="Tables With The Same Primary Key", level=3, num="9.7.4"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.PrimaryKey",
            level=4,
            num="9.7.4.1",
        ),
        Heading(name="Tables With The Same Storage Policy", level=3, num="9.7.5"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.StoragePolicy",
            level=4,
            num="9.7.5.1",
        ),
        Heading(
            name="Tables With The Same Indices and Projections", level=3, num="9.7.6"
        ),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.IndicesAndProjections",
            level=4,
            num="9.7.6.1",
        ),
        Heading(name="Partition Key Conditions", level=3, num="9.7.7"),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Key.PartitionKey",
            level=4,
            num="9.7.7.1",
        ),
        Heading(
            name="Role-Based Access Control when Move Partition", level=2, num="9.8"
        ),
        Heading(
            name="RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.RBAC",
            level=3,
            num="9.8.1",
        ),
        Heading(name="References", level=1, num="10"),
    ),
    requirements=(
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_SupportedTableEngines,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_S3,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_TieredStorage,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_PartitionTypes,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_CorruptedParts,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_TableName,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_DeleteData,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_FromTemporaryTable,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Replicas,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Shards,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_Structure,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_Key_OrderByKey,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_Key_PrimaryKey,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_StoragePolicy,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Same_IndicesAndProjections,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_Conditions_Key_PartitionKey,
        RQ_SRS_038_ClickHouse_Alter_Table_MovePartition_RBAC,
    ),
    content="""
# SRS038 ClickHouse Alter Table Move Partition
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Definitions](#definitions)
    * 3.1 [Source Table](#source-table)
    * 3.2 [Destination Table](#destination-table)
    * 3.3 [Compact part_type](#compact-part_type)
    * 3.4 [Wide part_type](#wide-part_type)
* 4 [Move Partition](#move-partition)
    * 4.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition](#rqsrs-038clickhousealtertablemovepartition)
* 5 [Supported Table Engines](#supported-table-engines)
    * 5.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.SupportedTableEngines](#rqsrs-038clickhousealtertablemovepartitionsupportedtableengines)
* 6 [Storage Policies](#storage-policies)
    * 6.1 [Table That Is Stored on S3  ](#table-that-is-stored-on-s3-)
        * 6.1.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.S3](#rqsrs-038clickhousealtertablemovepartitions3)
    * 6.2 [Table That Is Stored on Tiered Storage  ](#table-that-is-stored-on-tiered-storage-)
        * 6.2.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TieredStorage](#rqsrs-038clickhousealtertablemovepartitiontieredstorage)
* 7 [Partition Types](#partition-types)
    * 7.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.PartitionTypes](#rqsrs-038clickhousealtertablemovepartitionpartitiontypes)
* 8 [Corrupted Parts ](#corrupted-parts-)
    * 8.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.CorruptedParts](#rqsrs-038clickhousealtertablemovepartitioncorruptedparts)
* 9 [Table names](#table-names)
    * 9.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TableName](#rqsrs-038clickhousealtertablemovepartitiontablename)
    * 9.2 [Validation of Partition Expression](#validation-of-partition-expression)
    * 9.3 [Keeping Data on the Source Table ](#keeping-data-on-the-source-table-)
        * 9.3.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.DeleteData](#rqsrs-038clickhousealtertablemovepartitiondeletedata)
    * 9.4 [Temporary Tables](#temporary-tables)
        * 9.4.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.FromTemporaryTable](#rqsrs-038clickhousealtertablemovepartitionfromtemporarytable)
    * 9.5 [Destination Table That Is on a Different Replica](#destination-table-that-is-on-a-different-replica)
        * 9.5.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Replicas](#rqsrs-038clickhousealtertablemovepartitionreplicas)
    * 9.6 [Destination Table That Is on a Different Shard](#destination-table-that-is-on-a-different-shard)
        * 9.6.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Shards](#rqsrs-038clickhousealtertablemovepartitionshards)
    * 9.7 [Conditions when Move Partition ](#conditions-when-move-partition-)
        * 9.7.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions](#rqsrs-038clickhousealtertablemovepartitionconditions)
        * 9.7.2 [Tables With The Same Structure](#tables-with-the-same-structure)
            * 9.7.2.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Structure](#rqsrs-038clickhousealtertablemovepartitionconditionssamestructure)
        * 9.7.3 [Tables With The Same `ORDER BY` Key](#tables-with-the-same-order-by-key)
            * 9.7.3.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.OrderByKey](#rqsrs-038clickhousealtertablemovepartitionconditionssamekeyorderbykey)
        * 9.7.4 [Tables With The Same Primary Key](#tables-with-the-same-primary-key)
            * 9.7.4.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.PrimaryKey](#rqsrs-038clickhousealtertablemovepartitionconditionssamekeyprimarykey)
        * 9.7.5 [Tables With The Same Storage Policy](#tables-with-the-same-storage-policy)
            * 9.7.5.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.StoragePolicy](#rqsrs-038clickhousealtertablemovepartitionconditionssamestoragepolicy)
        * 9.7.6 [Tables With The Same Indices and Projections](#tables-with-the-same-indices-and-projections)
            * 9.7.6.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.IndicesAndProjections](#rqsrs-038clickhousealtertablemovepartitionconditionssameindicesandprojections)
        * 9.7.7 [Partition Key Conditions](#partition-key-conditions)
            * 9.7.7.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Key.PartitionKey](#rqsrs-038clickhousealtertablemovepartitionconditionskeypartitionkey)
    * 9.8 [Role-Based Access Control when Move Partition](#role-based-access-control-when-move-partition)
        * 9.8.1 [RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.RBAC](#rqsrs-038clickhousealtertablemovepartitionrbac)
* 10 [References](#references)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository]. All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for the `ALTER TABLE MOVE PARTITION TO TABLE` statement in [ClickHouse].

The documentation used:

- https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#move-partition-to-table

## Definitions

### Source Table

The table from which a partition or part is taken.

### Destination Table

The table to which a partition or part is going to be moved.

### Compact part_type

All columns are stored in one file in a filesystem.

### Wide part_type

Each column is stored in a separate file in a filesystem.

Data storing format is controlled by the min_bytes_for_wide_part and min_rows_for_wide_part settings of the MergeTree table.

## Move Partition

### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition

[ClickHouse] SHALL support the`ALTER TABLE MOVE PARTITION TO TABLE` statement. This feature SHALL allow the user to move data partition from [source table] to [destination table] with deleting the data from [source table].

```sql
ALTER TABLE table_source [ON CLUSTER cluster] MOVE PARTITION partition_expr TO TABLE table_dest
```

[ClickHouse] SHALL reflect the changes in the `system.parts` table, when the `ALTER TABLE MOVE PARTITION TO TABLE` is executed. 

## Supported Table Engines

### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.SupportedTableEngines
version: 1.0

[ClickHouse] SHALL support the following table engines for the `ALTER TABLE MOVE PARTITION TO TABLE` statement:

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

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.S3
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` statement with tables that are stored inside the S3 storage.

### Table That Is Stored on Tiered Storage  

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TieredStorage
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` statement with tables that are stored inside the tiered storage.

## Partition Types

### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.PartitionTypes
version: 1.0

| Partition Types                                   |
|---------------------------------------------------|
| Partition with only [compact] parts               |
| Partition with only [wide] parts                  |
| Partition with [compact] and [wide] parts (mixed) |
| Partition with empty parts                        |

The `ALTER TABLE MOVE PARTITION TO TABLE` statement SHALL work for any partition type.

## Corrupted Parts 

### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.CorruptedParts
version: 1.0

[ClickHouse] SHALL output an error when trying to `MOVE PARTITION` when parts of a specific partition are corrupted.

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when parts have correct checksums.

Possible partition types that can be corrupted are,

| Partition Types                               |
|-----------------------------------------------|
| Partition with compact parts                  |
| Partition with wide parts                     |
| Partition with compact and wide parts (mixed) |

## Table names

### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.TableName
version: 1.0

The `ALTER TABLE MOVE PARTITION TO TABLE` statement SHALL only work when the table names are valid.

### Validation of Partition Expression

- Valid or not
- partition exists or not
- partition exists but no right to access files

### Keeping Data on the Source Table 

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.DeleteData
version: 1.0

[ClickHouse] SHALL delete the data from the [source table] from which the partition is moved.

### Temporary Tables

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.FromTemporaryTable
version: 1.0

[ClickHouse] SHALL support moving the data partition from the temporary table.


### Destination Table That Is on a Different Replica

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Replicas
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` to move a partition to a [destination table] that is on a different replica than the [source table].

### Destination Table That Is on a Different Shard

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Shards
version: 1.0

[ClickHouse] SHALL support using `ALTER TABLE MOVE PARTITION TO TABLE` with tables that are on different shards.

### Conditions when Move Partition 

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` only when,

* Both tables must have the same structure.
* Both tables must have the same order by key and the same primary key.
* Both tables must have the same indices and projections.
* Both tables must have the same storage policy.
* Both tables must be the same engine family (replicated or non-replicated).

* Both tables have the same partition key or the [source table] has more granular partitioning.

#### Tables With The Same Structure

##### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Structure
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same structure.

#### Tables With The Same `ORDER BY` Key

##### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.OrderByKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same `ORDER BY` key.

#### Tables With The Same Primary Key

##### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.Key.PrimaryKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same primary key.

#### Tables With The Same Storage Policy

##### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.StoragePolicy
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same storage
policy.

#### Tables With The Same Indices and Projections

##### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Same.IndicesAndProjections
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when tables have the same indices and projections.

#### Partition Key Conditions

##### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.Conditions.Key.PartitionKey
version: 1.0

[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when the [source table] has more granular partitioning than the [desctination table]. 
It is allowed to move a partition from the table with different partition expression when the destination partition expression does not re-partition.
[ClickHouse] SHALL support the usage of `ALTER TABLE MOVE PARTITION TO TABLE` when moving from a partitioned table to an unpartitioned table.  

### Role-Based Access Control when Move Partition

#### RQ.SRS-038.ClickHouse.Alter.Table.MovePartition.RBAC
version: 1.0

| Privileges     |
|----------------|
| No privileges  |
| SELECT         |
| INSERT         |
| ALTER          |
| ALTER TABLE    |

The `MOVE PARTITION` SHALL only work when the user has the following privileges for the destination table:

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
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/move_partition/alter/table/move_partition/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/blob/move_partition/alter/table/move_partition/requirements/requirements.md
[GitHub]: https://github.com
[partition_expr]: https://clickhouse.com/docs/en/sql-reference/statements/alter/partition#how-to-set-partition-expression
""",
)

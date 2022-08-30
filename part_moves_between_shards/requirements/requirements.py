# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.7.211208.1222904.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_027_ClickHouse_PartMovesBetweenShards = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support moving parts between shards using the following command syntax:\n"
        "\n"
        "```sql\n"
        "ALTER TABLE <table_name> MOVE PART <part_name> TO SHARD 'ZooKeeper path'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.1.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_OnePartMove = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartMove",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support a single part movement from one shard to another when\n"
        "`MOVE PART TO SHARD` query is used.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.2.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_OnePartReturn = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartReturn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support a single part movement from one shard to another and back when `MOVE PART TO SHARD` query is used.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.3.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ZeroPart = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ZeroPart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries\n"
        "to move a part with an empty name.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.4.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_MovePartWithIncorrectName = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.MovePartWithIncorrectName",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries\n"
        "to move a part with an incorrect name.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.5.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SameShard = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SameShard",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries \n"
        "to move a part to the same shard where it is currently present.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.6.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DifferentLocalStructure = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentLocalStructure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part to the shard\n"
        "which has different local column structures.\n"
        "\n"
        "For example,\n"
        "\n"
        "* where column name was changed with `ALTER RENAME COLUMN` query\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.7.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DifferentPartitionKey = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentPartitionKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part to the shard\n"
        "which differs in partition key expression.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.8.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_PartNotExist = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.PartNotExist",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part \n"
        "that doesn't exist.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.9.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SupportedTableEngines = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SupportedTableEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using the `MOVE PART TO SHARD`  statement on \n"
        "sharded tables for all ReplicatedMergeTree table engines:\n"
        "\n"
        "* ReplicatedMergeTree\n"
        "* ReplicatedSummingMergeTree\n"
        "* ReplicatedReplacingMergeTree\n"
        "* ReplicatedAggregatingMergeTree\n"
        "* ReplicatedCollapsingMergeTree\n"
        "* ReplicatedVersionedCollapsingMergeTree\n"
        "* ReplicatedGraphiteMergeTree\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.10.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_NotSupportedTableEngines = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.NotSupportedTableEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support using the `MOVE PART TO SHARD` statement on \n"
        "sharded tables for non replicated MergeTree table engines.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.11.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when\n"
        "there are multiple concurrent `MOVE PART TO SHARD` operations.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.12.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_SamePart = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.SamePart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when there are\n"
        "multiple concurrent `MOVE PART TO SHARD` operations targeting the same part.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.12.2.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_InsertDataOnSourceNodeSamePartition = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnSourceNodeSamePartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when it is concurrent with\n"
        "`INSERT` statement that inserts data on the source node in the same partition as the one being moved.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.12.3.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_InsertDataOnDestinationNodeSamePartition = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnDestinationNodeSamePartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when it is concurrent with\n"
        "`INSERT` statement on the same destination node that writes data into the same partition as the one being moved.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.12.3.2",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL not duplicate data when parts are moved.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.13.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DestinationReplicaStopped = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DestinationReplicaStopped",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL allow moving part from a shard when even one\n"
        "of its destination replicas is down and SHALL finish part move query when replicas return.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.13.2.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_SourceReplicaStopped = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.SourceReplicaStopped",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL allow moving part from a shard when even one\n"
        "of its source replicas is down and SHALL finish part move query when replicas return.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.13.3.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DistributedTable = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL not cause data duplication when \n"
        "`MOVE PART TO SHARD` query is used multiple times when sharded table is accessed using\n"
        "`Distributed` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.13.4.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DistributedTable_ReplicaStopped = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable.ReplicaStopped",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] `MOVE PART TO SHARD` statement SHALL not cause data duplication when \n"
        "`MOVE PART TO SHARD` query is used multiple times and some replica on one shard \n"
        "starts and stops when sharded table is accessed using `Distributed` table engine.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=5,
    num="2.13.4.2.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL write information about `MOVE PART TO SHARD` queries to special\n"
        "system table `system.part_moves_between_shards`. \n"
        "\n"
        "The table SHALL have the following column names and types:\n"
        "\n"
        "    `database` String - database`s name\n"
        "    `table` String - table`s name\n"
        "    `task_name` String - task`s name\n"
        "    `task_uuid` UUID - task`s UUID\n"
        "    `create_time` DateTime - time of `PART MOVE` query creation\n"
        "    `part_name` String - part`s name\n"
        "    `part_uuid` UUID - part`s UUID\n"
        "    `to_shard` String - destination shard path in ZooKeeper\n"
        "    `dst_part_name` String - new part`s name on destination shard\n"
        "    `update_time` DateTime - time of update\n"
        "    `state` String - current state of task\n"
        "    `rollback` UInt8 - rollback state\n"
        "    `num_tries` UInt32 - number of tries\n"
        "    `last_exception` String - description of the last exception\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="2.14.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable_SyncFailSource = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailSource",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL change value in the `state` column to `SYNC_SOURCE` and show information\n"
        "about exception in `last_exception` column of system table `system.part_moves_between_shards` \n"
        "when one of the source replicas is down and `MOVE PART TO SHARD` query is in progress.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.14.2.1",
)

RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable_SyncFailDestination = Requirement(
    name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailDestination",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL change value in `state` column to `SYNC_DESTINATION` and show information\n"
        "about exception in `last_exception` column of system table `system.part_moves_between_shards` \n"
        "when one of the destination replicas is down and `MOVE PART TO SHARD` query is in progress.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="2.14.3.1",
)

SRS027_ClickHouse_Part_Moves_Between_Shards = Specification(
    name="SRS027 ClickHouse Part Moves Between Shards",
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
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Requirements", level=1, num="2"),
        Heading(name="General", level=2, num="2.1"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards", level=3, num="2.1.1"
        ),
        Heading(name="Move Part", level=2, num="2.2"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartMove",
            level=3,
            num="2.2.1",
        ),
        Heading(name="Return Part", level=2, num="2.3"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartReturn",
            level=3,
            num="2.3.1",
        ),
        Heading(name="Zero Part", level=2, num="2.4"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ZeroPart",
            level=3,
            num="2.4.1",
        ),
        Heading(name="Move Part With Incorrect Name", level=2, num="2.5"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.MovePartWithIncorrectName",
            level=3,
            num="2.5.1",
        ),
        Heading(name="Same Shard", level=2, num="2.6"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SameShard",
            level=3,
            num="2.6.1",
        ),
        Heading(name="Different Local Structure", level=2, num="2.7"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentLocalStructure",
            level=3,
            num="2.7.1",
        ),
        Heading(name="Different Partition Key", level=2, num="2.8"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentPartitionKey",
            level=3,
            num="2.8.1",
        ),
        Heading(name="Part Not Exist", level=2, num="2.9"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.PartNotExist",
            level=3,
            num="2.9.1",
        ),
        Heading(name="Supported Table Engines", level=2, num="2.10"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SupportedTableEngines",
            level=3,
            num="2.10.1",
        ),
        Heading(name="Not Supported Table Engines", level=2, num="2.11"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.NotSupportedTableEngines",
            level=3,
            num="2.11.1",
        ),
        Heading(name="Concurrent Part Moves", level=2, num="2.12"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves",
            level=3,
            num="2.12.1",
        ),
        Heading(name="Same Part", level=3, num="2.12.2"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.SamePart",
            level=4,
            num="2.12.2.1",
        ),
        Heading(name="Insert Data", level=3, num="2.12.3"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnSourceNodeSamePartition",
            level=4,
            num="2.12.3.1",
        ),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnDestinationNodeSamePartition",
            level=4,
            num="2.12.3.2",
        ),
        Heading(name="Data Deduplication", level=2, num="2.13"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication",
            level=3,
            num="2.13.1",
        ),
        Heading(name="Destination Replica Stopped", level=3, num="2.13.2"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DestinationReplicaStopped",
            level=4,
            num="2.13.2.1",
        ),
        Heading(name="Source Replica Stopped", level=3, num="2.13.3"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.SourceReplicaStopped",
            level=4,
            num="2.13.3.1",
        ),
        Heading(name="Distributed Table Data", level=3, num="2.13.4"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable",
            level=4,
            num="2.13.4.1",
        ),
        Heading(name="Replica Stopped", level=4, num="2.13.4.2"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable.ReplicaStopped",
            level=5,
            num="2.13.4.2.1",
        ),
        Heading(name="System Table", level=2, num="2.14"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable",
            level=3,
            num="2.14.1",
        ),
        Heading(name="Sync Fail Source", level=3, num="2.14.2"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailSource",
            level=4,
            num="2.14.2.1",
        ),
        Heading(name="Sync Fail Destination", level=3, num="2.14.3"),
        Heading(
            name="RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailDestination",
            level=4,
            num="2.14.3.1",
        ),
        Heading(name="References", level=1, num="3"),
    ),
    requirements=(
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_OnePartMove,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_OnePartReturn,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ZeroPart,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_MovePartWithIncorrectName,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SameShard,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DifferentLocalStructure,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DifferentPartitionKey,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_PartNotExist,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SupportedTableEngines,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_NotSupportedTableEngines,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_SamePart,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_InsertDataOnSourceNodeSamePartition,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_ConcurrentPartMoves_InsertDataOnDestinationNodeSamePartition,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DestinationReplicaStopped,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_SourceReplicaStopped,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DistributedTable,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DistributedTable_ReplicaStopped,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable_SyncFailSource,
        RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable_SyncFailDestination,
    ),
    content="""
# SRS027 ClickHouse Part Moves Between Shards
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
  * 2.1 [General](#general)
    * 2.1.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards](#rqsrs-027clickhousepartmovesbetweenshards)
  * 2.2 [Move Part](#move-part)
    * 2.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartMove](#rqsrs-027clickhousepartmovesbetweenshardsonepartmove)
  * 2.3 [Return Part](#return-part)
    * 2.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartReturn](#rqsrs-027clickhousepartmovesbetweenshardsonepartreturn)
  * 2.4 [Zero Part](#zero-part)
    * 2.4.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ZeroPart](#rqsrs-027clickhousepartmovesbetweenshardszeropart)
  * 2.5 [Move Part With Incorrect Name](#move-part-with-incorrect-name)
    * 2.5.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.MovePartWithIncorrectName](#rqsrs-027clickhousepartmovesbetweenshardsmovepartwithincorrectname)
  * 2.6 [Same Shard](#same-shard)
    * 2.6.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SameShard](#rqsrs-027clickhousepartmovesbetweenshardssameshard)
  * 2.7 [Different Local Structure](#different-local-structure)
    * 2.7.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentLocalStructure](#rqsrs-027clickhousepartmovesbetweenshardsdifferentlocalstructure)
  * 2.8 [Different Partition Key](#different-partition-key)
    * 2.8.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentPartitionKey](#rqsrs-027clickhousepartmovesbetweenshardsdifferentpartitionkey)
  * 2.9 [Part Not Exist](#part-not-exist)
    * 2.9.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.PartNotExist](#rqsrs-027clickhousepartmovesbetweenshardspartnotexist)
  * 2.10 [Supported Table Engines](#supported-table-engines)
    * 2.10.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SupportedTableEngines](#rqsrs-027clickhousepartmovesbetweenshardssupportedtableengines)
  * 2.11 [Not Supported Table Engines](#not-supported-table-engines)
    * 2.11.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.NotSupportedTableEngines](#rqsrs-027clickhousepartmovesbetweenshardsnotsupportedtableengines)
  * 2.12 [Concurrent Part Moves](#concurrent-part-moves)
    * 2.12.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmoves)
    * 2.12.2 [Same Part](#same-part)
      * 2.12.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.SamePart](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmovessamepart)
    * 2.12.3 [Insert Data](#insert-data)
      * 2.12.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnSourceNodeSamePartition](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmovesinsertdataonsourcenodesamepartition)
      * 2.12.3.2 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnDestinationNodeSamePartition](#rqsrs-027clickhousepartmovesbetweenshardsconcurrentpartmovesinsertdataondestinationnodesamepartition)
  * 2.13 [Data Deduplication](#data-deduplication)
    * 2.13.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplication)
    * 2.13.2 [Destination Replica Stopped](#destination-replica-stopped)
      * 2.13.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DestinationReplicaStopped](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationdestinationreplicastopped)
    * 2.13.3 [Source Replica Stopped](#source-replica-stopped)
      * 2.13.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.SourceReplicaStopped](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationsourcereplicastopped)
    * 2.13.4 [Distributed Table Data](#distributed-table-data)
      * 2.13.4.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationdistributedtable)
      * 2.13.4.2 [Replica Stopped](#replica-stopped)
        * 2.13.4.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable.ReplicaStopped](#rqsrs-027clickhousepartmovesbetweenshardsdatadeduplicationdistributedtablereplicastopped)
  * 2.14 [System Table](#system-table)
    * 2.14.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable](#rqsrs-027clickhousepartmovesbetweenshardssystemtable)
    * 2.14.2 [Sync Fail Source](#sync-fail-source)
      * 2.14.2.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailSource](#rqsrs-027clickhousepartmovesbetweenshardssystemtablesyncfailsource)
    * 2.14.3 [Sync Fail Destination](#sync-fail-destination)
      * 2.14.3.1 [RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailDestination](#rqsrs-027clickhousepartmovesbetweenshardssystemtablesyncfaildestination)
* 3 [References](#references)



## Introduction

[ClickHouse] feature to allow part uuid pinning and movement between shards.

## Requirements

### General

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards
version: 1.0

[ClickHouse] SHALL support moving parts between shards using the following command syntax:

```sql
ALTER TABLE <table_name> MOVE PART <part_name> TO SHARD 'ZooKeeper path'
```

### Move Part

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartMove
version: 1.0

[ClickHouse] SHALL support a single part movement from one shard to another when
`MOVE PART TO SHARD` query is used.

### Return Part

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.OnePartReturn
version: 1.0

[ClickHouse] SHALL support a single part movement from one shard to another and back when `MOVE PART TO SHARD` query is used.

### Zero Part

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ZeroPart
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries
to move a part with an empty name.

### Move Part With Incorrect Name

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.MovePartWithIncorrectName
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries
to move a part with an incorrect name.

### Same Shard

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SameShard
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries 
to move a part to the same shard where it is currently present.

### Different Local Structure

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentLocalStructure
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part to the shard
which has different local column structures.

For example,

* where column name was changed with `ALTER RENAME COLUMN` query

### Different Partition Key

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DifferentPartitionKey
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part to the shard
which differs in partition key expression.

### Part Not Exist

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.PartNotExist
version: 1.0

[ClickHouse] SHALL return an error if the `MOVE PART TO SHARD` query tries to move a part 
that doesn't exist.

### Supported Table Engines

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SupportedTableEngines
version: 1.0

[ClickHouse] SHALL support using the `MOVE PART TO SHARD`  statement on 
sharded tables for all ReplicatedMergeTree table engines:

* ReplicatedMergeTree
* ReplicatedSummingMergeTree
* ReplicatedReplacingMergeTree
* ReplicatedAggregatingMergeTree
* ReplicatedCollapsingMergeTree
* ReplicatedVersionedCollapsingMergeTree
* ReplicatedGraphiteMergeTree

### Not Supported Table Engines

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.NotSupportedTableEngines
version: 1.0

[ClickHouse] SHALL not support using the `MOVE PART TO SHARD` statement on 
sharded tables for non replicated MergeTree table engines.

### Concurrent Part Moves

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when
there are multiple concurrent `MOVE PART TO SHARD` operations.

#### Same Part

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.SamePart
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when there are
multiple concurrent `MOVE PART TO SHARD` operations targeting the same part.

#### Insert Data

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnSourceNodeSamePartition
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when it is concurrent with
`INSERT` statement that inserts data on the source node in the same partition as the one being moved.

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.ConcurrentPartMoves.InsertDataOnDestinationNodeSamePartition
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL perform correctly when it is concurrent with
`INSERT` statement on the same destination node that writes data into the same partition as the one being moved.

### Data Deduplication

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL not duplicate data when parts are moved.

#### Destination Replica Stopped

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DestinationReplicaStopped
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL allow moving part from a shard when even one
of its destination replicas is down and SHALL finish part move query when replicas return.

#### Source Replica Stopped

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.SourceReplicaStopped
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL allow moving part from a shard when even one
of its source replicas is down and SHALL finish part move query when replicas return.

#### Distributed Table Data

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL not cause data duplication when 
`MOVE PART TO SHARD` query is used multiple times when sharded table is accessed using
`Distributed` table engine.

##### Replica Stopped

###### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.DataDeduplication.DistributedTable.ReplicaStopped
version: 1.0

[ClickHouse] `MOVE PART TO SHARD` statement SHALL not cause data duplication when 
`MOVE PART TO SHARD` query is used multiple times and some replica on one shard 
starts and stops when sharded table is accessed using `Distributed` table engine.


### System Table

#### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable
version: 1.0

[ClickHouse] SHALL write information about `MOVE PART TO SHARD` queries to special
system table `system.part_moves_between_shards`. 

The table SHALL have the following column names and types:

    `database` String - database`s name
    `table` String - table`s name
    `task_name` String - task`s name
    `task_uuid` UUID - task`s UUID
    `create_time` DateTime - time of `PART MOVE` query creation
    `part_name` String - part`s name
    `part_uuid` UUID - part`s UUID
    `to_shard` String - destination shard path in ZooKeeper
    `dst_part_name` String - new part`s name on destination shard
    `update_time` DateTime - time of update
    `state` String - current state of task
    `rollback` UInt8 - rollback state
    `num_tries` UInt32 - number of tries
    `last_exception` String - description of the last exception


#### Sync Fail Source

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailSource
version: 1.0

[ClickHouse] SHALL change value in the `state` column to `SYNC_SOURCE` and show information
about exception in `last_exception` column of system table `system.part_moves_between_shards` 
when one of the source replicas is down and `MOVE PART TO SHARD` query is in progress.

#### Sync Fail Destination

##### RQ.SRS-027.ClickHouse.PartMovesBetweenShards.SystemTable.SyncFailDestination
version: 1.0

[ClickHouse] SHALL change value in `state` column to `SYNC_DESTINATION` and show information
about exception in `last_exception` column of system table `system.part_moves_between_shards` 
when one of the destination replicas is down and `MOVE PART TO SHARD` query is in progress.

## References

* **ClickHouse:** https://clickhouse.com

[SRS]: #srs
[ClickHouse]: https://clickhouse.com
""",
)

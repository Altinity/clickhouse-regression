# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.7.211208.1222904.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_028_ClickHouse_AtomicInserts = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support [atomic inserts].\n" "\n"),
    link=None,
    level=2,
    num="4.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_InsertSettings = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.InsertSettings",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support all `INSERT` settings with atomic inserts.\n"
        "\n"
        "The settings include the following:\n"
        "\n"
        "*  `max_insert_block_size` – split insert into chunks\n"
        "*  `min_insert_block_size_rows` – merge input into bigger chunks based on rows\n"
        "*  `min_insert_block_size_bytes` – merge input into bigger chunks based on bytes\n"
        "*  `input_format_parallel_parsing` – splits text input into chunks\n"
        "*  `max_insert_threads` – number of threads to use during insert\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_BlocksAndPartitions = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.BlocksAndPartitions",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] for the following cases:\n"
        "\n"
        "* single block, single partition\n"
        "* single block, multiple partitions\n"
        "* multiple blocks, single partition\n"
        "* multiple blocks, multiple partitions \n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_SupportedTableEngines_MergeTree = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.MergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] for all MergeTree table engines and their variants:\n"
        "\n"
        "* MergeTree\n"
        "* SummingMergeTree\n"
        "* ReplacingMergeTree\n"
        "* AggregatingMergeTree\n"
        "* CollapsingMergeTree\n"
        "* VersionedCollapsingMergeTree\n"
        "* GraphiteMergeTree\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.1.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_SupportedTableEngines_ReplicatedMergeTree = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.ReplicatedMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] for all ReplicatedMergeTree table engines and their variants:\n"
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
    level=4,
    num="4.4.2.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_DependentTables = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.DependentTables",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] when the following dependent tables are present: \n"
        "\n"
        "* one or more normal views\n"
        "* single or cascading materialized view\n"
        "* single or cascading window view\n"
        "* one or more live views\n"
        "* materialized with normal view\n"
        "* materialized with live view\n"
        "* materialized with window view\n"
        "* window with materialized view\n"
        "* window with normal view\n"
        "* window with live view\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable",
    version="1.0",
    priority="2.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] into distributed table\n"
        "when `insert_distributed_sync` setting is enabled.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable_ShardUnavailable = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ShardUnavailable",
    version="1.0",
    priority="2.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL abort [atomic inserts] if even one shard was not available.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.2",
)

RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable_ReplicaUnavailable = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ReplicaUnavailable",
    version="1.0,",
    priority="2.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL abort [atomic inserts] if even one replica was not available.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.3",
)

RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable_KeeperReadOnly = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.KeeperReadOnly",
    version="1.0",
    priority="2.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL abort [atomic inserts] if ZooKeeper or Clickhouse Keeper has placed a table into \n"
        'a "read only" mode.\n'
        "\n"
    ),
    link=None,
    level=3,
    num="4.6.4",
)

RQ_SRS_028_ClickHouse_AtomicInserts_MultipleTables = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.MultipleTables",
    version="1.0",
    priority="3.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] into multiple tables as a single atomic transaction.\n"
        "\n"
        "```sql\n"
        "BEGIN TRANSACTION\n"
        "INSERT INTO <table.a> ...\n"
        "INSERT INTO <table.b> ...\n"
        "...\n"
        "COMMIT TRANSACTION\n"
        "```\n"
        "\n"
        "The insert into multiple tables SHALL only succeed if [atomic inserts] can succeed in all the tables.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.7.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_DataDuplication = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.DataDuplication",
    version="1.0",
    priority="3.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow data duplication when:\n"
        "\n"
        "* user retries failed inserts\n"
        "* presence of collisions in message bus (e.g. Kafka re-balances)\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.8.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_OneOrMoreParts = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OneOrMoreParts",
    version="1.0",
    priority="3.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of fails to insert our or more parts\n"
        "into target table or any of its dependent tables.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.1.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_SyntaxError = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SyntaxError",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of a syntax error in the query.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.2.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_MismatchedTableStructure = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.MismatchedTableStructure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence failure to insert due to\n"
        "mismatch in table structure that occures in the target table or one or its dependent tables.\n"
        "\n"
        "Examples:\n"
        "\n"
        "* different column data type\n"
        "* missing columns\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.3.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_CircularDependentTables = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.CircularDependentTables",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of circular dependent tables.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.4.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_EmulatedUsingThrowIf = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.EmulatedUsingThrowIf",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of an emulated failure \n"
        "using [throwif] on a particular partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.5.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_DiskCorruption = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.DiskCorruption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of disk critically corrupted and cannot receive all the data.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.6.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_SlowDisk = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SlowDisk",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of one or more slow disks.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.9.7.1.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_UserRights = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.UserRights",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of a query issues by a user that does not have\n"
        "enough rights either on the target table or one of its dependent tables.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.8.1",
)

RQ_SRS_028_ClickHouse_AtomicInserts_Failures_OutOfSyncReplicas = Requirement(
    name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OutOfSyncReplicas",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [atomic inserts] in presence of issues with data synchronicity on replicas.\n"
        "\n"
        "[SRS]: #srs\n"
        "[atomic inserts]: #attomic-inserts\n"
        "[throwif]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions/#throwifx-custom-message\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.9.9.1",
)

SRS028_ClickHouse_Atomic_Inserts = Specification(
    name="SRS028 ClickHouse Atomic Inserts",
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
        Heading(name="Related Resources", level=1, num="2"),
        Heading(name="Terminology", level=1, num="3"),
        Heading(name="SRS", level=2, num="3.1"),
        Heading(name="Atomic Inserts", level=2, num="3.2"),
        Heading(name="Requirements", level=1, num="4"),
        Heading(name="RQ.SRS-028.ClickHouse.AtomicInserts", level=2, num="4.1"),
        Heading(name="Insert Settings", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.InsertSettings",
            level=3,
            num="4.2.1",
        ),
        Heading(name="Blocks And Partitions", level=2, num="4.3"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.BlocksAndPartitions",
            level=3,
            num="4.3.1",
        ),
        Heading(name="Supported Table Engines", level=2, num="4.4"),
        Heading(name="Merge Tree", level=3, num="4.4.1"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.MergeTree",
            level=4,
            num="4.4.1.1",
        ),
        Heading(name="Replicated Merge Tree", level=3, num="4.4.2"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.ReplicatedMergeTree",
            level=4,
            num="4.4.2.1",
        ),
        Heading(name="Dependent Tables", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.DependentTables",
            level=3,
            num="4.5.1",
        ),
        Heading(name="Distributed Table", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable",
            level=3,
            num="4.6.1",
        ),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ShardUnavailable",
            level=3,
            num="4.6.2",
        ),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ReplicaUnavailable",
            level=3,
            num="4.6.3",
        ),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.KeeperReadOnly",
            level=3,
            num="4.6.4",
        ),
        Heading(name="Multiple Tables", level=2, num="4.7"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.MultipleTables",
            level=3,
            num="4.7.1",
        ),
        Heading(name="Data Duplication", level=2, num="4.8"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.DataDuplication",
            level=3,
            num="4.8.1",
        ),
        Heading(name="Failure Modes", level=2, num="4.9"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OneOrMoreParts",
            level=4,
            num="4.9.1.1",
        ),
        Heading(name="Syntax Error", level=3, num="4.9.2"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SyntaxError",
            level=4,
            num="4.9.2.1",
        ),
        Heading(name="Mismatched Table Structure", level=3, num="4.9.3"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.MismatchedTableStructure",
            level=4,
            num="4.9.3.1",
        ),
        Heading(name="Circular Dependent Tables", level=3, num="4.9.4"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.CircularDependentTables",
            level=4,
            num="4.9.4.1",
        ),
        Heading(name="Emulated Error", level=3, num="4.9.5"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.EmulatedUsingThrowIf",
            level=4,
            num="4.9.5.1",
        ),
        Heading(name="Disk Corruption", level=3, num="4.9.6"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.DiskCorruption",
            level=4,
            num="4.9.6.1",
        ),
        Heading(name="Slow Disk", level=3, num="4.9.7"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SlowDisk",
            level=5,
            num="4.9.7.1.1",
        ),
        Heading(name="User Rights", level=3, num="4.9.8"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.UserRights",
            level=4,
            num="4.9.8.1",
        ),
        Heading(name="Out of Sync Replicas", level=3, num="4.9.9"),
        Heading(
            name="RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OutOfSyncReplicas",
            level=4,
            num="4.9.9.1",
        ),
    ),
    requirements=(
        RQ_SRS_028_ClickHouse_AtomicInserts,
        RQ_SRS_028_ClickHouse_AtomicInserts_InsertSettings,
        RQ_SRS_028_ClickHouse_AtomicInserts_BlocksAndPartitions,
        RQ_SRS_028_ClickHouse_AtomicInserts_SupportedTableEngines_MergeTree,
        RQ_SRS_028_ClickHouse_AtomicInserts_SupportedTableEngines_ReplicatedMergeTree,
        RQ_SRS_028_ClickHouse_AtomicInserts_DependentTables,
        RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable,
        RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable_ShardUnavailable,
        RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable_ReplicaUnavailable,
        RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable_KeeperReadOnly,
        RQ_SRS_028_ClickHouse_AtomicInserts_MultipleTables,
        RQ_SRS_028_ClickHouse_AtomicInserts_DataDuplication,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_OneOrMoreParts,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_SyntaxError,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_MismatchedTableStructure,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_CircularDependentTables,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_EmulatedUsingThrowIf,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_DiskCorruption,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_SlowDisk,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_UserRights,
        RQ_SRS_028_ClickHouse_AtomicInserts_Failures_OutOfSyncReplicas,
    ),
    content="""
# SRS028 ClickHouse Atomic Inserts
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
  * 3.2 [Atomic Inserts](#atomic-inserts)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-028.ClickHouse.AtomicInserts](#rqsrs-028clickhouseatomicinserts)
  * 4.2 [Insert Settings](#insert-settings)
    * 4.2.1 [RQ.SRS-028.ClickHouse.AtomicInserts.InsertSettings](#rqsrs-028clickhouseatomicinsertsinsertsettings)
  * 4.3 [Blocks And Partitions](#blocks-and-partitions)
    * 4.3.1 [RQ.SRS-028.ClickHouse.AtomicInserts.BlocksAndPartitions](#rqsrs-028clickhouseatomicinsertsblocksandpartitions)
  * 4.4 [Supported Table Engines](#supported-table-engines)
    * 4.4.1 [Merge Tree](#merge-tree)
      * 4.4.1.1 [RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.MergeTree](#rqsrs-028clickhouseatomicinsertssupportedtableenginesmergetree)
    * 4.4.2 [Replicated Merge Tree](#replicated-merge-tree)
      * 4.4.2.1 [RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.ReplicatedMergeTree](#rqsrs-028clickhouseatomicinsertssupportedtableenginesreplicatedmergetree)
  * 4.5 [Dependent Tables](#dependent-tables)
    * 4.5.1 [RQ.SRS-028.ClickHouse.AtomicInserts.DependentTables](#rqsrs-028clickhouseatomicinsertsdependenttables)
  * 4.6 [Distributed Table](#distributed-table)
    * 4.6.1 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable](#rqsrs-028clickhouseatomicinsertsdistributedtable)
    * 4.6.2 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ShardUnavailable](#rqsrs-028clickhouseatomicinsertsdistributedtableshardunavailable)
    * 4.6.3 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ReplicaUnavailable](#rqsrs-028clickhouseatomicinsertsdistributedtablereplicaunavailable)
    * 4.6.4 [RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.KeeperReadOnly](#rqsrs-028clickhouseatomicinsertsdistributedtablekeeperreadonly)
  * 4.7 [Multiple Tables](#multiple-tables)
    * 4.7.1 [RQ.SRS-028.ClickHouse.AtomicInserts.MultipleTables](#rqsrs-028clickhouseatomicinsertsmultipletables)
  * 4.8 [Data Duplication](#data-duplication)
    * 4.8.1 [RQ.SRS-028.ClickHouse.AtomicInserts.DataDuplication](#rqsrs-028clickhouseatomicinsertsdataduplication)
  * 4.9 [Failure Modes](#failure-modes)
      * 4.9.1.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OneOrMoreParts](#rqsrs-028clickhouseatomicinsertsfailuresoneormoreparts)
    * 4.9.2 [Syntax Error](#syntax-error)
      * 4.9.2.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SyntaxError](#rqsrs-028clickhouseatomicinsertsfailuressyntaxerror)
    * 4.9.3 [Mismatched Table Structure](#mismatched-table-structure)
      * 4.9.3.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.MismatchedTableStructure](#rqsrs-028clickhouseatomicinsertsfailuresmismatchedtablestructure)
    * 4.9.4 [Circular Dependent Tables](#circular-dependent-tables)
      * 4.9.4.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.CircularDependentTables](#rqsrs-028clickhouseatomicinsertsfailurescirculardependenttables)
    * 4.9.5 [Emulated Error](#emulated-error)
      * 4.9.5.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.EmulatedUsingThrowIf](#rqsrs-028clickhouseatomicinsertsfailuresemulatedusingthrowif)
    * 4.9.6 [Disk Corruption](#disk-corruption)
      * 4.9.6.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.DiskCorruption](#rqsrs-028clickhouseatomicinsertsfailuresdiskcorruption)
    * 4.9.7 [Slow Disk](#slow-disk)
        * 4.9.7.1.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SlowDisk](#rqsrs-028clickhouseatomicinsertsfailuresslowdisk)
    * 4.9.8 [User Rights](#user-rights)
      * 4.9.8.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.UserRights](#rqsrs-028clickhouseatomicinsertsfailuresuserrights)
    * 4.9.9 [Out of Sync Replicas](#out-of-sync-replicas)
      * 4.9.9.1 [RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OutOfSyncReplicas](#rqsrs-028clickhouseatomicinsertsfailuresoutofsyncreplicas)



## Introduction

This software requirements specification covers requirements related to [ClickHouse] 
transaction support.

## Related Resources

* https://github.com/ClickHouse/ClickHouse/issues/22086
* https://github.com/ClickHouse/ClickHouse/pull/24258
* https://docs.google.com/presentation/d/17EOqJ3lAnwGDVhFLTmKHB6BXnnE-xLyd/edit#slide=id.p1

## Terminology

### SRS

Software Requirements Specification

### Atomic Inserts

Insert that either completely succeeds or fails in the target table and its any dependent tables.

## Requirements

### RQ.SRS-028.ClickHouse.AtomicInserts
version: 1.0

[ClickHouse] SHALL support [atomic inserts].

### Insert Settings

#### RQ.SRS-028.ClickHouse.AtomicInserts.InsertSettings
version: 1.0 priority: 1.0

[ClickHouse] SHALL support all `INSERT` settings with atomic inserts.

The settings include the following:

*  `max_insert_block_size` – split insert into chunks
*  `min_insert_block_size_rows` – merge input into bigger chunks based on rows
*  `min_insert_block_size_bytes` – merge input into bigger chunks based on bytes
*  `input_format_parallel_parsing` – splits text input into chunks
*  `max_insert_threads` – number of threads to use during insert

### Blocks And Partitions

#### RQ.SRS-028.ClickHouse.AtomicInserts.BlocksAndPartitions
version: 1.0 priority: 1.0

[ClickHouse] SHALL support [atomic inserts] for the following cases:

* single block, single partition
* single block, multiple partitions
* multiple blocks, single partition
* multiple blocks, multiple partitions 

### Supported Table Engines

#### Merge Tree

##### RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.MergeTree
version: 1.0

[ClickHouse] SHALL support [atomic inserts] for all MergeTree table engines and their variants:

* MergeTree
* SummingMergeTree
* ReplacingMergeTree
* AggregatingMergeTree
* CollapsingMergeTree
* VersionedCollapsingMergeTree
* GraphiteMergeTree

#### Replicated Merge Tree

##### RQ.SRS-028.ClickHouse.AtomicInserts.SupportedTableEngines.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support [atomic inserts] for all ReplicatedMergeTree table engines and their variants:

* ReplicatedMergeTree
* ReplicatedSummingMergeTree
* ReplicatedReplacingMergeTree
* ReplicatedAggregatingMergeTree
* ReplicatedCollapsingMergeTree
* ReplicatedVersionedCollapsingMergeTree
* ReplicatedGraphiteMergeTree

### Dependent Tables

#### RQ.SRS-028.ClickHouse.AtomicInserts.DependentTables
version: 1.0 priority: 1.0

[ClickHouse] SHALL support [atomic inserts] when the following dependent tables are present: 

* one or more normal views
* single or cascading materialized view
* single or cascading window view
* one or more live views
* materialized with normal view
* materialized with live view
* materialized with window view
* window with materialized view
* window with normal view
* window with live view

### Distributed Table

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable
version: 1.0 priority: 2.0

[ClickHouse] SHALL support [atomic inserts] into distributed table
when `insert_distributed_sync` setting is enabled.

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ShardUnavailable
version: 1.0 priority: 2.0

[ClickHouse] SHALL abort [atomic inserts] if even one shard was not available.

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.ReplicaUnavailable
version: 1.0, priority: 2.0

[ClickHouse] SHALL abort [atomic inserts] if even one replica was not available.

#### RQ.SRS-028.ClickHouse.AtomicInserts.DistributedTable.KeeperReadOnly
version: 1.0 priority: 2.0

[ClickHouse] SHALL abort [atomic inserts] if ZooKeeper or Clickhouse Keeper has placed a table into 
a "read only" mode.

### Multiple Tables

#### RQ.SRS-028.ClickHouse.AtomicInserts.MultipleTables
version: 1.0 priority: 3.0

[ClickHouse] SHALL support [atomic inserts] into multiple tables as a single atomic transaction.

```sql
BEGIN TRANSACTION
INSERT INTO <table.a> ...
INSERT INTO <table.b> ...
...
COMMIT TRANSACTION
```

The insert into multiple tables SHALL only succeed if [atomic inserts] can succeed in all the tables.

### Data Duplication

#### RQ.SRS-028.ClickHouse.AtomicInserts.DataDuplication
version: 1.0 priority: 3.0

[ClickHouse] SHALL not allow data duplication when:

* user retries failed inserts
* presence of collisions in message bus (e.g. Kafka re-balances)

### Failure Modes

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OneOrMoreParts
version: 1.0 priority: 3.0

[ClickHouse] SHALL support [atomic inserts] in presence of fails to insert our or more parts
into target table or any of its dependent tables.

#### Syntax Error

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SyntaxError
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of a syntax error in the query.

#### Mismatched Table Structure

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.MismatchedTableStructure
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence failure to insert due to
mismatch in table structure that occures in the target table or one or its dependent tables.

Examples:

* different column data type
* missing columns

#### Circular Dependent Tables

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.CircularDependentTables
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of circular dependent tables.

#### Emulated Error

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.EmulatedUsingThrowIf
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of an emulated failure 
using [throwif] on a particular partition.

#### Disk Corruption

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.DiskCorruption
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of disk critically corrupted and cannot receive all the data.

#### Slow Disk

###### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.SlowDisk
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of one or more slow disks.

#### User Rights

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.UserRights
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of a query issues by a user that does not have
enough rights either on the target table or one of its dependent tables.

#### Out of Sync Replicas

##### RQ.SRS-028.ClickHouse.AtomicInserts.Failures.OutOfSyncReplicas
version: 1.0

[ClickHouse] SHALL support [atomic inserts] in presence of issues with data synchronicity on replicas.

[SRS]: #srs
[atomic inserts]: #attomic-inserts
[throwif]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions/#throwifx-custom-message
[ClickHouse]: https://clickhouse.com
""",
)

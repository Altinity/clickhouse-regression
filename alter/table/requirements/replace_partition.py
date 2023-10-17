# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.231001.1175523.
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
    num="7.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_System_Parts = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.System.Parts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support checking the partition values from the `system.parts` table.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT partition, formatReadableSize(sum(bytes))\n"
        "FROM system.parts\n"
        "WHERE table = 'table_1'\n"
        "GROUP BY partition\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.2.1",
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
        "|            Engines             |\n"
        "|:------------------------------:|\n"
        "|          `MergeTree`           |\n"
        "|     `ReplicatedMergeTree`      |\n"
        "|      `ReplacingMergeTree`      |\n"
        "|     `AggregatingMergeTree`     |\n"
        "|     `CollapsingMergeTree`      |\n"
        "| `VersionedCollapsingMergeTree` |\n"
        "|      `GraphiteMergeTree`       |\n"
        "|       `DistributedTable`       |\n"
        "|       `MaterializedView`       |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
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
    num="9.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NonExistentPartition = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NonExistentPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL keep the data of the destination partition when replacing partition form the non-existent partition.\n"
        "\n"
        "For example,\n"
        "\n"
        "If we try to copy the data partition from the `table1` to `table2` and replace existing partition in the `table2` on partition number `21` but this partition does not exist on `table1`.\n"
        "\n"
        "```sql\n"
        "ALTER TABLE table2 REPLACE PARTITION 21 FROM table1\n"
        "```\n"
        "\n"
        "The data on `table2` should not be deleted and an exception should be raised.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromTemporaryTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.FromTemporaryTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support copying the data partition from the temporary table.\n"
        "\n"
        "> A table that disappears when the session ends, including if the connection is lost, is considered a temporary table.\n"
        "\n"
        "For example,\n"
        "\n"
        "Let's say we have a MergeTree table named `destination`. If we create a temporary table and insert some values into it.\n"
        "\n"
        "```sql\n"
        "CREATE TEMPORARY TABLE temporary_table (p UInt64, k String, d UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY k;\n"
        "\n"
        "INSERT INTO temporary_table VALUES (0, '0', 1);\n"
        "INSERT INTO temporary_table VALUES (1, '0', 1);\n"
        "INSERT INTO temporary_table VALUES (1, '1', 1);\n"
        "INSERT INTO temporary_table VALUES (2, '0', 1);\n"
        "INSERT INTO temporary_table VALUES (3, '0', 1);\n"
        "INSERT INTO temporary_table VALUES (3, '1', 1);\n"
        "```\n"
        "\n"
        "We can use `REPLACE PARTITION` on the `destinaton` table from `temporary_table`,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE destinaton REPLACE PARTITION 1 FROM temporary_table;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTables = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTables",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support copying the data partition from the temporary table into another temporary table.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_IntoOutfile = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.IntoOutfile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `INTO OUTFILE` with `REPLACE PARTITION` and SHALL not output any errors.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Format = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Format",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `FORMAT` with `REPLACE PARTITION` and SHALL not output any errors.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Settings = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Settings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of the `SETTINGS` with `REPLACE PARTITION` and SHALL not output any errors.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="15.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Disks = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Disks",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Replacing partitions from one disk to another in the same table when tired storage is used.\n"
        "\n"
        "> When we have one table stored on different disks, and we want to replace partitions between partitions that are on different disks with `REPLACE PARTITION`.  \n"
        "\n"
    ),
    link=None,
    level=2,
    num="16.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between tables that are placed inside the S3 storage.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="17.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Replicas = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Replicas",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between replicas for tables with `ReplicatedMergeTree` engine.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="18.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Shards = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Shards",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between shards for tables with `DistributedTable` engine.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="19.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Versions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between different ClickHouse versions.\n"
        "\n"
        "> Users can create a new database with the target version and use `REPLACE PARTITION` to transfer data from the \n"
        "> old database to the new one, ensuring compatibility and benefits from new features.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Encodings = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encodings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between tables with different encodings.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="21.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Encryption = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between encrypted and not encrypted tables.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="22.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Deduplication = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Deduplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `REPLACE PARTITION` to replace data to a deduplication table, where duplicates are identified and eliminated.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="23.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `REPLACE PARTITION` command works with both source and destination tables. Each table can have its own partition type.\n"
        "\n"
        "| Partition Types                               |\n"
        "|-----------------------------------------------|\n"
        "| Partition with only compact parts             |\n"
        "| Partition with only wide parts                |\n"
        "| Partition with compact and wide parts (mixed) |\n"
        "| Partition with no parts                       |\n"
        "| Partition with empty parts                    |\n"
        "\n"
        "The `REPLACE PARTITION` SHALL work for any combination of partition types on both destination and source tables.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="24.1.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Corrupted_Wide = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Wide",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to `REPLACE PARTITION` when wide parts are corrupted for a destination table or a source table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="25.1.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Corrupted_Compact = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Compact",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to `REPLACE PARTITION` when compact parts are corrupted for a destination table or a source table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="25.2.1",
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
    level=3,
    num="26.1.1",
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
    level=3,
    num="26.2.1",
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
    level=3,
    num="26.3.1",
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
    level=3,
    num="26.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_OrderAndPartition = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.OrderAndPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when executing `ORDER BY` or `PARTITION BY` with the `REPLACE PARTITION` clause.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="27.1.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Merges = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Merges",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to run any merges before the executed `REPLACE PARTITION` is finished.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="27.2.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Mutations = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Mutations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to run any mutations before the executed `REPLACE PARTITION` is finished.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="27.3.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_TableFunctions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.TableFunctions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to use table functions after the `FROM` clause to replace partition of a table.\n"
        "\n"
        "For Example,\n"
        "\n"
        "```sql\n"
        "ALTER TABLE table_1 REPLACE PARTITION 2 FROM file(table_2.parquet)\n"
        "```\n"
        "\n"
        "The list of possible table functions,\n"
        "\n"
        "| Table Engines             |\n"
        "|---------------------------|\n"
        "| `azureBlobStorage`        |\n"
        "| `cluster`                 |\n"
        "| `deltaLake`               |\n"
        "| `dictionary`              |\n"
        "| `executable`              |\n"
        "| `azureBlobStorageCluster` |\n"
        "| `file`                    |\n"
        "| `format`                  |\n"
        "| `gcs`                     |\n"
        "| `generateRandom`          |\n"
        "| `hdfs`                    |\n"
        "| `hdfsCluster`             |\n"
        "| `hudi`                    |\n"
        "| `iceberg`                 |\n"
        "| `input`                   |\n"
        "| `jdbc`                    |\n"
        "| `merge`                   |\n"
        "| `mongodb`                 |\n"
        "| `mysql`                   |\n"
        "| `null function`           |\n"
        "| `numbers`                 |\n"
        "| `odbc`                    |\n"
        "| `postgresql`              |\n"
        "| `redis`                   |\n"
        "| `remote`                  |\n"
        "| `s3`                      |\n"
        "| `s3Cluster`               |\n"
        "| `sqlite`                  |\n"
        "| `url`                     |\n"
        "| `urlCluster`              |\n"
        "| `view`                    |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="27.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Subquery = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Subquery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to use subquery after the `FROM` clause to replace partition of a table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="27.5.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Join = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Join",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to use the `JOIN` clause after the `FROM` clause to replace partition of a table.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="27.6.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL make `REPLACE PARTITION` to wait for the ongoing mutations and partitions if they are running on the same partition as executed `REPLACE PARTITION`.\n"
        "\n"
        "For example,\n"
        "\n"
        "If we have two tables `table_1` and `table_2` and we populate them with columns `p` and `i`.\n"
        "\n"
        "```sql\n"
        "CREATE TABLE table_1\n"
        "(\n"
        "    `p` UInt8,\n"
        "    `i` UInt64\n"
        ")\n"
        "ENGINE = MergeTree\n"
        "PARTITION BY p\n"
        "ORDER BY tuple();\n"
        "```\n"
        "\n"
        "Run the `INESRT` that will result in two partitions.\n"
        "\n"
        "```sql\n"
        "INSERT INTO table_1 VALUES (1, 1), (2, 2);\n"
        "```\n"
        "\n"
        "If a lot of merges or mutations happen on partition number one and in the meantime we do `REPLACE PARTITION` on partition number two.\n"
        "\n"
        "> In this case partition number one is values (1, 1) and number two (2, 2) inside the `table_1`.\n"
        "\n"
        "```sql\n"
        "INSERT INTO table_1 (p, i) SELECT 1, number FROM numbers(100);\n"
        "ALTER TABLE table_1 ADD COLUMN make_merge_slower UInt8 DEFAULT sleepEachRow(0.03);\n"
        "\n"
        "ALTER TABLE table_1 REPLACE PARTITION id '2' FROM t2;\n"
        "```\n"
        "\n"
        "`REPLACE PARTITION` SHALL complete right away since there are no merges happening on this partition at the moment.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="28.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Insert = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Insert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `INSERT INTO TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="28.2.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Delete = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Delete",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DELETE FROM` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="28.3.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Attach = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Attach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `ATTACH TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="28.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Detach = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Detach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `DETACH TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="28.5.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Optimize = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Optimize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `OPTIMIZE TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="28.6.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Add = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Add",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `ADD COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.7.1.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Drop = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Drop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DROP COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.7.2.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Clear = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Clear",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DROP COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.7.3.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Modify = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Modify",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MODIFY COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.7.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_ModifyRemove = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.ModifyRemove",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MODIFY COLUMN REMOVE` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.7.5.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Materialize = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Materialize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MATERIALIZE REMOVE` is used on, when `REPLACE PARTITION` is executed on this partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.7.6.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish when another operation related to partition manipulation is being executed.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="28.8.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Detach = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Detach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DETACH PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.2.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Drop = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Drop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DROP PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.3.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Attach = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Attach",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `ATTACH PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.4.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_AttachFrom = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.AttachFrom",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `ATTACH PARTITION FROM` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.5.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Replace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing another `REPLACE PARTITION` on the same partition.\n"
        "\n"
        "For example,\n"
        "\n"
        "> If we run `REPLACE PARTITION` to replace the data partition from the `table1` to `table2` and replaces existing partition in the `table2`, \n"
        "> but at the same time try to replace partition of another table from `table2`, the first process should finish and only after that the second `REPLACE PARTITION` SHALL be executed.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.6.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_MoveToTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.MoveToTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `MOVE PARTITION TO TABLE` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.7.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearColumnInPartition = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearColumnInPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `CLEAR COLUMN IN PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.8.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Freeze",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `FREEZE PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.9.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Unfreeze = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Unfreeze",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `UNFREEZE PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.10.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearIndex = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearIndex",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `CLEAR INDEX IN PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.11.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Fetch = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Fetch",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `FETCH PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.12.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Move = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Move",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `MOVE PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.13.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_UpdateInPartition = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.UpdateInPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `UPDATE IN PARTITION` on the same partition.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.14.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_DeleteInPartition = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.DeleteInPartition",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DELETE IN PARTITION` on the same partition.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="28.8.15.1",
)

RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_RBAC = Requirement(
    name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.RBAC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `REPLACE PARTITION` command works with both source and destination tables. Each table can have its own privileges.\n"
        "\n"
        "```sql\n"
        "ALTER TABLE table2 REPLACE PARTITION 21 FROM table1\n"
        "```\n"
        "\n"
        "| Privileges              |\n"
        "|-------------------------|\n"
        "| No privileges           |\n"
        "| SELECT                  |\n"
        "| INSERT                  |\n"
        "| ALTER                   |\n"
        "| ALTER TABLE             |\n"
        "| ALTER REPLACE PARTITION |\n"
        "\n"
        "The `REPLACE PARTITION` SHALL only work when the user has the following privileges for the source and destination tables:\n"
        "\n"
        "| Source | Destination |\n"
        "|--------|-------------|\n"
        "| ALTER  | SELECT      |\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=2,
    num="29.1",
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
        Heading(name="Definitions", level=1, num="5"),
        Heading(name="User Actions", level=1, num="6"),
        Heading(name="Replace Partition", level=1, num="7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition",
            level=2,
            num="7.1",
        ),
        Heading(
            name="Check Existing Partitions From The Parts Table", level=2, num="7.2"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.System.Parts",
            level=3,
            num="7.2.1",
        ),
        Heading(name="Table Engines", level=1, num="8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TableEngines",
            level=2,
            num="8.1",
        ),
        Heading(name="Keeping Data When Replacing Partitions", level=1, num="9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData",
            level=2,
            num="9.1",
        ),
        Heading(
            name="Keeping Data When Replacing Partition From Non-Existent Partition",
            level=1,
            num="10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NonExistentPartition",
            level=2,
            num="10.1",
        ),
        Heading(name="Replacing Partitions From Temporary Table", level=1, num="11"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.FromTemporaryTable",
            level=2,
            num="11.1",
        ),
        Heading(
            name="Replacing Partitions Between Temporary Tables", level=1, num="12"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTables",
            level=2,
            num="12.1",
        ),
        Heading(name="Using Into Outfile With Replace Partition", level=1, num="13"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.IntoOutfile",
            level=2,
            num="13.1",
        ),
        Heading(name="Using Format With Replace Partition", level=1, num="14"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Format",
            level=2,
            num="14.1",
        ),
        Heading(name="Using Settings With Replace Partition", level=1, num="15"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Settings",
            level=2,
            num="15.1",
        ),
        Heading(
            name="Replacing Partitions From One Disk To Another In The Same Table",
            level=1,
            num="16",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Disks",
            level=2,
            num="16.1",
        ),
        Heading(name="Replacing Partitions Between Tables On S3", level=1, num="17"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.S3",
            level=2,
            num="17.1",
        ),
        Heading(name="Replacing Partitions Between Replicas", level=1, num="18"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Replicas",
            level=2,
            num="18.1",
        ),
        Heading(name="Replacing Partitions Between Shards", level=1, num="19"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Shards",
            level=2,
            num="19.1",
        ),
        Heading(
            name="Replacing Partitions Between Different ClickHouse versions",
            level=1,
            num="20",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Versions",
            level=2,
            num="20.1",
        ),
        Heading(
            name="Replacing Partitions Between Different Encodings", level=1, num="21"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encodings",
            level=2,
            num="21.1",
        ),
        Heading(
            name="Replacing Partitions Between Encrypted And Unencrypted Tables",
            level=1,
            num="22",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encryption",
            level=2,
            num="22.1",
        ),
        Heading(name="Replacing Partitions To Deduplication Tables", level=1, num="23"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Deduplication",
            level=2,
            num="23.1",
        ),
        Heading(name="Compact and Wide Parts", level=1, num="24"),
        Heading(
            name="Replace Partition Between Different Partition Types",
            level=2,
            num="24.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionTypes",
            level=3,
            num="24.1.1",
        ),
        Heading(name="Corrupted Parts", level=1, num="25"),
        Heading(
            name="Replacing Partition Between Tables With Corrupted Wide Parts",
            level=2,
            num="25.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Wide",
            level=3,
            num="25.1.1",
        ),
        Heading(
            name="Replacing Partition Between Tables With Corrupted Compact Parts",
            level=2,
            num="25.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Compact",
            level=3,
            num="25.2.1",
        ),
        Heading(name="Conditions", level=1, num="26"),
        Heading(
            name="Rules For Replacing Partitions Between Tables", level=2, num="26.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions",
            level=3,
            num="26.1.1",
        ),
        Heading(
            name="Replacing Partitions Between Tables With Different Structure",
            level=2,
            num="26.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure",
            level=3,
            num="26.2.1",
        ),
        Heading(
            name="Replacing Partitions Between Tables With Different Partition Key",
            level=2,
            num="26.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key",
            level=3,
            num="26.3.1",
        ),
        Heading(
            name="Replacing Partitions Between Tables With Different Storage Policy",
            level=2,
            num="26.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy",
            level=3,
            num="26.4.1",
        ),
        Heading(name="Prohibited Actions", level=1, num="27"),
        Heading(
            name="Using Order By and Partition By When Replacing Partitions Between Tables",
            level=2,
            num="27.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.OrderAndPartition",
            level=3,
            num="27.1.1",
        ),
        Heading(
            name="Staring New Merges With Ongoing Replace Partition",
            level=2,
            num="27.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Merges",
            level=3,
            num="27.2.1",
        ),
        Heading(
            name="Staring New Mutations With Ongoing Replace Partition",
            level=2,
            num="27.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Mutations",
            level=3,
            num="27.3.1",
        ),
        Heading(name="Replacing Partitions With Table Functions", level=2, num="27.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.TableFunctions",
            level=3,
            num="27.4.1",
        ),
        Heading(name="Replacing Partitions With Subquery", level=2, num="27.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Subquery",
            level=3,
            num="27.5.1",
        ),
        Heading(name="Replacing Partitions With Join Clause", level=2, num="27.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Join",
            level=3,
            num="27.6.1",
        ),
        Heading(
            name="Replacing Partitions During Ongoing Merges and Mutations",
            level=1,
            num="28",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent",
            level=2,
            num="28.1",
        ),
        Heading(name="Insert Into Table", level=2, num="28.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Insert",
            level=3,
            num="28.2.1",
        ),
        Heading(name="Delete Table", level=2, num="28.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Delete",
            level=3,
            num="28.3.1",
        ),
        Heading(name="Attach Table", level=2, num="28.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Attach",
            level=3,
            num="28.4.1",
        ),
        Heading(name="Detach Table", level=2, num="28.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Detach",
            level=3,
            num="28.5.1",
        ),
        Heading(name="Optimize Table", level=2, num="28.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Optimize",
            level=3,
            num="28.6.1",
        ),
        Heading(name="Alter", level=2, num="28.7"),
        Heading(name="Add Column", level=3, num="28.7.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Add",
            level=4,
            num="28.7.1.1",
        ),
        Heading(name="Drop Column", level=3, num="28.7.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Drop",
            level=4,
            num="28.7.2.1",
        ),
        Heading(name="Clear Column", level=3, num="28.7.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Clear",
            level=4,
            num="28.7.3.1",
        ),
        Heading(name="Modify Column", level=3, num="28.7.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Modify",
            level=4,
            num="28.7.4.1",
        ),
        Heading(name="Modify Column Remove", level=3, num="28.7.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.ModifyRemove",
            level=4,
            num="28.7.5.1",
        ),
        Heading(name="Materialize", level=3, num="28.7.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Materialize",
            level=4,
            num="28.7.6.1",
        ),
        Heading(name="Manipulating Partitions", level=2, num="28.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions",
            level=3,
            num="28.8.1",
        ),
        Heading(name="Detach", level=3, num="28.8.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Detach",
            level=4,
            num="28.8.2.1",
        ),
        Heading(name="Drop", level=3, num="28.8.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Drop",
            level=4,
            num="28.8.3.1",
        ),
        Heading(name="Attach", level=3, num="28.8.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Attach",
            level=4,
            num="28.8.4.1",
        ),
        Heading(name="Attach From", level=3, num="28.8.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.AttachFrom",
            level=4,
            num="28.8.5.1",
        ),
        Heading(name="Replace", level=3, num="28.8.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Replace",
            level=4,
            num="28.8.6.1",
        ),
        Heading(name="Move To Table", level=3, num="28.8.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.MoveToTable",
            level=4,
            num="28.8.7.1",
        ),
        Heading(name="Clear Column In Partition", level=3, num="28.8.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearColumnInPartition",
            level=4,
            num="28.8.8.1",
        ),
        Heading(name="Freeze", level=3, num="28.8.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Freeze",
            level=4,
            num="28.8.9.1",
        ),
        Heading(name="Unfreeze", level=3, num="28.8.10"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Unfreeze",
            level=4,
            num="28.8.10.1",
        ),
        Heading(name="Clear Index", level=3, num="28.8.11"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearIndex",
            level=4,
            num="28.8.11.1",
        ),
        Heading(name="Fetch", level=3, num="28.8.12"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Fetch",
            level=4,
            num="28.8.12.1",
        ),
        Heading(name="Move", level=3, num="28.8.13"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Move",
            level=4,
            num="28.8.13.1",
        ),
        Heading(name="Update In", level=3, num="28.8.14"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.UpdateInPartition",
            level=4,
            num="28.8.14.1",
        ),
        Heading(name="Delete In", level=3, num="28.8.15"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.DeleteInPartition",
            level=4,
            num="28.8.15.1",
        ),
        Heading(name="Role Based Access Control", level=1, num="29"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.RBAC",
            level=2,
            num="29.1",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_System_Parts,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TableEngines,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_KeepData,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NonExistentPartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromTemporaryTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTables,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_IntoOutfile,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Format,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Settings,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Disks,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_S3,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Replicas,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Shards,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Encodings,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Encryption,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Deduplication,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionTypes,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Corrupted_Wide,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Corrupted_Compact,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Structure,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Key,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_StoragePolicy,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_OrderAndPartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Merges,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Mutations,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_TableFunctions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Subquery,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Join,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Insert,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Delete,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Attach,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Detach,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Optimize,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Add,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Drop,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Clear,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Modify,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_ModifyRemove,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Materialize,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Detach,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Drop,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Attach,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_AttachFrom,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_MoveToTable,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearColumnInPartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Unfreeze,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearIndex,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Fetch,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Move,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_UpdateInPartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_DeleteInPartition,
        RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_RBAC,
    ),
    content="""
# SRS032 ClickHouse Alter Table Replace Partition

# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Flowchart](#flowchart)
* 4 [Definitions](#definitions)
* 5 [User Actions](#user-actions)
* 6 [Replace Partition](#replace-partition)
    * 6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition](#rqsrs-032clickhousealtertablereplacepartition)
    * 6.2 [Check Existing Partitions From The Parts Table](#check-existing-partitions-from-the-parts-table)
        * 6.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.System.Parts](#rqsrs-032clickhousealtertablereplacepartitionsystemparts)
* 7 [Table Engines](#table-engines)
    * 7.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TableEngines](#rqsrs-032clickhousealtertablereplacepartitiontableengines)
* 8 [Keeping Data When Replacing Partitions](#keeping-data-when-replacing-partitions)
    * 8.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData](#rqsrs-032clickhousealtertablereplacepartitionkeepdata)
* 9 [Keeping Data When Replacing Partition From Non-Existent Partition](#keeping-data-when-replacing-partition-from-non-existent-partition)
    * 9.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NonExistentPartition](#rqsrs-032clickhousealtertablereplacepartitionnonexistentpartition)
* 10 [Replacing Partitions From Temporary Table](#replacing-partitions-from-temporary-table)
    * 10.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.FromTemporaryTable](#rqsrs-032clickhousealtertablereplacepartitionfromtemporarytable)
* 11 [Replacing Partitions Between Temporary Tables](#replacing-partitions-between-temporary-tables)
    * 11.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTables](#rqsrs-032clickhousealtertablereplacepartitiontemporarytables)
* 12 [Using Into Outfile With Replace Partition](#using-into-outfile-with-replace-partition)
    * 12.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.IntoOutfile](#rqsrs-032clickhousealtertablereplacepartitionintooutfile)
* 13 [Using Format With Replace Partition](#using-format-with-replace-partition)
    * 13.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Format](#rqsrs-032clickhousealtertablereplacepartitionformat)
* 14 [Using Settings With Replace Partition](#using-settings-with-replace-partition)
    * 14.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Settings](#rqsrs-032clickhousealtertablereplacepartitionsettings)
* 15 [Replacing Partitions From One Disk To Another In The Same Table](#replacing-partitions-from-one-disk-to-another-in-the-same-table)
    * 15.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Disks](#rqsrs-032clickhousealtertablereplacepartitiondisks)
* 16 [Replacing Partitions Between Tables On S3](#replacing-partitions-between-tables-on-s3)
    * 16.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.S3](#rqsrs-032clickhousealtertablereplacepartitions3)
* 17 [Replacing Partitions Between Replicas](#replacing-partitions-between-replicas)
    * 17.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Replicas](#rqsrs-032clickhousealtertablereplacepartitionreplicas)
* 18 [Replacing Partitions Between Shards](#replacing-partitions-between-shards)
    * 18.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Shards](#rqsrs-032clickhousealtertablereplacepartitionshards)
* 19 [Replacing Partitions Between Different ClickHouse versions](#replacing-partitions-between-different-clickhouse-versions)
    * 19.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Versions](#rqsrs-032clickhousealtertablereplacepartitionversions)
* 20 [Replacing Partitions Between Different Encodings](#replacing-partitions-between-different-encodings)
    * 20.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encodings](#rqsrs-032clickhousealtertablereplacepartitionencodings)
* 21 [Replacing Partitions Between Encrypted And Unencrypted Tables](#replacing-partitions-between-encrypted-and-unencrypted-tables)
    * 21.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encryption](#rqsrs-032clickhousealtertablereplacepartitionencryption)
* 22 [Replacing Partitions To Deduplication Tables](#replacing-partitions-to-deduplication-tables)
    * 22.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Deduplication](#rqsrs-032clickhousealtertablereplacepartitiondeduplication)
* 23 [Compact and Wide Parts](#compact-and-wide-parts)
    * 23.1 [Replace Partition Between Different Partition Types](#replace-partition-between-different-partition-types)
        * 23.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionTypes](#rqsrs-032clickhousealtertablereplacepartitionpartitiontypes)
* 24 [Corrupted Parts](#corrupted-parts)
    * 24.1 [Replacing Partition Between Tables With Corrupted Wide Parts](#replacing-partition-between-tables-with-corrupted-wide-parts)
        * 24.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Wide](#rqsrs-032clickhousealtertablereplacepartitioncorruptedwide)
    * 24.2 [Replacing Partition Between Tables With Corrupted Compact Parts](#replacing-partition-between-tables-with-corrupted-compact-parts)
        * 24.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Compact](#rqsrs-032clickhousealtertablereplacepartitioncorruptedcompact)
* 25 [Conditions](#conditions)
    * 25.1 [Rules For Replacing Partitions Between Tables](#rules-for-replacing-partitions-between-tables)
        * 25.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions](#rqsrs-032clickhousealtertablereplacepartitionconditions)
    * 25.2 [Replacing Partitions Between Tables With Different Structure](#replacing-partitions-between-tables-with-different-structure)
        * 25.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentstructure)
    * 25.3 [Replacing Partitions Between Tables With Different Partition Key](#replacing-partitions-between-tables-with-different-partition-key)
        * 25.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentkey)
    * 25.4 [Replacing Partitions Between Tables With Different Storage Policy](#replacing-partitions-between-tables-with-different-storage-policy)
        * 25.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy](#rqsrs-032clickhousealtertablereplacepartitionconditionsdifferentstoragepolicy)
* 26 [Prohibited Actions](#prohibited-actions)
    * 26.1 [Using Order By and Partition By When Replacing Partitions Between Tables](#using-order-by-and-partition-by-when-replacing-partitions-between-tables)
        * 26.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.OrderAndPartition](#rqsrs-032clickhousealtertablereplacepartitionprohibitedorderandpartition)
    * 26.2 [Staring New Merges With Ongoing Replace Partition](#staring-new-merges-with-ongoing-replace-partition)
        * 26.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Merges](#rqsrs-032clickhousealtertablereplacepartitionprohibitedmerges)
    * 26.3 [Staring New Mutations With Ongoing Replace Partition](#staring-new-mutations-with-ongoing-replace-partition)
        * 26.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Mutations](#rqsrs-032clickhousealtertablereplacepartitionprohibitedmutations)
    * 26.4 [Replacing Partitions With Table Functions](#replacing-partitions-with-table-functions)
        * 26.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.TableFunctions](#rqsrs-032clickhousealtertablereplacepartitionprohibitedtablefunctions)
    * 26.5 [Replacing Partitions With Subquery](#replacing-partitions-with-subquery)
        * 26.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Subquery](#rqsrs-032clickhousealtertablereplacepartitionprohibitedsubquery)
    * 26.6 [Replacing Partitions With Join Clause](#replacing-partitions-with-join-clause)
        * 26.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Join](#rqsrs-032clickhousealtertablereplacepartitionprohibitedjoin)
* 27 [Replacing Partitions During Ongoing Merges and Mutations](#replacing-partitions-during-ongoing-merges-and-mutations)
    * 27.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent](#rqsrs-032clickhousealtertablereplacepartitionconcurrent)
    * 27.2 [Insert Into Table](#insert-into-table)
        * 27.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Insert](#rqsrs-032clickhousealtertablereplacepartitionconcurrentinsert)
    * 27.3 [Delete Table](#delete-table)
        * 27.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Delete](#rqsrs-032clickhousealtertablereplacepartitionconcurrentdelete)
    * 27.4 [Attach Table](#attach-table)
        * 27.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Attach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentattach)
    * 27.5 [Detach Table](#detach-table)
        * 27.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Detach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentdetach)
    * 27.6 [Optimize Table](#optimize-table)
        * 27.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Optimize](#rqsrs-032clickhousealtertablereplacepartitionconcurrentoptimize)
    * 27.7 [Alter](#alter)
        * 27.7.1 [Add Column](#add-column)
            * 27.7.1.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Add](#rqsrs-032clickhousealtertablereplacepartitionconcurrentalteradd)
        * 27.7.2 [Drop Column](#drop-column)
            * 27.7.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Drop](#rqsrs-032clickhousealtertablereplacepartitionconcurrentalterdrop)
        * 27.7.3 [Clear Column](#clear-column)
            * 27.7.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Clear](#rqsrs-032clickhousealtertablereplacepartitionconcurrentalterclear)
        * 27.7.4 [Modify Column](#modify-column)
            * 27.7.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Modify](#rqsrs-032clickhousealtertablereplacepartitionconcurrentaltermodify)
        * 27.7.5 [Modify Column Remove](#modify-column-remove)
            * 27.7.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.ModifyRemove](#rqsrs-032clickhousealtertablereplacepartitionconcurrentaltermodifyremove)
        * 27.7.6 [Materialize](#materialize)
            * 27.7.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Materialize](#rqsrs-032clickhousealtertablereplacepartitionconcurrentaltermaterialize)
    * 27.8 [Manipulating Partitions](#manipulating-partitions)
        * 27.8.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitions)
        * 27.8.2 [Detach](#detach)
            * 27.8.2.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Detach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsdetach)
        * 27.8.3 [Drop](#drop)
            * 27.8.3.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Drop](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsdrop)
        * 27.8.4 [Attach](#attach)
            * 27.8.4.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Attach](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsattach)
        * 27.8.5 [Attach From](#attach-from)
            * 27.8.5.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.AttachFrom](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsattachfrom)
        * 27.8.6 [Replace](#replace)
            * 27.8.6.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Replace](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsreplace)
        * 27.8.7 [Move To Table](#move-to-table)
            * 27.8.7.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.MoveToTable](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsmovetotable)
        * 27.8.8 [Clear Column In Partition](#clear-column-in-partition)
            * 27.8.8.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearColumnInPartition](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsclearcolumninpartition)
        * 27.8.9 [Freeze](#freeze)
            * 27.8.9.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Freeze](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsfreeze)
        * 27.8.10 [Unfreeze](#unfreeze)
            * 27.8.10.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Unfreeze](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsunfreeze)
        * 27.8.11 [Clear Index](#clear-index)
            * 27.8.11.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearIndex](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsclearindex)
        * 27.8.12 [Fetch](#fetch)
            * 27.8.12.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Fetch](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsfetch)
        * 27.8.13 [Move](#move)
            * 27.8.13.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Move](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsmove)
        * 27.8.14 [Update In](#update-in)
            * 27.8.14.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.UpdateInPartition](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsupdateinpartition)
        * 27.8.15 [Delete In](#delete-in)
            * 27.8.15.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.DeleteInPartition](#rqsrs-032clickhousealtertablereplacepartitionconcurrentmanipulatingpartitionsdeleteinpartition)
* 28 [Role Based Access Control](#role-based-access-control)
    * 28.1 [RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.RBAC](#rqsrs-032clickhousealtertablereplacepartitionrbac)

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

## Definitions

Source Table - The table from which a partition is taken.
Destination Table - The table in which a specific partition is going to be replaced..


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

### Check Existing Partitions From The Parts Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.System.Parts
version: 1.0

[ClickHouse] SHALL support checking the partition values from the `system.parts` table.

For example,

```sql
SELECT partition, formatReadableSize(sum(bytes))
FROM system.parts
WHERE table = 'table_1'
GROUP BY partition
```

## Table Engines

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TableEngines
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` for the following table engines,

|            Engines             |
|:------------------------------:|
|          `MergeTree`           |
|     `ReplicatedMergeTree`      |
|      `ReplacingMergeTree`      |
|     `AggregatingMergeTree`     |
|     `CollapsingMergeTree`      |
| `VersionedCollapsingMergeTree` |
|      `GraphiteMergeTree`       |
|       `DistributedTable`       |
|       `MaterializedView`       |


## Keeping Data When Replacing Partitions

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.KeepData
version: 1.0

[ClickHouse] SHALL keep the data of the table from which the partition is copied from.

## Keeping Data When Replacing Partition From Non-Existent Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.NonExistentPartition
version: 1.0

[ClickHouse] SHALL keep the data of the destination partition when replacing partition form the non-existent partition.

For example,

If we try to copy the data partition from the `table1` to `table2` and replace existing partition in the `table2` on partition number `21` but this partition does not exist on `table1`.

```sql
ALTER TABLE table2 REPLACE PARTITION 21 FROM table1
```

The data on `table2` should not be deleted and an exception should be raised.

## Replacing Partitions From Temporary Table

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.FromTemporaryTable
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table.

> A table that disappears when the session ends, including if the connection is lost, is considered a temporary table.

For example,

Let's say we have a MergeTree table named `destination`. If we create a temporary table and insert some values into it.

```sql
CREATE TEMPORARY TABLE temporary_table (p UInt64, k String, d UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY k;

INSERT INTO temporary_table VALUES (0, '0', 1);
INSERT INTO temporary_table VALUES (1, '0', 1);
INSERT INTO temporary_table VALUES (1, '1', 1);
INSERT INTO temporary_table VALUES (2, '0', 1);
INSERT INTO temporary_table VALUES (3, '0', 1);
INSERT INTO temporary_table VALUES (3, '1', 1);
```

We can use `REPLACE PARTITION` on the `destinaton` table from `temporary_table`,

```sql
ALTER TABLE destinaton REPLACE PARTITION 1 FROM temporary_table;
```

## Replacing Partitions Between Temporary Tables

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.TemporaryTables
version: 1.0

[ClickHouse] SHALL support copying the data partition from the temporary table into another temporary table.

## Using Into Outfile With Replace Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.IntoOutfile
version: 1.0

[ClickHouse] SHALL support the usage of the `INTO OUTFILE` with `REPLACE PARTITION` and SHALL not output any errors.

## Using Format With Replace Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Format
version: 1.0

[ClickHouse] SHALL support the usage of the `FORMAT` with `REPLACE PARTITION` and SHALL not output any errors.

## Using Settings With Replace Partition

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Settings
version: 1.0

[ClickHouse] SHALL support the usage of the `SETTINGS` with `REPLACE PARTITION` and SHALL not output any errors.

## Replacing Partitions From One Disk To Another In The Same Table

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Disks
version: 1.0

[ClickHouse] SHALL support Replacing partitions from one disk to another in the same table when tired storage is used.

> When we have one table stored on different disks, and we want to replace partitions between partitions that are on different disks with `REPLACE PARTITION`.  

## Replacing Partitions Between Tables On S3

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.S3
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between tables that are placed inside the S3 storage.

## Replacing Partitions Between Replicas

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Replicas
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between replicas for tables with `ReplicatedMergeTree` engine.

## Replacing Partitions Between Shards

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Shards
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between shards for tables with `DistributedTable` engine.

## Replacing Partitions Between Different ClickHouse versions

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Versions
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between different ClickHouse versions.

> Users can create a new database with the target version and use `REPLACE PARTITION` to transfer data from the 
> old database to the new one, ensuring compatibility and benefits from new features.

## Replacing Partitions Between Different Encodings

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encodings
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between tables with different encodings.

## Replacing Partitions Between Encrypted And Unencrypted Tables

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Encryption
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace partitions between encrypted and not encrypted tables.

## Replacing Partitions To Deduplication Tables

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Deduplication
version: 1.0

[ClickHouse] SHALL support using `REPLACE PARTITION` to replace data to a deduplication table, where duplicates are identified and eliminated.

## Compact and Wide Parts

In ClickHouse, a physical file on a disk that stores a portion of the table’s data is called a “part”. There are two types of parts
* `Wide Parts` - Each column is stored in a separate file in a filesystem.
* `Compact Parts` - All columns are stored in one file in a filesystem.

```mermaid
graph LR
    subgraph Part Types
        subgraph Wide
        A1[ClickHouse Table] -->|Partition| B1[Parts]
        B1 --> C1{File system}
        C1 --> |Column| D1[fas:fa-file File1]
        C1 --> |Column| E1[fas:fa-file File2]
        C1 --> |Column| F1[fas:fa-file File3]
        end

        subgraph Compact
        A2[ClickHouse Table] -->|Partition| B2[Parts]
        B2 --> C2{File system}
        C2 --> |All Columns| D2[fas:fa-file File]
        end
    end
```

Data storing format is controlled by the `min_bytes_for_wide_part` and `min_rows_for_wide_part` settings of the `MergeTree` table.

When a specific part is less than the values of `min_bytes_for_wide_part` or `min_rows_for_wide_part`, then it's considered a compact part.

### Replace Partition Between Different Partition Types

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.PartitionTypes
version: 1.0

The `REPLACE PARTITION` command works with both source and destination tables. Each table can have its own partition type.

| Partition Types                               |
|-----------------------------------------------|
| Partition with only compact parts             |
| Partition with only wide parts                |
| Partition with compact and wide parts (mixed) |
| Partition with no parts                       |
| Partition with empty parts                    |

The `REPLACE PARTITION` SHALL work for any combination of partition types on both destination and source tables.

## Corrupted Parts

### Replacing Partition Between Tables With Corrupted Wide Parts

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Wide
version: 1.0

[ClickHouse] SHALL output an error when trying to `REPLACE PARTITION` when wide parts are corrupted for a destination table or a source table.

### Replacing Partition Between Tables With Corrupted Compact Parts

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Corrupted.Compact
version: 1.0

[ClickHouse] SHALL output an error when trying to `REPLACE PARTITION` when compact parts are corrupted for a destination table or a source table.

## Conditions

### Rules For Replacing Partitions Between Tables

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions
version: 1.0

[ClickHouse] SHALL support the usage of `REPLACE PARTITION` between two tables only when,

* Both tables have the same structure.
* Both tables have the same partition key, the same `ORDER BY` key, and the same primary key.
* Both tables have the same storage policy.

### Replacing Partitions Between Tables With Different Structure

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Structure
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different structure.

### Replacing Partitions Between Tables With Different Partition Key

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.Key
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different partition
key, `ORDER BY` key and primary key.

### Replacing Partitions Between Tables With Different Storage Policy

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Conditions.Different.StoragePolicy
version: 1.0

[ClickHouse] SHALL not support the usage of `REPLACE PARTITION` between two tables when tables have different storage
policy.

## Prohibited Actions

### Using Order By and Partition By When Replacing Partitions Between Tables

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.OrderAndPartition
version: 1.0

[ClickHouse] SHALL output an error when executing `ORDER BY` or `PARTITION BY` with the `REPLACE PARTITION` clause.

### Staring New Merges With Ongoing Replace Partition

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Merges
version: 1.0

[ClickHouse] SHALL output an error when trying to run any merges before the executed `REPLACE PARTITION` is finished.

### Staring New Mutations With Ongoing Replace Partition

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Mutations
version: 1.0

[ClickHouse] SHALL output an error when trying to run any mutations before the executed `REPLACE PARTITION` is finished.

### Replacing Partitions With Table Functions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.TableFunctions
version: 1.0

[ClickHouse] SHALL output an error when trying to use table functions after the `FROM` clause to replace partition of a table.

For Example,

```sql
ALTER TABLE table_1 REPLACE PARTITION 2 FROM file(table_2.parquet)
```

The list of possible table functions,

| Table Engines             |
|---------------------------|
| `azureBlobStorage`        |
| `cluster`                 |
| `deltaLake`               |
| `dictionary`              |
| `executable`              |
| `azureBlobStorageCluster` |
| `file`                    |
| `format`                  |
| `gcs`                     |
| `generateRandom`          |
| `hdfs`                    |
| `hdfsCluster`             |
| `hudi`                    |
| `iceberg`                 |
| `input`                   |
| `jdbc`                    |
| `merge`                   |
| `mongodb`                 |
| `mysql`                   |
| `null function`           |
| `numbers`                 |
| `odbc`                    |
| `postgresql`              |
| `redis`                   |
| `remote`                  |
| `s3`                      |
| `s3Cluster`               |
| `sqlite`                  |
| `url`                     |
| `urlCluster`              |
| `view`                    |


### Replacing Partitions With Subquery

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Subquery
version: 1.0

[ClickHouse] SHALL output an error when trying to use subquery after the `FROM` clause to replace partition of a table.

### Replacing Partitions With Join Clause

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Prohibited.Join
version: 1.0

[ClickHouse] SHALL output an error when trying to use the `JOIN` clause after the `FROM` clause to replace partition of a table.

## Replacing Partitions During Ongoing Merges and Mutations

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent
version: 1.0

[ClickHouse] SHALL make `REPLACE PARTITION` to wait for the ongoing mutations and partitions if they are running on the same partition as executed `REPLACE PARTITION`.

For example,

If we have two tables `table_1` and `table_2` and we populate them with columns `p` and `i`.

```sql
CREATE TABLE table_1
(
    `p` UInt8,
    `i` UInt64
)
ENGINE = MergeTree
PARTITION BY p
ORDER BY tuple();
```

Run the `INESRT` that will result in two partitions.

```sql
INSERT INTO table_1 VALUES (1, 1), (2, 2);
```

If a lot of merges or mutations happen on partition number one and in the meantime we do `REPLACE PARTITION` on partition number two.

> In this case partition number one is values (1, 1) and number two (2, 2) inside the `table_1`.

```sql
INSERT INTO table_1 (p, i) SELECT 1, number FROM numbers(100);
ALTER TABLE table_1 ADD COLUMN make_merge_slower UInt8 DEFAULT sleepEachRow(0.03);

ALTER TABLE table_1 REPLACE PARTITION id '2' FROM t2;
```

`REPLACE PARTITION` SHALL complete right away since there are no merges happening on this partition at the moment.

### Insert Into Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Insert
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `INSERT INTO TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Delete Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Delete
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DELETE FROM` is used on, when `REPLACE PARTITION` is executed on this partition.

### Attach Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Attach
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `ATTACH TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Detach Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Detach
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `DETACH TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Optimize Table

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Optimize
version: 1.0

[ClickHouse] SHALL stop background merges, that are still in progress, for the partition `OPTIMIZE TABLE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Alter

#### Add Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Add
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `ADD COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Drop Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Drop
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DROP COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Clear Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Clear
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `DROP COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Modify Column

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Modify
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MODIFY COLUMN` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Modify Column Remove

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.ModifyRemove
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MODIFY COLUMN REMOVE` is used on, when `REPLACE PARTITION` is executed on this partition.

#### Materialize

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Alter.Materialize
version: 1.0

[ClickHouse] SHALL stop background mutations, that are still in progress, for the partition `MATERIALIZE REMOVE` is used on, when `REPLACE PARTITION` is executed on this partition.

### Manipulating Partitions

#### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish when another operation related to partition manipulation is being executed.

#### Detach

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Detach
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DETACH PARTITION` on the same partition.

#### Drop

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Drop
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DROP PARTITION` on the same partition.

#### Attach

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Attach
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `ATTACH PARTITION` on the same partition.

#### Attach From

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.AttachFrom
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `ATTACH PARTITION FROM` on the same partition.

#### Replace

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Replace
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing another `REPLACE PARTITION` on the same partition.

For example,

> If we run `REPLACE PARTITION` to replace the data partition from the `table1` to `table2` and replaces existing partition in the `table2`, 
> but at the same time try to replace partition of another table from `table2`, the first process should finish and only after that the second `REPLACE PARTITION` SHALL be executed.

#### Move To Table

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.MoveToTable
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `MOVE PARTITION TO TABLE` on the same partition.

#### Clear Column In Partition

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearColumnInPartition
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `CLEAR COLUMN IN PARTITION` on the same partition.

#### Freeze

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Freeze
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `FREEZE PARTITION` on the same partition.

#### Unfreeze

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Unfreeze
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `UNFREEZE PARTITION` on the same partition.

#### Clear Index

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.ClearIndex
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `CLEAR INDEX IN PARTITION` on the same partition.

#### Fetch

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Fetch
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `FETCH PARTITION` on the same partition.

#### Move

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.Move
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `MOVE PARTITION` on the same partition.

#### Update In

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.UpdateInPartition
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `UPDATE IN PARTITION` on the same partition.

#### Delete In

##### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.Concurrent.Manipulating.Partitions.DeleteInPartition
version: 1.0

[ClickHouse] SHALL wait for `REPLACE PARTITION` to finish before executing `DELETE IN PARTITION` on the same partition.


## Role Based Access Control

### RQ.SRS-032.ClickHouse.Alter.Table.ReplacePartition.RBAC
version: 1.0

The `REPLACE PARTITION` command works with both source and destination tables. Each table can have its own privileges.

```sql
ALTER TABLE table2 REPLACE PARTITION 21 FROM table1
```

| Privileges              |
|-------------------------|
| No privileges           |
| SELECT                  |
| INSERT                  |
| ALTER                   |
| ALTER TABLE             |
| ALTER REPLACE PARTITION |

The `REPLACE PARTITION` SHALL only work when the user has the following privileges for the source and destination tables:

| Source | Destination |
|--------|-------------|
| ALTER  | SELECT      |

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/alter/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/alter/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)

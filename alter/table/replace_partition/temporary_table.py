from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from alter.table.replace_partition.common import insert_into_table_random_uint64
from helpers.common import getuid
from helpers.tables import create_table_partitioned_by_column


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromTemporaryTable("1.0"),
)
def from_temporary_to_regular(self):
    """Check that it is possible to replace partition from the temporary table into a regular MergeTree table."""
    node = self.context.node
    reference_table = "reference_" + getuid()
    destination_table = "destination_" + getuid()
    source_table = "temporary_source_" + getuid()

    with Given(
        "I have a destination table partitioned by a column and filled with random data"
    ):
        create_table_partitioned_by_column(table_name=destination_table)
        insert_into_table_random_uint64(table_name=destination_table)

    with When(
        "I create a temporary table with the same structure and populate it with data that creates multiple partitions",
        description=f"""temporary table gets deleted when the clickhouse session ends, to complete all test steps the 
        actions are preformed with the help of --multiquery."
                    
        Actions performed with the temporary table: 
            1. Create a temporary table with the same structure as the destination table.
            2. Populate the temporary table with the data to create multiple partitions.
            3. Replace the partition on the destination table from the temporary source table. 
            4. Create a reference table that copies the data from the temporary table, so that when the 
            temporary table is deleted we can assert that the values on the partition of the destination table 
            were changed.""",
    ):
        node.query(
            f"""
        CREATE TEMPORARY TABLE {source_table} (p UInt8,i UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();
        INSERT INTO {source_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3)); 
        ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table};
        CREATE TABLE {reference_table} ENGINE = MergeTree PARTITION BY p ORDER BY tuple() AS SELECT * FROM {source_table};
        """
        )

    with Then(
        "I check that the data on the destination table's partition was replaced with the data from the temporary table"
    ):
        with By(
            "selecting the data from the reference table which has the same data as the temporary table"
        ):
            data_from_temporary = node.query(
                f"SELECT * FROM {reference_table} WHERE p = 1 ORDER BY i"
            )

        with And(
            "comparing the data of the replaced partition on the destination table to the data on the reference table"
        ):
            data_from_destination = node.query(
                f"SELECT * FROM {destination_table} WHERE p = 1 ORDER BY i"
            )

            assert (
                data_from_destination.output.strip()
                == data_from_temporary.output.strip()
            ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ToTemporaryTable("1.0")
)
def from_temporary_to_temporary_table(self):
    """Check that it is not possible to replace partition from the temporary table into another temporary table."""
    node = self.context.node
    destination_table = "temporary_destination_" + getuid()
    source_table = "temporary_source_" + getuid()

    with Given(
        "I create two temporary tables with the same structure and populate them with data that creates multiple partitions",
        description=f"""temporary table gets deleted when the clickhouse session ends, to complete all test steps the 
        actions are preformed with the help of --multiquery."

        Actions performed with the temporary table: 
            1. Create two temporary tables with the same structure.
            2. Populate them with the data to create multiple partitions.
            3. Replace the partition on the temporary destination table from the temporary source table. """,
    ):
        node.query(
            f"""
        CREATE TEMPORARY TABLE {destination_table} (p UInt8,i UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();
        CREATE TEMPORARY TABLE {source_table} (p UInt8,i UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();
        INSERT INTO {source_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3)); 
        INSERT INTO {destination_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3)); 
        ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table};
        """,
            exitcode=60,
            message=f"DB::Exception: Could not find table: {destination_table}",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromRegularTable("1.0")
)
def from_regular_to_temporary(self):
    """Check that it is not possible to replace partition from the regular table into temporary table."""
    node = self.context.node
    destination_table = "temporary_destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I create two temporary tables with the same structure and populate them with data that creates multiple partitions",
        description=f"""temporary table gets deleted when the clickhouse session ends, to complete all test steps the 
        actions are preformed with the help of --multiquery."

        Actions performed with the temporary table: 
            1. Create one temporary table and one regular table with the same structure.
            2. Populate them with the data to create multiple partitions.
            3. Replace the partition on the temporary destination table from the regular source table. """,
    ):
        node.query(
            f"""
        CREATE TEMPORARY TABLE {destination_table} (p UInt8,i UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();
        CREATE TABLE {source_table} (p UInt8,i UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();
        INSERT INTO {source_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3)); 
        INSERT INTO {destination_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3)); 
        ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table};
        """,
            exitcode=60,
            message=f"DB::Exception: Could not find table: {destination_table}",
        )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTable("1.0"))
@Name("temporary table")
def feature(self, node="clickhouse1"):
    """Check that it is possible to use temporary tables to replace partitions on the destination table."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=from_temporary_to_regular)
    Scenario(run=from_temporary_to_temporary_table)
    Scenario(run=from_regular_to_temporary)

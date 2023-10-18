from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from helpers.tables import create_table, Column
from helpers.datatypes import *
from time import sleep


@TestStep
def create_partitioned_table(self, table_name):
    """Create a partitioned table that has specific settings in order to get both wide and compact parts."""
    create_table(
        name=table_name,
        engine="MergeTree",
        partition_by="p",
        order_by="tuple()",
        columns=[
            Column(name="p", datatype=UInt8()),
            Column(name="i", datatype=UInt64()),
        ],
        query_settings="min_rows_for_wide_part = 10, min_bytes_for_wide_part = 100",
    )


@TestStep(Given)
def partition_with_compact_parts(self, table_name):
    """Create a table that has partition with only compact parts."""
    node = self.context.node
    with Given("I create a table with partition consisting of compact parts"):
        create_partitioned_table(table_name=table_name)

        node.query(f"INSERT INTO {table_name} (p, i) SELECT 1, number FROM numbers(1)")


@TestStep(Given)
def partition_with_wide_parts(self, table_name):
    """Create a table that has partition with only wide parts."""
    node = self.context.node
    with Given("I create a MergeTree table partitioned by column p"):
        create_partitioned_table(table_name=table_name)

        node.query(
            f"INSERT INTO {table_name} (p, i) SELECT 1, number FROM numbers(100)"
        )


@TestStep(Given)
def partition_with_compact_and_wide_parts(self, table_name):
    """Create a table that has partition with both wide and compact parts."""
    node = self.context.node
    with Given("I create a MergeTree table partitioned by column p"):
        create_partitioned_table(table_name=table_name)

        node.query(
            f"INSERT INTO {table_name} (p, i) SELECT 1, number FROM numbers(100)"
        )
        node.query(f"INSERT INTO {table_name} (p, i) SELECT 1, number FROM numbers(1)")


@TestStep(Given)
def partition_with_empty_parts(self, table_name):
    """Create a table that has a partition with empty parts."""
    node = self.context.node
    with Given("I create a MergeTree table partitioned by column p"):
        create_partitioned_table(table_name=table_name)

        node.query(
            f"INSERT INTO {table_name} (p, i) SELECT 1, number FROM numbers(100)"
        )
        node.query(f"DELETE FROM {table_name} WHERE p == 1;")


@TestCheck
def check_partition_types(self, destination_table, source_table):
    """Check that it is possible to use the replace partition command between partitions with different types of parts."""
    node = self.context.node
    table1 = "table" + getuid()
    table2 = "table2_" + getuid()

    with Given("I create two tables that have partitions with specific part types"):
        destination_table(table_name=table1)

        source_table(table_name=table2)
    with Then(
        "I use the replace partition clause to replace the partition from table_2 into table_1 and wait for the process to finish"
    ):
        node.query(f"ALTER TABLE {table1} REPLACE PARTITION 1 FROM {table2}")
        sleep(10)
    with And("I select and save the partition values from the source table_2"):
        partition_values_2 = node.query(
            f"SELECT part_type FROM system.parts WHERE table = '{table2}' AND partition = '1' ORDER "
            "BY part_type"
        )

    with Check("I check that the partition was replaced on the destination table"):
        partition_values_1 = node.query(
            f"SELECT part_type FROM system.parts WHERE table = '{table1}' AND partition = '1' ORDER "
            "BY part_type"
        )

        assert (
            partition_values_1.output.strip() == partition_values_2.output.strip()
        ), error()


@TestSketch(Scenario)
@Flags(TE)
def replace_partition_with_different_partition_types(self):
    """Run test check with different partition types to see if replace partition is possible."""
    values = {
        partition_with_compact_parts,
        partition_with_wide_parts,
        partition_with_compact_and_wide_parts,
        partition_with_empty_parts,
    }

    check_partition_types(
        destination_table=either(*values, i="destination_table"),
        source_table=either(*values, i="source_table"),
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionTypes("1.0"))
@Name("partition types")
def feature(self, node="clickhouse1"):
    """Check that it is possible to use the replace partition between different part types."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=replace_partition_with_different_partition_types)

from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from helpers.tables import (
    create_partitioned_table_with_compact_and_wide_parts,
)


@TestStep(Given)
def insert_into_table_random_uint64(self, node, table_name, number_of_values):
    with By("Inserting random values into a column with uint64 datatype"):
        for i in range(10):
            node.query(
                f"INSERT INTO {table_name} (p, i) SELECT {i}, rand64() FROM numbers({number_of_values})"
            )


@TestStep(Given)
def table_with_compact_parts(self, table_name):
    """Create a table that has partition with only compact parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And("inserting data that will create multiple compact parts"):
        for _ in range(3):
            insert_into_table_random_uint64(
                node=node, table_name=table_name, number_of_values=1
            )


@TestStep(Given)
def table_with_wide_parts(self, table_name):
    """Create a table that has partition with only wide parts."""
    node = self.context.node
    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And("inserting data that will create multiple wide parts"):
        for _ in range(3):
            insert_into_table_random_uint64(
                node=node, table_name=table_name, number_of_values=100
            )


@TestStep(Given)
def table_with_compact_and_wide_parts(self, table_name):
    """Create a table that has partition with both wide and compact parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And("inserting data that will create multiple compact and wide parts"):
        for _ in range(3):
            insert_into_table_random_uint64(
                node=node, table_name=table_name, number_of_values=100
            )
            insert_into_table_random_uint64(
                node=node, table_name=table_name, number_of_values=1
            )


@TestStep(Given)
def partition_with_empty_parts(self, table_name):
    """Create a table that has a partition with empty parts."""
    node = self.context.node
    with Given("I create a MergeTree table partitioned by column p"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

        for _ in range(3):
            insert_into_table_random_uint64(
                node=node, table_name=table_name, number_of_values=100
            )
        node.query(f"DELETE FROM {table_name} WHERE p == 1;")


@TestStep(Given)
def partition_with_no_parts(self, table_name):
    """Deleting all parts of the partition by dropping the partition."""
    node = self.context.node
    with Given("I create a MergeTree table partitioned by column p"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And("inserting data that will create multiple compact and wide parts"):
        for _ in range(3):
            insert_into_table_random_uint64(
                node=node, table_name=table_name, number_of_values=100
            )
            insert_into_table_random_uint64(
                node=node, table_name=table_name, number_of_values=1
            )
    with Then("I delete all of parts inside the partition"):
        node.query(f"ALTER TABLE {table_name} DROP PARTITION 1")


@TestCheck
def check_replace_partition(self, destination_table, source_table):
    """Check that it is possible to use the replace partition command between tables that have
    partitions with different types of parts.
    """
    node = self.context.node
    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given("I create two tables that have partitions with specific part types"):
        destination_table(table_name=destination_table_name)
        source_table(table_name=source_table_name)

    with Then("I replace partition from the source table into the destination table"):
        replace_partition(
            destination_table=destination_table_name,
            source_table=source_table_name,
            partition=1,
        )

    with And("I select and save the partition values from the source table"):
        partition_values_source = node.query(
            f"SELECT i FROM {source_table_name} WHERE p = 1 ORDER BY i"
        )

    with Check("I check that the partition was replaced on the destination table"):
        partition_values_destination = node.query(
            f"SELECT i FROM {destination_table_name} WHERE p = 1 ORDER BY i"
        )
        with By(
            "Validating that the values of the replaced partition on the destination table are the same as on the source table"
        ):
            assert (
                partition_values_destination.output.strip()
                == partition_values_source.output.strip()
            ), error()


@TestSketch(Scenario)
@Flags(TE)
def replace_partition_with_different_partition_types(self):
    """Run test check with different partition types to see if replace partition is possible."""
    values = {
        table_with_compact_parts,
        table_with_wide_parts,
        table_with_compact_and_wide_parts,
        partition_with_empty_parts,
        partition_with_no_parts,
    }

    check_replace_partition(
        destination_table=either(*values, i="destination_table"),
        source_table=either(*values, i="source_table"),
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionTypes("1.0"))
@Name("partition types")
def feature(self, node="clickhouse1"):
    """Check replace partition with different partition types.

    Partition types:
    * partition containing only compact parts
    * partition containing only wide parts
    * partition containing mix of compact and wide parts
    * partition containing empty parts
    * partition containing no parts (empty)
    """
    self.context.node = self.context.cluster.node(node)

    Scenario(run=replace_partition_with_different_partition_types)

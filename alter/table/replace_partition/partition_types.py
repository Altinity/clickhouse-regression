from testflows.core import *

from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    create_partitions_with_random_uint64,
)
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from helpers.tables import (
    create_partitioned_table_with_compact_and_wide_parts,
)


@TestStep(Given)
def table_with_compact_parts(self, table_name):
    """Create a table that has partition with only compact parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(
        f"inserting data into {table_name} that will create multiple compact parts"
    ):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=1
        )


@TestStep(Given)
def table_with_wide_parts(self, table_name):
    """Create a table that has partition with only wide parts."""
    node = self.context.node
    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(f"inserting data into {table_name} that will create multiple wide parts"):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100
        )


@TestStep(Given)
def table_with_compact_and_wide_parts(self, table_name):
    """Create a table that has partition with both wide and compact parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(
        f"inserting data into {table_name} that will create multiple compact and wide parts"
    ):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100
        )
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=1
        )


@TestStep(Given)
def partition_with_empty_parts(self, table_name):
    """Create a table that has a partition with empty parts."""
    node = self.context.node
    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(
        f"inserting data into {table_name} that will create multiple compact and wide parts"
    ):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100
        )

    with And("deleting all data from evey part in the partition"):
        node.query(f"DELETE FROM {table_name} WHERE p == 1;")


@TestStep(Given)
def partition_with_no_parts(self, table_name):
    """Deleting all parts of the partition by dropping the partition."""
    node = self.context.node
    with By("creating a MergeTree table partitioned by column p"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And("inserting data that will create multiple compact and wide parts"):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100
        )
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=1
        )

    with And("deleting all parts inside the partition"):
        node.query(f"ALTER TABLE {table_name} DROP PARTITION 1")


@TestCheck
def check_replace_partition(self, destination_table, source_table):
    """Check that it is possible to use the replace partition command between tables that have
    partitions with different types of parts.
    """
    node = self.context.node
    destination_table_name = "destination_" + getuid()
    source_table_name = "source_" + getuid()

    with Given(
        "I create two tables that have partitions with specific part types",
        description=f"""
               partition types:
               destination table: {destination_table.__name__}
               source table: {source_table.__name__}
               """,
    ):
        destination_table(table_name=destination_table_name)
        source_table(table_name=source_table_name)

    with When("I replace partition from the source table into the destination table"):
        replace_partition(
            destination_table=destination_table_name,
            source_table=source_table_name,
            partition=1,
        )

    with Then("I check that the partition on the destination table was replaced"):
        check_partition_was_replaced(
            destination_table=destination_table_name, source_table=source_table_name
        )


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

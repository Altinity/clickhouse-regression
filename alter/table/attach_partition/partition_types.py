from testflows.core import *

from alter.table.replace_partition.common import (
    create_partitions_with_random_uint64,
)
from alter.table.attach_partition.common import (
    check_partition_was_attached,
    check_partition_was_detached,
)
from alter.table.attach_partition.requirements.requirements import *
from helpers.common import (
    getuid,
    attach_partition,
    detach_partition,
    attach_partition_from,
)
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

    with And(f"inserting data into {table_name} that will create multiple wide parts"):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100
        )

    with And("deleting all data from every part in the partition"):
        node.query(f"DELETE FROM {table_name} WHERE p == 1")


@TestCheck
def check_attach_partition(self, table):
    """Check that it is possible to use the attach partition command with tables that have
    partitions with different types of parts.
    """
    node = self.context.node
    table_name = getuid()

    with Given(
        "I create table that has partitions with specific part types",
        description=f"""
               partition types:
               destination table: {table.__name__}
               """,
    ):
        table(table_name=table_name)

    with When("I detach partition from the table"):
        detach_partition(
            table=table_name,
            partition=1,
        )

    with When("I check that the partition was detached from the table"):
        check_partition_was_detached(
            table=table_name,
            partition=1,
        )

    with When("I attach partition from the table"):
        attach_partition(
            table=table_name,
            partition=1,
        )

    with Then("I check that the partition was attached to the table"):
        check_partition_was_attached(table=table_name, partition=1)


@TestCheck
def check_attach_partition_from(self, destination_table, source_table):
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
        attach_partition_from(
            destination_table=destination_table_name,
            source_table=source_table_name,
            partition=1,
        )

    with Then("I check that the partition on the destination table was replaced"):
        check_partition_was_attached(
            destination_table=destination_table_name, source_table=source_table_name
        )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_with_different_partition_types_detached(self):
    """Run test check with different partition types to see if attach partition is possible."""
    values = {
        table_with_compact_parts,
        table_with_wide_parts,
        table_with_compact_and_wide_parts,
        partition_with_empty_parts,
    }

    check_attach_partition(
        table=either(*values, i="table"),
    )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_with_different_partition_types_from_table(self):
    """Run test check with different partition types to see if attach partition is possible."""
    values = {
        table_with_compact_parts,
        table_with_wide_parts,
        table_with_compact_and_wide_parts,
        partition_with_empty_parts,
    }

    check_attach_partition_from(
        source_table=either(*values, i="source_table"),
        destination_table=either(*values, i="desctibation_table"),
    )


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartitionTypes("1.0"))
@Name("partition types")
def feature(self, node="clickhouse1"):
    """Check attach partition with different partition types.

    Partition types:
    * partition with only compact parts
    * partition with only wide parts
    * partition with compact and wide parts (mixed)
    * partition with empty parts
    * partition with no parts
    """
    self.context.node = self.context.cluster.node(node)

    # Scenario(run=attach_partition_with_different_partition_types_detached)
    # Scenario(run=attach_partition_with_different_partition_types_from_table)

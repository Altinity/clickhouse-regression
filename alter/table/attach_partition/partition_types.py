from testflows.core import *

from alter.table.attach_partition.requirements.requirements import *

from alter.table.attach_partition.common import (
    check_partition_was_attached,
    check_part_was_attached,
    check_partition_was_attached_from,
    check_partition_was_detached,
    check_part_was_detached,
    create_partitions_with_random_uint64,
)
from helpers.common import (
    getuid,
    attach_partition,
    detach_partition,
    attach_partition_from,
    attach_part,
    detach_part,
    check_clickhouse_version,
)
from helpers.tables import (
    create_partitioned_table_with_compact_and_wide_parts,
)


@TestStep(Given)
def table_with_compact_parts(self, table_name, bias=0):
    """Create a table that has partition with only compact parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(
        f"inserting data into {table_name} that will create multiple compact parts"
    ):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=1, bias=bias
        )


@TestStep(Given)
def table_with_wide_parts(self, table_name, bias=0):
    """Create a table that has partition with only wide parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(f"inserting data into {table_name} that will create multiple wide parts"):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100, bias=bias
        )


@TestStep(Given)
def table_with_compact_and_wide_parts(self, table_name, bias=0):
    """Create a table that has partition with both wide and compact parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(
        f"inserting data into {table_name} that will create multiple compact and wide parts"
    ):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100, bias=bias
        )
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=1, bias=bias
        )


@TestStep(Given)
def partition_with_empty_parts(self, table_name, bias=0):
    """Create a table that has a partition with empty parts."""
    node = self.context.node

    with By("creating a partitioned table"):
        create_partitioned_table_with_compact_and_wide_parts(table_name=table_name)

    with And(f"inserting data into {table_name} that will create multiple wide parts"):
        create_partitions_with_random_uint64(
            node=node, table_name=table_name, number_of_values=100, bias=bias
        )

    with And("deleting all data from part in the partition"):
        if check_clickhouse_version("<23.3")(self):
            node.query(
                f"DELETE FROM {table_name} WHERE p == 1",
                settings=[("allow_experimental_lightweight_delete", 1)],
            )
        else:
            node.query(f"DELETE FROM {table_name} WHERE p == 1")


@TestCheck
def check_attach_partition(self, table):
    """Check that it is possible to use the attach partition command with tables that have
    partitions with different types of parts.
    """
    table_name = getuid()

    with Given(
        "I create table that has partitions with specific part type",
        description=f"""
               partition type: {table.__name__}
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
    """Check that it is possible to use the attach partition command between tables that have
    partitions with different types of parts.
    """
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
        source_table(table_name=source_table_name)
        destination_table(table_name=destination_table_name, bias=6)

    with When("I attach partition from the source table to the destination table"):
        attach_partition_from(
            source_table=source_table_name,
            destination_table=destination_table_name,
            partition=1,
        )

    with Then(
        "I check that the partition from the source table has been attached to the destination table"
    ):
        check_partition_was_attached_from(
            destination_table=destination_table_name,
            source_table=source_table_name,
            partition=1,
        )


@TestCheck
def check_attach_part(self, table):
    """Check that it is possible to use the attach part command with different types of parts."""
    table_name = getuid()

    with Given(
        "I create two tables that have partitions with specific part types",
        description=f"""
               partition type: {table.__name__}
               """,
    ):
        table(table_name=table_name)

    if "empty" in table.__name__:
        skip("No parts in table")

    parts = self.context.node.query(
        f"SELECT name from system.parts where table='{table_name}' FORMAT TabSeparated"
    ).output.split("\n")
    number_of_active_parts = int(
        self.context.node.query(
            f"SELECT count(active) from system.parts where table='{table_name}' and active = 1 FORMAT TabSeparated"
        ).output
    )

    if number_of_active_parts == 0:
        skip("No parts")

    part = parts[0]

    with When("I detach part from the table"):
        detach_part(
            table=table_name,
            part=part,
        )

    with When("I check that the partition was detached from the table"):
        check_part_was_detached(
            table=table_name, part=part, number_of_active_parts=number_of_active_parts
        )

    with When("I attach partition from the table"):
        attach_part(
            table=table_name,
            part=part,
        )

    with Then("I check that the partition was attached to the table"):
        check_part_was_attached(
            table=table_name,
            part=part,
        )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_detached_with_different_partition_types(self):
    """Run test check with different partition types to see if attach partition is possible."""
    values = {
        table_with_compact_parts,
        table_with_wide_parts,
        table_with_compact_and_wide_parts,
        partition_with_empty_parts,
    }
    if check_clickhouse_version("<22.8")(
        self
    ):  # lightweight delete was introduced in 22.8
        values = {
            table_with_compact_parts,
            table_with_wide_parts,
            table_with_compact_and_wide_parts,
        }

    check_attach_partition(
        table=either(*values, i="table"),
    )


@TestSketch(Scenario)
@Flags(TE)
def attach_part_detached_with_different_partition_types(self):
    """Run test check with different partition types to see if attach partition is possible."""
    values = {
        table_with_compact_parts,
        table_with_wide_parts,
        table_with_compact_and_wide_parts,
        partition_with_empty_parts,
    }
    if check_clickhouse_version("<22.8")(
        self
    ):  # lightweight delete was introduced in 22.8
        values = {
            table_with_compact_parts,
            table_with_wide_parts,
            table_with_compact_and_wide_parts,
        }

    check_attach_part(
        table=either(*values, i="table"),
    )


@TestSketch(Scenario)
@Flags(TE)
def attach_partition_from_with_different_partition_types(self):
    """Run test check with different partition types to see if attach partition is possible."""
    values = {
        table_with_compact_parts,
        table_with_wide_parts,
        table_with_compact_and_wide_parts,
        partition_with_empty_parts,
    }

    check_attach_partition_from(
        source_table=either(*values),
        destination_table=either(*values),
    )


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartition_PartitionTypes("1.0"))
@Name("partition types")
def feature(self, node="clickhouse1"):
    """Check attach partition from and attach partition(detached folder) with different partition types.

    Partition types:
    * partition with only compact parts
    * partition with only wide parts
    * partition with compact and wide parts (mixed)
    * partition with empty parts
    """
    self.context.node = self.context.cluster.node(node)

    # Scenario(run=attach_partition_detached_with_different_partition_types)
    # Scenario(run=attach_partition_from_with_different_partition_types)
    Scenario(run=attach_part_detached_with_different_partition_types)

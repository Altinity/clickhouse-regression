from testflows.asserts import *
from testflows.core import *

from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from helpers.tables import create_table_partitioned_by_column

one_part = ["1_1_1_0"]
multiple_parts = ["1_1_1_0", "1_2_2_0"]
all_parts = ["1_1_1_0", "1_2_2_0", "1_3_3_0"]


@TestStep(When)
def corrupt_parts_on_table_partition(self, table_name, parts, bits_to_corrupt=1500000):
    """Corrupt the selected part file."""
    node = self.context.node

    with By(
        f"executing a corrupt_file script that will flip {bits_to_corrupt} bits on the {parts} part of the {table_name} table"
    ):
        for part in parts:
            node.command(
                f"corrupt_file /var/lib/clickhouse/data/default/{table_name}/{part}/data.bin {bits_to_corrupt}"
            )


@TestCheck
def replace_with_corrupted_parts(self, corrupt_destination, corrupt_source):
    """Replace partition when parts on one or both of the tables are corrupted."""
    node = self.context.node
    source_table = "source" + getuid()
    destination_table = "destination" + getuid()
    partition = 1

    with Given("I have two tables with the same structure"):
        create_table_partitioned_by_column(
            table_name=destination_table,
        )
        create_table_partitioned_by_column(
            table_name=source_table,
        )

    with And(
        "I populate these tables with data to create a partition with a set number of parts",
        description="""this will create a partition with three parts [
            "1_1_1_0",
            "1_2_2_0",
            "1_3_3_0",
        ]""",
    ):
        for i in range(3):
            node.query(
                f"INSERT INTO {destination_table} (p, i) SELECT {partition}, {i} FROM numbers(1);"
            )
            node.query(
                f"INSERT INTO {source_table} (p, i) SELECT {partition}, {i} FROM numbers(1);"
            )

    with When("I change some bit values of the part on one of or both tables"):
        corrupt_destination(table_name=destination_table)
        corrupt_source(table_name=source_table)

    with Then(
        "I replace partition on destination table from the source table and validate the data"
    ):
        parts_before_replace = node.query(
            f"SELECT partition, part_type, name FROM system.parts WHERE table = '{destination_table}' ORDER BY tuple(*)"
        )

        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            partition=partition,
        )

        parts_after_replace = node.query(
            f"SELECT partition, part_type, name FROM system.parts WHERE table = '{destination_table}' ORDER BY tuple(*)"
        )

    with And(
        "I check that data was replaced on the destination table",
        description="this allows us to validate that the partitions were replaced by validating that the inside the "
        "system.parts table the data for destination table was updated.",
    ):
        for retry in retries(timeout=10):
            with retry:
                assert (
                    parts_before_replace.output.strip()
                    != parts_after_replace.output.strip()
                ), error()


@TestStep(When)
def corrupt_one_part(self, table_name):
    """Corrupt a single part of the partition."""
    corrupt_parts_on_table_partition(table_name=table_name, parts=one_part)


@TestStep(When)
def corrupt_multiple_parts(self, table_name):
    """Corrupt multiple parts of the partition."""
    corrupt_parts_on_table_partition(table_name=table_name, parts=multiple_parts)


@TestStep(When)
def corrupt_all_parts(self, table_name):
    """Corrupt all parts of the partition."""
    corrupt_parts_on_table_partition(table_name=table_name, parts=all_parts)


@TestStep(When)
def corrupt_no_parts(self, table_name):
    """Corrupt no parts of the partition."""
    with By(f"not corrupting a {table_name} table"):
        note(f"{table_name} is not corrupted")


@TestSketch(Scenario)
@Flags(TE)
def replace_partition_with_corrupted_parts(self):
    """Run test check to replace partition with different amounts of parts being corrupted on one or both tables."""
    values = {
        corrupt_no_parts,
        corrupt_all_parts,
        corrupt_multiple_parts,
        corrupt_one_part,
    }

    replace_with_corrupted_parts(
        corrupt_destination=either(*values),
        corrupt_source=either(*values),
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Corrupted("1.0"))
@Name("corrupted partitions")
def feature(self, node="clickhouse1"):
    """
    Check how clickhouse behaves when replacing partition on tables with corrupted partitions.

    Combinations:
    * None of the parts are corrupted
    * One part is corrupted
    * Multiple parts are corrupted
    * All parts are corrupted
    """
    self.context.node = self.context.cluster.node(node)

    Scenario(run=replace_partition_with_corrupted_parts)

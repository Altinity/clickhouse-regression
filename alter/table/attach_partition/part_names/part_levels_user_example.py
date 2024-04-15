import random

from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *

from helpers.common import getuid


@TestScenario
def part_levels_user_example(self):
    """Check reset part level upon attach from disk on MergeTree."""
    node = self.context.node

    source_table = "source_" + getuid()
    destination_table = "destination_" + getuid()

    with Given("I create a source table on cluster with data"):
        create_table_on_cluster_with_data(
            table_name=source_table,
            cluster="replicated_cluster_secure",
            order_by="id",
            number_of_rows=100000000,
        )
        optimize_table(table_name=source_table)

    with And("I create a destination table"):
        create_MergeTree_table_with_data(
            table_name=destination_table,
            order_by="id",
            number_of_rows=0,
        )

    with And("I attach a partition from the source table to the destination table"):
        attach_partition_from(
            source_table=source_table,
            destination_table=destination_table,
            partition="tuple()",
        )
        optimize_table(table_name=destination_table)

    with And("I get part name and construct new part name with too high level"):
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table}' and active FORMAT TabSeparated"
        ).output.split("\n")
        part_name = random.choice(part_names)
        new_part_name = "_".join(part_name.split("_")[:-1]) + "_4294967295"

    with And("I detach the partition"):
        detach_partition(
            table_name=destination_table,
            partition="tuple()",
        )

    with And("Rename detached part of destination table"):
        rename_detached_part(
            table_name=destination_table,
            part_name=part_name,
            new_part_name=new_part_name,
        )

    with And("I attach detached partition"):
        attach_partition(
            table_name=destination_table,
            partition="tuple()",
        )
        node.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table}' and active FORMAT TabSeparated"
        ).output

    with And("I attach partition from destination table to source table"):
        attach_partition_from(
            source_table=destination_table,
            destination_table=source_table,
            partition="tuple()",
        )
        node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active FORMAT TabSeparated"
        ).output
        optimize_table(table_name=source_table)

    with And("I check current part names in source table"):
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active FORMAT TabSeparated"
        ).output.split("\n")

    with And("I create second destination table"):
        destination_table_2 = "destination_2_" + getuid()
        create_MergeTree_table_with_data(
            table_name=destination_table_2,
            order_by="id",
            number_of_rows=0,
        )

    with And(
        "I attach a partition from the source table to the second destination table"
    ):
        attach_partition_from(
            source_table=source_table,
            destination_table=destination_table_2,
            partition="tuple()",
        )
        optimize_table(table_name=destination_table_2)

    with And("I get part name and construct new part name"):
        part_names = node.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table_2}' AND active FORMAT TabSeparated"
        ).output.split("\n")
        part_name = random.choice(part_names)
        new_part_name = "_".join(part_name.split("_")[:-1]) + "_4294967294"

    with And("I detach the partition"):
        detach_partition(
            table_name=destination_table_2,
            partition="tuple()",
        )

    with And("Rename detached part of second destination table"):
        rename_detached_part(
            table_name=destination_table_2,
            part_name=part_name,
            new_part_name=new_part_name,
        )

    with And("I attach detached partition"):
        attach_partition(
            table_name=destination_table_2,
            partition="tuple()",
        )
        node.query(
            f"SELECT name FROM system.parts WHERE table = '{destination_table_2}' and active FORMAT TabSeparated"
        ).output

    with And("I attach partition from second destination table to source table"):
        attach_partition_from(
            source_table=destination_table_2,
            destination_table=source_table,
            partition="tuple()",
        )
        node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' and active FORMAT TabSeparated"
        ).output
        optimize_table(table_name=source_table)

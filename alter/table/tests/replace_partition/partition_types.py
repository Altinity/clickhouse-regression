from testflows.core import *
from testflows.asserts import *
from alter.table.requirements.replace_partition import *
from helpers.common import getuid
from helpers.tables import create_table, Column
from helpers.datatypes import *
from time import sleep


@TestCheck
def check_partition_replace_capability(self, destination_table, source_table):
    """Check that it is possible to use the replace partition command between partitions with all types of parts."""
    node = self.context.node
    table1 = "table1_" + getuid()
    table2 = "table2_" + getuid()

    part_types = {
        "compact": {
            "settings": "min_rows_for_wide_part = 10, min_bytes_for_wide_part = 100",
            "values": "(p, i) SELECT 1, number FROM numbers(1)",
        },
        "wide": {
            "settings": "min_rows_for_wide_part = 10, min_bytes_for_wide_part = 100",
            "values": "(p, i) SELECT 1, number FROM numbers(100)",
        },
        "compact and wide": {
            "settings": "min_rows_for_wide_part = 10, min_bytes_for_wide_part = 100",
        },
    }

    with Given("I create a MergeTree table partitioned by column p"):
        create_table(
            name=table1,
            engine="MergeTree",
            partition_by="p",
            order_by="tuple()",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
            query_settings=part_types[destination_table]["settings"],
        )

    with And("Create a new table with the same structure as the table_1"):
        create_table(
            name=table2,
            engine="MergeTree",
            partition_by="p",
            order_by="tuple()",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
            query_settings=part_types[source_table]["settings"],
        )

    with When(
        "I insert the data into table_1 based on the type of part we need to get"
    ):
        if destination_table == "compact and wide":
            node.query(f"INSERT INTO {table1} {part_types['compact']['values']}")
            node.query(f"INSERT INTO {table1} {part_types['wide']['values']}")

        else:
            node.query(
                f"INSERT INTO {table1} {part_types[destination_table]['values']}"
            )

    with And("I insert the data into table_2 based on the type of part we need to get"):
        if source_table == "compact and wide":
            node.query(f"INSERT INTO {table2} {part_types['compact']['values']}")
            node.query(f"INSERT INTO {table2} {part_types['wide']['values']}")
        else:
            node.query(f"INSERT INTO {table2} {part_types[source_table]['values']}")

    with Then(
        "I use the replace partition clause to replace the partition from table_2 into table_1 and wait for the process to finish"
    ):
        node.query(f"ALTER TABLE {table1} REPLACE PARTITION 1 FROM {table2}")

    with And("I select and save the part type values from the source table_2"):
        partition_values_2 = node.query(
            f"SELECT part_type FROM system.parts WHERE table = '{table2}' AND partition = '1' ORDER "
            "BY part_type"
        )

    with Check("I check that the part type for table_1 was replaced from the table_2"):
        partition_values_1 = node.query(
            f"SELECT part_type FROM system.parts WHERE table = '{table1}' AND partition = '1' ORDER "
            "BY part_type"
        )

        assert (
            partition_values_1.output.strip() == partition_values_2.output.strip()
        ), error()


@TestSketch(Scenario)
def test_parts(self):
    values = {"wide", "compact", "compact and wide"}

    check_partition_replace_capability(
        destination_table=either(*values, i="destination_table"),
        source_table=either(*values, i="source_table"),
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_PartitionTypes("1.0"))
@Name("replace partition types")
def feature(self, node="clickhouse1"):
    """Check that it is possible to use the replace partition between different part types."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=test_parts)

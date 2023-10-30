from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from helpers.datatypes import UInt8, UInt64
from helpers.tables import create_table_partitioned_by_column, create_table, Column


@TestStep(Given)
def insert_into_table_random_uint64(
    self, table_name, number_of_values=3, number_of_partitions=5, node=None
):
    """Insert random UInt64 values into a column and create multiple partitions based on the value of number_of_partitions."""
    if node is None:
        node = self.context.node

    with By("Inserting random values into a column with uint64 datatype"):
        for i in range(number_of_partitions):
            node.query(
                f"INSERT INTO {table_name} (p, i) SELECT {i}, rand64() FROM numbers({number_of_values})"
            )


@TestStep(Given)
def create_two_tables_partitioned_by_column_with_data(
    self, destination_table, source_table
):
    """Creating two tables that are partitioned by the same column and arr filled with random data."""

    with By("I create two tables with the same structure"):
        create_table_partitioned_by_column(table_name=source_table)
        create_table_partitioned_by_column(table_name=destination_table)

    with And("I insert data into both tables"):
        insert_into_table_random_uint64(
            table_name=destination_table, number_of_values=10
        )
        insert_into_table_random_uint64(table_name=source_table, number_of_values=10)


@TestStep(Given)
def create_merge_tree_and_memory_tables(self, merge_tree_table, memory_table):
    """Creating two tables, one is a MergeTree table partitioned by a column and the other is a Memory table."""

    with By(
        "I create a destination table with a MergeTree engine partitioned by a column"
    ):
        create_table_partitioned_by_column(table_name=merge_tree_table)

    with And("I create a table with a Memory engine that has no partitions"):
        create_table(
            engine="Memory",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
            name=memory_table,
        )

        with And("I insert data into both tables"):
            insert_into_table_random_uint64(
                table_name=merge_tree_table, number_of_values=10
            )
            insert_into_table_random_uint64(
                table_name=memory_table, number_of_values=10
            )

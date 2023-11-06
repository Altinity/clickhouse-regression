from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from helpers.datatypes import UInt8, UInt64
from helpers.tables import create_table_partitioned_by_column, create_table, Column


@TestStep(Given)
def create_partitions_with_random_uint64(
    self, table_name, number_of_values=3, number_of_partitions=5, node=None
):
    """Insert random UInt64 values into a column and create multiple partitions based on the value of number_of_partitions."""
    if node is None:
        node = self.context.node

    with By("Inserting random values into a column with uint64 datatype"):
        for i in range(1, number_of_partitions):
            node.query(
                f"INSERT INTO {table_name} (p, i) SELECT {i}, rand64() FROM numbers({number_of_values})"
            )


@TestStep(Given)
def create_two_tables_partitioned_by_column_with_data(
    self,
    destination_table,
    source_table,
    number_of_partitions=5,
    number_of_values=10,
    columns=None,
    query_settings=None,
):
    """Creating two tables that are partitioned by the same column and are filled with random data."""

    with By("creating two tables with the same structure"):
        create_table_partitioned_by_column(
            table_name=source_table, columns=columns, query_settings=query_settings
        )
        create_table_partitioned_by_column(
            table_name=destination_table, columns=columns, query_settings=query_settings
        )

    with And("inserting data into both tables"):
        create_partitions_with_random_uint64(
            table_name=destination_table,
            number_of_values=number_of_values,
            number_of_partitions=number_of_partitions,
        )
        create_partitions_with_random_uint64(
            table_name=source_table,
            number_of_values=number_of_values,
            number_of_partitions=number_of_partitions,
        )


@TestStep(Given)
def create_table_partitioned_by_column_with_data(
    self,
    table_name,
    number_of_partitions=5,
    number_of_values=10,
    query_settings=None,
    columns=None,
    partition_by="p",
    order_by="tuple()",
):
    with By("creating two tables with the same structure"):
        create_table_partitioned_by_column(
            table_name=table_name,
            query_settings=query_settings,
            partition_by=partition_by,
            columns=columns,
            order_by=order_by,
        )

    with And("inserting data into both tables"):
        create_partitions_with_random_uint64(
            table_name=table_name,
            number_of_values=number_of_values,
            number_of_partitions=number_of_partitions,
        )


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
        create_partitions_with_random_uint64(
            table_name=merge_tree_table, number_of_values=10
        )
        create_partitions_with_random_uint64(
            table_name=memory_table, number_of_values=10
        )


@TestStep(Then)
def check_partition_was_replaced(
    self,
    destination_table,
    source_table,
    source_table_before_replace,
    node=None,
    sort_column="p",
    partition=1,
    column="i",
):
    """Check that the partition on the destination table was replaced from the source table."""
    if node is None:
        node = self.context.node

    with By(
        "selecting and saving the partition data from the source table and destination table"
    ):
        partition_values_source = node.query(
            f"SELECT {column} FROM {source_table} WHERE {sort_column} = {partition} ORDER BY tuple(*)"
        )
        partition_values_destination = node.query(
            f"SELECT {column} FROM {destination_table} WHERE {sort_column} = {partition} ORDER BY tuple(*)"
        )

    with Then(
        "I check that the data on the partition of the destination table is the same as the data on the source table partition"
    ):
        assert (
            partition_values_destination.output.strip()
            == partition_values_source.output.strip()
        ), error()

    with And("I check that the data on the source table was preserved"):
        assert (
            source_table_before_replace.output.strip()
            == partition_values_source.output.strip()
        ), error()

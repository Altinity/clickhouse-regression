import random
from time import sleep

from testflows.asserts import *
from testflows.core import *

from helpers.common import replace_partition
from helpers.datatypes import UInt8, UInt64
from helpers.tables import create_table_partitioned_by_column, create_table, Column


@TestStep(Given)
def create_partitions_with_random_uint64(
    self,
    table_name,
    number_of_values=3,
    number_of_partitions=5,
    number_of_parts=1,
    node=None,
):
    """Insert random UInt64 values into a column and create multiple partitions based on the value of number_of_partitions."""
    if node is None:
        node = self.context.node

    with By("Inserting random values into a column with uint64 datatype"):
        for i in range(number_of_partitions):
            for parts in range(number_of_parts):
                node.query(
                    f"INSERT INTO {table_name} (p, i) SELECT {i}, rand64() FROM numbers({number_of_values})"
                )


@TestStep(Given)
def create_table_partitioned_by_column_with_data(
    self,
    table_name,
    number_of_partitions=5,
    number_of_values=10,
    number_of_parts=1,
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
            number_of_parts=number_of_parts,
        )


@TestStep(Given)
def create_two_tables_partitioned_by_column_with_data(
    self,
    destination_table,
    source_table,
    number_of_partitions=5,
    number_of_values=10,
    number_of_parts=1,
    columns=None,
    query_settings=None,
):
    """Creating two tables that are partitioned by the same column and are filled with random data."""

    with By("creating two tables with the same structure"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table,
            columns=columns,
            query_settings=query_settings,
            number_of_partitions=number_of_partitions,
            number_of_values=number_of_values,
            number_of_parts=number_of_parts,
        )
        create_table_partitioned_by_column_with_data(
            table_name=destination_table,
            columns=columns,
            query_settings=query_settings,
            number_of_partitions=number_of_partitions,
            number_of_parts=number_of_parts,
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
    source_table_before_replace=None,
    node=None,
    sort_column="p",
    partition=1,
    column="i",
    list=False,
):
    """Check that the partition on the destination table was replaced from the source table."""
    if node is None:
        node = self.context.node

    if not list:
        condition = "="
    else:
        condition = "IN"

    with By(
        "selecting and saving the partition data from the source table and destination table"
    ):
        partition_values_source = node.query(
            f"SELECT {column} FROM {source_table} WHERE {sort_column} {condition} {partition} ORDER BY tuple(*)"
        )
        partition_values_destination = node.query(
            f"SELECT {column} FROM {destination_table} WHERE {sort_column} {condition} {partition} ORDER BY tuple(*)"
        )

    with Then(
        "I check that the data on the partition of the destination table is the same as the data on the source table partition"
    ):
        assert (
            partition_values_destination.output.strip()
            == partition_values_source.output.strip()
        ), error()

    if source_table_before_replace is not None:
        with And("I check that the data on the source table was preserved"):
            assert (
                source_table_before_replace.output.strip()
                == partition_values_source.output.strip()
            ), error()


@TestStep(Then)
def replace_partition_and_validate_data(
    self,
    partition_to_replace,
    destination_table=None,
    source_table=None,
    delay_before=None,
    delay_after=None,
    validate=None,
    exitcode=None,
    message=None,
):
    """
    Replace partition and validate that the data on the destination table is the same data as on the source table.
    Also check that the data on the source table was not lost during replace partition.

     Args:
        partition_to_replace (str): The partition identifier that needs to be replaced in the destination table.
        destination_table (str, optional): The name of the destination table where the partition is to be replaced.
        Defaults to None, in which case the table name is taken from the test context.
        source_table (str, optional): The name of the source table from which to take the replacement partition.
        Defaults to None, in which case the table name is taken from the test context.
        delay_before (float, optional): The delay in seconds to wait before performing the partition replacement.
        Defaults to None, which causes a random delay.
        delay_after (float, optional): The delay in seconds to wait after performing the partition replacement.
        Defaults to None, which causes a random delay.
        validate (bool, optional): A flag determining whether to perform validation checks after the partition replacement.
        Defaults to True.
    """
    node = self.context.node

    if validate is None:
        validate = True
    else:
        validate = self.context.validate

    if destination_table is None:
        destination_table = self.context.destination_table

    if source_table is None:
        source_table = self.context.source_table

    if delay_before is None:
        delay_before = random.random()

    if delay_after is None:
        delay_after = random.random()

    with By(
        "saving the data from the source table before replacing partitions on the destination table"
    ):
        source_data_before = node.query(
            f"SELECT i FROM {source_table} WHERE p = {partition_to_replace} ORDER BY tuple(*)"
        )

    with And("replacing partition on the destination table"):
        sleep(delay_before)

        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            partition=partition_to_replace,
            exitcode=exitcode,
            message=message,
        )

        sleep(delay_after)

    if validate:
        with Then("checking that the partition was replaced on the destination table"):
            check_partition_was_replaced(
                destination_table=destination_table,
                source_table=source_table,
                source_table_before_replace=source_data_before,
                partition=partition_to_replace,
            )

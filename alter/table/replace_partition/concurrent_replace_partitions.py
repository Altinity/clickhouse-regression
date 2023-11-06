from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    check_partition_was_replaced,
)
from helpers.alter import *
from helpers.tables import create_table_partitioned_by_column
import random


@TestStep(Given)
def create_partitions_with_random_parts(self, table_name, number_of_partitions):
    """Create a number of partitions inside the table with random number of parts."""
    node = self.context.node

    with By(
        f"Inserting data into a {table_name} table",
        description="each insert creates a new part inside a partiion resulting in a partition with a set numebr of parts",
    ):
        for partition in range(1, number_of_partitions):
            number_of_parts = random.randrange(1, 50)
            with By(
                f"creating {number_of_parts} parts inside the {partition} partition"
            ):
                for parts in range(1, number_of_parts):
                    node.query(
                        f"INSERT INTO {table_name} (p, i) SELECT {partition}, rand64() FROM numbers(10)"
                    )


@TestStep(Given)
def destination_table_with_partitions(self, table_name, number_of_partitions):
    """Create a destination table with set number of partitions and parts."""

    with By(f"creating a {table_name} table with {number_of_partitions} partitions"):
        create_table_partitioned_by_column(table_name=table_name)
        create_partitions_with_random_parts(
            table_name=table_name, number_of_partitions=number_of_partitions
        )


@TestStep(Given)
def source_table_with_partitions(self, table_name, number_of_partitions):
    """Create a source table with set number of partitions and parts."""

    with By(f"creating a {table_name} table with {number_of_partitions} partitions"):
        create_table_partitioned_by_column(table_name=table_name)
        create_partitions_with_random_parts(
            table_name=table_name, number_of_partitions=number_of_partitions
        )


@TestStep(Given)
def create_two_tables_with_100_partitions(self, destination_table, source_table):
    """Create two tables, each has 100 partitions with random number of parts."""
    with Given("I have two partitioned tables with the same structure"):
        destination_table_with_partitions(
            table_name=destination_table, number_of_partitions=100
        )
        source_table_with_partitions(table_name=source_table, number_of_partitions=100)


@TestStep(When)
def replace_partition_and_validate_data(
    self, destination_table, source_table, partition_to_replace
):
    """
    Replace partition and validate that the data on the destination table is the same data as on the source table.
    Also check that the data on the source table was not lost during replace partition.
    """
    node = self.context.node

    with By(
        "saving the data from the source table before replacing partitions on the destination table"
    ):
        source_data_before = node.query(
            f"SELECT i FROM {source_table} WHERE p = {partition_to_replace} ORDER BY tuple(*)"
        )

    with And("replacing partition on the destination table"):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            partition=partition_to_replace,
        )

    with Check("I check that the partition was replaced on the destination table"):
        check_partition_was_replaced(
            destination_table=destination_table,
            source_table=source_table,
            source_table_before_replace=source_data_before,
            partition=partition_to_replace,
        )


@TestScenario
def concurrent_replace(
    self, number_of_concurrent_queries, destination_table, source_table
):
    """Concurrently run the number of replace partition on the destination table."""
    with Given(
        "concurrently run multiple replace partitions on the destination table and validate that the data on both "
        "destination and source tables is the same."
    ):
        for _ in range(number_of_concurrent_queries):
            partition_to_replace = random.randrange(1, 100)

            Step(
                name="replace partition on the destination table",
                test=replace_partition_and_validate_data,
                parallel=True,
            )(
                destination_table=destination_table,
                source_table=source_table,
                partition_to_replace=partition_to_replace,
            )


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace(
        "1.0"
    )
)
@Name("concurrent replace partitions")
def feature(self, node="clickhouse1"):
    """
    Concurrently execute replace partition on a destination table with different combinations.
    Combinations used:
        * Different number of partitions both on the destination and source tables.
        * Different number of concurrent replace partitions being executed on the destination table.
        * The partition which shall be replaced is set randomly.
    """
    self.context.node = self.context.cluster.node(node)
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    number_of_concurrent_queries = 15

    create_two_tables_with_100_partitions(
        destination_table=destination_table, source_table=source_table
    )

    Scenario(test=concurrent_replace)(
        number_of_concurrent_queries=number_of_concurrent_queries,
        destination_table=destination_table,
        source_table=source_table,
    )

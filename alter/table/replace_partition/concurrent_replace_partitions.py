import random

from time import sleep

from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    replace_partition_and_validate_data,
)
from helpers.alter import *
from helpers.tables import create_table_partitioned_by_column


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
def create_two_tables(
    self, destination_table=None, source_table=None, number_of_partitions=None
):
    """Create two tables with the same structure having the specified number of partitions.
    The destination table will be used as the table where replace partition command will be
    replacing the partition and the source table will be used as the table from which partitions will be taken.
    """
    if destination_table is None:
        destination_table = self.context.destination_table

    if source_table is None:
        source_table = self.context.source_table

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    with By("creating destination table"):
        destination_table_with_partitions(
            table_name=destination_table, number_of_partitions=number_of_partitions
        )

    with And("creating source table"):
        source_table_with_partitions(
            table_name=source_table, number_of_partitions=number_of_partitions
        )


@TestScenario
def concurrent_replace(
    self,
    number_of_partitions=None,
    number_of_concurrent_queries=None,
    destination_table=None,
    source_table=None,
    delay_before=None,
    delay_after=None,
):
    """Concurrently run multiple replace partitions on the destination table and
    validate that the data on both destination and source tables is the same."""

    validate = self.context.validate

    if delay_before is None:
        delay_before = self.context.delay_before

    if delay_after is None:
        delay_after = self.context.delay_after

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if number_of_concurrent_queries is None:
        number_of_concurrent_queries = self.context.number_of_concurrent_queries

    if destination_table is None:
        destination_table = self.context.destination_table

    if source_table is None:
        source_table = self.context.source_table

    list_of_partitions_replaced = []

    for i in range(number_of_concurrent_queries):
        partition_to_replace = random.randrange(1, number_of_partitions)
        list_of_partitions_replaced.append(partition_to_replace)

        Check(
            name=f"replace partition #{i} partition {partition_to_replace}",
            test=replace_partition_and_validate_data,
            parallel=True,
        )(
            partition_to_replace=partition_to_replace,
            validate=validate,
            delay_before=delay_before,
            delay_after=delay_after,
        )

    if not validate:
        with Then("checking that the partition was replaced on the destination table"):
            for i in list_of_partitions_replaced:
                check_partition_was_replaced(
                    destination_table=destination_table,
                    source_table=source_table,
                    partition=i,
                )


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace(
        "1.0"
    )
)
@Name("concurrent replace partitions")
def feature(
    self,
    node="clickhouse1",
    number_of_partitions=100,
    number_of_concurrent_queries=100,
    delay_before=None,
    delay_after=None,
    validate=True,
):
    """
    Concurrently execute replace partition on a destination table with
    different number of concurrent replace partitions being executed in parallel and
    using a randomly picked partition.
    """
    self.context.node = self.context.cluster.node(node)
    self.context.delay_before = delay_before
    self.context.delay_after = delay_after
    self.context.destination_table = "destination_" + getuid()
    self.context.source_table = "source_" + getuid()
    self.context.number_of_partitions = number_of_partitions
    self.context.number_of_concurrent_queries = number_of_concurrent_queries
    self.context.validate = validate

    with Given(
        "I create destination and source tables for the replace partition command"
    ):
        create_two_tables()

    Scenario(test=concurrent_replace)()

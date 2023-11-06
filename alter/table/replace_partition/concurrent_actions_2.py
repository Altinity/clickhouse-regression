from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    create_two_tables_partitioned_by_column_with_data,
)
from helpers.alter import *
from helpers.tables import Column, create_table_partitioned_by_column
import random

destination_table = "destination_" + getuid()
source_table = "source_" + getuid()


@TestStep(When)
def add_column(self, table_name):
    alter_table_add_column(
        table_name=table_name,
        column_name="column_" + getuid(),
        column_type="String",
    )


@TestStep(When)
def add_column_to_destination_table(self):
    """Alter add column to the destination table."""
    add_column(table_name=destination_table)


@TestStep(When)
def add_column_to_source_table(self):
    """Alter add column to the source table."""
    add_column(table_name=destination_table)


@TestStep(When)
def add_drop_column(self, table_name):
    alter_table_add_column(
        table_name=table_name, column_name="additional_column", column_type="String"
    )


@TestCheck
def concurrent_replace(
    self,
    action,
    partition_to_replace,
    number_of_concurrent_queries,
):
    node = self.context.node

    try:
        with Given("I have two partitioned tables with the same structure"):
            create_two_tables_partitioned_by_column_with_data(
                destination_table=destination_table,
                source_table=source_table,
            )

        with When(
            "I save the data from the source table before replacing partitions on the destination table"
        ):
            source_data_before = node.query(
                f"SELECT i FROM {source_table} WHERE p = {partition_to_replace} ORDER BY tuple(*)"
            )

        with And("I execute replace partition concurrently with another action"):
            Step(
                name="replace partition on the destination table",
                test=replace_partition,
                parallel=True,
            )(
                destination_table=destination_table,
                source_table=source_table,
                partition=partition_to_replace,
            )
            for _ in range(number_of_concurrent_queries):
                Step(
                    name=f"{action.__name__}",
                    test=action,
                    parallel=True,
                )()

        with Check("I check that the partition was replaced on the destination table"):
            check_partition_was_replaced(
                destination_table=destination_table,
                source_table=source_table,
                source_table_before_replace=source_data_before,
            )
    finally:
        with Finally("I delete both source and destination tables"):
            node.query(f"DROP TABLE {destination_table}")
            node.query(f"DROP TABLE {source_table}")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent("1.0"))
@Name("concurrent actions2")
def feature(self, node="clickhouse1"):
    """Check that it is possible to perform other actions at the same time as replace partitions is being triggered."""
    self.context.node = self.context.cluster.node(node)
    partition_to_replace = 1
    number_of_concurrent_queries = 5
    actions = [add_column_to_destination_table, add_column_to_source_table]

    for action in actions:
        Scenario(test=concurrent_replace)(
            partition_to_replace=partition_to_replace,
            number_of_concurrent_queries=number_of_concurrent_queries,
            action=action,
        )

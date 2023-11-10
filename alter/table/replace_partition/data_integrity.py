from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from alter.table.replace_partition.common import (
    create_two_tables_partitioned_by_column_with_data,
    replace_partition_and_validate_data,
    create_table_partitioned_by_column_with_data,
)


@TestScenario
def keep_data_on_a_source_table(self):
    """Creating two tables and checking that the `REPLACE PARTITION` does not delete the data from the source table."""
    source_table = "source" + getuid()
    destination_table = "destination" + getuid()

    with Given("I have two tables with the same structure"):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Then(
        "I replace partition on destination table from the source table and validate the data"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace=1,
        )


@TestOutline
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NonExistentPartition("1.0")
)
def non_existent_partition(
    self, destination_partitions, source_partitions, partition_to_replace
):
    source_table = "source" + getuid()
    destination_table = "destination" + getuid()

    with Given(
        f"I have a destination table that has {destination_partitions} partitions"
    ):
        create_table_partitioned_by_column_with_data(
            table_name=destination_table, number_of_partitions=destination_partitions
        )

    with And(f"I have a source table that has {source_partitions} partitions"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, number_of_partitions=source_partitions
        )

    with Then(
        "I replace partition that does not exist on the destination table but exists on the source table"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace=partition_to_replace,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NonExistentPartition("1.0")
)
def non_existent_partition_destination(self):
    """Check that it is possible to replace partition on the destination table from the non-existent partition on the source table."""

    non_existent_partition(
        destination_partitions=5, source_partitions=10, partition_to_replace=9
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NonExistentPartition("1.0")
)
def non_existent_partition_source(self):
    """Check that it is possible to replace partition on the destination table from the non-existent partition on the source table."""
    non_existent_partition(
        destination_partitions=10, source_partitions=5, partition_to_replace=9
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_KeepData("1.0"))
@Name("data integrity")
def feature(self, node="clickhouse1"):
    """Check the integrity of the data is kept after replacing partition from source table to the destination table."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=keep_data_on_a_source_table)
    Scenario(run=non_existent_partition_destination)
    Scenario(run=non_existent_partition_source)

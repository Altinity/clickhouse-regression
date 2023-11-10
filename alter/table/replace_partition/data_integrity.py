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


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NonExistentPartition("1.0")
)
def non_existent_partition_destination(self):
    """Check that it is possible to replace partition on the destination table from the non-existent partition on the source table."""
    source_table = "source" + getuid()
    destination_table = "destination" + getuid()

    with Given("I have a destination table that has 5 partitions"):
        create_table_partitioned_by_column_with_data(
            table_name=destination_table, number_of_partitions=5
        )

    with And("I have a source table that has 10 partitions"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, number_of_partitions=10
        )

    with Then(
        "I replace partition that does not exist on the destination table but exists on the source table"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace=10,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_NonExistentPartition("1.0")
)
def non_existent_partition_source(self):
    """Check that it is possible to replace partition on the destination table from the non-existent partition on the source table."""
    source_table = "source" + getuid()
    destination_table = "destination" + getuid()

    with Given("I have a destination table that has 10 partitions"):
        create_table_partitioned_by_column_with_data(
            table_name=destination_table, number_of_partitions=10
        )

    with And("I have a source table that has 5 partitions"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, number_of_partitions=5
        )

    with Then(
        "I replace partition that does not exist on the destination table but exists on the source table"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace=10,
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

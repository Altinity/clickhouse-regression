from testflows.asserts import *
from testflows.core import *

from alter.table.replace_partition.common import (
    create_two_tables_partitioned_by_column_with_data,
    replace_partition_and_validate_data,
    create_table_partitioned_by_column_with_data,
)
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition, check_clickhouse_version


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
    """Replace partition that does not exist either on the destination or the source table."""
    node = self.context.node
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

    source_partition_is_empty = partition_to_replace > source_partitions

    if source_partition_is_empty and check_clickhouse_version(">=26.6")(self):
        select_destination = (
            f"SELECT i FROM {destination_table} WHERE p = {partition_to_replace} "
            "ORDER BY tuple(*) FORMAT TabSeparated"
        )

        with And("I save the data of the partition on the destination table"):
            data_before = node.query(select_destination).output

        with Then(
            "replace partition is refused because the source partition has no parts"
        ):
            replace_partition(
                destination_table=destination_table,
                source_table=source_table,
                partition=partition_to_replace,
                exitcode=36,
                message="has no parts in partition",
            )

        with And("the data of the destination table is kept"):
            assert node.query(select_destination).output == data_before, error()
    else:
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


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_System_Parts("1.0"))
def partition_changes_in_system(self):
    """Check that partition changes are reflected inside the system.parts table."""
    node = self.context.node
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

    with And(
        "validate that changes inside the partition were reflected in the system.parts table"
    ):
        for retry in retries(timeout=30):
            with retry:
                destination_parts = node.query(
                    f"SELECT partition, part_type, name FROM system.parts WHERE table = '{destination_table}' FORMAT TabSeparated"
                )
                source_parts = node.query(
                    f"SELECT partition, part_type, name FROM system.parts WHERE table = '{destination_table}' FORMAT TabSeparated"
                )
                assert (
                    destination_parts.output.strip() == source_parts.output.strip()
                ), error()


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_KeepData("1.0"))
@Name("data integrity")
def feature(self, node="clickhouse1"):
    """Check the integrity of the data is kept after replacing partition from source table to the destination table."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=keep_data_on_a_source_table)
    Scenario(run=non_existent_partition_destination)
    Scenario(run=non_existent_partition_source)
    Scenario(run=partition_changes_in_system)

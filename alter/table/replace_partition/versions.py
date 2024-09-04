import random

from testflows.core import *

from alter.table.replace_partition.common import (
    replace_partition_and_validate_data,
    create_two_tables_partitioned_by_column_with_data,
    create_table_partitioned_by_column_with_data,
)
from alter.table.replace_partition.requirements.requirements import (
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions,
)
from helpers.common import getuid, check_clickhouse_version


@TestStep(Given)
def save_binary_to_another_directory(self):
    """Copy the existing binary file to the separate directory in order to save it."""
    node_with_different_version = self.context.node_with_different_version

    node_with_different_version.command("mkdir /usr/bin/clickhouse_main_version")
    node_with_different_version.command(
        "cp /usr/bin/clickhouse /usr/bin/clickhouse_main_version"
    )


@TestStep(When)
def change_clickhouse_version(self):
    """Change the current ClickHouse version to different version."""
    node_with_different_version = self.context.node_with_different_version

    with By("moving the ClickHouse binary to /usr/bin and restarting it"):
        node_with_different_version.stop_clickhouse(safe=False)

        if check_clickhouse_version(">=24.4")(self):
            node_with_different_version.command(
                "cp /usr/bin/clickhouse_different_version/clickhouse /usr/bin"
            )
        else:
            node_with_different_version.command(
                "cp /usr/bin/clickhouse_different_version/* /usr/bin"
            )

        node_with_different_version.start_clickhouse(check_version=False)

    with And("checking the current version"):
        version = node_with_different_version.query("SELECT version()").output
        assert version != self.context.clickhouse_version


@TestStep(When)
def revert_clickhouse_version(self):
    """Change the current ClickHouse version to the one that was selected on the test program run."""
    node_with_different_version = self.context.node_with_different_version

    with By(
        f"moving the ClickHouse {self.context.clickhouse_version} binary to /usr/bin and restarting the ClickHouse server"
    ):
        node_with_different_version.stop_clickhouse(safe=False)

        if check_clickhouse_version(">=24.3")(self):
            node_with_different_version.command(
                "cp /usr/bin/clickhouse_main_version/clickhouse /usr/bin"
            )
        else:
            node_with_different_version.command(
                "cp /usr/bin/clickhouse_main_version/* /usr/bin"
            )

        node_with_different_version.start_clickhouse(check_version=False)

    with And("checking the current version"):
        version = node_with_different_version.query("SELECT version()").output
        assert version == self.context.clickhouse_version


@TestCheck
def different_clickhouse_versions(
    self, node, change_clickhouse_version, partitions=None
):
    """Create destination and source tables and try to replace partition on a given node."""
    node_with_different_version = self.context.node_with_different_version
    destination_table_name = f"destination_{getuid()}"
    source_table_name = f"source_{getuid()}"

    if partitions is None:
        partitions = self.context.partitions

    list_of_partitions = [i for i in range(1, partitions + 1)]

    with Given(
        "I create destination and source tables on nodes with different clickhouse versions"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table_name,
            source_table=source_table_name,
            node=node_with_different_version,
            number_of_partitions=partitions,
        )

    with When(
        "I change the ClickHouse version on the {node_23_3}",
    ):
        change_clickhouse_version()

    with Then(
        f"I replace partition from the {source_table_name} table to the {destination_table_name} table"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table_name,
            source_table=source_table_name,
            partition_to_replace=random.choice(list_of_partitions),
            node=node_with_different_version,
        )


@TestCheck
def newly_created_tables_after_update(
    self,
    before_update_table,
    after_update_table,
    destination_table,
    source_table,
    partitions=None,
):
    """Update the ClickHouse version on the current node and create new destination or source table and try to replace partition."""

    node_with_different_version = self.context.node_with_different_version

    if partitions is None:
        partitions = self.context.partitions

    list_of_partitions = [i for i in range(1, partitions + 1)]

    with Given(
        "I create destination and source tables on nodes with different clickhouse versions"
    ):
        create_table_partitioned_by_column_with_data(
            table_name=before_update_table,
            number_of_partitions=partitions,
            node=node_with_different_version,
        )

    with When(
        "I change the ClickHouse version on the {node_with_different_version}",
    ):
        revert_clickhouse_version()

    with And("I create a new table on the newly updated ClickHouse version"):
        create_table_partitioned_by_column_with_data(
            table_name=after_update_table,
            number_of_partitions=partitions,
            node=node_with_different_version,
        )

    with Then(
        f"I replace partition from the {source_table} table to the {destination_table} table"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace=random.choice(list_of_partitions),
            node=node_with_different_version,
        )


@TestScenario
def replace_partition_on_updated_version(self):
    """Change the current version of ClickHouse to 23.3 and replace partition on the destination table."""
    node = self.context.node_with_different_version
    with By("setting the version to the selected one and reverting to the 23.3"):
        revert_clickhouse_version()
        different_clickhouse_versions(
            node=node, change_clickhouse_version=change_clickhouse_version
        )


@TestScenario
def replace_partition_on_updated_and_reverted_version(self):
    """Change the 23.3 version to the version that was selected on the test program run and replace partition on the
    destination table."""
    node = self.context.node_with_different_version
    with By("setting the current version to 23.3 and updating it to the selected"):
        change_clickhouse_version()
        different_clickhouse_versions(
            node=node, change_clickhouse_version=revert_clickhouse_version
        )


@TestScenario
def replace_partition_on_table_created_after_update(self):
    """Actions on this test:
    - Create table
    - Update ClickHouse version
    - Create new table
    - Replace partition on the table that was created after update
    """
    table_before_update = f"destination_{getuid()}"
    table_after_update = f"source_{getuid()}"

    newly_created_tables_after_update(
        before_update_table=table_before_update,
        after_update_table=table_after_update,
        destination_table=table_after_update,
        source_table=table_before_update,
    )


@TestScenario
def replace_partition_on_table_created_before_update(self):
    """Actions on this test:
    - Create table
    - Update ClickHouse version
    - Create new table
    - Replace partition on the table that was created before update
    """
    table_before_update = f"destination_{getuid()}"
    table_after_update = f"source_{getuid()}"

    newly_created_tables_after_update(
        before_update_table=table_before_update,
        after_update_table=table_after_update,
        destination_table=table_before_update,
        source_table=table_after_update,
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions("1.0"))
@Name("clickhouse versions")
def feature(self, partitions=15):
    """Check that it is possible to replace partition on destination table when ClickHouse version was changed.
    Versions:
        ClickHouse main version selected for the test run
        ClickHouse versions that differs from the main ClickHouse versions. Default: 23.3
    """
    self.context.current_node = self.context.cluster.node("clickhouse1")
    self.context.node_with_different_version = self.context.cluster.node(
        "clickhouse-different-versions"
    )
    self.context.partitions = partitions

    with Given(
        "I copy the ClickHouse version into a different directory",
        description="we copy the current version into a different directory in order to bring it back when needed "
        "after it will be replaced",
    ):
        save_binary_to_another_directory()

    for scenario in loads(current_module(), Scenario):
        scenario()

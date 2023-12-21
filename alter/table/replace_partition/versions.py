import random
from time import sleep

from testflows.core import *
from alter.table.replace_partition.requirements.requirements import (
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions,
)
from helpers.common import getuid
from alter.table.replace_partition.common import (
    create_partitions_with_random_uint64,
    replace_partition_and_validate_data,
    create_two_tables_partitioned_by_column_with_data,
    create_table_partitioned_by_column_with_data,
)


@TestStep(Given)
def copy_23_3_version(self):
    node_23_3 = self.context.node_23_3

    node_23_3.command("mkdir /usr/bin/clickhouse_23_3")
    node_23_3.command("cp /usr/bin/clickhouse /usr/bin/clickhouse_23_3")
    node_23_3.command("cp /usr/bin/clickhouse-odbc-bridge /usr/bin/clickhouse_23_3")


@TestStep(Given)
def create_table_on_cluster(self, table_name):
    """Create table on a cluster"""

    node = self.context.node_23_3

    with By("creating a MergeTree table on a replicated_different_versions cluster"):
        node.query(
            f"CREATE TABLE {table_name} ON CLUSTER replicated_different_versions (p Int16, i UInt64) "
            f"ENGINE=ReplicatedMergeTree('/clickhouse/tables/{{shard}}/default/{table_name}', '{{replica}}') ORDER BY "
            f"tuple() PARTITION BY p"
        )


@TestStep(When)
def change_version_to_23_3(self):
    """Change the current ClickHouse version to ClickHouse 23.3."""
    node_23_3 = self.context.node_23_3

    with By("moving the ClickHouse 23.3 binary to /usr/bin and restarting it"):
        node_23_3.stop_clickhouse(safe=False)

        # remove_clickhouse_binaries()
        node_23_3.command("cp /usr/bin/clickhouse_23_3/* /usr/bin")
        node_23_3.start_clickhouse(check_version=False)


@TestStep(When)
def change_version_to_selected(self):
    """Change the current ClickHouse version to the one that was selected on the test program run."""
    node_23_3 = self.context.node_23_3

    with By(
        f"moving the ClickHouse {self.context.clickhouse_version} binary to /usr/bin and restarting it"
    ):
        node_23_3.stop_clickhouse(safe=False)

        # remove_clickhouse_binaries()
        node_23_3.command("cp /usr/bin/clickhouse_selected_version/* /usr/bin")
        node_23_3.start_clickhouse(check_version=False)


@TestCheck
def different_clickhouse_versions(
    self, node, change_clickhouse_version, partitions=None
):
    """Create destination and source tables and try to replace partition on a given node."""
    node_23_3 = self.context.node_23_3
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
            node=node_23_3,
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
            node=node_23_3,
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

    node_23_3 = self.context.node_23_3

    if partitions is None:
        partitions = self.context.partitions

    list_of_partitions = [i for i in range(1, partitions + 1)]

    with Given(
        "I create destination and source tables on nodes with different clickhouse versions"
    ):
        create_table_partitioned_by_column_with_data(
            table_name=before_update_table,
            number_of_partitions=partitions,
            node=node_23_3,
        )

    with When(
        "I change the ClickHouse version on the {node_23_3}",
    ):
        change_version_to_selected()

    with And("I create a new table on the newly updated ClickHouse version"):
        create_table_partitioned_by_column_with_data(
            table_name=after_update_table,
            number_of_partitions=partitions,
            node=node_23_3,
        )

    with Then(
        f"I replace partition from the {source_table} table to the {destination_table} table"
    ):
        replace_partition_and_validate_data(
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace=random.choice(list_of_partitions),
            node=node_23_3,
        )


@TestScenario
def replace_partition_on_updated_version(self):
    """Change the current version of ClickHouse to 23.3 and replace partition on the destination table."""
    node = self.context.node_23_3
    with By("setting the version to the selected one and reverting to the 23.3"):
        change_version_to_selected()
        different_clickhouse_versions(
            node=node, change_clickhouse_version=change_version_to_23_3
        )


@TestScenario
def replace_partition_on_updated_and_reverted_version(self):
    """Change the 23.3 version to the version that was selected on the test program run and replace partition on the
    destination table."""
    node = self.context.node_23_3
    with By("setting the current version to 23.3 and updating it to the selected"):
        change_version_to_23_3()
        different_clickhouse_versions(
            node=node, change_clickhouse_version=change_version_to_selected
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
        ClickHouse 23.3
        ClickHouse selected on test run
    """
    self.context.current_node = self.context.cluster.node("clickhouse1")
    self.context.node_23_3 = self.context.cluster.node("clickhouse-23-3")
    self.context.partitions = partitions

    with Given(
        "I copy the current ClickHouse 23.3 version into a different file",
        description="we copy the current version into a different file in order to bring it back when needed after it will be replaced",
    ):
        copy_23_3_version()

    for scenario in loads(current_module(), Scenario):
        scenario()

from testflows.core import *
from alter.table.replace_partition.requirements.requirements import (
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions,
)
from helpers.common import getuid
from alter.table.replace_partition.common import (
    create_partitions_with_random_uint64,
    replace_partition_and_validate_data,
)


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


@TestStep(Then)
def populate_tables_with_data(self, node, destination_table, source_table):
    """Populate two tables with data and check replace partition works."""
    with By("populating both destination and source tables with data"):
        create_partitions_with_random_uint64(
            node=node,
            table_name=destination_table,
        )
        create_partitions_with_random_uint64(
            node=node,
            table_name=source_table,
        )

    with And("replacing partition on the destination table and validating the data"):
        replace_partition_and_validate_data(
            node=node,
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace="1",
        )


@TestStep(When)
def fetch_table(self, node, table_name):
    node.query(
        f"ALTER TABLE {table_name} FETCH PARTITION 1 FROM '/clickhouse/tables/01/default/{table_name}'"
    )
    node.query(f"ALTER TABLE {table_name} ATTACH PARTITION 1")


@TestCheck
def different_clickhouse_versions(self, node, action):
    """Create destination and source tables and try to replace partition on a given node."""
    current_node = self.context.current_node
    destination_table_name = f"destination_{getuid()}"
    source_table_name = f"source_{getuid()}"

    with Given(
        "I create destination and source tables on nodes with different clickhouse versions"
    ):
        create_table_on_cluster(table_name=destination_table_name)
        create_table_on_cluster(table_name=source_table_name)

    with When("I populate both tables with data to create partitions"):
        populate_tables_with_data(
            node=node,
            destination_table=destination_table_name,
            source_table=source_table_name,
        )

    with Then(
        "I fetch partition from the remote server and validate that the data was replaced on the destination table",
        description="The remote server in this instance has a different ClickHouse version compared to the current node",
    ):
        action(
            node=current_node,
            destination_table=destination_table_name,
            source_table=source_table_name,
        )


@TestStep(Then)
def fetch_destination_table(self, node, destination_table, source_table):
    with By(
        f"fetching partition from the {destination_table} table on remote server to the current node"
    ):
        fetch_table(node=node, table_name=destination_table)

    with And("replacing partition and validating the data on the destination table"):
        replace_partition_and_validate_data(
            node=node,
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace="1",
        )


@TestStep(Then)
def fetch_source_table(self, node, destination_table, source_table):
    with By(
        f"fetching partition from {source_table} table on the remote server to the current node"
    ):
        fetch_table(node=node, table_name=source_table)

    with And("replacing partition and validating the data on the destination table"):
        replace_partition_and_validate_data(
            node=node,
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace="1",
        )


@TestStep(Then)
def fetch_destination_and_source_table(self, node, destination_table, source_table):
    with By(
        f"fetching partition from the {destination_table} and {source_table} tables on remote server to the current node"
    ):
        fetch_table(node=node, table_name=source_table)
        fetch_table(node=node, table_name=destination_table)

    with And("replacing partition and validating the data on the destination table"):
        replace_partition_and_validate_data(
            node=node,
            destination_table=destination_table,
            source_table=source_table,
            partition_to_replace="1",
        )


values = [
    fetch_destination_table,
    fetch_source_table,
    fetch_destination_and_source_table,
]


@TestSketch(Scenario)
def replace_partition_on_23_3(self):
    """Copy partition from the table that is stored on the server with ClickHouse 23.3 to the current version and replace partition."""
    node = self.context.node_23_3
    different_clickhouse_versions(node=node, action=either(*values))


@TestScenario
def replace_partition_on_23_8(self):
    """Copy partition from the table that is stored on the server with ClickHouse 23.8 to the current version and replace partition."""
    node = self.context.node_23_8
    different_clickhouse_versions(node=node, action=either(*values))


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions("1.0"))
@Name("clickhouse versions")
def feature(self):
    """Check that replace partition works when there are multiple nodes in a cluster and each node has different
    ClickHouse versions. Destination and source tables are created on one of the ClickHouse versions, we move the
    partition to the current version and check that replace partition works correctly.


    Versions:
        ClickHouse 23.3
        ClickHouse 23.8
    """
    self.context.current_node = self.context.cluster.node("clickhouse1")
    self.context.node_23_3 = self.context.cluster.node("clickhouse-23-3")
    self.context.node_23_8 = self.context.cluster.node("clickhouse-23-8")

    Scenario(run=replace_partition_on_23_3)
    Scenario(run=replace_partition_on_23_8)

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
def create_table_on_cluster(self, table_name, node=None):
    """Create table on a cluster"""

    if node is None:
        node = self.context.node

    with By("creating a MergeTree table on a replicated_different_versions cluster"):
        node.query(
            f"CREATE TABLE {table_name} ON CLUSTER replicated_different_versions (p Int16, i UInt64) "
            f"ENGINE=MergeTree ORDER BY tuple() PARTITION BY p; "
        )


@TestStep(Then)
def populate_table_with_data_and_replace_partition(
    self, node, destination_table, source_table
):
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


@TestOutline
def different_clickhouse_versions(self, node):
    """Create destination and source tables and try to replace partition on a given node."""
    destination_table_name = f"destination_{getuid()}"
    source_table_name = f"source_{getuid()}"
    with Given(
        "I create destination and source tables on nodes with different clickhouse versions"
    ):
        create_table_on_cluster(table_name=destination_table_name)
        create_table_on_cluster(table_name=source_table_name)

    with Then("I validate that replacing partition on the given node is possible"):
        populate_table_with_data_and_replace_partition(
            node=node,
            destination_table=destination_table_name,
            source_table=source_table_name,
        )


@TestScenario
def replace_partition_on_23_3(self):
    """Replace partition on the table that is stored on the node with clickhouse 23_3 version."""
    node = self.context.node
    different_clickhouse_versions(node=node)


@TestScenario
def replace_partition_on_23_8(self):
    """Replace partition on the table that is stored on the node with clickhouse 23_8 version."""
    node = self.context.node_23_8
    different_clickhouse_versions(node=node)


@TestScenario
def replace_partition_on_specified(self):
    """Replace partition on the table that is stored on the node with clickhouse version specified on the test run."""
    node = self.context.current_node
    different_clickhouse_versions(node=node)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Versions("1.0"))
@Name("clickhouse versions")
def feature(self):
    """Check that replace partition works when there are multiple nodes in a cluster and each node has different
    ClickHouse versions. Destination and source tables are created on one of the ClickHouse versions, and we try to
    replace partition on each node.


    Versions:
        ClickHouse 23.3
        ClickHouse 23.8
        The version that is provided on a test program run
    """
    self.context.current_node = self.context.cluster.node("clickhouse1")
    self.context.node = self.context.cluster.node("clickhouse-23-3")
    self.context.node_23_8 = self.context.cluster.node("clickhouse-23-8")

    versions = [
        replace_partition_on_23_3,
        replace_partition_on_23_8,
        replace_partition_on_specified,
    ]

    for version in versions:
        Scenario(run=version)

import random

from itertools import combinations
from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from alter.table.replace_partition.common import create_partitions_with_random_uint64


@TestScenario
def different_nodes_same_destination(self, cluster, node1, node2):
    """Test export part from different nodes to same S3 destination in a given cluster."""

    with Given("I create an empty source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
            cluster=cluster,
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, cluster=cluster
        )

    with And("I populate the source tables on both nodes"):
        create_partitions_with_random_uint64(table_name="source", node=node1)
        create_partitions_with_random_uint64(table_name="source", node=node2)

    with When("I export parts to the S3 table from both nodes"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=node1,
        )
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=node2,
        )

    with And("I read data from all tables on both nodes"):
        source_data1 = select_all_ordered(table_name="source", node=node1)
        source_data2 = select_all_ordered(table_name="source", node=node2)
        destination_data1 = select_all_ordered(table_name=s3_table_name, node=node1)
        destination_data2 = select_all_ordered(table_name=s3_table_name, node=node2)

    with Then(
        "Destination data should be comprised of data from both sources, and identical on both nodes"
    ):
        assert set(destination_data1) == set(source_data1) | set(source_data2), error()
        assert set(destination_data2) == set(source_data1) | set(source_data2), error()


@TestFeature
@Name("clusters and nodes")
def feature(self):
    """Check functionality of exporting data parts to S3 storage from different clusters and nodes."""

    clusters = [
        "sharded_cluster",
        "replicated_cluster",
        "one_shard_cluster",
        "sharded_cluster12",
        "one_shard_cluster12",
        "sharded_cluster23",
        "one_shard_cluster23",
    ]

    for cluster in clusters:
        with Given(f"I get nodes for cluster {cluster}"):
            node_names = get_cluster_nodes(cluster=cluster)

        for node1_name, node2_name in combinations(node_names, 2):
            node1 = self.context.cluster.node(node1_name)
            node2 = self.context.cluster.node(node2_name)
            different_nodes_same_destination(cluster=cluster, node1=node1, node2=node2)

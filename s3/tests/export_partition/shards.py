from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import partitioned_merge_tree_table
from s3.tests.export_partition.steps import *
from helpers.queries import *
from s3.requirements.export_partition import *
from alter.table.replace_partition.common import create_partitions_with_random_uint64


@TestScenario
def sharded_table_with_distributed_engine(self, cluster, nodes):
    """Test export partition from a sharded table using Distributed engine with sharding key."""

    with Given("I create local MergeTree tables on each shard and a Distributed table"):
        local_table_name = "local_" + getuid()

        partitioned_merge_tree_table(
            table_name=local_table_name,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
            cluster=cluster,
        )

        distributed_table_name = create_distributed_table(
            cluster=cluster,
            local_table_name=local_table_name,
            node=nodes[0],
        )

        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, cluster=cluster
        )

        node = nodes[0]

    with And(
        "I insert data through the Distributed table (data will be distributed across shards)"
    ):
        create_partitions_with_random_uint64(
            table_name=distributed_table_name,
            number_of_values=200,
            node=node,
        )

    with And("I wait for data to be distributed to all shards"):
        wait_for_distributed_table_data(
            table_name=distributed_table_name,
            expected_count=1000,
            node=node,
        )

    with When("I export partitions from each shard's local table"):
        for shard_node in nodes:
            export_partitions(
                source_table=local_table_name,
                destination_table=s3_table_name,
                node=shard_node,
            )

    with And("I wait for all exports to complete on all nodes"):
        for shard_node in nodes:
            wait_for_all_exports_to_complete(
                node=shard_node, table_name=local_table_name
            )

    with Then("I verify exported data matches the Distributed table data"):
        source_matches_destination(
            source_table=distributed_table_name,
            destination_table=s3_table_name,
            source_node=node,
        )


@TestFeature
# @Requirements()
@Name("shards")
def feature(self):
    """Verify exporting partitions from sharded tables using Distributed engine."""

    sharded_clusters = [
        "sharded_cluster",
        "sharded_cluster12",
        "sharded_cluster23",
    ]

    for cluster in sharded_clusters:
        with Given(f"I get all nodes for sharded cluster {cluster}"):
            node_names = get_cluster_nodes(cluster=cluster)
            nodes = [self.context.cluster.node(name) for name in node_names]

        sharded_table_with_distributed_engine(cluster=cluster, nodes=nodes)

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from s3.tests.export_part.steps import *
from helpers.queries import *
from s3.requirements.export_part import *
from alter.table.replace_partition.common import create_partitions_with_random_uint64


@TestScenario
def sharded_table_with_distributed_engine(self, cluster, nodes):
    """Test export part from a sharded table using Distributed engine with sharding key."""

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

    with When("I export parts from each shard's local table"):
        for shard_node in nodes:
            export_parts(
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
            node=node,
        )


@TestScenario
def distributed_table_without_sharding_key_error(self, cluster, nodes):
    """Test that inserts into a Distributed table without a sharding key fail when there are multiple shards."""

    with Given("I create local MergeTree tables on each shard and a Distributed table without sharding key"):
        local_table_name = "local_" + getuid()

        partitioned_merge_tree_table(
            table_name=local_table_name,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
            cluster=cluster,
        )

        distributed_table_name = f"distributed_{getuid()}"
        nodes[0].query(
            f"""
            CREATE TABLE {distributed_table_name} AS {local_table_name}
            ENGINE = Distributed({cluster}, default, {local_table_name})
            """,
            exitcode=0,
            steps=True,
        )

        node = nodes[0]

    with When("I try to insert data through the Distributed table without sharding key"):
        result = insert_random_data(
            table_name=distributed_table_name,
            number_of_values=200,
            node=node,
            no_checks=True,
        )

    with Then("I verify the error indicates sharding key is required"):
        assert result.exitcode == 55, error()
        assert "STORAGE_REQUIRES_PARAMETER" in result.output or "sharding key" in result.output.lower(), error()


@TestScenario
def distributed_table_with_invalid_sharding_key(self, cluster, nodes):
    """Test that creating a Distributed table with an invalid sharding key fails appropriately."""

    with Given("I create local MergeTree tables on each shard"):
        local_table_name = "local_" + getuid()

        partitioned_merge_tree_table(
            table_name=local_table_name,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
            cluster=cluster,
        )

        node = nodes[0]

    with When("I try to create a Distributed table with an invalid sharding key"):
        distributed_table_name = f"distributed_{getuid()}"
        result = node.query(
            f"""
            CREATE TABLE {distributed_table_name} AS {local_table_name}
            ENGINE = Distributed({cluster}, default, {local_table_name}, invalid_column_name)
            """,
            no_checks=True,
            steps=True,
        )

    with Then("I verify the error indicates invalid sharding key"):
        assert result.exitcode == 47, error()
        assert "UNKNOWN_IDENTIFIER" in result.output or "BAD_ARGUMENTS" in result.output, error()


@TestScenario
def distributed_table_with_nonexistent_local_table(self, cluster, nodes):
    """Test that using a Distributed table pointing to a non-existent local table fails when inserting."""

    with Given("I have a non-existent local table name"):
        nonexistent_local_table = "nonexistent_" + getuid()
        node = nodes[0]

    with And("I create a Distributed table pointing to non-existent local table"):
        distributed_table_name = f"distributed_{getuid()}"
        node.query(
            f"""
            CREATE TABLE {distributed_table_name} (p UInt8, i UInt64)
            ENGINE = Distributed({cluster}, default, {nonexistent_local_table}, rand())
            """,
            exitcode=0,
            steps=True,
        )

    with When("I try to insert data through the Distributed table"):
        result = insert_random_data(
            table_name=distributed_table_name,
            number_of_values=200,
            node=node,
            no_checks=True,
        )

    with Then("I verify the error indicates the local table doesn't exist"):
        assert result.exitcode == 60, error()
        assert "UNKNOWN_TABLE" in result.output or "TABLE_DOESNT_EXIST" in result.output, error()


@TestFeature
@Name("shards")
def feature(self):
    """Verify exporting parts from sharded tables using Distributed engine."""

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

    with Given("I get all nodes for sharded cluster"):
        node_names = get_cluster_nodes(cluster="sharded_cluster")
        nodes = [self.context.cluster.node(name) for name in node_names]

    distributed_table_without_sharding_key_error(cluster="sharded_cluster", nodes=nodes)
    distributed_table_with_invalid_sharding_key(cluster="sharded_cluster", nodes=nodes)
    distributed_table_with_nonexistent_local_table(cluster="sharded_cluster", nodes=nodes)

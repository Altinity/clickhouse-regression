from testflows.core import *
from testflows.asserts import error

import swarms.tests.common as swarm_steps


@TestScenario
def create_swarm_cluster(self):
    """Swarm cluster creation check."""

    with Given("create swarm cluster by adding first node and observer"):
        swarm_steps.add_node_to_swarm(node=self.context.node, observer=True)

    with And("add swarm node"):
        swarm_steps.add_node_to_swarm(node=self.context.node2)

    with And("add second swarm node"):
        swarm_steps.add_node_to_swarm(node=self.context.node3)

    with Then("check that swarm cluster is created"):
        for node in self.context.nodes:
            result = swarm_steps.show_clusters(node=node)
            assert "swarm" in result.output, error()

    with And(
        "check that swarm nodes (clickhouse2 and clickhouse3) are added to the cluster"
    ):
        for node in self.context.nodes:
            output = swarm_steps.check_cluster_hostnames(
                cluster_name="swarm", node=node
            )
            assert "clickhouse2" in output and "clickhouse3" in output, error()

    with And("check that observer node is not added to the cluster"):
        for node in self.context.nodes:
            output = swarm_steps.check_cluster_hostnames(
                cluster_name="swarm", node=node
            )
            assert "clickhouse1" not in output, error()


@TestScenario
def cluster_with_only_one_observer_node(
    self, minio_root_user, minio_root_password, node=None
):
    """Check that cluster with one observer node can not be used for queries."""
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create swarm cluster with name `swarm` with one observer node"):
        swarm_steps.add_node_to_swarm(node=node, observer=True)

    with Then("check that swarm cluster is not shown in the list of clusters"):
        output = swarm_steps.show_clusters(node=node)
        assert "swarm" not in output.output, error()

    with And("try to select data with s3 table function using swarm cluster"):
        node.query(
            f"""
            SELECT hostName() AS host, count()
            FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
            GROUP BY host
            SETTINGS use_hive_partitioning=1, object_storage_cluster='swarm'
            """,
            exitcode=189,
            message="DB::Exception: Requested cluster 'swarm' not found.",
        )


@TestScenario
def check_scale_up_and_down(self, minio_root_user, minio_root_password, node=None):
    """Check cluster scale up and down."""
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create swarm cluster by adding first observer node"):
        swarm_steps.add_node_to_swarm(node=node, observer=True)

    with And("add swarm node"):
        swarm_steps.add_node_to_swarm(node=self.context.node2)

    with Then("check that swarm cluster is created"):
        output = swarm_steps.show_clusters(node=node)
        assert "swarm" in output.output, error()

    with And("try to select data with s3 table function using swarm cluster"):
        result = node.query(
            f"""
            SELECT hostName() AS host
            FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
            GROUP BY host
            SETTINGS object_storage_cluster='swarm'
            """
        )

    with And("check that data was selected only by swarm nodes"):
        assert "clickhouse2" in result.output, error()
        assert "clickhouse1" not in result.output, error()

    with And("add second swarm node"):
        swarm_steps.add_node_to_swarm(node=self.context.node3)

    with And(
        "check that swarm nodes (clickhouse2 and clickhouse3) are added to the cluster"
    ):
        output = swarm_steps.check_cluster_hostnames(cluster_name="swarm", node=node)
        assert "clickhouse2" in output and "clickhouse3" in output, error()

    with And("try to select data with s3 table function using swarm cluster"):
        result = node.query(
            f"""
            SELECT hostName() AS host
            FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
            GROUP BY host
            SETTINGS object_storage_cluster='swarm'
            """
        )

    with And("check that data was selected only by swarm nodes"):
        assert "clickhouse2" in result.output or "clickhouse3" in result.output, error()
        assert "clickhouse1" not in result.output, error()

    with And("remove first (clickhouse2) swarm node"):
        swarm_steps.remove_node_from_swarm(node=self.context.node2)
        output = swarm_steps.show_clusters(node=self.context.node2)
        assert "swarm" not in output.output, error()

    with And(
        "check that initiator node sees that clickhouse2 is removed from the cluster"
    ):
        for retry in retries(count=10, delay=2):
            with retry:
                output = swarm_steps.check_cluster_hostnames(
                    cluster_name="swarm", node=node
                )
                assert "clickhouse2" not in output, error()

    with And("try to select data with s3 table function using swarm cluster"):
        result = node.query(
            f"""
            SELECT hostName() AS host
            FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet', '{minio_root_user}', '{minio_root_password}')
            GROUP BY host
            SETTINGS object_storage_cluster='swarm'
            """
        )
        with Then("check that data was selected only by one swarm node (clickhouse3)"):
            assert "clickhouse3" in result.output, error()
            assert "clickhouse1" not in result.output, error()
            assert "clickhouse2" not in result.output, error()


@TestFeature
@Name("swarm sanity checks")
def feature(self, minio_root_user, minio_root_password):
    """Run swarm sanity checks."""
    Scenario(run=create_swarm_cluster)
    Scenario(test=cluster_with_only_one_observer_node)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=check_scale_up_and_down)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

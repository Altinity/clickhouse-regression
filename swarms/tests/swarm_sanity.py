from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from iceberg.tests.steps.icebergS3 import (
    read_data_with_icebergS3_table_function,
    read_data_with_icebergS3Cluster_table_function,
)
from swarms.requirements.requirements import *

import swarms.tests.steps.swarm_steps as swarm_steps
import swarms.tests.steps.s3_steps as s3_steps


EXPECTED_DATA = "('Alice',195.23,20),('Bob',123.45,30),('Charlie',67.89,40),('David',45.67,50),('Eve',89.01,60),('Frank',12.34,70),('Grace',56.78,80),('Heidi',90.12,90),('Ivan',34.56,100),('Judy',78.9,110),('Karl',23.45,120),('Leo',67.89,130),('Mallory',11.12,140),('Nina',34.56,150)"


@TestScenario
@Requirements(
    RQ_SRS_044_Swarm_NodeRegistration("1.0"),
    RQ_SRS_044_Swarm_ClusterDiscovery_Path("1.0"),
    RQ_SRS_044_Swarm_ClusterDiscovery_Authentication("1.0"),
)
def create_swarm_cluster(self):
    """Swarm cluster creation check."""
    with Given("create swarm cluster by adding first node as observer"):
        cluster_name = "swarm_cluster" + getuid()
        swarm_steps.add_node_to_swarm(
            node=self.context.node, observer=True, cluster_name=cluster_name
        )

    with And("add first swarm node"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name
        )

    with And("add second swarm node"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node3, cluster_name=cluster_name
        )

    with Then("check that swarm cluster is created"):
        for node in [self.context.node, self.context.node2, self.context.node3]:
            result = swarm_steps.show_clusters(node=node)
            for retry in retries(count=10, delay=2):
                with retry:
                    assert cluster_name in result.output, error()

    with And(
        "check that swarm nodes (clickhouse2 and clickhouse3) are added to the cluster"
    ):
        for node in [self.context.node, self.context.node2, self.context.node3]:
            output = swarm_steps.check_cluster_hostnames(
                cluster_name=cluster_name, node=node
            )
            assert "clickhouse2" in output and "clickhouse3" in output, error()

    with And("check that observer node was not added to the cluster"):
        for node in [self.context.node, self.context.node2, self.context.node3]:
            output = swarm_steps.check_cluster_hostnames(
                cluster_name=cluster_name, node=node
            )
            assert "clickhouse1" not in output, error()


@TestScenario
@Requirements(RQ_SRS_044_Swarm_ClusterDiscovery_Path("1.0"))
def cluster_with_only_one_observer_node(
    self, minio_root_user, minio_root_password, node=None
):
    """
    Check that cluster with one observer node can not be used for queries.
    """
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create swarm cluster with one observer node"):
        cluster_name = "swarm_cluster" + getuid()
        swarm_steps.add_node_to_swarm(
            node=node, observer=True, cluster_name=cluster_name
        )

    with Then("check that swarm cluster is not shown in the list of clusters"):
        output = swarm_steps.show_clusters(node=node)
        assert cluster_name not in output.output, error()

    with And("try to select data with s3 table function using swarm cluster"):
        s3_steps.read_data_with_s3_table_function(
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            exitcode=189,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )


@TestScenario
def cluster_with_one_observer_node_and_one_swarm_node(
    self, minio_root_user, minio_root_password, node=None
):
    """
    Check that cluster is deleted when only swarm node is removed.
    """
    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create swarm cluster by adding first observer node"):
        cluster_name = "swarm_cluster" + getuid()
        swarm_steps.add_node_to_swarm(
            node=self.context.node, observer=True, cluster_name=cluster_name
        )

    with And("add first swarm node"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name
        )

    with And("check that swarm cluster is created"):
        output = swarm_steps.show_clusters(node=self.context.node)
        assert cluster_name in output.output, error()

    with And(
        """
        read data with iceberg table function with swarm cluster and 
        check that data is read only by swarm node (clickhouse2)
        """
    ):
        result = read_data_with_icebergS3_table_function(
            columns="hostName() AS host, count()",
            group_by="host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
        )
        result_rows = read_data_with_icebergS3_table_function(
            columns="*",
            order_by="tuple(*)",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            format="Values",
        )
        assert result_rows.output == EXPECTED_DATA, error()
        assert "clickhouse2" in result.output, error()
        assert "clickhouse1" not in result.output, error()

    with When("remove only swarm node"):
        swarm_steps.remove_node_from_swarm(
            node=self.context.node2, cluster_name=cluster_name
        )

    with Then("check that swarm cluster is not shown in the list of clusters"):
        for retry in retries(count=10, delay=2):
            with retry:
                output = swarm_steps.show_clusters(node=self.context.node)
                assert cluster_name not in output.output, error()

    with And("check that swarm cluster is not accessible"):
        s3_steps.read_data_with_s3_table_function(
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            exitcode=189,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )
        s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            exitcode=189,
            message=f"DB::Exception: Requested cluster '{cluster_name}' not found.",
        )


@TestScenario
@Requirements(
    RQ_SRS_044_Swarm_NodeDeregistration("1.0"),
)
def check_scale_up_and_down(self, minio_root_user, minio_root_password, node=None):
    """
    Test the scaling capabilities of a swarm cluster by:
    1. Creating a swarm cluster with an observer node
    2. Adding first swarm node (clickhouse2) and verifying it reads data
    3. Adding second swarm node (clickhouse3) and verifying both nodes read data
    4. Removing first swarm node and verifying only remaining node reads data

    This test ensures that swarm nodes can be dynamically added and removed
    while maintaining proper data access patterns through the S3 table function.
    """
    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create swarm cluster by adding first observer node"):
        cluster_name = "swarm_cluster" + getuid()
        swarm_steps.add_node_to_swarm(
            node=self.context.node, observer=True, cluster_name=cluster_name
        )

    with And("add first swarm node"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name
        )

    with And("check that swarm cluster is created"):
        output = swarm_steps.show_clusters(node=self.context.node)
        for retry in retries(count=10, delay=2):
            with retry:
                assert cluster_name in output.output, error()

    with When("try to select data with s3 table function using swarm cluster"):
        result = s3_steps.read_data_with_s3_table_function(
            columns="hostName() AS host",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            group_by="host",
        )
        result_rows = s3_steps.read_data_with_s3_table_function(
            columns="*",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            order_by="tuple(*)",
            format="Values",
        )
        assert result_rows.output == EXPECTED_DATA, error()

    with And("check that data was selected only by swarm node"):
        assert "clickhouse1" not in result.output, error()
        assert "clickhouse2" in result.output, error()

    with And("add second swarm node"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node3, cluster_name=cluster_name
        )

    with And(
        "check that swarm nodes (clickhouse2 and clickhouse3) are added to the cluster"
    ):
        for retry in retries(count=10, delay=2):
            with retry:
                for node in [self.context.node, self.context.node2, self.context.node3]:
                    output = swarm_steps.check_cluster_hostnames(
                        cluster_name=cluster_name, node=node
                    )
                    assert "clickhouse2" in output and "clickhouse3" in output, error()

    with And(
        """
        try to select data with s3 table function using swarm cluster and 
        check that data was selected only by swarm nodes
        """
    ):
        for retry in retries(count=10, delay=2):
            with retry:
                result = s3_steps.read_data_with_s3_table_function(
                    columns="hostName() AS host, count()",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                    object_storage_cluster=cluster_name,
                    group_by="host",
                    node=self.context.node,
                )
                result_rows = s3_steps.read_data_with_s3_table_function(
                    columns="*",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                    object_storage_cluster=cluster_name,
                    order_by="tuple(*)",
                    format="Values",
                )
                assert result_rows.output == EXPECTED_DATA, error()
                assert (
                    "clickhouse2" in result.output and "clickhouse3" in result.output
                ), error()
                assert "clickhouse1" not in result.output, error()

    with And("remove first (clickhouse2) swarm node from the cluster"):
        swarm_steps.remove_node_from_swarm(
            node=self.context.node2, cluster_name=cluster_name
        )

    with And(
        "check that initiator node sees that clickhouse2 is removed from the cluster"
    ):
        for retry in retries(count=10, delay=2):
            with retry:
                output = swarm_steps.check_cluster_hostnames(
                    cluster_name=cluster_name, node=self.context.node
                )
                assert "clickhouse2" not in output, error()

    with And("try to select data with s3 table function using swarm cluster"):
        result = s3_steps.read_data_with_s3_table_function(
            columns="hostName() AS host, count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            group_by="host",
        )
        result_rows = s3_steps.read_data_with_s3_table_function(
            columns="*",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            order_by="tuple(*)",
            format="Values",
        )
        assert result_rows.output == EXPECTED_DATA, error()

    with Then(
        "check that data was selected only by one remaining swarm node (clickhouse3)"
    ):
        assert "clickhouse3" in result.output, error()
        assert "clickhouse1" not in result.output, error()
        assert "clickhouse2" not in result.output, error()


@TestScenario
def swarm_examples(self, minio_root_user, minio_root_password, node=None):
    """
    Antalya examples.
    """
    if node is None:
        node = self.context.node

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("setup swarm cluster"):
        cluster_name = "swarm_cluster" + getuid()
        swarm_steps.add_node_to_swarm(
            node=node, observer=True, cluster_name=cluster_name
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, cluster_name=cluster_name
        )
        swarm_steps.add_node_to_swarm(
            node=self.context.node3, cluster_name=cluster_name
        )

    with And("select with s3 table function using swarm cluster"):
        for retry in retries(count=10, delay=1):
            with retry:
                result = s3_steps.read_data_with_s3_table_function(
                    columns="hostName() AS host, count()",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                    object_storage_cluster=cluster_name,
                    group_by="host",
                    use_hive_partitioning=1,
                )
                assert "clickhouse2" in result.output, error()
                assert "clickhouse3" in result.output, error()
                assert "clickhouse1" not in result.output, error()

        result_rows = s3_steps.read_data_with_s3_table_function(
            columns="*",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            order_by="tuple(*)",
            use_hive_partitioning=1,
            format="Values",
        )
        assert result_rows.output == EXPECTED_DATA, error()

    with And("select with s3Cluster table function"):
        for retry in retries(count=10, delay=1):
            with retry:
                result = s3_steps.read_data_with_s3Cluster_table_function(
                    cluster_name=cluster_name,
                    columns="hostName() AS host, count()",
                    group_by="host",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                )
                assert "clickhouse2" in result.output, error()
                assert "clickhouse3" in result.output, error()
                assert "clickhouse1" not in result.output, error()

        result_rows = s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="*",
            order_by="tuple(*)",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            format="Values",
        )
        assert result_rows.output == EXPECTED_DATA, error()

    with And("select with iceberg table function using swarm cluster"):
        for retry in retries(count=10, delay=1):
            with retry:
                result = read_data_with_icebergS3_table_function(
                    columns="hostName() AS host, count()",
                    group_by="host",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                    object_storage_cluster=cluster_name,
                )
                assert "clickhouse2" in result.output, error()
                assert "clickhouse3" in result.output, error()
                assert "clickhouse1" not in result.output, error()

        result_rows = read_data_with_icebergS3_table_function(
            columns="*",
            order_by="tuple(*)",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            object_storage_cluster=cluster_name,
            format="Values",
        )
        assert result_rows.output == EXPECTED_DATA, error()

    with And("select with icebergS3Cluster table function"):
        for retry in retries(count=10, delay=1):
            with retry:
                result = read_data_with_icebergS3Cluster_table_function(
                    cluster_name=cluster_name,
                    columns="hostName() AS host, count()",
                    group_by="host",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                )
                assert "clickhouse2" in result.output, error()
                assert "clickhouse3" in result.output, error()
                assert "clickhouse1" not in result.output, error()

        result_rows = read_data_with_icebergS3Cluster_table_function(
            cluster_name=cluster_name,
            columns="*",
            order_by="tuple(*)",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            format="Values",
        )
        assert result_rows.output == EXPECTED_DATA, error()


@TestFeature
@Name("swarm sanity")
def feature(self, minio_root_user, minio_root_password):
    """Run swarm cluster sanity checks."""
    Scenario(run=create_swarm_cluster)
    Scenario(test=cluster_with_only_one_observer_node)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=check_scale_up_and_down)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=swarm_examples)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Scenario(test=cluster_with_one_observer_node_and_one_swarm_node)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )

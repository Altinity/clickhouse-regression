from testflows.core import *
from testflows.asserts import error
from swarms.requirements.requirements import *
from helpers.common import (
    check_if_antalya_build,
    getuid,
    check_clickhouse_version,
)

import swarms.tests.steps.swarm_steps as swarm_steps
import swarms.tests.steps.s3_steps as s3_steps


@TestScenario
@Requirements(
    RQ_SRS_044_Swarm_NodeRegistration("1.0"), RQ_SRS_044_Swarm_NodeDeregistration("1.0")
)
def cluster_registration_deregistration(self):
    """Check that cluster registration and deregistration properly works."""
    node = self.context.node
    cluster_name = f"swarm_cluster_{getuid()}"
    path = f"/{cluster_name}_path"
    secret = "some_secret"

    with Given("check that cluster is not registered"):
        result = swarm_steps.show_clusters(node=node)
        assert cluster_name not in result.output, error()

    with And("add nodes to swarm cluster"):
        swarm_steps.add_node_to_swarm(
            node=node,
            cluster_name=cluster_name,
            path=path,
            secret=secret,
            observer=True,
        )

    with And(
        "check that since added node is observer, cluster is still not registered"
    ):
        result = swarm_steps.show_clusters(node=node)
        assert cluster_name not in result.output, error()

    with And("add second node to swarm cluster"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node2,
            cluster_name=cluster_name,
            path=path,
            secret=secret,
        )

    with And("check that cluster is registered"):
        result = swarm_steps.show_clusters(node=node)
        assert cluster_name in result.output, error()

    with And("deregister node from swarm cluster"):
        swarm_steps.remove_node_from_swarm(
            node=self.context.node2,
            cluster_name=cluster_name,
            path=path,
            secret=secret,
        )

    with And("check that cluster is deregistered"):
        for retry in retries(count=10, delay=5):
            with retry:
                swarm_steps.get_cluster_info_from_system_clusters_table(
                    cluster_name=cluster_name, node=node
                )
                result = swarm_steps.show_clusters(node=node)
                assert cluster_name not in result.output, error()


@TestScenario
@Requirements(RQ_SRS_044_Swarm_NodeRegistration_MultipleDiscoverySections("1.0"))
def multiple_discovery_sections(self, minio_root_user, minio_root_password):
    """Check that ClickHouse only uses the first discovery section in case multiple
    discovery sections are defined in the configuration file.
    """
    node = self.context.node
    cluster_name = f"swarm_cluster_{getuid()}"
    secret = "secret_key"
    path1 = f"/{cluster_name}_path"
    path2 = f"/{cluster_name}_path2"

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And(
        "define invalid config with two discovery sections with different paths: path1 and path2"
    ):
        entries = {
            "allow_experimental_cluster_discovery": "1",
            "remote_servers": {
                cluster_name: [
                    {
                        "discovery": {
                            "path": path1,
                            "secret": secret,
                            "observer": "true",
                        },
                    },
                    {"discovery": {"path": path2, "secret": secret}},
                ]
            },
        }

    with When("add config with multiple discovery sections to the node"):
        swarm_steps.add_node_to_swarm(
            node=node, entries=entries, cluster_name=cluster_name
        )

    with And("add swarm node that corresponds to first discovery section"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node2,
            cluster_name=cluster_name,
            path=path1,
            secret=secret,
        )

    with And("add second swarm node that corresponds to second discovery section"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node3,
            cluster_name=cluster_name,
            path=path2,
            secret=secret,
        )

    with Then(
        "select with s3Cluster fails and check that only first discovery section is used"
    ):
        result = s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName(), count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            group_by="hostName()",
        )
        with By("check that clickhouse1 is not in result since it is an observer"):
            assert "clickhouse1" not in result.output, error()
        with And("check that clickhouse2 is in result"):
            assert "clickhouse2" in result.output, error()
        with And("check that clickhouse3 is not in result"):
            assert "clickhouse3" not in result.output, error()

    with Then(
        "select with s3 table function with swarm cluster and check that only first discovery section is used"
    ):
        if check_if_antalya_build(self):
            result = s3_steps.read_data_with_s3_table_function(
                object_storage_cluster=cluster_name,
                columns="hostName(), count()",
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
                group_by="hostName()",
            )
            with By("check that clickhouse1 is not in result since it is an observer"):
                assert "clickhouse1" not in result.output, error()
            with And("check that clickhouse2 is in result"):
                assert "clickhouse2" in result.output, error()
            with And("check that clickhouse3 is not in result"):
                assert "clickhouse3" not in result.output, error()


@TestScenario
@Requirements(RQ_SRS_044_Swarm_ClusterDiscovery_MultiplePaths("1.0"))
def multiple_paths(self, minio_root_user, minio_root_password):
    """Check that ClickHouse uses the first path in case multiple paths are defined."""
    node = self.context.node
    cluster_name = f"swarm_cluster_multiple_paths_{getuid()}"
    secret = "secret_key"
    path1 = f"/{cluster_name}_path"
    path2 = f"/{cluster_name}_path2"

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("define invalid config with two paths"):
        entries = {
            "allow_experimental_cluster_discovery": "1",
            "remote_servers": {
                cluster_name: [
                    {
                        "discovery": {
                            "path": [
                                path1,
                                path2,
                            ],
                            "secret": secret,
                            "observer": "true",
                        },
                    },
                ]
            },
        }

    with And("add invalid config to the first node"):
        swarm_steps.add_node_to_swarm(
            node=node,
            entries=entries,
            duplicate_tags=True,
        )

    with And("add swarm node to swarm cluster with first path"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node2,
            cluster_name=cluster_name,
            path=path1,
            secret=secret,
        )

    with And("add second swarm node to swarm cluster with second path"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node3,
            cluster_name=cluster_name,
            path=path2,
            secret=secret,
        )

    with Then("select with s3Cluster fails and check that only first path is used"):
        result = s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName(), count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            group_by="hostName()",
        )
        with By("check that clickhouse1 is not in result since it is an observer"):
            assert "clickhouse1" not in result.output, error()
        with And("check that clickhouse2 is in result"):
            assert "clickhouse2" in result.output, error()
        with And("check that clickhouse3 is not in result"):
            assert "clickhouse3" not in result.output, error()

    with Then("select with s3 table function and check that only first path is used"):
        if check_if_antalya_build(self):
            result = s3_steps.read_data_with_s3_table_function(
                object_storage_cluster=cluster_name,
                columns="hostName(), count()",
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
                group_by="hostName()",
            )
            with By("check that clickhouse1 is not in result since it is an observer"):
                assert "clickhouse1" not in result.output, error()
            with And("check that clickhouse2 is in result"):
                assert "clickhouse2" in result.output, error()
            with And("check that clickhouse3 is not in result"):
                assert "clickhouse3" not in result.output, error()


@TestScenario
def check_cluster_discovery_with_wrong_cluster_name(
    self, minio_root_user, minio_root_password, node=None
):
    """Check that swarm node is being registered in the cluster even though the cluster
    is not the same as in the first (observer) (current) node. Selects from s3Cluster
    and s3 table function should fail since swarm node does not know anything about
    the (correct) requested cluster name.
    """

    if node is None:
        node = self.context.node

    cluster_name = "swarm"
    path = f"/{cluster_name}_path"
    secret = "some_secret"

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create swarm cluster by adding first observer node"):
        swarm_steps.add_node_to_swarm(
            node=node,
            path=path,
            observer=True,
            cluster_name=cluster_name,
            secret=secret,
        )

    with And(
        "add first swarm node using wrong cluster name but correct path and secret"
    ):
        wrong_cluster_name = cluster_name + "_wrong"
        swarm_steps.add_node_to_swarm(
            node=self.context.node2,
            cluster_name=wrong_cluster_name,
            path=path,
            secret=secret,
        )

    with Then("check that swarm node is registered in the cluster"):
        output = swarm_steps.check_cluster_hostnames(
            cluster_name=cluster_name, node=node
        )
        assert "clickhouse2" in output, error()

    with And("define expected exit code and message"):
        if check_if_antalya_build(self) and check_clickhouse_version(">=25.6")(self):
            exitcode = 100
            message = "DB::Exception: Received from localhost:9000. DB::Exception: Unknown packet 18 from one of the following replicas"
        else:
            exitcode = 32
            message = "DB::Exception: Attempt to read after eof"

    with And(
        """check that select with s3Cluster fails since swarm node does not have 
        the correct cluster name in config"""
    ):
        result = s3_steps.read_data_with_s3Cluster_table_function(
            cluster_name=cluster_name,
            columns="hostName(), count()",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            group_by="hostName()",
            exitcode=exitcode,
            message=message,
        )

    with And(
        """check that select with s3Cluster table function and with swarm cluster fails 
        since swarm node does not have the correct cluster name in config"""
    ):
        if check_if_antalya_build(self):
            result = s3_steps.read_data_with_s3_table_function(
                object_storage_cluster=cluster_name,
                columns="hostName(), count()",
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
                group_by="hostName()",
                exitcode=exitcode,
                message=message,
            )


@TestFeature
@Name("cluster discovery")
def feature(self, minio_root_user, minio_root_password):
    """Check cluster discovery works properly."""
    Scenario(run=cluster_registration_deregistration)
    Scenario(test=multiple_discovery_sections)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=multiple_paths)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=check_cluster_discovery_with_wrong_cluster_name)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

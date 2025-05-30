from testflows.core import *
from testflows.asserts import error

from helpers.common import *
from swarms.requirements.requirements import *

import swarms.tests.steps.swarm_steps as swarm_steps
import swarms.tests.steps.s3_steps as s3_steps


@TestScenario
@Requirements(RQ_SRS_044_Swarm_ClusterDiscovery_Authentication_WrongKey("1.0"))
def wrong_key(self, minio_root_user, minio_root_password):
    """
    Check that node can't be added to the swarm cluster with wrong secret key.
    """
    cluster_name = f"swarm_{getuid()}"
    path = f"/clickhouse/discovery/{cluster_name}"
    initiator_secret = "some_secret"
    swarm_secret = "wrong_secret"

    with Given("setup Iceberg table"):
        swarm_steps.setup_iceberg_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create swarm cluster by adding first node"):
        swarm_steps.add_node_to_swarm(
            node=self.context.node,
            path=path,
            cluster_name=cluster_name,
            secret=initiator_secret,
        )

    with And("add swarm with different secret from initiator"):
        entries = {
            "remote_servers": {
                cluster_name: {"discovery": {"path": path, "secret": swarm_secret}}
            }
        }
        swarm_steps.add_node_to_swarm(
            node=self.context.node2, entries=entries, cluster_name=cluster_name
        )

    with Then("check that swarm node (clickhouse2) was not added to the cluster"):
        hostnames = swarm_steps.check_cluster_hostnames(
            cluster_name=cluster_name, node=self.context.node
        )
        assert "clickhouse2" not in hostnames, error()

    with And("select with s3Cluster and check that data was only read by clickhouse1"):
        for _ in range(10):
            result = s3_steps.read_data_with_s3Cluster_table_function(
                cluster_name=cluster_name,
                columns="hostName() AS host, count()",
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
                node=self.context.node,
            )

            assert "clickhouse2" not in result.output, error()
            assert "clickhouse1" in result.output, error()


@TestFeature
@Name("invalid configuration")
def feature(self, minio_root_user, minio_root_password):
    """
    Check that swarm nodes can't be added to the cluster with invalid configuration files.
    """
    Scenario(test=wrong_key)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

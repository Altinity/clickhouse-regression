from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, add_invalid_config, create_xml_config_content, add_config

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from swarms.requirements.requirements import *
from swarms.tests.common import setup_swarm_cluster, remove_node_from_swarm


@TestScenario
@Requirements(
    RQ_SRS_044_Swarm_NodeRegistration("1.0"), 
    RQ_SRS_044_Swarm_NodeDeregistration("1.0")
    )
def cluster_registration_deregistration(self, minio_root_user, minio_root_password):
    """Check cluster registration and deregistration properly works."""

    with Given("I check that cluster is not registered"):
        node = self.context.cluster.node("clickhouse1")
        result = node.query("SHOW clusters")
        assert "swarm" not in result.output, error()

    with Given("I add nodes to swarm cluster"):
        secret = "secret_key"
        setup_swarm_cluster(
            initiator_node="clickhouse1",
            swarm_nodes=["clickhouse2", "clickhouse3"],
            secret=secret
        )

    with Then("I check that cluster is registered"):
        for node_name in self.context.nodes:
            with By(f"checking that cluster is registered on {node_name} node"):
                node = self.context.cluster.node(node_name)
                result = node.query("SHOW clusters")
                assert "swarm" in result.output, error()

    with When("I remove nodes from swarm cluster"):
        remove_node_from_swarm(config_name="remote_swarm.xml", node_name="clickhouse1")
        remove_node_from_swarm(config_name="remote_swarm.xml", node_name="clickhouse2")
        remove_node_from_swarm(config_name="remote_swarm.xml", node_name="clickhouse3")

    with Then("I check that cluster is deregistered"):
        for node_name in self.context.nodes:
            with By(f"checking that cluster is deregistered on {node_name} node"):
                node = self.context.cluster.node(node_name)
                result = node.query("SHOW clusters")
                assert "swarm" not in result.output, error()


@TestScenario
@Requirements(RQ_SRS_044_Swarm_NodeRegistration_MultipleDiscoverySections("1.0"))
def multiple_discovery_sections(self, minio_root_user, minio_root_password):
    """Check that ClickHouse returns an error if multiple discovery sections are defined."""

    cluster_name = "swarm"
    secret = "secret_key"
    entries = {
        "allow_experimental_cluster_discovery": "1",
        "remote_servers": {
            cluster_name: [
                {
                    "discovery": {
                    "path": "/clickhouse/discovery/swarm",
                    "secret": secret
                    },
                },
                {
                    "discovery": {
                    "path": "/clickhouse/discovery/swarm",
                    "secret": secret
                    }
                }
            ]
        }
    }

    with Given("I add invalid config with multiple discovery sections"):
        for node_name in self.context.nodes:
            with By(f"adding invalid config with multiple discovery sections on {node_name} node"):
                add_invalid_config(
                    config=create_xml_config_content(root="clickhouse", entries=entries, config_file=f"remote_swarm.xml"),
                    message="Multiple discovery sections are not allowed",
                    restart=True,
                    node=self.context.cluster.node(node_name),
                    timeout=20
                )


@TestScenario
@Requirements(RQ_SRS_044_Swarm_ClusterDiscovery_MultiplePath("1.0"))
def multiple_paths(self, minio_root_user, minio_root_password):
    """Check that ClickHouse returns an error if multiple paths are defined."""

    cluster_name = "swarm"
    secret = "secret_key"
    entries = {
        "allow_experimental_cluster_discovery": "1",
        "remote_servers": {
            cluster_name: [
                {
                    "discovery": {
                    "path": "/clickhouse/discovery/swarm",
                    "path": "/clickhouse/discovery/swarm2",
                    "secret": secret
                    },
                },
            ]
        }
    }

    with Given("I add invalid config with multiple paths"):
        for node_name in self.context.nodes:
            with By(f"adding invalid config with multiple paths on {node_name} node"):
                add_invalid_config(
                    config=create_xml_config_content(root="clickhouse", entries=entries, config_file=f"remote_swarm.xml"),
                    message="Multiple paths are not allowed",
                    restart=True,
                    node=self.context.cluster.node(node_name),
                    timeout=20
                )


@TestScenario
@Requirements(RQ_SRS_044_Swarm_ClusterDiscovery_WrongPath("1.0"))
def wrong_path(self, minio_root_user, minio_root_password):
    """Check that ClickHouse returns an error if wrong path is defined."""

    cluster_name = "swarm"
    secret = "secret_key"
    entries = {
        "allow_experimental_cluster_discovery": "1",
        "remote_servers": {
            cluster_name: [
                {
                    "discovery": {
                    "path": "/../",
                    "secret": secret
                    },
                },
            ]
        }
    }

    with Given("I add invalid config with wrong path"):
        for node_name in self.context.nodes:
            with By(f"adding invalid config with wrong path on {node_name} node"):
                add_invalid_config(
                    config=create_xml_config_content(root="clickhouse", entries=entries, config_file=f"remote_swarm.xml"),
                    message="Exception: Coordination error: Bad arguments",
                    restart=True,
                    node=self.context.cluster.node(node_name),
                    timeout=20
                )


@TestFeature
@Name("cluster discovery")
def feature(self, minio_root_user, minio_root_password):
    """Check cluster discovery properly works."""

    for scenario in loads(current_module(), Scenario):
        scenario(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )

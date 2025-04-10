from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, add_config, create_xml_config_content, remove_config

import pyarrow as pa

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


def get_swarm_cluster_entries(nodes, cluster_name="swarm", secret="secret_key", observer=False):
    """Create swarm cluster configuration for given nodes.
    
    Args:
        nodes: List of node names
        secret: Secret key for authentication
        
    Returns:
        dict: Configuration entries for swarm cluster
    """
    entries = {
        "allow_experimental_cluster_discovery": "1",
        "remote_servers": {
            cluster_name: {
                "discovery": {
                    "path": "/clickhouse/discovery/swarm",
                    "secret": secret
                }
            }
        }
    }
    if observer:
        entries["remote_servers"][cluster_name]["discovery"]["observer"] = "true"

    return entries


@TestStep(Given)
def add_node_to_swarm(self, node_name, cluster_name="swarm", config_name="remote_swarm.xml", secret="secret_key", observer=False):
    """Add a node to the swarm cluster.
    
    Args:
        node_name: Name of the node to add
        cluster_name: Name of the cluster
        config_name: Name of the config file
        secret: Secret key for authentication
        observer: Whether the node is an observer
    """
    node = self.context.cluster.node(node_name)
    
    with By(f"adding swarm configuration to node {node_name}"):
        entries = get_swarm_cluster_entries(nodes=[node_name], cluster_name=cluster_name, secret=secret, observer=observer)
        return add_config(
            config=create_xml_config_content(root="clickhouse", entries=entries, config_file=config_name),
            restart=True,
            modify=True,
            node=node,
        )


@TestStep(Given)
def remove_node_from_swarm(self, node_name, cluster_name="swarm", config_name="remote_swarm.xml", secret="secret_key", observer=False, check_preprocessed=True):
    """Remove a node from the swarm cluster.
    """

    node = self.context.cluster.node(node_name)
    entries = get_swarm_cluster_entries(nodes=[node_name], cluster_name=cluster_name, secret=secret, observer=observer)

    return remove_config(
        config=create_xml_config_content(root="clickhouse", entries=entries, config_file=config_name), 
        node=node, 
        check_preprocessed=check_preprocessed,
        restart=True,
        modify=True
    )


@TestStep(Given)
def setup_swarm_cluster(self, initiator_node, swarm_nodes, secret="secret_key"):
    """Setup a swarm cluster with initiator and swarm nodes.
    
    Args:
        initiator_node: Name of the initiator node
        swarm_nodes: List of swarm node names
        secret: Secret key for authentication
    """
    with Given("I setup initiator node"):
        add_node_to_swarm(node_name=initiator_node, secret=secret, observer=True)
    configs = []
    with And("I setup swarm nodes"):
        for node in swarm_nodes:
            configs.append(add_node_to_swarm(node_name=node, secret=secret))

    return configs

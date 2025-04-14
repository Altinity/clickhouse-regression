from testflows.core import *

from helpers.common import getuid, add_config, create_xml_config_content, remove_config

import pyarrow as pa
import iceberg.tests.steps.catalog as catalog_steps


def create_swarm_cluster_entry(
    cluster_name="swarm",
    secret="secret_key",
    path="/clickhouse/discovery/swarm",
    observer=False,
    allow_experimental_cluster_discovery=True,
):
    """Create swarm cluster configuration entry.

    Args:
        cluster_name: Name of the cluster
        secret: Secret key for authentication
        observer: Whether the node is an observer
        allow_experimental_cluster_discovery: Whether to allow experimental cluster discovery

    Returns:
        dict: Configuration entries for swarm cluster
    """
    entries = {
        "remote_servers": {
            cluster_name: {"discovery": {"path": path, "secret": secret}}
        }
    }

    if allow_experimental_cluster_discovery == True:
        entries["allow_experimental_cluster_discovery"] = "1"

    if allow_experimental_cluster_discovery == False:
        entries["allow_experimental_cluster_discovery"] = "0"

    if observer:
        entries["remote_servers"][cluster_name]["discovery"]["observer"] = "true"

    return entries


@TestStep(Given)
def create_swarm_cluster(
    self,
    cluster_name="swarm",
    secret="secret_key",
    observer=False,
    allow_experimental_cluster_discovery=True,
    restart=True,
    node=None,
):
    """Add swarm cluster configuration to the server."""

    with By("creating swarm cluster configuration"):
        entries = create_swarm_cluster_entry(
            cluster_name=cluster_name,
            secret=secret,
            observer=observer,
            allow_experimental_cluster_discovery=allow_experimental_cluster_discovery,
        )

    with And("adding swarm cluster configuration to the server"):
        return change_clickhouse_config(entries=entries, restart=restart, node=node)


@TestStep(Given)
def show_clusters(self, node=None):
    """Show clusters on the server.

    Args:
        node: Node to execute the query on

    Returns:
        Result of the query
    """
    if node is None:
        node = self.context.node

    return node.query("SHOW CLUSTERS")


@TestStep(Given)
def check_cluster_hostnames(self, cluster_name, node=None):
    """Check host_name of nodes in the cluster.
    Args:
        node: Node to execute the query on
    Returns:
        Result of the `SELECT hist_name FROM system.clusters` query
    """
    if node is None:
        node = self.context.node

    return node.query(
        f"SELECT host_name FROM system.clusters WHERE cluster = '{cluster_name}'"
    ).output


@TestStep(Given)
def get_info_from_system_clusters(self, cluster_name, node=None, format="Vertical"):
    """Get information from system.clusters table.

    Args:
        cluster_name: Name of the cluster
        node: Node to execute the query on

    Returns:
        Result of the query in the specified format
    """
    if node is None:
        node = self.context.node

    return node.query(
        f"SELECT * FROM system.clusters WHERE cluster = '{cluster_name}' FORMAT {format}"
    )


@TestStep(Given)
def change_clickhouse_config(
    self,
    entries: dict,
    modify: bool = False,
    restart: bool = True,
    user: str = None,
    config_file="change_settings.xml",
    config_d_dir: str = "/etc/clickhouse-server/config.d",
    preprocessed_name: str = "config.xml",
    node: Node = None,
):
    """Change clickhouse configuration file."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(
            entries,
            config_file=config_file,
            config_d_dir=config_d_dir,
            preprocessed_name=preprocessed_name,
        )

    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user, node=node)


@TestStep(Given)
def add_node_to_swarm(
    self,
    node,
    cluster_name="swarm",
    config_name="remote_swarm.xml",
    secret="secret_key",
    observer=False,
    allow_experimental_cluster_discovery=True,
    restart=True,
    modify=False,
):
    """Add a node to the swarm cluster.

    Args:
        node_name: Name of the node to add
        cluster_name: Name of the cluster
        config_name: Name of the config file
        secret: Secret key for authentication
        observer: Whether the node is an observer
    """

    with By(f"adding swarm configuration to node {node.name}"):
        entries = create_swarm_cluster_entry(
            cluster_name=cluster_name,
            secret=secret,
            observer=observer,
            allow_experimental_cluster_discovery=allow_experimental_cluster_discovery,
        )
        change_clickhouse_config(
            entries=entries,
            config_file=config_name,
            node=node,
            restart=restart,
            modify=modify,
        )


@TestStep(Given)
def remove_node_from_swarm(
    self,
    node=None,
    cluster_name="swarm",
    config_name="remote_swarm.xml",
    secret="secret_key",
    observer=False,
    check_preprocessed=True,
):
    """Remove a node from the swarm cluster."""

    entries = create_swarm_cluster_entry(
        cluster_name=cluster_name,
        secret=secret,
        observer=observer,
    )

    config = create_xml_config_content(
        entries,
        config_file=config_name,
    )

    return remove_config(
        config=config,
        node=node,
        check_preprocessed=check_preprocessed,
        restart=True,
        modify=True,
    )


@TestStep(Given)
def setup_iceberg_table(self, minio_root_user, minio_root_password):
    """Setup an Iceberg table to select data from.
    Data is located in: http://minio:9000/warehouse/data/data/**/**.parquet

    Args:
        minio_root_user: MinIO root user
        minio_root_password: MinIO root password

    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"

    with By("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_access_key_id=minio_root_user,
            s3_endpoint="http://localhost:9002",
            s3_secret_access_key=minio_root_password,
        )

    with And(f"create namespace and create {namespace}.{table_name} table"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        table = catalog_steps.create_iceberg_table_with_three_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        df = pa.Table.from_pylist(
            [
                {"name": "Alice", "double": 195.23, "integer": 20},
                {"name": "Bob", "double": 123.45, "integer": 30},
                {"name": "Charlie", "double": 67.89, "integer": 40},
                {"name": "David", "double": 45.67, "integer": 50},
                {"name": "Eve", "double": 89.01, "integer": 60},
                {"name": "Frank", "double": 12.34, "integer": 70},
                {"name": "Grace", "double": 56.78, "integer": 80},
                {"name": "Heidi", "double": 90.12, "integer": 90},
                {"name": "Ivan", "double": 34.56, "integer": 100},
                {"name": "Judy", "double": 78.90, "integer": 110},
                {"name": "Karl", "double": 23.45, "integer": 120},
                {"name": "Leo", "double": 67.89, "integer": 130},
                {"name": "Mallory", "double": 11.12, "integer": 140},
                {"name": "Nina", "double": 34.56, "integer": 150},
            ]
        )
        table.append(df)

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(df)

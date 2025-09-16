from testflows.core import *

from helpers.common import (
    getuid,
    add_config,
    create_xml_config_content,
    remove_config,
    create_xml_config_content_with_duplicate_tags,
)

import pyarrow as pa
import iceberg.tests.steps.catalog as catalog_steps


def create_swarm_cluster_entry(
    cluster_name,
    secret="secret_key",
    path="/clickhouse/discovery/swarm",
    observer=None,
    allow_experimental_cluster_discovery=True,
):
    """Create swarm cluster configuration entry.

    Args:
        cluster_name: Name of the cluster
        secret: Secret key for authentication
        path: Path for discovery
        observer: Whether the node is an observer
        allow_experimental_cluster_discovery: Whether to allow experimental cluster discovery

    Returns:
        dict: Configuration entries for swarm cluster
    """
    discovery = {}

    if path is not None:
        discovery["path"] = path

    if secret is not None:
        discovery["secret"] = secret

    if observer == True:
        discovery["observer"] = "1"
    elif observer == False:
        discovery["observer"] = "0"

    entries = {"remote_servers": {cluster_name: {"discovery": discovery}}}

    if allow_experimental_cluster_discovery:
        entries["allow_experimental_cluster_discovery"] = "1"
    elif allow_experimental_cluster_discovery == False:
        entries["allow_experimental_cluster_discovery"] = "0"

    return entries


@TestStep(Given)
def add_node_to_swarm(
    self,
    node,
    cluster_name=None,
    config_name="remote_swarm.xml",
    secret="secret_key",
    path="/clickhouse/discovery/swarm",
    observer=False,
    allow_experimental_cluster_discovery=True,
    restart=True,
    modify=False,
    entries=None,
    duplicate_tags=False,
):
    """Add a node to the swarm cluster.

    Args:
        node: Node to add to the cluster
        cluster_name: Name of the cluster
        config_name: Name of the config file to be created on the node
        secret: Secret key for authentication
        path: Path for discovery
        observer: Whether the node is an observer
        allow_experimental_cluster_discovery: Whether to allow experimental cluster discovery
        restart: Whether to restart the node after adding the config
        modify: Whether to modify the existing config
        entries: Configuration entries to be added, if None, entries will be created based on the parameters (cluster_name, secret, path, observer, allow_experimental_cluster_discovery)
    """

    with By(f"adding swarm configuration to node {node.name}"):
        if entries is None:
            entries = create_swarm_cluster_entry(
                cluster_name=cluster_name,
                secret=secret,
                path=path,
                observer=observer,
                allow_experimental_cluster_discovery=allow_experimental_cluster_discovery,
            )

        change_clickhouse_config(
            entries=entries,
            config_file=config_name,
            node=node,
            restart=restart,
            modify=modify,
            duplicate_tags=duplicate_tags,
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
    duplicate_tags: bool = False,
):
    """
    Generate and apply a ClickHouse XML config file with the given entries.

    Args:
        entries (dict): Configuration entries to be converted into XML
        modify (bool): Whether to modify the existing config
        restart (bool): Whether to restart the node after applying the config
        user (str): ClickHouse user context for the config
        config_file (str): Name of the config file to create
        config_d_dir (str): Directory to place config in ClickHouse
        preprocessed_name (str): Preprocessed config file name
        node (Node): Target ClickHouse node
        duplicate_tags (bool): Whether to allow duplicate XML tags in config
    """
    with By("converting config file content to xml"):
        config_func = (
            create_xml_config_content_with_duplicate_tags
            if duplicate_tags
            else create_xml_config_content
        )
        config = config_func(
            entries,
            config_file=config_file,
            config_d_dir=config_d_dir,
            preprocessed_name=preprocessed_name,
        )

    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user, node=node)


@TestStep(Given)
def remove_node_from_swarm(
    self,
    cluster_name,
    node=None,
    config_name="remote_swarm.xml",
    secret="secret_key",
    path="/clickhouse/discovery/swarm",
    observer=False,
    allow_experimental_cluster_discovery=True,
    check_preprocessed=True,
):
    """Remove a node from the swarm cluster.

    Args:
        cluster_name: Name of the cluster
        node: Node to remove from the cluster
        config_name: Name of the config file to be removed from the node
        secret: Secret key for authentication
        path: Path for discovery
        observer: Whether the node is an observer
        allow_experimental_cluster_discovery: Whether experimental cluster discovery is allowed
        check_preprocessed: Whether to check the preprocessed config
    """

    entries = create_swarm_cluster_entry(
        cluster_name=cluster_name,
        secret=secret,
        path=path,
        observer=observer,
        allow_experimental_cluster_discovery=allow_experimental_cluster_discovery,
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
def show_clusters(self, node=None):
    """Show all clusters on the specified node.

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
    """Check the hostnames of nodes registered in the given cluster.

    Args:
        cluster_name: Name of the cluster
        node: Node to execute the query on

    Returns:
        Result of the `SELECT host_name FROM system.clusters` query
    """
    if node is None:
        node = self.context.node

    return node.query(
        f"SELECT host_name FROM system.clusters WHERE cluster = '{cluster_name}'"
    ).output


@TestStep(Given)
def get_cluster_info_from_system_clusters_table(
    self, cluster_name, columns="*", node=None, format="Vertical"
):
    """Get information from system.clusters table.

    Args:
        cluster_name: Name of the cluster
        columns: Columns to select from the table
        node: Node to execute the query on
        format: Format of the output

    Returns:
        Result of the `SELECT {columns} FROM system.clusters WHERE cluster = ...` query
    """
    if node is None:
        node = self.context.node

    return node.query(
        f"SELECT {columns} FROM system.clusters WHERE cluster = '{cluster_name}' FORMAT {format}"
    )


@TestStep(Given)
def setup_iceberg_table(
    self,
    minio_root_user,
    minio_root_password,
    uri="http://localhost:5000/",
    s3_endpoint="http://localhost:9002",
):
    """
    Create an Iceberg table with three columns and populate it with test data.

    The table contains 14 rows and is stored in Parquet format at:
    `s3://warehouse/data/data/**/**.parquet`

    Args:
        minio_root_user: MinIO root access key.
        minio_root_password: MinIO root secret key.
        uri: Iceberg REST catalog URI.
        s3_endpoint: S3 endpoint for MinIO access.

    Returns:
        Tuple of (Iceberg table object, table name, namespace).
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"

    with By("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_endpoint=s3_endpoint,
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

    return table, table_name, namespace

from testflows.core import *

import pyarrow as pa
import numpy as np
import random
import iceberg.tests.steps.catalog as catalog_steps

from datetime import datetime, timedelta, timezone, time, date
from decimal import Decimal

from helpers.common import (
    getuid,
    add_config,
    create_xml_config_content,
    remove_config,
    create_xml_config_content_with_duplicate_tags,
)

from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    BinaryType,
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    FixedType,
    FloatType,
    IntegerType,
    ListType,
    LongType,
    MapType,
    StringType,
    StructType,
    TimestampType,
    TimestamptzType,
    TimeType,
    UUIDType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform, HourTransform, BucketTransform

random.seed(42)


def create_swarm_cluster_entry(
    cluster_name,
    secret="secret_key",
    path="/clickhouse/discovery/swarm",
    observer=None,
    allow_experimental_cluster_discovery=True,
    user=None,
):
    """Create swarm cluster configuration entry.

    Args:
        cluster_name: Name of the cluster
        secret: Secret key for node authentication in the cluster
        path: Path for discovery
        observer: Whether the node is an observer
        allow_experimental_cluster_discovery: Whether to allow experimental cluster discovery

    Returns:
        dict: Configuration entries for swarm cluster
    """
    discovery = {}

    if path is not None:
        discovery["path"] = path

    if user is not None:
        discovery["user"] = user

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
    user=None,
):
    """Add a node to the swarm cluster.

    Args:
        node: Node to add to the cluster
        cluster_name: Name of the cluster
        config_name: Name of the config file to be created on the node
        secret: Secret key for node authentication in the cluster
        path: Path for discovery
        observer: Whether the node is an observer
        allow_experimental_cluster_discovery: Whether to allow experimental cluster discovery
        restart: Whether to restart the node after adding the config
        modify: Whether to modify the existing config
        entries: Configuration entries to be added, if None, entries will be created based on
        the parameters (cluster_name, secret, path, observer, allow_experimental_cluster_discovery)
        duplicate_tags: Whether to allow duplicate XML tags in config
    """

    with By(f"adding swarm configuration to node {node.name}"):
        if entries is None:
            entries = create_swarm_cluster_entry(
                cluster_name=cluster_name,
                secret=secret,
                path=path,
                observer=observer,
                allow_experimental_cluster_discovery=allow_experimental_cluster_discovery,
                user=user,
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
        entries: Configuration entries to be converted into XML
        modify: Whether to modify the existing config
        restart: Whether to restart the node after applying the config
        user: ClickHouse user context for the config
        config_file: Name of the config file to create
        config_d_dir: Directory to place config in ClickHouse
        preprocessed_name: Preprocessed config file name
        node: Target ClickHouse node
        duplicate_tags: Whether to allow duplicate XML tags in config
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
        secret: Secret key for node authentication in the cluster
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
    """Get information about a cluster from the system.clusters table.

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
    s3_endpoint="http://localhost:9002",
    location="s3://warehouse/data",
):
    """
    Create an Iceberg table with three columns and populate it with test data.
    Table is partitioned by name with IdentityTransform and sorted by name.
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
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            location=location,
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


@TestStep(Given)
def setup_performance_iceberg_table(
    self,
    minio_root_user,
    minio_root_password,
    row_count=100,
    batch_size=100,
    s3_endpoint="http://localhost:9002",
    location="s3://warehouse/data",
):
    """
    Create an Iceberg table with three columns and populate it with test data in batches.
    Table is partitioned by name with IdentityTransform and sorted by name.
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
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            location=location,
        )

    with And(
        f"insert {row_count} rows in batches of {batch_size} into {namespace}.{table_name} table"
    ):
        remaining_rows = row_count
        batch_num = 0

        while remaining_rows > 0:
            current_batch_size = min(batch_size, remaining_rows)
            batch_num += 1

            with By(f"inserted {batch_num*batch_size}/{row_count} rows"):
                data = []
                for _ in range(current_batch_size):
                    data.append(
                        {
                            "name": catalog_steps.random_name(),
                            "double": random.uniform(0, 100),
                            "integer": random.randint(0, 10000),
                        }
                    )
                df = pa.Table.from_pylist(data)
                table.append(df)

            remaining_rows -= current_batch_size

    with And("scan and display data"):
        df = table.scan().to_pandas()
        note(f"Total rows inserted: {len(df)}")

    return table, table_name, namespace


@TestStep(Given)
def iceberg_table_with_all_basic_data_types(
    self,
    minio_root_user,
    minio_root_password,
    s3_endpoint="http://localhost:9002",
    location="s3://warehouse/data",
):
    """
    Create an Iceberg table with all basic data types and populate it with test data.
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"

    with By("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_access_key_id=minio_root_user,
            s3_endpoint=s3_endpoint,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create table"):
        schema = Schema(
            NestedField(
                field_id=1, name="boolean_col", field_type=BooleanType(), required=False
            ),
            NestedField(
                field_id=2, name="long_col", field_type=LongType(), required=False
            ),
            NestedField(
                field_id=3, name="double_col", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=4, name="string_col", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=5,
                name="timestamp_col",
                field_type=TimestampType(),
                required=False,
            ),
            NestedField(
                field_id=6, name="date_col", field_type=DateType(), required=False
            ),
            NestedField(
                field_id=7, name="time_col", field_type=TimeType(), required=False
            ),
            NestedField(
                field_id=8,
                name="timestamptz_col",
                field_type=TimestamptzType(),
                required=False,
            ),
            NestedField(
                field_id=9, name="integer_col", field_type=IntegerType(), required=False
            ),
            NestedField(
                field_id=10, name="float_col", field_type=FloatType(), required=False
            ),
            NestedField(
                field_id=11,
                name="decimal_col",
                field_type=DecimalType(10, 2),
                required=False,
            ),
        )
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location=location,
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("insert data into table"):
        data = pa.table(
            {
                "boolean_col": pa.array([True, False]),
                "long_col": pa.array([1000, 2000], type=pa.int64()),
                "double_col": pa.array([456.78, 456.78], type=pa.float64()),
                "string_col": pa.array(["Alice", "Bob"], type=pa.string()),
                "timestamp_col": pa.array(
                    [datetime(2024, 1, 1, 12, 0, 0), datetime(2024, 1, 1, 12, 0, 0)],
                    type=pa.timestamp("us"),
                ),
                "date_col": pa.array(
                    [date(2024, 1, 1), date(2024, 1, 1)], type=pa.date32()
                ),
                "time_col": pa.array(
                    [time(12, 0, 0), time(12, 0, 0)], type=pa.time64("us")
                ),
                "timestamptz_col": pa.array(
                    [
                        datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                        datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                    ],
                    type=pa.timestamp("us", tz="UTC"),
                ),
                "integer_col": pa.array([1000, 2000], type=pa.int32()),
                "float_col": pa.array([456.78, 456.78], type=pa.float32()),
                "decimal_col": pa.array(
                    [Decimal("456.78"), Decimal("456.78")], type=pa.decimal128(10, 2)
                ),
            }
        )
        table.append(data)
        table.append(data)
        table.append(data)
        table.append(data)

    return table, table_name, namespace

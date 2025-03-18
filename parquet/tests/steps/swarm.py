import time
from datetime import datetime, timedelta

import pyarrow as pa
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.schema import Schema
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import DayTransform
from pyiceberg.transforms import IdentityTransform
from pyiceberg.types import (
    TimestampType,
    DoubleType,
    StringType,
    NestedField,
)
from testflows.core import *

from iceberg.tests.steps.catalog import (
    create_catalog,
    create_namespace,
    create_iceberg_table,
)
from parquet.tests.common import getuid
from parquet.tests.steps.metadata_caching import (
    select_parquet_metadata_from_s3,
    create_multiple_parquet_files_with_common_datatypes,
    create_parquet_files_in_different_paths,
)

PATH1 = "location_1"
PATH2 = "location_2"


def generate_data(num_partitions):
    """Generate data for the parquet file with partitions."""

    data = []
    base_date = datetime(2019, 8, 7, 8, 35, 0)
    tt = pa.timestamp("us")

    for i in range(num_partitions):
        date = base_date + timedelta(
            days=i * 2
        )  # Increment date by 2 days for each partition
        data.append(
            {
                "datetime": pa.scalar(date, tt),
                "symbol": "AAPL",
                "bid": 195.23 + i,
                "ask": 195.28 + i,
            }
        )
        data.append(
            {
                "datetime": pa.scalar(date, tt),
                "symbol": "AAPL",
                "bid": 195.22 + i,
                "ask": 195.28 + i,
            }
        )
    return data


@TestStep(Given)
def connect_to_catalog_minio(self, catalog_type=None):  # 1
    """Connect to the catalog."""

    if catalog_type is None:
        catalog_type = "rest"

    catalog = create_catalog(
        uri="http://localhost:8182/",
        catalog_type=catalog_type,
        s3_access_key_id=self.context.access_key_id,
        s3_secret_access_key=self.context.secret_access_key,
        s3_endpoint="http://localhost:9002",
    )

    return catalog


@TestStep(Given)
def create_iceberg_namespace(self, catalog, namespace=None):  # 2
    """Create namespace iceberg."""

    if namespace is None:
        namespace = "iceberg"

    create_namespace(catalog=catalog, namespace=namespace)

    note(catalog.list_namespaces())


def to_dt(string):
    """Convert a string to a datetime object."""
    format = "%Y-%m-%d %H:%M:%S"
    dt = datetime.strptime(string, format)
    return dt


@TestStep(Given)
def setup_iceberg(self, catalog_type=None, namespace=None):
    """Setup Iceberg for parquet testing."""
    catalog = connect_to_catalog_minio(catalog_type=catalog_type)

    create_iceberg_namespace(catalog=catalog, namespace=namespace)

    return catalog


@TestStep(Given)
def create_parquet_partitioned_by_datetime(  # 3
    self, catalog, location=None, number_of_partitions=1000
):
    """Create a partitioned table."""
    table_name = "table_" + getuid()

    if location is None:
        location = "s3://warehouse/data"

    with By("setting a schema for a parquet file"):
        schema = Schema(
            NestedField(
                field_id=1, name="datetime", field_type=TimestampType(), required=False
            ),
            NestedField(
                field_id=2, name="symbol", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=3, name="bid", field_type=DoubleType(), required=False
            ),
            NestedField(
                field_id=4, name="ask", field_type=DoubleType(), required=False
            ),
        )
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1000,
                transform=DayTransform(),
                name="datetime_day",
            )
        )
        sort_order = SortOrder(SortField(source_id=2, transform=IdentityTransform()))

    with And(f"creating the '{table_name}' table in the iceberg catalog"):
        table = create_iceberg_table(
            catalog=catalog,
            namespace="iceberg",
            table_name=table_name,
            schema=schema,
            location=location,
            partition_spec=partition_spec,
            sort_order=sort_order,
        )

    with And(f"generating data for the table to get {number_of_partitions} partitions"):
        data = generate_data(number_of_partitions)
        df = pa.Table.from_pylist(data)
        table.append(df)


@TestStep(When)
def copy_user_config_with_disabled_caching(self, node=None):
    """Copy /other_user_configs.xml to /etc/clickhouse-server/users.xml on node clickhouse-antalya."""

    if node is None:
        node = self.context.cluster.node("clickhouse-antalya")

    node.command("cp /other_user_configs.xml /etc/clickhouse-server/users.xml")


@TestStep(When)
def stop_initiator_node(self):
    """Stop clickhouse-antalya node."""
    node = self.context.cluster.node("clickhouse-antalya")
    node.stop_clickhouse(safe=False)


@TestStep(When)
def disable_caching_on_swarm_1_in_user_settings(self):
    """Disable caching on clickhouse-swarm-1 nodes."""

    copy_user_config_with_disabled_caching(node=self.context.swarm_nodes[0])


@TestStep(When)
def disable_caching_on_swarm_2_in_user_settings(self):
    """Disable caching on clickhouse-swarm-2 nodes."""

    copy_user_config_with_disabled_caching(node=self.context.swarm_nodes[1])


@TestStep(When)
def restart_initiator_antalya_node(self):
    """Restart clickhouse-antalya node."""
    node = self.context.cluster.node("clickhouse-antalya")
    node.restart_clickhouse()


@TestStep(When)
def restart_swarm_1_node(self):
    """Restart clickhouse-swarm-1 node."""
    node = self.context.swarm_nodes[0]
    node.restart_clickhouse()


@TestStep(When)
def restart_swarm_2_node(self):
    """Restart clickhouse-swarm-2 node."""
    node = self.context.swarm_nodes[1]
    node.restart_clickhouse()


@TestStep(When)
def apply_user_config_with_disabled_caching_on_antalya(self):
    """Apply user config with disabled caching on clickhouse-antalya."""

    with By("copying user config with disabled caching"):
        copy_user_config_with_disabled_caching()

    with And("restarting clickhouse-antalya"):
        restart_initiator_antalya_node()


@TestStep(When)
def apply_user_config_with_disabled_caching_on_swarm_1(self):
    """Apply user config with disabled caching on clickhouse-swarm-1."""

    with By("copying user config with disabled caching"):
        disable_caching_on_swarm_1_in_user_settings()

    with And("restarting clickhouse-swarm-1"):
        restart_swarm_1_node()


@TestStep(When)
def apply_user_config_with_disabled_caching_on_swarm_2(self):
    """Apply user config with disabled caching on clickhouse-swarm-2."""

    with By("copying user config with disabled caching"):
        disable_caching_on_swarm_2_in_user_settings()

    with And("restarting clickhouse-swarm-2"):
        restart_swarm_2_node()


@TestStep(Given)
def add_one_swarm_node(self):
    """Add one node to the swarm cluster."""
    pass  # FIXME


@TestStep(Given)
def add_two_swarm_nodes(self):
    """Add two nodes to the swarm cluster."""
    pass  # FIXME


@TestStep(When)
def stop_swarm_1_node(self):
    """Stop clickhouse on node clickhouse-swarm-1"""

    node = self.context.swarm_nodes[0]
    node.stop_clickhouse(safe=False)


@TestStep(When)
def start_swarm_1_node(self):
    """Start clickhouse on node clickhouse-swarm-1"""

    node = self.context.swarm_nodes[0]
    node.start_clickhouse()


@TestStep(Given)
def select_parquet_from_swarm_s3(
    self,
    node=None,
    statement="*",
    additional_settings=None,
    condition=None,
    cache_metadata=False,
    file_type="Parquet",
    path_glob="**",
    retrieve_query=False,
):
    """Select metadata of the Parquet file from Swarm on S3."""

    log_comment = "log_" + getuid()
    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1, object_storage_cluster='swarm', filesystem_cache_name = 'cache_for_s3', enable_filesystem_cache = 1"

    if node is None:
        node = self.context.node

    if cache_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    if additional_settings is not None:
        settings += f", {additional_settings}"

    if condition is None:
        condition = ""

    start_time = time.time()
    r = node.query(
        f"""SELECT {statement} FROM s3('{self.context.warehouse_uri}/{path_glob}/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) {condition} SETTINGS {settings} FORMAT TabSeparated"""
    )
    execution_time = time.time() - start_time

    if not retrieve_query:
        return execution_time, log_comment
    else:
        return execution_time, log_comment, r


@TestStep(Given)
def select_parquet_from_swarm_s3_cluster_join(
    self,
    node=None,
    statement="*",
    additional_settings=None,
    condition=None,
    cache_metadata=False,
    file_type="Parquet",
    path_glob="**",
):
    """Select metadata of the Parquet file from Iceberg on S3."""

    log_comment = "log_" + getuid()
    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1, object_storage_cluster='swarm', filesystem_cache_name = 'cache_for_s3', enable_filesystem_cache = 1"

    if node is None:
        node = self.context.node

    if cache_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    if additional_settings is not None:
        settings += f", {additional_settings}"

    if condition is None:
        condition = ""

    start_time = time.time()
    node.query(
        f"""SELECT *, a.*, b.* FROM s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/datetime_day=2019-08-09/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) AS a FULL OUTER JOIN s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/datetime_day=2019-08-07/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) AS b ON a.bid = b.bid SETTINGS {settings} FORMAT TabSeparated
"""
    )

    execution_time = time.time() - start_time

    return execution_time, log_comment


@TestStep(Given)
def select_parquet_from_swarm_s3_cluster(
    self,
    node=None,
    statement="*",
    additional_settings=None,
    condition=None,
    cache_metadata=False,
    file_type="Parquet",
    path_glob="**",
):
    """Select metadata of the Parquet file from Iceberg on s3Cluster."""

    log_comment = "log_" + getuid()
    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1, filesystem_cache_name = 'cache_for_s3', enable_filesystem_cache = 1"

    if node is None:
        node = self.context.node

    if cache_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    if additional_settings is not None:
        settings += f", {additional_settings}"

    if condition is None:
        condition = ""

    start_time = time.time()
    node.query(
        f"""SELECT {statement} FROM s3Cluster('swarm' ,'{self.context.warehouse_uri}/{path_glob}/**.parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', {file_type}) {condition} SETTINGS {settings} FORMAT TabSeparated"""
    )
    execution_time = time.time() - start_time

    return execution_time, log_comment


@TestStep(Given)
def create_parquet_in_different_locations(self):
    """Create Parquet files in different locations."""

    return create_parquet_files_in_different_paths(path1=PATH1, path2=PATH2)


@TestStep(Given)
def create_parquet_in_different_locations_on_cluster(self):
    """Create Parquet files in different locations on a cluster."""

    return create_parquet_files_in_different_paths(
        path1=PATH1, path2=PATH2, cluster=self.context.cluster_name
    )


@TestStep(Given)
def create_multiple_parquet_files_with_common_datatypes_on_cluster(self):
    """Create multiple Parquet files with common data types on a cluster."""
    create_multiple_parquet_files_with_common_datatypes(
        cluster=self.context.cluster_name
    )


@TestStep(When)
def select_without_cache(self, file_name, statement="*"):
    """Select metadata of the Parquet file without caching the metadata."""
    parquet, without_cache = select_parquet_metadata_from_s3(
        file_name=file_name, statement=statement
    )

    return parquet, without_cache


@TestStep(When)
def select_with_cache(self, file_name, statement="*", log_comment=None):
    """Select metadata of the Parquet file with caching the metadata."""
    parquet, with_cache = select_parquet_metadata_from_s3(
        file_name=file_name, caching=True, statement=statement, log_comment=log_comment
    )

    return parquet, with_cache


@TestStep(When)
def read_from_s3_and_expect_query_fail(self, node=None):
    """Read from S3 and expect the query to fail."""

    if node is None:
        node = self.context.swarm_initiator

    time, log, q = select_parquet_from_swarm_s3(
        node=node, statement="COUNT(*), sleep(3)", cache_metadata=True
    )
    assert q.exitcode != 0

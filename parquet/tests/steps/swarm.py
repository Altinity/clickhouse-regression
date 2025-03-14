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


def generate_data(num_partitions):

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

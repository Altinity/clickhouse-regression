from testflows.core import *
from testflows.asserts import error
from clickhouse_driver import Client
import boto3
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table
from pyiceberg.schema import Schema
from pyiceberg.types import (
    IntegerType,
    StringType,
    NestedField,
    LongType,
    TimestampType,
)
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.transforms import DayTransform, IdentityTransform

from minio import Minio


# S3 Configuration
S3_BUCKET = "mybucket"
CATALOG_NAME = "s3_catalog"
TABLE_NAME = "my_table"
ENDPOINT_URL = "http://localhost:8182"


@TestScenario
def sanity(self):
    # Define schema for the Iceberg table
    uri = "localhost:9001"
    access_key = "minio"
    secret_key = "minio123"
    minio_client = Minio(
        uri, access_key=access_key, secret_key=secret_key, secure=False
    )

    if not minio_client.bucket_exists(S3_BUCKET):
        minio_client.make_bucket(S3_BUCKET)

    schema = Schema(
        NestedField(field_id=1, name="time", field_type=TimestampType(), required=False),
    )

    # Load the S3 catalog
    catalog = load_catalog(
        name=CATALOG_NAME,
        **{
            "type": "rest",
            "uri": f"{ENDPOINT_URL}",
            "warehouse": f"s3://{S3_BUCKET}/",
            "aws.access-key-id": "minio",
            "aws.secret-access-key": "minio123",
            "aws.region": "us-east-1",
        },
    )

    namespace = "namespace1"
    if namespace not in catalog.list_namespaces():
        catalog.create_namespace(namespace)

    DEFAULT_PARTITION_SPEC = PartitionSpec(
        PartitionField(
            source_id=1, field_id=1000, transform=DayTransform(), name="datetime_day"
        )
    )
    
    pause()
    
    # Create the table
    try:
        table = catalog.create_table(
            identifier=f"{namespace}.{TABLE_NAME}",
            schema=schema,
            partition_spec=DEFAULT_PARTITION_SPEC,  # Define partitions if needed
            properties={
                "format-version": "2",  # Iceberg format version
            },
        )
    except Exception as e:
        note(f"Error creating table: {e}")
        raise


@TestFeature
def feature(self, servers=None, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

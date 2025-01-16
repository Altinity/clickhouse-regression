from testflows.core import *
from testflows.asserts import error
from clickhouse_driver import Client
import boto3
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table
from pyiceberg.schema import Schema
from pyiceberg.types import (
    IntegerType,
    NestedField,
)
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.transforms import DayTransform, IdentityTransform

from minio import Minio

import requests
import urllib3

from helpers.common import getuid


# S3 Configuration
S3_BUCKET = "my-bucket"
CATALOG_NAME = "s3_catalog"
TABLE_NAME = "my_table"

BASE_URL = "http://rest:8181/v1"
BASE_URL_LOCAL = "http://localhost:8182/v1"
BASE_URL_LOCAL_RAW = "http://localhost:8182"


def list_namespaces():
    response = requests.get(f"{BASE_URL_LOCAL}/namespaces")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to list namespaces: {response.status_code}")


@TestScenario
def sanity(self):
    minio_client = Minio(
        f"localhost:9001",
        access_key="minio",
        secret_key="minio123",
        secure=False,
        http_client=urllib3.PoolManager(cert_reqs="CERT_NONE"),
    )

    if not minio_client.bucket_exists(S3_BUCKET):
        minio_client.make_bucket(S3_BUCKET)

    schema = Schema(
        NestedField(
            field_id=1, name="num", field_type=IntegerType(), required=False
        ),
    )

    catalog = load_catalog(
        "nessie",
        **{
            "uri": "http://localhost:19120/iceberg/main/",
        },
    )
    catalog.create_namespace("demo")
    
    catalog.create_table("demo.sample_table", schema)

    table = catalog.load_table("demo.sample_table")

    # Get the table schema
    schema = table.schema()
    note(f"Table Schema: {schema}")

    # Get the table properties
    properties = table.properties
    note(f"Table Properties: {properties}")
   


@TestFeature
def feature(self, servers=None, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

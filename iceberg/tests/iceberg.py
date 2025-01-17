from testflows.core import *
from testflows.asserts import error

from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table
from pyiceberg.schema import Schema
from pyiceberg.types import (
    IntegerType,
    NestedField,
    LongType,
    StringType,
)
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.transforms import DayTransform, IdentityTransform

from minio import Minio

import requests
import urllib3
import pyarrow as pa
import pandas as pd

from helpers.common import getuid


S3_BUCKET = "my-bucket"
CATALOG_NAME = "nessie"

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
    with Given("create minio client"):
        minio_client = Minio(
            f"localhost:9001",
            access_key="minio",
            secret_key="minio123",
            secure=False,
            http_client=urllib3.PoolManager(cert_reqs="CERT_NONE"),
        )

    with And("create bucket"):
        if not minio_client.bucket_exists(S3_BUCKET):
            minio_client.make_bucket(S3_BUCKET)

    with When("create catalog"):
        catalog = load_catalog(
            CATALOG_NAME,
            **{
                "uri": "http://localhost:19120/iceberg/main/",
            },
        )

    with And("create namespace"):
        catalog.create_namespace("demo")

    with And("define schema and create table"):
        schema = Schema(
            NestedField(1, "id", LongType(), required=True),
            NestedField(2, "name", StringType(), required=False),
        )

        catalog.create_table("demo.sample_table", schema)

    with And("print table info"):
        table = catalog.load_table("demo.sample_table")
        note(f"Table Schema: {table.schema()}")
        note(f"Table Properties: {table.properties}")
        note(f"Table Location: {table.location()}")

    with And("insert rows into table"):
        data = pa.Table.from_pydict(
            {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]}
        )

        table = catalog.load_table("demo.sample_table")
        table.append(data)

    with And("print table content"):
        result = table.scan().to_arrow()
        note(result)


@TestFeature
def feature(self, servers=None, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)

    Scenario(run=sanity)

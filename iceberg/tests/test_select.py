from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

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

import boto3
import requests
import urllib3
import pyarrow as pa

S3_BUCKET = "warehouse"

BASE_URL = "http://rest:8181/v1"
BASE_URL_LOCAL = "http://localhost:8182/v1"
BASE_URL_LOCAL_RAW = "http://localhost:8182"

CATALOG_NAME = "demo"


def load_catalog_impl():
    return load_catalog(
        CATALOG_NAME,
        **{
            "uri": BASE_URL_LOCAL_RAW,
            "type": "rest",
            "s3.endpoint": f"http://localhost:9002",
            "s3.access-key-id": "minio",
            "s3.secret-access-key": "minio123",
        },
    )


def create_table(
    catalog,
    namespace,
    table,
):
    schema = Schema(
        NestedField(field_id=1, name="num", field_type=IntegerType(), required=False),
    )
    return catalog.create_table(
        identifier=f"{namespace}.{table}",
        schema=schema,
        #location=f"s3://warehouse",
    )


def generate_record():
    return {
        "num": 1,
    }


def list_namespaces():
    response = requests.get(f"{BASE_URL_LOCAL}/namespaces")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to list namespaces: {response.status_code}")


def create_clickhouse_iceberg_database(started_cluster, node, name):
    node.query(
        f"""
        DROP DATABASE IF EXISTS {name};
        SET allow_experimental_database_iceberg=true;
        CREATE DATABASE {name} ENGINE = Iceberg('{BASE_URL}', 'minio', 'minio123')
        SETTINGS catalog_type = 'rest',
                storage_endpoint = 'http://minio:9000/warehouse',
                warehouse='demo'
    """
    )


def print_objects():
    minio_client = Minio(
        f"localhost:9001",
        access_key="minio",
        secret_key="minio123",
        secure=False,
        http_client=urllib3.PoolManager(cert_reqs="CERT_NONE"),
    )

    objects = list(minio_client.list_objects("warehouse", "", recursive=True))
    names = [x.object_name for x in objects]
    names.sort()
    for name in names:
        print(f"Found object: {name}")


@TestScenario
def test_select(self):
    node = self.context.node

    test_ref = f"test_list_tables_{getuid()}"
    table_name = f"{test_ref}_table"
    root_namespace = f"{test_ref}_namespace"

    namespace = f"{root_namespace}.A.B.C"
    namespaces_to_create = [
        root_namespace,
        f"{root_namespace}.A",
        f"{root_namespace}.A.B",
        f"{root_namespace}.A.B.C",
    ]

    catalog = load_catalog_impl()
    

    for namespace in namespaces_to_create:
        catalog.create_namespace(namespace)
        assert len(catalog.list_tables(namespace)) == 0

    minio_client = Minio(
        "localhost:9001", access_key="minio", secret_key="minio123", secure=False
    )
    
    bucket_name = "warehouse"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    buckets = minio_client.list_buckets()
    for bucket in buckets:
        note(f"Bucket name: {bucket.name}")

    table = create_table(catalog, namespace, table_name)

    num_rows = 10
    data = [generate_record() for _ in range(num_rows)]
    df = pa.Table.from_pylist(data)
    table.append(df)

    create_clickhouse_iceberg_database(node, CATALOG_NAME)

    node.query(f"SHOW CREATE TABLE {CATALOG_NAME}.`{namespace}.{table_name}`")

    node.query(f"SELECT count() FROM {CATALOG_NAME}.`{namespace}.{table_name}`")


@TestFeature
def feature(self, servers=None, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)

    Scenario(run=test_select)

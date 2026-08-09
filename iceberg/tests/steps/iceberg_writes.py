import inspect

import boto3

from testflows.core import *
from testflows.asserts import error

from pyiceberg.schema import Schema
from pyiceberg.types import LongType, StringType, NestedField
from pyiceberg.partitioning import PartitionSpec
from pyiceberg.table.sorting import SortOrder

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine


MOR_TABLE_PROPERTIES = {
    "write.update.mode": "merge-on-read",
    "write.delete.mode": "merge-on-read",
    "write.merge.mode": "merge-on-read",
}

ICEBERG_INSERT_SETTINGS = [("allow_experimental_insert_into_iceberg", 1)]
ICEBERG_MUTATION_SETTINGS = [
    ("allow_insert_into_iceberg", 1),
    ("allow_experimental_insert_into_iceberg", 1),
]
ICEBERG_COMPACTION_SETTINGS = [("allow_experimental_iceberg_compaction", 1)]

HOST_MINIO_ENDPOINT = "http://localhost:9002"
WAREHOUSE_BUCKET = "warehouse"


def mor_id_data_schema():
    """Schema for compact delete/compaction smoke tests."""
    return Schema(
        NestedField(field_id=1, name="id", field_type=LongType(), required=False),
        NestedField(field_id=2, name="data", field_type=StringType(), required=False),
    )


def catalog_table_sql_name(database_name, namespace, table_name):
    """Fully-qualified DataLakeCatalog table name with escaped dots."""
    return f"{database_name}.\\`{namespace}.{table_name}\\`"


def table_s3_location(namespace, table_name):
    """Unique S3 table root under the warehouse bucket."""
    return f"s3://{WAREHOUSE_BUCKET}/data/{namespace}/{table_name}"


def table_engine_url(namespace, table_name):
    """ClickHouse-reachable HTTP URL for the same table root."""
    return f"http://minio:9000/{WAREHOUSE_BUCKET}/data/{namespace}/{table_name}"


def table_prefix(namespace, table_name):
    """Bucket-relative prefix for listing metadata files."""
    return f"data/{namespace}/{table_name}"


def latest_metadata_location(
    minio_root_user,
    minio_root_password,
    namespace,
    table_name,
    bucket=WAREHOUSE_BUCKET,
    endpoint_url=HOST_MINIO_ENDPOINT,
):
    """Return ``s3://...`` URI of the newest ``*.metadata.json`` for the table."""
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=minio_root_user,
        aws_secret_access_key=minio_root_password,
    )
    prefix = f"{table_prefix(namespace, table_name)}/metadata/"
    candidates = []
    for page in s3.get_paginator("list_objects_v2").paginate(
        Bucket=bucket, Prefix=prefix
    ):
        for obj in page.get("Contents", []) or []:
            if obj["Key"].endswith(".metadata.json"):
                candidates.append(obj)

    assert candidates, error(f"No *.metadata.json under s3://{bucket}/{prefix}")
    candidates.sort(key=lambda o: (o["LastModified"], o["Key"]), reverse=True)
    return f"s3://{bucket}/{candidates[0]['Key']}"


@TestStep(Given)
def setup_iceberg_engine_mor_table(
    self,
    minio_root_user,
    minio_root_password,
    namespace=None,
    table_name=None,
    ch_table_name=None,
    location=None,
    warehouse_url=None,
):
    """Create a merge-on-read PyIceberg table and a matching ENGINE=Iceberg table."""
    if namespace is None:
        namespace = f"iceberg_{getuid()}"
    if table_name is None:
        table_name = f"table_{getuid()}"
    if ch_table_name is None:
        ch_table_name = table_name
    if location is None:
        location = table_s3_location(namespace, table_name)
    if warehouse_url is None:
        warehouse_url = table_engine_url(namespace, table_name)

    with By("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint=HOST_MINIO_ENDPOINT,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"create merge-on-read table {namespace}.{table_name}"):
        iceberg_table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=mor_id_data_schema(),
            location=location,
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
            table_properties=MOR_TABLE_PROPERTIES,
        )

    with And("create ClickHouse table with Iceberg engine"):
        iceberg_table_engine.create_table_with_iceberg_engine(
            table_name=ch_table_name,
            url=warehouse_url,
            access_key_id=minio_root_user,
            secret_access_key=minio_root_password,
        )

    return iceberg_table, ch_table_name, namespace, table_name


@TestStep(When)
def insert_into_iceberg_engine_table(
    self,
    table_name,
    insert_query,
    node=None,
    settings=None,
):
    """Insert rows into an ENGINE=Iceberg table."""
    if node is None:
        node = self.context.node
    if settings is None:
        settings = ICEBERG_INSERT_SETTINGS

    node.query(insert_query, settings=settings)


@TestStep(When)
def delete_from_iceberg_engine_table(self, table_name, condition, node=None):
    """Issue ALTER DELETE against an ENGINE=Iceberg table (position deletes)."""
    if node is None:
        node = self.context.node

    node.query(
        f"ALTER TABLE {table_name} DELETE WHERE {condition}",
        settings=ICEBERG_MUTATION_SETTINGS,
    )


@TestStep(When)
def sync_catalog_to_latest_metadata(
    self,
    catalog,
    namespace,
    table_name,
    minio_root_user,
    minio_root_password,
):
    """Point the catalog at metadata written by path-based ENGINE=Iceberg.

    Catalog ``ALTER DELETE`` currently fails with ``Metadata is not initialized``
    because ``mutate()`` does not lazy-init metadata (unlike ``write()``). Path-based
    ENGINE=Iceberg writes succeed but do not update the catalog pointer, so readers
    through DataLakeCatalog need this re-register step.
    """
    metadata_location = latest_metadata_location(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        namespace=namespace,
        table_name=table_name,
    )
    identifier = f"{namespace}.{table_name}"
    # REST accepts purge_requested; Glue/Hive/etc. only take the identifier.
    drop_params = inspect.signature(catalog.drop_table).parameters
    if "purge_requested" in drop_params:
        catalog.drop_table(identifier, purge_requested=False)
    else:
        catalog.drop_table(identifier)
    catalog.register_table(identifier, metadata_location)
    return metadata_location


@TestStep(When)
def optimize_iceberg_engine_table(self, table_name, node=None):
    """Compact an ENGINE=Iceberg table."""
    if node is None:
        node = self.context.node

    node.query(
        f"OPTIMIZE TABLE {table_name}",
        settings=ICEBERG_COMPACTION_SETTINGS,
    )


@TestStep(Then)
def assert_table_count(self, table_name, expected_count, node=None):
    """Assert SELECT count() for a table."""
    if node is None:
        node = self.context.node

    result = node.query(f"SELECT count() FROM {table_name}")
    assert int(result.output.strip()) == expected_count, error()


@TestStep(Then)
def assert_table_ids(self, table_name, expected_ids, node=None):
    """Assert ordered id column matches expected values."""
    if node is None:
        node = self.context.node

    result = node.query(f"SELECT id FROM {table_name} ORDER BY id")
    actual_ids = [int(line) for line in result.output.strip().splitlines() if line]
    assert actual_ids == list(expected_ids), error()

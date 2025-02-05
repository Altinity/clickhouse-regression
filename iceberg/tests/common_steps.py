from testflows.core import *

import pyiceberg
from pyiceberg.catalog import load_catalog

from pyiceberg.schema import Schema
from pyiceberg.types import (
    DoubleType,
    StringType,
    NestedField,
    LongType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

S3_ACCESS_KEY_ID = "minio"
S3_SECRET_ACCESS_KEY = "minio123"
CATALOG_TYPE = "rest"


@TestStep(Given)
def create_catalog(
    self,
    uri,
    name="rest_catalog",
    s3_endpoint="http://localhost:9002",
    s3_access_key_id=S3_ACCESS_KEY_ID,
    s3_secret_access_key=S3_SECRET_ACCESS_KEY,
    catalog_type=CATALOG_TYPE,
):
    catalog = load_catalog(
        name,
        **{
            "uri": uri,
            "type": catalog_type,
            "s3.endpoint": s3_endpoint,
            "s3.access-key-id": s3_access_key_id,
            "s3.secret-access-key": s3_secret_access_key,
        },
    )

    return catalog


@TestStep(Given)
def create_namespace(self, catalog, namespace):
    try:
        catalog.create_namespace(namespace)
    except pyiceberg.exceptions.NamespaceAlreadyExistsError:
        note("Namespace already exists")
    except Exception as e:
        note(f"An unexpected error occurred: {e}")
        raise


@TestStep(Given)
def drop_iceberg_table(self, catalog, namespace, table_name):
    table_list = catalog.list_tables(namespace)
    for table in table_list:
        if table[0] == namespace and table[1] == table_name:
            note("Dropping table")
            catalog.drop_table(f"{namespace}.{table_name}")


@TestStep(Given)
def create_iceberg_table(
    self,
    catalog,
    namespace,
    table_name,
    schema,
    location,
    partition_spec,
    sort_order=None,
):
    try:
        table = catalog.create_table(
            identifier=f"{namespace}.{table_name}",
            schema=schema,
            location=location,
            sort_order=sort_order,
            partition_spec=partition_spec,
        )
        yield table
    finally:
        with Finally("drop table"):
            drop_iceberg_table(catalog=catalog, namespace=namespace, table_name=table_name)


@TestStep(Given)
def create_iceberg_table_with_three_columns(self, catalog, namespace, table_name):
    """Define schema, partition spec, sort order and create iceberg table with three columns."""
    schema = Schema(
        NestedField(field_id=1, name="name", field_type=StringType(), required=False),
        NestedField(field_id=2, name="double", field_type=DoubleType(), required=False),
        NestedField(field_id=3, name="integer", field_type=LongType(), required=False),
    )
    partition_spec = PartitionSpec(
        PartitionField(
            source_id=1,
            field_id=1001,
            transform=IdentityTransform(),
            name="symbol_partition",
        ),
    )
    sort_order = SortOrder(SortField(source_id=1, transform=IdentityTransform()))
    table = create_iceberg_table(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        schema=schema,
        location="s3://warehouse/data",
        partition_spec=partition_spec,
        sort_order=sort_order,
    )
    return table

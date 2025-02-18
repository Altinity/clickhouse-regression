from testflows.core import *

import pyiceberg
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    DoubleType,
    StringType,
    NestedField,
    LongType,
    BooleanType,
    IntegerType,
    FloatType,
    DecimalType,
    UUIDType,
    FixedType,
    BinaryType,
    DateType,
    TimeType,
    TimestampType,
    TimestamptzType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

import boto3

CATALOG_TYPE = "rest"


@TestStep(Given)
def create_catalog(
    self,
    uri,
    s3_access_key_id,
    s3_secret_access_key,
    name="rest_catalog",
    s3_endpoint="http://localhost:9002",
    catalog_type=CATALOG_TYPE,
):
    try:
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
        yield catalog

    finally:
        with Finally("drop catalog"):
            clean_minio_bucket(
                bucket_name="warehouse",
                s3_endpoint=s3_endpoint,
                s3_access_key_id=s3_access_key_id,
                s3_secret_access_key=s3_secret_access_key,
            )


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
    try:
        table_list = catalog.list_tables(namespace)
    except pyiceberg.exceptions.NoSuchNamespaceException:
        note("No such namespace")
        table_list = []

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
    format_version="2",
):
    try:
        table = catalog.create_table(
            identifier=f"{namespace}.{table_name}",
            schema=schema,
            location=location,
            sort_order=sort_order,
            partition_spec=partition_spec,
            properties={"format-version": format_version},
        )
        yield table
    finally:
        with Finally("drop table"):
            drop_iceberg_table(
                catalog=catalog, namespace=namespace, table_name=table_name
            )


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


@TestStep(Given)
def create_iceberg_table_with_five_columns(self, catalog, namespace, table_name):
    """Define schema, partition spec, sort order and create iceberg table with three columns."""
    schema = Schema(
        NestedField(
            field_id=1, name="boolean_col", field_type=BooleanType(), required=False
        ),
        NestedField(field_id=2, name="long_col", field_type=LongType(), required=False),
        NestedField(
            field_id=3, name="double_col", field_type=DoubleType(), required=False
        ),
        NestedField(
            field_id=4, name="string_col", field_type=StringType(), required=False
        ),
        NestedField(field_id=5, name="date_col", field_type=DateType(), required=False),
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


@TestStep(When)
def clean_minio_bucket(
    self, bucket_name, s3_endpoint, s3_access_key_id, s3_secret_access_key
):
    """Delete all objects from the MinIO bucket."""
    s3_client = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
    )

    # List all objects in the bucket
    objects = s3_client.list_objects_v2(Bucket=bucket_name)

    if "Contents" in objects:
        delete_objects = {
            "Objects": [{"Key": obj["Key"]} for obj in objects["Contents"]]
        }
        s3_client.delete_objects(Bucket=bucket_name, Delete=delete_objects)
        note(f"Deleted {len(delete_objects['Objects'])} objects from {bucket_name}")

    else:
        note(f"No objects found in {bucket_name}")


@TestStep(Given)
def drop_namespace(self, catalog, namespace):
    """Drop namespace in Iceberg catalog."""
    try:
        catalog.drop_namespace(namespace)
        note(f"Namespace {namespace} dropped")
    except pyiceberg.exceptions.NoSuchNamespaceError:
        note(f"Namespace {namespace} does not exist")
    except Exception as e:
        note(f"An error occurred while dropping namespace: {e}")
        raise

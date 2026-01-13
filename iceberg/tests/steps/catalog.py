import os

# import boto3
import random
import subprocess
import pyarrow as pa
import string
import pyiceberg

from testflows.core import *
from decimal import Decimal
from datetime import date, timedelta, time, datetime

from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    StringType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    TimestampType,
    BooleanType,
    TimestamptzType,
    DateType,
    TimeType,
    UUIDType,
    BinaryType,
    DecimalType,
    StructType,
    ListType,
    MapType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

# from pyiceberg.catalog.glue import GlueCatalog

from helpers.common import getuid


CATALOG_TYPE = "rest"

_PRIMITIVE_TYPES = [
    StringType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    TimestampType,
    BooleanType,
    TimestamptzType,
    DateType,
    TimeType,
    # UUIDType,
    BinaryType,
    DecimalType,
]


@TestStep(Given)
def create_rest_catalog(
    self,
    uri="http://localhost:5000/",
    name=None,
    s3_access_key_id="test",
    s3_secret_access_key="test",
    s3_endpoint="http://localhost:9002",
    catalog_type=CATALOG_TYPE,
    auth_header="foo",
    clean_up_minio_bucket=True,
):
    if name is None:
        name = f"catalog_{getuid()}"

    try:
        conf = {
            "uri": uri,
            "type": catalog_type,
            "s3.endpoint": s3_endpoint,
            "s3.access-key-id": s3_access_key_id,
            "s3.secret-access-key": s3_secret_access_key,
        }

        if auth_header:
            conf["token"] = auth_header

        catalog = load_catalog(
            name,
            **conf,
        )
        yield catalog

    finally:
        with Finally("drop catalog"):
            if clean_up_minio_bucket:
                clean_minio_bucket(
                    bucket_name="warehouse",
                    s3_endpoint=s3_endpoint,
                    s3_access_key_id=s3_access_key_id,
                    s3_secret_access_key=s3_secret_access_key,
                )


@TestStep(Given)
def create_glue_catalog(
    self,
    s3_access_key_id,
    s3_secret_access_key,
    name=None,
    glue_endpoint="http://localhost:4566",
    glue_region="us-east-1",
    glue_access_key_id="test",
    glue_secret_access_key="test",
    s3_endpoint="http://localhost:9002",
    clean_up_minio_bucket=True,
):
    if name is None:
        name = f"glue_catalog_{getuid()}"
    try:
        glue_catalog = load_catalog(
            name,
            type="glue",
            **{
                "glue.access-key-id": glue_access_key_id,
                "glue.secret-access-key": glue_secret_access_key,
                "glue.endpoint": glue_endpoint,
                "glue.region": glue_region,
                "s3.endpoint": s3_endpoint,
                "s3.access-key-id": s3_access_key_id,
                "s3.secret-access-key": s3_secret_access_key,
            },
        )
        yield glue_catalog

    finally:
        with Finally("drop catalog"):
            if clean_up_minio_bucket:
                clean_minio_bucket(
                    bucket_name="warehouse",
                    s3_endpoint=s3_endpoint,
                    s3_access_key_id=s3_access_key_id,
                    s3_secret_access_key=s3_secret_access_key,
                )


@TestStep(Given)
def create_catalog(self, **kwargs):
    if self.context.catalog == "rest":
        return create_rest_catalog(**kwargs)
    elif self.context.catalog == "glue":
        return create_glue_catalog(**kwargs)
    else:
        raise ValueError(f"Unsupported catalog type: {self.context.catalog}")


# @TestStep(Given)
# def list_sizes(
#     self,
#     bucket_name: str,
#     prefix: str,
#     s3_endpoint: str,
#     s3_access_key_id: str,
#     s3_secret_access_key: str,
# ):
#     """
#     Return (metadata_bytes, parquet_bytes, total_bytes) for everything
#     under `bucket_name/prefix`  on the given MinIO endpoint.

#     * “metadata” = any key that contains "/metadata/"
#     * “parquet”  = any key that ends with ".parquet"
#     * the rest is ignored for the two subtotals but still counted in total
#     """
#     s3 = boto3.client(
#         "s3",
#         endpoint_url=s3_endpoint,
#         aws_access_key_id=s3_access_key_id,
#         aws_secret_access_key=s3_secret_access_key,
#     )

#     paginator = s3.get_paginator("list_objects_v2")
#     meta_bytes = parquet_bytes = total_bytes = 0

#     for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
#         for o in page.get("Contents", []):
#             size = o["Size"]
#             key = o["Key"]
#             total_bytes += size
#             if "/metadata/" in key:
#                 meta_bytes += size
#             elif key.endswith(".parquet"):
#                 parquet_bytes += size

#     note(
#         f"metadata={meta_bytes:,} B  parquet={parquet_bytes:,} B  total={total_bytes:,} B"
#     )
#     return meta_bytes, parquet_bytes, total_bytes


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
    table_properties={},
    drop_table=True,
):
    """Create iceberg table."""
    table_properties["format-version"] = format_version

    try:
        table = catalog.create_table(
            identifier=f"{namespace}.{table_name}",
            schema=schema,
            location=location,
            sort_order=sort_order,
            partition_spec=partition_spec,
            properties=table_properties,
        )
        yield table

    finally:
        with Finally("drop table"):
            if drop_table:
                drop_iceberg_table(
                    catalog=catalog, namespace=namespace, table_name=table_name
                )


@TestStep(Given)
def create_iceberg_table_with_three_columns(
    self,
    catalog,
    namespace,
    table_name,
    location="s3://warehouse/data",
    with_data=False,
    number_of_rows=10,
    table_properties={},
):
    """Define schema, partition spec, sort order and create iceberg table with three columns."""
    schema = Schema(
        NestedField(field_id=1, name="name", field_type=StringType(), required=False),
        NestedField(field_id=2, name="double", field_type=DoubleType(), required=False),
        NestedField(field_id=3, name="integer", field_type=LongType(), required=False),
    )
    sort_order = SortOrder(SortField(source_id=1, transform=IdentityTransform()))
    partition_spec = PartitionSpec(
        PartitionField(
            source_id=1,
            field_id=1001,
            transform=IdentityTransform(),
            name="name",
        ),
    )
    table = create_iceberg_table(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        schema=schema,
        location=location,
        partition_spec=partition_spec,
        sort_order=sort_order,
        table_properties=table_properties,
    )

    if with_data:
        with By(f"insert random {number_of_rows} rows into Iceberg table"):
            data = []
            for _ in range(number_of_rows):
                data.append(
                    {
                        "name": random_name(),
                        "double": random.uniform(0, 100),
                        "integer": random.randint(0, 10000),
                    }
                )
            df = pa.Table.from_pylist(data)
            table.append(df)

    return table


@TestStep(Given)
def create_iceberg_table_with_five_columns(
    self,
    catalog,
    namespace,
    table_name,
    number_of_rows=10,
    with_data=False,
    location="s3://warehouse/data",
):
    """Create an Iceberg table with five columns and optionally insert random data.
    Table partitioned by string column and sorted by the same column."""

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
            source_id=4,
            field_id=1001,
            transform=IdentityTransform(),
            name="name",
        ),
    )

    sort_order = SortOrder(SortField(source_id=4, transform=IdentityTransform()))

    table = create_iceberg_table(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        schema=schema,
        location=location,
        partition_spec=partition_spec,
        sort_order=sort_order,
    )

    if with_data:
        with By("insert random data into Iceberg table"):
            data = []
            for _ in range(number_of_rows):
                data.append(
                    {
                        "boolean_col": random.choice([True, False]),
                        "long_col": random.randint(1000, 10000),
                        "double_col": round(random.uniform(1.0, 500.0), 2),
                        "string_col": f"User{random.randint(1, 1000)}",
                        "date_col": date.today()
                        - timedelta(days=random.randint(0, 3650)),
                    }
                )

            df = pa.Table.from_pylist(data)
            table.append(df)

    return table


@TestStep(Given)
def list_objects_cli(
    self,
    bucket_name,
    s3_endpoint,
    s3_access_key_id,
    s3_secret_access_key,
    recursive=True,
):
    """Return a list of keys in *bucket_name*."""
    cmd = ["aws", "--endpoint-url", s3_endpoint, "s3", "ls", f"s3://{bucket_name}"]

    if recursive:
        cmd.append("--recursive")

    env = {
        "AWS_ACCESS_KEY_ID": s3_access_key_id,
        "AWS_SECRET_ACCESS_KEY": s3_secret_access_key,
    }

    current_env = os.environ.copy()
    current_env.update(env)

    try:
        result = subprocess.run(
            cmd, env=current_env, capture_output=True, text=True, check=True
        )
        stdout = result.stdout
    except subprocess.CalledProcessError as e:
        note(f"AWS CLI command failed: {e}")
        note(f"Error output: {e.stderr}")
        raise

    keys = [line.split(maxsplit=3)[-1] for line in stdout.splitlines() if line.strip()]
    return keys


@TestStep(When)
def clean_minio_bucket(
    self,
    bucket_name,
    s3_endpoint,
    s3_access_key_id,
    s3_secret_access_key,
):
    """Remove every object in *bucket_name*."""
    with Given("list objects"):
        objects = list_objects_cli(
            bucket_name=bucket_name,
            s3_endpoint=s3_endpoint,
            s3_access_key_id=s3_access_key_id,
            s3_secret_access_key=s3_secret_access_key,
        )
        note(f"{len(objects)} object(s) found in {bucket_name}")

    if objects:
        cmd = [
            "aws",
            "--endpoint-url",
            s3_endpoint,
            "s3",
            "rm",
            f"s3://{bucket_name}",
            "--recursive",
        ]

        env = {
            "AWS_ACCESS_KEY_ID": s3_access_key_id,
            "AWS_SECRET_ACCESS_KEY": s3_secret_access_key,
        }

        current_env = os.environ.copy()
        current_env.update(env)

        try:
            result = subprocess.run(
                cmd,
                env=current_env,
                check=True,
                capture_output=True,
            )
            note(f"Emptied {bucket_name}")
        except subprocess.CalledProcessError as e:
            note(f"AWS CLI command failed: {e}")
            note(f"Error output: {e.stderr}")
            raise
    else:
        note(f"No objects to delete in {bucket_name}")


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


@TestStep(Given)
def create_catalog_and_iceberg_table_with_data(
    self,
    minio_root_user,
    minio_root_password,
    namespace=None,
    table_name=None,
    with_data=True,
):
    """Combine all steps to create catalog, namespace, table with five
    columns and insert 4 rows of data to the created table."""

    if namespace is None:
        namespace = "namespace_" + getuid()

    if table_name is None:
        table_name = "table_" + getuid()

    with By("create catalog"):
        catalog = create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        drop_iceberg_table(catalog=catalog, namespace=namespace, table_name=table_name)

    with And(f"define schema and create {namespace}.{table_name} table"):
        table = create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("insert data into Iceberg table if required"):
        df = pa.Table.from_pylist(
            [
                {
                    "boolean_col": True,
                    "long_col": 1000,
                    "double_col": 456.78,
                    "string_col": "Alice",
                    "date_col": date(2024, 1, 1),
                },
                {
                    "boolean_col": False,
                    "long_col": 2000,
                    "double_col": 456.78,
                    "string_col": "Bob",
                    "date_col": date(2023, 5, 15),
                },
                {
                    "boolean_col": True,
                    "long_col": 3000,
                    "double_col": 6.7,
                    "string_col": "Charlie",
                    "date_col": date(2022, 1, 1),
                },
                {
                    "boolean_col": False,
                    "long_col": 4000,
                    "double_col": 8.9,
                    "string_col": "1",
                    "date_col": date(2021, 1, 1),
                },
            ]
        )
        if with_data:
            table.append(df)

    return table_name, namespace


@TestStep(Given)
def equality_delete_from_iceberg_table(self, iceberg_table, condition):
    """Delete rows from Iceberg table using equality condition."""
    iceberg_table.delete(delete_filter=f"{condition}")


@TestStep(Given)
def delete_transaction(self, iceberg_table, condition):
    """Delete rows from Iceberg table using transaction."""
    with iceberg_table.transaction() as txn:
        txn.delete(condition)


@TestStep(Given)
def delete_rows_from_iceberg_table(self, iceberg_table, condition):
    """Delete rows from Iceberg table using transaction."""
    iceberg_table.delete(condition)


def random_time():
    """Generate a random time object with random hours, minutes, seconds, microseconds."""
    return time(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=random.randint(0, 999999),
    )


def random_name(length=5):
    """Generate a random lowercase string of specified length."""
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_datetime(start=datetime(2020, 1, 1), end=datetime.now()):
    """Generate a random datetime between start and end."""
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


def random_decimal(*, precision=9, scale=2):
    """Generate a random decimal matching the given precision and scale."""
    max_value = 10 ** (precision - scale) - 1
    value = round(random.uniform(-max_value, max_value), scale)
    return Decimal(f"{value:.{scale}f}")


def random_primitive(iceberg_type):
    """Generate a random primitive value matching the specified Iceberg type."""
    if isinstance(iceberg_type, StringType):
        return random_name(length=8)
    if isinstance(iceberg_type, IntegerType):
        return random.randint(0, 10000)
    if isinstance(iceberg_type, DoubleType):
        return random.uniform(0, 100)
    if isinstance(iceberg_type, TimeType):
        return random_time()
    if isinstance(iceberg_type, TimestampType):
        return random_datetime()
    if isinstance(iceberg_type, TimestamptzType):
        return random_datetime()
    if isinstance(iceberg_type, BooleanType):
        return random.choice([True, False])
    if isinstance(iceberg_type, LongType):
        return random.randint(0, 10000)
    if isinstance(iceberg_type, FloatType):
        return random.uniform(0, 100)
    if isinstance(iceberg_type, DecimalType):
        return random_decimal()
    if isinstance(iceberg_type, DateType):
        return random_datetime().date()
    if isinstance(iceberg_type, BinaryType):
        return bytes(random_name(length=16), "utf-8")
    raise NotImplementedError(f"Unsupported type: {type(iceberg_type)}")


def random_field_type(max_depth=3):
    """Randomly generate an Iceberg type (primitive or nested struct, list, map)."""
    if max_depth <= 0:
        selected_type = random.choice(_PRIMITIVE_TYPES)
        if selected_type is DecimalType:
            return DecimalType(precision=9, scale=2)
        return selected_type()

    type_choice = random.choice(["struct", "list", "map", "primitive"])

    if type_choice == "struct":
        fields = [
            NestedField(
                field_id=i + 1,
                name=random_name(),
                field_type=random_field_type(max_depth=max_depth - 1),
            )
            for i in range(random.randint(1, 3))
        ]
        return StructType(*fields)

    if type_choice == "list":
        return ListType(
            element_id=1,
            element_type=random_field_type(max_depth=max_depth - 1),
            element_required=False,
        )

    if type_choice == "map":
        return MapType(
            key_id=1,
            key_type=StringType(),
            value_id=2,
            value_type=random_field_type(max_depth=max_depth - 1),
            value_required=False,
        )

    selected_type = random.choice(_PRIMITIVE_TYPES)
    if selected_type is DecimalType:
        return DecimalType(precision=9, scale=2)
    return selected_type()


def iceberg_to_pyarrow(iceberg_type):
    """Convert Iceberg data type to corresponding PyArrow data type."""
    if isinstance(iceberg_type, StringType):
        return pa.string()
    if isinstance(iceberg_type, IntegerType):
        return pa.int32()
    if isinstance(iceberg_type, DoubleType):
        return pa.float64()
    if isinstance(iceberg_type, TimeType):
        return pa.time64("us")
    if isinstance(iceberg_type, TimestampType):
        return pa.timestamp("ms")
    if isinstance(iceberg_type, TimestamptzType):
        return pa.timestamp("ms", tz="UTC")
    if isinstance(iceberg_type, BooleanType):
        return pa.bool_()
    if isinstance(iceberg_type, LongType):
        return pa.int64()
    if isinstance(iceberg_type, FloatType):
        return pa.float32()
    if isinstance(iceberg_type, DecimalType):
        return pa.decimal128(9, 2)
    if isinstance(iceberg_type, DateType):
        return pa.date32()
    if isinstance(iceberg_type, BinaryType):
        return pa.binary()
    if isinstance(iceberg_type, StructType):
        return pa.struct(
            [
                (f.name, iceberg_to_pyarrow(iceberg_type=f.field_type))
                for f in iceberg_type.fields
            ]
        )
    if isinstance(iceberg_type, ListType):
        return pa.list_(iceberg_to_pyarrow(iceberg_type=iceberg_type.element_type))
    if isinstance(iceberg_type, MapType):
        return pa.map_(
            pa.string(), iceberg_to_pyarrow(iceberg_type=iceberg_type.value_type)
        )
    raise NotImplementedError(f"Unsupported type: {type(iceberg_type)}")


def random_data(iceberg_type):
    """Generate random data matching given Iceberg datatype."""
    if isinstance(iceberg_type, StructType):
        return {
            f.name: random_data(iceberg_type=f.field_type) for f in iceberg_type.fields
        }
    if isinstance(iceberg_type, ListType):
        return [
            random_data(iceberg_type=iceberg_type.element_type)
            for _ in range(random.randint(0, 3))
        ]
    if isinstance(iceberg_type, MapType):
        return {
            random_name(length=4): random_data(iceberg_type=iceberg_type.value_type)
            for _ in range(random.randint(0, 3))
        }
    return random_primitive(iceberg_type=iceberg_type)

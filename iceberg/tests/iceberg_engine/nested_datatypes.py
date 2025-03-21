from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid

from decimal import Decimal
from datetime import datetime, timedelta, time

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

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

import random
import string
import pyarrow as pa


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
    """Generate a random decimal number matching the given precision and scale."""
    if scale > precision:
        raise ValueError("Scale cannot exceed precision.")
    max_integer_part = 10 ** (precision - scale) - 1
    integer_part = random.randint(-max_integer_part, max_integer_part)
    fractional_part = random.randint(0, 10**scale - 1)
    return Decimal(f"{integer_part}.{fractional_part:0{scale}d}")

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


@TestScenario
def struct_list_map_test(self, minio_root_user, minio_root_password, num_columns):
    """
    Create Iceberg table with specified number of columns and random datatypes:
    primitives, structs, lists, and maps. Insert random data into the table and check
    that the data can be read via table from ClickHouse Iceberg engine.
    """
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_db_{getuid()}"

    with Given("create database and catalog"):
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When("define schema and create table"):
        nested_fields = [
            NestedField(
                field_id=i + 1,
                name=f"col_{i+1}",
                field_type=random_field_type(max_depth=3),
            )
            for i in range(num_columns)
        ]
        schema = Schema(*nested_fields)

        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("insert random data into table"):
        arrow_schema = pa.schema(
            [
                pa.field(
                    name=f.name, type=iceberg_to_pyarrow(iceberg_type=f.field_type)
                )
                for f in nested_fields
            ]
        )
        rows = [
            {f.name: random_data(iceberg_type=f.field_type) for f in nested_fields}
            for _ in range(10)
        ]
        table.append(pa.Table.from_pylist(mapping=rows, schema=arrow_schema))

    with Then("verify data via PyIceberg"):
        df = table.scan().to_pandas()
        note(f"PyIceberg data:\n{df}")

    with And("verify data via ClickHouse"):
        self.context.node.query(
            f"DESCRIBE TABLE {database_name}.\\`{namespace}.{table_name}\\`"
        )
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            format="JSONEachRow",
        )
        count = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            columns="count()",
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            format="TabSeparated",
        ).output
        assert count.strip() == "10", error()


@TestFeature
@Name("datatypes")
def feature(self, minio_root_user, minio_root_password):
    """Check that ClickHouse Iceberg engine supports reading all Iceberg data types."""
    for num_columns in range(1, 1000, 50):
        Scenario(name=f"number of columns {num_columns}", test=struct_list_map_test)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            num_columns=num_columns,
        )

#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

import pyarrow as pa
import pandas as pd

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine
import iceberg.tests.steps.s3 as s3_steps

from pyiceberg.schema import Schema, Field
from pyiceberg.types import (
    BooleanType,
    StringType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    TimestampType,
    TimestamptzType,
    DateType,
    TimeType,
    UUIDType,
    BinaryType,
    FixedType,
    DecimalType,
    StructType,
    ListType,
    MapType,
    NestedField,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField
from pyiceberg.transforms import IdentityTransform

from datetime import datetime, timedelta

from decimal import Decimal

import uuid
import random
import string

# pd.set_option("display.max_colwidth", None)  # Show full content in columns
# pd.set_option("display.expand_frame_repr", False)  # Avoid line wrapping
pd.set_option("display.max_rows", None)  # Show all rows
# pd.set_option("display.max_columns", None)  # Show all columns

_PRIMITIVE_TYPES = [StringType, IntegerType, DoubleType, TimestampType, BooleanType]


def random_datetime_in_range(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


def generate_random_name(length=5):
    """Generate a random lowercase field name."""
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


def generate_iceberg_struct_field(
    name, max_width, max_depth, start_id=1, required=False
):
    """
    Generate a nested NestedField with random width and random depth
    for each subfield. Returns (nested_field, next_field_id).
    """
    if max_depth <= 0:
        iceberg_type = random.choice(_PRIMITIVE_TYPES)()
        return NestedField(start_id, name, iceberg_type, required), start_id + 1

    field_id = start_id
    subfields = []
    current_width = random.randint(1, max_width)

    for _ in range(current_width):
        child_name = generate_random_name()
        child_depth = random.randint(0, max_depth - 1)
        child_field, next_id = generate_iceberg_struct_field(
            child_name, max_width, child_depth, field_id + 1, required=False
        )
        field_id = next_id - 1
        subfields.append(child_field)

    struct_type = StructType(*subfields)
    return NestedField(start_id, name, struct_type, required), field_id + 1


def generate_iceberg_list_field(name, max_width, max_depth, start_id=1, required=False):
    """
    Create a List NestedField whose element type can be either a nested type or a primitive,
    depending on random choice (and available nesting depth).
    Returns (NestedField, next_field_id).
    """

    if max_depth <= 0:
        element_type = random.choice(_PRIMITIVE_TYPES)()
        element_id = start_id + 1
        next_id = start_id + 2
    else:
        # Define possible element-type builders (struct or primitive)
        def build_struct(s_id):
            child_name = generate_random_name()
            struct_field, n_id = generate_iceberg_struct_field(
                name=child_name,
                max_width=max_width,
                max_depth=max_depth - 1,
                start_id=s_id + 1,
                required=False,
            )
            return struct_field.field_id, struct_field.field_type, n_id

        def build_primitive(s_id):
            element_type = random.choice(_PRIMITIVE_TYPES)()
            e_id = s_id + 1
            n_id = s_id + 2
            return e_id, element_type, n_id

        chosen_builder = random.choice([build_struct, build_primitive])
        element_id, element_type, next_id = chosen_builder(start_id)

    list_type = ListType(
        element_id=element_id, element_type=element_type, element_required=False
    )

    return NestedField(start_id, name, list_type, required), next_id


def iceberg_type_to_pyarrow(field_type):
    """
    Convert a single Iceberg field_type to the corresponding PyArrow type.
    """
    if isinstance(field_type, StringType):
        return pa.string()
    elif isinstance(field_type, IntegerType):
        return pa.int32()
    elif isinstance(field_type, DoubleType):
        return pa.float64()
    elif isinstance(field_type, TimestampType):
        return pa.timestamp("ms")
    elif isinstance(field_type, BooleanType):
        return pa.bool_()
    elif isinstance(field_type, StructType):
        return pa.struct(
            [(f.name, iceberg_type_to_pyarrow(f.field_type)) for f in field_type.fields]
        )
    elif isinstance(field_type, ListType):
        return pa.list_(iceberg_type_to_pyarrow(field_type.element_type))
    else:
        raise NotImplementedError(
            f"No PyArrow type mapping available for Iceberg type {type(field_type)}."
        )


def generate_random_value(field_type):
    """
    Generate a single random value corresponding to a given Iceberg type.
    """
    if isinstance(field_type, StringType):
        return generate_random_name(8)
    elif isinstance(field_type, IntegerType):
        return random.randint(0, 10000)
    elif isinstance(field_type, DoubleType):
        return random.random() * 100
    elif isinstance(field_type, TimestampType):
        return random_datetime_in_range(datetime(2020, 1, 1), datetime.now())
    elif isinstance(field_type, BooleanType):
        return bool(random.randint(0, 1))
    elif isinstance(field_type, StructType):
        return {f.name: generate_random_value(f.field_type) for f in field_type.fields}
    else:
        raise NotImplementedError(
            f"Unexpected Iceberg type {type(field_type)}, cannot generate data."
        )


def generate_arrow_field(nested_field):
    """
    Build a single PyArrow Field from an Iceberg NestedField.
    """
    arrow_type = iceberg_type_to_pyarrow(nested_field.field_type)
    return pa.field(nested_field.name, arrow_type)


def generate_arrow_schema_from_nested_field(nested_field):
    """
    Convert an Iceberg NestedField into a PyArrow Schema (with just one top-level field).
    """
    arrow_field = generate_arrow_field(nested_field)
    return pa.schema([arrow_field])


def generate_primitive_value(iceberg_type):
    """Return a random primitive value (String, Int, etc.)."""
    if isinstance(iceberg_type, StringType):
        return generate_random_name(8)
    elif isinstance(iceberg_type, IntegerType):
        return random.randint(0, 10000)
    elif isinstance(iceberg_type, DoubleType):
        return random.random() * 100
    elif isinstance(iceberg_type, TimestampType):
        return random_datetime_in_range(datetime(2020, 1, 1), datetime.now())
    elif isinstance(iceberg_type, BooleanType):
        return bool(random.randint(0, 1))
    else:
        raise NotImplementedError(
            f"No generator for primitive type {type(iceberg_type)}"
        )


def generate_value_for_type(iceberg_type):
    """
    Decide which of the three functions (primitive, struct, or list)
    to call based on the actual Iceberg type.
    """
    if isinstance(iceberg_type, StructType):
        return generate_value_for_struct(iceberg_type)
    elif isinstance(iceberg_type, ListType):
        return generate_value_for_list(iceberg_type)
    elif type(iceberg_type) in _PRIMITIVE_TYPES:
        return generate_primitive_value(iceberg_type)
    else:
        raise NotImplementedError(f"No generator for type {type(iceberg_type)}")


def generate_value_for_struct(struct_type):
    """Build a dict with random values for each subfield."""
    return {f.name: generate_value_for_type(f.field_type) for f in struct_type.fields}


def generate_value_for_list(list_type):
    """Build a random-sized list of elements, which might be primitive or struct."""
    length = random.randint(0, 5)  # e.g. 0..5 elements
    return [generate_value_for_type(list_type.element_type) for _ in range(length)]


def generate_data_from_nested_field(nf: NestedField):
    """
    Generate random data for a single NestedField (which might be struct or list).
    """
    t = nf.field_type
    if isinstance(t, StructType):
        return generate_value_for_struct(t)
    elif isinstance(t, ListType):
        return generate_value_for_list(t)
    elif type(t) in _PRIMITIVE_TYPES:
        return generate_primitive_value(t)
    else:
        raise NotImplementedError(f"No generator for type {type(t)}")


def generate_iceberg_primitive_field(name, start_id=1, required=False, **kwargs):
    """Randomly pick one of the primitive Iceberg types to use as a single field."""
    iceberg_type = random.choice(_PRIMITIVE_TYPES)()
    return NestedField(start_id, name, iceberg_type, required), start_id + 1


@TestScenario
def struct_or_list_type(self, minio_root_user, minio_root_password, num_columns):
    """Create a table with a fixed number of columns. Each column is randomly either a Struct or a List."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create database with Iceberg engine"):
        iceberg_engine.create_experimental_iceberg_database(
            namespace=namespace,
            database_name=database_name,
            rest_catalog_url="http://rest:8181/v1",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema with {num_columns} random columns and create table"):
        nested_fields = []
        start_id = 1
        for i in range(num_columns):
            col_name = f"col_{i+1}"

            # Randomly pick which kind of field to generate
            col_func = random.choice(
                [
                    generate_iceberg_struct_field,
                    generate_iceberg_list_field,
                    generate_iceberg_primitive_field,
                ]
            )

            nf, next_id = col_func(
                name=col_name,
                max_width=3,
                max_depth=3,
                start_id=start_id,
                required=False,
            )
            nested_fields.append(nf)
            start_id = next_id

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

    with And(f"insert data into {namespace}.{table_name} table"):
        arrow_fields = [generate_arrow_field(nf) for nf in nested_fields]

        num_rows = 10
        data_rows = []
        for _ in range(num_rows):
            row_dict = {}
            for nf in nested_fields:
                row_dict.update({nf.name: generate_data_from_nested_field(nf)})
            data_rows.append(row_dict)

        final_arrow_schema = pa.schema(arrow_fields)
        table_data = pa.Table.from_pylist(data_rows, schema=final_arrow_schema)
        table.append(table_data)

    with And("scan and display data via PyIceberg"):
        df = table.scan().to_pandas()
        note(f"PyIceberg data:\n{df}")

    with And("read data in ClickHouse from the previously created table"):
        self.context.node.query(
            f"DESCRIBE TABLE {database_name}.\\`{namespace}.{table_name}\\`"
        )
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            format="JSONEachRow",
        )
        note(f"ClickHouse data:\n{result}")
        pause()


@TestScenario
def multiple_structs(self, minio_root_user, minio_root_password):
    """Run the same scenario with different numbers of struct fields."""
    for num in [2, 5, 10]:
        struct_or_list_type(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            num_columns=num,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=multiple_structs)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

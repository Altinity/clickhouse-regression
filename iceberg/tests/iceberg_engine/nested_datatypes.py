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

_PRIMITIVE_TYPES = [StringType, IntegerType, DoubleType, TimestampType, BooleanType]


def random_datetime_in_range(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )


def generate_random_name(length=5):
    """Generate a random lowercase field name."""
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


def generate_iceberg_nested_field(
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
        child_field, next_id = generate_iceberg_nested_field(
            child_name, max_width, child_depth, field_id + 1, required=False
        )
        field_id = next_id - 1
        subfields.append(child_field)

    struct_type = StructType(*subfields)
    return NestedField(start_id, name, struct_type, required), field_id + 1


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


def generate_data_from_nested_field(nested_field):
    """
    Generate random data for an Iceberg NestedField.
    """
    data_value = generate_random_value(nested_field.field_type)
    return {nested_field.name: data_value}



@TestScenario
@Name("struct_type_with_n_structs")
def struct_type_with_n_structs(
    self, minio_root_user, minio_root_password, num_structs=2
):
    """Create an Iceberg table with 1 string field + N struct fields, then insert & read data."""
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
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            uri="http://localhost:8182/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with When(f"define schema with {num_structs} struct fields and create table"):
        struct_fields = []
        start_id = 1
        for i in range(num_structs):
            name = f"details{i+1}"
            nf, next_id = generate_iceberg_nested_field(
                name, max_width=3, max_depth=4, start_id=start_id
            )
            struct_fields.append(nf)
            start_id = next_id

        schema = Schema(*struct_fields)

        partition_spec = PartitionSpec()
        sort_order = SortOrder()

        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=sort_order,
        )

    with And(f"insert data into {namespace}.{table_name} table"):
        arrow_struct_fields = [generate_arrow_field(nf) for nf in struct_fields]

        # We'll collect rows in data_rows
        data_rows = []
        number_of_rows = 10
        for _ in range(number_of_rows):
            row_dict = {}
            for nf in struct_fields:
                data = generate_data_from_nested_field(nf)
                row_dict.update(data)
            data_rows.append(row_dict)

        final_arrow_schema = pa.schema([*arrow_struct_fields])

        table_data = pa.Table.from_pylist(data_rows, schema=final_arrow_schema)
        table.append(table_data)

    with And("scan and display data via PyIceberg"):
        df = table.scan().to_pandas()
        note(f"Data from PyIceberg:\n{df}")

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
        note(f"Data from ClickHouse:\n{result}")
        pause()


@TestScenario
def multiple_structs(self, minio_root_user, minio_root_password):
    """Run the same scenario with different numbers of struct fields."""
    for num in [2, 5, 10]:
        struct_type_with_n_structs(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            num_structs=num,
        )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    Scenario(test=multiple_structs)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

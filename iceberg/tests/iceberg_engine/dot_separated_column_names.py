#!/usr/bin/env python3

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from decimal import Decimal
from pyiceberg.schema import Schema
from pyiceberg.types import (
    BooleanType,
    StringType,
    LongType,
    IntegerType,
    DoubleType,
    FloatType,
    DecimalType,
    TimestampType,
    TimestamptzType,
    DateType,
    TimeType,
    BinaryType,
    FixedType,
    NestedField,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import IdentityTransform
from pyiceberg.table.sorting import SortOrder, SortField

import pyarrow as pa
import random

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.icebergS3 as icebergS3
import iceberg.tests.steps.s3 as s3_steps


@TestScenario
def all_datatypes_with_dot_separated_columns(self, minio_root_user, minio_root_password):
    """Test that ClickHouse correctly reads all Iceberg data types with
    dot-separated column names using Iceberg engine, icebergS3 table function and S3 table function."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    dot_separated_columns = [
        ("integer.col", IntegerType()),
        ("long.column", LongType()),
        ("double.col", DoubleType()),
        ("float.column", FloatType()),
        ("boolean.col", BooleanType()),
        ("timestamp.column", TimestampType()),
        ("timestamptz.col", TimestamptzType()),
        ("date.column", DateType()),
        ("string.column", StringType()),
        # ("fixed.string", FixedType(length=10)),
        ("binary.column", BinaryType()),
        ("decimal.column", DecimalType(38, 18)),
        ("time.column", TimeType()),
        ("integer.column.dot", IntegerType()),
        ("string.col.dot", StringType()),
        ("double.column.dot", DoubleType()),
    ]

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create iceberg table with all datatypes and dot-separated column names"):
        fields = [
            NestedField(field_id=i + 1, name=col_name, field_type=col_type, required=False)
            for i, (col_name, col_type) in enumerate(dot_separated_columns)
        ]
        schema = Schema(*fields)
        partition_spec = random.choice(
            [
                PartitionSpec(),
                PartitionSpec(
                    PartitionField(
                        source_id=1,
                        field_id=1001,
                        transform=IdentityTransform(),
                        name="name",
                    )
                ),
            ]
        )
        sort_order = random.choice(
            [
                SortOrder(),
                SortOrder(SortField(source_id=1, transform=IdentityTransform())),
            ]
        )

        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=sort_order,
        )

    with And("create arrow schema for data insertion"):
        arrow_fields = []
        for col_name, col_type in dot_separated_columns:
            if isinstance(col_type, IntegerType):
                arrow_type = pa.int32()
            elif isinstance(col_type, LongType):
                arrow_type = pa.int64()
            elif isinstance(col_type, DoubleType):
                arrow_type = pa.float64()
            elif isinstance(col_type, FloatType):
                arrow_type = pa.float32()
            elif isinstance(col_type, BooleanType):
                arrow_type = pa.bool_()
            elif isinstance(col_type, TimestampType):
                arrow_type = pa.timestamp("us")
            elif isinstance(col_type, TimestamptzType):
                arrow_type = pa.timestamp("us", tz="UTC")
            elif isinstance(col_type, DateType):
                arrow_type = pa.date32()
            elif isinstance(col_type, StringType):
                arrow_type = pa.string()
            elif isinstance(col_type, BinaryType):
                arrow_type = pa.binary()
            elif isinstance(col_type, DecimalType):
                arrow_type = pa.decimal128(col_type.precision, col_type.scale)
            elif isinstance(col_type, TimeType):
                arrow_type = pa.time64("us")
            else:
                arrow_type = pa.string()
            arrow_fields.append((col_name, arrow_type))

        arrow_schema = pa.schema(arrow_fields)

    with And("insert test data into iceberg table"):
        test_data = []
        for _ in range(5):
            row = {}
            for col_name, col_type in dot_separated_columns:
                if isinstance(col_type, IntegerType):
                    row[col_name] = random.randint(0, 10000)
                elif isinstance(col_type, LongType):
                    row[col_name] = random.randint(0, 10000)
                elif isinstance(col_type, DoubleType):
                    row[col_name] = round(random.uniform(0, 100), 2)
                elif isinstance(col_type, FloatType):
                    row[col_name] = round(random.uniform(0, 100), 2)
                elif isinstance(col_type, BooleanType):
                    row[col_name] = random.choice([True, False])
                elif isinstance(col_type, TimestampType):
                    row[col_name] = random.randint(0, 100000000)
                elif isinstance(col_type, TimestamptzType):
                    row[col_name] = random.randint(0, 100000000)
                elif isinstance(col_type, DateType):
                    row[col_name] = random.randint(0, 10000)
                elif isinstance(col_type, StringType):
                    row[col_name] = random.choice(["test", "test2", "test3"])
                elif isinstance(col_type, BinaryType):
                    row[col_name] = random.choice(["test", "test2", "test3"])
                elif isinstance(col_type, DecimalType):
                    row[col_name] = Decimal(random.randint(0, 10000)) / Decimal(100)
                elif isinstance(col_type, TimeType):
                    row[col_name] = random.randint(0, 100000000)
            test_data.append(row)

        df = pa.Table.from_pylist(test_data, schema=arrow_schema)
        table.append(df)

    with And("scan and display data with pyiceberg"):
        df = table.scan().to_pandas()
        note(df)

    with Then("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("read data using Iceberg engine and verify all columns are accessible"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns="*",
        )
        assert result.output != "", error()

    with And("read data using Iceberg engine and verify specific columns are accessible"):
        for col_name, _ in dot_separated_columns:
            result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name, namespace=namespace, table_name=table_name, columns=f"\\`{col_name}\\`"
            )
            assert result.output != "", error()

    with And("read data using icebergS3 table function"):
        result = icebergS3.read_data_with_icebergS3_table_function(
            storage_endpoint="http://minio:9000/warehouse/data",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            columns="*",
        )
        assert result.output != "", error()

    with And("read data using icebergS3 table function and verify specific columns are accessible"):
        for col_name, _ in dot_separated_columns:
            result = icebergS3.read_data_with_icebergS3_table_function(
                storage_endpoint="http://minio:9000/warehouse/data",
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
                columns=f"\\`{col_name}\\`",
            )
            assert result.output != "", error()

    with And("read data using S3 table function"):
        result = s3_steps.read_data_with_s3_table_function(
            endpoint="http://minio:9000/warehouse/data/data/**.parquet",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            columns="*",
        )
        assert result.output != "", error()

    # with And("read data using S3 table function and verify specific columns are accessible"):
    #     for col_name, _ in dot_separated_columns:
    #         result = s3_steps.read_data_with_s3_table_function(
    #             endpoint="http://minio:9000/warehouse/data/data/**.parquet",
    #             s3_access_key_id=minio_root_user,
    #             s3_secret_access_key=minio_root_password,
    #             columns=f"\\`{col_name}\\`",
    #         )
    #         assert result.output != "", error()


@TestScenario
def sanity_dot_separated_column_names(self, minio_root_user, minio_root_password):
    """Sanity check for dot-separated column names in ClickHouse."""
    namespace = f"namespace_{getuid()}"
    table_name = f"table_{getuid()}"
    database_name = f"iceberg_database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create iceberg table with dot-separated column names"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
            schema=Schema(NestedField(field_id=1, name="name.column", field_type=StringType(), required=False)),
        )

    with And("insert one row into iceberg table"):
        test_data = [{"name.column": "test"}]
        df = pa.Table.from_pylist(test_data, schema=pa.schema([("name.column", pa.string())]))
        table.append(df)

    with And("create database with DataLakeCatalog engine"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    with And("read data using Iceberg engine and verify specific columns are accessible"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name, namespace=namespace, table_name=table_name, columns="name.column"
        )
        assert result.output == "test", error()


@TestFeature
@Name("dot separated column names")
def feature(self, minio_root_user, minio_root_password):
    """Check that ClickHouse correctly handles dot-separated column names
    with all Iceberg data types using Iceberg engine, icebergS3 table function and S3 table function."""
    Scenario(test=sanity_dot_separated_column_names)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=all_datatypes_with_dot_separated_columns)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

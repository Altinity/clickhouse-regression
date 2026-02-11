import pyarrow as pa

from testflows.core import *
from testflows.asserts import error

from functools import partial
from helpers.common import getuid
from datetime import datetime, timedelta, date, time

from decimal import Decimal
from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    FixedType,
    FloatType,
    IntegerType,
    ListType,
    LongType,
    MapType,
    StringType,
    StructType,
    TimeType,
    TimestampType,
    TimestamptzType,
    UUIDType,
)

from pyiceberg.partitioning import PartitionSpec
from pyiceberg.table.sorting import SortOrder

import iceberg.tests.steps.common as common
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestStep(Then)
def check_read_with_predicate_push_down(
    self, where_clause, database_name, namespace, table_name
):
    """Check that ClickHouse does not read any rows when predicate pushdown is enabled
    and the condition does not match any data.
    """
    with By("drop all caches"):
        common.drop_all_caches(node=self.context.node)

    with And("read with input_format_parquet_filter_push_down"):
        log_comment_with_pruning = f"with_pruning_{getuid()}"
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            where_clause=where_clause,
            input_format_parquet_filter_push_down="1",
            log_comment=log_comment_with_pruning,
            use_iceberg_metadata_files_cache="0",
            use_iceberg_partition_pruning="0",
            input_format_parquet_bloom_filter_push_down="0"
        )
        assert result.output.strip() == "", error()

    with And(f"check that 0 rows were read"):
        read_rows = metrics.get_read_rows(
            log_comment=log_comment_with_pruning,
        )
        assert int(read_rows.output.strip()) == 0, error(
            f"Expected 0 rows to be read, with where clause: {where_clause}, but got {read_rows.output.strip()}"
        )


@TestStep(Then)
def check_read_without_predicate_push_down(
    self, database_name, namespace, table_name, where_clause, length
):
    """Check that ClickHouse reads all rows when predicate pushdown is disabled,
    even if the condition matches no data.
    """
    with By("drop all caches"):
        common.drop_all_caches(node=self.context.node)

    with And("read without input_format_parquet_filter_push_down"):
        log_comment_without_pruning = f"without_pruning_{getuid()}"
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            where_clause=where_clause,
            input_format_parquet_filter_push_down="0",
            log_comment=log_comment_without_pruning,
            use_iceberg_metadata_files_cache="0",
            use_iceberg_partition_pruning="0",
            input_format_parquet_bloom_filter_push_down="0",
        )
        assert result.output.strip() == "", error()

    with And(f"check that {length} rows were read"):
        read_rows = metrics.get_read_rows(
            log_comment=log_comment_without_pruning,
        )
        assert int(read_rows.output.strip()) == length, error(
            f"Expected {length} rows to be read, with where clause: {where_clause}, but got {read_rows.output.strip()}"
        )


def check_predicate_pushdown_clauses(where_clauses, read_with, read_without, length):
    """Run read checks with and without predicate pushdown for the given list of WHERE clauses."""
    for clause in where_clauses:
        read_with(where_clause=clause)
    for clause in where_clauses:
        read_without(where_clause=clause, length=length)


@TestScenario
def check_input_format_parquet_filter_push_down(
    self, minio_root_user, minio_root_password
):
    """Check that input_format_parquet_filter_push_down correctly skips row groups
    based on min/max stats for all data types.
    """
    table_name = f"table_{getuid()}"
    namespace = f"namespace_{getuid()}"
    database_name = f"database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("define table schema"):
        iceberg_schema = Schema(
            NestedField(field_id=1, name="string", field_type=StringType()),
            NestedField(field_id=2, name="boolean", field_type=BooleanType()),
            NestedField(field_id=3, name="integer", field_type=IntegerType()),
            NestedField(field_id=4, name="float", field_type=FloatType()),
            NestedField(field_id=5, name="double", field_type=DoubleType()),
            NestedField(field_id=6, name="decimal", field_type=DecimalType(9, 2)),
            NestedField(field_id=7, name="date", field_type=DateType()),
            NestedField(field_id=8, name="timestamp", field_type=TimestampType()),
            NestedField(
                field_id=9,
                name="timestamptz",
                field_type=TimestamptzType(),
            ),
            NestedField(field_id=10, name="long", field_type=LongType()),
            NestedField(field_id=11, name="time", field_type=TimeType()),
            NestedField(
                field_id=12,
                name="fixed",
                field_type=FixedType(length=16),
            ),
        )

    with And("create unpartitioned and unsorted table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=iceberg_schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("insert fixed data into iceberg table"):
        length = 10
        string_values = [str(i) for i in range(length)]
        boolean_values = [False for _ in range(length)]
        integer_values = [i for i in range(length)]
        float_values = [float(i + 0.5) for i in range(length)]
        double_values = [float(i + 2.5) for i in range(length)]
        decimal_values = [Decimal(i + 0.5) for i in range(length)]
        date_values = [date(2021, 1, 1) + timedelta(days=i) for i in range(length)]
        timestamp_values = [
            datetime(2022, 1, 1) + timedelta(days=i) for i in range(length)
        ]
        timestamptz_values = [
            datetime(2023, 1, 1) + timedelta(days=i) for i in range(length)
        ]
        long_values = [i + 1000 for i in range(length)]
        time_values = [time(hour=i, minute=i, second=i) for i in range(length)]
        fixed_values = [i.to_bytes(16, "big") for i in range(length, length + length)]

        data = [
            {
                "string": string_values[i],
                "boolean": boolean_values[i],
                "integer": integer_values[i],
                "float": float_values[i],
                "double": double_values[i],
                "decimal": decimal_values[i],
                "date": date_values[i],
                "timestamp": timestamp_values[i],
                "timestamptz": timestamptz_values[i],
                "long": long_values[i],
                "time": time_values[i],
                "fixed": fixed_values[i],
            }
            for i in range(length)
        ]
        arrow_schema = pa.schema(
            [
                ("string", pa.string()),
                ("boolean", pa.bool_()),
                ("integer", pa.int32()),
                ("float", pa.float32()),
                ("double", pa.float64()),
                ("decimal", pa.decimal128(9, 2)),
                ("date", pa.date32()),
                ("timestamp", pa.timestamp("us")),
                ("timestamptz", pa.timestamp("us", tz="UTC")),
                ("long", pa.int64()),
                ("time", pa.time64("us")),
                ("fixed", pa.binary(16)),
            ]
        )
        df = pa.Table.from_pylist(data, schema=arrow_schema)
        table.append(df)
    
    with And("scan and display data using PyIceberg"):
        df = table.scan().to_pandas()
        note(df)

    with And("create Iceberg database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("define functions for reading data with and without predicate push down"):
        read_with_pruning = partial(
            check_read_with_predicate_push_down,
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
        )
        read_without_pruning = partial(
            check_read_without_predicate_push_down,
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
        )

    with Then("check predicate push down with string column"):
        with By(
            "define several where clauses: with string < min index, with string > max index, with string = value > max index"
        ):
            where_clauses = [
                "string < '0'",
                "string > 'a'",
                "string = 'a'",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with integer column"):
        with By(
            """define several where clauses: with integer < min index, with integer > max index, 
            with integer = value > max index, with integer = value < min index"""
        ):
            where_clauses = [
                "integer < 0",
                "integer > 10",
                f"integer = {integer_values[-1]+1}",
                f"integer = {integer_values[0]-1}",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with float column"):
        with By(
            """define several where clauses: with float < min index, with float > max index, 
            with float = value > max index, with float = value < min index"""
        ):
            where_clauses = [
                "float < 0",
                "float > 10",
                f"float > toFloat32({float_values[-1]+1})",
                f"float < toFloat32({float_values[0]-1})",
                f"float = toFloat32({float_values[-1]+1})",
                f"float = toFloat32({float_values[0]-1})",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with double column"):
        with By(
            """define several where clauses: with double < min index, with double > max index, 
            with double = value > max index, with double = value < min index"""
        ):
            where_clauses = [
                f"double < {double_values[0]-1}",
                f"double > {double_values[-1]+1}",
                f"double > toFloat32({double_values[-1]+1})",
                f"double = {double_values[-1]+1}",
                f"double = {double_values[0]-1}",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with decimal column"):
        with By(
            """define several where clauses: with decimal < min index, with decimal > max index, 
            with decimal = value > max index, with decimal = value < min index"""
        ):
            where_clauses = [
                f"decimal < toDecimal32({decimal_values[0]-1}, 2)",
                f"decimal > toDecimal32({decimal_values[-1]+1}, 2)",
                f"decimal = toDecimal32({decimal_values[-1]+1}, 2)",
                f"decimal = toDecimal32({decimal_values[0]-1}, 2)",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with date column"):
        with By(
            """define several where clauses: with date < min index, with date > max index, 
            with date = value > max index, with date = value < min index"""
        ):
            where_clauses = [
                f"date < '{date_values[0]}'",
                f"date > '{date_values[-1]}'",
                f"date = '2025-01-10'",
                f"date = '2020-01-01'",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with timestamp column"):
        with By(
            """define several where clauses: with timestamp < min index, with timestamp > max index, 
            with timestamp = value > max index, with timestamp = value < min index"""
        ):
            where_clauses = [
                f"timestamp < '{timestamp_values[0]}'",
                f"timestamp > '{timestamp_values[-1]}' + interval 1 day",
                f"timestamp = '{timestamp_values[-1]}' + interval 1 day",
                f"timestamp = '{timestamp_values[0]}' - interval 1 day",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with timestamptz column"):
        with By(
            """define several where clauses: with timestamptz < min index, with timestamptz > max index, 
            with timestamptz = value > max index, with timestamptz = value < min index"""
        ):
            where_clauses = [
                f"timestamptz < '{timestamptz_values[0]}'",
                f"timestamptz > '{timestamptz_values[-1]}' + interval 1 day",
                f"timestamptz = '{timestamptz_values[-1]}' + interval 1 day",
                f"timestamptz = '{timestamptz_values[0]}' - interval 1 day",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with long column"):
        with By(
            """define several where clauses: with long < min index, with long > max index, 
            with long = value > max index, with long = value < min index"""
        ):
            where_clauses = [
                f"long < {long_values[0]}",
                f"long > {long_values[-1]}",
                f"long = {long_values[-1]+1}",
                f"long = {long_values[0]-1}",
            ]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )

    with And("check predicate push down with fixed column"):
        with By(
            "define two where clauses: one with fixed = value > max index and the other with fixed > max index"
        ):
            where_clauses = [f"fixed = 'b\0'", f"fixed > 'b\0'"]

        check_predicate_pushdown_clauses(
            where_clauses, read_with_pruning, read_without_pruning, length
        )


@TestScenario
def issue_with_decimal_column(self, minio_root_user, minio_root_password):
    """Regression test for predicate pushdown behavior on decimal column."""
    table_name = f"table_{getuid()}"
    namespace = f"namespace_{getuid()}"
    database_name = f"database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create table"):
        iceberg_schema = Schema(
            NestedField(field_id=1, name="decimal", field_type=DecimalType(9, 2)),
        )
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=iceberg_schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("insert decimal data into table"):
        length = 10
        decimal_values = [Decimal(i + 0.5) for i in range(length)]
        data = [{"decimal": decimal_values[i]} for i in range(length)]
        arrow_schema = pa.schema(
            [("decimal", pa.decimal128(9, 2))],
        )
        df = pa.Table.from_pylist(data, schema=arrow_schema)
        table.append(df)

    with And("create Iceberg database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then("check predicate push down with decimal column"):
        with By("define where clauses"):
            where_clauses = [
                f"decimal < 0.5",
                f"decimal > 10.5",
            ]
        for where_clause in where_clauses:
            check_read_with_predicate_push_down(
                where_clause=where_clause,
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
            )

        for where_clause in where_clauses:
            check_read_without_predicate_push_down(
                where_clause=where_clause,
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                length=length,
            )


@TestScenario
def issue_with_float_column(self, minio_root_user, minio_root_password):
    """Regression test for predicate pushdown behavior on float column."""
    table_name = f"table_{getuid()}"
    namespace = f"namespace_{getuid()}"
    database_name = f"database_{getuid()}"

    with Given("create catalog and namespace"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And("create table"):
        iceberg_schema = Schema(
            NestedField(field_id=1, name="float", field_type=FloatType()),
        )
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=iceberg_schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
        )

    with And("insert float data into table"):
        length = 10
        float_values = [float(i + 0.5) for i in range(length)]
        data = [{"float": float_values[i]} for i in range(length)]
        arrow_schema = pa.schema(
            [("float", pa.float32())],
        )
        df = pa.Table.from_pylist(data, schema=arrow_schema)
        table.append(df)

    with And("create Iceberg database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with Then("check predicate push down with float column"):
        with By("define where clauses"):
            where_clauses = [
                f"float < 0.5",
                f"float > 10.5",
            ]
        for where_clause in where_clauses:
            check_read_with_predicate_push_down(
                where_clause=where_clause,
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
            )

        for where_clause in where_clauses:
            check_read_without_predicate_push_down(
                where_clause=where_clause,
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                length=length,
            )


@TestFeature
@Name("predicate push down")
def feature(self, minio_root_user, minio_root_password):
    """Check that input_format_parquet_filter_push_down works correctly for different data types."""
    Scenario(test=check_input_format_parquet_filter_push_down)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=issue_with_decimal_column)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=issue_with_float_column)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

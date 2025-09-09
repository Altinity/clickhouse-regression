import pyarrow as pa

from testflows.core import *
from testflows.asserts import error
from datetime import datetime, timedelta, date

from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    TimestampType,
    StringType,
    IntegerType,
    BooleanType,
    DateType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder, SortField, SortDirection, NullOrder
from pyiceberg.transforms import (
    IdentityTransform,
    MonthTransform,
    TruncateTransform,
    DayTransform,
)

from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build

import iceberg.tests.steps.common as common
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.icebergS3 as icebergS3


@TestScenario
def check_iceberg_partition_pruning_with_integer_type(
    self, minio_root_user, minio_root_password, node=None
):
    """Check that iceberg partition pruning works with integer type."""
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

    with And("define table schema with three columns: string, boolean, integer"):
        schema = Schema(
            NestedField(
                field_id=1, name="string", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="boolean", field_type=BooleanType(), required=False
            ),
            NestedField(
                field_id=3, name="integer", field_type=IntegerType(), required=False
            ),
        )

    with When("partition table by integer column with identity transform"):
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=3,
                field_id=1001,
                transform=IdentityTransform(),
                name="integer_partition",
            ),
        )

    with And("create iceberg table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=SortOrder(),
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("insert data into iceberg table"):
        length = 20
        string_values = [str(i) for i in range(length)]
        boolean_values = [True if i % 2 == 0 else False for i in range(length)]
        integer_values = [i for i in range(length)]
        rows = [
            f"{string_values[i]}\t{str(boolean_values[i]).lower()}\t{integer_values[i]}"
            for i in range(length)
        ]
        data = [
            {
                "string": string_values[i],
                "boolean": boolean_values[i],
                "integer": integer_values[i],
            }
            for i in range(length)
        ]
        schema = pa.schema(
            [
                ("string", pa.string()),
                ("boolean", pa.bool_()),
                ("integer", pa.int32()),
            ]
        )
        df = pa.Table.from_pylist(data, schema=schema)
        table.append(df)

    with And("read data from ClickHouse with partition pruning enabled"):
        for i in range(length):
            with By("drop all caches"):
                common.drop_all_caches(node=node)

            with And("define `where` clause on integer column"):
                where_clause = f"integer >= {i}"

            with And("select with `where` clause on integer column"):
                log_comment_with_partition_pruning = (
                    f"with_partition_pruning_{i}_{getuid()}"
                )
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    where_clause=where_clause,
                    order_by="integer",
                    log_comment=log_comment_with_partition_pruning,
                    input_format_parquet_filter_push_down="0",
                    use_iceberg_metadata_files_cache="0",
                    use_cache_for_count_from_files="0",
                    use_iceberg_partition_pruning="1",
                )

            with And("check that output is correct"):
                assert result.output.strip() == "\n".join(rows[i:]), error()

            with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
                partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
                    log_comment=log_comment_with_partition_pruning,
                ).output.strip()
                assert int(partition_pruned_files) == i, error()

            with And("check that S3ReadRequestsCount is correct"):
                # 2 requests for each row: one for metadata and one for data
                # 3-5 requests for metadata files
                s3_read_requests_count = metrics.get_S3ReadRequestsCount(
                    log_comment=log_comment_with_partition_pruning,
                ).output.strip()
                min_count = 2 * (length - i) + 3
                max_count = 2 * (length - i) + 10
                assert min_count <= int(s3_read_requests_count), error()
                assert int(s3_read_requests_count) <= max_count, error()

    with And("read data from ClickHouse with partition pruning disabled"):
        for i in range(length):
            with By("drop all caches"):
                common.drop_all_caches(node=node)

            with And("define `where` clause on integer column"):
                where_clause = f"integer >= {i}"

            with And("select with `where` clause on integer column"):
                log_comment_without_partition_pruning = (
                    f"without_partition_pruning_{i}_{getuid()}"
                )
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    where_clause=where_clause,
                    order_by="integer",
                    log_comment=log_comment_without_partition_pruning,
                    input_format_parquet_filter_push_down="0",
                    use_iceberg_metadata_files_cache="0",
                    use_cache_for_count_from_files="0",
                    use_iceberg_partition_pruning="0",
                )

            with And("check that output is correct"):
                assert result.output.strip() == "\n".join(rows[i:]), error()

            with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
                partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
                    log_comment=log_comment_without_partition_pruning,
                ).output.strip()
                assert int(partition_pruned_files) == 0, error()

            with And("check that S3ReadRequestsCount is correct"):
                s3_read_requests_count = metrics.get_S3ReadRequestsCount(
                    log_comment=log_comment_without_partition_pruning,
                ).output.strip()
                min_count = 2 * length + 3
                max_count = 2 * length + 10
                assert min_count <= int(s3_read_requests_count), error()
                assert int(s3_read_requests_count) <= max_count, error()


@TestScenario
def check_partition_pruning_with_complex_where_clause(
    self, minio_root_user, minio_root_password
):
    """Check that Iceberg partition pruning works when selecting from an Iceberg
    table with a complex WHERE clause that includes multiple columns.
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

    with And(
        "define table schema with four columns: string, boolean, integer, datetime"
    ):
        schema = Schema(
            NestedField(
                field_id=1, name="string", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="boolean", field_type=BooleanType(), required=False
            ),
            NestedField(
                field_id=3, name="integer", field_type=IntegerType(), required=False
            ),
            NestedField(
                field_id=4, name="datetime", field_type=TimestampType(), required=False
            ),
        )

    with When(
        "partition table by string, boolean, integer and datetime columns with different transforms"
    ):
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=1,
                field_id=1001,
                transform=TruncateTransform(1),
                name="string_partition",
            ),
            PartitionField(
                source_id=2,
                field_id=1002,
                transform=IdentityTransform(),
                name="boolean_partition",
            ),
            PartitionField(
                source_id=3,
                field_id=1003,
                transform=IdentityTransform(),
                name="integer_partition",
            ),
            PartitionField(
                source_id=4,
                field_id=1004,
                transform=MonthTransform(),
                name="datetime_partition",
            ),
        )

    with And("create iceberg table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=SortOrder(),
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("insert data into iceberg table"):
        length = 100
        string_values = [str(i) for i in range(length)]
        boolean_values = [True if i % 2 == 0 else False for i in range(length)]
        integer_values = [i for i in range(length)]
        datetime_values = [
            datetime(2024, 1, 1) - timedelta(days=i * 35) for i in range(length)
        ]

        data = [
            {
                "string": string_values[i],
                "boolean": boolean_values[i],
                "integer": integer_values[i],
                "datetime": datetime_values[i],
            }
            for i in range(length)
        ]
        schema = pa.schema(
            [
                ("string", pa.string()),
                ("boolean", pa.bool_()),
                ("integer", pa.int32()),
                ("datetime", pa.timestamp("us")),
            ]
        )
        df = pa.Table.from_pylist(data, schema=schema)
        table.append(df)

    with And("define complex `where` clause and expectation for output"):
        where_clause = (
            "string > '1' AND boolean = true AND integer > 5 AND toMonth(datetime) = 1"
        )
        expected_output = (
            "10	true	10	2023-01-16 01:00:00.000000\n"
            "20	true	20	2022-01-31 01:00:00.000000\n"
            "52	true	52	2019-01-07 01:00:00.000000\n"
            "62	true	62	2018-01-22 01:00:00.000000"
        )

    with And("read data from ClickHouse with partition pruning enabled"):
        log_comment_with_partition_pruning = f"with_partition_pruning_{getuid()}"
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            where_clause=where_clause,
            order_by="tuple(*)",
            use_iceberg_partition_pruning="1",
            input_format_parquet_filter_push_down="0",
            use_iceberg_metadata_files_cache="0",
            use_cache_for_count_from_files="0",
            log_comment=log_comment_with_partition_pruning,
        )
        assert result.output.strip() == expected_output, error()

    with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
        partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
            log_comment=log_comment_with_partition_pruning,
        ).output.strip()
        assert int(partition_pruned_files) == 53, error()

    with And("check IcebergMinMaxIndexPrunedFiles from ProfileEvents"):
        min_max_pruned_files = metrics.get_IcebergMinMaxIndexPrunedFiles(
            log_comment=log_comment_with_partition_pruning,
        ).output.strip()
        if check_clickhouse_version(">=25.4")(self):
            assert int(min_max_pruned_files) == 43, error()

    with And("check that S3ReadRequestsCount is correct"):
        s3_read_requests_count = metrics.get_S3ReadRequestsCount(
            log_comment=log_comment_with_partition_pruning,
        ).output.strip()
        if check_clickhouse_version(">=25.4")(self) or check_if_antalya_build(self):

            assert 10 <= int(s3_read_requests_count), error()
            assert int(s3_read_requests_count) <= 18, error()
        else:
            assert 95 <= int(s3_read_requests_count), error()
            assert int(s3_read_requests_count) <= 100, error()

    with And("read data from ClickHouse with partition pruning disabled"):
        log_comment_without_partition_pruning = f"without_partition_pruning_{getuid()}"
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            where_clause=where_clause,
            order_by="tuple(*)",
            use_iceberg_partition_pruning="0",
            input_format_parquet_filter_push_down="0",
            use_iceberg_metadata_files_cache="0",
            use_cache_for_count_from_files="0",
            log_comment=log_comment_without_partition_pruning,
        )
        assert result.output.strip() == expected_output, error()

    with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
        partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
            log_comment=log_comment_without_partition_pruning,
        ).output.strip()
        assert int(partition_pruned_files) == 0, error()

    with And("check that S3ReadRequestsCount is correct"):
        s3_read_requests_count = metrics.get_S3ReadRequestsCount(
            log_comment=log_comment_without_partition_pruning,
        ).output.strip()
        assert 200 <= int(s3_read_requests_count), error()
        assert int(s3_read_requests_count) <= 210, error()


@TestScenario
def partition_pruning_with_date_type(self, minio_root_user, minio_root_password):
    """Check that Iceberg partition pruning works when selecting from an Iceberg
    table with a date type column.
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

    with And("define table schema with two columns: string, date"):
        schema = Schema(
            NestedField(
                field_id=1, name="string", field_type=StringType(), required=False
            ),
            NestedField(field_id=2, name="date", field_type=DateType(), required=False),
        )

    with When("partition table by date column with month transform"):
        partition_spec = PartitionSpec(
            PartitionField(
                source_id=2,
                field_id=1001,
                transform=DayTransform(),
                name="date_month_partition",
            ),
        )

    with And("create iceberg table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=partition_spec,
            sort_order=SortOrder(),
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("insert data into iceberg table"):
        length = 100
        string_values = [str(i) for i in range(length)]
        date_values = [date(2024, 1, 1) + timedelta(days=i) for i in range(length)]

        data = [
            {
                "string": string_values[i],
                "date": date_values[i],
            }
            for i in range(length)
        ]
        schema = pa.schema(
            [
                ("string", pa.string()),
                ("date", pa.date32()),
            ]
        )
        df = pa.Table.from_pylist(data, schema=schema)
        table.append(df)

    with And("read data from ClickHouse with partition pruning enabled"):
        log_comment_with_partition_pruning = f"with_partition_pruning_{getuid()}"
        result_with_partition_pruning = (
            iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                where_clause="date >= '2024-02-03'",
                order_by="date, string",
                use_iceberg_partition_pruning="1",
                input_format_parquet_filter_push_down="0",
                use_iceberg_metadata_files_cache="0",
                use_cache_for_count_from_files="0",
                log_comment=log_comment_with_partition_pruning,
            )
        )

    with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
        partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
            log_comment=log_comment_with_partition_pruning,
        ).output.strip()
        assert int(partition_pruned_files) == 33, error()

    with And("check IcebergMinMaxIndexPrunedFiles from ProfileEvents"):
        min_max_pruned_files = metrics.get_IcebergMinMaxIndexPrunedFiles(
            log_comment=log_comment_with_partition_pruning,
        ).output.strip()
        if check_clickhouse_version(">=25.4")(self):
            assert int(min_max_pruned_files) == 0, error()

    with And("check that S3ReadRequestsCount is correct"):
        s3_read_requests_count = metrics.get_S3ReadRequestsCount(
            log_comment=log_comment_with_partition_pruning,
        ).output.strip()
        if check_clickhouse_version(">=25.4")(self) or check_if_antalya_build(self):

            assert 137 <= int(s3_read_requests_count), error()
            assert int(s3_read_requests_count) <= 142, error()
        else:
            assert 200 <= int(s3_read_requests_count), error()
            assert int(s3_read_requests_count) <= 210, error()

    with And("read data from ClickHouse with partition pruning disabled"):
        log_comment_without_partition_pruning = f"without_partition_pruning_{getuid()}"
        result_without_partition_pruning = (
            iceberg_engine.read_data_from_clickhouse_iceberg_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                where_clause="date >= '2024-02-03'",
                order_by="date, string",
                use_iceberg_partition_pruning="0",
                input_format_parquet_filter_push_down="0",
                use_iceberg_metadata_files_cache="0",
                use_cache_for_count_from_files="0",
                log_comment=log_comment_without_partition_pruning,
            )
        )
        assert (
            result_without_partition_pruning.output.strip()
            == result_with_partition_pruning.output.strip()
        ), error()

    with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
        partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
            log_comment=log_comment_without_partition_pruning,
        ).output.strip()
        assert int(partition_pruned_files) == 0, error()

    with And("check that S3ReadRequestsCount is correct"):
        s3_read_requests_count = metrics.get_S3ReadRequestsCount(
            log_comment=log_comment_without_partition_pruning,
        ).output.strip()
        assert 200 <= int(s3_read_requests_count), error()
        assert int(s3_read_requests_count) <= 210, error()


@TestScenario
def non_partitioned_table(self, minio_root_user, minio_root_password):
    """Check that iceberg partition pruning does not affect non-partitioned tables."""
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

    with And(
        "define table schema with five columns: string, boolean, integer, date, datetime"
    ):
        schema = Schema(
            NestedField(
                field_id=1, name="string", field_type=StringType(), required=False
            ),
            NestedField(
                field_id=2, name="boolean", field_type=BooleanType(), required=False
            ),
            NestedField(
                field_id=3, name="integer", field_type=IntegerType(), required=False
            ),
            NestedField(field_id=4, name="date", field_type=DateType(), required=False),
            NestedField(
                field_id=5, name="datetime", field_type=TimestampType(), required=False
            ),
        )

    with And("create non-partitioned table"):
        sort_order = SortOrder(
            SortField(
                source_id=1,  # string column
                transform=IdentityTransform(),
                direction=SortDirection.ASC,
                null_order=NullOrder.NULLS_FIRST,
            )
        )
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location="s3://warehouse/data",
            partition_spec=PartitionSpec(),
            sort_order=sort_order,
        )

    with And("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("insert data into iceberg table"):
        length = 20
        string_values = [str(i) for i in range(length)]
        boolean_values = [True if i % 2 == 0 else False for i in range(length)]
        integer_values = [i for i in range(length)]
        date_values = [date(2024, 1, 1) + timedelta(days=i) for i in range(length)]
        datetime_values = [
            datetime(2024, 1, 1) + timedelta(days=i) for i in range(length)
        ]
        data = [
            {
                "string": string_values[i],
                "boolean": boolean_values[i],
                "integer": integer_values[i],
                "date": date_values[i],
                "datetime": datetime_values[i],
            }
            for i in range(length)
        ]
        schema = pa.schema(
            [
                ("string", pa.string()),
                ("boolean", pa.bool_()),
                ("integer", pa.int32()),
                ("date", pa.date32()),
                ("datetime", pa.timestamp("us")),
            ]
        )
        df = pa.Table.from_pylist(data, schema=schema)
        table.append(df)

    with When("define various `where` clauses"):
        where_clauses = [
            "string > '1'",
            "boolean = true",
            "integer = 1",
            "integer < 5",
            "date >= '2024-01-05'",
            "integer > 5",
            "date >= '2024-01-01' AND date < '2024-02-01'",
            "datetime >= '2024-01-01 00:00:00'",
            "string > '1' AND boolean = true",
            "boolean = true AND integer < 15",
            "datetime <= '2024-01-01 00:00:00'",
            "string < '1' AND boolean = true",
            "integer > 1 AND date >= '2024-01-01'",
            "datetime >= '2024-01-01 00:00:00' AND date >= '2024-01-01'",
            "string > '1' AND boolean = true AND integer > 1",
            "date >= '2024-02-02' AND datetime >= '2024-01-01 00:00:00'",
            "datetime <= '2025-01-01 00:00:00' AND date >= '2024-01-02'",
        ]

    with And(
        "compare select results when use_iceberg_partition_pruning setting is 0 or 1"
    ):
        for where_clause in where_clauses:
            result_with_partition_pruning = (
                iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    where_clause=where_clause,
                    order_by="tuple(*)",
                    use_iceberg_partition_pruning="1",
                    input_format_parquet_filter_push_down="0",
                    use_iceberg_metadata_files_cache="0",
                    use_cache_for_count_from_files="0",
                ).output.strip()
            )
            result_without_partition_pruning = (
                iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    where_clause=where_clause,
                    order_by="tuple(*)",
                    use_iceberg_partition_pruning="0",
                    input_format_parquet_filter_push_down="0",
                    use_iceberg_metadata_files_cache="0",
                    use_cache_for_count_from_files="0",
                ).output.strip()
            )
            result_with_s3_table_function = (
                icebergS3.read_data_with_icebergS3_table_function(
                    storage_endpoint="http://minio:9000/warehouse/data",
                    s3_access_key_id=minio_root_user,
                    s3_secret_access_key=minio_root_password,
                    order_by="tuple(*)",
                    where_clause=where_clause,
                ).output.strip()
            )
            assert (
                result_with_partition_pruning == result_without_partition_pruning
            ), error("result with and without partition pruning are not equal")
            assert (
                result_with_partition_pruning == result_with_s3_table_function
            ), error(
                "result with icebergS3 table function and with DataLakeCatalog are not equal"
            )


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Check that iceberg partition pruning works when selecting from table from iceberg engine."""
    Scenario(test=check_iceberg_partition_pruning_with_integer_type)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=check_partition_pruning_with_complex_where_clause)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=partition_pruning_with_date_type)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=non_partitioned_table)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

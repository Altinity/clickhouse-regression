import pyarrow as pa

from testflows.core import *
from testflows.asserts import error
from datetime import datetime, timedelta

from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import (
    TimestampType,
    StringType,
    IntegerType,
    BooleanType,
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.table.sorting import SortOrder
from pyiceberg.transforms import (
    IdentityTransform,
    MonthTransform,
    TruncateTransform,
)

from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build

import iceberg.tests.steps.common as common
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


@TestScenario
def check_iceberg_partition_pruning_with_integer_type(
    self, minio_root_user, minio_root_password, node=None
):
    """Check that iceberg partition pruning works with integer type."""
    if node is None:
        node = self.context.node

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

    with And("create DatalakeCatalog database"):
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

            with And("select with where clause on integer column"):
                log_comment_with_partition_pruning = (
                    f"with_partition_pruning_{i}_{getuid()}"
                )
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    where_clause=f"integer >= {i}",
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
                )
                assert int(partition_pruned_files.output.strip()) == i, error()

            with And("check that S3ReadRequestsCount is correct"):
                # 2 requests for each row: one for metadata and one for data
                # 3-5 requests for metadata files
                s3_read_requests_count = metrics.get_S3ReadRequestsCount(
                    log_comment=log_comment_with_partition_pruning,
                )
                assert (
                    2 * (length - i) + 3
                    <= int(s3_read_requests_count.output.strip())
                    <= 2 * (length - i) + 5
                ), error()

    with And("read data from ClickHouse with partition pruning disabled"):
        for i in range(length):
            with By("drop all caches"):
                common.drop_all_caches(node=node)

            with And("select with where clause on integer column"):
                log_comment_without_partition_pruning = (
                    f"without_partition_pruning_{i}_{getuid()}"
                )
                result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    where_clause=f"integer >= {i}",
                    order_by="integer",
                    log_comment=log_comment_without_partition_pruning,
                    input_format_parquet_filter_push_down="0",
                    use_iceberg_metadata_files_cache="0",
                    use_cache_for_count_from_files="0",
                    use_iceberg_partition_pruning="0",
                )

            with And("check that output is correct"):
                assert result.output.strip() == "\n".join(rows[i:]), error()

            with And("check iceberg_partition_pruned_files from ProfileEvents"):
                partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
                    log_comment=log_comment_without_partition_pruning,
                )
                assert int(partition_pruned_files.output.strip()) == 0, error()

            with And(
                "check that all data files were requested without partition pruning"
            ):
                s3_read_requests_count = metrics.get_S3ReadRequestsCount(
                    log_comment=log_comment_without_partition_pruning,
                )
                assert (
                    2 * length + 3
                    <= int(s3_read_requests_count.output.strip())
                    <= 2 * length + 5
                ), error()


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

    with And("create DatalakeCatalog database"):
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

    with And("read data from ClickHouse with partition pruning enabled"):
        log_comment_with_partition_pruning = f"with_partition_pruning_{getuid()}"
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            where_clause="string > '1' AND boolean = true AND integer > 5 AND toMonth(datetime) = 1",
            order_by="tuple(*)",
            use_iceberg_partition_pruning="1",
            input_format_parquet_filter_push_down="0",
            use_iceberg_metadata_files_cache="0",
            use_cache_for_count_from_files="0",
            log_comment=log_comment_with_partition_pruning,
        )
        assert (
            result.output.strip()
            == "10	true	10	2023-01-16 01:00:00.000000\n20	true	20	2022-01-31 01:00:00.000000\n52	true	52	2019-01-07 01:00:00.000000\n62	true	62	2018-01-22 01:00:00.000000"
        ), error()

    with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
        partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
            log_comment=log_comment_with_partition_pruning,
        )
        assert int(partition_pruned_files.output.strip()) == 53, error()

    with And("check IcebergMinMaxIndexPrunedFiles from ProfileEvents"):
        min_max_pruned_files = metrics.get_IcebergMinMaxIndexPrunedFiles(
            log_comment=log_comment_with_partition_pruning,
        )
        if check_clickhouse_version(">=25.4")(self):
            assert int(min_max_pruned_files.output.strip()) == 43, error()

    with And("check that S3ReadRequestsCount is correct"):
        s3_read_requests_count = metrics.get_S3ReadRequestsCount(
            log_comment=log_comment_with_partition_pruning,
        )
        if check_clickhouse_version(">=25.4")(self) or check_if_antalya_build(self):
            assert 10 <= int(s3_read_requests_count.output.strip()) <= 16, error()
        else:
            assert 95 <= int(s3_read_requests_count.output.strip()) <= 100, error()

    with And("read data from ClickHouse with partition pruning disabled"):
        log_comment_without_partition_pruning = f"without_partition_pruning_{getuid()}"
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            where_clause="string > '1' AND boolean = true AND integer > 5 AND toMonth(datetime) = 1",
            order_by="tuple(*)",
            use_iceberg_partition_pruning="0",
            input_format_parquet_filter_push_down="0",
            use_iceberg_metadata_files_cache="0",
            use_cache_for_count_from_files="0",
            log_comment=log_comment_without_partition_pruning,
        )
        assert (
            result.output.strip()
            == "10	true	10	2023-01-16 01:00:00.000000\n20	true	20	2022-01-31 01:00:00.000000\n52	true	52	2019-01-07 01:00:00.000000\n62	true	62	2018-01-22 01:00:00.000000"
        ), error()

    with And("check IcebergPartitionPrunedFiles from ProfileEvents"):
        partition_pruned_files = metrics.get_IcebergPartitionPrunedFiles(
            log_comment=log_comment_without_partition_pruning,
        )
        assert int(partition_pruned_files.output.strip()) == 0, error()

    with And("check that S3ReadRequestsCount is correct"):
        s3_read_requests_count = metrics.get_S3ReadRequestsCount(
            log_comment=log_comment_without_partition_pruning,
        )
        assert 200 <= int(s3_read_requests_count.output.strip()) <= 210, error()


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Check that iceberg partition pruning works when selecting from table from iceberg engine."""
    Scenario(test=check_iceberg_partition_pruning_with_integer_type)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=check_partition_pruning_with_complex_where_clause)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )

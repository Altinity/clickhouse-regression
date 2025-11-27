import time
import random

from testflows.core import *
from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build


@TestStep(Then)
def read_data_with_icebergS3_table_function(
    self,
    s3_access_key_id,
    s3_secret_access_key,
    storage_endpoint="http://minio:9000/warehouse/data",
    node=None,
    columns="*",
    where_clause=None,
    order_by=None,
    group_by=None,
    user=None,
    password=None,
    log_comment=None,
    exitcode=None,
    message=None,
    input_format_parquet_filter_push_down=None,
    use_iceberg_partition_pruning=None,
    use_iceberg_metadata_files_cache=None,
    use_cache_for_count_from_files=None,
    input_format_parquet_bloom_filter_push_down=None,
    format="TabSeparated",
    object_storage_cluster=None,
    iceberg_metadata_table_uuid=None,
):
    """Read Iceberg tables from S3 using the icebergS3(iceberg) table function."""
    if node is None:
        node = self.context.node

    settings = []

    if user:
        settings.append(("user", user))

    if password:
        settings.append(("password", f"{password}"))

    if log_comment:
        settings.append(("log_comment", f"{log_comment}"))

    if input_format_parquet_filter_push_down:
        settings.append(
            (
                "input_format_parquet_filter_push_down",
                f"{input_format_parquet_filter_push_down}",
            )
        )

    if use_iceberg_partition_pruning:
        settings.append(
            (
                "use_iceberg_partition_pruning",
                f"{use_iceberg_partition_pruning}",
            )
        )

    if use_iceberg_metadata_files_cache and (
        check_clickhouse_version(">=25.4")(self) or check_if_antalya_build(self)
    ):
        settings.append(
            (
                "use_iceberg_metadata_files_cache",
                use_iceberg_metadata_files_cache,
            )
        )

    if use_cache_for_count_from_files:
        settings.append(
            (
                "use_cache_for_count_from_files",
                f"{use_cache_for_count_from_files}",
            )
        )

    if input_format_parquet_bloom_filter_push_down:
        settings.append(
            (
                "input_format_parquet_bloom_filter_push_down",
                f"{input_format_parquet_bloom_filter_push_down}",
            )
        )

    if object_storage_cluster:
        settings.append(("object_storage_cluster", object_storage_cluster))

    if check_clickhouse_version(">=24.9")(self):
        function_name = random.choice(["iceberg", "icebergS3"])
    else:
        function_name = "iceberg"

    if iceberg_metadata_table_uuid:
        query = f"""
            SELECT {columns} 
            FROM {function_name}('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}', SETTINGS iceberg_metadata_table_uuid = '{iceberg_metadata_table_uuid}')
            """
    else:
        query = f"""
            SELECT {columns} 
            FROM {function_name}('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}')
            """

    if where_clause:
        query += f" WHERE {where_clause}"

    if group_by:
        query += f" GROUP BY {group_by}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if format:
        query += f" FORMAT {format}"

    result = node.query(
        query,
        settings=settings,
        exitcode=exitcode,
        message=message,
    )
    return result


@TestStep(Then)
def read_data_with_icebergS3Cluster_table_function(
    self,
    cluster_name,
    s3_access_key_id,
    s3_secret_access_key,
    storage_endpoint="http://minio:9000/warehouse/data",
    node=None,
    columns="*",
    where_clause=None,
    order_by=None,
    group_by=None,
    user=None,
    password=None,
    log_comment=None,
    exitcode=None,
    message=None,
    input_format_parquet_filter_push_down=None,
    use_iceberg_partition_pruning=None,
    use_iceberg_metadata_files_cache=None,
    use_cache_for_count_from_files=None,
    input_format_parquet_bloom_filter_push_down=None,
    format="TabSeparated",
    iceberg_metadata_table_uuid=None,
):
    """Read Iceberg tables from S3 using the icebergS3 table function."""
    if node is None:
        node = self.context.node

    settings = []

    if user:
        settings.append(("user", user))

    if password:
        settings.append(("password", f"{password}"))

    if log_comment:
        settings.append(("log_comment", f"{log_comment}"))

    if input_format_parquet_filter_push_down:
        settings.append(
            (
                "input_format_parquet_filter_push_down",
                f"{input_format_parquet_filter_push_down}",
            )
        )

    if use_iceberg_partition_pruning:
        settings.append(
            (
                "use_iceberg_partition_pruning",
                f"{use_iceberg_partition_pruning}",
            )
        )

    if use_iceberg_metadata_files_cache and (
        check_clickhouse_version(">=25.4")(self) or check_if_antalya_build(self)
    ):
        settings.append(
            (
                "use_iceberg_metadata_files_cache",
                use_iceberg_metadata_files_cache,
            )
        )

    if use_cache_for_count_from_files:
        settings.append(
            (
                "use_cache_for_count_from_files",
                f"{use_cache_for_count_from_files}",
            )
        )

    if input_format_parquet_bloom_filter_push_down:
        settings.append(
            (
                "input_format_parquet_bloom_filter_push_down",
                f"{input_format_parquet_bloom_filter_push_down}",
            )
        )

    if iceberg_metadata_table_uuid:
        query = f"""
                SELECT {columns}
                FROM icebergS3Cluster(
                    '{cluster_name}',
                    '{storage_endpoint}',
                    '{s3_access_key_id}',
                    '{s3_secret_access_key}',
                    SETTINGS iceberg_metadata_table_uuid = '{iceberg_metadata_table_uuid}'
                )
            """
    else:
        query = f"""
                SELECT {columns}
                FROM icebergS3Cluster(
                    '{cluster_name}',
                    '{storage_endpoint}',
                    '{s3_access_key_id}',
                    '{s3_secret_access_key}'
                )
            """

    if where_clause:
        query += f" WHERE {where_clause}"

    if group_by:
        query += f" GROUP BY {group_by}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if format:
        query += f" FORMAT {format}"

    result = node.query(
        query,
        settings=settings,
        exitcode=exitcode,
        message=message,
    )
    return result


@TestStep(Then)
def read_parquet_data_with_icebergS3_table_function(
    self,
    storage_endpoint,
    s3_access_key_id,
    s3_secret_access_key,
    node=None,
    columns="*",
    cache_parquet_metadata=False,
    where_clause=None,
):
    """Read Iceberg tables from S3 using the icebergS3 table function.

    Args:
        storage_endpoint: S3 storage endpoint
        s3_access_key_id: S3 access key ID
        s3_secret_access_key: S3 secret access key
        node: ClickHouse node to execute query on
        columns: Columns to select (default: "*")
        cache_parquet_metadata: Whether to cache Parquet metadata
        where_clause: Optional WHERE clause to filter results
    """
    if node is None:
        node = self.context.node

    log_comment = "log_" + getuid()

    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1"

    if cache_parquet_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1,input_format_parquet_filter_push_down=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    start_time = time.time()

    query = f"SELECT {columns} FROM icebergS3('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}', Parquet)"

    if where_clause:
        query += f" WHERE {where_clause}"

    query += f" SETTINGS {settings}"

    node.query(query)

    execution_time = time.time() - start_time

    return execution_time, log_comment

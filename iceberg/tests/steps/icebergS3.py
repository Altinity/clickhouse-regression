import time
from testflows.core import *

from helpers.common import getuid


@TestStep(Then)
def read_data_with_icebergS3_table_function(
    self,
    storage_endpoint,
    s3_access_key_id,
    s3_secret_access_key,
    node=None,
    columns="*",
):
    """Read Iceberg tables from S3 using the icebergS3 table function."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM iceberg('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}')"
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
    log_comment=None,
):
    """Read Iceberg tables from S3 using the icebergS3 table function."""
    if node is None:
        node = self.context.node

    log_comment = "log_" + getuid()

    settings = f"optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}', use_hive_partitioning=1"

    if cache_parquet_metadata:
        settings += ", input_format_parquet_use_metadata_cache=1"
    else:
        settings += ", input_format_parquet_use_metadata_cache=0"

    start_time = time.time()

    node.query(
        f"SELECT {columns} FROM icebergS3('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}', Parquet) SETTINGS {settings}"
    )

    execution_time = time.time() - start_time

    return execution_time, log_comment

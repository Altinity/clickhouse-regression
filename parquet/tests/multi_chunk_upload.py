import os
import json

from testflows.core import *
from helpers.common import getuid, check_clickhouse_version
from parquet.requirements import *
from parquet.tests.steps.general import select_from_parquet
from parquet.performance.tests.datasets.ontime import create_table_with_ontime_dataset


@TestStep(Given)
def create_parquet_from_ontime_dataset(
    self,
    min_insert_block_size_rows,
    min_insert_block_size_bytes,
    output_format_parquet_row_group_size,
    output_format_parquet_row_group_size_bytes,
    output_format_parquet_parallel_encoding,
    max_threads,
    max_insert_block_size,
    max_block_size,
    threads=20,
    max_memory_usage=0,
):
    table_name = self.context.table_name
    parquet_file = "ontime_parquet_" + getuid() + ".parquet"

    node = self.context.node

    insert_into_parquet = (
        f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS "
        f"max_insert_threads = {threads}, max_memory_usage={max_memory_usage}, "
        f"min_insert_block_size_rows={min_insert_block_size_rows}, min_insert_block_size_bytes={min_insert_block_size_bytes}, "
        f"output_format_parquet_row_group_size={output_format_parquet_row_group_size}, "
        f"output_format_parquet_row_group_size_bytes={output_format_parquet_row_group_size_bytes}, "
        f"output_format_parquet_parallel_encoding={output_format_parquet_parallel_encoding}, "
        f"max_threads={max_threads}, "
        f"max_insert_block_size={max_insert_block_size}, "
        f"max_block_size={max_block_size}"
    )

    if check_clickhouse_version(">=23.3")(self):
        insert_into_parquet += f", output_format_parquet_compression_method='snappy'"

    node.query(
        insert_into_parquet,
        timeout=3600,
    )

    node.command(f"mv {parquet_file} /var/lib/clickhouse/user_files", exitcode=0)

    yield parquet_file
    node.command(f"rm /var/lib/clickhouse/user_files/{parquet_file}", exitcode=0)

@TestCheck
def multi_chunk_inserts(
    self,
    min_insert_block_size_rows,
    min_insert_block_size_bytes,
    output_format_parquet_row_group_size,
    output_format_parquet_row_group_size_bytes,
    output_format_parquet_parallel_encoding,
    max_threads,
    max_insert_block_size,
    max_block_size,
):
    """Check that the parquet file was created with the specified settings."""
    node = self.context.node

    with Given(
        "I create a parquet file from ontime dataset",
        description=f"min_insert_block_size_rows={min_insert_block_size_rows}, min_insert_block_size_bytes={min_insert_block_size_bytes}, output_format_parquet_row_group_size={output_format_parquet_row_group_size}, output_format_parquet_row_group_size_bytes={output_format_parquet_row_group_size_bytes}, output_format_parquet_parallel_encoding={output_format_parquet_parallel_encoding}, max_threads={max_threads}, max_insert_block_size={max_insert_block_size}, max_block_size={max_block_size}",
    ):
        parquet_file = create_parquet_from_ontime_dataset(
            min_insert_block_size_rows=min_insert_block_size_rows,
            min_insert_block_size_bytes=min_insert_block_size_bytes,
            output_format_parquet_row_group_size=output_format_parquet_row_group_size,
            output_format_parquet_row_group_size_bytes=output_format_parquet_row_group_size_bytes,
            output_format_parquet_parallel_encoding=output_format_parquet_parallel_encoding,
            max_threads=max_threads,
            max_insert_block_size=max_insert_block_size,
            max_block_size=max_block_size,
        )

    with Then("I select from the parquet file"):
        select_from_parquet(file_name=parquet_file, limit=1)



@TestSketch(Scenario)
def multi_chunk_upload(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file."""
    min_insert_block_size_rows = either(*[10000, 100000, 1000000])
    min_insert_block_size_bytes = either(*[10000000, 100000000, 1000000000])
    output_format_parquet_row_group_size = either(*[10000, 100000, 1000000])
    output_format_parquet_row_group_size_bytes = either(
        *[10000000, 100000000, 1000000000]
    )
    output_format_parquet_parallel_encoding = 1
    max_threads = either(*[2, 4, 8, 16, 32])
    max_insert_block_size = either(*[10000000, 100000000, 1000000000])
    max_block_size = either(*[15000000, 150000000, 1500000000])

    multi_chunk_inserts(
        min_insert_block_size_rows=min_insert_block_size_rows,
        min_insert_block_size_bytes=min_insert_block_size_bytes,
        output_format_parquet_row_group_size=output_format_parquet_row_group_size,
        output_format_parquet_row_group_size_bytes=output_format_parquet_row_group_size_bytes,
        output_format_parquet_parallel_encoding=output_format_parquet_parallel_encoding,
        max_threads=max_threads,
        max_insert_block_size=max_insert_block_size,
        max_block_size=max_block_size,
    )


@TestFeature
@Name("multi chunk upload")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Insert("1.0"))
def feature(self, node="clickhouse1"):
    """Validating multi chunked uploads into a parquet file."""
    self.context.node = self.context.cluster.node(node)

    with Given("I create a MergeTree table with the ontime dataset"):
        self.context.table_name = create_table_with_ontime_dataset()

    Scenario(run=multi_chunk_upload)
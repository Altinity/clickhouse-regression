from testflows.core import *
from helpers.common import getuid, check_clickhouse_version
from parquet.requirements import *
from parquet.tests.steps.general import select_from_parquet
from parquet.performance.tests.datasets.ontime import create_table_with_ontime_dataset


@TestStep(Given)
def move_parquet_to_user_files(self, file_name, node=None):
    """Move the parquet file to the user_files directory so that ClickHouse can read it."""

    if node is None:
        node = self.context.node

    node.command(f"mv {file_name} /var/lib/clickhouse/user_files", exitcode=0)


@TestStep(Then)
def remove_parquet_from_user_files(self, file_name, node=None):
    """Remove the parquet file from the user_files directory."""

    if node is None:
        node = self.context.node

    node.command(f"rm /var/lib/clickhouse/user_files/{file_name}", exitcode=0)


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
    """Create a parquet file from the MergeTree table with the ontime dataset."""
    table_name = self.context.table_name
    parquet_file = "ontime_" + getuid() + ".parquet"

    node = self.context.node

    insert_into_parquet = (
        f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS "
        # f"max_insert_threads = {threads}, max_memory_usage={max_memory_usage}, "
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

    move_parquet_to_user_files(file_name=parquet_file)

    yield parquet_file
    remove_parquet_from_user_files(file_name=parquet_file)


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
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Insert("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Settings_RowGroupSize("1.0"),
)
def multi_chunk_upload(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file

    To get a single large block ideally:

    the block should be less than `output_format_parquet_row_group_size * 2` but more than `output_format_parquet_row_group_size`.
    """

    min_insert_block_size_rows = either(*[0, 10000, 100000, 13000000, 130000000000])
    min_insert_block_size_bytes = either(*[0, 10000000, 100000000, 130000000000])
    output_format_parquet_row_group_size = either(*[0, 100000, 1000000, 100000000000])
    output_format_parquet_row_group_size_bytes = either(
        *[0, 10000000, 100000000, 1000000000]
    )
    output_format_parquet_parallel_encoding = 1
    max_threads = either(*[2, 4, 8, 16, 32])
    max_insert_block_size = either(*[0, 10000000, 100000000, 1000000000, 100000000000])
    max_block_size = either(*[0, 15000000, 20000000, 150000000, 150000000000])

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
def feature(self, node="clickhouse1", from_year=1987, to_year=2022):
    """Validating multi chunked uploads into a parquet file.

    The parameters: `from_year` and `to_year` determine the size of the dataset, the larger the range between two numbers, the larger the dataset.
    """
    self.context.node = self.context.cluster.node(node)

    with Given("I create a MergeTree table with the ontime dataset"):
        self.context.table_name = create_table_with_ontime_dataset(
            from_year=from_year, to_year=to_year
        )

    Scenario(run=multi_chunk_upload)

import random

from testflows.core import *
from testflows.combinatorics import product
from helpers.common import getuid, check_clickhouse_version
from parquet.requirements import *
from parquet.tests.steps.general import select_from_parquet
from parquet.performance.tests.datasets.ontime import create_table_with_ontime_dataset


@TestStep(Given)
def create_wide_dataset(self, table_name, node=None):

    if node is None:
        node = self.context.node

    node.query(
        f"""
        CREATE TABLE {table_name}
        ENGINE = MergeTree
        ORDER BY tuple()
        AS
        SELECT
            number AS id,
            repeat('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 1000) AS big_col
        FROM numbers(1000000);
    """
    )


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

    settings = [
        (
            f"min_insert_block_size_rows={min_insert_block_size_rows}"
            if min_insert_block_size_rows is not None
            else ""
        ),
        (
            f"min_insert_block_size_bytes={min_insert_block_size_bytes}"
            if min_insert_block_size_bytes is not None
            else ""
        ),
        (
            f"output_format_parquet_row_group_size={output_format_parquet_row_group_size}"
            if output_format_parquet_row_group_size is not None
            else ""
        ),
        (
            f"output_format_parquet_row_group_size_bytes={output_format_parquet_row_group_size_bytes}"
            if output_format_parquet_row_group_size_bytes is not None
            else ""
        ),
        (
            f"output_format_parquet_parallel_encoding={output_format_parquet_parallel_encoding}"
            if output_format_parquet_parallel_encoding is not None
            else ""
        ),
        f"max_threads={max_threads}" if max_threads is not None else "",
        (
            f"max_insert_block_size={max_insert_block_size}"
            if max_insert_block_size is not None
            else ""
        ),
        f"max_block_size={max_block_size}" if max_block_size is not None else "",
    ]

    settings = ", ".join(filter(None, settings))

    insert_into_parquet = f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS {settings}"

    if check_clickhouse_version(">=23.3")(self):
        insert_into_parquet += f", output_format_parquet_compression_method='snappy'"

    node.query(
        insert_into_parquet,
        timeout=3600,
    )

    move_parquet_to_user_files(file_name=parquet_file)

    yield parquet_file
    remove_parquet_from_user_files(file_name=parquet_file)


@TestOutline(Combination)
def multi_chunk_inserts(self, combination):
    """Check that the parquet file was created with the specified settings."""
    node = self.context.node
    (
        min_insert_block_size_rows,
        min_insert_block_size_bytes,
        output_format_parquet_row_group_size,
        output_format_parquet_row_group_size_bytes,
        output_format_parquet_parallel_encoding,
        max_threads,
        max_insert_block_size,
        max_block_size,
    ) = combination

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


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Insert("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Settings_RowGroupSize("1.0"),
)
def multi_chunk_upload(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file

    To get a single large block ideally:

    the block should be less than `output_format_parquet_row_group_size * 2` but more than `output_format_parquet_row_group_size`.
    """

    combinations = product(
        [0, 10000, 100000, 13000000, 130000000000],
        [0, 10000000, 100000000, 130000000000],
        [0, 100000, 1000000, 100000000000],
        [0, 10000000, 100000000, 1000000000, 100000000000],
        [1],
        [2, 4, 8, 16, 32],
        [0, 10000000, 100000000, 1000000000, 100000000000],
        [1, 15000000, 20000000, 150000000, 150000000000],
    )

    with Given("I execute combinations for multi chunk upload"):
        with Pool(4) as executor:
            for i, combination in enumerate(combinations):
                Scenario(
                    f"combination {i}",
                    test=multi_chunk_inserts,
                    parallel=True,
                    executor=executor,
                )(combination=combination)


@TestSketch(Scenario)
def max_block_size_and_group_size_bytes(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file.

    Variations of two settings: `max_block_size` and `min_insert_block_size_bytes`
    """
    max_block_size = random.sample(range(100000000001, 150000000001), 4)
    min_insert_block_size_bytes = random.sample(range(100000000001, 130000000001), 4)

    max_block_size = either(*max_block_size)
    min_insert_block_size_bytes = either(*min_insert_block_size_bytes)

    multi_chunk_inserts(
        max_block_size=max_block_size,
        min_insert_block_size_bytes=min_insert_block_size_bytes,
        output_format_parquet_parallel_encoding=1,
    )


@TestSketch(Scenario)
def output_format_parquet_row_group_size(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file.

    Variations of the `output_format_parquet_row_group_size` setting.
    """
    output_format_parquet_row_group_size = random.sample(
        range(100000001, 1000000001), 4
    )

    output_format_parquet_row_group_size = either(*output_format_parquet_row_group_size)

    multi_chunk_inserts(
        output_format_parquet_row_group_size=output_format_parquet_row_group_size,
        output_format_parquet_parallel_encoding=1,
    )


@TestSketch(Scenario)
def output_format_parquet_row_group_size_bytes(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file.

    Variations of the `output_format_parquet_row_group_size_bytes` setting.
    """
    output_format_parquet_row_group_size_bytes = random.sample(
        range(10000000001, 100000000001), 4
    )

    output_format_parquet_row_group_size_bytes = either(
        *output_format_parquet_row_group_size_bytes
    )

    multi_chunk_inserts(
        output_format_parquet_row_group_size_bytes=output_format_parquet_row_group_size_bytes,
        output_format_parquet_parallel_encoding=1,
    )


@TestSketch(Scenario)
def max_threads(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file.

    Variations of the `max_threads` setting.
    """
    max_threads = random.sample(range(2, 33), 4)

    max_threads = either(*max_threads)

    multi_chunk_inserts(
        max_threads=max_threads,
        output_format_parquet_parallel_encoding=1,
    )


@TestSketch
def max_insert_block_size(self):
    """Combinatorial checks with multiple settings that might affect the chunk size when exporting into a parquet file.

    Variations of the `max_insert_block_size` setting.
    """
    max_insert_block_size = random.sample(range(10000000001, 100000000001), 4)

    max_insert_block_size = either(*max_insert_block_size)

    multi_chunk_inserts(
        max_insert_block_size=max_insert_block_size,
        output_format_parquet_parallel_encoding=1,
    )


@TestFeature
@Name("multi chunk upload")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Insert("1.0"))
def feature(
    self,
    node="clickhouse1",
    from_year=1987,
    to_year=2022,
    ontime=False,
    all_combinations=True,
):
    """
    Validating multi chunked uploads into a parquet file.

    The parameters: `from_year` and `to_year` determine the size of the dataset, the larger the range between two numbers, the larger the dataset.
    create_wide_dataset creates a table with a single column that contains a large string.
    """
    self.context.node = self.context.cluster.node(node)
    wide_table = "wide_" + getuid()
    with Given("I create a MergeTree table with the ontime dataset"):
        if ontime:
            self.context.table_name = create_table_with_ontime_dataset(
                from_year=from_year, to_year=to_year, threads=40
            )
        else:
            create_wide_dataset(table_name=wide_table)
            self.context.table_name = wide_table

    if not all_combinations:
        Scenario(run=max_block_size_and_group_size_bytes)
        Scenario(run=output_format_parquet_row_group_size)
        Scenario(run=output_format_parquet_row_group_size_bytes)
        Scenario(run=max_threads)
        Scenario(run=max_insert_block_size)
    else:
        Scenario(run=multi_chunk_upload)

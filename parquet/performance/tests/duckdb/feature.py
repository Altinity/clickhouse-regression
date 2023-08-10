from testflows.core import *
from helpers.common import getuid
from parquet.performance.tests.datasets.ontime import create_parquet_files
from parquet.performance.tests.duckdb.steps import *


@TestSuite
def compare_clickhouse_vs_duckdb_performance(
    self, from_year, to_year, threads, max_memory_usage
):
    """Comparing the time it takes to read the large dataset in ClickHouse and duckdb"""

    clickhouse_node = self.context.clickhouse_node

    with Given("I generate a parquet file with large dataset"):
        parquet_file = create_parquet_files(
            from_year=from_year,
            to_year=to_year,
            threads=threads,
            max_memory_usage=max_memory_usage,
        )
        clickhouse_node.command(
            f"cp /var/lib/clickhouse/user_files/{parquet_file} /data1", exitcode=0
        )

    with When(
        "I run all the queries from the steps file in ClickHouse and DuckDB to read from the Parquet file with large ontime dataset"
    ):
        with By("Running the scenario which contains all the query steps"):
            queries(filename=parquet_file)


@TestFeature
@Name("clickhouse vs duckdb")
def feature(self, from_year, to_year, threads, max_memory_usage):
    """Compare parquet performance between single node clickhouse and duckdb"""
    Suite(test=compare_clickhouse_vs_duckdb_performance)(
        from_year=from_year,
        to_year=to_year,
        threads=threads,
        max_memory_usage=max_memory_usage,
    )

from testflows.core import *
from helpers.common import getuid
from parquet.performance.tests.datasets.ontime import create_parquet_file
from parquet.performance.tests.datasets.hits import create_parquet_file_hits
from parquet.performance.tests.duckdb.reports import (
    write_to_csv,
    create_bar_chart,
    convert_to_markdown,
)
from parquet.performance.tests.duckdb.steps import *
from parquet.performance.tests.duckdb.steps_hits import *


@TestSuite
def compare_clickhouse_vs_duckdb_performance(
    self, from_year, to_year, threads, max_memory_usage, compression
):
    """Comparing the time it takes to read the large dataset in ClickHouse and duckdb"""

    clickhouse_node = self.context.clickhouse_node

    with Given("I generate a parquet file with large dataset"):
        parquet_file = create_parquet_file(
            from_year=from_year,
            to_year=to_year,
            threads=threads,
            max_memory_usage=max_memory_usage,
            compression=compression,
        )
        clickhouse_node.command(
            f"cp /var/lib/clickhouse/user_files/{parquet_file} /data1", exitcode=0
        )

    with When(
        "I run all the queries from the steps file in ClickHouse and DuckDB to read from the Parquet file with large ontime dataset"
    ):
        with By("Running the scenario which contains all the query steps"):
            queries(filename=parquet_file)

    with Then("I export the test run results into a CSV file and generate charts"):
        write_to_csv(
            filename=f"results/ontime/{self.context.filename}",
            data=self.context.query_results,
            row_count=self.context.row_count[0],
            test_machine=self.context.test_machine,
            repeats=self.context.rerun_queries,
        )

        create_bar_chart(
            csv_file=f"results/ontime/{self.context.filename}",
            png_path="results/ontime/bar_chart.png",
        )

        convert_to_markdown(
            csv_file=f"results/ontime/{self.context.filename}",
            markdown_name="results/ontime/README.md",
            query=self.context.query_results,
        )


@TestSuite
def compare_clickhouse_vs_duckdb_performance_hits(
    self, first_number, last_number, threads, max_memory_usage, compression
):
    """Comparing the time it takes to read the large hits dataset in ClickHouse and duckdb"""

    clickhouse_node = self.context.clickhouse_node

    with Given("I generate a parquet file with large dataset"):
        parquet_file = create_parquet_file_hits(
            first_number=first_number,
            last_number=last_number,
            threads=threads,
            max_memory_usage=max_memory_usage,
            compression=compression,
        )
        clickhouse_node.command(
            f"cp /var/lib/clickhouse/user_files/{parquet_file} /data1", exitcode=0
        )

    with When(
        "I run all the queries from the steps file in ClickHouse and DuckDB to read from the Parquet file with large ontime dataset"
    ):
        with By("Running the scenario which contains all the query steps"):
            queries_hits(filename=parquet_file)

    with Then("I export the test run results into a CSV file and generate charts"):
        write_to_csv(
            filename=f"results/hits/performance_hits.csv",
            data=self.context.query_results_hits,
            row_count=self.context.row_count[0],
            test_machine=self.context.test_machine,
            repeats=self.context.rerun_queries,
        )

        create_bar_chart(
            csv_file=f"results/hits/performance_hits.csv",
            png_path="results/hits/bar_chart.png",
        )

        convert_to_markdown(
            csv_file=f"results/hits/performance_hits.csv",
            markdown_name="results/hits/README.md",
            query=self.context.query_results_hits,
        )


@TestFeature
@Name("clickhouse vs duckdb")
def feature(
    self,
    first_number,
    last_number,
    from_year,
    to_year,
    threads,
    hits,
    max_memory_usage,
    compression,
):
    """Compare parquet performance between single node clickhouse and duckdb"""
    if not hits:
        Suite(test=compare_clickhouse_vs_duckdb_performance)(
            from_year=from_year,
            to_year=to_year,
            threads=threads,
            max_memory_usage=max_memory_usage,
            compression=compression,
        )
    else:
        Suite(test=compare_clickhouse_vs_duckdb_performance_hits)(
            first_number=first_number,
            last_number=last_number,
            threads=threads,
            max_memory_usage=max_memory_usage,
            compression=compression,
        )

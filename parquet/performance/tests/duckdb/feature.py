from testflows.core import *
from helpers.common import getuid
from parquet.performance.tests.datasets.nyc_taxi import create_parquet_file_nyc_taxi
from parquet.performance.tests.datasets.ontime import create_parquet_file
from parquet.performance.tests.datasets.hits import create_parquet_file_hits
from parquet.performance.tests.duckdb.reports import (
    write_to_csv,
    create_bar_chart,
    convert_to_markdown,
    create_directory_if_not_exists,
)
from parquet.performance.tests.duckdb.steps import *
from parquet.performance.tests.duckdb.steps_hits import *
from parquet.performance.tests.duckdb.steps_nyc_taxi import queries_nyc_taxi


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
        path = f"results/ontime/{self.context.clickhouse_version}"

        create_directory_if_not_exists(path)

        write_to_csv(
            filename=f"{path}/{self.context.filename}",
            data=self.context.query_results,
            row_count=self.context.row_count[0],
            test_machine=self.context.test_machine,
            repeats=self.context.rerun_queries,
        )

        create_bar_chart(
            csv_file=f"{path}/{self.context.filename}",
            png_path=f"{path}/bar_chart.png",
        )

        convert_to_markdown(
            csv_file=f"{path}/{self.context.filename}",
            markdown_name=f"{path}/README.md",
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
        path = f"results/hits/{self.context.clickhouse_version}"

        create_directory_if_not_exists(path)

        write_to_csv(
            filename=f"{path}/performance_hits.csv",
            data=self.context.query_results,
            row_count=self.context.row_count[0],
            test_machine=self.context.test_machine,
            repeats=self.context.rerun_queries,
        )

        create_bar_chart(
            csv_file=f"{path}/performance_hits.csv",
            png_path=f"{path}/bar_chart.png",
        )

        convert_to_markdown(
            csv_file=f"{path}/performance_hits.csv",
            markdown_name=f"{path}/README.md",
            query=self.context.query_results,
        )


@TestSuite
def nyc_taxi(self, threads, max_memory_usage, compression):
    """Comparing the time it takes to read from the nyc taxi dataset in ClickHouse and duckdb"""

    clickhouse_node = self.context.clickhouse_node
    with Given("I generate a parquet file with large dataset"):
        parquet_file = create_parquet_file_nyc_taxi(
            threads=threads,
            max_memory_usage=max_memory_usage,
            compression=compression,
        )

        clickhouse_node.command(
            f"cp /var/lib/clickhouse/user_files/{parquet_file} /data1", exitcode=0
        )

    with When(
        "I run all the queries from the steps file in ClickHouse and DuckDB to read from the Parquet file with nyc taxi dataset"
    ):
        with By("Running the scenario which contains all the query steps"):
            queries_nyc_taxi(filename=parquet_file)

    with Then("I export the test run results into a CSV file and generate charts"):
        path = f"results/nyc_taxi/{self.context.clickhouse_version}"

        create_directory_if_not_exists(path)

        write_to_csv(
            filename=f"{path}/performance.csv",
            data=self.context.query_results,
            row_count=self.context.row_count[0],
            test_machine=self.context.test_machine,
            repeats=self.context.rerun_queries,
        )

        create_bar_chart(
            csv_file=f"{path}/performance.csv",
            png_path=f"{path}/bar_chart.png",
        )

        convert_to_markdown(
            csv_file=f"{path}/performance.csv",
            markdown_name=f"{path}/README.md",
            query=self.context.query_results,
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
    data,
    max_memory_usage,
    compression,
):
    """Compare parquet performance between single node clickhouse and duckdb"""
    if data == "ontime":
        Suite(test=compare_clickhouse_vs_duckdb_performance)(
            from_year=from_year,
            to_year=to_year,
            threads=threads,
            max_memory_usage=max_memory_usage,
            compression=compression,
        )
    elif data == "hits":
        Suite(test=compare_clickhouse_vs_duckdb_performance_hits)(
            first_number=first_number,
            last_number=last_number,
            threads=threads,
            max_memory_usage=max_memory_usage,
            compression=compression,
        )
    elif data == "nyc_taxi":
        Suite(test=nyc_taxi)(
            threads=threads, max_memory_usage=max_memory_usage, compression=compression
        )

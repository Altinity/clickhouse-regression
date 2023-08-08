from testflows.core import *
from helpers.common import getuid
from parquet.performance.tests.datasets.ontime import create_parquet_files
from parquet.performance.tests.duckdb.steps import *


@TestSuite
def compare_clickhouse_vs_duckdb_performance(self):
    """Comparing the time it takes to read the large dataset in ClickHouse and duckdb"""

    duckdb_node = self.context.duckdb_node
    clickhouse_node = self.context.clickhouse_node

    with Given("I generate a parquet file with large dataset"):
        parquet_file = create_parquet_files()

    with When(
        "I run all the queries from the steps file in ClickHouse to read from the Parquet file"
    ):
        with Step("Select * FROM file query") as clickhouse_query_all:
            query_all(filename=f"file('{parquet_file}')")
        with Step("Query 0") as clickhouse_query0:
            query_0(filename=f"file('{parquet_file}')")
        with Step("Query 1") as clickhouse_query1:
            query_1(filename=f"file('{parquet_file}')")

    with And(
        "I move the generated parquet file into shared data1 directory where DuckDB node can access it"
    ):
        clickhouse_node.command(
            f"mv /var/lib/clickhouse/user_files/{parquet_file} /data1", exitcode=0
        )
        parquet_file = f"/data1/{parquet_file}"

    with And(
        "I run all the queries from the steps file in duckdb to read from the Parquet file"
    ):
        with Step("Run query_all") as duckdb_query_all:
            query_all(filename=f'"{parquet_file}"', database="duckdb")
        with Step("Run query_0") as duckdb_query_0:
            query_0(filename=f'"{parquet_file}"', database="duckdb")
        with Step("Run query_1") as duckdb_query_1:
            query_1(filename=f'"{parquet_file}"', database="duckdb")

    with Then(
        "I get the runtime results of the ClickHouse and the DuckDB for each query"
    ):
        metric(
            name=f"ClickHouse query_all",
            value=current_time(test=clickhouse_query_all),
            units="s",
        )
        metric(
            name=f"ClickHouse query_0",
            value=current_time(test=clickhouse_query0),
            units="s",
        )
        metric(
            name=f"ClickHouse query_1",
            value=current_time(test=clickhouse_query1),
            units="s",
        )

        metric(
            name=f"DuckDB query_all",
            value=current_time(test=duckdb_query_all),
            units="s",
        )
        metric(
            name=f"DuckDB query_0", value=current_time(test=duckdb_query_0), units="s"
        )
        metric(
            name=f"DuckDB query_1", value=current_time(test=duckdb_query_1), units="s"
        )


@TestFeature
@Name("clickhouse vs duckdb")
def feature(self):
    """Compare parquet performance between single node clickhouse and duckdb"""
    Suite(run=compare_clickhouse_vs_duckdb_performance)

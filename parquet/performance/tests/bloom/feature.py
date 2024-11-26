import os
import json

from testflows.core import *
from helpers.common import getuid
from parquet.tests.steps.general import *


def rows_read(json_data):
    """Get the number of rows read from the json data."""

    return str(json.loads(json_data)["statistics"]["rows_read"])


def elapsed_time(json_data):
    """Get the elapsed time from the query run."""

    return str(json.loads(json_data)["statistics"]["elapsed"])


@TestStep
def read_bloom(self, file_name, condition=None, bloom_filter="true"):
    """Read a parquet file with bloom filter."""

    if condition is None:
        condition = "WHERE t2 = 'third-99999'"

    if bloom_filter == "with_bloom_filter":
        bloom_filter = "true"
    else:
        bloom_filter = "false"

    with Given(f"I read a parquet file with bloom filter {file_name}"):
        data = select_from_parquet(
            file_name=file_name,
            statement="*",
            condition=condition,
            format="Json",
            settings=f"input_format_parquet_bloom_filter_push_down={bloom_filter},"
            f"input_format_parquet_filter_push_down=false,"
            f"use_cache_for_count_from_files=false",
        )

    with And("I get the total number of rows from this file"):
        total_rows = count_rows_in_parquet(file_name=file_name)

    return data.output.strip(), condition, total_rows


@TestOutline
def collect_benchmark_data(self, file_name, predicate_conditions):
    """Collect benchmark data for a parquet file with bloom filter."""
    results = self.context.results
    results[file_name] = {}

    for predicate_condition in predicate_conditions:
        results[file_name][predicate_condition] = {}
        for bloom_filter in ["with_bloom_filter", "without_bloom_filter"]:
            with Given(
                "I read from the parquet with given predicate condition and bloom filter",
                description=f"{bloom_filter, predicate_condition}",
            ):
                output, query, total_rows = read_bloom(
                    file_name=os.path.join("bloom_test_files", f"{file_name}"),
                    bloom_filter=bloom_filter,
                    condition=predicate_condition,
                )

            with When("I collect benchmark data"):
                with By("getting the number of rows read"):
                    rows = rows_read(json_data=output)
                with And("getting the elapsed time"):
                    elapsed = elapsed_time(json_data=output)

            with Then("I append data into the dictionary to generate a report"):
                rows_skipped = total_rows - int(rows)

                benchmark_data = {
                    "rows_skipped": rows_skipped,
                    "total_rows": total_rows,
                    "elapsed": elapsed,
                    "query": query,
                }

                results[file_name][predicate_condition][bloom_filter] = benchmark_data


@TestScenario
def file_with_10_million_rows_and_10_row_groups(self, predicate_conditions):
    """Read a parquet file with 10 million rows and 10 row groups."""
    collect_benchmark_data(
        file_name="10M_rows_10_row_groups.parquet",
        predicate_conditions=predicate_conditions,
    )


@TestScenario
def few_and_large_row_groups(self, predicate_conditions):
    """Read a parquet file with few and large row groups."""
    collect_benchmark_data(
        file_name="few_and_large_row_groups.parquet",
        predicate_conditions=predicate_conditions,
    )


@TestScenario
def few_and_small_row_groups(self, predicate_conditions):
    """Read a parquet file with few and small row groups."""
    collect_benchmark_data(
        file_name="few_and_small_row_groups.parquet",
        predicate_conditions=predicate_conditions,
    )


@TestScenario
def many_and_large_row_groups(self, predicate_conditions):
    """Read a parquet file with many and large row groups."""
    collect_benchmark_data(
        file_name="lots_of_row_groups_large.parquet",
        predicate_conditions=predicate_conditions,
    )


@TestScenario
def many_and_small_row_groups(self, predicate_conditions):
    """Read a parquet file with many and small row groups."""
    collect_benchmark_data(
        file_name="lots_of_row_groups_small.parquet",
        predicate_conditions=predicate_conditions,
    )


@TestFeature
@Name("bloom filter")
def feature(self, rows=None, row_groups=None):
    """Check benchmarks for parquet files with bloom filters."""
    self.context.node = self.context.cluster.node("clickhouse1")

    conditions = [
        "WHERE t2 = 'third-99999'",
        "WHERE t2 = 'third-90000'",
        "WHERE t2 = 'third-80000'",
        "WHERE t2 = 'third-70000'",
        "WHERE t2 = 'third-60000'",
        "WHERE t2 = 'third-50000'",
        "WHERE t2 = 'third-40000'",
        "WHERE t2 = 'third-30000'",
        "WHERE t2 = 'third-20000'",
        "WHERE t2 = 'third-10000'",
        "WHERE t2 = 'third-00000'",
    ]

    for scenario in loads(current_module(), Scenario):
        Scenario(test=scenario)(predicate_conditions=conditions)

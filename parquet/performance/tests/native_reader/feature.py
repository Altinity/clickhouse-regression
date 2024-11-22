import json
import os
import re
import subprocess
import time

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
from parquet.performance.tests.native_reader.steps import hits_queries


def get_memory_usage(output):
    """Extract MemoryTracker values from the output of a ClickHouse query from print-profile-events."""

    output = output.stderr

    memory_tracker_usage_pattern = r"MemoryTrackerUsage:\s+(\d+)\s+\(gauge\)"
    memory_tracker_peak_usage_pattern = r"MemoryTrackerPeakUsage:\s+(\d+)\s+\(gauge\)"

    memory_tracker_usage = re.search(memory_tracker_usage_pattern, output)
    memory_tracker_peak_usage = re.search(memory_tracker_peak_usage_pattern, output)

    if memory_tracker_usage and memory_tracker_peak_usage:
        return {
            "MemoryTrackerUsage": int(memory_tracker_usage.group(1)),
            "MemoryTrackerPeakUsage": int(memory_tracker_peak_usage.group(1)),
        }
    else:
        return {"error": output}


@TestStep(Given)
def clear_filesystem_and_flush_cache(self):
    """Clear filesystem and flush cache."""
    subprocess.run("sync", shell=True)
    subprocess.run("echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null", shell=True)
    note("Filesystem cleared and cache flushed.")


@TestStep(Given)
def clickhouse_local(self, query, statistics=False):
    """Run a query locally."""
    query_args = [self.context.clickhouse_binary, "--multiquery"]

    if statistics:
        query_args.append("--print-profile-events")

    result = subprocess.run(
        query_args,
        input=query,
        text=True,
        capture_output=True,
    )

    # Assert that the exit code is 0
    # assert (
    #     result.returncode == 0
    # ), f"ClickHouse local {query} failed with exit code {result.returncode}. Error: {result.stderr}"

    note(f"query: {result.stdout}")

    if not statistics:
        return result.stdout
    else:
        return result.stdout, get_memory_usage(result)


@TestStep(Given)
def download_hits_dataset(self, filename):
    """Download the hits dataset."""
    if os.path.exists(filename):
        note(f"The file '{filename}' already exists. Skipping download.")
        return
    note(f"Downloading the hits dataset to '{filename}'...")
    subprocess.run(
        f"wget -O {filename} https://datasets.clickhouse.com/hits_compatible/hits.parquet",
        shell=True,
        check=True,
    )


@TestStep(Given)
def get_clickhouse_version(self):
    """Get the ClickHouse version."""
    version = clickhouse_local(query="SELECT version();")

    return version


@TestStep(Given)
def create_parquet_file(self, table_name, parquet_file, threads=10, max_memory_usage=0):
    insert_into_parquet = (
        f"SELECT * FROM {table_name} INTO OUTFILE '{parquet_file}' FORMAT Parquet SETTINGS "
        f"max_insert_threads = {threads}, max_memory_usage={max_memory_usage};"
    )

    return insert_into_parquet


@TestScenario
def hits_dataset(self, repeats):
    """Check performance of ClickHouse parquet native reader using the hits dataset."""
    file_name = f"hits.parquet"
    results = {"native_reader": {}, "regular_reader": {}}
    with Given("I create a parquet file with the hits dataset"):
        download_hits_dataset(filename=file_name)

    with When("I run queries against the parquet file with native parquet reader"):
        queries_with_native_reader = hits_queries(
            file_name=f"{file_name}", native_reader=True
        )

        for index, query in enumerate(queries_with_native_reader):
            for i in range(repeats):
                clear_filesystem_and_flush_cache()
                start_time = time.time()
                result, memory_used = clickhouse_local(query=query, statistics=True)
                clickhouse_run_time = time.time() - start_time

                if f"query_{index}" not in results["native_reader"]:
                    results["native_reader"][f"query_{index}"] = {
                        f"time_{i}": clickhouse_run_time,
                        f"memory_{i}": memory_used,
                    }
                else:
                    results["native_reader"][f"query_{index}"][
                        f"time_{i}"
                    ] = clickhouse_run_time
                    results["native_reader"][f"query_{index}"][
                        f"memory_{i}"
                    ] = memory_used

    with And("I run queries against the parquet file without native parquet reader"):
        queries_without_native_reader = hits_queries(
            file_name=f"{file_name}", native_reader=False
        )

        for index, query in enumerate(queries_without_native_reader):
            for i in range(repeats):
                clear_filesystem_and_flush_cache()
                start_time = time.time()
                result, memory_used = clickhouse_local(query=query, statistics=True)
                clickhouse_run_time = time.time() - start_time

                if f"query_{index}" not in results["regular_reader"]:
                    results["regular_reader"][f"query_{index}"] = {
                        f"time_{i}": clickhouse_run_time,
                        f"memory_{i}": memory_used,
                    }
                else:
                    results["regular_reader"][f"query_{index}"][
                        f"time_{i}"
                    ] = clickhouse_run_time
                    results["regular_reader"][f"query_{index}"][
                        f"memory_{i}"
                    ] = memory_used

    with Then("I write results into a JSON file"):
        clickhouse_version = get_clickhouse_version().strip()
        json_file_path = os.path.join(
            current_dir(),
            "..",
            "..",
            "results",
            "native_reader",
            "hits",
            f"{clickhouse_version}",
            "results.json",
        )

        # Ensure the directory exists
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

        # Write the results dictionary to a JSON file
        with open(json_file_path, "w") as json_file:
            json.dump(results, json_file, indent=2)


@TestFeature
@Name("native reader")
def feature(self, repeats=3):
    """Check performance of ClickHouse parquet native reader."""
    Scenario(test=hits_dataset)(repeats=repeats)

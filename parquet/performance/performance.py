#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "../..")

from parquet.performance.argparsers import argparser
from helpers.cluster import short_hash, Shell, Cluster
from parquet.performance.tests.duckdb.reports import (
    write_to_csv,
    convert_to_markdown,
    create_bar_chart,
)


@TestStep(Given)
def performance_cluster(
    self,
    duckdb_binary_path,
    clickhouse_binary_path,
    stress,
    clickhouse_version,
    allow_vfs=False,
    allow_experimental_analyzer=False,
):
    nodes = {"clickhouse": ("clickhouse1",), "duckdb": ("duckdb1",)}

    if os.path.exists("/tmp/duckdb"):
        with Given("I save the path to the duckdb binary"):
            duckdb_binary_path = os.path.abspath("/tmp/duckdb")
    else:
        if duckdb_binary_path.startswith(("http://", "https://")):
            with Given(
                "I download duckdb binary using wget",
                description=f"{duckdb_binary_path}",
            ):
                filename = f"{short_hash(duckdb_binary_path)}-{duckdb_binary_path.rsplit('/', 1)[-1]}"
                if not os.path.exists(f"/tmp/duckdb"):
                    with Shell() as bash:
                        bash.timeout = 300
                        try:
                            cmd = bash(
                                f'wget --progress dot "{duckdb_binary_path}" -O {filename}'
                            )
                            assert cmd.exitcode == 0

                            if ".zip" in filename:
                                cmd = bash(f"unzip {filename} -d /tmp")
                                assert cmd.exitcode == 0

                        except BaseException:
                            if os.path.exists(filename):
                                os.remove(filename)
                            raise

            duckdb_binary_path = os.path.abspath("/tmp/duckdb")

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Cluster(
        local=True,
        collect_service_logs=False,
        nodes=nodes,
        clickhouse_binary_path=clickhouse_binary_path,
        environ={"DUCKDB_TESTS_BIN_PATH": duckdb_binary_path},
    ) as cluster:
        yield cluster


@TestModule
@Name("performance")
@ArgumentParser(argparser)
def module(
    self,
    local,
    clickhouse_version,
    duckdb_binary_path,
    stress,
    from_year,
    filename,
    to_year,
    threads,
    first_number,
    last_number,
    data,
    max_memory_usage,
    compression,
    collect_service_logs,
    rerun_queries,
    test_machine,
    clickhouse_binary_path=None,
):
    """Running performance tests for ClickHouse"""
    with Given("I bring up the performance cluster environment"):
        self.context.cluster = performance_cluster(
            duckdb_binary_path=duckdb_binary_path,
            clickhouse_binary_path=clickhouse_binary_path,
            clickhouse_version=clickhouse_version,
            stress=stress,
        )

    self.context.clickhouse_node = self.context.cluster.node("clickhouse1")
    self.context.duckdb_node = self.context.cluster.node("duckdb1")
    self.context.clickhouse_version = clickhouse_version
    self.context.duckdb_version = duckdb_binary_path.rsplit("/", 2)[-2][1:]
    self.context.run_count = rerun_queries
    self.context.query_results = []
    self.context.row_count = []
    self.context.test_machine = test_machine
    self.context.rerun_queries = rerun_queries
    self.context.filename = filename

    self.context.from_year = from_year
    self.context.to_year = to_year

    Feature(test=load("parquet.performance.tests.duckdb.feature", "feature"))(
        from_year=from_year,
        to_year=to_year,
        threads=threads,
        first_number=first_number,
        last_number=last_number,
        max_memory_usage=max_memory_usage,
        compression=compression,
        data=data,
    )


if main():
    module()

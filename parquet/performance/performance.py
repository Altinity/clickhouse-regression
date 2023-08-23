#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "../..")

from parquet.performance.argparsers import argparser
from helpers.cluster import short_hash, Shell, Cluster
from parquet.performance.tests.duckdb.reports import write_to_csv


@TestStep(Given)
def performance_cluster(
    self, duckdb_binary_path, clickhouse_binary_path, stress, clickhouse_version
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

    from platform import processor as current_cpu

    folder_name = os.path.basename(current_dir())

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    if current_cpu() == "aarch64":
        env = f"parquet_{folder_name}_env_arm64"
    else:
        env = f"parquet_{folder_name}_env"

    with Cluster(
        local=True,
        collect_service_logs=False,
        nodes=nodes,
        clickhouse_binary_path=clickhouse_binary_path,
        environ={"DUCKDB_TESTS_BIN_PATH": duckdb_binary_path},
        docker_compose_project_dir=os.path.join(current_dir(), env),
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
    max_memory_usage,
    compression,
    collect_service_logs,
    rerun_queries,
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

    self.context.run_count = rerun_queries
    self.context.duckdb_node = self.context.cluster.node("duckdb1")
    self.context.clickhouse_node = self.context.cluster.node("clickhouse1")
    self.context.query_results = []
    self.context.row_count = []
    self.context.clickhouse_version = clickhouse_version
    self.context.duckdb_version = duckdb_binary_path.rsplit("/", 2)[-2][1:]

    Feature(test=load("parquet.performance.tests.duckdb.feature", "feature"))(
        from_year=from_year,
        to_year=to_year,
        threads=threads,
        max_memory_usage=max_memory_usage,
        compression=compression,
    )

    write_to_csv(
        filename=filename,
        data=self.context.query_results,
        row_count=self.context.row_count[0],
    )


if main():
    module()

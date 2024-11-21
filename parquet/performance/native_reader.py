#!/usr/bin/env python3
import os
import sys
import subprocess
import re

from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import short_hash, Shell, Cluster, get_binary_from_docker_container
from helpers.argparser import CaptureClusterArgs
from parquet.performance.tests.duckdb.reports import (
    write_to_csv,
    convert_to_markdown,
    create_bar_chart,
)


def argparser(parser):
    """Default argument parser for regressions."""
    parser.add_argument(
        "--clickhouse",
        "--clickhouse-package-path",
        "--clickhouse-binary-path",
        type=str,
        dest="clickhouse_path",
        help="Path to ClickHouse package or binary.",
        metavar="PATH",
        default="docker://altinity/clickhouse-server:24.3.12.76.altinitystable",
    )


@TestStep(Given)
def get_binary_and_copy_here(self, clickhouse_binary_path):
    """Get the ClickHouse binary from the docker container and copy it to the current directory."""
    binary_path = get_binary_from_docker_container(
        clickhouse_binary_path,
    )

    return binary_path


@TestStep(Given)
def run_local_query(self, query, clickhouse_binary):
    """Run a query locally."""
    result = subprocess.run(
        [clickhouse_binary, "-n", "--print-profile-events"],
        input=query,
        text=True,
        capture_output=True,
    )

    return result


@TestModule
@Name("native reader")
@ArgumentParser(argparser)
def module(self, clickhouse_path=None):
    """Running performance tests for Parquet native reader in ClickHouse."""

    with Given("I get the ClickHouse binary from the docker container"):
        self.context.clickhouse_binary = get_binary_and_copy_here(
            clickhouse_binary_path=clickhouse_path
        )

    Feature(run=load("parquet.performance.tests.native_reader.feature", "feature"))


if main():
    module()

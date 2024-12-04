#!/usr/bin/env python3
import subprocess
import sys

from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import get_binary_from_docker_container


def argparser(parser):
    """Default argument parser for native reader checks."""
    parser.add_argument(
        "--clickhouse",
        "--clickhouse-package-path",
        "--clickhouse-binary-path",
        type=str,
        dest="clickhouse_path",
        help="Path to ClickHouse package or binary.",
        metavar="PATH",
        default="docker://clickhouse/clickhouse-server:head",
    )


@TestStep(Given)
def get_binary_clickhouse_binary(self, clickhouse_binary_path):
    """Get the ClickHouse binary from the docker container."""
    binary_path = get_binary_from_docker_container(
        clickhouse_binary_path,
    )

    return binary_path


@TestModule
@Name("native reader")
@ArgumentParser(argparser)
def module(self, clickhouse_path=None):
    """Running performance tests for Parquet native reader in ClickHouse."""

    with Given("I get the ClickHouse binary from the docker container"):
        self.context.clickhouse_binary = get_binary_clickhouse_binary(
            clickhouse_binary_path=clickhouse_path
        )

    Feature(run=load("parquet.performance.tests.native_reader.feature", "feature"))


if main():
    module()

#!/usr/bin/env python3
import subprocess
import sys
import os
from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import get_binary_from_docker_container, download_http_binary, unpack_deb, unpack_tgz


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
def get_binary_from_deb(self, source):
    return unpack_deb(
        deb_binary_path=source,
        program_name="clickhouse",
    )

@TestStep(Given)
def get_binary_from_package(self, source):
    self.context.package_path = source
    if source.endswith(".deb"):
        return get_binary_from_deb(source=source)
    elif source.endswith(".rpm"):
        pass
    elif source.endswith(".tgz"):
        self.context.binary_path = os.path.join(
            unpack_tgz(source), "usr/bin", "clickhouse"
        )

@TestStep(Given)
def get_binary_clickhouse_binary(self, clickhouse_binary_path):
    """Get the ClickHouse binary from the docker container."""
    binary_path = get_binary_from_docker_container(
        clickhouse_binary_path,
    )

    return binary_path

@TestStep(Given)
def get_binary_from_http(self, url):
    """Get the binary from the HTTP URL."""
    package_formats = (".deb", ".rpm", ".tgz")
    binary_path = download_http_binary(url)
    if binary_path.endswith(package_formats):
        binary_path = get_binary_from_package(source=binary_path)
    else:
        binary_path = self.context.binary_path

    return binary_path
@TestModule
@Name("native reader")
@ArgumentParser(argparser)
def module(self, clickhouse_path=None):
    """Running performance tests for Parquet native reader in ClickHouse."""

    with Given("I get the ClickHouse binary from the docker container"):
        if clickhouse_path.startswith("docker://"):
            self.context.clickhouse_binary = get_binary_clickhouse_binary(
                clickhouse_binary_path=clickhouse_path
            )
        elif clickhouse_path.startswith(("http://", "https://")):
            self.context.clickhouse_binary = get_binary_from_http(url=clickhouse_path)


    Feature(run=load("parquet.performance.tests.native_reader.feature", "feature"))


if main():
    module()

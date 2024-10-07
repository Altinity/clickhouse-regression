#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import create_cluster
from helpers.common import experimental_analyzer
from helpers.argparser import CaptureClusterArgs

from parquet.performance.tests.bloom.generate_report import generate_bloom_report


def argparser(parser):
    """Default argument parser for regressions."""
    parser.add_argument(
        "--local",
        action="store_true",
        help="run regression in local mode",
        default=True,
    )

    parser.add_argument(
        "--clickhouse-version",
        type=str,
        dest="clickhouse_version",
        help="clickhouse server version",
        metavar="version",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_VERSION", None),
    )

    parser.add_argument(
        "--clickhouse-binary-path",
        type=str,
        dest="clickhouse_path",
        help="path to ClickHouse binary, default: /usr/bin/clickhouse",
        metavar="path",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH", "/usr/bin/clickhouse"),
    )

    parser.add_argument(
        "--stress",
        action="store_true",
        default=False,
        help="enable stress testing (might take a long time)",
    )

    parser.add_argument(
        "--collect-service-logs",
        action="store_true",
        default=False,
        help="enable docker log collection. for ci/cd use, does not work locally.",
    )

    parser.add_argument(
        "--with-analyzer",
        action="store_true",
        default=False,
        help="Use experimental analyzer.",
    )


@TestModule
@ArgumentParser(argparser)
@Name("bloom benchmark")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    with_analyzer,
    stress,
):
    """Parquet regression."""
    nodes = {"clickhouse": ("clickhouse1",)}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            docker_compose_project_dir=os.path.join(
                current_dir(), "env", "bloom_performance_env"
            ),
        )
        self.context.cluster = cluster
        self.context.results = {}
    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(test=load("parquet.performance.tests.bloom.feature", "feature"))()

    generate_bloom_report(
        data=self.context.results,
        filename=os.path.join("results", "bloom_filter", "README.md"),
        csv_filename=os.path.join("results", "bloom_filter", "bloom_report.csv"),
    )


if main():
    regression()

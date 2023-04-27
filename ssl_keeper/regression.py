#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from platform import processor as current_cpu


def argparser(parser):
    """Custom argperser that add --thread-fuzzer option."""
    base_argparser(parser)

    parser.add_argument(
        "--thread-fuzzer",
        action="store_true",
        help="enable thread fuzzer",
        default=False,
    )


xfails = {}
xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("ssl keeper")
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
    thread_fuzzer=None,
):
    """ClickHouse ssl ClickHouse Keeper regression."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "bash_tools": ("bash_tools"),
    }

    self.context.clickhouse_version = clickhouse_version

    self.context.transaction_atomic_insert = True

    if stress is not None:
        self.context.stress = stress

    env = "ssl_keeper_env"

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        thread_fuzzer=thread_fuzzer,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster

        if check_clickhouse_version("<22.4")(self):
            skip(reason="only supported on ClickHouse version >= 22.4")

        Feature(run=load("ssl_keeper.tests.sanity", "feature"))
        Feature(run=load("ssl_keeper.tests.keeper_ssl_cluster", "feature"))


if main():
    regression()

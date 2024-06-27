#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from ssl_keeper.helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer


def argparser(parser):
    """Custom argperser that add --thread-fuzzer option."""
    base_argparser(parser)

    parser.add_argument(
        "--thread-fuzzer",
        action="store_true",
        help="enable thread fuzzer",
        default=False,
    )


xfails = {
    "ssl keeper/FIPS SSL/openssl check/port:%%%%/connection using FIPS compatible cipher ECDHE-ECDSA-AES128-GCM-SHA256 should work": [
        (Fail, "not supported by SSL library")
    ],
    "/ssl keeper/FIPS SSL/openssl check/port:%%%%/connection using FIPS compatible cipher ECDHE-ECDSA-AES256-GCM-SHA384 should work": [
        (Fail, "not supported by SSL library")
    ],
}
xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("ssl keeper")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    thread_fuzzer=None,
    with_analyzer=False,
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

    with Cluster(
        **cluster_args,
        thread_fuzzer=thread_fuzzer,
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster

        if check_clickhouse_version("<22.4")(self):
            skip(reason="only supported on ClickHouse version >= 22.4")

        with Given("I enable or disable experimental analyzer if needed"):
            for node in nodes["clickhouse"]:
                experimental_analyzer(
                    node=cluster.node(node), with_analyzer=with_analyzer
                )

        Feature(run=load("ssl_keeper.tests.sanity", "feature"))
        Feature(run=load("ssl_keeper.tests.fips_ssl", "feature"))


if main():
    regression()

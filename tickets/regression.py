#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from platform import processor as current_cpu


def fuzzer_arg(parser):
    base_argparser(parser)

    parser.add_argument(
        "--thread_fuzzer",
        action="store_true",
        help="enable thread fuzzer",
        default=False,
    )


xfails = {}


xflags = {}


@TestModule
@ArgumentParser(fuzzer_arg)
@XFails(xfails)
@XFlags(xflags)
@Name("tickets")
@Requirements()
@Specifications()
def regression(
    self, local, thread_fuzzer, clickhouse_binary_path, clickhouse_version, stress=None
):
    """ClickHouse regression for tickets."""
    nodes = {
        "zookeeper": ("zookeeper",),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3", "clickhouse4"),
    }

    self.context.clickhouse_version = clickhouse_version

    if check_clickhouse_version("<21.8")(self):
        skip(reason="only supported on ClickHouse version >= 21.8")

    if stress is not None:
        self.context.stress = stress

    if current_cpu() == "aarch64":
        env = "tickets_env_arm64"
    else:
        env = "tickets_env"

    with Cluster(
        local,
        clickhouse_binary_path,
        thread_fuzzer=thread_fuzzer,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster

        pass


if main():
    regression()

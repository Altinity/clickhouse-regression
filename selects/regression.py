#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from platform import processor as current_cpu

from selects.requirements import *


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
    "/selects/final/force modifier/select join clause/:": [
        (
            Fail,
            "doesn't work in clickhouse"
            " https://github.com/ClickHouse/"
            "ClickHouse/issues/8655",
        )
    ],
    "/selects/final/modifier": [(Fail, "not implemented")],
}
xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("selects")
@Specifications(
    SRS032_ClickHouse_Automatic_Final_Modifier_For_Select_Queries
)  # FIXME: move to force_modifier.py
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    stress=None,
    thread_fuzzer=None,
):
    """ClickHouse SELECT query regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    if current_cpu() == "aarch64":
        env = "selects_env_arm64"
    else:
        env = "selects_env"

    with Cluster(
        local,
        clickhouse_binary_path,
        thread_fuzzer=thread_fuzzer,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

        if check_clickhouse_version("<22.11")(self):  # FIXME: move to force_modifier.py
            skip(
                reason="force_select_final is only supported on ClickHouse version >= 22.11"
            )

        Module(run=load("selects.tests.final.feature", "module"))


if main():
    regression()

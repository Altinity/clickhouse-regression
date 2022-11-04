#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from select_final.requirements import *
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
@Name("select final")
@Requirements(RQ_SRS_033_ClickHouse_SelectFinal("1.0"))
@Specifications(SRS033_ClickHouse_Select_Final)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    stress=None,
    thread_fuzzer=None,
):
    """ClickHouse auto "SELECT ... FINAL" query regression."""
    nodes = {
        "clickhouse": ("clickhouse",),
    }

    self.context.clickhouse_version = clickhouse_version

    self.context.transaction_atomic_insert = True

    # if check_clickhouse_version("<22.10")(self) or clickhouse_version is None:
    #     skip(reason="only supported on ClickHouse version >= 22.10")

    if stress is not None:
        self.context.stress = stress

    if current_cpu() == "aarch64":
        env = "select_final_env_arm64"
    else:
        env = "select_final_env"

    with Cluster(
        local,
        clickhouse_binary_path,
        thread_fuzzer=thread_fuzzer,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster

        Feature(run=load("select_final.tests.sanity", "feature"))


if main():
    regression()

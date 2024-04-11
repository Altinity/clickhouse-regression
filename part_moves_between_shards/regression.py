#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from part_moves_between_shards.requirements import *


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


ffails = {
    "/part moves between shards/part_moves/part move parallel with big insert": (
        Skip,
        "SELECT uuid FROM system.parts WHERE uuid = {uuid} doesn't output anything: https://github.com/ClickHouse/ClickHouse/issues/61220",
        check_clickhouse_version(">=24.1"),
    ),
    "/part moves between shards/part_moves/part move parallel with insert to destination": (
        Skip,
        "SELECT uuid FROM system.parts WHERE uuid = {uuid} doesn't output anything: https://github.com/ClickHouse/ClickHouse/issues/61220",
        check_clickhouse_version(">=24.1"),
    ),
    "/part moves between shards/part_moves/part move parallel with insert to source": (
        Skip,
        "SELECT uuid FROM system.parts WHERE uuid = {uuid} doesn't output anything: https://github.com/ClickHouse/ClickHouse/issues/61220",
        check_clickhouse_version(">=24.1"),
    ),
    "/part moves between shards/deduplication/distributed table": (
        Skip,
        "SELECT uuid FROM system.parts WHERE uuid = {uuid} doesn't output anything: https://github.com/ClickHouse/ClickHouse/issues/61220",
        check_clickhouse_version(">=24.1"),
    ),
    "/part moves between shards/deduplication/distributed table stopped replica": (
        Skip,
        "SELECT uuid FROM system.parts WHERE uuid = {uuid} doesn't output anything: https://github.com/ClickHouse/ClickHouse/issues/61220",
        check_clickhouse_version(">=24.1"),
    ),
}


@TestModule
@ArgumentParser(fuzzer_arg)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("part moves between shards")
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards("1.0"))
@Specifications(SRS027_ClickHouse_Part_Moves_Between_Shards)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
    thread_fuzzer=None,
    allow_vfs=False,
    allow_experimental_analyzer=False,
):
    """ClickHouse regression when using parts moves."""
    nodes = {
        "zookeeper": ("zookeeper",),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3", "clickhouse4"),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            thread_fuzzer=thread_fuzzer,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    if check_clickhouse_version("<21.4")(self):
        skip(reason="only supported on ClickHouse version >= 21.4")

    Feature(run=load("part_moves_between_shards.tests.sanity", "feature"))
    Feature(run=load("part_moves_between_shards.tests.part_moves", "feature"))
    Feature(run=load("part_moves_between_shards.tests.system_table", "feature"))
    Feature(run=load("part_moves_between_shards.tests.deduplication", "feature"))


if main():
    regression()

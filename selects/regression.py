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
    "final/force modifier/without experimental analyzer/select join clause": [
        (
            Fail,
            "doesn't work in clickhouse"
            " https://github.com/ClickHouse/"
            "ClickHouse/issues/8655",
        )
    ],
    "final/modifier": [(Fail, "not implemented")],
    "/selects/final/force modifier/with experimental analyzer/select group by": [(Fail, "group by conflict analyzer")],
    "/selects/final/force modifier/with experimental analyzer/select count": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select limit": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select limit by": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select distinct": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select prewhere": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select where": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select multiple join clause select": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select nested join clause select": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select join clause": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select prewhere subquery": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select nested subquery": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select where subquery": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select subquery": [
        (Fail, "column fail for distributed tables")],
    "/selects/final/force modifier/with experimental analyzer/select with clause": [
        (Fail, "column fail for distributed tables")],

}
xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("selects")
@Specifications()
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

        Feature(run=load("selects.tests.final.feature", "module"))


if main():
    regression()

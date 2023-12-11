#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from s3.tests.common import enable_vfs

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
    "final/force/general/without experimental analyzer/select join clause/*": [
        (
            Fail,
            "doesn't work in clickhouse"
            " https://github.com/ClickHouse/ClickHouse/issues/8655",
        )
    ],
    "final/force/general/with experimental analyzer/simple select group by/*": [
        (Fail, "group by conflict analyzer")
    ],
    "final/force/general/with experimental analyzer/simple select count/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select as/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select limit/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select limit by/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select distinct/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/simple select where/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/select multiple join clause select/AggregatingMergeTree*": [
        (Fail, "AggregatingFunction problem with analyzer")
    ],
    "final/force/general/with experimental analyzer/select nested join clause select/AggregatingMergeTree*": [
        (Fail, "AggregatingFunction problem with analyzer")
    ],
    "final/force/general/with experimental analyzer/select nested subquery/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/select where subquery/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
    "final/force/general/with experimental analyzer/select subquery/distr_*": [
        (Fail, "column fail for distributed tables")
    ],
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
    collect_service_logs,
    stress=None,
    thread_fuzzer=None,
    allow_vfs=False,
):
    """ClickHouse SELECT query regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("I have a clickhouse cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            thread_fuzzer=thread_fuzzer,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
            configs_dir=current_dir(),
        ) 
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    if allow_vfs:
        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

    Feature(run=load("selects.tests.final.feature", "module"))


if main():
    regression()

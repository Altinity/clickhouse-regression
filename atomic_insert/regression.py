#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from atomic_insert.requirements import *

from atomic_insert.tests.steps import *


def argparser(parser):
    """Custom argperser that add --thread-fuzzer option."""
    base_argparser(parser)

    parser.add_argument(
        "--thread-fuzzer",
        action="store_true",
        help="enable thread fuzzer",
        default=False,
    )


ffails = {
    "/atomic insert/dependent_tables/Replicated*/table with materialized view engine mismatch/*": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/59670",
    ),
}

xfails = {
    "/atomic insert/dependent_tables/Replicated*/table with materialized view*/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/19352",
        )
    ],
    "/atomic insert/hard restart/SIGKILL/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/60406",
        )
    ],
}


@TestModule
@ArgumentParser(argparser)
@FFails(ffails)
@XFails(xfails)
@Name("atomic insert")
@Requirements(RQ_SRS_028_ClickHouse_AtomicInserts("1.0"))
@Specifications(SRS028_ClickHouse_Atomic_Inserts)
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
    """ClickHouse atomic inserts regression."""
    nodes = {
        "zookeeper": ("zookeeper",),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3", "clickhouse4"),
    }

    self.context.clickhouse_version = clickhouse_version

    self.context.transaction_atomic_insert = True

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
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
        )
        self.context.cluster = cluster

    if check_clickhouse_version("<22.4")(self):
        skip(reason="only supported on ClickHouse version >= 22.4")

    create_transactions_configuration()

    Feature(run=load("atomic_insert.tests.sanity", "feature"))
    Feature(run=load("atomic_insert.tests.dependent_tables", "feature"))
    Feature(run=load("atomic_insert.tests.block_fail", "feature"))
    Feature(run=load("atomic_insert.tests.insert_settings", "feature"))
    Feature(run=load("atomic_insert.tests.distributed_table", "feature"))
    Feature(run=load("atomic_insert.tests.user_rights", "feature"))
    Feature(run=load("atomic_insert.tests.transaction", "feature"))
    Feature(run=load("atomic_insert.tests.hard_restart", "feature"))


if main():
    regression()

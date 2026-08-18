#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import CaptureClusterArgs, argparser as argparser_base
from helpers.common import check_clickhouse_version
from atomic_insert.requirements import *

from atomic_insert.tests.steps import *
from atomic_insert.cas_mode import (
    enable_cas_default_storage,
    reset_cas_config,
)


def argparser(parser):
    argparser_base(parser)
    parser.add_argument(
        "--cas",
        action="store_true",
        default=False,
        dest="use_cas",
        help="use content-addressed storage as the default MergeTree disk",
    )

ffails = {
    "/atomic insert/dependent_tables/Replicated*/table with materialized view engine mismatch/*": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/59670",
    ),
    "/atomic insert/hard restart/SIGKILL/hard restart with big insert/*": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/60406",
        check_current_cpu("aarch64"),
    ),
    "/atomic insert/hard restart/SIGKILL/hard restart with random insert/*": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/60406",
    ),
    "/atomic insert/dependent_tables/:/materialized view live view": (
        Skip,
        "Live view feature was removed in 25.10 https://github.com/ClickHouse/ClickHouse/pull/88706",
        check_clickhouse_version(">=25.10"),
    ),
}

xfails = {
    "/atomic insert/dependent_tables/Replicated*/table with materialized view*/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/19352",
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
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    use_cas=False,
):
    """ClickHouse atomic inserts regression."""
    nodes = {
        "zookeeper": ("zookeeper1",),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3", "clickhouse4"),
    }

    self.context.clickhouse_version = clickhouse_version
    self.context.use_cas_storage = False
    self.context.default_storage_policy = None

    self.context.transaction_atomic_insert = True

    if stress is not None:
        self.context.stress = stress

    if use_cas:
        with Given("content-addressed storage as the default MergeTree disk"):
            enable_cas_default_storage()
    else:
        with Given("no content-addressed storage configuration"):
            reset_cas_config()

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
        )
        self.context.cluster = cluster

    if check_clickhouse_version("<22.4")(self):
        skip(reason="only supported on ClickHouse version >= 22.4")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with And("I create configs"):
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

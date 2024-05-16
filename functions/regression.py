#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser
from helpers.cluster import create_cluster
from helpers.common import experimental_analyzer


issue_59401 = "https://github.com/ClickHouse/ClickHouse/issues/59401"

xfails = {
    "/functions/merge/*": [
        (
            Fail,
            issue_59401,
            check_clickhouse_version(">=23.6") and check_clickhouse_version("<24.2"),
        )
    ],
}

ffails = {
    "/functions/projection optimization/projection optimization/*": (
        Skip,
        "Crashes before 23.11 https://github.com/ClickHouse/ClickHouse/pull/58638",
        check_clickhouse_version("<23.11"),
    )
}


@TestModule
@ArgumentParser(argparser)
@Name("functions")
@XFails(xfails)
@FFails(ffails)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    keeper_binary_path=None,
    zookeeper_version=None,
    stress=None,
    allow_vfs=False,
    with_analyzer=False,
):
    """Functions regression suite. Automated test for issues."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            keeper_binary_path=keeper_binary_path,
            zookeeper_version=zookeeper_version,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(run=load("functions.tests.merge", "feature"))
    Feature(run=load("functions.tests.insert", "feature"))
    Feature(run=load("functions.tests.projection_optimization", "feature"))


if main():
    regression()

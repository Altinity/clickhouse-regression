#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser
from helpers.cluster import create_cluster


issue_59401 = "https://github.com/ClickHouse/ClickHouse/issues/59401"

xfails = {
    "/issues/merge/*": [
        (
            Fail,
            issue_59401,
            check_clickhouse_version(">=23.6") and check_clickhouse_version("<24.2"),
        )
    ],
}


@TestModule
@ArgumentParser(argparser)
@Name("issues")
@XFails(xfails)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
    allow_vfs=None,
):
    """Issues regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    Feature(run=load("issues.tests.merge", "feature"))
    Feature(run=load("issues.tests.insert", "feature"))


if main():
    regression()

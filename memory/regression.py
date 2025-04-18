#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.cluster import create_cluster
from helpers.common import *


def memory_leak_versions():
    """Versions where memory leak was suspected."""

    def check(test):
        return check_clickhouse_version(">24.5")(test) or check_clickhouse_version(
            "<24"
        )(test)

    return check


xfails = {
    "/memory/memory leak/*": [
        (
            Fail,
            "memory leak detected on 23.8, need to investigate on  versions >=24.6",
            memory_leak_versions(),
        )
    ],
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@Name("memory")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Memory regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
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

    Feature(
        run=load(
            "memory.tests.test_memory_leak_using_system_memory_dump_log", "feature"
        )
    )
    Feature(run=load("memory.tests.test_memory_leak", "feature"))


if main():
    regression()

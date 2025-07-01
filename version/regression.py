#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import (
    experimental_analyzer,
    check_is_altinity_build,
    check_clickhouse_version,
)


ffails = {
    "/version/altinity/issue link": (
        Skip,
        "Need to investigate 1 exit code of grep",
    ),
}


xfails = {
    "/version/altinity/stacktrace/*": [
        (
            Fail,
            "Stacktrace message is different on older versions",
            check_clickhouse_version("<=23.4"),
        ),
    ],
    "/version/altinity/version format/*": [
        (Fail, "No --version option", check_clickhouse_version("<=23.4")),
    ],
}


@TestFeature
@Name("version")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Simple example of how you can use TestFlows to test ClickHouse."""
    nodes = {
        "clickhouse": ("clickhouse1",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    node = cluster.node("clickhouse1")
    is_altinity_build = check_is_altinity_build(node)
    if not is_altinity_build:
        skip("This suite is for Altinity builds only")

    with And("I enable or disable experimental analyzer if needed"):
        experimental_analyzer(node=node, with_analyzer=with_analyzer)

    Scenario(run=load("version.tests.altinity_version", "feature"))


if main():
    regression()

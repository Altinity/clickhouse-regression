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


ffails = {}


xfails = {
    "/version/altinity/stacktrace/*": [
        (
            Fail,
            "Stacktrace message is different on older versions",
            check_clickhouse_version("<=23.4"),
        ),
    ],
    "/version/altinity/embedded logos/*": [
        (
            Fail,
            "fix not introduced before the given version",
            check_clickhouse_version("<25.3.3.20152"),
        ),
    ],
    "/version/altinity/issue link in binary/*": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/pull/899",
            check_clickhouse_version("<25.3"),
        ),
    ],
    "/version/altinity/error message/": [
        (
            Fail,
            "Not expected to pass on PR builds",
            lambda test: test.context.build_options["clickhouse1"]["git_branch"]
            == "HEAD",
            ".*Expected message '\(altinity build\)' not found in log.*",
        ),
    ],
    "/version/altinity/version format/": [
        (
            Fail,
            "Not expected to pass on PR builds",
            lambda test: test.context.build_options["clickhouse1"]["git_branch"]
            == "HEAD",
        ),
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

    with And("check if this is an Altinity build"):
        is_altinity_build = check_is_altinity_build(node)

    if not is_altinity_build:
        skip("This suite is for Altinity builds only")

    with And("I enable or disable experimental analyzer if needed"):
        experimental_analyzer(node=node, with_analyzer=with_analyzer)

    Scenario(run=load("version.tests.altinity_version", "feature"))


if main():
    regression()

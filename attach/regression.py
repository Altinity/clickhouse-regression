#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from attach.requirements.requirements import SRS_039_ClickHouse_Attach_Statement

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.tables import check_clickhouse_version
from helpers.common import experimental_analyzer


issue_62905 = "https://github.com/ClickHouse/ClickHouse/issues/62905"

xfails = {
    "/attach/active path/check active path convert:/run #[0-9]": [(Fail, issue_62905)],
}

ffails = {
    "/attach/replica path/check replica path intersection": (
        Skip,
        "Crashes before 24.4",
        check_clickhouse_version("<24.4"),
    ),
    "/attach/active path/check active path convert*": (
        Skip,
        "Engine MergeTree does not support convert_to_replicated flag before 24.2",
        check_clickhouse_version("<24.2"),
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@FFails(ffails)
@Specifications(SRS_039_ClickHouse_Attach_Statement)
@Name("attach")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Attach statement regression."""

    self.context.clickhouse_version = clickhouse_version
    self.context.stress = stress

    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.node_1 = self.context.cluster.node("clickhouse1")
        self.context.node_2 = self.context.cluster.node("clickhouse2")
        self.context.node_3 = self.context.cluster.node("clickhouse3")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(run=load("attach.tests.replica_path", "feature"), flags=TE)
    Feature(run=load("attach.tests.active_path", "feature"), flags=TE)


if main():
    regression()

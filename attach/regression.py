#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from attach.requirements.requirements import SRS_039_ClickHouse_Attach_Statement

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.tables import check_clickhouse_version


issue_62905 = "https://github.com/ClickHouse/ClickHouse/issues/62905"

xfails = {
    "/attach/active path/check active path convert:/run #[0-9]": [(Fail, issue_62905)],
}

ffails = {
    "/attach/replica_path/check replica path intersection": (
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
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress,
    allow_vfs,
    allow_experimental_analyzer=False,
    keeper_binary_path=None,
    zookeeper_version=None,
):
    """Attach statement regression."""

    self.context.clickhouse_version = clickhouse_version
    self.context.stress = stress
    self.context.allow_vfs = allow_vfs

    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3"),
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            keeper_binary_path=keeper_binary_path,
            zookeeper_version=zookeeper_version,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.node_1 = self.context.cluster.node("clickhouse1")
        self.context.node_2 = self.context.cluster.node("clickhouse2")
        self.context.node_3 = self.context.cluster.node("clickhouse3")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
        self.context.zk_nodes = [cluster.node(n) for n in cluster.nodes["zookeeper"]]

    Feature(run=load("attach.tests.replica_path", "feature"), flags=TE)
    Feature(run=load("attach.tests.active_path", "feature"), flags=TE)


if main():
    regression()

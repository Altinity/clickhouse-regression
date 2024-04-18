#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from attach.requirements.requirements import SRS_039_ClickHouse_Attach_Statement

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.tables import check_clickhouse_version

xfails = {}

ffails = {
    "/attach/replica_path/check replica path intersection": (
        Skip,
        "Crashes before 24.4",
        check_clickhouse_version("<24.4"),
    ),
}


@TestModule
@Name("attach")
@XFails(xfails)
@FFails(ffails)
@ArgumentParser(argparser)
@Specifications(SRS_039_ClickHouse_Attach_Statement)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress,
    allow_vfs,
    allow_experimental_analyzer=False,
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
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            use_zookeeper_nodes=True,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = self.context.cluster.node("clickhouse1")
        self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]
        self.context.zk_nodes = [cluster.node(n) for n in cluster.nodes["zookeeper"]]

    Feature(run=load("attach.tests.replica_path", "feature"), flags=TE)
    Feature(run=load("attach.tests.active_path", "feature"), flags=TE)


if main():
    regression()

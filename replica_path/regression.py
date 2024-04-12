#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "../")

from helpers.cluster import create_cluster
from helpers.common import check_clickhouse_version
from helpers.argparser import argparser
from s3.tests.common import start_minio

xfails = {
}

ffails = {

}

@TestModule
@Name("stress")
@ArgumentParser(argparser)
@XFails(xfails)
@FFails(ffails)
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
    """Disk Object Storage VFS regression."""

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

    Feature(run=load("replica_path", "feature"))
   

    

if main():
    regression()

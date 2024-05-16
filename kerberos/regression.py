#!/usr/bin/env python3
import os
import sys
from testflows.core import *
from platform import processor as current_cpu

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.common import experimental_analyzer
from kerberos.requirements.requirements import *

xfails = {
    "config/principal and realm specified/:": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/26197")
    ],
}


@TestModule
@Name("kerberos")
@ArgumentParser(argparser)
@Requirements(RQ_SRS_016_Kerberos("1.0"))
@XFails(xfails)
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
    """ClickHouse Kerberos authentication test regression module."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "kerberos": ("kerberos",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    folder_name = os.path.basename(current_dir())
    if current_cpu() == "aarch64":
        env = f"{folder_name}_env_arm64"
    else:
        env = f"{folder_name}_env"
    self.context.env = env

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            keeper_binary_path=keeper_binary_path,
            zookeeper_version=zookeeper_version,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(run=load("kerberos.tests.generic", "generic"), flags=TE)
    Feature(run=load("kerberos.tests.config", "config"), flags=TE)
    Feature(run=load("kerberos.tests.parallel", "parallel"), flags=TE)


if main():
    regression()

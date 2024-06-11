#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.common import experimental_analyzer

xfails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@Name("kafka")
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    keeper_binary_path=None,
    zookeeper_version=None,
    use_keeper=False,
    stress=None,
    allow_vfs=False,
    with_analyzer=False,
):
    """Kafka regression."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
        "kafka": ("kafka1", "kafka2", "kafka3"),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            keeper_binary_path=keeper_binary_path,
            zookeeper_version=zookeeper_version,
            use_keeper=use_keeper,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Scenario(run=load("kafka.tests.distributed", "scenario"), flags=TE)
    Scenario(run=load("kafka.tests.non_replicated", "scenario"), flags=TE)
    Scenario(run=load("kafka.tests.non_replicated_4_consumers", "scenario"), flags=TE)
    Scenario(
        run=load("kafka.tests.non_replicated_target_table_not_writable", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("kafka.tests.non_replicated_clickhouse_restart", "scenario"),
        flags=TE,
    )
    Scenario(
        run=load("kafka.tests.non_replicated_4_consumers_restart", "scenario"),
        flags=TE,
    )
    Scenario(run=load("kafka.tests.replicated_stop_and_restart", "scenario"), flags=TE)


if main():
    regression()

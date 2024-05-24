#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import experimental_analyzer

xfails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@Name("kafka")
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
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
            **cluster_args,
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

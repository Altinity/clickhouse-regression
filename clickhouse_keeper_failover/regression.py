#!/usr/bin/env python3
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.common import check_clickhouse_version

from clickhouse_keeper_failover.tests.steps import *


xfails = {}

ffails = {}


@TestModule
def run_feature(
    self,
    local,
    clickhouse_binary_path,
    collect_service_logs,
    feature_file_name,
):
    nodes = {
        "clickhouse": [],
        "keeper": [f"keeper-{i}" for i in range(1, 7)],
    }

    try:
        with Given("docker-compose cluster"):
            cluster = create_cluster(
                local=local,
                clickhouse_binary_path=clickhouse_binary_path,
                collect_service_logs=collect_service_logs,
                nodes=nodes,
                configs_dir=current_dir(),
            )
            self.context.cluster = cluster
            self.context.keeper_nodes = [
                cluster.node(n) for n in cluster.nodes["keeper"]
            ]

        with And("I set the keeper config file"):
            set_keeper_config(
                nodes=self.context.keeper_nodes,
                config_file_name="keeper_config_6node.xml",
                restart=True,
            )

        with And("I know which ports are in use"):
            self.context.keeper_ports = get_external_ports(internal_port=9182)

        with And("I wait for a leader to be elected"):
            current_leader = retry(
                get_current_leader, timeout=30, delay=5, initial_delay=10
            )()

        Feature(
            run=load(f"clickhouse_keeper_failover.tests.{feature_file_name}", "feature")
        )

    finally:
        with Finally("I reset the config"):
            set_keeper_config(
                nodes=self.context.keeper_nodes,
                config_file_name="keeper_config_6node.xml",
                restart=False,
            )


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@FFails(ffails)
@Name("keeper failover")
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
    allow_vfs=False,
):
    """Clickhouse-keeper failover testing."""

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    if check_clickhouse_version("<21.4")(self):
        skip(reason="only supported on ClickHouse version >= 21.4")

    features = ["dynamic_reconfiguration_failover", "manual_failover"]

    for feature in features:
        run_feature(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            feature_file_name=feature,
        )


if main():
    regression()

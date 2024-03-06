#!/usr/bin/env python3
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.common import check_clickhouse_version, current_cpu


xfails = {}

ffails = {}


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
    """ClickHouse regression when using clickhouse-keeper."""
    nodes = {
        "clickhouse": [],
        "clickhouse-keeper": [f"clickhouse-keeper-{i}" for i in range(1, 6)],
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    if check_clickhouse_version("<21.4")(self):
        skip(reason="only supported on ClickHouse version >= 21.4")

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    Feature(run=load("clickhouse_keeper_failover.tests.manual_failover", "feature"))
    Feature(
        run=load(
            "clickhouse_keeper_failover.tests.dynamic_reconfiguration_failover",
            "feature",
        )
    )


if main():
    regression()

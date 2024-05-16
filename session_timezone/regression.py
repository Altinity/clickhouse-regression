#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.common import experimental_analyzer
from session_timezone.requirements import *
from session_timezone.common import *


xfails = {}

ffails = {}


@TestModule
@Name("session timezone")
@ArgumentParser(argparser)
@Specifications(SRS037_ClickHouse_Session_Timezone)
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone("1.0"))
@XFails(xfails)
@FFails(ffails)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    keeper_binary_path=None,
    zookeeper_version=None,
    stress=False,
    allow_vfs=False,
    with_analyzer=False,
):
    """ClickHouse Session Timezone regression module."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
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
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    if check_clickhouse_version("<23.5")(self):
        skip(reason="only supported on ClickHouse version >= 23.5")

    Feature(run=load("session_timezone.tests.sanity", "feature"))
    Feature(run=load("session_timezone.tests.basic", "feature"))
    Feature(run=load("session_timezone.tests.clickhouse_local", "feature"))
    Feature(run=load("session_timezone.tests.date_functions", "feature"))
    Feature(run=load("session_timezone.tests.tables_with_date_columns", "feature"))


if main():
    regression()

#!/usr/bin/env python3
import os
import sys
import time

from testflows.core import *

append_path(sys.path, "..", pos=0)

from helpers.cluster import create_cluster
from helpers.common import *
from helpers.argparser import argparser

xfails = {
    "lookup": [(Fail, "https://github.com/ClickHouse/ClickHouse/issues/17202")],
}
xflags = {}
ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("dns")
def regression(
    self,
    local,
    clickhouse_binary_path,
    collect_service_logs,
    clickhouse_version=None,
    stress=None,
):
    """DNS regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    Scenario(run=load("dns.tests.lookup.scenario", "scenario"))
    Feature(run=load("dns.tests.ipv6", "feature"))


if main():
    regression()

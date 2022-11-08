#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser
from aggregate_functions.requirements import SRS_031_ClickHouse_Aggregate_Functions


@TestModule
@ArgumentParser(argparser)
@Name("aggregate functions")
@Specifications(SRS_031_ClickHouse_Aggregate_Functions)
def regression(self, local, clickhouse_binary_path, clickhouse_version, stress=None):
    """Aggregate functions regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Cluster(
        local,
        clickhouse_binary_path,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(
            current_dir(), os.path.basename(current_dir()) + "_env"
        ),
    ) as cluster:
        self.context.cluster = cluster

        Feature(run=load("aggregate_functions.tests.count", "feature"))
        Feature(run=load("aggregate_functions.tests.state", "feature"))


if main():
    regression()

#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.tables import *

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

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    with And("table with all data types"):
        self.context.table = create_table(
            engine="MergeTree() ORDER BY tuple()", columns=generate_all_column_types()
        )

    with And("I populate table with test data"):
        self.context.table.insert_test_data()

    Feature(run=load("aggregate_functions.tests.count", "feature"))
    Feature(run=load("aggregate_functions.tests.min", "feature"))
    Feature(run=load("aggregate_functions.tests.state", "feature"))


if main():
    regression()

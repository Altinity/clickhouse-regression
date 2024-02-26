#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser
from helpers.cluster import create_cluster
from helpers.common import check_clickhouse_version, check_current_cpu

from aggregate_functions.tests.steps import aggregate_functions, window_functions
from aggregate_functions.requirements import SRS_031_ClickHouse_Aggregate_Functions


@TestModule
@ArgumentParser(argparser)
@Name("logger")
@Specifications(SRS_031_ClickHouse_Aggregate_Functions)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
    allow_vfs=None,
):
    """Logger regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    Feature(
        run=load(
            "memory.tests.test_memory_leak_using_system_memory_dump_log", "feature"
        )
    )
    Feature(run=load("memory.tests.test_memory_leak", "feature"))


if main():
    regression()

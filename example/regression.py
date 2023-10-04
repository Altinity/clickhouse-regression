#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser
from requirements.requirements import (
    SRS_001_ClickHouse_Software_Requirements_Specification_Template,
)


@TestFeature
@Name("example")
@ArgumentParser(argparser)
@Specifications(SRS_001_ClickHouse_Software_Requirements_Specification_Template)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
):
    """Simple example of how you can use TestFlows to test ClickHouse."""
    nodes = {
        "clickhouse": ("clickhouse1",),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
    ) as cluster:
        self.context.cluster = cluster

        Scenario(run=load("example.tests.example", "scenario"))


if main():
    regression()

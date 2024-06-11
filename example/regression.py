#!/usr/bin/env python3
import os
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from helpers.common import experimental_analyzer
from example.requirements.requirements import (
    SRS_001_ClickHouse_Software_Requirements_Specification_Template,
)


@TestFeature
@Name("example")
@ArgumentParser(argparser)
@Specifications(SRS_001_ClickHouse_Software_Requirements_Specification_Template)
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    allow_vfs=False,
    with_analyzer=False,
):
    """Simple example of how you can use TestFlows to test ClickHouse."""
    nodes = {
        "clickhouse": ("clickhouse1",),
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
        experimental_analyzer(
            node=cluster.node("clickhouse1"), with_analyzer=with_analyzer
        )

    Scenario(run=load("example.tests.example", "scenario"))


if main():
    regression()

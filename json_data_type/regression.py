#!/usr/bin/env python3
import sys
from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser,
    CaptureClusterArgs,
)
from helpers.common import check_clickhouse_version

from json_data_type.requirements.requirements import *


xfails = {}
ffails = {}


@TestModule
@Name("iceberg")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser)
@Specifications(SRS_043_JSON_Data_Type)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Run tests for Iceberg tables."""
    nodes = {
        "clickhouse": (
            "clickhouse1",
            # "clickhouse2",
            # "clickhouse3",
        ),
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

    self.context.node = self.context.cluster.node("clickhouse1")
    # self.context.node2 = self.context.cluster.node("clickhouse2")
    # self.context.node3 = self.context.cluster.node("clickhouse3")

    Feature(
        test=load("json_data_type.tests.combinations", "feature"),
    )()


if main():
    regression()

#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser

from extended_precision_data_types.requirements import *

xfails = {}

xflags = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@Name("extended precision data types")
@Specifications(SRS020_ClickHouse_Extended_Precision_Data_Types)
@Requirements(
    RQ_SRS_020_ClickHouse_Extended_Precision("1.0"),
)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    keeper_binary_path=None,
    zookeeper_version=None,
    stress=None,
    allow_vfs=False,
    allow_experimental_analyzer=False,
):
    """Extended precision data type regression."""
    nodes = {"clickhouse": ("clickhouse1",)}

    self.context.clickhouse_version = clickhouse_version

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
        self.context.stress = stress

    Feature(run=load("extended_precision_data_types.tests.feature", "feature"))


if main():
    regression()

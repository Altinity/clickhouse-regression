#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser
from s3.tests.common import enable_vfs

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
    stress=None,
    allow_vfs=False,
):
    """Extended precision data type regression."""
    nodes = {"clickhouse": ("clickhouse1",)}

    self.context.clickhouse_version = clickhouse_version

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.stress = stress

    if allow_vfs:
        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

    Feature(run=load("extended_precision_data_types.tests.feature", "feature"))


if main():
    regression()

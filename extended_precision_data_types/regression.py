#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import (
    experimental_analyzer,
    check_several_sanitizers_in_binary_link,
)

from extended_precision_data_types.requirements import *

issue_70518 = "https://github.com/ClickHouse/ClickHouse/issues/70518"

xfails = {
    "/extended precision data types/tests/mathematical/math int inline/lgamma（） - Int128/*": [
        (
            Fail,
            "fails with tsan",
            check_several_sanitizers_in_binary_link(["tsan", "asan", "msan"]),
        )
    ],
    "/extended precision data types/tests/mathematical/math int inline/lgamma（） - Int256/*": [
        (
            Fail,
            issue_70518,
            check_several_sanitizers_in_binary_link(["tsan", "asan", "msan"]),
        )
    ],
    "/extended precision data types/tests/mathematical/math dec inline/lgamma（） - Decimal256/*": [
        (
            Fail,
            issue_70518,
            check_several_sanitizers_in_binary_link(["tsan", "asan", "msan"]),
        )
    ],
}

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
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Extended precision data type regression."""
    nodes = {"clickhouse": ("clickhouse1",)}

    self.context.clickhouse_version = clickhouse_version

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.stress = stress

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    Feature(run=load("extended_precision_data_types.tests.feature", "feature"))


if main():
    regression()

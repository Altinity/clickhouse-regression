#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from base_58.requirements.requirements import *

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer, check_with_any_sanitizer

pr_70846 = "https://github.com/ClickHouse/ClickHouse/pull/70846"

xfails = {
    # Memory usage tests fail with sanitizers due to test code issues and memory overhead
    "/base58/memory usage/*": [
        (
            Error,
            "Memory usage tests have issues with sanitizer builds",
            check_with_any_sanitizer,
        )
    ],
    "alias input/alias instead of table and column": [(Fail, "not implemented")],
    "/base58/unsupported types constant/Nullable（FixedString（3））/*": [
        (
            Fail,
            f"base58 encode/decode is supported for FixedString(3) since 24.10: {pr_70846}",
            check_clickhouse_version(">=24.10"),
        )
    ],
    "/base58/unsupported types constant/FixedString（3）/*": [
        (
            Fail,
            f"base58 encode/decode is supported for FixedString(3) since 24.10: {pr_70846}",
            check_clickhouse_version(">=24.10"),
        )
    ],
    "/base58/unsupported types column/FixedString（3）/unsupported types/*": [
        (
            Fail,
            f"base58 encode/decode is supported for FixedString(3) since 24.10: {pr_70846}",
            check_clickhouse_version(">=24.10"),
        )
    ],
}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("base58")
@Specifications(SRS_ClickHouse_Base58_Encoding_and_Decoding)
@Requirements(RQ_ClickHouse_Base58_Encode("1.0"), RQ_ClickHouse_Base58_Decode("1.0"))
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    parallel=None,
    with_analyzer=False,
):
    """Base58 regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

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

    if parallel is not None:
        self.context.parallel = parallel

    if check_clickhouse_version("<22.7")(self):
        skip(reason="only supported on ClickHouse version >= 22.7")

    Feature(run=load("base_58.tests.consistency", "feature"))
    Feature(run=load("base_58.tests.null", "feature"))
    Feature(run=load("base_58.tests.alias_input", "feature"))
    Feature(run=load("base_58.tests.function_input", "feature"))
    Feature(run=load("base_58.tests.compatibility", "feature"))
    Feature(run=load("base_58.tests.memory_usage", "feature"))
    Feature(run=load("base_58.tests.performance", "feature"))
    Feature(run=load("base_58.tests.supported_types_constant", "feature"))
    Feature(run=load("base_58.tests.supported_types_column", "feature"))
    Feature(run=load("base_58.tests.unsupported_types_constant", "feature"))
    Feature(run=load("base_58.tests.unsupported_types_column", "feature"))


if main():
    regression()

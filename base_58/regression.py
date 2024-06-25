#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from base_58.requirements.requirements import *

from helpers.cluster import create_cluster
from helpers.argparser import argparser as argparser
from helpers.common import check_clickhouse_version, experimental_analyzer

xfails = {"alias input/alias instead of table and column": [(Fail, "not implemented")]}

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
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    keeper_binary_path=None,
    zookeeper_version=None,
    use_keeper=False,
    stress=None,
    parallel=None,
    with_analyzer=False,
):
    """Base58 regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            keeper_binary_path=keeper_binary_path,
            zookeeper_version=zookeeper_version,
            use_keeper=use_keeper,
            collect_service_logs=collect_service_logs,
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

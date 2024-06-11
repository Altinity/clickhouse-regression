#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from key_value.requirements.requirements import *
from helpers.argparser import argparser as argparser
from helpers.common import check_clickhouse_version, experimental_analyzer
from key_value.tests.constant import *

xfails = {}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("key value")
@Specifications(SRS033_ClickHouse_Key_Value_Function)
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function("1.0"))
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
    allow_vfs=False,
    with_analyzer=False,
):
    """Key Value regression."""
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

    if check_clickhouse_version("<23.5")(self):
        skip(reason="only supported on ClickHouse version >= 23.5")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    if parallel is not None:
        self.context.parallel = parallel

    Feature(run=load("key_value.tests.constant", "feature"))
    Feature(run=load("key_value.tests.column", "feature"))
    Feature(run=load("key_value.tests.map", "feature"))
    Feature(run=load("key_value.tests.array", "feature"))
    Feature(run=load("key_value.tests.special_symbols_conflict", "feature"))
    Feature(run=load("key_value.tests.supported_data_types", "feature"))
    Feature(run=load("key_value.tests.unsupported_data_types", "feature"))
    Feature(run=load("key_value.tests.parameters_format", "feature"))


if main():
    regression()

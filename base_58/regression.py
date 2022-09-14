#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from base_58.requirements.requirements import *
from helpers.argparser import argparser as argparser
from helpers.common import check_clickhouse_version

xfails = {}

xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("base58")
# @Specifications(SRS029_ClickHouse_Base58)
# @Requirements(
#     RQ_SRS_029_ClickHouse_Base58_Statement("1.0"),
# )
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    stress=None,
    parallel=None,
):
    """Base58 regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    with Cluster(
        local,
        clickhouse_binary_path,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(
            current_dir(), os.path.basename(current_dir()) + "_env"
        ),
    ) as cluster:
        self.context.cluster = cluster
        self.context.stress = stress

        if parallel is not None:
            self.context.parallel = parallel

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

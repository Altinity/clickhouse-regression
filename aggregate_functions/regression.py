#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser
from helpers.cluster import create_cluster
from helpers.common import check_clickhouse_version

from aggregate_functions.tests.steps import aggregate_functions
from aggregate_functions.requirements import SRS_031_ClickHouse_Aggregate_Functions

issue_43140 = "https://github.com/ClickHouse/ClickHouse/issues/43140"
issue_44511 = (
    "https://github.com/ClickHouse/ClickHouse/issues/44511",
    check_clickhouse_version(">=22.6"),
)
issue_47142 = "https://github.com/ClickHouse/ClickHouse/issues/47142"
issue_48917 = (
    "https://github.com/ClickHouse/ClickHouse/issues/48917",
    check_clickhouse_version(">=23.2"),
)
issue_55997 = "https://github.com/ClickHouse/ClickHouse/issues/55997"

xfails = {
    "/aggregate functions/singleValueOrNull/Map:": [(Fail, issue_43140)],
    "/aggregate functions/singleValueOrNull/Array:": [(Fail, issue_43140)],
    "/aggregate functions/singleValueOrNull/Tuple:": [(Fail, issue_43140)],
    "/aggregate functions/welchTTest/datatypes/permutations/float64:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/welchTTest/datatypes/permutations/nullable_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/welchTTest/datatypes/permutations/lowcardinality_nullable_float64__:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/welchTTest/datatypes/permutations/lowcardinality_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/studentTTest/datatypes/permutations/float64:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/studentTTest/datatypes/permutations/nullable_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/studentTTest/datatypes/permutations/lowcardinality_nullable_float64__:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/studentTTest/datatypes/permutations/lowcardinality_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/quantileTDigestWeighted/datatypes/permutations/date:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/quantileTDigestWeighted/datatypes/permutations/:_date_:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/state/topKWeightedState/datatypes/permutations/*": [
        (Fail, issue_55997)
    ],
    # 23.2
    "/aggregate functions/state/singleValueOrNullState/:": [
        (
            Fail,
            issue_47142,
            check_clickhouse_version(">=23"),
            r".*Exception: Nested type [^\n]+ cannot be inside Nullable type.*",
        )
    ],
}


@TestModule
@ArgumentParser(argparser)
@Name("aggregate functions")
@XFails(xfails)
@Specifications(SRS_031_ClickHouse_Aggregate_Functions)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    stress=None,
):
    """Aggregate functions regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            local=local,
            clickhouse_binary_path=clickhouse_binary_path,
            collect_service_logs=collect_service_logs,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    with And("table with all data types"):
        self.context.table = create_table(
            engine="MergeTree() ORDER BY tuple()", columns=generate_all_column_types()
        )

    with And("I populate table with test data"):
        self.context.table.insert_test_data()

    with Pool(5) as executor:
        for name in aggregate_functions:
            try:
                scenario = load(f"aggregate_functions.tests.{name}", "scenario")
            except ModuleNotFoundError:
                with Scenario(f"{name}"):
                    skip(reason=f"{name} test is not implemented")
                continue

            Scenario(test=scenario, parallel=True, executor=executor)()

        join()

    Feature(run=load("aggregate_functions.tests.state", "feature"))


if main():
    regression()

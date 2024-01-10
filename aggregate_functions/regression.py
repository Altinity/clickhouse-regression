#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser
from helpers.cluster import create_cluster
from helpers.common import check_clickhouse_version

from aggregate_functions.tests.steps import aggregate_functions, window_functions
from aggregate_functions.requirements import SRS_031_ClickHouse_Aggregate_Functions

issue_41176 = "https://github.com/ClickHouse/ClickHouse/issues/41176"
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
issue_57683 = "https://github.com/ClickHouse/ClickHouse/issues/57683"
issue_57801 = "https://github.com/ClickHouse/ClickHouse/issues/57801"

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
    "/aggregate functions/state/quantileTDigestWeightedState/datatypes/permutations/date:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/state/quantileTDigestWeightedState/datatypes/permutations/:_date_:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/state/topKWeightedState/datatypes/permutations/*": [
        (Fail, issue_55997)
    ],
    "/aggregate functions/state/maxIntersectionsState/*": [
        (
            Fail,
            "Another value on 22.8.13.22; needs to be investigated",
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/maxIntersectionsPositionState/*": [
        (
            Fail,
            "Another value on 22.8.13.22; needs to be investigated",
            check_clickhouse_version("<23"),
        )
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
    "/aggregate functions/:/quantilesGK:/:": [
        (
            Fail,
            issue_57683,
        )
    ],
    "/aggregate functions/merge/quantileGKMerge/*": [
        (
            Fail,
            "Need to investigate",
        )
    ],
}

ffails = {
    "/aggregate functions/window_functions/ntile/*": (
        Skip,
        "ntile works from 23.5",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/analysisOfVariance/*": (
        Skip,
        "analysisOfVariance works from 22.10",
        check_clickhouse_version("<=22.9"),
    ),
    "/aggregate functions/:/analysisOfVariance:/*": (
        Skip,
        "analysisOfVariance works from 22.10",
        check_clickhouse_version("<=22.9"),
    ),
    "/aggregate functions/corrMatrix/*": (
        Skip,
        "corrMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/:/corrMatrix:/*": (
        Skip,
        "corrMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/covarSampMatrix/*": (
        Skip,
        "covarSampMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/:/covarSampMatrix:/*": (
        Skip,
        "covarSampMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/covarPopMatrix/*": (
        Skip,
        "covarPopMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/:/covarPopMatrix:/*": (
        Skip,
        "covarPopMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/groupArrayLast/*": (
        Skip,
        "groupArrayLast works from 23",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/:/groupArrayLast:/*": (
        Skip,
        "groupArrayLast works from 23",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/kolmogorovSmirnovTest/*": (
        Skip,
        "kolmogorovSmirnovTest works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/:/kolmogorovSmirnovTest:/*": (
        Skip,
        "kolmogorovSmirnovTest works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/quantileGK/*": (
        Skip,
        "quantileGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/:/quantileGK:/*": (
        Skip,
        "quantileGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/quantilesGK/*": (
        Skip,
        "quantilesGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/:/quantilesGK:/*": (
        Skip,
        "quantilesGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/:/sequenceNextNode*Merge/*": (
        Skip,
        "sequenceNextNodeMerge needs to be done",
    ),
    "/aggregate functions/largestTriangleThreeBuckets/*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.10",
        check_clickhouse_version("<23.10"),
    ),
    "/aggregate functions/:/largestTriangleThreeBuckets*/*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.10",
        check_clickhouse_version("<23.10"),
    ),
    "/aggregate functions/merge/largestTriangleThreeBucketsMerge/*": (
        Skip,
        "largestTriangleThreeBuckets does not work with Merge, need to fix",
    ),
    "/aggregate functions/first_value_respect_nulls/*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/:/first_value_respect_nulls*/*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/last_value_respect_nulls/*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/:/last_value_respect_nulls*/*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/flameGraph/*": (
        Skip,
        "flameGraph works from 23.8",
        check_clickhouse_version("<23.8"),
    ),
    # states
    "/aggregate functions/state/sequenceNextNodeState/NULL value handling/*": (
        XFail,
        "need to invesigate",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/state/sequenceNextNodeState/single NULL value/*": (
        XFail,
        "need to invesigate",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/state/retentionState/NULL value handling/*": (
        XFail,
        issue_57801,
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/state/retentionState/single NULL value/*": (
        XFail,
        issue_57801,
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/state/sequenceCountState/NULL value handling/*": (
        XFail,
        issue_57801,
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/finalizeAggregation/studentTTest_finalizeAggregation_Merge/*": (
        XFail,
        issue_41176,
        check_clickhouse_version("<23.3"),
    ),
    "/aggregate functions/merge/studentTTestMerge/*": (
        XFail,
        issue_41176,
        check_clickhouse_version("<23.3"),
    ),
    "/aggregate functions/merge/topKWeightedMerge/*": (
        XFail,
        "need to invesigate fail on 23.3",
        check_clickhouse_version("<=23") and check_clickhouse_version(">=23"),
    ),
    "/aggregate functions/state/windowFunnelState/NULL value handling/*": (
        XFail,
        issue_57801,
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/state/windowFunnelState/single NULL value/*": (
        XFail,
        issue_57801,
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/state/sequenceMatchState/NULL value handling/*": (
        XFail,
        issue_57801,
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/float64:/*": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/nullable_float64_:/*": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/lowcardinality_nullable_float64__:/*": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/lowcardinality_float64_:/*": (
        Skip,
        *issue_44511,
    ),
}


@TestModule
@ArgumentParser(argparser)
@Name("aggregate functions")
@XFails(xfails)
@FFails(ffails)
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

    Feature(run=load("aggregate_functions.tests.function_list", "feature"))

    with Pool(5) as executor:
        for name in [
            name for name in aggregate_functions if name not in window_functions
        ]:
            try:
                scenario = load(f"aggregate_functions.tests.{name}", "scenario")
            except ModuleNotFoundError:
                with Scenario(f"{name}"):
                    skip(reason=f"{name} test is not implemented")
                continue

            Scenario(test=scenario, parallel=True, executor=executor)()

        join()

    Feature(run=load("aggregate_functions.tests.window_functions", "feature"))
    Feature(run=load("aggregate_functions.tests.aggThrow", "scenario"))
    Feature(run=load("aggregate_functions.tests.state", "feature"))
    Feature(run=load("aggregate_functions.tests.merge", "feature"))
    Feature(run=load("aggregate_functions.tests.finalizeAggregation", "feature"))


if main():
    regression()

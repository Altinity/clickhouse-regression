#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.tables import *
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.cluster import create_cluster
from helpers.common import *

from aggregate_functions.tests.steps import (
    aggregate_functions,
    window_functions,
    funcs_to_run_with_extra_data,
)
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
issue_58727 = "https://github.com/ClickHouse/ClickHouse/issues/58727"
issue_58741 = "https://github.com/ClickHouse/ClickHouse/issues/58741"
issue_64745 = "https://github.com/ClickHouse/ClickHouse/issues/64745"

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
    "/aggregate functions/state/topKWeightedState/datatypes/permutations/:": [
        (Fail, issue_55997)
    ],
    "/aggregate functions/state/maxIntersectionsState/:": [
        (
            Fail,
            "Another value on 22.8.13.22; needs to be investigated",
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/maxIntersectionsPositionState/:": [
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
    "/aggregate functions/sumMapFiltered/inf, -inf, nan/*": [
        (
            Fail,
            issue_58741,
            check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
        )
    ],
    "/aggregate functions/sumMapFilteredWithOverflow/inf, -inf, nan/*": [
        (
            Fail,
            issue_58741,
            check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
        )
    ],
    "/aggregate functions/simpleLinearRegression/*": [
        (
            Fail,
            "need to investigate on aarch",
            check_clickhouse_version(">=23.11") and check_current_cpu("aarch64"),
        )
    ],
    "/aggregate functions/:/simpleLinearRegression*/*": [
        (
            Fail,
            "need to investigate on aarch",
            check_clickhouse_version(">=23.11") and check_current_cpu("aarch64"),
        )
    ],
    "/aggregate functions/state/corrStableState/inf, -inf, nan/nan,inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/state/corrStableState/inf, -inf, nan/nan,-inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/state/covarPopStableState/inf, -inf, nan/nan,inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/state/covarPopStableState/inf, -inf, nan/nan,-inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/state/covarSampStableState/inf, -inf, nan/nan,inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/state/covarSampStableState/inf, -inf, nan/nan,-inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/merge/welchTTestMerge/*": [
        (
            Fail,
            "Error in function boost::math::students_t_distribution<double>",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/aggregate functions/finalizeAggregation/welchTTest_finalizeAggregation_Merge/*": [
        (
            Fail,
            "Error in function boost::math::students_t_distribution<double>",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/aggregate functions/state/sequenceNextNodeState/NULL value handling/*": [
        (
            Fail,
            "need to investigate",
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/sequenceNextNodeState/single NULL value/*": [
        (
            Fail,
            "need to investigate",
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/retentionState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/retentionState/single NULL value/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/sequenceCountState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/:/studentTTest*Merge/*": [
        (
            Fail,
            issue_41176,
            check_clickhouse_version("<23.3"),
        )
    ],
    "/aggregate functions/state/windowFunnelState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/windowFunnelState/single NULL value/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/state/sequenceMatchState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
}

ffails = {
    "/aggregate functions/window_functions/ntile": (
        Skip,
        "ntile works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/analysisOfVariance": (
        Skip,
        "analysisOfVariance works from 22.10",
        check_clickhouse_version("<=22.9"),
    ),
    "/aggregate functions/:/analysisOfVariance:": (
        Skip,
        "analysisOfVariance works from 22.10",
        check_clickhouse_version("<=22.9"),
    ),
    "/aggregate functions/corrMatrix": (
        Skip,
        "corrMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/:/corrMatrix:": (
        Skip,
        "corrMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/covarSampMatrix": (
        Skip,
        "covarSampMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/:/covarSampMatrix:": (
        Skip,
        "covarSampMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/covarPopMatrix": (
        Skip,
        "covarPopMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/:/covarPopMatrix:": (
        Skip,
        "covarPopMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/groupArrayLast": (
        Skip,
        "groupArrayLast works from 23",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/:/groupArrayLast:": (
        Skip,
        "groupArrayLast works from 23",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/groupArrayIntersect": (
        Skip,
        "groupArrayIntersect works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/:/*groupArrayIntersect*": (
        Skip,
        "groupArrayIntersect works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/groupArraySorted": (
        Skip,
        "groupArraySorted works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/:/*groupArraySorted*": (
        Skip,
        "groupArraySorted works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/kolmogorovSmirnovTest": (
        Skip,
        "kolmogorovSmirnovTest works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/:/kolmogorovSmirnovTest:": (
        Skip,
        "kolmogorovSmirnovTest works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/quantileGK": (
        Skip,
        "quantileGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/:/quantileGK:": (
        Skip,
        "quantileGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/quantilesGK": (
        Skip,
        "quantilesGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/:/quantilesGK:": (
        Skip,
        "quantilesGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/largestTriangleThreeBuckets": (
        Skip,
        "largestTriangleThreeBuckets works from 23.10",
        check_clickhouse_version("<23.10"),
    ),
    "/aggregate functions/:/largestTriangleThreeBuckets*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.10",
        check_clickhouse_version("<23.10"),
    ),
    "/aggregate functions/first_value_respect_nulls": (
        Skip,
        "first_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/:/first_value_respect_nulls*": (
        Skip,
        "first_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/last_value_respect_nulls": (
        Skip,
        "last_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/:/last_value_respect_nulls*": (
        Skip,
        "last_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/flameGraph": (
        Skip,
        "flameGraph works from 23.8",
        check_clickhouse_version("<23.8"),
    ),
    "/aggregate functions/:/flameGraph*": (
        Skip,
        "flameGraph works from 23.8",
        check_clickhouse_version("<23.8"),
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/float64:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/nullable_float64_:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/lowcardinality_nullable_float64__:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/state/welchTTestState/datatypes/permutations/lowcardinality_float64_:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/:/sumMapFiltered*/inf, -inf, nan": (
        Skip,
        issue_58741,
        check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
    ),
    "/aggregate functions/:/sumMapFilteredWithOverflow*/inf, -inf, nan": (
        Skip,
        issue_58741,
        check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
    ),
    "/aggregate functions/largestTriangleThreeBuckets/inf, -inf, nan": (
        Skip,
        issue_64745,
        check_clickhouse_version(">=23.11"),
    ),
    "/aggregate functions/state/largestTriangleThreeBucketsState/inf, -inf, nan": (
        Skip,
        issue_64745,
        check_clickhouse_version(">=23.11"),
    ),
    "/aggregate functions/approx_top_k": (
        Skip,
        "approx_top_k works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/:/*approx_top_k*": (
        Skip,
        "approx_top_k works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/approx_top_sum": (
        Skip,
        "approx_top_sum works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/:/*approx_top_sum*": (
        Skip,
        "approx_top_sum works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/groupConcat": (
        Skip,
        "groupConcat was introduced in 24.7",
        check_clickhouse_version("<24.7"),
    ),
    "/aggregate functions/:/*groupConcat*": (
        Skip,
        "groupConcat was introduced in 24.7",
        check_clickhouse_version("<24.7"),
    ),
}


@TestModule
@ArgumentParser(argparser)
@Name("aggregate functions")
@XFails(xfails)
@FFails(ffails)
@Specifications(SRS_031_ClickHouse_Aggregate_Functions)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """Aggregate functions regression suite."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            docker_compose_project_dir=os.path.join(
                current_dir(), os.path.basename(current_dir()) + "_env"
            ),
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster
        self.context.node = cluster.node("clickhouse1")

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with And("tables with all data types"):
        self.context.table = create_table(
            engine="MergeTree",
            columns=generate_all_column_types(),
            order_by_all_columns=False,
            order_by="tuple()",
        )
        self.context.table_extra_data = create_table(
            engine="MergeTree",
            columns=generate_all_column_types(),
            order_by_all_columns=False,
            order_by="tuple()",
        )

    with And("I populate tables with test data"):
        self.context.table.insert_test_data(cardinality=1, shuffle_values=False)
        self.context.table_extra_data.insert_test_data(
            cardinality=5, shuffle_values=True
        )

    Feature(run=load("aggregate_functions.tests.function_list", "feature"))

    with Pool(10) as executor:
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

    Feature(run=load("aggregate_functions.tests.state", "feature"))

    with Pool(5) as executor:
        Feature(
            test=load("aggregate_functions.tests.merge", "feature"),
            parallel=True,
            executor=executor,
        )()
        Feature(
            test=load("aggregate_functions.tests.finalizeAggregation", "feature"),
            parallel=True,
            executor=executor,
        )()
        Feature(
            test=load("aggregate_functions.tests.window_functions", "feature"),
            parallel=True,
            executor=executor,
        )()
        # Feature(
        #     test=load(
        #         "aggregate_functions.tests.combinators.argMinCombinator_const_expr",
        #         "feature",
        #     ),
        #     parallel=True,
        #     executor=executor,
        # )()
        # Feature(
        #     test=load(
        #         "aggregate_functions.tests.combinators.argMinStateCombinator_const_expr",
        #         "feature",
        #     ),
        #     parallel=True,
        #     executor=executor,
        # )()
        # Feature(
        #     test=load(
        #         "aggregate_functions.tests.argMinMergeCombinator_const_expr",
        #         "feature",
        #     ),
        #     parallel=True,
        #     executor=executor,
        # )()
        # Feature(
        #     test=load(
        #         "aggregate_functions.tests.combinators.argMaxCombinator_const_expr",
        #         "feature",
        #     ),
        #     parallel=True,
        #     executor=executor,
        # )()
        # Feature(
        #     test=load(
        #         "aggregate_functions.tests.combinators.argMaxStateCombinator_const_expr",
        #         "feature",
        #     ),
        #     parallel=True,
        #     executor=executor,
        # )()
        join()

    # Feature(test=load("aggregate_functions.tests.run_with_extra_data", "feature"))(table=self.context.table_extra_data)


if main():
    regression()

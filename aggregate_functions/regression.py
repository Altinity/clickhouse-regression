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

issue_41057 = "https://github.com/ClickHouse/ClickHouse/issues/41057"
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
issue_69192 = "https://github.com/ClickHouse/ClickHouse/issues/69192"

xfails = {
    "/aggregate functions/part */singleValueOrNull/Map:": [(Fail, issue_43140)],
    "/aggregate functions/part */singleValueOrNull/Array:": [(Fail, issue_43140)],
    "/aggregate functions/part */singleValueOrNull/Tuple:": [(Fail, issue_43140)],
    "/aggregate functions/part */welchTTest/datatypes/permutations/float64:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */welchTTest/datatypes/permutations/nullable_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */welchTTest/datatypes/permutations/lowcardinality_nullable_float64__:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */welchTTest/datatypes/permutations/lowcardinality_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */studentTTest/datatypes/permutations/float64:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */studentTTest/datatypes/permutations/nullable_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */studentTTest/datatypes/permutations/lowcardinality_nullable_float64__:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */studentTTest/datatypes/permutations/lowcardinality_float64_:": [
        (Fail, *issue_44511)
    ],
    "/aggregate functions/part */quantileTDigestWeighted/datatypes/permutations/date:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/part */quantileTDigestWeighted/datatypes/permutations/:_date_:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/part */state/quantileTDigestWeightedState/datatypes/permutations/date:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/part */state/quantileTDigestWeightedState/datatypes/permutations/:_date_:": [
        (Fail, "DECIMAL_OVERFLOW error that needs to be investigated")
    ],
    "/aggregate functions/part */state/topKWeightedState/datatypes/permutations/:": [
        (Fail, issue_55997)
    ],
    "/aggregate functions/part */state/maxIntersectionsState/:": [
        (
            Fail,
            "Another value on 22.8.13.22; needs to be investigated",
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */state/maxIntersectionsPositionState/:": [
        (
            Fail,
            "Another value on 22.8.13.22; needs to be investigated",
            check_clickhouse_version("<23"),
        )
    ],
    # 23.2
    "/aggregate functions/part */state/singleValueOrNullState/:": [
        (
            Fail,
            issue_47142,
            check_clickhouse_version(">=23"),
            r".*Exception: Nested type [^\n]+ cannot be inside Nullable type.*",
        )
    ],
    "/aggregate functions/part */:/quantilesGK:/:": [
        (
            Fail,
            issue_57683,
        )
    ],
    "/aggregate functions/part */merge/quantileGKMerge/*": [
        (
            Fail,
            "Need to investigate",
        )
    ],
    "/aggregate functions/part */sumMapFiltered/inf, -inf, nan/*": [
        (
            Fail,
            issue_58741,
            check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
        )
    ],
    "/aggregate functions/part */sumMapFilteredWithOverflow/inf, -inf, nan/*": [
        (
            Fail,
            issue_58741,
            check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
        )
    ],
    "/aggregate functions/part */simpleLinearRegression/*": [
        (
            Fail,
            "need to investigate on aarch",
            check_clickhouse_version(">=23.11") and check_current_cpu("aarch64"),
        )
    ],
    "/aggregate functions/part */:/simpleLinearRegression*/*": [
        (
            Fail,
            "need to investigate on aarch",
            check_clickhouse_version(">=23.11") and check_current_cpu("aarch64"),
        )
    ],
    "/aggregate functions/part */state/corrStableState/inf, -inf, nan/nan,inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/part */state/corrStableState/inf, -inf, nan/nan,-inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/part */state/covarPopStableState/inf, -inf, nan/nan,inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/part */state/covarPopStableState/inf, -inf, nan/nan,-inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/part */state/covarSampStableState/inf, -inf, nan/nan,inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/part */state/covarSampStableState/inf, -inf, nan/nan,-inf/*": [
        (Fail, "different state representation of nan", check_current_cpu("x86_64"))
    ],
    "/aggregate functions/part */merge/welchTTestMerge/*": [
        (
            Fail,
            "Error in function boost::math::students_t_distribution<double>",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/aggregate functions/part */finalizeAggregation/welchTTest_finalizeAggregation_Merge/*": [
        (
            Fail,
            "Error in function boost::math::students_t_distribution<double>",
            check_clickhouse_version("<22.9"),
        )
    ],
    "/aggregate functions/part */state/sequenceNextNodeState/NULL value handling/*": [
        (
            Fail,
            "need to investigate",
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */state/sequenceNextNodeState/single NULL value/*": [
        (
            Fail,
            "need to investigate",
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */state/retentionState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */state/retentionState/single NULL value/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */state/sequenceCountState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */:/studentTTest*Merge/*": [
        (
            Fail,
            issue_41176,
            check_clickhouse_version("<23.3"),
        )
    ],
    "/aggregate functions/part */state/windowFunnelState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */state/windowFunnelState/single NULL value/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */state/sequenceMatchState/NULL value handling/*": [
        (
            Fail,
            issue_57801,
            check_clickhouse_version("<23"),
        )
    ],
    "/aggregate functions/part */sumMapFiltered/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/sumMapFilteredState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */sumMapFilteredWithOverflow/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/sumMapFilteredWithOverflowState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */sumMapWithOverflow/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/sumMapWithOverflowState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */sumMappedArrays/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/sumMappedArraysState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */sumMap_alias/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/sumMap_aliasState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */maxMappedArrays/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/maxMappedArraysState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */maxMap_alias/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/maxMap_aliasState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */minMappedArrays/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/minMappedArraysState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */minMap_alias/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/minMap_aliasState/datatypes/permutations/*LowCardinality*": [
        (
            Fail,
            issue_41057,
            check_clickhouse_version("<22.6"),
        )
    ],
    "/aggregate functions/part */state/maxIntersectionsPositionState/datatypes/permutations/Nullable（Float32）,Nullable（Float32）/*": [
        (
            Fail,
            "Different intermediate state representation of zero",
            check_clickhouse_version("<22.4"),
        )
    ],
    "/aggregate functions/part */state/maxIntersectionsPositionState/datatypes/permutations/LowCardinality（Float32）,LowCardinality（Float32）/*": [
        (
            Fail,
            "Different intermediate state representation of zero",
            check_clickhouse_version("<22.4"),
        )
    ],
    "/aggregate functions/part */state/maxIntersectionsState/datatypes/permutations/Nullable（Float32）,Nullable（Float32）/*": [
        (
            Fail,
            "Different intermediate state representation of zero",
            check_clickhouse_version("<22.4"),
        )
    ],
    "/aggregate functions/part */state/maxIntersectionsState/datatypes/permutations/LowCardinality（Float32）,LowCardinality（Float32）/*": [
        (
            Fail,
            "Different intermediate state representation of zero",
            check_clickhouse_version("<22.4"),
        )
    ],
    "/aggregate functions/part */state/maxIntersectionsState/datatypes/permutations/Float32,Float32/*": [
        (
            Fail,
            "Different intermediate state representation of zero",
            check_clickhouse_version("<22.4"),
        )
    ],
    "/aggregate functions/part */state/maxIntersectionsPositionState/datatypes/permutations/Float32,Float32/*": [
        (
            Fail,
            "Different intermediate state representation of zero",
            check_clickhouse_version("<22.4"),
        )
    ],
    "/aggregate functions/part */mannWhitneyUTest/*": [
        (
            Fail,
            issue_69192,
            check_clickhouse_version(">=24.9"),
        )
    ],
    "/aggregate functions/part */merge/mannWhitneyUTestMerge/*": [
        (
            Fail,
            issue_69192,
            check_clickhouse_version(">=24.9"),
        )
    ],
    "/aggregate functions/part */finalizeAggregation/mannWhitneyUTest_finalizeAggregation_Merge/*": [
        (
            Fail,
            issue_69192,
            check_clickhouse_version(">=24.9"),
        )
    ],
    "/aggregate functions/part */function_list/untested function distinctJSONPathsAndTypes": [
        (
            Fail,
            "Tests are not implemented for distinctJSONPathsAndTypes function.",
            check_clickhouse_version(">=24.9"),
        ),
    ],
    "/aggregate functions/part */function_list/untested function distinctJSONPaths": [
        (
            Fail,
            "Tests are not implemented for distinctJSONPaths function.",
            check_clickhouse_version(">=24.9"),
        ),
    ],
    "/aggregate functions/part */function_list/untested function distinctDynamicTypes": [
        (
            Fail,
            "Tests are not implemented for distinctDynamicTypes function.",
            check_clickhouse_version(">=24.9"),
        ),
    ],
    "/aggregate functions/part */function_list/untested function estimateCompressionRatio": [
        (
            Fail,
            "Tests are not implemented for estimateCompressionRatio function.",
            check_clickhouse_version(">=25.3"),
        ),
    ],
    "/aggregate functions/part */deltaSumTimestamp/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/72189",
            check_clickhouse_version(">=24.11"),
        )
    ],
    "/aggregate functions/part */state/deltaSumTimestampState/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/72189",
            check_clickhouse_version(">=24.11"),
        )
    ],
    "/aggregate functions/part */finalizeAggregation/deltaSumTimestamp_finalizeAggregation_Merge/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/72189",
            check_clickhouse_version(">=24.11"),
        )
    ],
    "/aggregate functions/part */merge/deltaSumTimestampMerge/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/72189",
            check_clickhouse_version(">=24.11"),
        )
    ],
    "/aggregate functions/part */state/*": [
        (
            Fail,
            "Not deterministic, need to investigate",
            check_clickhouse_version(">=25.1"),
        )
    ],
}


ffails = {
    "/aggregate functions/part */window_functions/ntile": (
        Skip,
        "ntile works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/part */window_functions/nonNegativeDerivative": (
        Skip,
        "nonNegativeDerivative was introduced in 22.6",
        check_clickhouse_version("<22.6"),
    ),
    "/aggregate functions/part */window_functions/nth value": (
        Skip,
        "nth value was introduced in 22.5",
        check_clickhouse_version("<22.5"),
    ),
    "/aggregate functions/part */analysisOfVariance": (
        Skip,
        "analysisOfVariance works from 22.10",
        check_clickhouse_version("<=22.9"),
    ),
    "/aggregate functions/part */:/analysisOfVariance:": (
        Skip,
        "analysisOfVariance works from 22.10",
        check_clickhouse_version("<=22.9"),
    ),
    "/aggregate functions/part */corrMatrix": (
        Skip,
        "corrMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/part */:/corrMatrix:": (
        Skip,
        "corrMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/part */covarSampMatrix": (
        Skip,
        "covarSampMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/part */:/covarSampMatrix:": (
        Skip,
        "covarSampMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/part */covarPopMatrix": (
        Skip,
        "covarPopMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/part */:/covarPopMatrix:": (
        Skip,
        "covarPopMatrix works from 23.2",
        check_clickhouse_version("<=23.1"),
    ),
    "/aggregate functions/part */groupArrayLast": (
        Skip,
        "groupArrayLast works from 23",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/part */:/groupArrayLast:": (
        Skip,
        "groupArrayLast works from 23",
        check_clickhouse_version("<23"),
    ),
    "/aggregate functions/part */groupArrayIntersect": (
        Skip,
        "groupArrayIntersect works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/part */:/*groupArrayIntersect*": (
        Skip,
        "groupArrayIntersect works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/part */groupArraySorted": (
        Skip,
        "groupArraySorted works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/part */:/*groupArraySorted*": (
        Skip,
        "groupArraySorted works from 24.2",
        check_clickhouse_version("<=24.1"),
    ),
    "/aggregate functions/part */kolmogorovSmirnovTest": (
        Skip,
        "kolmogorovSmirnovTest works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/part */:/kolmogorovSmirnovTest:": (
        Skip,
        "kolmogorovSmirnovTest works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/part */quantileGK": (
        Skip,
        "quantileGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/part */:/quantileGK:": (
        Skip,
        "quantileGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/part */quantilesGK": (
        Skip,
        "quantilesGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/part */:/quantilesGK:": (
        Skip,
        "quantilesGK works from 23.4",
        check_clickhouse_version("<23.4"),
    ),
    "/aggregate functions/part */largestTriangleThreeBuckets": (
        Skip,
        "largestTriangleThreeBuckets works from 23.10",
        check_clickhouse_version("<23.10"),
    ),
    "/aggregate functions/part */:/largestTriangleThreeBuckets*": (
        Skip,
        "largestTriangleThreeBuckets works from 23.10",
        check_clickhouse_version("<23.10"),
    ),
    "/aggregate functions/part */first_value_respect_nulls": (
        Skip,
        "first_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/part */:/first_value_respect_nulls*": (
        Skip,
        "first_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/part */last_value_respect_nulls": (
        Skip,
        "last_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/part */:/last_value_respect_nulls*": (
        Skip,
        "last_value_respect_nulls works from 23.5",
        check_clickhouse_version("<23.5"),
    ),
    "/aggregate functions/part */flameGraph": (
        Skip,
        "flameGraph works from 23.8",
        check_clickhouse_version("<23.8"),
    ),
    "/aggregate functions/part */:/flameGraph*": (
        Skip,
        "flameGraph works from 23.8",
        check_clickhouse_version("<23.8"),
    ),
    "/aggregate functions/part */state/welchTTestState/datatypes/permutations/float64:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/part */state/welchTTestState/datatypes/permutations/nullable_float64_:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/part */state/welchTTestState/datatypes/permutations/lowcardinality_nullable_float64__:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/part */state/welchTTestState/datatypes/permutations/lowcardinality_float64_:": (
        Skip,
        *issue_44511,
    ),
    "/aggregate functions/part */:/sumMapFiltered*/inf, -inf, nan": (
        Skip,
        issue_58741,
        check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
    ),
    "/aggregate functions/part */:/sumMapFilteredWithOverflow*/inf, -inf, nan": (
        Skip,
        issue_58741,
        check_clickhouse_version(">=23.11") and check_clickhouse_version("<24"),
    ),
    "/aggregate functions/part */largestTriangleThreeBuckets/inf, -inf, nan": (
        Skip,
        issue_64745,
        check_clickhouse_version(">=23.11"),
    ),
    "/aggregate functions/part */state/largestTriangleThreeBucketsState/inf, -inf, nan": (
        Skip,
        issue_64745,
        check_clickhouse_version(">=23.11"),
    ),
    "/aggregate functions/part */approx_top_k": (
        Skip,
        "approx_top_k works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/part */:/*approx_top_k*": (
        Skip,
        "approx_top_k works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/part */approx_top_sum": (
        Skip,
        "approx_top_sum works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/part */:/*approx_top_sum*": (
        Skip,
        "approx_top_sum works from 24.3",
        check_clickhouse_version("<24.3"),
    ),
    "/aggregate functions/part */groupConcat": (
        Skip,
        "groupConcat was introduced in 24.7",
        check_clickhouse_version("<24.7"),
    ),
    "/aggregate functions/part */:/*groupConcat*": (
        Skip,
        "groupConcat was introduced in 24.7",
        check_clickhouse_version("<24.7"),
    ),
    "/aggregate functions/part */function_list/untested function quantilesExactWeightedInterpolated": (
        Skip,
        "quantilesExactWeightedInterpolated test is not implemented",
        check_clickhouse_version(">=24.10"),
    ),
    "/aggregate functions/part */function_list/untested function quantileExactWeightedInterpolated": (
        Skip,
        "quantileExactWeightedInterpolated test is not implemented",
        check_clickhouse_version(">=24.10"),
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesInstantDeltaToGrid": (
        Skip,
        "timeSeriesInstantDeltaToGrid test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesInstantRateToGrid": (
        Skip,
        "timeSeriesInstantRateToGrid test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesRateToGrid": (
        Skip,
        "timeSeriesRateToGrid test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function groupNumericIndexedVector": (
        Skip,
        "groupNumericIndexedVector test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesResampleToGridWithStaleness": (
        Skip,
        "timeSeriesResampleToGridWithStaleness test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesDeltaToGrid": (
        Skip,
        "timeSeriesDeltaToGrid test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesLastTwoSamples": (
        Skip,
        "timeSeriesLastTwoSamples test is not implemented",
    ),
    "/aggregate functions/part */:/*sequenceMatchEvents*": (
        Skip,
        "sequenceMatchEvents was introduced in 25.1",
        check_clickhouse_version("<25.1"),
    ),
    "/aggregate functions/part */sequenceMatchEvents": (
        Skip,
        "sequenceMatchEvents was introduced in 25.1",
        check_clickhouse_version("<25.1"),
    ),
    "/aggregate functions/part 1/function_list/untested function lead": (
        Skip,
        "Test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function lag": (
        Skip,
        "Test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesPredictLinearToGrid": (
        Skip,
        "timeSeriesPredictLinearToGrid test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesDerivToGrid": (
        Skip,
        "timeSeriesDerivToGrid test is not implemented",
    ),
    "/aggregate functions/part 1/function_list/untested function timeSeriesGroupArray": (
        Skip,
        "timeSeriesGroupArray test is not implemented",
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

    with And("allow higher cpu_wait_ratio "):
        if check_clickhouse_version(">=25.4")(self):
            allow_higher_cpu_wait_ratio(
                min_os_cpu_wait_time_ratio_to_throw=10,
                max_os_cpu_wait_time_ratio_to_throw=20,
            )

    with Feature("part 1"):
        Feature(run=load("aggregate_functions.tests.function_list", "feature"))
        with Pool() as executor:
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

    with Feature("part 2"):
        with Pool(3) as executor:
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
            Feature(
                test=load("aggregate_functions.tests.run_with_extra_data", "feature"),
                parallel=True,
                executor=executor,
            )(table=self.context.table_extra_data)
            join()

    with Feature("part 3"):
        with Pool(2) as executor:
            Feature(
                test=load("aggregate_functions.tests.state", "feature"),
                parallel=True,
                executor=executor,
            )()
            Feature(
                test=load("aggregate_functions.tests.merge", "feature"),
                parallel=True,
                executor=executor,
            )()
            join()


if main():
    regression()

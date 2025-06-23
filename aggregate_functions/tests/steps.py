import itertools
import json

from testflows.core import *
from testflows.asserts import values, error, snapshot

from helpers.common import (
    check_clickhouse_version,
    check_current_cpu,
    get_snapshot_id,
    getuid,
    current_cpu,
    is_with_analyzer,
    check_analyzer,
)

# exhaustive list of all aggregate functions
aggregate_functions = [
    "aggThrow",
    "analysisOfVariance",
    "any",
    "anyLast_respect_nulls",
    "any_respect_nulls",
    "anyHeavy",
    "anyLast",
    "approx_top_k",
    "approx_top_sum",
    "argMax",
    "argMin",
    "avg",
    "avgWeighted",
    "boundingRatio",
    "categoricalInformationValue",
    "contingency",
    "corr",
    "corrMatrix",
    "corrStable",
    "count",
    "covarPop",
    "covarPopMatrix",
    "covarPopStable",
    "covarSamp",
    "covarSampMatrix",
    "covarSampStable",
    "cramersV",
    "cramersVBiasCorrected",
    "deltaSum",
    "deltaSumTimestamp",
    "dense_rank",
    "denseRank",
    "entropy",
    "exponentialMovingAverage",
    "exponentialTimeDecayedAvg",
    "exponentialTimeDecayedCount",
    "exponentialTimeDecayedMax",
    "exponentialTimeDecayedSum",
    "first_value",
    "first_value_respect_nulls",
    "flameGraph",
    "groupArray",
    "groupArrayInsertAt",
    "groupArrayIntersect",
    "groupArrayLast",
    "groupArrayMovingAvg",
    "groupArrayMovingSum",
    "groupArraySample",
    "groupArraySorted",
    "groupBitAnd",
    "groupBitOr",
    "groupBitXor",
    "groupBitmap",
    "groupBitmapAnd",
    "groupBitmapOr",
    "groupBitmapXor",
    "groupConcat",
    "groupUniqArray",
    "histogram",
    "intervalLengthSum",
    "kolmogorovSmirnovTest",
    "kurtPop",
    "kurtSamp",
    "lagInFrame",
    "largestTriangleThreeBuckets",
    "last_value",
    "last_value_respect_nulls",
    "leadInFrame",
    "mannWhitneyUTest",
    "max",
    "maxIntersections",
    "maxIntersectionsPosition",
    "maxMap",
    "maxMap_alias",
    "maxMappedArrays",
    "meanZTest",
    "minMap",
    "min",
    "minMap_alias",
    "minMappedArrays",
    "nonNegativeDerivative",
    "nothing",
    "nothingNull",
    "nothingUInt64",
    "nth_value",
    "ntile",
    "percent_rank",
    "percentRank",
    "quantile",
    "quantileBFloat16",
    "quantileBFloat16Weighted",
    "quantileDD",
    "quantileDeterministic",
    "quantileExact",
    "quantileExactExclusive",
    "quantileExactHigh",
    "quantileExactInclusive",
    "quantileExactLow",
    "quantileExactWeighted",
    "quantileGK",
    "quantileInterpolatedWeighted",
    "quantileTDigest",
    "quantileTDigestWeighted",
    "quantileTiming",
    "quantileTimingWeighted",
    "quantiles",
    "quantilesBFloat16",
    "quantilesBFloat16Weighted",
    "quantilesDD",
    "quantilesDeterministic",
    "quantilesExact",
    "quantilesExactExclusive",
    "quantilesExactHigh",
    "quantilesExactInclusive",
    "quantilesExactLow",
    "quantilesExactWeighted",
    "quantilesGK",
    "quantilesInterpolatedWeighted",
    "quantilesTDigest",
    "quantilesTDigestWeighted",
    "quantilesTiming",
    "quantilesTimingWeighted",
    "rank",
    "rankCorr",
    "retention",
    "row_number",
    "sequenceCount",
    "sequenceMatch",
    "sequenceMatchEvents",
    "sequenceNextNode",
    "simpleLinearRegression",
    "singleValueOrNull",
    "skewPop",
    "skewSamp",
    "sparkbar",
    "stddevPop",
    "stddevPopStable",
    "stddevSamp",
    "stddevSampStable",
    "stochasticLinearRegression",
    "stochasticLogisticRegression",
    "studentTTest",
    "sum",
    "sumCount",
    "sumKahan",
    "sumMapFiltered",
    "sumMapFilteredWithOverflow",
    "sumMapWithOverflow",
    "sumMappedArrays",
    "sumMap_alias",
    "sumMap",
    "sumWithOverflow",
    "theilsU",
    "topK",
    "topKWeighted",
    "uniq",
    "uniqCombined",
    "uniqCombined64",
    "uniqExact",
    "uniqHLL12",
    "uniqTheta",
    "uniqUpTo",
    "varPop",
    "varPopStable",
    "varSamp",
    "varSampStable",
    "welchTTest",
    "windowFunnel",
]


window_functions = [
    "row_number",
    "nth_value",
    "ntile",
    "rank",
    "dense_rank",
    "denseRank",
    "lagInFrame",
    "leadInFrame",
    "exponentialTimeDecayedSum",
    "exponentialTimeDecayedMax",
    "exponentialTimeDecayedCount",
    "exponentialTimeDecayedAvg",
    "nonNegativeDerivative",
    "percent_rank",
    "percentRank",
]

parametric = [
    "approx_top_k",
    "approx_top_sum",
    "exponentialMovingAverage",
    "groupArrayLast",
    "groupArraySample",
    "groupArraySorted",
    "histogram",
    "kolmogorovSmirnovTest",
    "mannWhitneyUTest",
    "meanZTest",
    "quantileGK",
    "quantiles",
    "quantilesBFloat16",
    "quantilesBFloat16Weighted",
    "quantilesDeterministic",
    "quantilesExact",
    "quantilesExactExclusive",
    "quantilesExactHigh",
    "quantilesExactInclusive",
    "quantilesExactLow",
    "quantilesExactWeighted",
    "quantilesGK",
    "quantilesInterpolatedWeighted",
    "quantilesTDigest",
    "quantilesTDigestWeighted",
    "quantilesTiming",
    "quantilesTimingWeighted",
    "sparkbar",
    "sumMapFiltered",
    "topK",
    "topKWeighted",
    "uniqUpTo",
    "windowFunnel",
    "largestTriangleThreeBuckets",
]

funcs_to_run_with_extra_data = ["argMin", "argMax"]


def permutations_with_replacement(n, r):
    """Return all possible permutations with replacement."""
    return itertools.product(n, repeat=r)


def execute_query(
    sql,
    expected=None,
    exitcode=None,
    message=None,
    no_checks=False,
    snapshot_name=None,
    format="JSONEachRow",
    use_file=False,
    hash_output=False,
    timeout=None,
    settings=None,
    use_result_in_snapshot_name=None,
):
    """Execute SQL query and compare the output to the snapshot."""
    if settings is None:
        settings = [("allow_suspicious_low_cardinality_types", 1)]

    if snapshot_name is None:
        snapshot_name = (
            current()
            .name.replace("/part 1", "")
            .replace("/part 2", "")
            .replace("/part 3", "")
        )

    if "DateTime64" in snapshot_name:
        if check_clickhouse_version(">=22.8")(current()):
            snapshot_name += ">=22.8"

    if message is None and exitcode is None:
        assert (
            "snapshot_id" in current().context
        ), "test must set self.context.snapshot_id"

    with When("I execute query", description=sql):
        note(sql)
        if format and not "FORMAT" in sql:
            sql += " FORMAT " + format

        r = current().context.node.query(
            sql,
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
            use_file=use_file,
            hash_output=hash_output,
            timeout=timeout,
            settings=settings,
        )
        if no_checks:
            return r

    if use_result_in_snapshot_name:
        result = json.loads(r.output)
        result_value = list(result.values())[0]
        snapshot_name += f"_{result_value}"

    if message is None:
        if expected is not None:
            with Then("I check output against expected"):
                assert r.output.strip() == expected, error()
        else:
            with Then("I check only json values if compare_json_values is set"):
                if hasattr(current().context, "compare_json_values"):
                    if hasattr(current().context, "replace_part"):
                        current().context.replace_with = getsattr(
                            current().context, "replace_with", ""
                        )
                        snapshot_name = snapshot_name.replace(
                            current().context.replace_part,
                            current().context.replace_with,
                        )

                    snapshot_value = snapshot(
                        value="\n" + r.output.strip() + "\n",
                        id=current().context.snapshot_id + "." + current_cpu(),
                        name=snapshot_name,
                        encoder=str,
                        mode=snapshot.CHECK,
                    ).snapshot_value
                    compare_json_values(current=r.output, expected=snapshot_value)
                    return

            with Then("I check output against snapshot"):
                with values() as that:
                    assert that(
                        snapshot(
                            "\n" + r.output.strip() + "\n",
                            id=current().context.snapshot_id + "." + current_cpu(),
                            name=snapshot_name,
                            encoder=str,
                            mode=snapshot.CHECK,  # snapshot.REWRITE | snapshot.CHECK | snapshot.UPDATE
                        )
                    ), error()


def get_snapshot_id(
    snapshot_id=None, clickhouse_version=None, add_analyzer=False, extra_data=None
):
    """Return snapshot id based on the current test's name
    and ClickHouse server version."""
    id_postfix = ""
    if clickhouse_version:
        if check_clickhouse_version(clickhouse_version)(current()):
            id_postfix = clickhouse_version

    if snapshot_id is None:
        snapshot_id = name.basename(current().name) + id_postfix
        if check_analyzer()(current()) and add_analyzer:
            snapshot_id += "_with_analyzer"

    if extra_data is not None:
        snapshot_id += "_extra_data"

    return snapshot_id


def compare_json_values(current, expected):
    """Compare only the value of jsons from a snapshot."""
    current_list = current.strip().split("\n")
    expected_list = expected.strip().split("\n")

    for current, expected in zip(current_list, expected_list):
        current = list(json.loads(current).values())[0]
        expected = list(json.loads(expected).values())[0]
        assert current == expected, error()

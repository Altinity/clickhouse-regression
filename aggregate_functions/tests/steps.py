import itertools

from testflows.core import *
from testflows.asserts import values, error, snapshot

from helpers.common import (
    check_clickhouse_version,
    get_snapshot_id,
    getuid,
    current_cpu,
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
    "groupArrayLast",
    "groupArrayMovingAvg",
    "groupArrayMovingSum",
    "groupArraySample",
    "groupBitAnd",
    "groupBitOr",
    "groupBitXor",
    "groupBitmap",
    "groupBitmapAnd",
    "groupBitmapOr",
    "groupBitmapXor",
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
    "lagInFrame",
    "leadInFrame",
    "exponentialTimeDecayedSum",
    "exponentialTimeDecayedMax",
    "exponentialTimeDecayedCount",
    "exponentialTimeDecayedAvg",
    "nonNegativeDerivative",
]


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
):
    """Execute SQL query and compare the output to the snapshot."""
    if snapshot_name is None:
        snapshot_name = current().name

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

    if message is None:
        if expected is not None:
            with Then("I check output against expected"):
                assert r.output.strip() == expected, error()
        else:
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

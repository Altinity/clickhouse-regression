from testflows.core import *
from testflows.asserts import values, error, snapshot

# exhaustive list of all aggregate functions
aggregate_functions = [
    "count",
    "min",
    "max",
    "sum",
    "avg",
    "any",
    "stddevPop",
    "stddevSamp",
    "varPop",
    "varSamp",
    "covarPop",
    "covarSamp",
    "anyHeavy",
    "anyLast",
    "argMin",
    "argMax",
    "avgWeighted",
    "corr",
    "exponentialmovingaverage",
    "topK",
    "topKWeighted",
    "groupArray",
    "groupUniqArray",
    "groupArrayInsertAt",
    "groupArrayMovingSum",
    "groupArrayMovingAvg",
    "groupArraySample",
    "groupBitAnd",
    "groupBitOr",
    "groupBitXor",
    "groupBitmap",
    "groupBitmapAnd",
    "groupBitmapOr",
    "groupBitmapXor",
    "sumWithOverflow",
    "deltaSum",
    "deltaSumTimestamp",
    "sumMap",
    "minMap",
    "maxMap",
    "sumCount",
    "rankCorr",
    "sumKahan",
    "intervalLengthSum",
    "skewPop",
    "skewSamp",
    "kurtPop",
    "kurtSamp",
    "uniq",
    "uniqExact",
    "uniqCombined",
    "uniqCombined64",
    "uniqHLL12",
    "uniqTheta",
    "quantile",
    "quantiles",
    "quantileExact",
    "quantileExactWeighted",
    "quantileTiming",
    "quantileTimingWeighted",
    "quantileDeterministic",
    "quantileTDigest",
    "quantileTDigestWeighted",
    "quantileBFloat16",
    "median",
    "simpleLinearRegression",
    "stochasticLinearRegression",
    "stochasticLogisticRegression",
    "categoricalInformationValue",
    "studentTTest",
    "welchTTest",
    "entropy",
    "meanZTest",
    "mannWhitneyUTest",
    "sparkbar",
    "histogram",
    "sequenceMatch",
    "sequenceCount",
    "windowFunnel",
    "retention",
    "uniqUpTo",
    "sumMapFiltered",
    "sequenceNextNode",
]


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
):
    """Execute SQL query and compare the output to the snapshot."""
    if snapshot_name is None:
        snapshot_name = current().name

    assert "snapshot_id" in current().context, "test must set self.context.snapshot_id"

    with When("I execute query", description=sql):
        if format and not "FORMAT" in sql:
            sql += " FORMAT " + format

        r = current().context.node.query(
            sql,
            exitcode=exitcode,
            message=message,
            no_checks=no_checks,
            use_file=use_file,
            hash_output=hash_output,
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
                            id=current().context.snapshot_id,
                            name=snapshot_name,
                            encoder=str,
                        )
                    ), error()

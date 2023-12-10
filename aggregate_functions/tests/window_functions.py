from testflows.core import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LagInFrame,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LeadInFrame,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Rank,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_DenseRank,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_RowNumber,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NthValue,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedAvg,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedMax,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedSum,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedCount,
)

from aggregate_functions.tests.steps import execute_query
from aggregate_functions.tests.steps import window_functions


@TestScenario
def check(self, arguments, func, func_):
    execute_query(
        f"SELECT {func_}({arguments}) FROM values('sample_data UInt8, sample_index UInt8', (10,1), (11,0), (12,0), (1,0), (2,0), (3,0))",
        exitcode=36,
        message=f"DB::Exception: The function '{func}' can only be used as a window function, not as an aggregate function: While executing AggregatingTransform.",
    )


@TestFeature
@Name("window_functions")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LagInFrame("1.0"),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LeadInFrame("1.0"),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Rank("1.0"),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_DenseRank("1.0"),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_RowNumber("1.0"),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NthValue("1.0"),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedAvg(
        "1.0"
    ),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedMax(
        "1.0"
    ),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedSum(
        "1.0"
    ),
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedCount(
        "1.0"
    ),
)
def feature(self):
    """Check that window function can not be used as aggregate functions."""

    functions_with_two_arguments = [
        "nth_value",
        "exponentialTimeDecayedSum",
        "exponentialTimeDecayedMax",
        "exponentialTimeDecayedAvg",
    ]
    parametric_functions = [
        "exponentialTimeDecayedSum",
        "exponentialTimeDecayedMax",
        "exponentialTimeDecayedCount",
        "exponentialTimeDecayedAvg",
    ]

    with Pool(5) as executor:
        for func in window_functions:
            if func == "nonNegativeDerivative":
                execute_query(
                    "SELECT nonNegativeDerivative(number, cast(number, 'DateTime')) FROM numbers(10)",
                    exitcode=36,
                    message=f"DB::Exception: The function '{func}' can only be used as a window function, not as an aggregate function: While executing AggregatingTransform.",
                    )
                continue

            if func in functions_with_two_arguments:
                arguments = "sample_data,sample_index"
            else:
                arguments = "sample_data"

            func_ = func
            if func in parametric_functions:
                func_ += "(5)"
            Scenario(name=f"{func}", test=check, parallel=True, executor=executor)(
                func=func, arguments=arguments, func_=func_
            )

        join()

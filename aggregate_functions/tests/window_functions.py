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
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Ntile,
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NonNegativeDerivative,
)

from aggregate_functions.tests.steps import execute_query


@TestOutline
def check(self, arguments, func, func_=None):
    if func_ is None:
        func_ = func
    execute_query(
        f"SELECT {func}({arguments}) FROM values('sample_data UInt8, sample_index UInt8', (10,1), (11,0), (12,0), (1,0), (2,0), (3,0))",
        exitcode=36,
        message=f"DB::Exception: The function '{func_}' can only be used as a window function, not as an aggregate function: While executing AggregatingTransform.",
    )


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_RowNumber("1.0"))
def row_number(self):
    """Check that row_number window function can not be used as an aggregate functions."""
    arguments = "sample_data"
    check(func="row_number", arguments=arguments)


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NthValue("1.0"))
def nth_value(self):
    """Check that nth_value window function can not be used as an aggregate functions."""
    arguments = "sample_data,sample_index"
    check(func="nth_value", arguments=arguments)


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Ntile("1.0"))
def ntile(self):
    """Check that ntile window function can not be used as an aggregate functions."""
    arguments = "sample_data"
    check(func="ntile", arguments=arguments)


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Rank("1.0"))
def rank(self):
    """Check that rank window function can not be used as an aggregate functions."""
    arguments = "sample_data"
    check(func="rank", arguments=arguments)


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_DenseRank("1.0"))
def dense_rank(self):
    """Check that dense_rank window function can not be used as an aggregate functions."""
    arguments = "sample_data"
    execute_query(
        f"SELECT dense_rank({arguments}) FROM values('sample_data UInt8, sample_index UInt8', (10,1), (11,0), (12,0), (1,0), (2,0), (3,0))",
        exitcode=36,
        message=f"DB::Exception: The function",
    )


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LagInFrame("1.0"))
def lagInFrame(self):
    """Check that lagInFrame window function can not be used as an aggregate functions."""
    arguments = "sample_data"
    check(func="lagInFrame", arguments=arguments)


@TestScenario
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LeadInFrame("1.0"))
def leadInFrame(self):
    """Check that leadInFrame window function can not be used as an aggregate functions."""
    arguments = "sample_data"
    check(func="leadInFrame", arguments=arguments)


@TestScenario
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedSum(
        "1.0"
    )
)
def exponentialTimeDecayedSum(self):
    """Check that exponentialTimeDecayedSum window function can not be used as an aggregate functions."""
    arguments = "sample_data,sample_index"
    check(
        func="exponentialTimeDecayedSum(5)",
        arguments=arguments,
        func_="exponentialTimeDecayedSum",
    )


@TestScenario
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedMax(
        "1.0"
    )
)
def exponentialTimeDecayedMax(self):
    """Check that exponentialTimeDecayedMax window function can not be used as an aggregate functions."""
    arguments = "sample_data,sample_index"
    check(
        func="exponentialTimeDecayedMax(5)",
        arguments=arguments,
        func_="exponentialTimeDecayedMax",
    )


@TestScenario
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedCount(
        "1.0"
    )
)
def exponentialTimeDecayedCount(self):
    """Check that exponentialTimeDecayedCount window function can not be used as an aggregate functions."""
    arguments = "sample_data"
    check(
        func="exponentialTimeDecayedCount(5)",
        arguments=arguments,
        func_="exponentialTimeDecayedCount",
    )


@TestScenario
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_ExponentialTimeDecayedAvg(
        "1.0"
    )
)
def exponentialTimeDecayedAvg(self):
    """Check that exponentialTimeDecayedAvg window function can not be used as an aggregate functions."""
    arguments = "sample_data,sample_index"
    check(
        func="exponentialTimeDecayedAvg(5)",
        arguments=arguments,
        func_="exponentialTimeDecayedAvg",
    )


@TestScenario
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_NonNegativeDerivative("1.0")
)
def nonNegativeDerivative(self):
    """Check that nonNegativeDerivative window function can not be used as an aggregate functions."""
    execute_query(
        "SELECT nonNegativeDerivative(number, cast(number, 'DateTime')) FROM numbers(10)",
        exitcode=36,
        message=f"DB::Exception: The function 'nonNegativeDerivative' can only be used as a window function, not as an aggregate function: While executing AggregatingTransform.",
    )


@TestFeature
@Name("window_functions")
def feature(self):
    """Check that window function can not be used as aggregate functions."""
    for scenario in loads(current_module(), Scenario):
        scenario()

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ExponentialMovingAverage,
)

from aggregate_functions.tests.covarPop import feature as checks


@TestFeature
@Name("exponentialMovingAverage")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ExponentialMovingAverage("1.0")
)
def feature(self, func="exponentialMovingAverage({params})", table=None):
    """Check exponentialMovingAverage aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    func = func.replace("({params})", "(0.5)({params})")
    checks(func=func, table=table, decimal=True)

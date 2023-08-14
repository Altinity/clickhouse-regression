from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ExponentialMovingAverage,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import scenario as checks


@TestScenario
@Name("exponentialMovingAverage")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ExponentialMovingAverage("1.0")
)
def scenario(self, func="exponentialMovingAverage({params})", table=None):
    """Check exponentialMovingAverage aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    func = func.replace("({params})", "(0.5)({params})")

    checks(func=func, table=table, decimal=True)

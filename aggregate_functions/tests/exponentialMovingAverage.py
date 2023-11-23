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
def scenario(
    self, func="exponentialMovingAverage({params})", table=None, snapshot_id=None
):
    """Check exponentialMovingAverage aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    func = func.replace("({params})", "(0.5)({params})")

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=True, snapshot_id=self.context.snapshot_id)

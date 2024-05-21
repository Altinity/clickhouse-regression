from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySample,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.groupArrayMovingAvg import scenario as checks


@TestScenario
@Name("groupArraySample")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySample("1.0"))
def scenario(self, func="groupArraySample({params})", table=None, snapshot_id=None):
    """Check groupArraySample aggregate function by using the same tests as for groupArrayMovingAvg."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if table is None:
        table = self.context.table

    params = "({params}"

    func_ = func.replace(params, f"(3, 2){params}")

    if "Merge" in self.name:
        return self.context.snapshot_id, func_.replace("({params})", "")

    checks(func=func_, table=table, snapshot_id=self.context.snapshot_id)

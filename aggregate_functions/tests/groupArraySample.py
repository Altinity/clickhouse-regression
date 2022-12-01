from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySample,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.groupArrayMovingAvg import feature as checks


@TestFeature
@Name("groupArraySample")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArraySample("1.0"))
def feature(self, func="groupArraySample({params})", table=None):
    """Check groupArraySample aggregate function by using the same tests as for groupArrayMovingAvg."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    params = "({params})"

    checks(func=func.replace(params, f"(3, 2){params}"), table=table)

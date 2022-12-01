from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayMovingAvg,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.avg import feature as checks


@TestFeature
@Name("groupArrayMovingAvg")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayMovingAvg("1.0")
)
def feature(self, func="groupArrayMovingAvg({params})", table=None):
    """Check groupArrayMovingAvg aggregate function by using the same tests as for avg."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

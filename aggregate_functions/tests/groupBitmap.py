from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmap,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.groupBitAnd import scenario as checks


@TestScenario
@Name("groupBitmap")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmap("1.0"))
def scenario(self, func="groupBitmap({params})", table=None):
    """Check groupBitmap aggregate function by using the same tests as for groupBitAnd."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

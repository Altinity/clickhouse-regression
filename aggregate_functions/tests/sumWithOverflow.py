from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumWithOverflow,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.sum import scenario as checks


@TestScenario
@Name("sumWithOverflow")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumWithOverflow("1.0"))
def scenario(self, func="sumWithOverflow({params})", table=None):
    """Check sumWithOverflow aggregate function by using the same tests as for sum."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

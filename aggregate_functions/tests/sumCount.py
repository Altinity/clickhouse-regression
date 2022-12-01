from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumCount,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.sum import feature as checks


@TestFeature
@Name("sumCount")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumCount("1.0"))
def feature(self, func="sumCount({params})", table=None):
    """Check sumCount aggregate function by using the same tests as for sum."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

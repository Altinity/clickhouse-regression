from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyLast,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.any import feature as checks


@TestFeature
@Name("anyLast")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyLast("1.0"))
def feature(self, func="anyLast({params})", table=None):
    """Check anyLast aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

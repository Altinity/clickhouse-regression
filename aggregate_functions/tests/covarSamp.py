from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import feature as checks


@TestFeature
@Name("covarSamp")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp("1.0"))
def feature(self, func="covarSamp({params})", table=None):
    """Check covarSamp aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

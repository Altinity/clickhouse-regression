from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import scenario as checks


@TestScenario
@Name("covarPopStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop("1.0"))
def scenario(self, func="covarPopStable({params})", table=None):
    """Check covarPopStable aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

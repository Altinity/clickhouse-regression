from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarSamp import scenario as checks


@TestScenario
@Name("covarSampStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp("1.0"))
def scenario(self, func="covarSampStable({params})", table=None):
    """Check covarSampStable aggregate function by using the same checks as for covarSamp."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

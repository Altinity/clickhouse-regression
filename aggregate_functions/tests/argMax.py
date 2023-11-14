from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.argMin import scenario as checks


@TestScenario
@Name("argMax")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax("1.0"))
def scenario(self, func="argMax({params})", table=None):
    """Check argMax aggregate function by using the same tests as for argMin."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

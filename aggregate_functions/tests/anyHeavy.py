from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyHeavy,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("anyHeavy")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyHeavy("1.0"))
def scenario(self, func="anyHeavy({params})", table=None):
    """Check anyHeavy aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

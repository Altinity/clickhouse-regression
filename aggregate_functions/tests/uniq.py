from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("uniq")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq("1.0"))
def scenario(self, func="uniq({params})", table=None):
    """Check uniq aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

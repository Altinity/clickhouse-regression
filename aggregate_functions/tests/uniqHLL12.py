from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqHLL12,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.uniq import scenario as checks


@TestScenario
@Name("uniqHLL12")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqHLL12("1.0"))
def scenario(self, func="uniqHLL12({params})", table=None):
    """Check uniqHLL12 aggregate function by using the same tests as for uniq."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

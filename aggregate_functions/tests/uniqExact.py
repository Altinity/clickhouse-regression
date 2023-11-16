from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqExact,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.uniq import scenario as checks


@TestScenario
@Name("uniqExact")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqExact("1.0"))
def scenario(self, func="uniqExact({params})", table=None, snapshot_id=None):
    """Check uniqExact aggregate function by using the same tests as for uniq."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if 'Merge' in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

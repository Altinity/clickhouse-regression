from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyLast,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("anyLast")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyLast("1.0"))
def scenario(self, func="anyLast({params})", table=None, snapshot_id=None):
    """Check anyLast aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id, clickhouse_version=">=23.2")

    if 'Merge' in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

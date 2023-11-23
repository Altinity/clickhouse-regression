from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitXor,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.groupBitAnd import scenario as checks


@TestScenario
@Name("groupBitXor")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitXor("1.0"))
def scenario(self, func="groupBitXor({params})", table=None, snapshot_id=None):
    """Check groupBitXor aggregate function by using the same tests as for groupBitAnd."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

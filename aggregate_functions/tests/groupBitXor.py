from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitXor,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.groupBitAnd import feature as checks


@TestFeature
@Name("groupBitXor")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitXor("1.0"))
def feature(self, func="groupBitXor({params})", table=None):
    """Check groupBitXor aggregate function by using the same tests as for groupBitAnd."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmap,
)

from aggregate_functions.tests.groupBitAnd import feature as checks


@TestFeature
@Name("groupBitmap")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmap("1.0"))
def feature(self, func="groupBitmap({params})", table=None):
    """Check groupBitmap aggregate function by using the same tests as for groupBitAnd."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

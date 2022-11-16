from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitOr,
)

from aggregate_functions.tests.groupBitAnd import feature as checks


@TestFeature
@Name("groupBitOr")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitOr("1.0"))
def feature(self, func="groupBitOr({params})", table=None):
    """Check groupBitOr aggregate function by using the same tests as for groupBitAnd."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

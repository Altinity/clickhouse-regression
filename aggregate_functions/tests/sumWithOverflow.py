from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumWithOverflow,
)

from aggregate_functions.tests.sum import feature as checks


@TestFeature
@Name("sumWithOverflow")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumWithOverflow("1.0"))
def feature(self, func="sumWithOverflow({params})", table=None):
    """Check sumWithOverflow aggregate function by using the same tests as for sum."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)
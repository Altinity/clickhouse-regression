from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewPop,
)

from aggregate_functions.tests.avg import feature as checks


@TestFeature
@Name("skewPop")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewPop("1.0"))
def feature(self, func="skewPop({params})", table=None):
    """Check skewPop aggregate function by using the same tests as for avg."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False)

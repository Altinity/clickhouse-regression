from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewSamp,
)

from aggregate_functions.tests.skewPop import feature as checks


@TestFeature
@Name("skewSamp")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewSamp("1.0"))
def feature(self, func="skewSamp({params})", table=None):
    """Check skewSamp aggregate function by using the same tests as for skewPop."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

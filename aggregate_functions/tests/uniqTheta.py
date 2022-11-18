from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqTheta,
)

from aggregate_functions.tests.uniq import feature as checks


@TestFeature
@Name("uniqTheta")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqTheta("1.0"))
def feature(self, func="uniqTheta({params})", table=None):
    """Check uniqTheta aggregate function by using the same tests as for uniq."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

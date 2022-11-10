from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp,
)

from aggregate_functions.tests.covarSamp import feature as covarsamp_feature


@TestFeature
@Name("covarSampStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarSamp("1.0"))
def feature(self, func="covarSampStable({params})", table=None):
    """Check covarSampStable aggregate function by using the same checks as for covarSamp."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    covarsamp_feature(func=func, table=table)

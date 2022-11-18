from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Corr,
)

from aggregate_functions.tests.corr import feature as checks


@TestFeature
@Name("corrStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Corr("1.0"))
def feature(self, func="corrStable({params})", table=None):
    """Check corrStable aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

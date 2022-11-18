from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AvgWeighted,
)

from aggregate_functions.tests.covarPop import feature as checks


@TestFeature
@Name("avgWeighted")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AvgWeighted("1.0"))
def feature(
    self,
    func="avgWeighted({params})",
    table=None,
    decimal=True,
    date=False,
    datetime=False,
):
    """Check avgWeighted aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=decimal, date=date, datetime=datetime)

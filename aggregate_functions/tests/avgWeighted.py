from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AvgWeighted,
)

from helpers.common import check_clickhouse_version
from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import scenario as checks


@TestScenario
@Name("avgWeighted")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AvgWeighted("1.0"))
def scenario(
    self,
    func="avgWeighted({params})",
    table=None,
    decimal=True,
    date=False,
    datetime=False,
    snapshot_id=None
):
    """Check avgWeighted aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if table is None:
        table = self.context.table

    if check_clickhouse_version(">=22.8.7")(self):
        xfail(
            "doesn't work from 22.8.7",
            "https://github.com/ClickHouse/ClickHouse/issues/31768",
        )
        
    if 'Merge' in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    checks(func=func, table=table, decimal=decimal, date=date, datetime=datetime, snapshot_id=self.context.snapshot_id)

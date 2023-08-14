from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantile,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.avg import scenario as checks


@TestScenario
@Name("quantile")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantile("1.0"))
def scenario(
    self,
    func="quantile({params})",
    table=None,
    decimal=True,
    date=True,
    datetime=True,
    extended_precision=False,
):
    """Check quantile aggregate function by using the same tests as for avg."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(
        func=func,
        table=table,
        decimal=decimal,
        date=date,
        datetime=datetime,
        extended_precision=extended_precision,
    )

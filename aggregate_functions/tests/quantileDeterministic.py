from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileDeterministic,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantile import scenario as checks


@TestScenario
@Name("quantileDeterministic")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileDeterministic("1.0")
)
def scenario(
    self, func="quantileDeterministic({params})", table=None, date=True, datetime=True, snapshot_id=None
):
    """Check quantileDeterministic aggregate function by using the same tests as for avg."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if table is None:
        table = self.context.table

    checks(
        func=func.replace("({params})", "({params},1)"),
        table=table,
        decimal=False,
        date=date,
        datetime=datetime,
        snapshot_id=self.context.snapshot_id
    )

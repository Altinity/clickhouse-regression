from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLogisticRegression,
)

from aggregate_functions.tests.avg import scenario as checks
from aggregate_functions.tests.steps import *


@TestScenario
@Name("stochasticLogisticRegression")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLogisticRegression(
        "1.0"
    )
)
def scenario(
    self, func="stochasticLogisticRegression({params})", table=None, snapshot_id=None
):
    """Check stochasticLogisticRegression aggregate function by using the same tests as for avg."""

    if table is None:
        table = self.context.table

    clickhouse_version = ">=23.2"
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    _func = func.replace(
        "({params})",
        f"(1.0, 1.0, 1.0, 'SGD')({{params}}*0.1+{{params}}*0.2+7,{{params}},{{params}}*0.3)",
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    checks(func=_func, table=table, decimal=False, snapshot_id=self.context.snapshot_id)

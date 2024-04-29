from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLinearRegression,
)

from aggregate_functions.tests.avg import scenario as checks
from aggregate_functions.tests.steps import *


@TestScenario
@Name("stochasticLinearRegression")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLinearRegression("1.0")
)
def scenario(
    self, func="stochasticLinearRegression({params})", table=None, snapshot_id=None
):
    """Check stochasticLinearRegression aggregate function by using the same tests as for avg."""

    if table is None:
        table = self.context.table

    if check_clickhouse_version(">=24.3")(self) and check_current_cpu("aarch64")(self):
        clickhouse_version = ">=24.3"
    else:
        clickhouse_version = ">=23.2"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    _func = func.replace(
        "({params})",
        f"(0.1, 0.0, 5, 'SGD')({{params}}*0.1+{{params}}*0.2+7,{{params}},{{params}}*0.3)",
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    checks(func=_func, table=table, decimal=False, snapshot_id=self.context.snapshot_id)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactWeighted,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileExactWeighted import scenario as checks


@TestScenario
@Name("quantilesExactWeighted")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesExactWeighted("1.0")
)
def scenario(self, func="quantilesExactWeighted({params})", table=None, snapshot_id=None):
    """Check quantilesExactWeighted aggregate function by using the same tests as for quantileExactWeighted."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id, clickhouse_version=">=23.2")

    if table is None:
        table = self.context.table

    _func = func.replace(
        "({params})", f"(0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)({{params}})"
    )

    if 'Merge' in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    checks(func=_func, snapshot_id=self.context.snapshot_id)

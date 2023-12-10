from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesInterpolatedWeighted,
)

from aggregate_functions.tests.quantileWeighted import scenario as checks
from aggregate_functions.tests.steps import *


@TestScenario
@Name("quantilesInterpolatedWeighted")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesInterpolatedWeighted(
        "1.0"
    )
)
def scenario(
    self, func="quantilesInterpolatedWeighted({params})", table=None, snapshot_id=None
):
    """Check quantilesInterpolatedWeighted aggregate function by using the same tests as for quantileWeighted."""

    if check_clickhouse_version("<23.5"):
        skip(reason=f"quantilesInterpolatedWeighted works from 23")

    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    _func = func.replace(
        "({params})", f"(0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)({{params}})"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=_func, table=table, decimal=True, snapshot_id=self.context.snapshot_id)

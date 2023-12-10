from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileInterpolatedWeighted,
)

from aggregate_functions.tests.steps import *
from aggregate_functions.tests.quantileWeighted import scenario as checks


@TestScenario
@Name("quantileInterpolatedWeighted")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileInterpolatedWeighted(
        "1.0"
    )
)
def scenario(
    self, func="quantileInterpolatedWeighted({params})", table=None, snapshot_id=None
):
    """Check quantileInterpolatedWeighted aggregate function by using the same tests as for quantileWeighted."""

    if check_clickhouse_version("<23.5"):
        skip(reason=f"quantilesInterpolatedWeighted works from 23")

    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=True, snapshot_id=self.context.snapshot_id)

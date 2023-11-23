from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactExclusive,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantile import scenario as checks


@TestScenario
@Name("quantileExactExclusive")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactExclusive("1.0")
)
def scenario(
    self, func="quantileExactExclusive({params})", table=None, snapshot_id=None
):
    """Check quantileExactExclusive aggregate function by using the same tests as for quantile."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False, snapshot_id=self.context.snapshot_id)

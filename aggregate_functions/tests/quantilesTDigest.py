from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTDigest,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileTDigest import scenario as checks


@TestScenario
@Name("quantilesTDigest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTDigest("1.0"))
def scenario(self, func="quantilesTDigest({params})", table=None):
    """Check quantilesTDigest aggregate function by using the same tests as for quantileTDigest."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    _func = func.replace(
        "({params})", f"(0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)({{params}})"
    )
    checks(func=_func)

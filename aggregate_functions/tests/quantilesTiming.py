from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTiming,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileTiming import scenario as checks


@TestScenario
@Name("quantilesTiming")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesTiming("1.0"))
def scenario(self, func="quantilesTiming({params})", table=None, snapshot_id=None):
    """Check quantilesTiming aggregate function by using the same tests as for quantileTiming."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if table is None:
        table = self.context.table

    _func = func.replace(
        "({params})", f"(0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)({{params}})"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    checks(func=_func, snapshot_id=self.context.snapshot_id)

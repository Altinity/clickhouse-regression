from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesBFloat16,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileBFloat16 import scenario as checks


@TestScenario
@Name("quantilesBFloat16")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesBFloat16("1.0")
)
def scenario(self, func="quantilesBFloat16({params})", table=None):
    """Check quantilesBFloat16 aggregate function by using the same tests as for quantileBFloat16."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    _func = func.replace(
        "({params})", f"(0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)({{params}})"
    )
    checks(func=_func)

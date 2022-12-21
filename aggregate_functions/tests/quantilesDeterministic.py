from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesDeterministic,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileDeterministic import feature as checks


@TestFeature
@Name("quantilesDeterministic")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantilesDeterministic("1.0")
)
def feature(self, func="quantilesDeterministic({params})", table=None):
    """Check quantilesDeterministic aggregate function by using the same tests as for quantileDeterministic."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    _func = func.replace(
        "({params})", f"(0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)({{params}})"
    )
    checks(func=_func)

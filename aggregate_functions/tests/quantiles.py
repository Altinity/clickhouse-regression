from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantiles,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantile import feature as checks


@TestFeature
@Name("quantiles")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantiles("1.0"))
def feature(self, func="quantiles({params})", table=None):
    """Check quantiles aggregate function by using the same tests as for quantile."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    params = "({params})"

    _func = func.replace(params, f"(0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999){params}")

    checks(func=_func)

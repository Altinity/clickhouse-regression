from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactLow,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantile import feature as checks


@TestFeature
@Name("quantileExactLow")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileExactLow("1.0"))
def feature(self, func="quantileExactLow({params})", table=None):
    """Check quantileExactLow aggregate function by using the same tests as for quantile."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False)

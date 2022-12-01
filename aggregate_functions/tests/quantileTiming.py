from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTiming,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantile import feature as checks


@TestFeature
@Name("quantileTiming")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTiming("1.0"))
def feature(self, func="quantileTiming({params})", table=None):
    """Check quantileTiming aggregate function by using the same tests as for quantile."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False, date=False, datetime=False)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileBFloat16Weighted,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileWeighted import feature as checks


@TestFeature
@Name("quantileBFloat16Weighted")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileBFloat16Weighted("1.0")
)
def feature(self, func="quantileBFloat16Weighted({params})", table=None):
    """Check quantileBFloat16Weighted aggregate function by using the same tests as for quantileWeighted."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False, date=False, datetime=False)

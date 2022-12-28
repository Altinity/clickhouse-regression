from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTDigestWeighted,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileWeighted import feature as checks


@TestFeature
@Name("quantileTDigestWeighted")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileTDigestWeighted("1.0")
)
def feature(self, func="quantileTDigestWeighted({params})", table=None):
    """Check quantileTDigestWeighted aggregate function by using the same tests as for quantileWeighted."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Entropy,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.any import feature as checks


@TestFeature
@Name("entropy")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Entropy("1.0"))
def feature(self, func="entropy({params})", table=None):
    """Check entropy aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

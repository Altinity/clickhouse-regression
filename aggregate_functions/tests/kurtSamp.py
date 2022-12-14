from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtSamp,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.kurtPop import feature as checks


@TestFeature
@Name("kurtSamp")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtSamp("1.0"))
def feature(self, func="kurtSamp({params})", table=None):
    """Check kurtSamp aggregate function by using the same tests as for kurtPop."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined64,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.uniq import feature as checks


@TestFeature
@Name("uniqCombined64")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined64("1.0"))
def feature(self, func="uniqCombined64({params})", table=None):
    """Check uniqCombined64 aggregate function by using the same tests as for uniq."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

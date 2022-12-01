from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.uniq import feature as checks


@TestFeature
@Name("uniqCombined")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_UniqCombined("1.0"))
def feature(self, func="uniqCombined({params})", table=None):
    """Check uniqCombined aggregate function by using the same tests as for uniq."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

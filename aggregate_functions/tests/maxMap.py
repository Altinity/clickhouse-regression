from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MaxMap,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.sumMap import feature as checks


@TestFeature
@Name("maxMap")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MaxMap("1.0"))
def feature(self, func="maxMap({params})", table=None):
    """Check maxMap aggregate function by using the same tests as for sumMap."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Anylast,
)

from aggregate_functions.tests.any import feature as any_feature


@TestFeature
@Name("anyLast")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Anylast("1.0"))
def feature(self, func="anyLast({params})", table=None):
    """Check anyLast aggregate function by using the same tests as for any."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    any_feature(func=func, table=table)

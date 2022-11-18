from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop,
)

from aggregate_functions.tests.avg import feature as avg_feature


@TestFeature
@Name("stddevPop")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop("1.0"))
def feature(self, func="stddevPop({params})", table=None):
    """Check stddevPop aggregate function by using the same checks as for avg."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    avg_feature(func=func, table=table, decimal=False)

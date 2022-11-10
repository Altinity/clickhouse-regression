from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarPop,
)

from aggregate_functions.tests.varPop import feature as varpop_feature


@TestFeature
@Name("varPopStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarPop("1.0"))
def feature(self, func="varPopStable({params})", table=None):
    """Check varPopStable aggregate function by using the same checks as for varPop."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    varpop_feature(func=func, table=table)

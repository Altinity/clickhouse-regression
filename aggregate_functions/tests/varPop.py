from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarPop,
)

from aggregate_functions.tests.avg import feature as checks


@TestFeature
@Name("varPop")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarPop("1.0"))
def feature(self, func="varPop({params})", table=None):
    """Check varPop aggregate function by using the same checks as for avg."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False)

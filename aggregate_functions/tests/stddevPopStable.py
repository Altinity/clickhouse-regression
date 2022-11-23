from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop,
)

from aggregate_functions.tests.stddevPop import feature as checks


@TestFeature
@Name("stddevPopStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop("1.0"))
def feature(self, func="stddevPopStable({params})", table=None):
    """Check stddevPopStable aggregate function by using the same checks as for stddevPop."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

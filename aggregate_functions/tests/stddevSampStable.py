from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevSamp,
)

from aggregate_functions.tests.stddevSamp import feature as checks


@TestFeature
@Name("stddevSampStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevSamp("1.0"))
def feature(self, func="stddevSampStable({params})", table=None):
    """Check stddevSampStable aggregate function by using the same checks as for stddevSamp."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarSamp,
)

from aggregate_functions.tests.varSamp import feature as varsamp_feature


@TestFeature
@Name("varSampStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_VarSamp("1.0"))
def feature(self, func="varSampStable({params})", table=None):
    """Check varSampStable aggregate function by using the same checks as for varSamp."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    varsamp_feature(func=func, table=table)

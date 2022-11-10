from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop,
)

from aggregate_functions.tests.covarPop import feature as covarpop_feature


@TestFeature
@Name("covarPopStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_CovarPop("1.0"))
def feature(self, func="covarPopStable({params})", table=None):
    """Check covarPopStable aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    covarpop_feature(func=func, table=table)

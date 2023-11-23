from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Corr,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.corr import scenario as checks


@TestScenario
@Name("corrStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Corr("1.0"))
def scenario(self, func="corrStable({params})", table=None, snapshot_id=None):
    """Check corrStable aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

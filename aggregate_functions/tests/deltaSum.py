from testflows.core import *

from aggregate_functions.tests.steps import execute_query

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSum,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.sum import scenario as checks


@TestScenario
@Name("deltaSum")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSum("1.0"))
def scenario(self, func="deltaSum({params})", table=None, snapshot_id=None):
    """Check deltaSum aggregate function by using the same tests as for sum."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False, snapshot_id=self.context.snapshot_id)

    with Check("delta"):
        execute_query(
            f"SELECT {func.format(params='x')}, any(toTypeName(x)) FROM values('x Int8', (1),(-2),(-3),(-1))"
        )

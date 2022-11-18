from testflows.core import *

from aggregate_functions.tests.steps import execute_query

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSum,
)

from aggregate_functions.tests.sum import feature as checks


@TestFeature
@Name("deltaSum")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_DeltaSum("1.0"))
def feature(self, func="sumWithOverflow({params})", table=None):
    """Check deltaSum aggregate function by using the same tests as for sum."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False)

    with Check("delta"):
        execute_query(
            f"SELECT {func.format(params='x')} FROM values('x Int8', (1),(-2),(-3),(-1))"
        )

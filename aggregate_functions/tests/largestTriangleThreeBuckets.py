from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_LargestTriangleThreeBuckets,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import scenario as checks


@TestScenario
@Name("largestTriangleThreeBuckets")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_LargestTriangleThreeBuckets(
        "1.0"
    )
)
def scenario(
    self, func="largestTriangleThreeBuckets({params})", table=None, snapshot_id=None
):
    """Check largestTriangleThreeBuckets aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    func_ = func.replace("({params})", f"(4)({{params}})")

    if "Merge" in self.name:
        return self.context.snapshot_id, func_.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(
        func=func_,
        table=table,
        snapshot_id=self.context.snapshot_id,
        decimal=True,
        date=True,
        datetime=True,
        extended_precision=True,
    )
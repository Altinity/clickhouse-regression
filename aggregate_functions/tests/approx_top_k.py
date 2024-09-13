from testflows.core import *
from aggregate_functions.tests.steps import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Approx_Top_K,
)

from aggregate_functions.tests.topK import scenario as checks


@TestScenario
@Name("approx_top_k")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Approx_Top_K("1.0"))
def scenario(self, func="approx_top_k({params})", table=None, snapshot_id=None):
    """Check approx_top_k, aggregate function by using the same checks as for topK."""

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=24.8", add_analyzer=True
    )

    if table is None:
        table = self.context.table

    params = "({params}"

    _func = func.replace(params, f"(3){params}")

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    checks(
        func=func,
        table=table,
        snapshot_id=self.context.snapshot_id,
    )

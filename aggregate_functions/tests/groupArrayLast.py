from testflows.core import *

from aggregate_functions.tests.steps import execute_query, get_snapshot_id
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayLast,
)

from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("groupArrayLast")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArrayLast("1.0"))
def scenario(self, func="groupArrayLast({params})", table=None, snapshot_id=None):
    """Check groupArrayLast aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id
    )

    _func = func.replace(
        "({params})", f"(5)({{params}})"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=_func, table=table, snapshot_id=self.context.snapshot_id)

    
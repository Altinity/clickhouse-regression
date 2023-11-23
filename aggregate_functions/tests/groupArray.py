from testflows.core import *

from aggregate_functions.tests.steps import execute_query, get_snapshot_id
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray,
)

from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("groupArray")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray("1.0"))
def scenario(self, func="groupArray({params})", table=None, snapshot_id=None):
    """Check groupArray aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.2"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    params = "({params})"
    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

    with Check("max size"):
        for size in range(1, 10):
            with When(f"{size}"):
                _func = func.replace(params, f"({size}){params}")
                execute_query(
                    f"SELECT {_func.format(params='number')}, any(toTypeName(number)) FROM numbers(8)"
                )

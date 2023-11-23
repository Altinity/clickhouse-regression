from testflows.core import *
from aggregate_functions.tests.steps import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopK,
)

from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("topK")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_TopK("1.0"))
def scenario(self, func="topK({params})", table=None, snapshot_id=None):
    """Check topK aggregate function by using the same checks as for any
    as well as functions specific checks."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.2"
    )

    if table is None:
        table = self.context.table

    params = "({params})"

    _func = func.replace(params, f"(3){params}")
    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    checks(
        func=func.replace(params, f"(3){params}"),
        table=table,
        snapshot_id=self.context.snapshot_id,
    )

    with Check("K values"):
        for k in range(1, 10):
            with When(f"{k}"):
                _func = func.replace(params, f"({k}){params}")
                execute_query(
                    f"SELECT {_func.format(params='bitAnd(number, 7)')} FROM numbers(100)"
                )

    with Check("custom load factor"):
        _func = func.replace(params, f"(5,5){params}")
        execute_query(
            f"SELECT {_func.format(params='bitAnd(number, 7)')} FROM numbers(56)"
        )

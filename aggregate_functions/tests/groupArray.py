from testflows.core import *

from aggregate_functions.tests.steps import (
    execute_query,
    get_snapshot_id,
    check_clickhouse_version,
)
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray,
)

from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("groupArray")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray("1.0"))
def scenario(self, func="groupArray({params})", table=None, snapshot_id=None):
    """Check groupArray aggregate function by using the same tests as for any."""
    if check_clickhouse_version(">=24.8")(self):
        clickhouse_version = (
            ">=24.8"  # https://github.com/ClickHouse/ClickHouse/issues/69518
        )
    elif check_clickhouse_version(">=23.12")(self):
        clickhouse_version = ">=23.12"
    else:
        clickhouse_version = ">=23.2"
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id,
        clickhouse_version=clickhouse_version,
        add_analyzer=True,
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    params = "({params}"
    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

    with Check("max size"):
        for size in range(1, 10):
            with When(f"{size}"):
                _func = func.replace(params, f"({size}){params}")
                execute_query(
                    f"SELECT {_func.format(params='number')}, any(toTypeName(number)) FROM numbers(8)"
                )

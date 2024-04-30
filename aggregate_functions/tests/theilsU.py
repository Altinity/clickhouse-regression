from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_TheilsU,
)

from aggregate_functions.tests.steps import *
from aggregate_functions.tests.corr import scenario as checks


@TestScenario
@Name("theilsU")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_TheilsU("1.0"))
def scenario(self, func="theilsU({params})", table=None, snapshot_id=None):
    """Check theilsU aggregate function by using the same checks as for covarPop
    as well as functions specific checks."""

    clickhouse_version = None
    if check_current_cpu("aarch64")(self):
        clickhouse_version = ">=24.3"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

    with Check("example2"):
        execute_query(
            f"SELECT {func.format(params='number % 10,number % 4')}, any(toTypeName(number)), any(toTypeName(number)) FROM numbers(150)"
        )

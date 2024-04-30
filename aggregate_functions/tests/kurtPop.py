from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtPop,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_current_cpu
from aggregate_functions.tests.avg import scenario as checks


@TestScenario
@Name("kurtPop")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KurtPop("1.0"))
def scenario(self, func="kurtPop({params})", table=None, snapshot_id=None):
    """Check kurtPop aggregate function by using the same tests as for avg."""
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

    checks(func=func, table=table, decimal=False, snapshot_id=self.context.snapshot_id)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_current_cpu
from aggregate_functions.tests.stddevPop import scenario as checks


@TestScenario
@Name("stddevPopStable")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevPop("1.0"))
def scenario(self, func="stddevPopStable({params})", table=None, snapshot_id=None):
    """Check stddevPopStable aggregate function by using the same checks as for stddevPop."""
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

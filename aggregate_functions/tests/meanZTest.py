from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MeanZTest,
)

from aggregate_functions.tests.steps import *
from aggregate_functions.tests.welchTTest import scenario as checks


@TestScenario
@Name("meanZTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MeanZTest("1.0"))
def scenario(self, func="meanZTest({params})", table=None, snapshot_id=None):
    """Check meanZTest aggregate function by using the same tests as for welchTTest."""

    if check_clickhouse_version(">=24.3")(self) and check_current_cpu("aarch64")(self):
        clickhouse_version = ">=24.3"
    elif check_clickhouse_version(">=24.1")(self):
        clickhouse_version = ">=24.1"
    elif check_clickhouse_version(">=23.2")(self):
        clickhouse_version = ">=23.2"
    else:
        clickhouse_version = ">=22.6"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if table is None:
        table = self.context.table

    _func = func.replace("({params})", f"(0.7, 0.45, 0.95)({{params}})")

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    checks(func=_func, snapshot_id=self.context.snapshot_id)

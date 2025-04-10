from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewSamp,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_current_cpu
from aggregate_functions.tests.skewPop import scenario as checks


@TestScenario
@Name("skewSamp")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SkewSamp("1.0"))
def scenario(self, func="skewSamp({params})", table=None, snapshot_id=None):
    """Check skewSamp aggregate function by using the same tests as for skewPop."""
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

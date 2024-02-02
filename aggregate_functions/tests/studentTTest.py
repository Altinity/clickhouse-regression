from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest,
)

from helpers.common import check_clickhouse_version
from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.welchTTest import scenario as checks


@TestScenario
@Name("studentTTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest("1.0"))
def scenario(self, func="studentTTest({params})", table=None, snapshot_id=None):
    """Check studentTTest aggregate function by using the same tests as for welchTTest."""

    if check_clickhouse_version(">=24.1")(self):
        clickhouse_version = ">=24.1"
    elif check_clickhouse_version(">=23.2")(self):
        clickhouse_version = ">=23.2"
    else:
        clickhouse_version = ">=22.6"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, snapshot_id=self.context.snapshot_id)

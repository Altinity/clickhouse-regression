from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqTheta,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_clickhouse_version
from aggregate_functions.tests.uniq import scenario as checks


@TestScenario
@Name("uniqTheta")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_UniqTheta("1.0"))
def scenario(self, func="uniqTheta({params})", table=None, snapshot_id=None):
    """Check uniqTheta aggregate function by using the same tests as for uniq."""
    
    if check_clickhouse_version(">=25.8.15")(self):
        clickhouse_version = ">=25.8"
    elif check_clickhouse_version(">=24.8")(self):
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

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

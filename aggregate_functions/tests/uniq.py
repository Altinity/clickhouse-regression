from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_clickhouse_version
from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("uniq")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq("1.0"))
def scenario(self, func="uniq({params})", table=None, snapshot_id=None):
    """Check uniq aggregate function by using the same tests as for any."""
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

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

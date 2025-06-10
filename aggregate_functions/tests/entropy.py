from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Entropy,
)

from aggregate_functions.tests.steps import *
from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("entropy")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Entropy("1.0"))
def scenario(self, func="entropy({params})", table=None, snapshot_id=None):
    """Check entropy aggregate function by using the same tests as for any."""

    if check_clickhouse_version(">=25.1")(self) and "Merge" in self.name:
        clickhouse_version = ">=25.1"
    elif check_clickhouse_version(">=24.8")(self):
        clickhouse_version = (
            ">=24.8"  # https://github.com/ClickHouse/ClickHouse/issues/69518
        )
    elif check_clickhouse_version(">=24.3")(self) and check_current_cpu("aarch64")(
        self
    ):
        clickhouse_version = ">=24.3"
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

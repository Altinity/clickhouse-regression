from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_clickhouse_version
from aggregate_functions.tests.argMin import scenario as checks


@TestScenario
@Name("argMax")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax("1.0"))
def scenario(self, func="argMax({params})", table=None, snapshot_id=None):
    """Check argMax aggregate function by using the same tests as for argMin."""
    # https://github.com/ClickHouse/ClickHouse/pull/58139
    if "State" in self.name:
        if check_clickhouse_version(">=24.4"):
            clickhouse_version = ">=24.4"
        elif check_clickhouse_version(">=23.12"):
            clickhouse_version = ">=23.12"
        else:
            clickhouse_version = ">=23.2"
    else:
        clickhouse_version = (
            ">=23.2" if check_clickhouse_version("<23.12")(self) else ">=23.12"
        )

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

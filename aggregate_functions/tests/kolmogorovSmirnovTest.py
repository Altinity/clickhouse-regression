from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KolmogorovSmirnovTest,
)

from aggregate_functions.tests.steps import *
from aggregate_functions.tests.mannWhitneyUTest import scenario as checks


@TestScenario
@Name("kolmogorovSmirnovTest")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_KolmogorovSmirnovTest("1.0")
)
def scenario(
    self, func="kolmogorovSmirnovTest({params})", table=None, snapshot_id=None
):
    """Check kolmogorovSmirnovTest aggregate function by using the same tests as for mannWhitneyUTest."""
    if check_clickhouse_version(">=24.3")(self) and check_current_cpu("aarch64")(self):
        clickhouse_version = ">=24.3"
    elif check_clickhouse_version("<24.1")(self):
        clickhouse_version = ">=23.11"
    else:
        clickhouse_version = ">=24.1"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if "Merge" in self.name:
        func_ = func.replace("({params})", f"('greater')({{params}})")
        return self.context.snapshot_id, func_.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

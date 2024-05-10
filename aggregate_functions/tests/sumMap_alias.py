from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumMap,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_clickhouse_version
from aggregate_functions.tests.maxMappedArrays import scenario as checks


@TestScenario
@Name("sumMap_alias")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SumMap("1.0"))
def scenario(self, func="sumMap({params})", table=None, snapshot_id=None):
    """Check sumMap(sumMappedArrays) aggregate function by using the same tests as for maxMap(maxMappedArrays)."""

    clickhouse_version = (
        ">=23.11" if check_clickhouse_version("<24.1")(self) else ">=24.1"
    )
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

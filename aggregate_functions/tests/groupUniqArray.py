from testflows.core import *

from aggregate_functions.tests.steps import execute_query
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupUniqArray,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.groupArray import scenario as checks


@TestScenario
@Name("groupUniqArray")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupUniqArray("1.0"))
def scenario(self, func="groupUniqArray({params})", table=None, snapshot_id=None):
    """Check groupUniqArray aggregate function by using the same tests as for groupArray."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id, clickhouse_version=">=23.2")

    if 'Merge' in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

    with Check("duplicates"):
        execute_query(f"SELECT {func.format(params='number % 2')} FROM numbers(8)")

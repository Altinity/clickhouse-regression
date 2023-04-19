from testflows.core import *

from aggregate_functions.tests.steps import execute_query
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupUniqArray,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.groupArray import feature as checks


@TestFeature
@Name("groupUniqArray")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupUniqArray("1.0"))
def feature(self, func="groupUniqArray({params})", table=None):
    """Check groupUniqArray aggregate function by using the same tests as for groupArray."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=23.2")

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

    with Check("duplicates"):
        execute_query(f"SELECT {func.format(params='number % 2')} FROM numbers(8)")

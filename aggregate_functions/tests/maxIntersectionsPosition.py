from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersectionsPosition,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.maxIntersections import scenario as checks


@TestScenario
@Name("maxIntersectionsPosition")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_MaxIntersectionsPosition(
        "1.0"
    )
)
def scenario(
    self, func="maxIntersectionsPosition({params})", table=None, snapshot_id=None
):
    """Check maxIntersectionsPosition aggregate function by using the same tests as for maxIntersections."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=">=23.2"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

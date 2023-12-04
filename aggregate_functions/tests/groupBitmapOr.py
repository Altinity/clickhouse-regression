from testflows.core import *

from helpers.tables import *
from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapOr,
)
from aggregate_functions.tests.groupBitmapAnd import scenario as checks


@TestScenario
@Name("groupBitmapOr")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupBitmapOr("1.0"))
def scenario(
    self,
    func="groupBitmapOr({params})",
    snapshot_id=None,
):
    """Check groupBitmapOr aggregate function by using the same tests as for groupBitmapAnd."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id, clickhouse_version=">=23.10")

    if "Merge" in self.name:
        skip(reason=f"Does not support -Merge combinator")

    checks(func=func, snapshot_id=self.context.snapshot_id)

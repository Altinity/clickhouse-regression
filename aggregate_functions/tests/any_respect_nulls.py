from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_AnyRespectNulls,
)

from aggregate_functions.tests.steps import get_snapshot_id, check_clickhouse_version
from aggregate_functions.tests.any import scenario as checks


@TestScenario
@Name("any_respect_nulls")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_AnyRespectNulls("1.0"))
def scenario(self, func="any_respect_nulls({params})", table=None, snapshot_id=None):
    """Check any_respect_nulls aggregate function by using the same tests as for any."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, add_analyzer=True
    )

    if check_clickhouse_version("<23.11")(self):
        skip("any_respect_nulls works from 23.11")
    else:
        if "Merge" in self.name:
            return self.context.snapshot_id, func.replace("({params})", "")

        if table is None:
            table = self.context.table
        checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

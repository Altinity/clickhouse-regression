from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LastValueRespectNulls,
)

from aggregate_functions.tests.steps import *
from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.first_value_respect_nulls import scenario as checks


@TestScenario
@Name("last_value_respect_nulls")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LastValueRespectNulls("1.0")
)
def scenario(
    self, func="last_value_respect_nulls({params})", table=None, snapshot_id=None
):
    """Check last_value_respect_nulls aggregate function by using the same tests as for first_value_respect_nulls."""

    if check_clickhouse_version("<23.5"):
        skip(reason=f"first_value_respect_nulls works from 23.5")

    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

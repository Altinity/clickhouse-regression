from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.first_value import scenario as checks

from helpers.common import check_clickhouse_version


@TestScenario
@Name("singleValueOrNull")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull("1.0")
)
def scenario(self, func="singleValueOrNull({params})", table=None, snapshot_id=None):
    """Check singleValueOrNull aggregate function by using the same tests as for first_value."""

    if check_clickhouse_version(">=26.1")(self):
        clickhouse_version = ">=26.1"
    else:
        clickhouse_version = ">=23.2"

    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, clickhouse_version=clickhouse_version
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=self.context.snapshot_id)

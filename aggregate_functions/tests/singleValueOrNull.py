from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.first_value import scenario as checks


@TestScenario
@Name("singleValueOrNull")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull("1.0")
)
def scenario(self, func="singleValueOrNull({params})", table=None):
    """Check singleValueOrNull aggregate function by using the same tests as for first_value."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

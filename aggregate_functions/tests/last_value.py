from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LastValue,
)

from aggregate_functions.tests.first_value import feature as checks


@TestFeature
@Name("last_value")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_LastValue("1.0"))
def feature(self, func="last_value({params})", table=None):
    """Check last_value aggregate function by using the same tests as for first_value."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

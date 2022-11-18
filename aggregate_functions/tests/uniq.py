from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq,
)

from aggregate_functions.tests.any import feature as checks


@TestFeature
@Name("uniq")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Uniq("1.0"))
def feature(self, func="uniq({params})", table=None):
    """Check uniq aggregate function by using the same tests as for any."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

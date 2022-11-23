from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyHeavy,
)

from aggregate_functions.tests.any import feature as checks


@TestFeature
@Name("anyHeavy")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_AnyHeavy("1.0"))
def feature(self, func="anyHeavy({params})", table=None):
    """Check anyHeavy aggregate function by using the same tests as for any."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

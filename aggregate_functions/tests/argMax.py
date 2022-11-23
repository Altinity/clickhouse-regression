from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax,
)

from aggregate_functions.tests.argMin import feature as checks


@TestFeature
@Name("argMax")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax("1.0"))
def feature(self, func="argMax({params})", table=None):
    """Check argMax aggregate function by using the same tests as for argMin."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

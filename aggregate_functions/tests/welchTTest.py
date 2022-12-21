from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.quantileWeighted import feature as checks


@TestFeature
@Name("welchTTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest("1.0"))
def feature(self, func="welchTTest({params})", table=None):
    """Check welchTTest aggregate function by using the same tests as for quantileWeighted."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func)

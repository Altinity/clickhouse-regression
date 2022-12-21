from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.welchTTest import feature as checks


@TestFeature
@Name("studentTTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest("1.0"))
def feature(self, func="studentTTest({params})", table=None):
    """Check studentTTest aggregate function by using the same tests as for welchTTest."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table
    checks(func=func)

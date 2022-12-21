from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest,
)

from helpers.common import check_clickhouse_version
from aggregate_functions.tests.welchTTest import feature as checks


@TestFeature
@Name("studentTTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StudentTTest("1.0"))
def feature(self, func="studentTTest({params})", table=None, snapshot_id=None):
    """Check studentTTest aggregate function by using the same tests as for welchTTest."""
    if snapshot_id is None:
        if check_clickhouse_version(">=22.6")(self):
            snapshot_id = name.basename(current().name) + ">=22.6"

    if table is None:
        table = self.context.table

    checks(func=func, snapshot_id=snapshot_id)

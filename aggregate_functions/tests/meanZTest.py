from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MeanZTest,
)

from helpers.common import check_clickhouse_version
from aggregate_functions.tests.welchTTest import feature as checks


@TestFeature
@Name("meanZTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MeanZTest("1.0"))
def feature(self, func="meanZTest({params})", table=None, snapshot_id=None):
    """Check meanZTest aggregate function by using the same tests as for welchTTest."""
    if snapshot_id is None:
        if check_clickhouse_version(">=22.6")(self):
            snapshot_id = name.basename(current().name) + ">=22.6"

    if table is None:
        table = self.context.table

    _func = func.replace("({params})", f"(0.7, 0.45, 0.95)({{params}})")

    checks(func=_func, snapshot_id=snapshot_id)

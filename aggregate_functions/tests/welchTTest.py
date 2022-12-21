from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest,
)

from helpers.common import check_clickhouse_version
from aggregate_functions.tests.steps import get_snapshot_id, execute_query
from aggregate_functions.tests.quantileWeighted import feature as checks


@TestFeature
@Name("welchTTest")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_WelchTTest("1.0"))
def feature(self, func="welchTTest({params})", table=None, snapshot_id=None):
    """Check welchTTest aggregate function by using the same tests as for quantileWeighted."""
    if snapshot_id is None:
        if check_clickhouse_version(">=22.6")(self):
            snapshot_id = name.basename(current().name) + ">=22.6"

    self.context.snapshot_id = get_snapshot_id(snapshot_id)

    if table is None:
        table = self.context.table

    with Check("single value in 0 population"):
        execute_query(
            f"SELECT {func.format(params='sample_data,sample_index')} FROM values('sample_data Int8, sample_index Int8', (10,0), (11,1), (12,1), (1,1), (2,1), (3,1))"
        )

    with Check("single value in 1 population"):
        execute_query(
            f"SELECT {func.format(params='sample_data,sample_index')} FROM values('sample_data Int8, sample_index Int8', (10,1), (11,0), (12,0), (1,0), (2,0), (3,0))"
        )

    checks(func=func, snapshot_id=snapshot_id)

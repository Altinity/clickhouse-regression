from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SimpleLinearRegression,
)

from helpers.common import check_clickhouse_version
from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import feature as checks


@TestFeature
@Name("simpleLinearRegression")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_SimpleLinearRegression("1.0")
)
def feature(self, func="simpleLinearRegression({params})", table=None):
    """Check simpleLinearRegression aggregate function by using the same tests as for covarPop."""
    snapshot_id = get_snapshot_id(clickhouse_version="<22.6")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, snapshot_id=snapshot_id)

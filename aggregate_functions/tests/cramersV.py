from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersV,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import scenario as checks


@TestScenario
@Name("cramersV")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersV("1.0"))
def scenario(self, func="cramersV({params})", table=None):
    """Check cramersV aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(
        func=func,
        table=table,
        decimal=False,
        extended_precision=False,
        snapshot_id=self.context.snapshot_id,
    )

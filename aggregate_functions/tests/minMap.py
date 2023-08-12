from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MinMap,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.sumMap import scenario as checks


@TestScenario
@Name("minMap")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_MinMap("1.0"))
def scenario(self, func="minMap({params})", table=None):
    """Check minMap aggregate function by using the same tests as for sumMap."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    checks(func=func, table=table)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Contingency,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.covarPop import scenario as checks


@TestScenario
@Name("contingency")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_Contingency("1.0"))
def scenario(self, func="contingency({params})", table=None, snapshot_id=None):
    """Check contingency aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id(
        snapshot_id=snapshot_id, add_analyzer=True
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(
        func=func,
        table=table,
        decimal=False,
        extended_precision=False,
        snapshot_id=self.context.snapshot_id,
    )

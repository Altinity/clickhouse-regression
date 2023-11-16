from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevSamp,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.avg import scenario as checks


@TestScenario
@Name("stddevSamp")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Standard_StddevSamp("1.0"))
def scenario(self, func="stddevSamp({params})", table=None, snapshot_id=None):
    """Check stddevSamp aggregate function by using the same checks as for avg."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if 'Merge' in self.name:
        return self.context.snapshot_id, func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False, snapshot_id=self.context.snapshot_id)

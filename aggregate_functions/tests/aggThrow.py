from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AggThrow,
)


@TestScenario
@Name("aggThrow")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_AggThrow("1.0")
)
def scenario(
    self,
    func="aggThrow({params})",
):
    """Check aggThrow aggregate function."""
    self.context.snapshot_id = get_snapshot_id()

    if table is None:
        table = self.context.table

    
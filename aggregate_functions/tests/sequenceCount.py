from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceCount,
)
from aggregate_functions.tests.sequenceMatch import scenario as checks


@TestScenario
@Name("sequenceCount")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Parametric_SequenceCount("1.0"))
def scenario(
    self,
    func="sequenceCount({params})",
    table=None,
    decimal=True,
    snapshot_id=None,
    date=True,
    datetime=True,
):
    """Check sequenceCount parametric aggregate function by using the same tests as for sequenceMatch."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if table is None:
        table = self.context.table

    checks(
        func=func,
        table=table,
        decimal=decimal,
        date=date,
        datetime=datetime,
        snapshot_id=self.context.snapshot_id,
    )

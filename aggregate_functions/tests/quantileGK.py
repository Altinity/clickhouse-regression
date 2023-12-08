from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileGK,
)

from aggregate_functions.tests.steps import get_snapshot_id
from aggregate_functions.tests.avg import scenario as checks


@TestScenario
@Name("quantileGK")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_QuantileGK("1.0"))
def scenario(
    self,
    func="quantileGK({params})",
    table=None,
    decimal=True,
    date=True,
    datetime=True,
    extended_precision=False,
    snapshot_id=None,
):
    """Check quantileGK aggregate function by using the same tests as for avg."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    _func = func.replace(
        "({params})", f"(100)({{params}})"
    )

    if "Merge" in self.name:
        return self.context.snapshot_id, _func.replace("({params})", "")

    if table is None:
        table = self.context.table

    checks(
        func=_func,
        table=table,
        decimal=decimal,
        date=date,
        datetime=datetime,
        extended_precision=extended_precision,
        snapshot_id=self.context.snapshot_id,
    )

    if "State" not in self.name:
        for i in range(5, 100, 20):
            _func = func.replace(
                "({params})", f"({i})({{params}})"
            )
            with Check(f"accuracy {i}"):
                checks(
                    func=_func,
                    table=table,
                    decimal=decimal,
                    date=date,
                    datetime=datetime,
                    extended_precision=extended_precision,
                    snapshot_id=self.context.snapshot_id,
                )

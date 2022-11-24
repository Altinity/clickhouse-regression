from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantile,
)

from aggregate_functions.tests.avg import feature as checks


@TestFeature
@Name("quantile")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_Quantile("1.0"))
def feature(
    self,
    func="quantile({params})",
    table=None,
    decimal=True,
    date=False,
    datetime=False,
    extended_precision=False,
):
    """Check quantile aggregate function by using the same tests as for avg."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(
        func=func,
        table=table,
        decimal=decimal,
        date=date,
        datetime=datetime,
        extended_precision=extended_precision,
    )

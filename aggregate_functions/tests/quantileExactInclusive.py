from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactInclusive,
)

from aggregate_functions.tests.quantile import feature as checks


@TestFeature
@Name("quantileExactInclusive")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_QuantileExactInclusive("1.0")
)
def feature(self, func="quantileExactInclusive({params})", table=None):
    """Check quantileExactInclusive aggregate function by using the same tests as for quantile."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    checks(func=func, table=table, decimal=False)

from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull,
)

from aggregate_functions.tests.first_value import feature as firstvalue_feature


@TestFeature
@Name("singleValueOrNull")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_SingleValueOrNull("1.0")
)
def feature(self, func="singleValueOrNull({params})", table=None):
    """Check singleValueOrNull aggregate function by using the same tests as for first_value."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    firstvalue_feature(func=func, table=table)

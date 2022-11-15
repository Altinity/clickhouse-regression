from testflows.core import *

from aggregate_functions.tests.steps import execute_query
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray,
)

from aggregate_functions.tests.any import feature as checks


@TestFeature
@Name("groupArray")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_GroupArray("1.0"))
def feature(self, func="groupArray({params})", table=None):
    """Check groupArray aggregate function by using the same tests as for any."""
    self.context.snapshot_id = name.basename(current().name)

    if table is None:
        table = self.context.table

    params = "({params})"
    checks(func=func, table=table)

    with Check("max size"):
        for size in range(1,10):
            with When(f"{size}"):
                _func = func.replace(params,f"({size}){params}")
                execute_query(
                    f"SELECT {_func.format(params='number')} FROM numbers(8)"
                )
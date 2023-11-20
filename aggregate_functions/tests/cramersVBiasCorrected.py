from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersVBiasCorrected,
)

from aggregate_functions.tests.steps import *
from aggregate_functions.tests.covarPop import scenario as checks


@TestScenario
@Name("cramersVBiasCorrected")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Miscellaneous_CramersVBiasCorrected("1.0")
)
def scenario(self, func="cramersVBiasCorrected({params})", table=None, snapshot_id=None):
    """Check cramersVBiasCorrected aggregate function by using the same checks as for covarPop."""
    self.context.snapshot_id = get_snapshot_id(snapshot_id=snapshot_id)

    if 'Merge' in self.name:
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

    with Check("example_2"):
        execute_query(
            f"SELECT {func.format(params='a,b')}, any(toTypeName(a)), any(toTypeName(b)) FROM (SELECT number % 10 AS a, number % 4 AS b FROM numbers(150))"
        )

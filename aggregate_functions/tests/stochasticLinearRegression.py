from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLinearRegression,
)

from aggregate_functions.tests.avg import scenario as checks


@TestScenario
@Name("stochasticLinearRegression")
@Requirements(
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_StochasticLinearRegression("1.0")
)
def scenario(self, func="stochasticLinearRegression({params})", table=None):
    """Check stochasticLinearRegression aggregate function by using the same tests as for avg."""

    if table is None:
        table = self.context.table

    _func = func.replace(
        "({params})",
        f"(0.1, 0.0, 5, 'SGD')({{params}}*0.1+{{params}}*0.2+7,{{params}},{{params}}*0.3)",
    )

    checks(func=_func, table=table, decimal=False)

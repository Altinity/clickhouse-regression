from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State,
)


@TestFeature
def state(self, suite, func):
    """Check -State combinator function."""
    suite(func=func)


@TestFeature
@Name("state")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State("1.0"))
def feature(self):
    """Check aggregate functions `-State` combinator
    that serializes the state of the function."""

    with Pool(5) as executor:
        for name in aggregate_functions:
            func = f"hex({name}State({{params}}))"
            if name == "exponentialMovingAverage":
                func = f"hex({name}State(0.5)({{params}}))"
            try:
                suite = load(f"aggregate_functions.tests.{name}", "feature")
            except ModuleNotFoundError as e:
                with Suite(f"{name}State"):
                    xfail(reason=f"{name}State() tests are not implemented")
            else:
                Suite(
                    name=f"{name}State", test=state, parallel=True, executor=executor
                )(func=func, suite=suite)

        join()

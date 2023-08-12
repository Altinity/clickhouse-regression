from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State,
)


@TestScenario
def state(self, scenario, func):
    """Check -State combinator function."""
    scenario(func=func)


@TestFeature
@Name("state")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State("1.0"))
def feature(self):
    """Check aggregate functions `-State` combinator
    that serializes the state of the function."""

    with Pool(5) as executor:
        for name in aggregate_functions:
            func = f"hex({name}State({{params}}))"
            try:
                scenario = load(f"aggregate_functions.tests.{name}", "scenario")
            except ModuleNotFoundError as e:
                with Scenario(f"{name}State"):
                    skip(reason=f"{name}State() test is not implemented")
            else:
                Scenario(
                    name=f"{name}State", test=state, parallel=True, executor=executor
                )(func=func, scenario=scenario)

        join()

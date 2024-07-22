from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State,
)


@TestScenario
def state(self, scenario, func, extra_data=None):
    """Check -State combinator function."""
    scenario(func=func, extra_data=extra_data)


@TestFeature
@Name("state")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State("1.0"))
def feature(self, extra_data=None):
    """Check aggregate functions `-State` combinator
    that serializes the state of the function."""

    with Pool(15) as executor:
        for name in aggregate_functions:
            if "alias" in name:
                name_ = name.replace("_alias", "")
                func = f"hex({name_}State({{params}}))"
            else:
                func = f"hex({name}State({{params}}))"
            try:
                scenario = load(f"aggregate_functions.tests.{name}", "scenario")
            except ModuleNotFoundError as e:
                with Scenario(f"{name}State"):
                    skip(reason=f"{name}State() test is not implemented")
            else:
                if extra_data is not None:
                    if name in funcs_to_run_with_extra_data:
                        Scenario(
                            name=f"{name}State",
                            test=state,
                            parallel=True,
                            executor=executor,
                        )(func=func, scenario=scenario, extra_data=extra_data)
                else:
                    Scenario(
                        name=f"{name}State",
                        test=state,
                        parallel=True,
                        executor=executor,
                    )(func=func, scenario=scenario)
        join()

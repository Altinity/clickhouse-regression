from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State,
)


@TestScenario
def state(self, scenario, func, table=None, extra_data=None):
    """Check -State combinator function."""
    if extra_data is not None:
        scenario(func=func, extra_data=extra_data, table=table)
    else:
        scenario(func=func, table=table)


@TestFeature
@Name("state")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Combinator_State("1.0"))
def feature(self, table=None, extra_data=None):
    """Check aggregate functions `-State` combinator
    that serializes the state of the function."""

    if extra_data is not None:
        with Pool() as executor:
            for name in funcs_to_run_with_extra_data:
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
                    Scenario(
                        name=f"{name}State",
                        test=state,
                        parallel=True,
                        executor=executor,
                    )(func=func, scenario=scenario, table=table, extra_data=extra_data)
            join()
    else:
        with Pool() as executor:
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
                    Scenario(
                        name=f"{name}State",
                        test=state,
                        parallel=True,
                        executor=executor,
                    )(func=func, table=table, scenario=scenario)
            join()

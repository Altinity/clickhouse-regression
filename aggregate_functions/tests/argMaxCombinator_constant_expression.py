from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax,
)
from aggregate_functions.tests.steps import *


@TestScenario
def check_combinator(self, scenario, func, combinator):
    """Check -ArgMax combinator function."""
    current().name = current().name.replace(
        f"{combinator}Combinator_constant_expression/", ""
    )
    current().context.compare_json_values = True
    scenario(func=func)


@TestFeature
@Name("ArgMaxCombinator_constant_expression")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMax("1.0"))
def feature(self, combinator="ArgMax"):
    """
    Check that function with -ArgMax combinator and constant
    expression works as function without combinator.
    """
    with Pool(15) as executor:
        for function_name in aggregate_functions:
            params = "{params}, 1"
            if "alias" in function_name:
                function_name_ = function_name.replace("_alias", "")
                func = f"{function_name_}{combinator}({params})"
            else:
                func = f"{function_name}{combinator}({params})"
            try:
                scenario = load(
                    f"aggregate_functions.tests.{function_name}", "scenario"
                )
            except ModuleNotFoundError as e:
                skip(reason=f"{function_name} not found")
            else:
                Scenario(
                    name=f"{function_name}",
                    test=check_combinator,
                    parallel=True,
                    executor=executor,
                )(func=func, scenario=scenario, combinator=combinator)
        join()

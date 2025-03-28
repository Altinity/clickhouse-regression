from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin,
)
from aggregate_functions.tests.steps import *


@TestScenario
def check_combinator(self, scenario, func, combinator):
    """Check -ArgMin combinator function."""
    self.context.compare_json_values = True
    self.context.replace_part = f"{combinator}Combinator_constant_expression/"
    scenario(func=func)


@TestFeature
@Name("ArgMinCombinator_constant_expression")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin("1.0"))
def feature(self, combinator="ArgMin"):
    """
    Check that function with -ArgMin combinator and constant
    expression works as function without combinator.
    """
    self.context.snapshot_id = get_snapshot_id()
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

    with Check("Check very long {-ArgMinArgMax} combinator"):
        combinator = "ArgMinArgMax" * 84
        expr = ", 1" * 84 * 2
        query = f"SELECT sum{combinator}(number{expr}) FROM numbers(10)"
        exitcode, message = (
            131,
            "DB::Exception: Too long name of aggregate function, maximum: 1000",
        )
        execute_query(query, exitcode=exitcode, message=message)

    with Check("Check long {-ArgMinArgMax} combinator"):
        combinator = "ArgMinArgMax" * 83
        expr = ", 1" * 83 * 2
        query = f"SELECT sum{combinator}(number{expr}) FROM numbers(10)"
        execute_query(query)

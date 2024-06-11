from testflows.core import *

from aggregate_functions.requirements import (
    RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin,
)
from aggregate_functions.tests.steps import *


@TestFeature
@Name("ArgMinStateCombinator_constant_expression")
@Requirements(RQ_SRS_031_ClickHouse_AggregateFunctions_Specific_ArgMin("1.0"))
def feature(self, combinator="ArgMin"):
    """
    Check that function with -ArgMinState combinator and constant
    expression works as function with only -State combinator.
    """
    self.context.snapshot_id = get_snapshot_id()

    with Pool(15) as executor:
        for function_name in aggregate_functions:
            params = "{params}, 1"
            if "alias" in function_name:
                function_name_ = function_name.replace("_alias", "")
                func = f"hex({function_name_}{combinator}State({params}))"
            else:
                func = f"hex({function_name}{combinator}State({params}))"
            try:
                scenario = load(
                    f"aggregate_functions.tests.{function_name}", "scenario"
                )
            except ModuleNotFoundError as e:
                skip(reason=f"{function_name} not found")
            else:
                Scenario(
                    name=f"{function_name}{combinator}State_const_expr",
                    test=scenario,
                    parallel=True,
                    executor=executor,
                )(func=func)
        join()

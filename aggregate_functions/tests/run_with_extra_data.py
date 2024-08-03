from testflows.core import *
from aggregate_functions.tests.steps import *


@TestFeature
@Name("extra data")
def feature(self, table=None):
    """Run chosen aggregate function tests on a table with extra data."""

    with Pool(10) as executor:
        for name in funcs_to_run_with_extra_data:
            try:
                scenario = load(f"aggregate_functions.tests.{name}", "scenario")
            except ModuleNotFoundError:
                with Scenario(f"{name}"):
                    skip(reason=f"{name} test is not implemented")
                continue

            Scenario(test=scenario, parallel=True, executor=executor)(
                table=table, extra_data=True
            )
        join()

    Feature(test=load("aggregate_functions.tests.state", "feature"))(
        extra_data=True, table=table
    )

    with Pool(2) as executor:
        Feature(
            test=load("aggregate_functions.tests.merge", "feature"),
            parallel=True,
            executor=executor,
        )(extra_data=True)
        Feature(
            test=load("aggregate_functions.tests.finalizeAggregation", "feature"),
            parallel=True,
            executor=executor,
        )(extra_data=True)
        join()

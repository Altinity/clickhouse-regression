from testflows.core import *
from aggregate_functions.tests.steps import aggregate_functions


@TestFeature
@Name("function_list")
@Flags(TE)
def feature(self):
    """Check if new aggregate functions was not added in system.functions table."""
    r = self.context.node.query(
        "SELECT name FROM system.functions WHERE is_aggregate=1 and alias_to=''"
    )
    aggregate_functions_list = r.output.strip().split("\n")
    diff = [
        name for name in aggregate_functions_list if name not in aggregate_functions
    ]

    for name in diff:
        with Check(f"untested function {name}", flags=TE):
            fail(f"Aggregate function `{name}` was added, but not tested.")

from testflows.core import *
from aggregate_functions.tests.steps import aggregate_functions


@TestFeature
@Name("function_list")
def feature(self):
    """Check if new aggregate functions was not added in system.functions table."""

    with Check(""):
        r = (
            current()
            .context.node.query(
                "SELECT name FROM system.functions WHERE is_aggregate=1 and alias_to='' ORDER BY name"
            )
            .output
        )
        aggregate_functions_list = r.strip().split("\n")
        diff = [
            name for name in aggregate_functions_list if name not in aggregate_functions
        ]
        assert len(diff) == 0, f"{', '.join(i for i in diff)} was added"

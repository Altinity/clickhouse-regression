from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import *

import aggregate_functions.tests.count as count_tests


@TestSuite
def count(self):
    """Check countState combinator."""
    for scenario in loads(count_tests, Scenario):
        scenario(func="hex(countState({params}))")


@TestFeature
@Name("state")
def feature(self, node="clickhouse1"):
    """Check aggregate functions `-State` combinator that serializes
    the state of the function."""
    self.context.node = self.context.cluster.node(node)

    for name in aggregate_functions:
        suite = getattr(current_module(), name, None)
        with Suite(f"{name}State"):
            if not suite:
                xfail(reason=f"{name}State() tests are not implemented")
            suite()

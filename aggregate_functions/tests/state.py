from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import *

import aggregate_functions.tests.count as count_tests
import aggregate_functions.tests.min as min_tests
import aggregate_functions.tests.max as max_tests


@TestSuite
def count(self):
    """Check countState combinator."""
    for scenario in loads(count_tests, Scenario):
        scenario(func="hex(countState({params}))")


@TestSuite
def min(self):
    """Check minState combinator."""
    for scenario in loads(min_tests, Scenario):
        scenario(func="hex(minState({params}))")


@TestSuite
def max(self):
    """Check maxState combinator."""
    for scenario in loads(max_tests, Scenario):
        scenario(func="hex(maxState({params}))")


@TestFeature
@Name("state")
def feature(self, node="clickhouse1"):
    """Check aggregate functions `-State` combinator that serializes
    the state of the function."""
    self.context.node = self.context.cluster.node(node)

    with Pool(3) as executor:
        for name in aggregate_functions:
            suite = getattr(current_module(), name, None)
            if not suite:
                with Suite(f"{name}State"):
                    xfail(reason=f"{name}State() tests are not implemented")
            else:
                Suite(name=f"{name}State", run=suite, parallel=True, executor=executor)

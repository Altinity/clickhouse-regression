from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import *

import aggregate_functions.tests.count as count_tests
import aggregate_functions.tests.min as min_tests
import aggregate_functions.tests.max as max_tests
import aggregate_functions.tests.sum as sum_tests


@TestSuite
def count(self):
    """Check countState combinator."""
    load(count_tests, "feature")(func="hex(countState({params}))")


@TestSuite
def min(self):
    """Check minState combinator."""
    load(min_tests, "feature")(func="hex(minState({params}))")


@TestSuite
def max(self):
    """Check maxState combinator."""
    load(max_tests, "feature")(func="hex(maxState({params}))")


@TestSuite
def sum(self):
    """Check sumState combinator."""
    load(sum_tests, "feature")(func="hex(sumState({params}))")


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

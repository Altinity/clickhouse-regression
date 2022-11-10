from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import *

import aggregate_functions.tests.count as count_tests
import aggregate_functions.tests.min as min_tests
import aggregate_functions.tests.max as max_tests
import aggregate_functions.tests.sum as sum_tests
import aggregate_functions.tests.avg as avg_tests
import aggregate_functions.tests.any as any_tests
import aggregate_functions.tests.argMin as argMin_tests
import aggregate_functions.tests.argMax as argMax_tests


@TestFeature
def count(self):
    """Check countState combinator."""
    load(count_tests, "feature")(func="hex(countState({params}))")


@TestFeature
def min(self):
    """Check minState combinator."""
    load(min_tests, "feature")(func="hex(minState({params}))")


@TestFeature
def max(self):
    """Check maxState combinator."""
    load(max_tests, "feature")(func="hex(maxState({params}))")


@TestFeature
def sum(self):
    """Check sumState combinator."""
    load(sum_tests, "feature")(func="hex(sumState({params}))")


@TestFeature
def avg(self):
    """Check avgState combinator."""
    load(avg_tests, "feature")(func="hex(avgState({params}))")


@TestFeature
def any(self):
    """Check anyState combinator."""
    load(any_tests, "feature")(func="hex(anyState({params}))")


@TestFeature
def argMin(self):
    """Check argMinState combinator."""
    load(argMin_tests, "feature")(func="hex(argMinState({params}))")


@TestFeature
def argMax(self):
    """Check argMaxState combinator."""
    load(argMax_tests, "feature")(func="hex(argMaxState({params}))")


@TestFeature
@Name("state")
def feature(self, node="clickhouse1"):
    """Check aggregate functions `-State` combinator that serializes
    the state of the function."""
    self.context.node = self.context.cluster.node(node)

    with Pool(5) as executor:
        for name in aggregate_functions:
            suite = getattr(current_module(), name, None)
            if not suite:
                with Suite(f"{name}State"):
                    xfail(reason=f"{name}State() tests are not implemented")
            else:
                Suite(name=f"{name}State", run=suite, parallel=True, executor=executor)

        join()
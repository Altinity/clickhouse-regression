from testflows.core import *

from aggregate_function_type.tests.steps import *
from aggregate_function_type.requirements import *


@TestFeature
@Name("tests")
def feature(self, node="clickhouse1"):
    """Check AggregateFunction data type."""
    self.context.node = self.context.cluster.node(node)

    xfail("not implemented")

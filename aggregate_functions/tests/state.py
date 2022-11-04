from testflows.core import *

from aggregate_functions.tests.steps import *
from aggregate_functions.requirements import *


@TestFeature
@Name("state")
def feature(self, node="clickhouse1"):
    """Check aggregate functions `-State` combinator that serializes
    the state of the function."""
    self.context.node = self.context.cluster.node(node)

    xfail(reason="not implemented")

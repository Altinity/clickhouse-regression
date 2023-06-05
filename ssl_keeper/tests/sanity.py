from testflows.core import *
from testflows.asserts import error


@TestScenario
def select_1(self):
    """Check that SELECT 1 works on all nodes."""
    for name in self.context.cluster.nodes["clickhouse"]:
        node = self.context.cluster.node(name)

        with Check(f"{name}"):
            with When("I try to execute SELECT 1 query"):
                retry(node.query, timeout=300, delay=10)(
                    "SELECT 1", message="1", exitcode=0
                )


@TestFeature
@Name("sanity")
def feature(self):
    """Sanity check suite."""
    Scenario(run=select_1)

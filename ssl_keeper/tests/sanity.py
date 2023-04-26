from testflows.core import *
from testflows.asserts import error


@TestScenario
def select_1(self):
    """Check that SELECT 1 works on all nodes."""
    for name in self.context.cluster.nodes["clickhouse"]:
        node = self.context.cluster.node(name)

        with Check(f"{name}"):
            with When("I try to execute SELECT 1 query"):
                r = node.query("SELECT 1")
                pause()

            with Then("it should work"):
                assert r.output == "1", error()


@TestFeature
@Name("sanity")
def feature(self):
    """Sanity check suite."""
    Scenario(run=select_1)

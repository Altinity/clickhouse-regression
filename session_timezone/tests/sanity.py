from testflows.core import *
from testflows.asserts import error


@TestScenario
def select_timezone_of_now(self):
    """Check that session_timezone setting works on all nodes."""
    for name in self.context.cluster.nodes["clickhouse"]:
        node = self.context.cluster.node(name)

        with Check(f"on node {name}"):
            with When("I check that session_timezone is changing timezone"):
                node.query("select timezoneOf(now());", message="Europe/Berlin")
                node.query(
                    "select timezoneOf(now()) SETTINGS session_timezone = 'Asia/Novosibirsk' format TSV;",
                    message="Asia/Novosibirsk",
                )


@TestFeature
@Name("sanity")
def feature(self):
    """Sanity check suite."""
    for scenario in loads(current_module(), Scenario):
        scenario()

from testflows.core import *
from testflows.asserts import error

from helpers.common import check_clickhouse_version


@TestScenario
@Name("throwIf function")
def throw_if(self, node="clickhouse1"):
    """Check that ClickHouse provides stacktraces properly for throwIf function."""
    node = self.context.cluster.node(node)

    with When("I execute query with exception"):
        r = node.query("SELECT throwIf(1,'throw')", no_checks=True, query_id=10000)

    for attempt in retries(timeout=40, delay=5):
        with attempt:
            with Then("I get stack trace for this query"):
                stack_trace = node.query(
                    "SELECT stack_trace FROM system.query_log where query_id='10000'",
                    no_checks=True,
                ).output

            with And("I check query_log table is created"):
                assert not ("Table system.query_log" in stack_trace), error()

            with And("I check query appeared in query_log table"):
                assert stack_trace != "", error()

    with Then("I check stacktrace"):
        if check_clickhouse_version(">=22.8")(self):
            assert "DB::Exception" in stack_trace, error()
        else:
            assert "DB::Function" in stack_trace, error()


@TestFeature
@Name("exceptions")
def feature(self):
    self.context.node = self.context.cluster.node("clickhouse1")
    for scenario in loads(current_module(), Scenario):
        scenario()

from key_value.tests.steps import *
from key_value.tests.checks import *


@TestOutline
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Constant("1.0"))
def constant_input(self, input, output, params, node=None):
    """Check that clickhouse extractKeyValuePairs function support constant input string."""

    if node is None:
        node = self.context.node

    with Then("I check extractKeyValuePairs function returns correct value for constant input"):
        check_constant_input(input=input, output=output, params=params)


@TestModule
@Name("constant")
def module(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support constant input string."""

    self.context.node = self.context.cluster.node(node)

    for check in checks:
        check(scenario=constant_input)

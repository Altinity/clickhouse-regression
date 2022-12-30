from key_value.tests.steps import *
from key_value.tests.checks import *


@TestOutline
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Array("1.0"))
def array_input(self, input, output, params, node=None):
    """Check that clickhouse extractKeyValuePairs function support input as the value from the array."""

    if node is None:
        node = self.context.node

    with Then("I check parseKeyValue function returns correct value"):
        r = node.query(
            f"SELECT extractKeyValuePairs([{input}][1], {params})", use_file=True
        )
        assert r.output == output, error()


@TestFeature
@Name("array")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Array("1.0"))
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support input as value from an array."""

    self.context.node = self.context.cluster.node(node)
    for check in checks:
        Scenario(test=check)(scenario=array_input)

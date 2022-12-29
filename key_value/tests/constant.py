from key_value.tests.steps import *


@TestOutline
def constant_input(self, input, output, params, node=None):
    """Check that clickhouse extractKeyValuePairs function support constant input."""

    if node is None:
        node = self.context.node

    with Then("I check extractKeyValuePairs function returns correct value for constant input"):
        check_constant_input(input=input, output=output, params=params)


@TestModule
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_RecognizedKeyValuePairs("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Output("1.0")
)
@Name("constant")
def module(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support constant."""

    self.context.node = self.context.cluster.node(node)

    key_format_feature(scenario=constant_input)
    value_format_feature(scenario=constant_input)
    input_format(scenario=constant_input)
    specifying_special_symbols(scenario=constant_input)

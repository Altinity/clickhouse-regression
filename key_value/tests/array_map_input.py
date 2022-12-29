from key_value.tests.steps import *
import json


@TestOutline
def array_input(self, input, output, params, node=None):
    """Check that clickhouse extractKeyValuePairs function support input as value from array."""

    if node is None:
        node = self.context.node

    with Then("I check parseKeyValue function returns correct value"):
        r = node.query(f"SELECT extractKeyValuePairs([{input}][1], {params})", use_file=True)
        assert r.output == output, error()


@TestScenario
def map_input(self, input, output, params, node=None):
    """Check that clickhouse extractKeyValuePairs function support input as value from map."""

    if node is None:
        node = self.context.node

    with Then("I check parseKeyValue function returns correct value"):
        r = node.query(f"SELECT extractKeyValuePairs(map({input}, {input})[{input}], {params})", use_file=True)
        assert r.output == output, error()


@TestModule
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function("1.0")
)
@Name("array_map_input")
def module(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support input as value from array and map."""

    self.context.node = self.context.cluster.node(node)
    for outline in loads(current_module(), Outline):
        key_format_feature(scenario=outline)
        value_format_feature(scenario=outline)
        input_format(scenario=outline)
        specifying_special_symbols(scenario=outline)
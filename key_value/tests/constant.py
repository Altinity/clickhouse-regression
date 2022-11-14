from key_value.tests.steps import *


@TestScenario
def constant_input(self, input_string, output_string, node=None):
    """Check that clickhouse parseKeyValue function support constant input."""

    if node is None:
        node = self.context.node

    with Then("I check parseKeyValue function returns correct value"):
        r = node.query(f"SELECT parseKeyValue({input_string})")
        assert r.output == output_string, error()


@TestModule
@Requirements(RQ_ClickHouse_ParseKeyValue("1.0"))
@Name("constant")
def feature(self, node="clickhouse1"):
    """Check that clickhouse parseKeyValue function support constant input."""

    self.context.node = self.context.cluster.node(node)

    with open("tests/input_strings") as input_strings:
        with open("tests/output_strings") as output_strings:
            for input_string in input_strings:
                output_string = output_strings.readline()
                with Feature(f"parsing {input_string}"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(input_string=input_string, output_string=output_string)

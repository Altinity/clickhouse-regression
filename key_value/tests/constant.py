from key_value.tests.steps import *
import json


@TestScenario
def constant_input(self, input_string, output_string, node=None):
    """Check that clickhouse extractKeyValuePairs function support constant input."""

    if node is None:
        node = self.context.node

    with Then("I check parseKeyValue function returns correct value"):
        r = node.query(f"SELECT extractKeyValuePairs({input_string})", use_file=True)
        if ':' in output_string and ':' in r.output:
            assert json.loads(r.output.replace("'", '"')) == json.loads(output_string.replace("'", '"')), error()
        else:
            assert r.output == output_string, error()


@TestModule
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_RecognizedKeyValuePairs("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format("1.0"),
)
@Name("constant")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support constant input."""

    self.context.node = self.context.cluster.node(node)

    with open("tests/input_strings") as input_strings:
        with open("tests/output_strings") as output_strings:
            for input_string in input_strings:
                output_string = output_strings.readline()
                with Feature(f"parsing {input_string}"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(input_string=input_string[0:-1], output_string=output_string[0:-1])

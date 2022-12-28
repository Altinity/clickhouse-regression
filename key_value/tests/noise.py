from key_value.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter("1.0"))
def noise(self, node=None):
    """Check that clickhouse extractKeyValuePairs function removes all noise
    that is not related to the key or value."""

    if node is None:
        node = self.context.node

    noise = askii_punctuation_marks.replace("\\", "\\\\").replace('"', '\\"').\
        replace("!", "\\!").replace("`", "\\`").replace("'", "\\'")
    key1 = askii_alfa + "1"
    key2 = askii_alfa + "2"
    value = askii_num

    with When("I specifying input and output values for extractKeyValuePairs function"):
        input_strings = [f"'{noise} {key1}:{value} {noise}, {noise} {key2}:{value} {noise}'"]
        print(input_strings[0])
        output_strings = ["{'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1':'0123456789',"
                          "'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz2':'0123456789'}"]

    with Then("I check extractKeyValuePairs function returns correct value"):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, output_string=output_strings[i])


@TestFeature
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise("1.0"))
@Name("noise")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function removes all noise
    that is not related to the key or value."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
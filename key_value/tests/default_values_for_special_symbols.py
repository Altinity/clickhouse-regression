from key_value.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ValueSpecialCharactersAllowList("1.0"),
              RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EnclosingCharacter("1.0"),
              RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ItemDelimiter("1.0"),
              RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_KeyValuePairDelimiter("1.0"),
              RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter("1.0"))
def special_symbols_default_values(self, node=None):
    """Check that clickhouse extractKeyValuePairs default values for special symbols are
    `\` - for escape_character, `:` - for key_value_pair_delimiter, `,` for item_delimeter
    `"` for enclosing_character, empty string for value_special_characters_allow_list."""

    if node is None:
        node = self.context.node

    with When("I specifying input and output values for extractKeyValuePairs function"):
        input_strings = ["'krgk:\)kfrkfk, www:\")_)(_\"'"]
        output_strings = ["{'krgk':')kfrkfk','www':')_)(_'}"]

    with Then("I check extractKeyValuePairs function returns correct value"):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, output_string=output_strings[i])


@TestFeature
@Requirements()
@Name("default special symbols")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs default values for special symbols are
    `\` - for escape_character, `:` - for key_value_pair_delimiter, `,` for item_delimeter
    `"` for enclosing_character, empty string for value_special_characters_allow_list."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
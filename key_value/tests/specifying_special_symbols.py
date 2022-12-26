from key_value.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter("1.0"))
def specifying_escape_character(self, node=None):
    """Check that clickhouse extractKeyValuePairs function support specifying escape character."""

    if node is None:
        node = self.context.node
    with When("I specifying input and output values for extractKeyValuePairs function"):
        input_strings = ["'krgkp:kfrkfkrkf:a, www:www', 'p'"]
        output_strings = ["{'krgk:kfrkfkrkf':'a','www':'www'}"]

    with Then("I check extractKeyValuePairs function returns correct value"):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, output_string=output_strings[i])


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_KeyValuePairDelimiter("1.0"))
def specifying_key_value_pair_delimiter(self, node=None):
    """Check that clickhouse extractKeyValuePairs function support specifying key value pair delimiter."""

    if node is None:
        node = self.context.node

    with When("I specifying input and output values for extractKeyValuePairs function"):
        input_strings = ["'krgkpkfrkfkrkf, wwwpwww', '\\\\', 'p'"]
        output_strings = ["{'krgk':'kfrkfkrkf','www':'www'}"]

    with Then("I check extractKeyValuePairs function returns correct value"):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, output_string=output_strings[i])


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ItemDelimiter("1.0"))
def specifying_item_delimiter(self, node=None):
    """Check that clickhouse extractKeyValuePairs function support specifying item delimiter."""

    if node is None:
        node = self.context.node

    with When("I specifying input and output values for extractKeyValuePairs function"):
        input_strings = ["'krgk:kfrkfkrkfp www:www', '\\\\', ':', 'p'"]
        output_strings = ["{'krgk':'kfrkfkrkf','www':'www'}"]

    with Then("I check extractKeyValuePairs function returns correct value"):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, output_string=output_strings[i])


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EnclosingCharacter("1.0"))
def specifying_enclosing_character(self, node=None):
    """Check that clickhouse extractKeyValuePairs function support specifying enclosing character."""

    if node is None:
        node = self.context.node

    with When("I specifying input and output values for extractKeyValuePairs function"):
        input_strings = ["'p!@#$%^&*()[]krgkp:pkfrkfkrkf[]!@#$%^&*()p', '\\\\', ':', ',', 'p'"]
        output_strings = ["{'!@#$%^&*()[]krgk':'kfrkfkrkf[]!@#$%^&*()'}"]

    with Then("I check extractKeyValuePairs function returns correct value"):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, output_string=output_strings[i])


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ValueSpecialCharactersAllowList("1.0"))
def specifying_value_special_characters_allow_list(self, node=None):
    """Check that clickhouse extractKeyValuePairs function support specifying value special characters allow list."""

    if node is None:
        node = self.context.node

    with When("I specifying input and output values for extractKeyValuePairs function"):
        input_strings = ["'.,.krgk:.kfrkfkrkf.][', '\\\\', ':', ',', '\\\"', '.]['"]
        output_strings = ["{'krgk':'.kfrkfkrkf.]['}"]

    with Then("I check extractKeyValuePairs function returns correct value"):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, output_string=output_strings[i])


@TestFeature
@Requirements()
@Name("specifying special symbols")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support specifying special symbols."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
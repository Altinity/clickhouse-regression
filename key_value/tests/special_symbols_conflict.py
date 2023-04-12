from key_value.tests.steps import *


@TestScenario
def special_symbols_conflict(self, node=None, i=0, j=0):
    """Check that clickhouse extractKeyValuePairs function returns an error any of the:
    `escape_character`, `key_value_pair_delimiter`, `item_delimiter`, `enclosing_character`,
    `value_special_characters_allow_list` specified with the same symbol."""

    if node is None:
        node = self.context.node

    with When("I specify parameters, some of them with the same symbol"):
        parameters = ["':'", "','", "'\"'"]
        parameters[j] = parameters[i]

    with And("I specifying input values for extractKeyValuePairs function"):
        input_strings = [f"'ppp:pp, qqq:q', {','.join(parameters)}"]

    with Then("I check extractKeyValuePairs function returns an error."):
        for i, input_string in enumerate(input_strings):
            check_constant_input(
                input=input_string, exitcode=36
            )


@TestModule
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_ParametersSpecifying_SpecialCharactersConflict(
        "1.0"
    )
)
@Name("special symbols conflict")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function returns an error any of the:
     `key_value_pair_delimiter`, `pair_delimeter`, `quoting_character` specified with the same symbol."""

    self.context.node = self.context.cluster.node(node)

    parameter_names = [
        "key_value_pair_delimiter",
        "pair_delimiters",
        "quoting_character"
    ]

    for i in range(3):
        for j in range(i + 1, 3):
            with Feature(f"{parameter_names[i]} and {parameter_names[j]}"):
                for scenario in loads(current_module(), Scenario):
                    scenario(i=i, j=j)

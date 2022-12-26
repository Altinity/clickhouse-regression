from key_value.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_EscapeCharacter("1.0"))
def special_symbols_conflict(self, node=None):
    """Check that clickhouse extractKeyValuePairs function returns an error if any
    specified special symbols match."""

    if node is None:
        node = self.context.node

    with When("I specifying input values for extractKeyValuePairs function"):
        input_strings = ["'ppp:pp', 'p', 'p'"]

    with Then("I check extractKeyValuePairs function returns an error."):
        for i, input_string in enumerate(input_strings):
            check_constant_input(input_string=input_string, exitcode=10)# todo fing existing exitcode after inmplementation


@TestFeature
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_SpecialCharactersConflict("1.0"))
@Name("special symbols conflict")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function returns an error if any
    specified special symbols match."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
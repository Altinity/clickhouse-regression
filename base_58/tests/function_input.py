from base_58.tests.steps import *


@TestScenario
def function_input_constant(self, node=None):
    """Check that clickhouse base58 function for constant support input as function result."""

    if node is None:
        node = self.context.node

    with When(
        "I check I can encode string returned as function result"
    ):
        r = node.query(
            f"SELECT base58Encode(reverse('{string_of_all_askii_symbols()*30}'))"
        )
        encoded_string = r.output

    with Then(
        "I check decode value is right even if input of the base58Decode, base58Encode is function result"
    ):
        r = node.query(f"SELECT base58Decode(reverse(reverse('{encoded_string}')))")
        assert encoded_string == r.output, error()


@TestFeature
@Requirements()
@Name("function input")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 function support input as function result."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

from base_58.tests.steps import *


@TestScenario
def function_input_column(self, node=None):
    """Check that clickhouse base58 functions for column support input as function result."""
    if node is None:
        node = self.context.node

    table_name_e58 = f"table_{getuid()}_e58"
    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name_e58, partition="")

    with When("I insert data into the table with base58 encoding with function result input"):
        r = node.query(
            f"insert into {table_name_e58} values (0, Base58Encode(reverse(reverse('{string_of_all_askii_symbols() * 30}'))))",
        )

    with Then("I check data is correctly inserted"):
        r = node.query(f"select base58Decode(reversed(reversed(x))) from {table_name_e58}")
        assert r.output == string_of_all_askii_symbols() * 30


@TestScenario
def function_input_constant(self, node=None):
    """Check that clickhouse base58 functions for constant support input as function result."""

    if node is None:
        node = self.context.node

    with When(
        "I check I can encode string returned as function result"
    ):
        r = node.query(
            f"SELECT base58Encode(reverse(reverse('{string_of_all_askii_symbols()*30}')))"
        )
        encoded_string = r.output

    with Then(
        "I check decode value is right even if input of the base58Decode, base58Encode is function result"
    ):
        r = node.query(f"SELECT base58Decode(reverse(reverse('{encoded_string}')))")
        assert string_of_all_askii_symbols()*30 == r.output, error()


@TestFeature
@Requirements()
@Name("function input")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 function support input as function result."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

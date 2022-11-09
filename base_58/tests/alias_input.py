from base_58.tests.steps import *


@TestScenario
def alias_instead_of_function(self, node=None):
    """Check that clickhouse base58 function support using alias instead of the functions."""

    if node is None:
        node = self.context.node

    with When("I check alias can be used as base58Encode function"):
        r = node.query(
            f"with base58Encode('{string_of_all_askii_symbols()*30}') as fun SELECT fun"
        )
        encoded_string = r.output

    with Then(
        "I check base58Encode function and function from base58 library return the same string"
    ):
        r = node.query(f"with base58Decode('{encoded_string}') as fun SELECT fun")
        assert string_of_all_askii_symbols() * 30 == r.output, error()


@TestScenario
def alias_instead_of_table_and_column(self, node=None):
    """Check that clickhouse base58 function support using alias instead of the table."""

    if node is None:
        node = self.context.node

    table_name_random = f"table_{getuid()}_random"
    table_name_e58 = f"table_{getuid()}_e58"

    with When("I create a table with random engine"):
        create_partitioned_table(
            table_name=table_name_random,
            engine="GenerateRandom(1, 5, 3)",
            order="",
            partition="",
        )

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name_e58, partition="")

    with When(
        "I insert data into the table with base58 encoding with alias expression"
    ):
        node.query(
            f"with Base58Encode('{string_of_all_askii_symbols() * 30}') as str insert into {table_name_e58} select id, str from {table_name_random};",
        )

    with Then("I check data in the table is correctly"):
        r = node.query(
            f"with {table_name_e58} as t select base58Decode(x) from t limit 1",
        )
        assert r.output == string_of_all_askii_symbols() * 30, error()


@TestFeature
@Requirements(RQ_ClickHouse_Base58_Decode("1.0"), RQ_ClickHouse_Base58_Encode("1.0"))
@Name("alias input")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 function support input as alias."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

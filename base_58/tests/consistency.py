import time

from base_58.tests.steps import *


@TestScenario
def consistency_for_column_input(self, node=None):
    """Check that clickhouse base58 function for columns return the same string after being encoded with `base58Encode`
    function and decoded with `base58Decode` function."""
    if node is None:
        node = self.context.node

    table_name_random = f"table_{getuid()}_random"
    table_name = f"table_{getuid()}"
    table_name_e58 = f"table_{getuid()}_e58"

    with When("I create a table with random engine"):
        create_partitioned_table(
            table_name=table_name_random,
            engine="GenerateRandom(1, 5, 3)",
            order="",
            partition="",
        )

    with And("I create table"):
        create_partitioned_table(table_name=table_name)

    with And("I insert data from random table"):
        node.query(
            f"insert into {table_name} select * from {table_name_random} limit 100"
        )

    with And("I compute expected result"):
        expected_result = node.query(f"select sum(length(x)) from {table_name}").output

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name_e58, partition="")

    with When("I insert data into the table with base58 encoding"):
        node.query(
            f"insert into {table_name_e58} select id, base58Encode(x) from {table_name}",
        )

    with When("I decode data from table with base58 encoding"):
        r = node.query(
            f"select sum(length(x)) from (select base58Decode(x) as x from {table_name_e58})",
        )
        base58_decoded = r.output
    with Then("I check data is not changed"):
        assert expected_result == base58_decoded, error()


@TestScenario
def consistency_for_constant_input(self, node=None):
    """Check that clickhouse base58 function for constants return the same string after being encoded with `base58Encode`
    function and decoded with `base58Decode` function."""

    if node is None:
        node = self.context.node

    with When("I encode string"):
        r = node.query(f"SELECT base58Encode('{string_of_all_askii_symbols()*30}')")
        b58_encoded_string = r.output

    with When("I decode string"):
        r = node.query(f"SELECT base58Decode('{b58_encoded_string}')")
        b58_decoded_string = r.output

    with Then("I check strings are not changed after encode, decode"):
        assert b58_decoded_string == string_of_all_askii_symbols() * 30, error()


@TestFeature
@Requirements(RQ_ClickHouse_Base58_Consistency_EncodeDecode("1.0"))
@Name("consistency")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 function return the same string after being encoded with `base58Encode` function and
    decoded with `base58Decode` function."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

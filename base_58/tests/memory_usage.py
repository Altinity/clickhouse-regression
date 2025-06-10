from base_58.tests.steps import *


@TestScenario
def memory_usage_for_column_input(self, node=None):
    """Check that clickhouse base58 and base64 functions for columns has small difference in memory usage."""
    if node is None:
        node = self.context.node

    table_name_random = f"table_{getuid()}_random"
    table_name_e64 = f"table_{getuid()}_e64"
    table_name_e58 = f"table_{getuid()}_e58"

    with When("I create a table with random engine"):
        create_partitioned_table(
            table_name=table_name_random,
            engine="GenerateRandom(1, 500, 3)",
            order="",
            partition="",
        )

    with When("I compute expected result"):
        expected_result = node.query(
            f"select count(*) from (select * from {table_name_random} limit 1000000) FORMAT TabSeparated"
        ).output

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name_e64, partition="")

    with When("I insert data into the table with base64 encoding"):
        node.query(
            f"insert into {table_name_e64} select id, base64Encode(x) from {table_name_random} limit 1000000;",
            query_id=2000,
        )

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name_e58, partition="")

    with When("I insert data into the table with base58 encoding"):
        node.query(
            f"insert into {table_name_e58} select id, base58Encode(x) from {table_name_random} limit 1000000;",
            query_id=2001,
        )

    with When("I decode data from table with base64 encoding"):
        r = node.query(
            f"select count(*) from (select base64Decode(x) as b64 from {table_name_e64}) FORMAT TabSeparated",
            query_id=2002,
        )
        base64_decoded = r.output

    with When("I decode data from table with base58 encoding"):
        r = node.query(
            f"select count(*) from (select base58Decode(x) from {table_name_e58}) FORMAT TabSeparated",
            query_id=2003,
        )
        base58_decoded = r.output
    with Then("I check data is not changed"):
        assert expected_result == base64_decoded == base58_decoded, error()

    for attempt in retries(timeout=100, delay=10):
        with attempt:
            with When("I remember memory usages"):
                r = node.query(
                    f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '2000' FORMAT TabSeparated"
                )
                b64_encode_memory_usage = int(r.output)
                r = node.query(
                    f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '2001' FORMAT TabSeparated"
                )
                b58_encode_memory_usage = int(r.output)
                r = node.query(
                    f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '2002' FORMAT TabSeparated"
                )
                b64_decode_memory_usage = int(r.output)
                r = node.query(
                    f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '2003' FORMAT TabSeparated"
                )
                b58_decode_memory_usage = int(r.output)
                debug(
                    f"b58_encode_memory_usage: {b58_encode_memory_usage},\n"
                    f"b64_encode_memory_usage: {b64_encode_memory_usage},\n"
                    f"b58_decode_memory_usage: {b58_decode_memory_usage},\n"
                    f"b64_decode_memory_usage: {b64_decode_memory_usage}"
                )

                assert b58_encode_memory_usage > 0, error()
                assert b64_encode_memory_usage > 0, error()
                assert b58_decode_memory_usage > 0, error()
                assert b64_decode_memory_usage > 0, error()

    with Then("I check memory usages are similar"):
        assert b58_encode_memory_usage <= b64_encode_memory_usage * 2, error()
        assert b58_decode_memory_usage <= b64_decode_memory_usage * 2, error()


@TestScenario
def memory_usage_for_constant_input(self, node=None):
    """Check that clickhouse base58 and base64 functions for constants has small difference in memory usage."""

    if node is None:
        node = self.context.node

    with Check("constant input"):
        for attempt in retries(timeout=100, delay=10):
            with attempt:
                id_for_retry = (1000 + attempt.retry_number) * 10

                with When("I run base58 encode function"):
                    r = node.query(
                        f"SELECT base58Encode('{string_of_all_askii_symbols()*1000}') FORMAT TabSeparated",
                        query_id=id_for_retry + 0,
                    )
                    b58_encoded_string = r.output

                with When("I run base64 encode function"):
                    r = node.query(
                        f"SELECT base64Encode('{string_of_all_askii_symbols()*1000}') FORMAT TabSeparated",
                        query_id=id_for_retry + 1,
                    )
                    b64_encoded_string = r.output

                with When("I run base58 decode function"):
                    r = node.query(
                        f"SELECT base58Decode('{b58_encoded_string}') FORMAT TabSeparated",
                        query_id=id_for_retry + 2,
                    )
                    b58_decoded_string = r.output

                with When("I run base64 decode function"):
                    r = node.query(
                        f"SELECT base64Decode('{b64_encoded_string}') FORMAT TabSeparated",
                        query_id=id_for_retry + 3,
                    )
                    b64_decoded_string = r.output

                with Then("I check strings are not changed after encode, decode"):
                    assert (
                        b58_decoded_string == string_of_all_askii_symbols() * 1000
                    ), error()
                    assert (
                        b64_decoded_string == string_of_all_askii_symbols() * 1000
                    ), error()

                for attempt_1 in retries(timeout=100, delay=10):
                    with attempt_1:
                        with When("I remember memory usages"):
                            r = node.query(
                                f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '{id_for_retry + 0}' FORMAT TabSeparated"
                            )
                            b58_encode_memory_usage = int(r.output)
                            assert b58_encode_memory_usage > 0, error()

                            r = node.query(
                                f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '{id_for_retry + 1}' FORMAT TabSeparated"
                            )
                            b64_encode_memory_usage = int(r.output)
                            assert b64_encode_memory_usage > 0, error()

                            r = node.query(
                                f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '{id_for_retry + 2}' FORMAT TabSeparated"
                            )
                            b58_decode_memory_usage = int(r.output)
                            assert b58_decode_memory_usage > 0, error()

                            r = node.query(
                                f"SELECT max(memory_usage) FROM system.query_log WHERE query_id = '{id_for_retry + 3}' FORMAT TabSeparated"
                            )
                            b64_decode_memory_usage = int(r.output)
                            assert b64_decode_memory_usage > 0, error()

                with Then("I check memory usages are similar"):
                    debug(
                        f"b58_encode_memory_usage: {b58_encode_memory_usage},\n"
                        f"b64_encode_memory_usage: {b64_encode_memory_usage},\n"
                        f"b58_decode_memory_usage: {b58_decode_memory_usage},\n"
                        f"b64_decode_memory_usage: {b64_decode_memory_usage}"
                    )
                    assert (
                        b58_encode_memory_usage <= b64_encode_memory_usage * 2
                    ), error()
                    assert (
                        b58_decode_memory_usage <= b64_decode_memory_usage * 2
                    ), error()


@TestFeature
@Requirements(RQ_ClickHouse_Base58_MemoryUsage_Base58vsBase64("1.0"))
@Name("memory usage")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 and base64 functions has small difference in memory usage."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

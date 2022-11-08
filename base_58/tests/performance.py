from base_58.tests.steps import *


@TestScenario
@Requirements(RQ_ClickHouse_Base58_Performance_Base58vsBase64("1.0"))
def performance(self, node=None):
    """Check that clickhouse base58 functions have simular performance with base64 functions."""

    if node is None:
        node = self.context.node

    table_name_random = f"table_{getuid()}_random"
    table_name = f"table_{getuid()}"
    table_name_e64 = f"table_{getuid()}_e64"
    table_name_e58 = f"table_{getuid()}_e58"

    with When("I create a table with random engine"):
        create_partitioned_table(
            table_name=table_name_random,
            engine="GenerateRandom(1, 5, 3)",
            order="",
            partition="",
        )

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name, partition="")

    with When("I insert data into the MergeTree table"):
        node.query(
            f"insert into {table_name} select id, x from {table_name_random} limit 10000"
        )

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name_e64, partition="")

    with When("I insert data into the table with base64 encoding"):
        node.query(
            f"insert into {table_name_e64} select id, base64Encode(x) from {table_name};"
        )

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(table_name=table_name_e58, partition="")

    with When("I insert data into the table with base58 encoding"):
        node.query(
            f"insert into {table_name_e58} select id, base58Encode(x) from {table_name};"
        )

    with Then("I compare base58 select performance and base64 select performance"):
        execution_times_encode = []
        execution_times_decode = []
        start_time = time.time()
        node.query(
            f"select count(b64) from (select base64Encode(x) as b64 from {table_name})"
        )
        execution_times_encode.append(time.time() - start_time)
        start_time = time.time()
        node.query(
            f"select count(b58) from (select base58Encode(x) as b58 from {table_name})"
        )
        execution_times_encode.append(time.time() - start_time)
        start_time = time.time()
        node.query(
            f"select count(*) from (select base64Decode(x) from {table_name_e64})"
        )
        execution_times_decode.append(time.time() - start_time)
        start_time = time.time()
        node.query(
            f"select count(*) from (select base58Decode(x) from {table_name_e58})"
        )
        execution_times_decode.append(time.time() - start_time)

        assert 2 * min(execution_times_encode) > max(execution_times_encode), error()
        assert 2 * min(execution_times_decode) > max(execution_times_decode), error()


@TestFeature
@Name("performance")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 functions have simular performance with base64 functions."""

    self.context.node = self.context.cluster.node(node)
    for scenario in loads(current_module(), Scenario):
        scenario()

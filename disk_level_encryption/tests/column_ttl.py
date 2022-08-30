import time
from testflows.core import *
from testflows.asserts import error
from disk_level_encryption.tests.steps import *
from disk_level_encryption.requirements.requirements import *
from helpers.cluster import QueryRuntimeException


@TestStep(Given)
def create_table_column_ttl(self, node=None):
    """Create a MergeTree table that uses a given storage policy with column ttl."""

    table_name = getuid()
    policy = self.context.policy
    if node is None:
        node = self.context.node

    try:
        node.query(
            textwrap.dedent(
                f"""
        CREATE TABLE {table_name}
        (
                Date DateTime,
                a Int TTL Date + INTERVAL 1 HOUR,
                b Int TTL Date + INTERVAL 2 HOUR
        )
        ENGINE = MergeTree()
        ORDER BY Date
        SETTINGS storage_policy = '{policy}'
        """
            )
        )
        yield table_name

    finally:
        with Finally("I drop the table if exists"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
def column_ttl_move(self, node=None):
    """Check that ClickHouse supports Column TTL move when table is stored on the encrypted disk."""

    if node is None:
        node = self.context.node

    with Given("I add configuration file"):
        create_policy_with_local_encrypted_disk()

    with Given("I create table with column ttl"):
        table_name = create_table_column_ttl()

    with When("I insert data into the table"):
        now = time.time()
        wait_expire = 31 * 60
        date = now
        for i in range(6):
            values = f"(toDateTime({date-i*wait_expire}), {i+1}, {i+1})"
            insert_into_table(name=table_name, values=values)

    r = node.query(f"SELECT Date as Seconds, a, b FROM {table_name} FORMAT JSONEachRow")

    with Then("I compute expected output"):
        expected_output = (
            '{"Seconds":' + f"{int(date)}" + ',"a":1,"b":1}\n'
            '{"Seconds":' + f"{int(date-wait_expire)}" + ',"a":2,"b":2}\n'
            '{"Seconds":' + f"{int(date-2*wait_expire)}" + ',"a":0,"b":3}\n'
            '{"Seconds":' + f"{int(date-3*wait_expire)}" + ',"a":0,"b":4}\n'
            '{"Seconds":' + f"{int(date-4*wait_expire)}" + ',"a":0,"b":0}\n'
            '{"Seconds":' + f"{int(date-5*wait_expire)}" + ',"a":0,"b":0}'
        )

    with Then("I expect data is successfully inserted"):
        for attempt in retries(timeout=30, delay=5):
            with attempt:
                r = node.query(f"OPTIMIZE TABLE {table_name} FINAL", steps=False)
                r = node.query(
                    f"SELECT toInt32(Date) as Seconds, a, b FROM {table_name} ORDER BY Date DESC FORMAT JSONEachRow",
                    steps=False,
                )
                assert r.output == expected_output, error()

        r = node.query(
            f"SELECT count() FROM system.parts WHERE table = '{table_name}' AND active FORMAT JSONEachRow"
        )
        assert r.output == '{"count()":"1"}', error()

        with And("I check data is not lost after merge"):
            r = node.query(
                f"SELECT toInt32(Date) as Seconds, a, b FROM {table_name} ORDER BY Date DESC FORMAT JSONEachRow"
            )
            assert r.output == expected_output, error()

    with Then("I restart server"):
        node.restart()

    with Then("I expect data is not changed after restart"):
        r = node.query(
            f"SELECT toInt32(Date) as Seconds, a, b FROM {table_name} ORDER BY Date DESC FORMAT JSONEachRow"
        )
        assert r.output == expected_output, error()


@TestScenario
def column_ttl_delete(self, node=None):
    """Check that ClickHouse supports Column TTL move when table is stored on the encrypted disk."""

    if node is None:
        node = self.context.node

    with Given("I add configuration file"):
        create_policy_with_local_encrypted_disk()

    with Given("I create table with column ttl"):
        table_name = create_table_column_ttl()

    with When("I insert data into the table"):
        now = time.time()
        wait_expire = 31 * 60
        date = now
        for i in range(2, 6):
            values = f"(toDateTime({date-i*wait_expire}), {i+1}, {i+1})"
            insert_into_table(name=table_name, values=values)

    r = node.query(f"SELECT Date as Seconds, a, b FROM {table_name} FORMAT JSONEachRow")

    with Then("I compute expected output"):
        expected_output = (
            '{"Seconds":' + f"{int(date-2*wait_expire)}" + ',"a":0,"b":3}\n'
            '{"Seconds":' + f"{int(date-3*wait_expire)}" + ',"a":0,"b":4}\n'
            '{"Seconds":' + f"{int(date-4*wait_expire)}" + ',"a":0,"b":0}\n'
            '{"Seconds":' + f"{int(date-5*wait_expire)}" + ',"a":0,"b":0}'
        )

    with Then("I expect data is successfully inserted"):
        for attempt in retries(timeout=30, delay=5):
            with attempt:
                r = node.query(f"OPTIMIZE TABLE {table_name} FINAL", steps=False)
                r = node.query(
                    f"SELECT toInt32(Date) as Seconds, a, b FROM {table_name} ORDER BY Date DESC FORMAT JSONEachRow",
                    steps=False,
                )
                assert r.output == expected_output, error()

        r = node.query(
            f"SELECT count() FROM system.parts WHERE table = '{table_name}' AND active FORMAT JSONEachRow"
        )
        assert r.output == '{"count()":"1"}', error()

        with And("I check data is not lost after merge"):
            r = node.query(
                f"SELECT toInt32(Date) as Seconds, a, b FROM {table_name} ORDER BY Date DESC FORMAT JSONEachRow"
            )
            assert r.output == expected_output, error()

    with Then("I restart server"):
        node.restart()

    with Then("I expect data is not changed after restart"):
        r = node.query(
            f"SELECT toInt32(Date) as Seconds, a, b FROM {table_name} ORDER BY Date DESC FORMAT JSONEachRow"
        )
        assert r.output == expected_output, error()


@TestFeature
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_ColumnTTL("1.0"))
@Name("column ttl")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse supports Column TTL when table is stored on the encrypted disk."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

import time

from testflows.asserts import values as That
from testflows.core.name import basename
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from testflows.asserts import snapshot, error
from helpers.cluster import QueryRuntimeException


@TestScenario
def check_only_compact_format(self, policy=None, disk_path=None, node=None):
    """Check that ClickHouse supports disk level encryption for tables when
    all parts stored in compact format.
    """

    node = self.context.node if node is None else node
    disk_path = "/disk_local"

    with Given("I have policy that uses local encrypted disk"):
        create_policy_with_local_encrypted_disk(
            key_parameter_name="key", key_value="firstfirstfirstf"
        )

    policy = self.context.policy if policy is None else policy

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, min_bytes_for_wide_part=1000000000)

    with And("I stop all merges"):
        node.query(f"SYSTEM STOP MERGES {table_name}")

    with When("I insert data into the table"):
        values = (
            "("
            + "), (".join([str(i) + f",'insert_number {i}'" for i in range(100)])
            + ")"
        )
        insert_into_table(name=table_name, values=values)
        insert_into_table(name=table_name, values=values)

    with Then("I expect data stored in compact format"):
        r = node.query(
            f"SELECT DISTINCT part_type FROM system.parts WHERE table = '{table_name}' and active"
        )
        assert r.output == "Compact", error()

    with Then("I expect data is successfully inserted"):
        r = node.query(
            f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
        )
        with That() as that:
            assert that(snapshot(r.output, name=basename(self.name))), error()

    with Then("I check all files have ENC header"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with Then("I restart server"):
        node.restart()

    with Then("I expect data is not changed after restart"):
        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            with That() as that:
                assert that(snapshot(r.output, name=basename(self.name))), error()


@TestScenario
def check_only_wide_format(self, policy=None, disk_path=None, node=None):
    """Check that ClickHouse supports disk level encryption for tables when
    all parts stored in wide format.
    """

    node = self.context.node if node is None else node
    disk_path = "/disk_local"

    with Given("I have policy that uses local encrypted disk"):
        create_policy_with_local_encrypted_disk(
            key_parameter_name="key", key_value="firstfirstfirstf"
        )

    policy = self.context.policy if policy is None else policy

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, min_bytes_for_wide_part=0)

    with And("I stop all merges"):
        node.query(f"SYSTEM STOP MERGES {table_name}")

    with When("I insert data into the table"):
        values = (
            "("
            + "), (".join([str(i) + f",'insert_number {i}'" for i in range(500)])
            + ")"
        )
        insert_into_table(name=table_name, values=values)
        insert_into_table(name=table_name, values=values)

    with Then("I expect data stored in wide format"):
        r = node.query(
            f"SELECT DISTINCT part_type FROM system.parts WHERE table = '{table_name}' and active"
        )
        assert r.output == "Wide", error()

    with Then("I expect data is successfully inserted"):
        r = node.query(
            f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
        )
        with That() as that:
            assert that(snapshot(r.output, name=basename(self.name))), error()

    with Then("I check all files have ENC header"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with Then("I restart server"):
        node.restart()

    with Then("I expect data is not changed after restart"):
        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            with That() as that:
                assert that(snapshot(r.output, name=basename(self.name))), error()


@TestScenario
def check_wide_and_compact_format(self, policy=None, disk_path=None, node=None):
    """Check that ClickHouse supports disk level encryption for tables when
    parts stored in wide and compact format.
    """

    node = self.context.node if node is None else node
    disk_path = "/disk_local"

    with Given("I have policy that uses local encrypted disk"):
        create_policy_with_local_encrypted_disk(
            key_parameter_name="key", key_value="firstfirstfirstf"
        )

    policy = self.context.policy if policy is None else policy

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy, min_bytes_for_wide_part=1000)

    with And("I stop all merges"):
        node.query(f"SYSTEM STOP MERGES {table_name}")
    try:
        with When("I insert data into the table"):
            values = (
                "("
                + "), (".join([str(i) + f",'insert_number {i}'" for i in range(20)])
                + ")"
            )
            insert_into_table(name=table_name, values=values)
            values = (
                "("
                + "), (".join([str(i) + f",'insert_number {i}'" for i in range(100)])
                + ")"
            )
            insert_into_table(name=table_name, values=values)

        with Then("I expect data stored in wide and compact format"):
            r = node.query(
                f"SELECT DISTINCT part_type FROM system.parts WHERE table = '{table_name}' and active ORDER BY part_type"
            )
            assert r.output == "Compact\nWide", error()

        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            with That() as that:
                assert that(snapshot(r.output, name=basename(self.name))), error()

        with Then("I check all files have ENC header"):
            check_if_all_files_are_encrypted(disk_path=disk_path)

        with Then("I restart server"):
            node.restart()

        with Then("I expect data is not changed after restart"):
            with Then("I expect data is successfully inserted"):
                r = node.query(
                    f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
                )
                with That() as that:
                    assert that(snapshot(r.output, name=basename(self.name))), error()
    finally:
        with Finally("I start merges"):
            node.query("SYSTEM START MERGES")

    with When("I merges parts"):
        r = node.query(f"OPTIMIZE TABLE {table_name} FINAL")
        r = node.query(
            f"SELECT count() FROM system.parts WHERE table = '{table_name}' AND active FORMAT JSONEachRow"
        )
        assert r.output == '{"count()":"1"}', error()

    with Then("I expect data is not changed after merge"):
        with Then("I expect data is successfully inserted"):
            r = node.query(
                f"SELECT * FROM {table_name} ORDER BY Id, Value FORMAT JSONEachRow"
            )
            with That() as that:
                assert that(snapshot(r.output, name=basename(self.name))), error()

    with Then("I expect all the data in wide format"):
        r = node.query(
            f"SELECT DISTINCT part_type FROM system.parts WHERE table = '{table_name}' and active ORDER BY part_type"
        )
        assert r.output == "Wide", error()


@TestFeature
@Name("wide and compact formats")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_WideAndCompactFormat("1.0"))
def feature(self, node="clickhouse1"):
    """Check that ClickHouse supports wide table parts and compact table parts when using encrypted disks."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()

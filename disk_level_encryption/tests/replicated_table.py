import time

from testflows.asserts import values as That
from testflows.core.name import basename
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from testflows.asserts import snapshot, error
from helpers.cluster import QueryRuntimeException

expected_output = '{"Id":1,"Value":"clickhouse1"}\n{"Id":2,"Value":"clickhouse1"}'


@TestOutline
def replicated_table(self, key_values, policies):
    """Check that ClickHouse supports replicated tables for encrypted disk."""

    table_name = getuid()

    with Given(
        "I create replicated table on cluster",
        description="""
        Using the following cluster configuration with 1 shard and 3 replicas in it:
            shard0: 
                replica0: clickhouse1
                replica1: clickhouse2
                replica2: clickhouse3
        """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            node = self.context.cluster.node(name)
            self.context.node = node
            if policies[i] == "local_encrypted":
                create_policy_with_local_encrypted_disk(key_value=key_values[i])
            with When(f"I create table on {name} node"):
                create_table(
                    node=node,
                    name=table_name,
                    policy=policies[i],
                    engine=f"ReplicatedMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}')",
                )

    with When(f"I insert into table on clickhouse1 node"):
        name = "clickhouse1"
        self.context.node = node = self.context.cluster.node(name)
        values = f"(1, '{name}'),(2, '{name}')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect i can select from replicated table on any node"):
        for name in self.context.cluster.nodes["clickhouse"]:
            node = self.context.cluster.node(name)
            self.context.node = node
            with When(f"I expect data is successfully inserted on {name} node"):
                for attempt in retries(timeout=30, delay=5):
                    with attempt:
                        r = node.query(
                            f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow"
                        )
                        assert r.output == expected_output, error()

    with Then("I expect i can select from replicated table on any node after restart"):
        for name in self.context.cluster.nodes["clickhouse"]:
            self.context.node = node = self.context.cluster.node(name)
            with When(f"I restart {name} node"):
                node.restart()
            with Then(
                f"I expect data is successfully inserted on {name} node after restart"
            ):
                for attempt in retries(timeout=30, delay=5):
                    with attempt:
                        r = node.query(
                            f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow"
                        )
                        assert r.output == expected_output, error()


@TestScenario
def replicated_table_three_different_keys(self):
    """Check that ClickHouse supports replicated tables for encrypted disk, three encrypted replicas tree different keys."""
    replicated_table(
        key_values=["firstfirstfirstf", "secondsecondseco", "thirdthirdthirdt"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
def replicated_table_one_key(self):
    """Check that ClickHouse supports replicated tables for encrypted disk, three encrypted replicas one key."""
    replicated_table(
        key_values=["firstfirstfirstf", "firstfirstfirstf", "firstfirstfirstf"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
def replicated_table_two_encrypted_replica_two_keys(self):
    """Check that ClickHouse supports replicated tables for encrypted disk, two encrypted replicas two different keys."""
    replicated_table(
        key_values=["firstfirstfirstf", "secondsecondseco", None],
        policies=["local_encrypted", "local_encrypted", "default"],
    )


@TestScenario
def replicated_table_one_encrypted_replica(self):
    """Check that ClickHouse supports replicated tables for encrypted disk, one encrypted replica
    insertion into encrypted replica.
    """
    replicated_table(
        key_values=["firstfirstfirstf", None, None],
        policies=["local_encrypted", "default", "default"],
    )


@TestScenario
def replicated_table_one_encrypted_replica_insert_into_unencrypted(self):
    """Check that ClickHouse supports replicated tables for encrypted disk, one encrypted replica
    insertion into unencrypted replica.
    """
    replicated_table(
        key_values=[None, "secondsecondseco", None],
        policies=["default", "local_encrypted", "default"],
    )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables("1.0"),
)
@Name("replicated table")
def feature(self):
    """Check that ClickHouse supports replicated tables for encrypted disk."""

    for scenario in loads(current_module(), Scenario):
        scenario()

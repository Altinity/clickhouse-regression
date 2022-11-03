import time

from testflows.asserts import values as That
from testflows.core.name import basename
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from testflows.asserts import snapshot, error

expected_output = '{"Id":1,"Value":"clickhouse1"}\n{"Id":2,"Value":"clickhouse1"}'


@TestOutline
def distributed_table_replicated(self, key_values, policies):
    """Check that ClickHouse supports distributed tables for encrypted disk
    when distributed table configuration contains 1 shard and 3 replicas.
    """
    table_name = getuid()

    with Given(
        "I create replicated table on cluster",
        description="""
        Using the following cluster configuration containing 1 shard with 3 replicas:
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
            else:
                create_policy_with_local_encrypted_disk()
            with When(f"I create table on {name} node"):
                create_table(
                    node=node,
                    name=table_name,
                    policy=policies[i],
                    engine=f"ReplicatedMergeTree('/clickhouse/tables/shard0/{table_name}', 'replica{i}')",
                )

    with When(f"I create distributed table that uses policy with encrypted local disk"):
        self.context.node = node = self.context.cluster.node("clickhouse1")
        create_table(
            node=node,
            name=table_name + "_distributed",
            cluster="replicated_cluster",
            without_order_by=True,
            engine=f"Distributed('replicated_cluster', default, {table_name}, rand(), 'local_encrypted')",
        )

    with When(f"I insert into table on clickhouse1 node"):
        name = "clickhouse1"
        self.context.node = node = self.context.cluster.node(name)
        with When(f"I insert into table on {name} node"):
            values = f"(1, '{name}'),(2, '{name}')"
            node.query(
                f"INSERT INTO {table_name}_distributed VALUES {values}",
                settings=[("insert_distributed_sync", "1")],
            )

    with Then("I expect i can select from distributed table on any node"):
        for name in self.context.cluster.nodes["clickhouse"]:
            node = self.context.cluster.node(name)
            self.context.node = node
            with Then(f"I expect data is successfully inserted on {name} node"):
                for attempt in retries(timeout=100, delay=1):
                    with attempt:
                        r = node.query(
                            f"SELECT * FROM {table_name}_distributed ORDER BY Id FORMAT JSONEachRow"
                        )
                        assert r.output == expected_output, error()


@TestOutline
def distributed_table_sharded(self, key_values, policies):
    """Check that ClickHouse supports distributed tables for encrypted disk
    when distributed table configuration contains 3 shards one replica in each.
    """
    table_name = getuid()

    with Given(
        "I create sharded table on cluster",
        description="""
        Using the following cluster configuration without replication and containing only 3 shards:
            shard0: clickhouse1
            shard1: clickhouse2
            shard2: clickhouse3
        """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            self.context.node = node = self.context.cluster.node(name)
            if policies[i] == "local_encrypted":
                create_policy_with_local_encrypted_disk(key_value=key_values[i])
            else:
                create_policy_with_local_encrypted_disk()
            with When(f"I create table on {name} node"):
                create_table(
                    node=node,
                    name=table_name,
                    policy=policies[i],
                    engine=f"ReplicatedMergeTree('/clickhouse/tables/shard{i}/{table_name}', 'replica1')",
                )

    with When(f"I create distributed table that uses policy with encrypted local disk"):
        self.context.node = node = self.context.cluster.node("clickhouse1")
        create_table(
            node=node,
            name=table_name + "_distributed",
            cluster="sharded_cluster",
            without_order_by=True,
            engine=f"Distributed('sharded_cluster', default, {table_name}, rand(), 'local_encrypted')",
        )

    with When(f"I insert into table on clickhouse1 node"):
        name = "clickhouse1"
        self.context.node = node = self.context.cluster.node(name)
        values = f"(1, '{name}'),(2, '{name}')"
        node.query(
            f"INSERT INTO {table_name}_distributed VALUES {values}",
            settings=[("insert_distributed_sync", "1")],
        )

    with Then("I expect i can select from distributed table on any node"):
        for name in self.context.cluster.nodes["clickhouse"]:
            self.context.node = node = self.context.cluster.node(name)
            with Then(f"I expect data is successfully inserted on {name} node"):
                for attempt in retries(timeout=100, delay=1):
                    with attempt:
                        r = node.query(
                            f"SELECT * FROM {table_name}_distributed ORDER BY Id FORMAT JSONEachRow"
                        )
                        assert r.output == expected_output, error()


@TestOutline
def distributed_table_sharded_and_replicated(self, key_values, policies):
    """Check that ClickHouse supports distributed tables for encrypted disk
    when distributed table configuration contains 2 shards two replicas in one
    replica in the other.
    """
    table_name = getuid()

    with Given(
        "I create sharded table on cluster",
        description="""
        Using the following cluster configuration without replication and containing only 3 shards:
            shard0:
                replica0: clickhouse1
                replica1: clickhouse2
            shard1:
                replica0: clickhouse3
        """,
    ):
        for i, name in enumerate(self.context.cluster.nodes["clickhouse"]):
            self.context.node = node = self.context.cluster.node(name)
            if policies[i] == "local_encrypted":
                create_policy_with_local_encrypted_disk(key_value=key_values[i])
            else:
                create_policy_with_local_encrypted_disk()
            with When(f"I create table on {name} node"):
                create_table(
                    node=node,
                    name=table_name,
                    policy=policies[i],
                    engine=f"ReplicatedMergeTree('/clickhouse/tables/shard{i//2}/{table_name}', 'replica{i % 2}')",
                )

    with When(f"I create distributed table that uses policy with encrypted local disk"):
        self.context.node = node = self.context.cluster.node("clickhouse1")
        create_table(
            node=node,
            name=table_name + "_distributed",
            cluster="sharded_cluster",
            without_order_by=True,
            engine=f"Distributed('mixed_cluster', default, {table_name}, rand(), 'local_encrypted')",
        )

    with When(f"I insert into table on clickhouse1 node"):
        name = "clickhouse1"
        self.context.node = node = self.context.cluster.node(name)
        values = f"(1, '{name}'),(2, '{name}')"
        node.query(
            f"INSERT INTO {table_name}_distributed VALUES {values}",
            settings=[("insert_distributed_sync", "1")],
        )

    with Then("I expect i can select from distributed table on any node"):
        for name in self.context.cluster.nodes["clickhouse"]:
            self.context.node = node = self.context.cluster.node(name)
            with Then(f"I expect data is successfully inserted on {name} node"):
                for attempt in retries(timeout=100, delay=1):
                    with attempt:
                        r = node.query(
                            f"SELECT * FROM {table_name}_distributed ORDER BY Id FORMAT JSONEachRow"
                        )
                        assert r.output == expected_output, error()


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables("1.0"))
def distributed_table_replicated_three_different_keys(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the replicated table with three encrypted replicas with different keys.
    """
    distributed_table_replicated(
        key_values=["firstfirstfirstf", "secondsecondseco", "thirdthirdthirdt"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables("1.0"))
def distributed_table_replicated_one_key(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the replicated table with three encrypted replicas with the same key.
    """
    distributed_table_replicated(
        key_values=["firstfirstfirstf", "firstfirstfirstf", "firstfirstfirstf"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables("1.0"))
def distributed_table_replicated_two_encrypted_replica_two_keys(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the replicated table with three replicas two encrypted one not
    with two different keys.
    """
    distributed_table_replicated(
        key_values=["firstfirstfirstf", "secondsecondseco", None],
        policies=["local_encrypted", "local_encrypted", "default"],
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables("1.0"))
def distributed_table_replicated_one_encrypted_replica(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the replicated table with three replicas one encrypted two not
    insertion into encrypted replica.
    """
    distributed_table_replicated(
        key_values=["firstfirstfirstf", None, None],
        policies=["local_encrypted", "default", "default"],
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_ReplicatedTables("1.0"))
def distributed_table_replicated_one_encrypted_replica_insert_into_unencrypted(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the replicated table with three replicas one encrypted two not
    insertion into unencrypted replica.
    """
    distributed_table_replicated(
        key_values=[None, "secondsecondseco", None],
        policies=["default", "local_encrypted", "default"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Sharded("1.0"),
)
def distributed_table_sharded_three_different_keys(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded table with three encrypted shards with different keys.
    """
    distributed_table_sharded(
        key_values=["firstfirstfirstf", "secondsecondseco", "thirdthirdthirdt"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Sharded("1.0"),
)
def distributed_table_sharded_one_key(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded table with three encrypted shards with the same key.
    """
    distributed_table_sharded(
        key_values=["firstfirstfirstf", "firstfirstfirstf", "firstfirstfirstf"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Sharded("1.0"),
)
def distributed_table_sharded_two_encrypted_replica_two_keys(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded table with three shards two encrypted one not
    with two different keys.
    """
    distributed_table_sharded(
        key_values=["firstfirstfirstf", "secondsecondseco", None],
        policies=["local_encrypted", "local_encrypted", "default"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Sharded("1.0"),
)
def distributed_table_sharded_one_encrypted_replica(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded table with three shards one encrypted two not
    insertion into encrypted shard.
    """
    distributed_table_sharded(
        key_values=["firstfirstfirstf", None, None],
        policies=["local_encrypted", "default", "default"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Sharded("1.0"),
)
def distributed_table_sharded_one_encrypted_replica_insert_into_unencrypted(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded table with three shards one encrypted two not
    insertion into unencrypted shard.
    """
    distributed_table_sharded(
        key_values=[None, "secondsecondseco", None],
        policies=["default", "local_encrypted", "default"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_ShardedAndReplicatedTables("1.0"),
)
def distributed_table_sharded_and_replicated_three_different_keys(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded and replicated table with two encrypted shards
    two replicas in one replica in the other with three different keys.
    """
    distributed_table_sharded_and_replicated(
        key_values=["firstfirstfirstf", "secondsecondseco", "thirdthirdthirdt"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_ShardedAndReplicatedTables("1.0"),
)
def distributed_table_sharded_and_replicated_one_key(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded and replicated table with two encrypted shards
    two replicas in one replica in the other with the same key.
    """
    distributed_table_sharded_and_replicated(
        key_values=["firstfirstfirstf", "firstfirstfirstf", "firstfirstfirstf"],
        policies=["local_encrypted", "local_encrypted", "local_encrypted"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_ShardedAndReplicatedTables("1.0"),
)
def distributed_table_sharded_and_replicated_two_encrypted_replica_two_keys(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded and replicated table with two shards
    two replicas in one replica in the other the first shard is encrypted
    with two keys.
    """
    distributed_table_sharded_and_replicated(
        key_values=["firstfirstfirstf", "secondsecondseco", None],
        policies=["local_encrypted", "local_encrypted", "default"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_ShardedAndReplicatedTables("1.0"),
)
def distributed_table_sharded_and_replicated_one_encrypted_replica(self):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded and replicated table with two shards
    two replicas in one replica in the other the first replica is encrypted
    insertion into encrypted replica.
    """
    distributed_table_sharded_and_replicated(
        key_values=["firstfirstfirstf", None, None],
        policies=["local_encrypted", "default", "default"],
    )


@TestScenario
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_ShardedAndReplicatedTables("1.0"),
)
def distributed_table_sharded_and_replicated_one_encrypted_replica_insert_into_unencrypted(
    self,
):
    """Check that ClickHouse supports distributed tables for encrypted disk,
    that refers to the sharded and replicated table with two shards
    two replicas in one replica in the other the first replica is encrypted
    insertion into encrypted replica into first shard.
    """
    distributed_table_sharded_and_replicated(
        key_values=[None, "secondsecondseco", None],
        policies=["default", "local_encrypted", "default"],
    )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_DistributedTables("1.0"),
)
@Name("distributed table")
def feature(self):
    """Check that ClickHouse supports distributed tables for encrypted disk."""
    for scenario in loads(current_module(), Scenario):
        scenario()

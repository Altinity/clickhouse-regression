from part_moves_between_shards.requirements import *
from part_moves_between_shards.tests.steps import *
from helpers.common import *


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_SourceReplicaStopped(
        "1.0"
    )
)
def source_replica_stopped(self, node=None):
    cluster = self.context.cluster
    if node is None:
        node = self.context.node
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name, cluster_name=cluster_name
            )

        with And("I move part from shard 1 to shard 3"):
            move_part_with_check(
                table_name=table_name,
                shard_b_number="3",
                shard_a_name="clickhouse1",
                part_name="'all_0_0_0'",
            )

        with And("I stop shard 1 replica"):
            cluster.node("clickhouse4").stop_clickhouse()

        with And("I move part from shard 3 to shard 1"):
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"ALTER TABLE {table_name} MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/01/{table_name}'"
            )

        with Then("I check part move doesn't finishing while replica down"):
            retry(node.query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="0"
            )
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="2"
            )

        with And("I start shard 1 replica"):
            cluster.node("clickhouse4").start_clickhouse()

        with And("I start merges"):
            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part move finished"):
            retry(node.query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="1"
            )

            for name in ["clickhouse3", "clickhouse4"]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="1"
                )
    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DestinationReplicaStopped(
        "1.0"
    )
)
def destination_replica_stopped(self):
    """Check one part moves between two shards correct when destination replica stopped."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name, cluster_name=cluster_name
            )

        with And("I stop shard 1 replica"):
            cluster.node("clickhouse4").stop_clickhouse()

        with And("I move part from shard 1 to shard 3"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/03/{table_name}'"
            )

        with Then("I check part move doesn't finishing while replica down"):
            retry(node.query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="1"
            )
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="1"
            )

        with And("I start shard 1 replica"):
            cluster.node("clickhouse4").start_clickhouse()

        with And("I start merges"):
            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check part move finished"):
            retry(node.query, timeout=100, delay=1)(
                f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="0"
            )

            for name in ["clickhouse3", "clickhouse4"]:
                retry(cluster.node(name).query, timeout=100, delay=1)(
                    f"SELECT count() FROM {table_name} FORMAT TabSeparated", message="2"
                )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DistributedTable(
        "1.0"
    )
)
def distributed_table(self):
    """Check data in distributed table doesn't deduplicate when
    `MOVE PART TO SHARD` query is used multiple times.
    """
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"
            table_name_d = f"test_table_d{uid}"

        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name, cluster_name=cluster_name
            )
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (3)"
            )

        with And("I create distributed table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name_d} as {table_name} "
                f"ENGINE = Distributed"
                f"({cluster_name}, currentDatabase(), {table_name})",
                steps=False,
            )

        with And("I move same part between shards and check data in distributed table"):
            part_uuid = (
                self.context.cluster.node("clickhouse1")
                .query(
                    f"SELECT uuid FROM system.parts where name = 'all_0_0_0' FORMAT TabSeparated"
                )
                .output.strip()
            )
            for i in range(10):
                part = ""
                for retr in retries(timeout=30):
                    with retr:
                        part = (
                            self.context.cluster.node("clickhouse1")
                            .query(
                                f"SELECT name FROM system.parts where uuid = '{part_uuid}' FORMAT TabSeparated"
                            )
                            .output.strip()
                        )

                        assert (
                            part != ""
                        ), f"No part with uuid {part_uuid} in system.parts table"
                with Given(f"LOOP STEP {i}"):
                    When(
                        "I move part from shard 1 to shard 3 and return it",
                        test=move_part_and_return,
                        parallel=True,
                    )(
                        table_name=table_name,
                        part=part,
                        part_uuid=part_uuid,
                        shard1="01",
                        shard2="03",
                        node_name1="clickhouse1",
                        node_name2="clickhouse3",
                    )
                    When(
                        "I make concurrent check of data in distributed table",
                        test=select_all_from_table,
                        parallel=True,
                    )(table_name=table_name_d)
                    When(
                        "I make concurrent check number of rows in distributed table",
                        test=select_count_from_table,
                        parallel=True,
                    )(table_name=table_name_d, message="3")
                    join()

        with And("I start merges"):
            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

    finally:
        with Finally("I drop tables if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )
            node.query(
                f"DROP TABLE IF EXISTS {table_name_d} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication_DistributedTable_ReplicaStopped(
        "1.0"
    )
)
def distributed_table_stopped_replica(self):
    """Check data in distributed table doesn't deduplicate when `MOVE PART TO SHARD` query is used multiple times
    and some replica stops and starts.
    """
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")
    cluster_name = "'cluster_1replica_3shard'"
    try:
        with Given("Receive UID"):
            uid = getuid()
            table_name = f"test_table{uid}"
            table_name_d = f"test_table_d{uid}"
        with And("I create table with simple data"):
            create_test_table_with_insert(
                table_name=table_name, cluster_name=cluster_name
            )
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"INSERT INTO {table_name} VALUES (3)"
            )

        with And("I create distributed table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name_d} as {table_name} "
                f"ENGINE = Distributed"
                f"({cluster_name}, currentDatabase(), {table_name})",
                steps=False,
            )

        with And("I move same part between shards and check data in distributed table"):
            part_uuid = (
                self.context.cluster.node("clickhouse1")
                .query(
                    f"SELECT uuid FROM system.parts where name = 'all_0_0_0' FORMAT TabSeparated"
                )
                .output.strip()
            )
            for i in range(5):
                part = ""
                for retr in retries(timeout=30):
                    with retr:
                        part = (
                            self.context.cluster.node("clickhouse1")
                            .query(
                                f"SELECT name FROM system.parts where uuid = '{part_uuid}' FORMAT TabSeparated"
                            )
                            .output.strip()
                        )

                        assert (
                            part != ""
                        ), f"No part with uuid {part_uuid} in system.parts table"
                with Given(f"LOOP STEP {i}"):
                    When(
                        "I move part from shard 1 to shard 3 and return it",
                        test=move_part_and_return_stopped_replica,
                        parallel=True,
                    )(
                        table_name=table_name,
                        part=part,
                        part_uuid=part_uuid,
                        shard1="01",
                        shard2="03",
                        node_name1="clickhouse1",
                        node_name2="clickhouse3",
                    )
                    # When("I make concurrent check number of rows in distributed table", test=select_count_from_table,
                    #      parallel=True)(table_name=table_name_d, message="3")
                    When(
                        "I make concurrent check of data in distributed table",
                        test=select_all_from_table,
                        parallel=True,
                    )(table_name=table_name_d)
                    join()

        with And("I start merges"):
            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

    finally:
        with Finally("I drop tables if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )
            node.query(
                f"DROP TABLE IF EXISTS {table_name_d} ON CLUSTER {cluster_name} SYNC"
            )


@TestFeature
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_DataDeduplication("1.0"))
@Name("deduplication")
def feature(self):
    """Check part moves between shards on deduplicate data cases."""

    with Given("I create remote config"):
        entries = {
            "cluster_1replica_3shard": [
                {"shard": [{"replica": {"host": "clickhouse1", "port": "9000"}}]},
                {"shard": [{"replica": {"host": "clickhouse2", "port": "9000"}}]},
                {
                    "shard": [
                        {"replica": {"host": "clickhouse3", "port": "9000"}},
                        {"replica": {"host": "clickhouse4", "port": "9000"}},
                    ]
                },
            ]
        }
        create_remote_configuration(entries=entries)

    for scenario in loads(current_module(), Scenario):
        scenario()

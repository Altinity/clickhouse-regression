from part_moves_between_shards.requirements import *
from part_moves_between_shards.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable("1.0"))
def system_table_check(self):
    """Check system table part_moves_between_shards receives information about `MOVE PART` query."""
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

        with And("I move part from shard 1 to shard 3"):
            node.query(
                f"ALTER TABLE {table_name} MOVE PART 'all_0_0_0' TO SHARD '/clickhouse/tables/"
                f"replicated/03/{table_name}'"
            )

            node.query(f"SYSTEM START MERGES {table_name}")
            node.query(f"OPTIMIZE TABLE {table_name} FINAL")

        with Then("I check system table part_moves_between_shards was created"):
            retry(cluster.node("clickhouse1").query, timeout=100, delay=1)(
                "select count() from "
                "system.part_moves_between_shards "
                f"where table ilike '{table_name}' FORMAT TabSeparated",
                message="1",
            )

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable_SyncFailSource("1.0")
)
def system_table_source_replica_stopped(self):
    """Check one part moves between two shards correct when one source replica stopped."""
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

        with Then("I check information in 'state' and 'last_exception' columns"):
            retry(cluster.node("clickhouse3").query, timeout=100, delay=1)(
                "SELECT state FROM system.part_moves_between_shards "
                f"WHERE table = '{table_name}' FORMAT TabSeparated",
                message="SYNC_SOURCE",
            )

            # retry(cluster.node("clickhouse3").query, timeout=100, delay=1)("SELECT last_exception FROM "
            #                                                                "system.part_moves_between_shards "
            #                                                                f"WHERE table = '{table_name}'",
            #                                                                message="DB::Exception: Some replicas"
            #                                                                        " haven\\'t processed event:"
            #                                                                        " [\\'clickhouse4\\'], will retry"
            #                                                                        " later.")
        with And("I start shard 1 replica"):
            cluster.node("clickhouse4").start_clickhouse()

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestScenario
@Requirements(
    RQ_SRS_027_ClickHouse_PartMovesBetweenShards_SystemTable_SyncFailDestination("1.0")
)
def system_table_destination_replica_stopped(self):
    """Check one part moves between two shards correct when one destination replica stopped."""
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

        with Then("I check information in 'state' and 'last_exception' columns"):
            retry(node.query, timeout=100, delay=1)(
                "SELECT state FROM system.part_moves_between_shards "
                f"WHERE table = '{table_name}' FORMAT TabSeparated",
                message="SYNC_DESTINATION",
            )

            # retry(node.query, timeout=100, delay=1)("SELECT last_exception FROM "
            #                                                                "system.part_moves_between_shards "
            #                                                                f"WHERE table = '{table_name}'",
            #                                                                message="DB::Exception: Some replicas"
            #                                                                        " haven\\'t processed event:"
            #                                                                        " [\\'clickhouse4\\'], will retry"
            #                                                                        " later.")
        with And("I start shard 1 replica"):
            cluster.node("clickhouse4").start_clickhouse()

    finally:
        with Finally("I drop table if exists"):
            node.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
            )


@TestFeature
@Name("system_table")
def feature(self):
    """Check part moves between shards system table."""

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

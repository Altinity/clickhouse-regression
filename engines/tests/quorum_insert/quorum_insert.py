import sys
import time
from testflows.core import *
from testflows.asserts import error

append_path(sys.path, "../..")

from helpers.common import getuid
from engines.tests.steps import *

# Note: The original test suite included test_insert_quorum_with_keeper_loss_connection
# which uses kazoo client and PartitionManager. This test is not included here as
# those dependencies are not available in the testflows setup. If needed, it can be
# added later using alternative methods to simulate zookeeper connection loss.


@TestScenario
def simple_add_replica(self):
    """Test adding a replica to a ReplicatedMergeTree table with quorum inserts."""
    table_name = f"test_simple_{getuid()}"

    zero = self.context.cluster.node("clickhouse1")
    first = self.context.cluster.node("clickhouse2")
    second = self.context.cluster.node("clickhouse3")

    create_query = (
        f"CREATE TABLE {table_name} "
        "(a Int8, d Date) "
        f"Engine = ReplicatedMergeTree('/clickhouse/tables/{{shard}}/{table_name}', '{{replica}}') "
        "PARTITION BY d ORDER BY a"
    )

    try:
        with Given("I create the table on zero and first replicas"):
            zero.query(create_query)
            first.query(create_query)

        with When("I stop fetches on first replica"):
            first.query(f"SYSTEM STOP FETCHES {table_name}")

        with And("I insert data into zero replica"):
            zero.query(
                f"INSERT INTO {table_name} VALUES (1, '2011-01-01')",
                settings=[("insert_quorum", 1)],
            )

        with Then("I check data is only on zero replica"):
            zero.query(f"SELECT * from {table_name}", message="1\t2011-01-01\n")
            first.query(f"SELECT * from {table_name}", message="")

        with When("I start fetches and sync first replica"):
            first.query(f"SYSTEM START FETCHES {table_name}")
            first.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)

        with Then("I check data is on both replicas"):
            zero.query(f"SELECT * from {table_name}", message="1\t2011-01-01\n")
            first.query(f"SELECT * from {table_name}", message="1\t2011-01-01\n")

        with When("I add second replica and sync"):
            second.query(create_query)
            second.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)

        with Then("I check data is on all three replicas"):
            zero.query(f"SELECT * from {table_name}", message="1\t2011-01-01\n")
            first.query(f"SELECT * from {table_name}", message="1\t2011-01-01\n")
            second.query(f"SELECT * from {table_name}", message="1\t2011-01-01\n")

    finally:
        with Finally("I drop the table"):
            zero.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER replicated_cluster"
            )


@TestScenario
def drop_replica_and_achieve_quorum(self):
    """Test that quorum is achieved after dropping and re-adding a replica."""
    table_name = f"test_drop_replica_and_achieve_quorum_{getuid()}"

    zero = self.context.cluster.node("clickhouse1")
    first = self.context.cluster.node("clickhouse2")
    second = self.context.cluster.node("clickhouse3")

    create_query = (
        f"CREATE TABLE {table_name} "
        "(a Int8, d Date) "
        f"Engine = ReplicatedMergeTree('/clickhouse/tables/{{shard}}/{table_name}', '{{replica}}') "
        "PARTITION BY d ORDER BY a"
    )

    try:
        with Given("I create Replicated table with two replicas"):
            zero.query(create_query)
            first.query(create_query)

        with When("I stop fetches on one replica to isolate it"):
            first.query(f"SYSTEM STOP FETCHES {table_name}")

        with And("I try to insert with quorum which should fail"):
            r = zero.query(
                f"INSERT INTO {table_name}(a,d) VALUES (1, '2011-01-01')",
                settings=[("insert_quorum_timeout", 5000)],
                no_checks=True,
            )
            assert "Timeout while waiting for quorum" in r.output, error()

        with Then(
            "I check data exists on zero but not visible with sequential consistency"
        ):
            zero.query(
                f"SELECT * FROM {table_name}",
                message="1\t2011-01-01\n",
                settings=[("select_sequential_consistency", 0)],
            )
            zero.query(
                f"SELECT * FROM {table_name}",
                message="",
                settings=[("select_sequential_consistency", 1)],
            )

        with When("I start fetches and sync first replica"):
            first.query(f"SYSTEM START FETCHES {table_name}")
            first.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)

        with And("I add second replica and sync"):
            second.query(create_query)
            second.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)

        with Then("I check quorum for previous insert is achieved"):
            second.query(
                f"SELECT * FROM {table_name}",
                message="1\t2011-01-01\n",
                settings=[("select_sequential_consistency", 1)],
            )

    finally:
        with Finally("I drop the table"):
            zero.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER replicated_cluster"
            )


@TestScenario
@Examples(
    "add_new_data",
    [
        (False,),
        (True,),
    ],
)
def insert_quorum_with_drop_partition(self, add_new_data):
    """Test insert quorum with drop partition."""
    table_name = (
        f"test_quorum_insert_with_drop_partition"
        + ("_new_data" if add_new_data else "")
        + f"_{getuid()}"
    )

    zero = self.context.cluster.node("clickhouse1")
    first = self.context.cluster.node("clickhouse2")
    second = self.context.cluster.node("clickhouse3")

    create_query = (
        f"CREATE TABLE {table_name} ON CLUSTER replicated_cluster "
        "(a Int8, d Date) "
        "Engine = ReplicatedMergeTree "
        "PARTITION BY d ORDER BY a "
    )

    try:
        with Given("I create Replicated table with three replicas"):
            zero.query(create_query)

        with When("I stop fetches for table at first replica"):
            first.query(f"SYSTEM STOP FETCHES {table_name}")

        with And("I insert with quorum (zero and second)"):
            zero.query(f"INSERT INTO {table_name}(a,d) VALUES(1, '2011-01-01')")

        with And("I drop partition"):
            zero.query(f"ALTER TABLE {table_name} DROP PARTITION '2011-01-01'")

        if add_new_data:
            with And("I insert to deleted partition"):
                zero.query(f"INSERT INTO {table_name}(a,d) VALUES(2, '2011-01-01')")

        with When("I resume fetches for table at first replica"):
            first.query(f"SYSTEM START FETCHES {table_name}")

        with And("I sync first replica with others"):
            first.query(f"SYSTEM SYNC REPLICA {table_name}")

        with Then("I check quorum entry is cleaned up"):
            result = first.query(
                f"""
                WITH (SELECT toString(uuid) FROM system.tables WHERE name = '{table_name}') AS uuid,
                     '/clickhouse/tables/' || uuid || '/0/quorum/last_part' AS p
                SELECT * FROM system.zookeeper WHERE path = p FORMAT Vertical
                """
            )
            assert "20110101" not in result, error()

        with And("I sync second replica"):
            second.query(f"SYSTEM SYNC REPLICA {table_name}")

        with Then("I check data in updated partition"):
            if add_new_data:
                zero.query(f"SELECT * FROM {table_name}", message="2\t2011-01-01\n")
                second.query(f"SELECT * FROM {table_name}", message="2\t2011-01-01\n")
            else:
                zero.query(f"SELECT * FROM {table_name}", message="")
                second.query(f"SELECT * FROM {table_name}", message="")

    finally:
        with Finally("I drop the table"):
            zero.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER replicated_cluster"
            )


@TestScenario
@Examples(
    "add_new_data",
    [
        (False,),
        (True,),
    ],
)
def insert_quorum_with_move_partition(self, add_new_data):
    """Test insert quorum with move partition."""
    source_table_name = (
        f"test_insert_quorum_with_move_partition_source"
        + ("_new_data" if add_new_data else "")
        + f"_{getuid()}"
    )
    destination_table_name = (
        f"test_insert_quorum_with_move_partition_destination"
        + ("_new_data" if add_new_data else "")
        + f"_{getuid()}"
    )

    zero = self.context.cluster.node("clickhouse1")
    first = self.context.cluster.node("clickhouse2")
    second = self.context.cluster.node("clickhouse3")

    create_source = (
        f"CREATE TABLE {source_table_name} ON CLUSTER replicated_cluster "
        "(a Int8, d Date) "
        "Engine = ReplicatedMergeTree "
        "PARTITION BY d ORDER BY a "
    )

    create_destination = (
        f"CREATE TABLE {destination_table_name} ON CLUSTER replicated_cluster "
        "(a Int8, d Date) "
        "Engine = ReplicatedMergeTree "
        "PARTITION BY d ORDER BY a "
    )

    try:
        with Given(
            "I create source and destination Replicated tables with three replicas"
        ):
            zero.query(create_source)
            zero.query(create_destination)

        with When("I stop fetches for source table at first replica"):
            first.query(f"SYSTEM STOP FETCHES {source_table_name}")

        with And("I insert with quorum (zero and second)"):
            zero.query(f"INSERT INTO {source_table_name}(a,d) VALUES(1, '2011-01-01')")

        with And("I move partition"):
            zero.query(
                f"ALTER TABLE {source_table_name} MOVE PARTITION '2011-01-01' TO TABLE {destination_table_name}"
            )

        if add_new_data:
            with And("I insert to deleted partition"):
                zero.query(
                    f"INSERT INTO {source_table_name}(a,d) VALUES(2, '2011-01-01')"
                )

        with When("I resume fetches for source table at first replica"):
            first.query(f"SYSTEM START FETCHES {source_table_name}")

        with And("I sync first replica with others"):
            first.query(f"SYSTEM SYNC REPLICA {source_table_name}")

        with Then("I check quorum entry is cleaned up"):
            result = first.query(
                f"""
                WITH (SELECT toString(uuid) FROM system.tables WHERE name = '{source_table_name}') AS uuid,
                     '/clickhouse/tables/' || uuid || '/0/quorum/last_part' AS p
                SELECT * FROM system.zookeeper WHERE path = p FORMAT Vertical
                """
            )
            assert "20110101" not in result, error()

        with And("I sync second replica"):
            second.query(f"SYSTEM SYNC REPLICA {source_table_name}")

        with Then("I check data in updated partition"):
            if add_new_data:
                zero.query(
                    f"SELECT * FROM {source_table_name}", message="2\t2011-01-01\n"
                )
                second.query(
                    f"SELECT * FROM {source_table_name}", message="2\t2011-01-01\n"
                )
            else:
                zero.query(f"SELECT * FROM {source_table_name}", message="")
                second.query(f"SELECT * FROM {source_table_name}", message="")

    finally:
        with Finally("I drop the tables"):
            zero.query(
                f"DROP TABLE IF EXISTS {source_table_name} ON CLUSTER replicated_cluster"
            )
            zero.query(
                f"DROP TABLE IF EXISTS {destination_table_name} ON CLUSTER replicated_cluster"
            )


@TestScenario
def insert_quorum_with_ttl(self):
    """Test insert quorum with TTL."""
    table_name = f"test_insert_quorum_with_ttl_{getuid()}"

    zero = self.context.cluster.node("clickhouse1")
    first = self.context.cluster.node("clickhouse2")

    create_query = (
        f"CREATE TABLE {table_name} "
        "(a Int8, d Date) "
        "Engine = ReplicatedMergeTree('/clickhouse/tables/{{shard}}/{table_name}', '{{replica}}') "
        "PARTITION BY d ORDER BY a "
        "TTL d + INTERVAL 5 second DELETE WHERE toYear(d) = 2011 "
        "SETTINGS merge_with_ttl_timeout=2 "
    )

    try:
        with Given("I create Replicated table with two replicas"):
            zero.query(create_query)
            first.query(create_query)

        with When("I stop fetches for table at first replica"):
            first.query(f"SYSTEM STOP FETCHES {table_name}")

        with And("I try to insert which should fail since it can not reach the quorum"):
            r = zero.query(
                f"INSERT INTO {table_name}(a,d) VALUES(1, '2011-01-01')",
                settings=[("insert_quorum_timeout", 5000)],
                no_checks=True,
            )
            assert "Timeout while waiting for quorum" in r.output, error()

        with And("I wait 10 seconds for TTL merge to execute"):
            time.sleep(10)

        with Then("I check data still exists (TTL won't delete data without quorum)"):
            zero.query(
                f"SELECT * FROM {table_name}",
                message="1\t2011-01-01\n",
                settings=[("select_sequential_consistency", 0)],
            )

        with When("I resume fetches for table at first replica"):
            first.query(f"SYSTEM START FETCHES {table_name}")

        with And("I sync first replica"):
            first.query(f"SYSTEM SYNC REPLICA {table_name}")

        with And("I insert again with quorum"):
            zero.query(
                f"INSERT INTO {table_name}(a,d) VALUES(1, '2011-01-01')",
                settings=[("insert_quorum_timeout", 5000)],
            )

        with And("I insert data for 2012"):
            zero.query(f"INSERT INTO {table_name}(a, d) VALUES(2, '2012-02-02')")

        with And("I optimize and sync replicas"):
            first.query(f"OPTIMIZE TABLE {table_name}")
            first.query(f"SYSTEM SYNC REPLICA {table_name}")
            zero.query(f"SYSTEM SYNC REPLICA {table_name}")

        with Then("I check only 2012 data is visible"):
            first.query(
                f"SELECT * FROM {table_name}",
                message="2\t2012-02-02\n",
                settings=[("select_sequential_consistency", 0)],
            )
            first.query(
                f"SELECT * FROM {table_name}",
                message="2\t2012-02-02\n",
                settings=[("select_sequential_consistency", 1)],
            )

    finally:
        with Finally("I drop the table"):
            zero.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER replicated_cluster"
            )


@TestScenario
def ttl_delete_keeps_sequential_reads_consistent(self):
    """Test that TTL delete keeps sequential reads consistent."""
    table_name = f"test_ttl_delete_quorum_cleanup_{getuid()}"

    zero = self.context.cluster.node("clickhouse1")
    first = self.context.cluster.node("clickhouse2")

    create_query = (
        f"CREATE TABLE {table_name} "
        "(id UInt64, ts DateTime) "
        "Engine = ReplicatedMergeTree('/clickhouse/tables/{{shard}}/{table_name}', '{{replica}}') "
        "PARTITION BY toYYYYMM(ts) ORDER BY id "
        "TTL ts + INTERVAL 1 SECOND DELETE "
        "SETTINGS merge_with_ttl_timeout=0"
    )

    try:
        with Given("I create Replicated table with two replicas"):
            zero.query(create_query)
            first.query(create_query)

        with When("I insert data with quorum"):
            zero.query(
                f"INSERT INTO {table_name} VALUES (1, toDateTime('2000-01-01 00:00:00'))",
                settings=[
                    ("insert_quorum", 2),
                    ("insert_quorum_timeout", 15000),
                ],
            )

        with And("I sync replicas"):
            zero.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)
            first.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)

        with And("I materialize TTL"):
            zero.query(
                f"ALTER TABLE {table_name} MATERIALIZE TTL",
                settings=[("mutations_sync", 2)],
            )

        with And("I sync replicas again"):
            zero.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)
            first.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=20)

        with Then("I check count is 0 with sequential consistency"):
            for attempt in retries(timeout=20, delay=0.5):
                with attempt:
                    zero.query(
                        f"SELECT count() FROM {table_name}",
                        message="0",
                        settings=[("select_sequential_consistency", 1)],
                    )
                    first.query(
                        f"SELECT count() FROM {table_name}",
                        message="0",
                        settings=[("select_sequential_consistency", 1)],
                    )

    finally:
        with Finally("I drop the table"):
            zero.query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER replicated_cluster"
            )


@TestModule
@Name("quorum_insert")
def feature(self):
    """Check ReplicatedMergeTree quorum insert functionality."""
    self.context.cluster_name = "replicated_cluster"
    self.context.nodes = [
        self.context.cluster.node(name)
        for name in self.context.cluster.nodes["clickhouse"]
    ]

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()

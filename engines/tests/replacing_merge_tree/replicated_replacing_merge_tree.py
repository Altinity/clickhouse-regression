import sys

from testflows.core import *
from engines.requirements import *
from engines.tests.steps import *
from helpers.common import check_clickhouse_version


append_path(sys.path, "..")


@TestScenario
def without_is_deleted(self):
    """Checking that the new ReplicateReplacingMergeTree engine on 2 shard cluster with one shard on 2 replicas
     without is_deleted parameter and without clean_deleted_rows
    setting works in the same way as the old ReplacingMergeTree engine, and that it does not conceal rows with
    is_deleted=1."""

    node1 = self.context.cluster.node("clickhouse1")

    name = f"without_is_deleted_{getuid()}"

    cluster_name = "sharded_replicated_cluster"

    try:
        with Given("I create table without is_deleted column"):
            node1.query("SHOW clusters;")
            node1.query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                f"/tables/{name}/',"
                " '{replica}', version) ORDER BY id"
            )

        with When("I insert data in this table"):
            node1.query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            for node in self.context.cluster.nodes["clickhouse"][:3]:
                self.context.cluster.node(node).query(
                    f"SELECT count(*) FROM {name};", message="3"
                )
    finally:
        with Finally("I drop table"):
            node1.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}")


@TestScenario
def without_is_deleted_distributed(self):
    """Checking that the new ReplicateReplacingMergeTree engine on 2 shard cluster with one shard on 2 replicas
     without and distributed table on it is_deleted parameter and without clean_deleted_rows
    setting works in the same way as the old ReplacingMergeTree engine, and that it does not conceal rows with
    is_deleted=1."""

    node1 = self.context.cluster.node("clickhouse1")

    name = f"without_is_deleted_{getuid()}"

    cluster_name = "sharded_replicated_cluster"

    try:
        with Given("I create table with is_deleted column"):
            node1.query("SHOW clusters;", message="sharded_replicated_cluster")
            node1.query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                f"/tables/{name}/',"
                " '{replica}', version) ORDER BY id"
            )

        with When("I insert data in this table"):
            node1.query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with And("I create distributed table"):
            node1.query(
                f"CREATE TABLE IF NOT EXISTS distr_{name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = Distributed('{cluster_name}','default','{name}')"
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            node1.query(
                f"SELECT * FROM distr_{name} FINAL FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}\n'
                '{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}',
                settings=[("final", 1)],
            )

    finally:
        with Finally("I drop table"):
            node1.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}")
            node1.query(f"DROP TABLE IF EXISTS distr_{name} ON CLUSTER {cluster_name}")


@TestScenario
def with_is_deleted(self):
    """Checking that the new ReplicateReplacingMergeTree engine on 2 shard cluster with one shard on 2 replicas
     with is_deleted parameter and without clean_deleted_rows
    setting works in the same way as the old ReplacingMergeTree engine, and that it does not conceal rows with
    is_deleted=1."""

    node1 = self.context.cluster.node("clickhouse1")

    name = f"without_is_deleted_{getuid()}"

    cluster_name = "sharded_replicated_cluster"

    try:
        with Given("I create table without is_deleted column"):
            node1.query("SHOW clusters;")
            node1.query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                f"/tables/{name}/',"
                " '{replica}', version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            node1.query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with Then(
            "I select all data from the table and expect to see only not deleted data"
        ):
            for node in self.context.cluster.nodes["clickhouse"][:3]:
                self.context.cluster.node(node).query(
                    f"SELECT count(*) FROM {name} FINAL;", message="1"
                )
    finally:
        with Finally("I drop table"):
            node1.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}")


@TestScenario
def with_is_deleted_distributed(self):
    """Checking that the new ReplicateReplacingMergeTree engine on 2 shard cluster with one shard on 2 replicas and
    distributed table on it with is_deleted parameter and without clean_deleted_rows
    setting works in the same way as the old ReplacingMergeTree engine, and that it does not conceal rows with
    is_deleted=1."""

    node1 = self.context.cluster.node("clickhouse1")

    name = f"with_is_deleted_{getuid()}"

    cluster_name = "sharded_replicated_cluster"

    try:
        with Given("I create table with is_deleted column"):
            node1.query("SHOW clusters;", message="sharded_replicated_cluster")
            node1.query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                f"/tables/{name}/',"
                " '{replica}', version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            node1.query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with And("I create distributed table"):
            node1.query(
                f"CREATE TABLE IF NOT EXISTS distr_{name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = Distributed('{cluster_name}','default','{name}')"
            )

        with Then(
            "I select all data from the table and expect to see only not delete data"
        ):
            node1.query(
                f"SELECT * FROM distr_{name} FINAL FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data1","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

    finally:
        with Finally("I drop table"):
            node1.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}")
            node1.query(f"DROP TABLE IF EXISTS distr_{name} ON CLUSTER {cluster_name}")


@TestScenario
def update_distributed(self):
    """Check updating a row by inserting a row with (arbitrary) greater version or delete old one for the new
    ReplicateReplacingMergeTree engine on 2 shard cluster with one shard on 2 replicas and distributed table on it."""

    insert_values_local = (
        " ('data1','adsf', 1, 0),"
        " ('data1','adsf', 2, 0),"
        " ('data1', 'a', 3, 0),"
        " ('data1', 'b', 1, 1),"
        " ('data1', 'c', 2, 1)"
    )

    insert_values_update = " ('data1', 'a', 3, 1)" " ('data1', 'fdasd', 3, 0),"

    node1 = self.context.cluster.node("clickhouse1")

    name = f"update_{getuid()}"

    cluster_name = "sharded_replicated_cluster"

    try:
        with Given(
            "I create table with is_deleted column and clean_deleted_rows='Always'"
        ):
            node1.query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, some_data String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                f"/tables/{name}/',"
                " '{replica}', version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            node1.query(
                f"INSERT INTO {name} VALUES {insert_values_local}",
            )

        with And("I create distributed table"):
            node1.query(
                f"CREATE TABLE IF NOT EXISTS distr_{name} ON CLUSTER '{cluster_name}'"
                f"(id String, some_data String, version UInt32, is_deleted UInt8)"
                f" ENGINE = Distributed('{cluster_name}','default','{name}')"
            )

        with Then(
            "I select all data from the table with --final and expect to see all the latest "
            "version not deleted data"
        ):
            node1.query(
                f"SELECT * FROM distr_{name} FORMAT JSONEachRow;",
                message='{"id":"data1","some_data":"a","version":3,"is_deleted":0}\n'
                        '{"id":"data1","some_data":"a","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

        with And("I insert data in this table"):
            node1.query(f"INSERT INTO {name} VALUES {insert_values_update}")

        with And("I check data that data has been updated"):
            node1.query(
                f"SELECT * FROM distr_{name} FORMAT JSONEachRow;",
                message='{"id":"data1","some_data":"fdasd","version":3,"is_deleted":0}\n'
                        '{"id":"data1","some_data":"fdasd","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )
    finally:
        with Finally("I drop table"):
            node1.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}")
            node1.query(f"DROP TABLE IF EXISTS distr_{name} ON CLUSTER {cluster_name}")


@TestModule
@Requirements(RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree("1.0"),
              RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree_Distributed("1.0"))
@Name("replicated_replacing_merge_tree")
def feature(self):
    """Check new ReplicatedReplacingMergeTree engine and Distributed engine on it."""
    xfail("in progress, coming soon")
    if check_clickhouse_version("<23.2")(self):
        skip(
            reason="new ReplacingMergeTree engine is only supported on ClickHouse version >= 23.2"
        )

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()

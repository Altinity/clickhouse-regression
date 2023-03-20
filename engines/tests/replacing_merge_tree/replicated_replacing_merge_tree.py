import sys

from testflows.core import *
from engines.requirements import *
from engines.tests.steps import *
from helpers.common import check_clickhouse_version


append_path(sys.path, "..")


@TestScenario
def without_is_deleted(self, cluster_name=None):
    """Checking that ReplicatedReplacingMergeTree engine created without `is_deleted` parameter setting works in the
    same way as the old ReplacingMergeTree engine, and that it does not hide rows with is_deleted=1."""

    if cluster_name is None:
        cluster_name = self.context.cluster_name

    name = f"without_is_deleted_{getuid()}"

    try:
        with Given("I create table without is_deleted column"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                "/tables/{shard}"
                f"/{name}',"
                " '{replica}', version) ORDER BY id"
            )

        with When("I insert data in this table"):
            self.context.nodes[0].query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            for node in self.context.nodes[0:2]:
                node.query(
                    f"SELECT * FROM {name} FINAL FORMAT JSONEachRow;",
                    message='{"id":"data1","version":3,"is_deleted":0}\n'
                    '{"id":"data2","version":3,"is_deleted":1}\n'
                    '{"id":"data3","version":3,"is_deleted":1}',
                    settings=[("final", 1)],
                )
            self.context.nodes[2].query(
                f"SELECT count(*) FROM {name} FINAL FORMAT JSONEachRow;",
                message="0",
                settings=[("final", 1)],
            )
    finally:
        with Finally("I drop table on cluster"):
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}"
            )


@TestScenario
def without_is_deleted_distributed(self, cluster_name=None):
    """Checking that Distributed engine on the new ReplacingMergeTree engine created without `is_deleted` parameter
    setting works in the same way as the old ReplacingMergeTree engine, and that it does not hide
    rows with is_deleted=1."""

    if cluster_name is None:
        cluster_name = self.context.cluster_name

    name = f"without_is_deleted_{getuid()}"

    try:
        with Given("I create initial table with is_deleted column"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                "/tables/{shard}"
                f"/{name}',"
                " '{replica}', version) ORDER BY id"
            )

        with When("I insert data on the first shard of this table"):
            self.context.nodes[0].query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with And("I create distributed table on the initial table"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS distr_{name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = Distributed('{self.context.cluster_name}','default','{name}')"
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            self.context.nodes[0].query(
                f"SELECT * FROM distr_{name} FINAL FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}',
                settings=[("final", 1)],
            )

        with And("I insert data in the second shard of the initial table"):
            self.context.nodes[2].query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            self.context.nodes[0].query(
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
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}"
            )
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS distr_{name} ON CLUSTER" f" {cluster_name}"
            )


@TestScenario
def with_is_deleted(self, cluster_name=None):
    """Checking that ReplicatedReplacingMergeTree engine created with `is_deleted` parameter setting works in the same
    way as the old ReplacingMergeTree engine, but it it hides rows with is_deleted=1."""

    if cluster_name is None:
        cluster_name = self.context.cluster_name

    name = f"without_is_deleted_{getuid()}"

    try:
        with Given("I create table with is_deleted column"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                "/tables/{shard}"
                f"/{name}',"
                " '{replica}', version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            self.context.nodes[0].query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            for node in self.context.nodes[0:2]:
                node.query(
                    f"SELECT * FROM {name} FINAL FORMAT JSONEachRow;",
                    message='{"id":"data1","version":3,"is_deleted":0}',
                    settings=[("final", 1)],
                )
                node.query(
                    f"SELECT count(*) FROM {name} FINAL FORMAT JSONEachRow;",
                    message="1",
                    settings=[("final", 1)],
                )
            self.context.nodes[2].query(
                f"SELECT count(*) FROM {name} FINAL FORMAT JSONEachRow;",
                message="0",
                settings=[("final", 1)],
            )
    finally:
        with Finally("I drop table on cluster"):
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}"
            )


@TestScenario
def with_is_deleted_distributed(self, cluster_name=None):
    """Checking that Distributed engine on the new ReplacingMergeTree engine created with `is_deleted` parameter setting
    works in the same way as the old ReplacingMergeTree engine,but it hides rows with is_deleted=1."""

    if cluster_name is None:
        cluster_name = self.context.cluster_name

    name = f"without_is_deleted_{getuid()}"

    try:
        with Given("I create initial table with is_deleted column"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                "/tables/{shard}"
                f"/{name}',"
                " '{replica}', version, is_deleted) ORDER BY id"
            )

        with When("I insert data on the first shard of this table"):
            self.context.nodes[0].query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with And("I create distributed table on the initial table"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS distr_{name} ON CLUSTER '{cluster_name}'"
                f"(id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = Distributed('{self.context.cluster_name}','default','{name}')"
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            self.context.nodes[0].query(
                f"SELECT * FROM distr_{name} FINAL FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )
            self.context.nodes[0].query(
                f"SELECT count(*) FROM {name} FINAL FORMAT JSONEachRow;",
                message="1",
                settings=[("final", 1)],
            )

        with And("I insert data in the second shard of the initial table"):
            self.context.nodes[2].query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with Then(
            "I select all data from the table and expect to see all latest version data (deleted and not)"
        ):
            self.context.nodes[0].query(
                f"SELECT * FROM distr_{name} FINAL FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data1","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

    finally:
        with Finally("I drop table"):
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}"
            )
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS distr_{name} ON CLUSTER" f" {cluster_name}"
            )


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_Update_Distributed("1.0"))
def update_distributed(self, cluster_name=None):
    """Check updating a row by inserting a row with (arbitrary) greater version or delete old one for the new
    ReplicateReplacingMergeTree engine."""

    if cluster_name is None:
        cluster_name = self.context.cluster_name

    insert_values_local = (
        " ('data1','adsf', 1, 0),"
        " ('data1','adsf', 2, 0),"
        " ('data1', 'a', 3, 0),"
        " ('data1', 'b', 1, 1),"
        " ('data1', 'c', 2, 1)"
    )

    insert_values_update = " ('data1', 'a', 3, 1)" " ('data1', 'fdasd', 3, 0),"

    name = f"update_{getuid()}"

    try:
        with Given("I create table with is_deleted column"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS {name} ON CLUSTER '{cluster_name}'"
                f"(id String, some_data String, version UInt32, is_deleted UInt8)"
                " ENGINE = ReplicatedReplacingMergeTree('/clickhouse"
                "/tables/{shard}"
                f"/{name}',"
                " '{replica}', version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            self.context.nodes[0].query(
                f"INSERT INTO {name} VALUES {insert_values_local}",
            )

        with And("I create distributed table"):
            self.context.nodes[0].query(
                f"CREATE TABLE IF NOT EXISTS distr_{name} ON CLUSTER '{cluster_name}'"
                f"(id String, some_data String, version UInt32, is_deleted UInt8)"
                f" ENGINE = Distributed('{cluster_name}','default','{name}')"
            )

        with Then(
            "I select all data from the table with --final and expect to see all the latest "
            "version not deleted data"
        ):
            self.context.nodes[0].query(
                f"SELECT * FROM distr_{name} FORMAT JSONEachRow;",
                message='{"id":"data1","some_data":"a","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

        with And("I insert data in this replicated table on the first node"):
            self.context.nodes[0].query(
                f"INSERT INTO {name} VALUES {insert_values_update}"
            )

        with And("I check data that data has been updated"):
            self.context.nodes[0].query(
                f"SELECT * FROM distr_{name} FORMAT JSONEachRow;",
                message='{"id":"data1","some_data":"fdasd","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )
    finally:
        with Finally("I drop table"):
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster_name}"
            )
            self.context.nodes[0].query(
                f"DROP TABLE IF EXISTS distr_{name} ON CLUSTER {cluster_name}"
            )


@TestModule
@Requirements(
    RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree("1.0"),
    RQ_SRS_035_ClickHouse_ReplicatedReplacingMergeTree_Distributed("1.0"),
)
@Name("replicated_replacing_merge_tree")
def feature(self):
    """Check new ReplicatedReplacingMergeTree engine and Distributed engine on it
    on 2-shard cluster where one shard has 2 replicas and the other shard has only 1 replica.
    """
    self.context.cluster_name = "sharded_replicated_cluster"
    self.context.nodes = [
        self.context.cluster.node(name)
        for name in self.context.cluster.nodes["clickhouse"]
    ]

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

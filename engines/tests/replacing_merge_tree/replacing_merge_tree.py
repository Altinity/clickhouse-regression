import sys

from testflows.core import *
from engines.requirements import *
from engines.tests.steps import *
from helpers.common import check_clickhouse_version


append_path(sys.path, "..")


@TestScenario
def final(self, node=None):
    """Test to check --final setting behaviour with new ReplacingMergeTree engine"""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"repl_tbl_part_{getuid()}"

    try:
        with Given("I create table with ReplacingMergeTree engine"):
            node.query(
                f"CREATE TABLE {name} (key UInt32, value UInt32, part_key UInt32) ENGINE = ReplacingMergeTree"
                f" PARTITION BY part_key ORDER BY key;"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} SELECT 1 AS key, number AS value, number % 2 AS part_key FROM numbers(4)"
                f" SETTINGS optimize_on_insert = 0;"
            )

        with Then("I select all data from the table"):
            node.query(f"SELECT count(*) FROM {name};", message="4")

        with And("I select all data from the table with --final"):
            node.query(
                f"SELECT count(*) FROM {name};", message="1", settings=[("final", 1)]
            )

        with And(
            "I select all data from the table with --final and --do_not_merge_across_partitions_select_final"
        ):
            node.query(
                f"SELECT count(*) FROM {name};",
                message="2",
                settings=[
                    ("final", 1),
                    ("do_not_merge_across_partitions_select_final", 1),
                ],
            )

        with And("I optimize table"):
            node.query(
                f"OPTIMIZE TABLE {name} FINAL;",
            )

        with Then("I select again all data from the table"):
            node.query(f"SELECT count(*) FROM {name};", message="2")

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_DeleteDisabled("1.0"))
def without_is_deleted(self, node=None):
    """Checking that the new ReplacingMergeTree engine without is_deleted parameter and without clean_deleted_rows
    setting works in the same way as the old ReplacingMergeTree engine, and that it does not conceal rows with
    is_deleted=1."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"without_is_deleted_{getuid()}"

    try:
        with Given("I create table without is_deleted column"):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = ReplacingMergeTree(version) ORDER BY id"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES {insert_values}",
                settings=[("optimize_on_insert", 0)],
            )

        with Then(
            "I select all data from the table and expect to see all inserted data"
        ):
            node.query(f"SELECT count(*) FROM {name};", message="18")

        with And(
            "I select all data from the table with --final and expect to see all the latest version data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}',
                settings=[("final", 1)],
            )

        with And("I optimize table"):
            node.query(
                f"OPTIMIZE TABLE {name} FINAL;",
            )

        with Then(
            "I select again all data from the table and expect to see all the latest version data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}',
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(
    RQ_SRS_035_ClickHouse_ReplacingMergeTree_Settings_CleanDeletedRowsDisabled("1.0")
)
def clean_deleted_rows_without_is_deleted(self, node=None):
    """Checking that the new ReplacingMergeTree engine without is_deleted parameter and with clean_deleted_rows="Always"
    setting works in the same way as the old ReplacingMergeTree engine, and that it does not conceal rows with
     is_deleted=1."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"clean_deleted_rows_without_is_deleted_{getuid()}"

    try:
        with Given(
            "I create table without is_deleted column and with clean_deleted_rows='Always'"
        ):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = ReplacingMergeTree(version) ORDER BY id SETTINGS clean_deleted_rows='Always'"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES {insert_values}",
                settings=[("optimize_on_insert", 0)],
            )

        with Then(
            "I select all data from the table and expect to see all inserted data"
        ):
            node.query(f"SELECT count(*) FROM {name};", message="18")

        with And(
            "I select all data from the table with --final and expect to see all the latest version data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}',
                settings=[("final", 1)],
            )

        with And("I optimize table"):
            node.query(
                f"OPTIMIZE TABLE {name} FINAL;",
            )

        with Then(
            "I select again all data from the table and expect to see all the latest version data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}',
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_Delete("1.0"))
def with_is_deleted(self, node=None):
    """Checking that the new ReplacingMergeTree engine, which includes the is_deleted parameter and excludes the
    clean_deleted_rows setting, will conceal all rows with is_deleted=1 and the same rows with is_deleted=0 with
     --final=1 but `OPTIMIZE TABLE FINAL` doesn't influence result as clean_deleted_rows='Never'.
    """

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"clean_deleted_rows_with_is_deleted_{getuid()}"

    try:
        with Given("I create table with is_deleted column"):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = ReplacingMergeTree(version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES {insert_values}",
                settings=[("optimize_on_insert", 0)],
            )

        with Then(
            "I select all data from the table and expect to see all inserted data"
        ):
            node.query(f"SELECT count(*) FROM {name};", message="18")

        with And(
            "I select all data from the table with --final and expect to see all the latest "
            "version not deleted data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

        with And("I optimize table"):
            node.query(
                f"OPTIMIZE TABLE {name} FINAL;",
            )

        with Then(
            "I select again all data from the table and expect to see all the latest version data but without"
            " deletes as clean_deleted_rows='Never'"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}\n'
                '{"id":"data2","version":3,"is_deleted":1}\n'
                '{"id":"data3","version":3,"is_deleted":1}',
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_Settings_CleanDeletedRows("1.0"))
def clean_deleted_rows_with_is_deleted(self, node=None):
    """Checking that the new ReplacingMergeTree engine, which includes the is_deleted parameter and the
    clean_deleted_rows setting is'Always', will conceal all rows with is_deleted=1 and the same rows with is_deleted=0
    with --final=1 or after `OPTIMIZE TABLE FINAL` for all queries."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"clean_deleted_rows_with_is_deleted_{getuid()}"

    try:
        with Given(
            "I create table with is_deleted column and clean_deleted_rows='Always'"
        ):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = ReplacingMergeTree(version, is_deleted) ORDER BY id SETTINGS clean_deleted_rows='Always'"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES {insert_values}",
                settings=[("optimize_on_insert", 0)],
            )

        with Then(
            "I select all data from the table and expect to see all inserted data"
        ):
            node.query(f"SELECT count(*) FROM {name};", message="18")

        with And(
            "I select all data from the table with --final and expect to see all the latest "
            "version not deleted data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

        with And("I optimize table"):
            node.query(
                f"OPTIMIZE TABLE {name} FINAL;",
            )

        with Then(
            "I select again all data from the table and expect to see all the the latest version not deleted data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","version":3,"is_deleted":0}',
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_Update("1.0"))
def update(self, node=None):
    """Check updating a row by inserting a row with (arbitrary) greater version or delete old one."""

    insert_values = (
        " ('data1','adsf', 1, 0),"
        " ('data1','adsf', 2, 0),"
        " ('data1', 'a', 3, 0),"
        " ('data1', 'b', 1, 1),"
        " ('data1', 'c', 2, 1)"
    )

    insert_values_update = " ('data1', 'a', 3, 1)" " ('data1', 'fdasd', 3, 0),"

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"update_{getuid()}"

    try:
        with Given(
            "I create table with is_deleted column and clean_deleted_rows='Always'"
        ):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, some_data String, version UInt32, is_deleted UInt8)"
                f" ENGINE = ReplacingMergeTree(version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES {insert_values}",
            )

        with Then(
            "I select all data from the table with --final and expect to see all the latest "
            "version not deleted data"
        ):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","some_data":"a","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

        with And("I insert data in this table"):
            node.query(f"INSERT INTO {name} VALUES {insert_values_update}")

        with And("I check data that data has been updated"):
            node.query(
                f"SELECT * FROM {name} FORMAT JSONEachRow;",
                message='{"id":"data1","some_data":"fdasd","version":3,"is_deleted":0}',
                settings=[("final", 1)],
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_Update_Distributed("1.0"))
def update_distributed(self, node=None):
    """Check updating a row by inserting a row with (arbitrary) greater version or delete old one."""

    insert_values = (
        " ('data1','adsf', 1, 0),"
        " ('data1','adsf', 2, 0),"
        " ('data1', 'a', 3, 0),"
        " ('data1', 'b', 1, 1),"
        " ('data1', 'c', 2, 1)"
    )

    cluster_name = "sharded_replicated_cluster"

    insert_values_update = " ('data1', 'a', 3, 1)" " ('data1', 'fdasd', 3, 0),"

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"update_{getuid()}"

    try:
        with Given("I create table with is_deleted column aon all nodes"):
            for node_local in self.context.cluster.nodes["clickhouse"]:
                self.context.cluster.node(node_local).query(
                    f"CREATE TABLE IF NOT EXISTS {name} (id String, some_data String, version UInt32, is_deleted UInt8)"
                    f" ENGINE = ReplacingMergeTree(version, is_deleted) ORDER BY id"
                )

        with And("I create distributed table"):
            node.query(
                f"CREATE TABLE IF NOT EXISTS distr_{name} ON CLUSTER '{cluster_name}'"
                f"(id String, some_data String, version UInt32, is_deleted UInt8)"
                f" ENGINE = Distributed('{cluster_name}','default','{name}')",
            )

        with When("I insert data in this table"):
            for node_local in self.context.cluster.nodes["clickhouse"][0:2]:
                self.context.cluster.node(node_local).query(
                    f"INSERT INTO {name} VALUES {insert_values}"
                )

        with Then(
            "I select all data from the table with --final and expect to see all the latest "
            "version not deleted data"
        ):
            for node_local in self.context.cluster.nodes["clickhouse"][0:2]:
                self.context.cluster.node(node_local).query(
                    f"SELECT * FROM distr_{name} FORMAT JSONEachRow;",
                    message='{"id":"data1","some_data":"a","version":3,"is_deleted":0}',
                    settings=[("final", 1)],
                )

        with And("I insert data in this table"):
            for node_local in self.context.cluster.nodes["clickhouse"][0:2]:
                self.context.cluster.node(node_local).query(
                    f"INSERT INTO {name} VALUES {insert_values_update}"
                )

        with And("I check data that data has been updated"):
            for node_local in self.context.cluster.nodes["clickhouse"][0:2]:
                self.context.cluster.node(node_local).query(
                    f"SELECT * FROM distr_{name} FORMAT JSONEachRow;",
                    message='{"id":"data1","some_data":"fdasd","version":3,"is_deleted":0}',
                    settings=[("final", 1)],
                )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_Errors_WrongDataValue("1.0"))
def incorrect_data_insert(self, node=None):
    """Check for incorrect insert data value into is_deleted column."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"incorrect_data_insert_{getuid()}"

    try:
        with Given(
            "I create table with is_deleted column and clean_deleted_rows='Always'"
        ):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = ReplacingMergeTree(version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES ('data1', 1, 6)",
                message="Received from localhost:9000. DB::Exception: Incorrect data: is_deleted = 6 (must be 1 or 0).."
                " (INCORRECT_DATA)",
                exitcode=117,
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_035_ClickHouse_ReplacingMergeTree_Errors_WrongDataType("1.0"))
def incorrect_data_type(self, node=None):
    """Check that incorrect insert data type for is_deleted column provides Exception."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"incorrect_data_insert_{getuid()}"

    try:
        with Given(
            "I create table with is_deleted column and clean_deleted_rows='Always'"
        ):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, version UInt32, is_deleted String)"
                f" ENGINE = ReplacingMergeTree(version, is_deleted) ORDER BY id SETTINGS clean_deleted_rows='Always'",
                message="DB::Exception: Received from localhost:9000. DB::Exception: is_deleted column (is_deleted) for "
                "storage ReplacingMergeTree must have type UInt8. Provided column of type String.. "
                "(BAD_TYPE_OF_FIELD)",
                exitcode=169,
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
def incorrect_data_insert_with_disabled_optimize_on_insert(self, node=None):
    """Check for incorrect insert data value into is_deleted column with optimize_on_insert=0."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"error_{getuid()}"

    try:
        with Given(
            "I create table with is_deleted column and clean_deleted_rows='Always'"
        ):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {name} (id String, version UInt32, is_deleted UInt8)"
                f" ENGINE = ReplacingMergeTree(version, is_deleted) ORDER BY id"
            )

        with When("I insert data in this table"):
            node.query(
                f"INSERT INTO {name} VALUES ('data1', 1, 6)",
                settings=[("optimize_on_insert", 0)],
            )

        with Then(
            "I select all data from the table with --final and expect to see all the latest "
            "version not deleted data"
        ):
            node.query(f"SELECT * FROM {name} FORMAT JSONEachRow;")

            with And("I optimize table"):
                node.query(
                    f"OPTIMIZE TABLE {name} FINAL;",
                    message="DB::Exception:",
                    exitcode=117,
                )

                node.query(
                    f"SELECT * FROM {name}  FORMAT JSONEachRow;",
                    message="DB::Exception:",
                    exitcode=117,
                    settings=[("final", 1)],
                )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestModule
@Name("replacing_merge_tree")
def feature(self):
    """Check new ReplacingMergeTree engine."""
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

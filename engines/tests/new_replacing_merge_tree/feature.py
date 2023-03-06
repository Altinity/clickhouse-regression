import sys

from testflows.core import *
from engines.requirements import *
from engines.tests.steps import *
from helpers.common import check_clickhouse_version


append_path(sys.path, "..")


@TestScenario
def test_example(self, node=None):
    """https://kb.altinity.com/engines/mergetree-table-engine-family/replacingmergetree/"""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"repl_tbl_part_{getuid()}"

    try:
        with Given("I create table form the issue"):
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


@TestModule
@Name("new_replacing_merge_tree")
def feature(self):
    """Check new ReplacingMergeTree engine."""
    if check_clickhouse_version("<23.2")(self):
        skip(
            reason="--final query setting is only supported on ClickHouse version >= 23.2"
        )

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()

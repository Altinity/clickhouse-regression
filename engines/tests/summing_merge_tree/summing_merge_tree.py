import sys

from testflows.core import *
from engines.tests.steps import *
from helpers.common import check_clickhouse_version

append_path(sys.path, "..")


@TestScenario
def zero_row_deletion_with_update(self, node=None):
    """Check that SummingMergeTree deletes rows where all summed columns
    are zero after UPDATE and OPTIMIZE TABLE FINAL."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"summing_zero_update_{getuid()}"

    try:
        with Given("I create SummingMergeTree table with partition key"):
            node.query(
                f"CREATE TABLE {name} (v UInt64, p UInt64, c UInt64)"
                f" ENGINE = SummingMergeTree PARTITION BY p ORDER BY v"
            )

        with When("I insert data"):
            node.query(f"INSERT INTO {name} VALUES (1, 1, 100)")
            node.query(f"INSERT INTO {name} VALUES (2, 2, 200)")

        with And("I update summing column to zero"):
            node.query(f"ALTER TABLE {name} UPDATE c = 0 WHERE v = 1")

        with And("I optimize table"):
            node.query(f"OPTIMIZE TABLE {name} FINAL")

        with Then("row with all summed columns = 0 should be deleted"):
            node.query(
                f"SELECT count() FROM {name} FORMAT TabSeparated",
                message="1",
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
def zero_row_deletion_with_clear_column(self, node=None):
    """Check that SummingMergeTree deletes rows where all summed columns
    are zero after CLEAR COLUMN IN PARTITION and OPTIMIZE TABLE FINAL.

    Related: https://github.com/ClickHouse/ClickHouse/issues/101953
    """

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name = f"summing_zero_clear_{getuid()}"

    try:
        with Given("I create SummingMergeTree table with partition key"):
            node.query(
                f"CREATE TABLE {name} (v UInt64, p UInt64, c UInt64)"
                f" ENGINE = SummingMergeTree PARTITION BY p ORDER BY v"
            )

        with When("I insert data"):
            node.query(f"INSERT INTO {name} VALUES (1, 1, 100)")
            node.query(f"INSERT INTO {name} VALUES (2, 2, 200)")

        with And("I clear summing column in partition 1"):
            node.query(f"ALTER TABLE {name} CLEAR COLUMN c IN PARTITION 1")

        with And("I optimize table"):
            node.query(f"OPTIMIZE TABLE {name} FINAL")

        with Then("row with all summed columns = 0 should be deleted"):
            node.query(
                f"SELECT count() FROM {name} FORMAT TabSeparated",
                message="1",
            )

    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
def clear_column_validation_consistency(self, node=None):
    """Check that CLEAR COLUMN on auto-detected summing columns is
    blocked the same way as explicitly declared ones.

    Related: https://github.com/ClickHouse/ClickHouse/issues/101953
    """

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name_explicit = f"summing_explicit_{getuid()}"
    name_auto = f"summing_auto_{getuid()}"

    try:
        with Given("I create table with explicit columns_to_sum"):
            node.query(
                f"CREATE TABLE {name_explicit} (v UInt64, p UInt64, c UInt64)"
                f" ENGINE = SummingMergeTree(c) PARTITION BY p ORDER BY v"
            )

        with And("I create table with auto-detected columns_to_sum"):
            node.query(
                f"CREATE TABLE {name_auto} (v UInt64, p UInt64, c UInt64)"
                f" ENGINE = SummingMergeTree PARTITION BY p ORDER BY v"
            )

        with When("I try to clear summing column on explicit table"):
            node.query(
                f"ALTER TABLE {name_explicit} CLEAR COLUMN c IN PARTITION 1",
                exitcode=524,
                message="ALTER_OF_COLUMN_IS_FORBIDDEN",
            )

        with Then("I try to clear summing column on auto-detected table"):
            node.query(
                f"ALTER TABLE {name_auto} CLEAR COLUMN c IN PARTITION 1",
                exitcode=524,
                message="ALTER_OF_COLUMN_IS_FORBIDDEN",
            )

    finally:
        with Finally("I drop tables"):
            node.query(f"DROP TABLE IF EXISTS {name_explicit}")
            node.query(f"DROP TABLE IF EXISTS {name_auto}")


@TestModule
@Name("summing_merge_tree")
def feature(self):
    """SummingMergeTree engine tests."""
    for scenario in loads(current_module(), Scenario):
        scenario()

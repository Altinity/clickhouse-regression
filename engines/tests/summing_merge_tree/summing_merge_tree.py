import sys

from testflows.core import *
from engines.tests.steps import *
from helpers.common import check_clickhouse_version
from helpers.create import create_summing_merge_tree_table
from helpers.alter.update import alter_table_update_column
from helpers.alter.column import alter_table_clear_column_in_partition

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
            create_summing_merge_tree_table(
                table_name=name,
                columns=[
                    {"name": "v", "type": "UInt64"}, 
                    {"name": "p", "type": "UInt64"}, 
                    {"name": "c", "type": "UInt64"}, 
                ],
                partition_by="p",
                order_by="v",
            )

        with When("I insert data"):
            insert_values_into_table(
                table_name=name,
                values=["(1, 1, 100)", "(2, 2, 200)"],
            )

        with And("I update summing column to zero"):
            alter_table_update_column(
                table_name=name,
                column_name="c",
                expression="0",
                condition="v = 1",
                node=node,
            )

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
            create_summing_merge_tree_table(
                table_name=name,
                columns=[
                    {"name": "v", "type": "UInt64"},
                    {"name": "p", "type": "UInt64"},
                    {"name": "c", "type": "UInt64"},
                ],
                partition_by="p",
                order_by="v",
            )

        with When("I insert data"):
            insert_values_into_table(
                table_name=name,
                values=["(1, 1, 100)", "(2, 2, 200)"],
            )

        with And("I clear summing column in partition 1"):
            alter_table_clear_column_in_partition(
                table_name=name,
                partition_name="1",
                column_name="c",
                node=node,
            )

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
    """Check that CLEAR COLUMN on summing columns is allowed consistently
    for both explicit and auto-detected ``columns_to_sum``.

    Related: https://github.com/ClickHouse/ClickHouse/issues/101953
    """

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    name_explicit = f"summing_explicit_{getuid()}"
    name_auto = f"summing_auto_{getuid()}"

    try:
        columns = [
            {"name": "v", "type": "UInt64"},
            {"name": "p", "type": "UInt64"},
            {"name": "c", "type": "UInt64"},
        ]

        with Given("I create table with explicit columns_to_sum"):
            create_summing_merge_tree_table(
                table_name=name_explicit,
                columns=columns,
                partition_by="p",
                order_by="v",
                columns_to_sum=["c"],
            )

        with And("I create table with auto-detected columns_to_sum"):
            create_summing_merge_tree_table(
                table_name=name_auto,
                columns=columns,
                partition_by="p",
                order_by="v",
            )

        with When("I clear summing column on explicit table"):
            alter_table_clear_column_in_partition(
                table_name=name_explicit,
                partition_name="1",
                column_name="c",
                node=node,
            )

        with Then("I clear summing column on auto-detected table"):
            alter_table_clear_column_in_partition(
                table_name=name_auto,
                partition_name="1",
                column_name="c",
                node=node,
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

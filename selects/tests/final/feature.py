from testflows.core import *
from selects.requirements import *
from selects.tests.steps import *


@TestScenario
def replacing_without_ver(
    self, replacing_tables, collapsing_tables, aggregating_tables
):
    """
    Without ver - the last inserted 'wins'.
    """
    node = self.context.cluster.node("clickhouse1")
    node.query(f"SELECT count() FROM {replacing_tables[0]} FINAL;", message="1")
    node.query(f"SELECT count() FROM {replacing_tables[0]};", message="2")


@TestScenario
def replacing_with_ver(self, replacing_tables, collapsing_tables, aggregating_tables):
    """
    With ver - the row with the biggest ver 'wins'.
    """
    node = self.context.cluster.node("clickhouse1")
    node.query(f"SELECT count() FROM {replacing_tables[1]} FINAL;", message="1")
    node.query(f"SELECT count() FROM {replacing_tables[1]};", message="2")


@TestScenario
def collapsing(self, replacing_tables, collapsing_tables, aggregating_tables):
    """
    Collapsing with final.
    """
    node = self.context.cluster.node("clickhouse1")
    node.query(f"SELECT count() FROM {collapsing_tables[0]} FINAL;", message="1")
    node.query(f"SELECT count() FROM {collapsing_tables[0]};", message="3")


@TestScenario
def aggregating(self, replacing_tables, collapsing_tables, aggregating_tables):
    """
    AggregatingMergeTree with columns which are nor the part of ORDER BY key picks the first value met.
    """
    node = self.context.cluster.node("clickhouse1")
    node.query(f"SELECT count() FROM {aggregating_tables[0]} FINAL;", message="1")
    node.query(f"SELECT count() FROM {aggregating_tables[0]};", message="2")


@TestScenario
def aggregating(self, replacing_tables, collapsing_tables, aggregating_tables):
    """
    Last non-null value for each column.
    """
    node = self.context.cluster.node("clickhouse1")
    node.query(f"SELECT count() FROM {aggregating_tables[1]} FINAL;", message="1")
    node.query(f"SELECT count() FROM {aggregating_tables[1]};", message="2")


@TestFeature
@Name("final")
def feature(self):
    """Check FINAL modifier."""
    node = self.context.cluster.node("clickhouse1")
    try:
        with Given("I create ReplacingMergeTree tables with inserted data"):
            replacing_tables = ["ReplacingMT_without_ver", "ReplacingMT_with_ver"]
            with Given("I create example table without ver"):
                node.query(
                    f"CREATE TABLE {replacing_tables[0]} (key Int64,someCol String,eventTime DateTime) "
                    "ENGINE = ReplacingMergeTree ORDER BY key;"
                )
                node.query(
                    f"INSERT INTO {replacing_tables[0]} Values (1, 'first', '2020-01-01 01:01:01');"
                )
                node.query(
                    f"INSERT INTO {replacing_tables[0]} Values (1, 'second', '2020-01-01 00:00:00');"
                )

            with Given("I create example table with ver"):
                node.query(
                    f"CREATE TABLE {replacing_tables[1]} (key Int64,someCol String,eventTime DateTime) "
                    "ENGINE = ReplacingMergeTree(eventTime) ORDER BY key;"
                )
                node.query(
                    f"INSERT INTO {replacing_tables[1]} Values (1, 'first', '2020-01-01 01:01:01');"
                )
                node.query(
                    f"INSERT INTO {replacing_tables[1]} Values (1, 'second', '2020-01-01 00:00:00');"
                )

            with Given("I create simple tables"):
                for i in range(3):
                    create_table(
                        core_table=f"simple_replacingmergetree_table{i}",
                        core_table_engine="ReplacingMergeTree()",
                        distributed=None,
                        cluster=None,
                        distributed_table=None,
                    )

                    insert_into_table(
                        table_name=f"simple_replacingmergetree_table{i}",
                        block_number=3,
                        row_number=10,
                        unique_rows=True,
                        equal_rows=True,
                    )

        with Given("I create CollapsingMergeTree tables"):
            collapsing_tables = ["CollapsingMT"]
            with Given("I create example table"):
                node.query(
                    f"CREATE TABLE {collapsing_tables[0]}"
                    f" ( UserID UInt64, PageViews UInt8, Duration UInt8, Sign Int8)"
                    f" ENGINE = CollapsingMergeTree(Sign) ORDER BY UserID"
                )
                node.query(
                    f"INSERT INTO {collapsing_tables[0]} VALUES (4324182021466249494, 5, 146, 1)"
                )
                node.query(
                    f"INSERT INTO {collapsing_tables[0]}"
                    f" VALUES (4324182021466249494, 5, 146, -1),(4324182021466249494, 6, 185, 1)"
                )

        with Given("I create AggregatingMergeTree tables"):
            aggregating_tables = ["AggregatingMT", "AggregatingMT_last_nonnull"]
            with Given("I create example table"):
                node.query(
                    f"CREATE TABLE {aggregating_tables[0]} (a String, b UInt8,"
                    f" c SimpleAggregateFunction(max, UInt8)) "
                    f"ENGINE = AggregatingMergeTree ORDER BY a;"
                )
                node.query(f"INSERT INTO {aggregating_tables[0]} VALUES ('a', 1, 1);")
                node.query(f"INSERT INTO {aggregating_tables[0]} VALUES ('a', 2, 2);")

            with Given("I create example table"):
                node.query(
                    f"CREATE TABLE {aggregating_tables[1]} (col1 Int32,"
                    f" col2 SimpleAggregateFunction(anyLast, Nullable(DateTime)),"
                    f"col3 SimpleAggregateFunction(anyLast, Nullable(DateTime)))"
                    f" ENGINE = AggregatingMergeTree ORDER BY col1"
                )
                node.query(
                    f"INSERT INTO {aggregating_tables[1]} (col1, col2) VALUES (1, now());"
                )
                node.query(
                    f"INSERT INTO {aggregating_tables[1]} (col1, col2) VALUES (1, now());"
                )

        with Given("I create SummingMergeTree tables"):
            pass

        for scenario in loads(current_module(), Scenario):
            scenario(
                replacing_tables=replacing_tables,
                collapsing_tables=collapsing_tables,
                aggregating_tables=aggregating_tables,
            )

    finally:
        with Finally("I clear all data"):
            for table_name in replacing_tables:
                node.query(f"DROP TABLE {table_name};")
            for table_name in collapsing_tables:
                node.query(f"DROP TABLE {table_name};")
            for table_name in aggregating_tables:
                node.query(f"DROP TABLE {table_name};")

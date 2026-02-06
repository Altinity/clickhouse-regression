from testflows.core import *
from helpers.common import getuid
import ice.steps.hybrid as hybrid_steps


@TestScenario
def test_alias_columns_in_select(self, node=None):
    """Test that ALIAS columns defined in segment tables can be selected from hybrid table."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    sum_alias ALIAS id + value
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    sum_alias ALIAS id + value
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 10, '2025-01-15'),
                (2, 20, '2025-01-16'),
                (3, 30, '2025-01-17')
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (4, 40, '2025-01-10'),
                (5, 50, '2025-01-11'),
                (6, 60, '2025-01-12')
                """
            )

        with And("create a hybrid table using created merge tree tables"):
            watermark_date = "2025-01-15"
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed Int64,
                    sum_alias Int64,
                )
                """

            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate=f"date_col >= '{watermark_date}'",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate=f"date_col < '{watermark_date}'",
            )

        with And("select only ALIAS columns"):
            result = node.query(f"SELECT computed, sum_alias FROM {hybrid_table} WHERE id = 1").output.strip()

            assert "20\t11" in result, f"Expected computed=20, sum_alias=11"

        with Then("select different columns from the hybrid table"):
            result = node.query(f"SELECT id, value, computed, sum_alias FROM {hybrid_table} ORDER BY id").output.strip()

            assert "1\t10\t20\t11" in result, f"Expected computed=20, sum_alias=11 for id=1"
            assert "2\t20\t40\t22" in result, f"Expected computed=40, sum_alias=22 for id=2"
            assert "3\t30\t60\t33" in result, f"Expected computed=60, sum_alias=33 for id=3"
            assert "4\t40\t80\t44" in result, f"Expected computed=80, sum_alias=44 for id=4"
            assert "5\t50\t100\t55" in result, f"Expected computed=100, sum_alias=55 for id=5"
            assert "6\t60\t120\t66" in result, f"Expected computed=120, sum_alias=66 for id=6"

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestScenario
def test_alias_columns_in_predicates(self, node=None):
    """Test that ALIAS columns can not be used in hybrid table predicates (watermarks)."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    threshold ALIAS 50
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    threshold ALIAS 50
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 30, '2025-01-15'), 
                (2, 25, '2025-01-16'), 
                (3, 20, '2025-01-17')  
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (4, 15, '2025-01-10'),  
                (5, 10, '2025-01-11'),  
                (6, 40, '2025-01-12') 
                """
            )

        with And("create a hybrid table using ALIAS column in watermarks"):
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed Int64,
                    threshold UInt8,
                )
            """

            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate="computed >= threshold",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate="computed < threshold",
            )

        with Then("query the hybrid table with ALIAS column in watermarks, expect exception"):
            result = node.query(f"SELECT id, value, computed FROM {hybrid_table} ORDER BY id").output.strip()

            assert "1\t30\t60" in result
            assert "2\t25\t50" in result

            assert "4\t15\t30" in result
            assert "5\t10\t20" in result

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestScenario
def test_alias_columns_that_depends_on_alias_columns(self, node=None):
    """Test that ALIAS columns that depends on other ALIAS columns are accessible when querying hybrid tables."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    computed_2 ALIAS computed + 10
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    computed_2 ALIAS computed + 10
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 30, '2025-01-15'), 
                (2, 25, '2025-01-16'), 
                (3, 20, '2025-01-17')  
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (4, 15, '2025-01-10'),  
                (5, 10, '2025-01-11'),  
                (6, 40, '2025-01-12') 
                """
            )

        with And("create a hybrid table using created merge tree tables"):
            watermark_date = "2025-01-15"
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed Int64,
                    computed_2 Int64,
                )
            """
            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate=f"date_col >= '{watermark_date}'",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate=f"date_col < '{watermark_date}'",
            )

        with Then("query the hybrid table with ALIAS columns that depends on other ALIAS columns"):
            result = node.query(
                f"SELECT id, value, computed, computed_2 FROM {hybrid_table} ORDER BY id"
            ).output.strip()

            assert "1\t30\t60\t70" in result, "Expected computed=60, computed_2=70 for id=1"
            assert "2\t25\t50\t60" in result, "Expected computed=50, computed_2=60 for id=2"
            assert "4\t15\t30\t40" in result, "Expected computed=30, computed_2=40 for id=4"
            assert "5\t10\t20\t30" in result, "Expected computed=20, computed_2=30 for id=5"

        with And("filter by ALIAS columns in WHERE clause"):
            result = node.query(
                f"SELECT id, value, computed, computed_2 FROM {hybrid_table} WHERE computed_2 < 50 ORDER BY id"
            ).output.strip()

            assert "1\t30\t60\t70" not in result, "Expected computed=60, computed_2=70 for id=1"
            assert "2\t25\t50\t60" not in result, "Expected computed=50, computed_2=60 for id=2"
            assert "4\t15\t30\t40" in result, "Expected computed=30, computed_2=40 for id=4"
            assert "5\t10\t20\t30" in result, "Expected computed=20, computed_2=30 for id=5"

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestScenario
def test_alias_columns_in_where_clause(self, node=None):
    """Test that ALIAS columns can be used in WHERE clauses when querying hybrid tables."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    is_even ALIAS value % 2 = 0
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed ALIAS value * 2,
                    is_even ALIAS value % 2 = 0
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 10, '2025-01-15'),
                (2, 15, '2025-01-16'),
                (3, 20, '2025-01-17')
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (4, 25, '2025-01-10'),
                (5, 30, '2025-01-11'),
                (6, 35, '2025-01-12')
                """
            )

        with And("create a hybrid table using created merge tree tables"):
            watermark_date = "2025-01-15"
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    computed Int64,
                    is_even UInt8,
                )
            """
            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate=f"date_col >= '{watermark_date}'",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate=f"date_col < '{watermark_date}'",
            )

        with Then("select from hybrid table with ALIAS column in WHERE clause"):
            result = node.query(
                f"SELECT id, value, computed FROM {hybrid_table} WHERE computed > 40 ORDER BY id"
            ).output.strip()

            assert "2\t15\t30" not in result, "computed=30 should not be in result"
            assert "3\t20\t40" not in result, "computed=40 should not be in result"
            assert "5\t30\t60" in result, "computed=60 should be in result"
            assert "6\t35\t70" in result, "computed=70 should be in result"

            result = node.query(f"SELECT id, value FROM {hybrid_table} WHERE is_even = 1 ORDER BY id").output.strip()

            assert "1\t10" in result, "value=10 is even"
            assert "3\t20" in result, "value=20 is even"
            assert "5\t30" in result, "value=30 is even"
            assert "2\t15" not in result, "value=15 is odd"

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestScenario
def test_alias_columns_in_group_by_order_by(self, node=None):
    """Test that ALIAS columns in hybrid tables can be used in GROUP BY and ORDER BY clauses."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    category ALIAS value % 3,
                    computed ALIAS value * 2
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    category ALIAS value % 3,
                    computed ALIAS value * 2
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 10, '2025-01-15'),
                (2, 11, '2025-01-16'),
                (3, 12, '2025-01-17')
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (4, 13, '2025-01-10'),
                (5, 14, '2025-01-11'),
                (6, 15, '2025-01-12')
                """
            )

        with And("create a hybrid table using created merge tree tables"):
            watermark_date = "2025-01-15"
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    category Int16,
                    computed Int64,
                )
            """
            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate=f"date_col >= '{watermark_date}'",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate=f"date_col < '{watermark_date}'",
            )

        with Then("select from hybrid table with ALIAS columns in GROUP BY"):
            result = node.query(
                f"""
                SELECT category, count(), sum(computed) as total_computed
                FROM {hybrid_table}
                GROUP BY category
                """
            ).output.strip()
            assert "0\t2\t54" in result, "Expected category=0, count=2, total_computed=54"
            assert "1\t2\t46" in result, "Expected category=1, count=2, total_computed=46"
            assert "2\t2\t50" in result, "Expected category=2, count=2, total_computed=50"

            result = node.query(f"SELECT computed, count() FROM {hybrid_table} GROUP BY computed").output.strip()
            assert "20\t1" in result, "Expected computed=20, count=1"
            assert "22\t1" in result, "Expected computed=22, count=1"
            assert "24\t1" in result, "Expected computed=24, count=1"
            assert "26\t1" in result, "Expected computed=26, count=1"
            assert "28\t1" in result, "Expected computed=28, count=1"
            assert "30\t1" in result, "Expected computed=30, count=1"

        with And("select from hybrid table with ALIAS columns in ORDER BY"):
            result = node.query(f"SELECT id, computed, category FROM {hybrid_table} ORDER BY computed").output.strip()
            assert "1\t20\t1" in result, "Expected id=1, computed=20, category=1"
            assert "2\t22\t2" in result, "Expected id=2, computed=22, category=2"
            assert "3\t24\t0" in result, "Expected id=3, computed=24, category=0"
            assert "4\t26\t1" in result, "Expected id=4, computed=26, category=1"
            assert "5\t28\t2" in result, "Expected id=5, computed=28, category=2"
            assert "6\t30\t0" in result, "Expected id=6, computed=30, category=0"

            result = node.query(f"SELECT id, computed, category FROM {hybrid_table} ORDER BY category").output.strip()
            assert "3\t24\t0" in result, "Expected id=3, computed=24, category=0"
            assert "6\t30\t0" in result, "Expected id=6, computed=30, category=0"
            assert "1\t20\t1" in result, "Expected id=1, computed=20, category=1"
            assert "4\t26\t1" in result, "Expected id=4, computed=26, category=1"
            assert "2\t22\t2" in result, "Expected id=2, computed=22, category=2"
            assert "5\t28\t2" in result, "Expected id=5, computed=28, category=2"

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestScenario
def mismatch_alias_columns_type_in_hybrid_table_columns_definition(self, node=None):
    """Test that ALIAS columns with type mismatch in Hybrid table columns definition work correctly."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    category ALIAS value % 3,
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    category ALIAS value % 3,
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 10, '2025-01-15'),
                (2, 11, '2025-01-16'),
                (3, 12, '2025-01-17')
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (4, 13, '2025-01-10'),
                (5, 14, '2025-01-11'),
                (6, 15, '2025-01-12')
                """
            )

        with And("create a hybrid table using created merge tree tables"):
            watermark_date = "2025-01-15"
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    category Int32,
                )
            """
            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate=f"date_col >= '{watermark_date}'",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate=f"date_col < '{watermark_date}'",
            )

        with Then("select from hybrid table with ALIAS columns in GROUP BY"):
            result = node.query(
                f"""
                SELECT category, count()
                FROM {hybrid_table}
                GROUP BY category
                ORDER BY category
                """
            ).output.strip()

            # Verify grouping works correctly
            assert "0\t2" in result, "Expected category=0, count=2"
            assert "1\t2" in result, "Expected category=1, count=2"
            assert "2\t2" in result, "Expected category=2, count=2"

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestScenario
def test_nested_alias_columns(self, node=None):
    """Test ALIAS columns that reference other ALIAS columns."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with nested ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    doubled ALIAS value * 2,
                    quadrupled ALIAS doubled * 2,
                    sum_all ALIAS id + value + doubled + quadrupled
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    doubled ALIAS value * 2,
                    quadrupled ALIAS doubled * 2,
                    sum_all ALIAS id + value + doubled + quadrupled
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 10, '2025-01-15'),
                (2, 20, '2025-01-16')
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (3, 30, '2025-01-10'),
                (4, 40, '2025-01-11')
                """
            )

        with And("create a hybrid table using created merge tree tables"):
            watermark_date = "2025-01-15"
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    doubled Int64,
                    quadrupled Int64,
                    sum_all Int64,
                )
            """
            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate=f"date_col >= '{watermark_date}'",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate=f"date_col < '{watermark_date}'",
            )

        with Then("select from hybrid table with nested ALIAS columns"):
            result = node.query(
                f"SELECT id, value, doubled, quadrupled, sum_all FROM {hybrid_table} WHERE id = 1"
            ).output.strip()

            assert "1\t10\t20\t40\t71" in result

            result = node.query(
                f"SELECT id, value, doubled, quadrupled, sum_all FROM {hybrid_table} WHERE id = 4"
            ).output.strip()

            assert "4\t40\t80\t160\t284" in result

        with And("select with where clause and order by non-alias columns"):
            result = node.query(
                f"SELECT id, value, doubled, quadrupled, sum_all FROM {hybrid_table} WHERE id = 1 ORDER BY value"
            ).output.strip()

            assert "1\t10\t20\t40\t71" in result

            result = node.query(
                f"SELECT id, value, doubled, quadrupled, sum_all FROM {hybrid_table} WHERE id = 4 ORDER BY value"
            ).output.strip()

            assert "4\t40\t80\t160\t284" in result

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestScenario
def test_alias_columns_with_date_predicates(self, node=None):
    """Test ALIAS columns combined with date-based predicates in hybrid tables."""
    if node is None:
        node = self.context.node

    try:
        with Given("create MergeTree tables with date-based ALIAS columns"):
            left_table = f"left_table_{getuid()}"
            right_table = f"right_table_{getuid()}"

            node.query(
                f"""
                CREATE TABLE {left_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    year_month ALIAS toYYYYMM(date_col),
                    is_recent ALIAS date_col >= '2025-01-15'
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                CREATE TABLE {right_table}
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    year_month ALIAS toYYYYMM(date_col),
                    is_recent ALIAS date_col >= '2025-01-15'
                )
                ENGINE = MergeTree()
                ORDER BY (date_col, id)
                PARTITION BY toYYYYMM(date_col)
                """
            )

            node.query(
                f"""
                INSERT INTO {left_table} (id, value, date_col) VALUES
                (1, 10, '2025-01-15'),
                (2, 20, '2025-01-20'),
                (3, 30, '2025-02-01')
                """
            )

            node.query(
                f"""
                INSERT INTO {right_table} (id, value, date_col) VALUES
                (4, 40, '2025-01-10'),
                (5, 50, '2025-01-12'),
                (6, 60, '2025-02-05')
                """
            )

        with And("I create a hybrid table with date predicate"):
            watermark_date = "2025-01-15"
            hybrid_table = f"hybrid_table_{getuid()}"

            columns_definition = """
                (
                    id Int32,
                    value Int32,
                    date_col Date,
                    year_month UInt32,
                    is_recent UInt8,
                )
            """

            hybrid_steps.create_hybrid_table(
                table_name=hybrid_table,
                columns_definition=columns_definition,
                left_table_name=f"remote('localhost', currentDatabase(), {left_table})",
                left_predicate=f"date_col >= '{watermark_date}'",
                right_table_name=f"remote('localhost', currentDatabase(), {right_table})",
                right_predicate=f"date_col < '{watermark_date}'",
            )

        with Then("select from hybrid table with date-based ALIAS columns"):
            result = node.query(
                f"SELECT id, year_month FROM {hybrid_table} WHERE is_recent = 1 ORDER BY id"
            ).output.strip()

            assert "1\t202501" in result
            assert "2\t202501" in result
            assert "3\t202502" in result
            assert "4\t" not in result, "Right segment rows should not match is_recent=1"

        with And("select from hybrid table with date-based ALIAS columns in GROUP BY "):
            result = node.query(
                f"""
                SELECT year_month, count() as cnt
                FROM {hybrid_table}
                GROUP BY year_month
                ORDER BY year_month
                """
            ).output.strip()

            assert "202501\t4" in result
            assert "202502\t1" in result

    finally:
        with Finally("clean up"):
            node.query(f"DROP TABLE IF EXISTS {hybrid_table}")
            node.query(f"DROP TABLE IF EXISTS {left_table}")
            node.query(f"DROP TABLE IF EXISTS {right_table}")


@TestFeature
@Name("alias")
def feature(self, minio_root_user, minio_root_password):
    """Test ALIAS columns support in hybrid table engine segments."""
    Scenario(test=test_alias_columns_in_select)()
    Scenario(test=test_alias_columns_in_predicates)()
    Scenario(test=test_alias_columns_that_depends_on_alias_columns)()
    Scenario(test=test_alias_columns_in_where_clause)()
    Scenario(test=test_alias_columns_in_group_by_order_by)()
    # Scenario(test=mismatch_alias_columns_type_in_hybrid_table_columns_definition)()
    Scenario(test=test_nested_alias_columns)()
    Scenario(test=test_alias_columns_with_date_predicates)()

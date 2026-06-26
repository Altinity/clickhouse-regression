from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def cte_with_filter(self):
    """
    CTE with WHERE filter on alias column.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "sum_alias", "expression": "id + value", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed, sum_alias FROM {hybrid_table} ORDER BY id",
        "WITH cte AS (SELECT id, computed, sum_alias FROM {hybrid_table} WHERE computed > 50) SELECT * FROM cte ORDER BY id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def cte_with_expression(self):
    """
    CTE followed by expression on alias column in outer SELECT.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "WITH cte AS (SELECT id, computed FROM {hybrid_table}) SELECT id, computed, computed + 10 AS adjusted FROM cte ORDER BY id",
        "WITH cte AS (SELECT id, computed FROM {hybrid_table}) SELECT id, computed * 3 AS tripled FROM cte WHERE computed > 100 ORDER BY id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def cte_with_cross_join(self):
    """
    CTE on alias column, cross-joined with main table for filtering.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "WITH sub AS (SELECT id, computed FROM {hybrid_table} WHERE computed > 10) SELECT t.id, t.computed FROM {hybrid_table} AS t, sub WHERE t.id = sub.id ORDER BY t.id",
        "WITH sub AS (SELECT id AS sub_id, computed AS sub_computed FROM {hybrid_table} WHERE id < 5) SELECT t.id, t.computed, sub.sub_computed FROM {hybrid_table} AS t, sub WHERE t.id = sub.sub_id ORDER BY t.id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def cte_with_group_by(self):
    """
    CTE with GROUP BY and aggregation on alias column.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "year_month", "expression": "toYYYYMM(date_col)", "hybrid_type": "UInt32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed, year_month FROM {hybrid_table} ORDER BY id",
        "WITH monthly AS (SELECT year_month, sum(computed) AS total, count() AS cnt FROM {hybrid_table} GROUP BY year_month) SELECT * FROM monthly ORDER BY year_month",
        "WITH monthly AS (SELECT year_month, sum(computed) AS total FROM {hybrid_table} GROUP BY year_month) SELECT year_month, total FROM monthly WHERE total > 100 ORDER BY year_month",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def cte_with_order_by(self):
    """
    CTE with ORDER BY on alias column (no LIMIT).
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "WITH ranked AS (SELECT id, computed FROM {hybrid_table} ORDER BY computed DESC) SELECT * FROM ranked ORDER BY id",
        "WITH ranked AS (SELECT id, computed FROM {hybrid_table} ORDER BY computed ASC) SELECT id, computed FROM ranked ORDER BY id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def cte_with_limit(self):
    """
    CTE with LIMIT inside (no ORDER BY).
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "WITH limited AS (SELECT id, computed FROM {hybrid_table} LIMIT 10) SELECT * FROM limited ORDER BY id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def cte_with_order_by_and_limit(self):
    """
    CTE with both ORDER BY and LIMIT inside.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "WITH ranked AS (SELECT id, computed FROM {hybrid_table} ORDER BY computed DESC LIMIT 10) SELECT * FROM ranked ORDER BY id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def cte_multiple(self):
    """
    Multiple CTEs in a single query referencing alias columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "WITH high AS (SELECT id, computed FROM {hybrid_table} WHERE computed > 1000), low AS (SELECT id, computed FROM {hybrid_table} WHERE computed <= 1000) SELECT 'high' AS seg, count() AS cnt FROM high UNION ALL SELECT 'low' AS seg, count() AS cnt FROM low",
        "WITH src AS (SELECT id, computed FROM {hybrid_table}), stats AS (SELECT avg(computed) AS avg_c FROM src) SELECT src.id, src.computed FROM src, stats WHERE src.computed > stats.avg_c ORDER BY src.id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
def double_nested_subquery(self):
    """
    Double-nested subqueries with alias columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "SELECT * FROM (SELECT * FROM (SELECT id, computed FROM {hybrid_table} WHERE computed > 10) inner_q WHERE inner_q.computed < 10000) outer_q ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE id IN (SELECT id FROM (SELECT id, computed FROM {hybrid_table} WHERE computed > 100) sub) ORDER BY id",
    ]
    order_by = "(date_col, id)"
    partition_by = "toYYYYMM(date_col)"

    outline(
        self,
        base_columns=base_columns,
        alias_columns=alias_columns,
        watermark=watermark,
        expected=expected,
        test_queries=test_queries,
        order_by=order_by,
        partition_by=partition_by,
    )


@TestScenario
@Requirements(RQ_Ice_HybridAlias_QueryContext("1.0"))
@Name("subquery nested")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test CTE and nested subqueries with alias columns."""
    Scenario(run=cte_with_filter)
    Scenario(run=cte_with_expression)
    Scenario(run=cte_with_cross_join)
    Scenario(run=cte_with_group_by)
    Scenario(run=cte_with_order_by)
    Scenario(run=cte_with_limit)
    Scenario(run=cte_with_order_by_and_limit)
    Scenario(run=cte_multiple)
    Scenario(run=double_nested_subquery)

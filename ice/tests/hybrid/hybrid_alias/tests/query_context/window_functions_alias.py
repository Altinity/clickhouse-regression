from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def window_row_number_on_alias(self):
    """
    Test window functions (row_number, rank) applied to alias columns.
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
        "SELECT id, computed, row_number() OVER (ORDER BY computed) AS rn FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, rank() OVER (ORDER BY computed DESC) AS rnk FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, dense_rank() OVER (ORDER BY computed) AS drnk FROM {hybrid_table} ORDER BY id",
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
def window_aggregate_on_alias(self):
    """
    Test window aggregate functions (sum, avg) OVER on alias columns.
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
        "SELECT id, computed, sum(computed) OVER () AS total FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, avg(computed) OVER (PARTITION BY year_month) AS monthly_avg FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, min(computed) OVER (PARTITION BY year_month) AS monthly_min, max(computed) OVER (PARTITION BY year_month) AS monthly_max FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, sum(computed) OVER (ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total FROM {hybrid_table} ORDER BY id",
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
def window_lead_lag_on_alias(self):
    """
    Test lead/lag window functions on alias columns.
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
        "SELECT id, computed, lagInFrame(computed, 1, 0) OVER (ORDER BY id) AS prev_computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, leadInFrame(computed, 1, 0) OVER (ORDER BY id) AS next_computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, computed - lagInFrame(computed, 1, 0) OVER (ORDER BY id) AS diff_from_prev FROM {hybrid_table} ORDER BY id",
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
@Name("window functions alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test window functions (row_number, rank, sum OVER, lag/lead) on alias columns."""
    Scenario(run=window_row_number_on_alias)
    Scenario(run=window_aggregate_on_alias)
    Scenario(run=window_lead_lag_on_alias)

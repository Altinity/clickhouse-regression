from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def group_by_single_alias(self):
    """
    Test GROUP BY on a single alias column.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "year_month", "expression": "toYYYYMM(date_col)", "hybrid_type": "UInt32"},
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, computed, year_month FROM {hybrid_table} ORDER BY id",
        "SELECT year_month, count() AS cnt FROM {hybrid_table} GROUP BY year_month ORDER BY year_month",
        "SELECT year_month, sum(computed) AS total FROM {hybrid_table} GROUP BY year_month ORDER BY year_month",
        "SELECT year_month, avg(computed) AS avg_val, min(computed) AS min_val, max(computed) AS max_val FROM {hybrid_table} GROUP BY year_month ORDER BY year_month",
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
def group_by_multiple_aliases(self):
    """
    Test GROUP BY on multiple alias columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "year_val", "expression": "toYear(date_col)", "hybrid_type": "UInt16"},
        {"name": "month_val", "expression": "toMonth(date_col)", "hybrid_type": "UInt8"},
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, computed, year_val, month_val FROM {hybrid_table} ORDER BY id",
        "SELECT year_val, month_val, count() AS cnt FROM {hybrid_table} GROUP BY year_val, month_val ORDER BY year_val, month_val",
        "SELECT year_val, month_val, sum(computed) AS total FROM {hybrid_table} GROUP BY year_val, month_val ORDER BY year_val, month_val",
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
@Name("group by alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test GROUP BY on single and multiple alias columns."""
    Scenario(run=group_by_single_alias)
    Scenario(run=group_by_multiple_aliases)

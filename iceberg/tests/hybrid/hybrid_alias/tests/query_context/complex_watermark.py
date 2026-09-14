from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def and_or_watermark(self):
    """
    Test complex AND/OR watermark predicate combining base and alias columns.
    Watermark: date_col >= '2025-01-15' AND value > 100.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {
        "left_predicate": "date_col >= '2025-01-15' AND value > 100",
        "right_predicate": "date_col < '2025-01-15' OR value <= 100",
    }
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
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
def mixed_base_alias_watermark(self):
    """
    Test watermark predicate mixing base column and alias column.
    Watermark: date_col >= '2025-01-15' AND computed > 200.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {
        "left_predicate": "date_col >= '2025-01-15' AND computed > 200",
        "right_predicate": "date_col < '2025-01-15' OR computed <= 200",
    }
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
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
@Name("complex watermark")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test complex AND/OR watermark predicates combining base and alias columns."""
    Scenario(run=and_or_watermark)
    Scenario(run=mixed_base_alias_watermark)

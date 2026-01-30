from testflows.core import *
from ...outline import outline


@TestScenario
def round_precision_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: rounded_precision ALIAS round(value, 2)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Float64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "rounded_precision", "expression": "round(value, 2)", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT rounded_precision FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, rounded_precision FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, rounded_precision FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("round precision alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: rounded_precision ALIAS round(value, 2)."""
    Scenario(run=round_precision_alias)

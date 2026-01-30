from testflows.core import *
from ...outline import outline


@TestScenario
def sqrt_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: sqrt_value ALIAS sqrt(value)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int16"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "sqrt_value", "expression": "sqrt(value)", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT sqrt_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sqrt_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sqrt_value FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("sqrt alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: sqrt_value ALIAS sqrt(value)."""
    Scenario(run=sqrt_alias)

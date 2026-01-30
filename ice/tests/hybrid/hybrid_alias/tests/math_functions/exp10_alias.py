from testflows.core import *
from ...outline import outline


@TestScenario
def exp10_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: exp10_value ALIAS exp10(value)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Float32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "exp10_value", "expression": "exp10(value)", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT exp10_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, exp10_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, exp10_value FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("exp10 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: exp10_value ALIAS exp10(value)."""
    Scenario(run=exp10_alias)

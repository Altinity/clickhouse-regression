from testflows.core import *
from ...outline import outline


@TestScenario
def conditional_with_math(self):
    """
    Define parameters for test case and call main outline.
    Test alias: conditional_math ALIAS if(value > 0, sqrt(value), abs(value))
    Conditional expression with math functions.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "conditional_math", "expression": "if(value > 0, sqrt(value), abs(value))", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT conditional_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, conditional_math FROM {hybrid_table} ORDER BY id",
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
@Name("conditional with math")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: conditional_math ALIAS if(value > 0, sqrt(value), abs(value))."""
    Scenario(run=conditional_with_math)

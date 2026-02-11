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
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
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
def conditional_with_math_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: conditional_math ALIAS if(value > 0, sqrt(value), abs(value))
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "conditional_math", "expression": "if(value > 0, sqrt(value), abs(value))", "hybrid_type": "Float64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "conditional_math >= 50.0", "right_predicate": "conditional_math < 50.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT conditional_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, conditional_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, conditional_math FROM {hybrid_table} WHERE conditional_math >= 50.0 ORDER BY id",
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
    Scenario(run=conditional_with_math_in_watermark)

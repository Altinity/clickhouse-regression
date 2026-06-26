from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def nested_conditional_arithmetic(self):
    """
    Define parameters for test case and call main outline.
    Test alias: nested_conditional ALIAS multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)
    MultiIf with arithmetic operations.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "nested_conditional",
            "expression": "multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)",
            "hybrid_type": "Int64",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT nested_conditional FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nested_conditional FROM {hybrid_table} ORDER BY id",
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
def nested_conditional_arithmetic_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: nested_conditional ALIAS multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "nested_conditional",
            "expression": "multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)",
            "hybrid_type": "Int64",
        },
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "nested_conditional >= 100", "right_predicate": "nested_conditional < 100"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT nested_conditional FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nested_conditional FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nested_conditional FROM {hybrid_table} WHERE nested_conditional >= 100 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_ComplexExpression("1.0"))
@Name("nested conditional arithmetic")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: nested_conditional ALIAS multiIf(value < 10, value * 2, value < 50, value * 3, value * 4)."""
    Scenario(run=nested_conditional_arithmetic)
    Scenario(run=nested_conditional_arithmetic_in_watermark)

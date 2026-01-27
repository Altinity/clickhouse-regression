from testflows.core import *
from ...outline import outline


@TestScenario
def array_sum_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_sum ALIAS arraySum(array_col)
    Sum of array elements.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array_col", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_sum", "expression": "arraySum(array_col)", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_sum FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_sum FROM {hybrid_table} ORDER BY id",
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
def array_sum_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_sum ALIAS arraySum(array_col)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array_col", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_sum", "expression": "arraySum(array_col)", "hybrid_type": "Int64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "array_sum >= 100", "right_predicate": "array_sum < 100"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_sum FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_sum FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_sum FROM {hybrid_table} WHERE array_sum >= 100 ORDER BY id",
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
@Name("array sum alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: array_sum ALIAS arraySum(array_col)."""
    Scenario(run=array_sum_alias)
    Scenario(run=array_sum_alias_in_watermark)

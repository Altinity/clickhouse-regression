from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def array_concat_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_concat ALIAS arrayConcat(array1, array2)
    Concatenate two arrays.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array1", "datatype": "Array(Int32)"},
        {"name": "array2", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_concat", "expression": "arrayConcat(array1, array2)", "hybrid_type": "Array(Int32)"},
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_concat FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_concat FROM {hybrid_table} ORDER BY id",
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
def array_concat_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_concat ALIAS arrayConcat(array1, array2)
    Using alias column length in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array1", "datatype": "Array(Int32)"},
        {"name": "array2", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_concat", "expression": "arrayConcat(array1, array2)", "hybrid_type": "Array(Int32)"},
    ]
    # Use alias column length in watermark predicates (can't compare arrays directly)
    watermark = {"left_predicate": "length(array_concat) >= 6", "right_predicate": "length(array_concat) < 6"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_concat FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_concat FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_concat FROM {hybrid_table} WHERE length(array_concat) >= 6 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_ArrayFunction("1.0"))
@Name("array concat alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: array_concat ALIAS arrayConcat(array1, array2)."""
    Scenario(run=array_concat_alias)
    Scenario(run=array_concat_alias_in_watermark)

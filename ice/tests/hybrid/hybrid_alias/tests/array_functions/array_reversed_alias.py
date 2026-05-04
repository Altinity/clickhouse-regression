from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def array_reversed_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_reversed ALIAS arrayReverse(array_col)
    Reversed array.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array_col", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_reversed", "expression": "arrayReverse(array_col)", "hybrid_type": "Array(Int32)"},
    ]
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_reversed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_reversed FROM {hybrid_table} ORDER BY id",
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
def array_reversed_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_reversed ALIAS arrayReverse(array_col)
    Using alias column length in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array_col", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_reversed", "expression": "arrayReverse(array_col)", "hybrid_type": "Array(Int32)"},
    ]
    # Use alias column length in watermark predicates (can't compare arrays directly)
    watermark = {"left_predicate": "length(array_reversed) >= 5", "right_predicate": "length(array_reversed) < 5"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_reversed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_reversed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_reversed FROM {hybrid_table} WHERE length(array_reversed) >= 5 ORDER BY id",
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
@Name("array reversed alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: array_reversed ALIAS arrayReverse(array_col)."""
    Scenario(run=array_reversed_alias)
    Scenario(run=array_reversed_alias_in_watermark)

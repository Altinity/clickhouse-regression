from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def array_first_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_first ALIAS arrayElement(array_col, 1)
    First element of array.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array_col", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_first", "expression": "arrayElement(array_col, 1)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-05-12'", "right_predicate": "date_col < '2013-05-12'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_first FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_first FROM {hybrid_table} ORDER BY id",
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
def array_first_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_first ALIAS arrayElement(array_col, 1)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array_col", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_first", "expression": "arrayElement(array_col, 1)", "hybrid_type": "Int32"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "array_first >= 0", "right_predicate": "array_first < 0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_first FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_first FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_first FROM {hybrid_table} WHERE array_first >= 0 ORDER BY id",
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
@Name("array first alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: array_first ALIAS arrayElement(array_col, 1)."""
    Scenario(run=array_first_alias)
    Scenario(run=array_first_alias_in_watermark)

from testflows.core import *
from ...outline import outline


@TestScenario
def is_greater_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_greater ALIAS value > 0
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "UInt16"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_greater", "expression": "value > 0", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_greater FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_greater FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_greater FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def is_greater_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_greater ALIAS value > 0
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "UInt16"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_greater", "expression": "value > 0", "hybrid_type": "UInt8"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "is_greater = 1", "right_predicate": "is_greater = 0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_greater FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_greater FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_greater FROM {hybrid_table} WHERE is_greater = 1 ORDER BY id",
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
@Name("is greater alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: is_greater ALIAS value > 0."""
    Scenario(run=is_greater_alias)
    Scenario(run=is_greater_alias_in_watermark)

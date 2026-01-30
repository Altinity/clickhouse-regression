from testflows.core import *
from ...outline import outline


@TestScenario
def negative_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: negative ALIAS abs(value) - abs(value * 2)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "negative", "expression": "abs(value) - abs(value * 2)", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2004-04-16'", "right_predicate": "date_col < '2004-04-16'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT negative FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, negative FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, negative FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def negative_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: negative ALIAS abs(value) - abs(value * 2)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "negative", "expression": "abs(value) - abs(value * 2)", "hybrid_type": "Int64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "negative < 0", "right_predicate": "negative >= 0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT negative FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, negative FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, negative FROM {hybrid_table} WHERE negative < 0 ORDER BY id",
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
@Name("negative alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: negative ALIAS abs(value) - abs(value * 2)"""
    Scenario(run=negative_alias)
    Scenario(run=negative_alias_in_watermark)

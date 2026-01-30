from testflows.core import *
from ...outline import outline


@TestScenario
def is_like_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_like ALIAS name LIKE '%test%'
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_like", "expression": "name LIKE '%test%'", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_like FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_like FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_like FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def is_like_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_like ALIAS name LIKE '%test%'
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_like", "expression": "name LIKE '%test%'", "hybrid_type": "UInt8"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "is_like = 1", "right_predicate": "is_like = 0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_like FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_like FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_like FROM {hybrid_table} WHERE is_like = 1 ORDER BY id",
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
@Name("is like alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: is_like ALIAS name LIKE '%test%'."""
    Scenario(run=is_like_alias)
    Scenario(run=is_like_alias_in_watermark)

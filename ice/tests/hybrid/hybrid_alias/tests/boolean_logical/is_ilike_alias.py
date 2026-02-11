from testflows.core import *
from ...outline import outline


@TestScenario
def is_ilike_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_ilike ALIAS name ILIKE '%TEST%'
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "UInt8"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_ilike", "expression": "name ILIKE '%TEST%'", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_ilike FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_ilike FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_ilike FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def is_ilike_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_ilike ALIAS name ILIKE '%TEST%'
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "UInt8"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_ilike", "expression": "name ILIKE '%TEST%'", "hybrid_type": "UInt8"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "is_ilike = 1", "right_predicate": "is_ilike = 0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_ilike FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_ilike FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_ilike FROM {hybrid_table} WHERE is_ilike = 1 ORDER BY id",
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
@Name("is ilike alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: is_ilike ALIAS name ILIKE '%TEST%'."""
    Scenario(run=is_ilike_alias)
    Scenario(run=is_ilike_alias_in_watermark)

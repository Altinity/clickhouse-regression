from testflows.core import *
from ...outline import outline


@TestScenario
def transform_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: transformed ALIAS transform(value, [0, -2147483648, 2147483647], ['a', 'b', 'c'], 'default')
    Uses 0, min (Int32), and max (Int32) values to test transform function with boundary values.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "transformed",
            "expression": "transform(value, [0, -2147483648, 2147483647], ['a', 'b', 'c'], 'default')",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT transformed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, transformed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, transformed FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def transform_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: transformed ALIAS transform(value, [0, -2147483648, 2147483647], ['a', 'b', 'c'], 'default')
    Using alias column length in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "transformed",
            "expression": "transform(value, [0, -2147483648, 2147483647], ['a', 'b', 'c'], 'default')",
            "hybrid_type": "String",
        },
    ]
    # Use alias column length in watermark predicates (can't compare strings directly)
    watermark = {"left_predicate": "length(transformed) >= 7", "right_predicate": "length(transformed) < 7"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT transformed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, transformed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, transformed FROM {hybrid_table} WHERE length(transformed) >= 7 ORDER BY id",
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
@Name("transform alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: transformed ALIAS transform(value, [0, -2147483648, 2147483647], ['a', 'b', 'c'], 'default')."""
    Scenario(run=transform_alias)
    Scenario(run=transform_alias_in_watermark)

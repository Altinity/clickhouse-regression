from testflows.core import *
from ...outline import outline


@TestScenario
def toString_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_str ALIAS toString(value)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_str", "expression": "toString(value)", "hybrid_type": "String"},
    ]
    watermark = {"left_predicate": "date_col >= '2004-04-16'", "right_predicate": "date_col < '2004-04-16'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_str FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_str FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_str FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toString_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_str ALIAS toString(value)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_str", "expression": "toString(value)", "hybrid_type": "String"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "value_str >= '1000'", "right_predicate": "value_str < '1000'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_str FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_str FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_str FROM {hybrid_table} WHERE value_str >= '1000' ORDER BY id",
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
@Name("toString alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_str ALIAS toString(value)."""
    Scenario(run=toString_alias)
    Scenario(run=toString_alias_in_watermark)

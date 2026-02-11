from testflows.core import *
from ...outline import outline


@TestScenario
def toNullable_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: nullable_value ALIAS toNullable(value)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "nullable_value", "expression": "toNullable(value)", "hybrid_type": "Nullable(Int32)"},
    ]
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT nullable_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nullable_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nullable_value FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toNullable_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: nullable_value ALIAS toNullable(value)
    Using alias column null check in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "nullable_value", "expression": "toNullable(value)", "hybrid_type": "Nullable(Int32)"},
    ]
    # Use alias column null check in watermark predicates
    watermark = {"left_predicate": "isNull(nullable_value) = 0", "right_predicate": "isNull(nullable_value) = 1"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT nullable_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nullable_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nullable_value FROM {hybrid_table} WHERE isNull(nullable_value) = 0 ORDER BY id",
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
@Name("toNullable alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: nullable_value ALIAS toNullable(value)."""
    Scenario(run=toNullable_alias)
    Scenario(run=toNullable_alias_in_watermark)

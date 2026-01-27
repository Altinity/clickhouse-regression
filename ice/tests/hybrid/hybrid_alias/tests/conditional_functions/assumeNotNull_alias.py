from testflows.core import *
from ...outline import outline


@TestScenario
def assumeNotNull_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: assumed_not_null ALIAS assumeNotNull(nullable_value)
    Note: This requires a nullable source column
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "nullable_value", "datatype": "Nullable(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "assumed_not_null", "expression": "assumeNotNull(nullable_value)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-05-12'", "right_predicate": "date_col < '2013-05-12'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, nullable_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT assumed_not_null FROM {hybrid_table} ORDER BY id",
        "SELECT id, nullable_value, assumed_not_null FROM {hybrid_table} ORDER BY id",
        "SELECT id, nullable_value, assumed_not_null FROM {hybrid_table} WHERE nullable_value > 5000 ORDER BY id",
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
def assumeNotNull_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: assumed_not_null ALIAS assumeNotNull(nullable_value)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "nullable_value", "datatype": "Nullable(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "assumed_not_null", "expression": "assumeNotNull(nullable_value)", "hybrid_type": "Int32"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "assumed_not_null >= 100", "right_predicate": "assumed_not_null < 100"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, nullable_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT assumed_not_null FROM {hybrid_table} ORDER BY id",
        "SELECT id, nullable_value, assumed_not_null FROM {hybrid_table} ORDER BY id",
        "SELECT id, nullable_value, assumed_not_null FROM {hybrid_table} WHERE assumed_not_null >= 100 ORDER BY id",
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
@Name("assumeNotNull alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: assumed_not_null ALIAS assumeNotNull(nullable_value)."""
    Scenario(run=assumeNotNull_alias)
    Scenario(run=assumeNotNull_alias_in_watermark)

from testflows.core import *
from ...outline import outline


@TestScenario
def toDayOfWeek_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: day_of_week ALIAS toDayOfWeek(date_col)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "day_of_week", "expression": "toDayOfWeek(date_col)", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT day_of_week FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, day_of_week FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, day_of_week FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toDayOfWeek_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: day_of_week ALIAS toDayOfWeek(date_col)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "day_of_week", "expression": "toDayOfWeek(date_col)", "hybrid_type": "UInt8"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "day_of_week >= 4", "right_predicate": "day_of_week < 4"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT day_of_week FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, day_of_week FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, day_of_week FROM {hybrid_table} WHERE day_of_week >= 4 ORDER BY id",
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
@Name("toDayOfWeek alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: day_of_week ALIAS toDayOfWeek(date_col)."""
    Scenario(run=toDayOfWeek_alias)
    Scenario(run=toDayOfWeek_alias_in_watermark)

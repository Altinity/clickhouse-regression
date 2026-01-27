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
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
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
@Name("toDayOfWeek alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: day_of_week ALIAS toDayOfWeek(date_col)."""
    Scenario(run=toDayOfWeek_alias)

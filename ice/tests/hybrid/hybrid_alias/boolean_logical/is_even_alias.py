from testflows.core import *
from ..outline import outline


@TestScenario
def is_even_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_even ALIAS value % 2 = 0
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int8"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_even", "expression": "value % 2 = 0", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_even FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_even FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_even FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("is even alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: is_even ALIAS value % 2 = 0."""
    Scenario(run=is_even_alias)

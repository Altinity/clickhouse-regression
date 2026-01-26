from testflows.core import *
from ..outline import outline


@TestScenario
def is_valid_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: is_valid ALIAS value > 0 AND value < 100
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Float32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "is_valid", "expression": "value > 0 AND value < 100", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT is_valid FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_valid FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, is_valid FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("is valid alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: is_valid ALIAS value > 0 AND value < 100."""
    Scenario(run=is_valid_alias)

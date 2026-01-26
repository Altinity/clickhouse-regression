from testflows.core import *
from ..outline import outline


@TestScenario
def default_int32(self):
    """
    Define parameters for test case and call main outline.
    Test alias: default_int32 ALIAS 50000
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "default_int32", "expression": "toInt32(50000)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT default_int32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_int32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_int32 FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("default int32")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: default_int32 ALIAS 50000."""
    Scenario(run=default_int32)

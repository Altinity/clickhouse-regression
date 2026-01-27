from testflows.core import *
from ...outline import outline


@TestScenario
def toInt32_fromInt64_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_int32 ALIAS toInt32(big_value) - Shrinking conversion from Int64 to Int32
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "big_value", "datatype": "Int64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_int32", "expression": "toInt32(big_value)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, big_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_int32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, value_int32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, value_int32 FROM {hybrid_table} WHERE big_value > 5000 ORDER BY id",
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
@Name("toInt32 from Int64 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_int32 ALIAS toInt32(big_value) - Shrinking conversion from Int64."""
    Scenario(run=toInt32_fromInt64_alias)

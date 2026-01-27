from testflows.core import *
from ...outline import outline


@TestScenario
def toInt8_fromInt16_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_int8 ALIAS toInt8(small_value) - Shrinking conversion from Int16 to Int8
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "small_value", "datatype": "Int16"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_int8", "expression": "toInt8(small_value)", "hybrid_type": "Int8"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, small_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_int8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, small_value, value_int8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, small_value, value_int8 FROM {hybrid_table} WHERE small_value > 50 ORDER BY id",
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
@Name("toInt8 from Int16 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_int8 ALIAS toInt8(small_value) - Shrinking conversion from Int16."""
    Scenario(run=toInt8_fromInt16_alias)

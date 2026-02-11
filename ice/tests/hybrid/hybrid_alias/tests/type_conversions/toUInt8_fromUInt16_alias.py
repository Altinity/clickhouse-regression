from testflows.core import *
from ...outline import outline


@TestScenario
def toUInt8_fromUInt16_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_uint8 ALIAS toUInt8(small_value) - Shrinking conversion from UInt16 to UInt8
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "small_value", "datatype": "UInt16"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_uint8", "expression": "toUInt8(small_value)", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, small_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_uint8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, small_value, value_uint8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, small_value, value_uint8 FROM {hybrid_table} WHERE small_value > 50 ORDER BY id",
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
@Name("toUInt8 from UInt16 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_uint8 ALIAS toUInt8(small_value) - Shrinking conversion from UInt16."""
    Scenario(run=toUInt8_fromUInt16_alias)

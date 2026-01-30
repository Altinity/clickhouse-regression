from testflows.core import *
from ...outline import outline


@TestScenario
def countDigits_uint32_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: digit_count_uint32 ALIAS countDigits(uint_value)
    Count digits in UInt32 value.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "uint_value", "datatype": "UInt32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "digit_count_uint32", "expression": "countDigits(uint_value)", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, uint_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT digit_count_uint32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, uint_value, digit_count_uint32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, uint_value, digit_count_uint32 FROM {hybrid_table} WHERE uint_value > 5000 ORDER BY id",
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
@Name("countDigits uint32 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: digit_count_uint32 ALIAS countDigits(uint_value) (UInt32)."""
    Scenario(run=countDigits_uint32_alias)

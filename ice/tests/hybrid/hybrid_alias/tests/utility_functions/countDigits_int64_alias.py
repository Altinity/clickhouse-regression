from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def countDigits_int64_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: digit_count_int64 ALIAS countDigits(big_value)
    Count digits in Int64 value.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "big_value", "datatype": "Int64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "digit_count_int64", "expression": "countDigits(big_value)", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, big_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT digit_count_int64 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, digit_count_int64 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, digit_count_int64 FROM {hybrid_table} WHERE big_value > 5000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_UtilityFunction("1.0"))
@Name("countDigits int64 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: digit_count_int64 ALIAS countDigits(big_value) (Int64)."""
    Scenario(run=countDigits_int64_alias)

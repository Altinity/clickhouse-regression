from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def toUInt32_fromUInt64_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_uint32 ALIAS toUInt32(big_value) - Shrinking conversion from UInt64 to UInt32
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "big_value", "datatype": "UInt64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_uint32", "expression": "toUInt32(big_value)", "hybrid_type": "UInt32"},
    ]
    watermark = {"left_predicate": "date_col >= '2004-04-16'", "right_predicate": "date_col < '2004-04-16'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, big_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_uint32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, value_uint32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, value_uint32 FROM {hybrid_table} WHERE big_value > 5000 ORDER BY id",
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
def toUInt32_fromUInt64_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_uint32 ALIAS toUInt32(big_value) - Shrinking conversion from UInt64 to UInt32
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "big_value", "datatype": "UInt64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_uint32", "expression": "toUInt32(big_value)", "hybrid_type": "UInt32"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "value_uint32 >= 5000", "right_predicate": "value_uint32 < 5000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, big_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_uint32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, value_uint32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, big_value, value_uint32 FROM {hybrid_table} WHERE value_uint32 >= 5000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_TypeConversion("1.0"))
@Name("toUInt32 from UInt64 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_uint32 ALIAS toUInt32(big_value) - Shrinking conversion from UInt64."""
    Scenario(run=toUInt32_fromUInt64_alias)
    Scenario(run=toUInt32_fromUInt64_alias_in_watermark)

from testflows.core import *
from ...outline import outline


@TestScenario
def toUInt8_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_uint8 ALIAS toUInt8(value)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_uint8", "expression": "toUInt8(value)", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-11-06'", "right_predicate": "date_col < '2008-11-06'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_uint8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_uint8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_uint8 FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toUInt8_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_uint8 ALIAS toUInt8(value)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_uint8", "expression": "toUInt8(value)", "hybrid_type": "UInt8"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "value_uint8 >= 50", "right_predicate": "value_uint8 < 50"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_uint8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_uint8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_uint8 FROM {hybrid_table} WHERE value_uint8 >= 50 ORDER BY id",
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
@Name("toUInt8 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_uint8 ALIAS toUInt8(value)."""
    Scenario(run=toUInt8_alias)
    Scenario(run=toUInt8_alias_in_watermark)

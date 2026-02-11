from testflows.core import *
from ...outline import outline


@TestScenario
def toInt16_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_int16 ALIAS toInt16(value)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_int16", "expression": "toInt16(value)", "hybrid_type": "Int16"},
    ]
    watermark = {"left_predicate": "date_col >= '2007-05-01'", "right_predicate": "date_col < '2007-05-01'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_int16 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_int16 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_int16 FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toInt16_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_int16 ALIAS toInt16(value)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_int16", "expression": "toInt16(value)", "hybrid_type": "Int16"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "value_int16 >= 5000", "right_predicate": "value_int16 < 5000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_int16 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_int16 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_int16 FROM {hybrid_table} WHERE value_int16 >= 5000 ORDER BY id",
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
@Name("toInt16 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_int16 ALIAS toInt16(value)."""
    Scenario(run=toInt16_alias)
    Scenario(run=toInt16_alias_in_watermark)

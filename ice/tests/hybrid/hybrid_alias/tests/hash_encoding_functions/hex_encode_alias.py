from testflows.core import *
from ...outline import outline


@TestScenario
def hex_encode_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: hex_encoded ALIAS hex(string_col)
    Hexadecimal encoding.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "string_col", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "hex_encoded", "expression": "hex(string_col)", "hybrid_type": "String"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT hex_encoded FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, hex_encoded FROM {hybrid_table} ORDER BY id",
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
@Name("hex encode alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: hex_encoded ALIAS hex(string_col)."""
    Scenario(run=hex_encode_alias)

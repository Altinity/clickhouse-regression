from testflows.core import *
from ...outline import outline


@TestScenario
def md5_hash_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: md5_hash ALIAS MD5(string_col)
    MD5 hash of string.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "string_col", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "md5_hash", "expression": "MD5(string_col)", "hybrid_type": "FixedString(16)"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT md5_hash FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, md5_hash FROM {hybrid_table} ORDER BY id",
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
@Name("md5 hash alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: md5_hash ALIAS MD5(string_col)."""
    Scenario(run=md5_hash_alias)

from testflows.core import *
from ...outline import outline


@TestScenario
def sha1_hash_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: sha1_hash ALIAS SHA1(string_col)
    SHA1 hash of string.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "string_col", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "sha1_hash", "expression": "SHA1(string_col)", "hybrid_type": "FixedString(20)"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT sha1_hash FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sha1_hash FROM {hybrid_table} ORDER BY id",
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
@Name("sha1 hash alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: sha1_hash ALIAS SHA1(string_col)."""
    Scenario(run=sha1_hash_alias)

from testflows.core import *
from ...outline import outline


@TestScenario
def json_extract_int_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: json_extract_int ALIAS JSONExtractInt(json_col, 'key')
    Extract integer from JSON.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "json_col", "datatype": "JSON"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "json_extract_int", "expression": "JSONExtractInt(json_col, 'key')", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT json_extract_int FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, json_extract_int FROM {hybrid_table} ORDER BY id",
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
@Name("json extract int alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: json_extract_int ALIAS JSONExtractInt(json_col, 'key')."""
    Scenario(run=json_extract_int_alias)

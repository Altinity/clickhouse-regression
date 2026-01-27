from testflows.core import *
from ...outline import outline


@TestScenario
def greatest_string_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: greatest_string ALIAS greatest(str1, str2, str3)
    Greatest of string values (lexicographic comparison).
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "str1", "datatype": "String"},
        {"name": "str2", "datatype": "String"},
        {"name": "str3", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "greatest_string", "expression": "greatest(str1, str2, str3)", "hybrid_type": "String"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, str1, str2, str3, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT greatest_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, str1, str2, str3, greatest_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, str1, str2, str3, greatest_string FROM {hybrid_table} WHERE id > 5 ORDER BY id",
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
@Name("greatest string alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: greatest_string ALIAS greatest(str1, str2, str3) (string values)."""
    Scenario(run=greatest_string_alias)

from testflows.core import *
from ...outline import outline


@TestScenario
def arithmetic_string_combined(self):
    """
    Define parameters for test case and call main outline.
    Test alias: score ALIAS (value * 2) + (id % 10) - length(name)
    Complex expression combining arithmetic and string functions.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "score", "expression": "(value * 2) + (id % 10) - length(name)", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, name, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT score FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, name, score FROM {hybrid_table} ORDER BY id",
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
def arithmetic_string_combined_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: score ALIAS (value * 2) + (id % 10) - length(name)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "score", "expression": "(value * 2) + (id % 10) - length(name)", "hybrid_type": "Int64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "score >= 100", "right_predicate": "score < 100"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, name, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT score FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, name, score FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, name, score FROM {hybrid_table} WHERE score >= 100 ORDER BY id",
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
@Name("arithmetic string combined")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: score ALIAS (value * 2) + (id % 10) - length(name)."""
    Scenario(run=arithmetic_string_combined)
    Scenario(run=arithmetic_string_combined_in_watermark)

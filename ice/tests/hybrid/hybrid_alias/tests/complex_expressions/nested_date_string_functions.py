from testflows.core import *
from ...outline import outline


@TestScenario
def nested_date_string_functions(self):
    """
    Define parameters for test case and call main outline.
    Test alias: formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))
    Nested date and string functions.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "formatted_date",
            "expression": "concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT formatted_date FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_col, formatted_date FROM {hybrid_table} ORDER BY id",
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
@Name("nested date string functions")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))."""
    Scenario(run=nested_date_string_functions)

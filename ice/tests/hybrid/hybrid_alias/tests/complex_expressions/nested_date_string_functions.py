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
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
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
def nested_date_string_functions_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: formatted_date ALIAS concat(toString(toYear(date_col)), '-', toString(toMonth(date_col)))
    Using alias column length in watermark predicate.
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
    # Use alias column length in watermark predicates (can't compare strings directly)
    watermark = {"left_predicate": "length(formatted_date) >= 7", "right_predicate": "length(formatted_date) < 7"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT formatted_date FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_col, formatted_date FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, formatted_date FROM {hybrid_table} WHERE length(formatted_date) >= 7 ORDER BY id",
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
    Scenario(run=nested_date_string_functions_in_watermark)

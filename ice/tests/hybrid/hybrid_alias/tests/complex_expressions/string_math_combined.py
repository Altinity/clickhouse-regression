from testflows.core import *
from ...outline import outline


@TestScenario
def string_math_combined(self):
    """
    Define parameters for test case and call main outline.
    Test alias: string_math ALIAS length(concat(toString(value), '_', toString(id)))
    String concatenation with length calculation.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "string_math",
            "expression": "length(concat(toString(value), '_', toString(id)))",
            "hybrid_type": "UInt64",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2013-05-12'", "right_predicate": "date_col < '2013-05-12'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT string_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, string_math FROM {hybrid_table} ORDER BY id",
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
def string_math_combined_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: string_math ALIAS length(concat(toString(value), '_', toString(id)))
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "string_math",
            "expression": "length(concat(toString(value), '_', toString(id)))",
            "hybrid_type": "UInt64",
        },
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "string_math >= 10", "right_predicate": "string_math < 10"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT string_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, string_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, string_math FROM {hybrid_table} WHERE string_math >= 10 ORDER BY id",
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
@Name("string math combined")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: string_math ALIAS length(concat(toString(value), '_', toString(id)))."""
    Scenario(run=string_math_combined)
    Scenario(run=string_math_combined_in_watermark)

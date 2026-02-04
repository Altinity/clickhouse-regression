from testflows.core import *
from ...outline import outline


@TestScenario
def addYears_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: date_plus_years ALIAS addYears(date_col, 1)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "date_plus_years", "expression": "addYears(date_col, 1)", "hybrid_type": "Date"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT date_plus_years FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_plus_years FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_plus_years FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def addYears_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: date_plus_years ALIAS addYears(date_col, 1)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "date_plus_years", "expression": "addYears(date_col, 1)", "hybrid_type": "Date"},
    ]
    # Use alias column in watermark predicates
    watermark = {
        "left_predicate": "date_plus_years >= '2010-01-01'",
        "right_predicate": "date_plus_years < '2010-01-01'",
    }
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT date_plus_years FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_plus_years FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_plus_years FROM {hybrid_table} WHERE date_plus_years >= '2010-01-01' ORDER BY id",
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
@Name("addYears alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: date_plus_years ALIAS addYears(date_col, 1)."""
    Scenario(run=addYears_alias)
    Scenario(run=addYears_alias_in_watermark)

from testflows.core import *
from ...outline import outline


@TestScenario
def percentage_calculation_aliases(self):
    """
    Define parameters for test case and call main outline.
    Test alias: percentage ALIAS (doubled * 100) / (value + doubled)
    Percentage calculation with aliases.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "percentage", "expression": "(doubled * 100) / (value + doubled)", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-05-12'", "right_predicate": "date_col < '2013-05-12'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, percentage FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, percentage FROM {hybrid_table} ORDER BY id",
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
def percentage_calculation_aliases_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: percentage ALIAS (doubled * 100) / (value + doubled)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "percentage", "expression": "(doubled * 100) / (value + doubled)", "hybrid_type": "Float64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "percentage >= 50.0", "right_predicate": "percentage < 50.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, percentage FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, percentage FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, percentage FROM {hybrid_table} WHERE percentage >= 50.0 ORDER BY id",
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
@Name("percentage calculation aliases")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: percentage ALIAS (doubled * 100) / (value + doubled) (percentage calculation with aliases)."""
    Scenario(run=percentage_calculation_aliases)
    Scenario(run=percentage_calculation_aliases_in_watermark)

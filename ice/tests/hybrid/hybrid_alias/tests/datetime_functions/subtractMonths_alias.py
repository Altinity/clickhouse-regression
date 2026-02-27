from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def subtractMonths_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: date_minus_months ALIAS subtractMonths(date_col, 1)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "date_minus_months", "expression": "subtractMonths(date_col, 1)", "hybrid_type": "Date"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT date_minus_months FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_minus_months FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_minus_months FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def subtractMonths_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: date_minus_months ALIAS subtractMonths(date_col, 1)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "date_minus_months", "expression": "subtractMonths(date_col, 1)", "hybrid_type": "Date"},
    ]
    # Use alias column in watermark predicates
    watermark = {
        "left_predicate": "date_minus_months >= '2010-01-01'",
        "right_predicate": "date_minus_months < '2010-01-01'",
    }
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT date_minus_months FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_minus_months FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_minus_months FROM {hybrid_table} WHERE date_minus_months >= '2010-01-01' ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_DateTimeFunction("1.0"))
@Name("subtractMonths alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: date_minus_months ALIAS subtractMonths(date_col, 1)."""
    Scenario(run=subtractMonths_alias)
    Scenario(run=subtractMonths_alias_in_watermark)

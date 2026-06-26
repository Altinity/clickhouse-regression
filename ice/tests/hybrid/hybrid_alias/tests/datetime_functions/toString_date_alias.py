from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def toString_date_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: date_string ALIAS toString(date_col)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "date_string", "expression": "toString(date_col)", "hybrid_type": "String"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-05-12'", "right_predicate": "date_col < '2013-05-12'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT date_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_string FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toString_date_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: date_string ALIAS toString(date_col)
    Using alias column length in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "date_string", "expression": "toString(date_col)", "hybrid_type": "String"},
    ]
    # Use alias column length in watermark predicates (can't compare strings directly)
    watermark = {"left_predicate": "length(date_string) >= 10", "right_predicate": "length(date_string) < 10"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT date_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, date_string FROM {hybrid_table} WHERE length(date_string) >= 10 ORDER BY id",
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
@Name("toString date alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: date_string ALIAS toString(date_col)."""
    Scenario(run=toString_date_alias)
    Scenario(run=toString_date_alias_in_watermark)

from testflows.core import *
from ...outline import outline


@TestScenario
def div_by_zero_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: div_by_zero ALIAS value / 0
    Note: This may produce infinity or errors depending on ClickHouse behavior.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "div_by_zero", "expression": "value / 0", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2012-04-28'", "right_predicate": "date_col < '2012-04-28'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT div_by_zero FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, div_by_zero FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, div_by_zero FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def div_by_zero_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: div_by_zero ALIAS value / 0
    Using alias column in watermark predicate.
    Note: This may produce infinity or errors depending on ClickHouse behavior.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "div_by_zero", "expression": "value / 0", "hybrid_type": "Float64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "isFinite(div_by_zero) = 0", "right_predicate": "isFinite(div_by_zero) = 1"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT div_by_zero FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, div_by_zero FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, div_by_zero FROM {hybrid_table} WHERE isFinite(div_by_zero) = 0 ORDER BY id",
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
@Name("div by zero alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: div_by_zero ALIAS value / 0"""
    Scenario(run=div_by_zero_alias)
    Scenario(run=div_by_zero_alias_in_watermark)

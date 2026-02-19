from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def computed_multiply(self):
    """
    Define parameters for test case and call main outline.
    Test alias: computed ALIAS value * 2
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2012-04-28'", "right_predicate": "date_col < '2012-04-28'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def computed_multiply_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: computed ALIAS value * 2
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "computed >= 10000", "right_predicate": "computed < 10000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} WHERE computed >= 10000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_Arithmetic("1.0"))
@Name("computed multiply")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: computed ALIAS value * 2"""
    Scenario(run=computed_multiply)
    Scenario(run=computed_multiply_in_watermark)

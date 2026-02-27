from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def arithmetic_with_rounding(self):
    """
    Define parameters for test case and call main outline.
    Test alias: complex_round ALIAS round((value * 1.5) / 3.0, 2)
    Arithmetic operations with rounding function.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "complex_round", "expression": "round((value * 1.5) / 3.0, 2)", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT complex_round FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, complex_round FROM {hybrid_table} ORDER BY id",
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
def arithmetic_with_rounding_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: complex_round ALIAS round((value * 1.5) / 3.0, 2)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "complex_round", "expression": "round((value * 1.5) / 3.0, 2)", "hybrid_type": "Float64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "complex_round >= 1000.0", "right_predicate": "complex_round < 1000.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT complex_round FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, complex_round FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, complex_round FROM {hybrid_table} WHERE complex_round >= 1000.0 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_ComplexExpression("1.0"))
@Name("arithmetic with rounding")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: complex_round ALIAS round((value * 1.5) / 3.0, 2)."""
    Scenario(run=arithmetic_with_rounding)
    Scenario(run=arithmetic_with_rounding_in_watermark)

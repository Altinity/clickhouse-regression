from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def pythagorean_calculation(self):
    """
    Define parameters for test case and call main outline.
    Test alias: complex_math ALIAS sqrt(pow(value, 2) + pow(id, 2))
    Pythagorean calculation with nested math functions.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "complex_math", "expression": "sqrt(pow(value, 2) + pow(id, 2))", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-05-12'", "right_predicate": "date_col < '2013-05-12'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT complex_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, complex_math FROM {hybrid_table} ORDER BY id",
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
def pythagorean_calculation_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: complex_math ALIAS sqrt(pow(value, 2) + pow(id, 2))
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "complex_math", "expression": "sqrt(pow(value, 2) + pow(id, 2))", "hybrid_type": "Float64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "complex_math >= 1000.0", "right_predicate": "complex_math < 1000.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT complex_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, complex_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, complex_math FROM {hybrid_table} WHERE complex_math >= 1000.0 ORDER BY id",
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
@Name("pythagorean calculation")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: complex_math ALIAS sqrt(pow(value, 2) + pow(id, 2))."""
    Scenario(run=pythagorean_calculation)
    Scenario(run=pythagorean_calculation_in_watermark)

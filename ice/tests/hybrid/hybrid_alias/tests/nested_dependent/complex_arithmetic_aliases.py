from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def complex_arithmetic_aliases(self):
    """
    Define parameters for test case and call main outline.
    Test alias: nested_math ALIAS (doubled + quadrupled) * 2
    Complex arithmetic expression with aliases.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
        {"name": "nested_math", "expression": "(doubled + quadrupled) * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, nested_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, nested_math FROM {hybrid_table} ORDER BY id",
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
def complex_arithmetic_aliases_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: nested_math ALIAS (doubled + quadrupled) * 2
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
        {"name": "nested_math", "expression": "(doubled + quadrupled) * 2", "hybrid_type": "Int64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "nested_math >= 1000", "right_predicate": "nested_math < 1000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, nested_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, nested_math FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, nested_math FROM {hybrid_table} WHERE nested_math >= 1000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_NestedDependent("1.0"))
@Name("complex arithmetic aliases")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: nested_math ALIAS (doubled + quadrupled) * 2 (complex arithmetic with aliases)."""
    Scenario(run=complex_arithmetic_aliases)
    Scenario(run=complex_arithmetic_aliases_in_watermark)

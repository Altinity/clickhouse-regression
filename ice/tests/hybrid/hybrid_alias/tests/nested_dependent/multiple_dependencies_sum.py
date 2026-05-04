from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def multiple_dependencies_sum(self):
    """
    Define parameters for test case and call main outline.
    Test alias: sum_all ALIAS id + value + doubled + quadrupled
    Multiple dependencies: alias depends on multiple other aliases.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
        {"name": "sum_all", "expression": "id + value + doubled + quadrupled", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, sum_all FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, sum_all FROM {hybrid_table} ORDER BY id",
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
def multiple_dependencies_sum_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: sum_all ALIAS id + value + doubled + quadrupled
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
        {"name": "sum_all", "expression": "id + value + doubled + quadrupled", "hybrid_type": "Int64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "sum_all >= 500", "right_predicate": "sum_all < 500"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, sum_all FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, sum_all FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sum_all FROM {hybrid_table} WHERE sum_all >= 500 ORDER BY id",
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
@Name("multiple dependencies sum")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: sum_all ALIAS id + value + doubled + quadrupled (multiple dependencies)."""
    Scenario(run=multiple_dependencies_sum)
    Scenario(run=multiple_dependencies_sum_in_watermark)

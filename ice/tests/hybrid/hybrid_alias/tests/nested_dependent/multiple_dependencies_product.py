from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def multiple_dependencies_product(self):
    """
    Define parameters for test case and call main outline.
    Test alias: product_all ALIAS doubled * quadrupled
    Multiple dependencies: alias depends on multiple other aliases (product).
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
        {"name": "product_all", "expression": "doubled * quadrupled", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, product_all FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, product_all FROM {hybrid_table} ORDER BY id",
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
def multiple_dependencies_product_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: product_all ALIAS doubled * quadrupled
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
        {"name": "product_all", "expression": "doubled * quadrupled", "hybrid_type": "Int64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "product_all >= 10000", "right_predicate": "product_all < 10000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, product_all FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, product_all FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, product_all FROM {hybrid_table} WHERE product_all >= 10000 ORDER BY id",
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
@Name("multiple dependencies product")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: product_all ALIAS doubled * quadrupled (multiple dependencies)."""
    Scenario(run=multiple_dependencies_product)
    Scenario(run=multiple_dependencies_product_in_watermark)

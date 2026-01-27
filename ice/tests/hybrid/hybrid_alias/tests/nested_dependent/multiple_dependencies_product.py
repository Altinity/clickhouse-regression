from testflows.core import *
from ...outline import outline


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
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
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
@Name("multiple dependencies product")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: product_all ALIAS doubled * quadrupled (multiple dependencies)."""
    Scenario(run=multiple_dependencies_product)

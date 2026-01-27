from testflows.core import *
from ...outline import outline


@TestScenario
def array_product_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: array_product ALIAS arrayProduct(array_col)
    Product of array elements.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "array_col", "datatype": "Array(Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "array_product", "expression": "arrayProduct(array_col)", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT array_product FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, array_product FROM {hybrid_table} ORDER BY id",
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
@Name("array product alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: array_product ALIAS arrayProduct(array_col)."""
    Scenario(run=array_product_alias)

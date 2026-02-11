from testflows.core import *
from ...outline import outline


@TestScenario
def product_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: product ALIAS value1 * value2
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "product", "expression": "value1 * value2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-08-05'", "right_predicate": "date_col < '2013-08-05'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT product FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, product FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, product FROM {hybrid_table} WHERE value1 > 5000 ORDER BY id",
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
def product_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: product ALIAS value1 * value2
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "product", "expression": "value1 * value2", "hybrid_type": "Int64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "product >= 1000000", "right_predicate": "product < 1000000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT product FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, product FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, product FROM {hybrid_table} WHERE product >= 1000000 ORDER BY id",
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
@Name("product alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: product ALIAS value1 * value2"""
    Scenario(run=product_alias)
    Scenario(run=product_alias_in_watermark)

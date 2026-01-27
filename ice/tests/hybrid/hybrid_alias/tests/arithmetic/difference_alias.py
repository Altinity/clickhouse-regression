from testflows.core import *
from ...outline import outline


@TestScenario
def difference_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: difference ALIAS value1 - value2
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "difference", "expression": "value1 - value2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-11-06'", "right_predicate": "date_col < '2008-11-06'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT difference FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, difference FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, difference FROM {hybrid_table} WHERE value1 > 5000 ORDER BY id",
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
def difference_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: difference ALIAS value1 - value2
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "difference", "expression": "value1 - value2", "hybrid_type": "Int64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "difference >= 0", "right_predicate": "difference < 0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT difference FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, difference FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, difference FROM {hybrid_table} WHERE difference >= 0 ORDER BY id",
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
@Name("difference alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: difference ALIAS value1 - value2"""
    Scenario(run=difference_alias)
    Scenario(run=difference_alias_in_watermark)

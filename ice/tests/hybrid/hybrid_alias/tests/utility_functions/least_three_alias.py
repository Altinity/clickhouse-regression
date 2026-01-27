from testflows.core import *
from ...outline import outline


@TestScenario
def least_three_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: least_three ALIAS least(val1, val2, val3)
    Least of three numeric values.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "val1", "datatype": "Int32"},
        {"name": "val2", "datatype": "Int32"},
        {"name": "val3", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "least_three", "expression": "least(val1, val2, val3)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, val1, val2, val3, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT least_three FROM {hybrid_table} ORDER BY id",
        "SELECT id, val1, val2, val3, least_three FROM {hybrid_table} ORDER BY id",
        "SELECT id, val1, val2, val3, least_three FROM {hybrid_table} WHERE val1 > 5000 ORDER BY id",
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
@Name("least three alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: least_three ALIAS least(val1, val2, val3)."""
    Scenario(run=least_three_alias)

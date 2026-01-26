from testflows.core import *
from ..outline import outline


@TestScenario
def multiple_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: multiple ALIAS (value1 * value2 - value3) % value2
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "value3", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "multiple", "expression": "(value1 * value2 - value3) % (value2 + 1)", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, value3, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT multiple FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, value3, multiple FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, value3, multiple FROM {hybrid_table} WHERE value1 > 5000 ORDER BY id",
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
@Name("multiple alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: multiple ALIAS (value1 * value2 - value3) % value2"""
    Scenario(run=multiple_alias)

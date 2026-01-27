from testflows.core import *
from ...outline import outline


@TestScenario
def default_int256(self):
    """
    Define parameters for test case and call main outline.
    Test alias: default_int256 ALIAS 57896044618658097711785492504343953926634992332820282019728792003956564819967
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "default_int256",
            "expression": "toInt256(57896044618658097711785492504343953926634992332820282019728792003956564819967)",
            "hybrid_type": "Int256",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT default_int256 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_int256 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_int256 FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("default int256")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: default_int256 ALIAS 57896044618658097711785492504343953926634992332820282019728792003956564819967."""
    Scenario(run=default_int256)

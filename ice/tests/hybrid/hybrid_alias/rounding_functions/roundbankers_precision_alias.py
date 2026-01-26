from testflows.core import *
from ..outline import outline


@TestScenario
def roundbankers_precision_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: bankers_round_precision ALIAS roundBankers(value, 2)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Float64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "bankers_round_precision", "expression": "roundBankers(value, 2)", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT bankers_round_precision FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, bankers_round_precision FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, bankers_round_precision FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("roundbankers precision alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: bankers_round_precision ALIAS roundBankers(value, 2)."""
    Scenario(run=roundbankers_precision_alias)

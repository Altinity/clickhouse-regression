from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def greatest_three_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: greatest_three ALIAS greatest(val1, val2, val3)
    Greatest of three numeric values.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "val1", "datatype": "Int32"},
        {"name": "val2", "datatype": "Int32"},
        {"name": "val3", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "greatest_three", "expression": "greatest(val1, val2, val3)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, val1, val2, val3, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT greatest_three FROM {hybrid_table} ORDER BY id",
        "SELECT id, val1, val2, val3, greatest_three FROM {hybrid_table} ORDER BY id",
        "SELECT id, val1, val2, val3, greatest_three FROM {hybrid_table} WHERE val1 > 5000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_UtilityFunction("1.0"))
@Name("greatest three alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: greatest_three ALIAS greatest(val1, val2, val3)."""
    Scenario(run=greatest_three_alias)

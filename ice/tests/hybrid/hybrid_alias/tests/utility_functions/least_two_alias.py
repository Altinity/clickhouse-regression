from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def least_two_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: least_two ALIAS least(val1, val2)
    Least of two numeric values.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "val1", "datatype": "Int32"},
        {"name": "val2", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "least_two", "expression": "least(val1, val2)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, val1, val2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT least_two FROM {hybrid_table} ORDER BY id",
        "SELECT id, val1, val2, least_two FROM {hybrid_table} ORDER BY id",
        "SELECT id, val1, val2, least_two FROM {hybrid_table} WHERE val1 > 5000 ORDER BY id",
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
@Name("least two alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: least_two ALIAS least(val1, val2)."""
    Scenario(run=least_two_alias)

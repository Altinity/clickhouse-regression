from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def intersect_except_with_alias(self):
    """
    Test INTERSECT and EXCEPT set operations with alias columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed > 100 INTERSECT SELECT id, computed FROM {hybrid_table} WHERE value > 50 ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed > 0 EXCEPT SELECT id, computed FROM {hybrid_table} WHERE computed > 1000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_QueryContext("1.0"))
@Name("set operations alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test INTERSECT and EXCEPT set operations with alias columns."""
    Scenario(run=intersect_except_with_alias)

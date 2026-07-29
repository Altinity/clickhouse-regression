from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def order_by_alias_with_limit(self):
    """
    Test ORDER BY alias with LIMIT and OFFSET.
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
        "SELECT id, computed FROM {hybrid_table} ORDER BY computed ASC LIMIT 5",
        "SELECT id, computed FROM {hybrid_table} ORDER BY computed DESC LIMIT 5",
        "SELECT id, computed FROM {hybrid_table} ORDER BY computed ASC LIMIT 5 OFFSET 2",
        "SELECT id, computed FROM {hybrid_table} ORDER BY computed ASC, id DESC LIMIT 10",
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
@Name("order by limit")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test ORDER BY alias with LIMIT and OFFSET."""
    Scenario(run=order_by_alias_with_limit)

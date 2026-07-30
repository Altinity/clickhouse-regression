from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def order_by_alias_asc(self):
    """
    Test ORDER BY on alias column ascending.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "sum_alias", "expression": "id + value", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY computed ASC",
        "SELECT id, computed FROM {hybrid_table} ORDER BY computed DESC",
        "SELECT id, computed, sum_alias FROM {hybrid_table} ORDER BY computed DESC, sum_alias ASC",
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
@Name("order by alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test ORDER BY on alias columns with ASC and DESC."""
    Scenario(run=order_by_alias_asc)

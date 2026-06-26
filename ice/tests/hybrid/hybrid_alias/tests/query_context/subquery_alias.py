from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def subquery_select_alias(self):
    """
    Test alias columns accessible in subquery SELECT and WHERE clauses.
    Query: SELECT * FROM (SELECT id, computed FROM hybrid_table WHERE computed > 50) sub ORDER BY id.
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
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
        "SELECT * FROM (SELECT id, computed FROM {hybrid_table} WHERE computed > 50) sub ORDER BY id",
        "SELECT * FROM (SELECT id, computed FROM {hybrid_table}) sub WHERE sub.computed > 100 ORDER BY id",
        "SELECT max_computed FROM (SELECT max(computed) AS max_computed FROM {hybrid_table})",
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
@Name("subquery alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias columns in subqueries involving hybrid tables."""
    Scenario(run=subquery_select_alias)

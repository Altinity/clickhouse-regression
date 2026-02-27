from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def select_with_alias_expressions(self):
    """
    Test SELECT with arithmetic and conditional expressions on alias columns.
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
        "SELECT id, computed, sum_alias FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed + 10 AS adjusted, computed * 2 AS doubled FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed - sum_alias AS diff FROM {hybrid_table} ORDER BY id",
        "SELECT id, if(computed > 100, 'high', 'low') AS category FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed, CASE WHEN computed > 1000 THEN 'big' WHEN computed > 100 THEN 'medium' ELSE 'small' END AS size FROM {hybrid_table} ORDER BY id",
        "SELECT DISTINCT computed FROM {hybrid_table} ORDER BY computed LIMIT 10",
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
@Name("select expressions")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test SELECT with arithmetic, conditional, and DISTINCT expressions on alias columns."""
    Scenario(run=select_with_alias_expressions)

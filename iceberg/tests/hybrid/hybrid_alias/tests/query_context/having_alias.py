from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def having_on_alias_aggregation(self):
    """
    Test HAVING clause filtering on aggregation of alias column.
    Query: SELECT date_col, sum(computed) AS total ... GROUP BY date_col HAVING total > 100.
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
        "SELECT date_col, sum(computed) AS total FROM {hybrid_table} GROUP BY date_col HAVING total > 100 ORDER BY date_col",
        "SELECT date_col, avg(computed) AS avg_val FROM {hybrid_table} GROUP BY date_col HAVING avg_val > 50 ORDER BY date_col",
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
@Name("having alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test HAVING clause with alias column aggregations."""
    Scenario(run=having_on_alias_aggregation)

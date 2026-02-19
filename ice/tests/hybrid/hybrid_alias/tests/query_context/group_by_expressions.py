from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def group_by_expression_on_alias(self):
    """
    Test GROUP BY with expressions applied to alias columns and groupArray.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "year_month", "expression": "toYYYYMM(date_col)", "hybrid_type": "UInt32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed, year_month FROM {hybrid_table} ORDER BY id",
        "SELECT intDiv(computed, 100) AS bucket, count() AS cnt FROM {hybrid_table} GROUP BY bucket ORDER BY bucket",
        "SELECT year_month, groupArray(computed) AS values FROM {hybrid_table} GROUP BY year_month ORDER BY year_month",
        "SELECT year_month, count() AS cnt, sum(computed) AS total, min(computed) AS lo, max(computed) AS hi FROM {hybrid_table} GROUP BY year_month ORDER BY year_month",
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
@Name("group by expressions")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test GROUP BY with expressions on aliases and groupArray."""
    Scenario(run=group_by_expression_on_alias)

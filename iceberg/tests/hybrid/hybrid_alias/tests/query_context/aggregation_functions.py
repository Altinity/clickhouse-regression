from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def various_aggregations_on_alias(self):
    """
    Test various aggregation functions applied to alias columns.
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
        "SELECT count() AS cnt FROM {hybrid_table}",
        "SELECT sum(computed) AS total FROM {hybrid_table}",
        "SELECT avg(computed) AS average FROM {hybrid_table}",
        "SELECT min(computed) AS min_val, max(computed) AS max_val FROM {hybrid_table}",
        "SELECT uniq(computed) AS unique_count FROM {hybrid_table}",
        "SELECT countIf(computed > 100) AS high_count FROM {hybrid_table}",
        "SELECT sumIf(computed, computed > 0) AS positive_sum FROM {hybrid_table}",
        "SELECT quantile(0.5)(computed) AS median FROM {hybrid_table}",
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
@Name("aggregation functions")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test various aggregation functions on alias columns."""
    Scenario(run=various_aggregations_on_alias)

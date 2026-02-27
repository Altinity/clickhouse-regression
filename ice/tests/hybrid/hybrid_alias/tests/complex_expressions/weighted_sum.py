from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def weighted_sum(self):
    """
    Define parameters for test case and call main outline.
    Test alias: weighted_sum ALIAS (value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)
    Weighted sum calculation.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "value3", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "weighted_sum",
            "expression": "(value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)",
            "hybrid_type": "Float64",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, value3, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT weighted_sum FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, value3, weighted_sum FROM {hybrid_table} ORDER BY id",
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
def weighted_sum_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: weighted_sum ALIAS (value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "value3", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "weighted_sum",
            "expression": "(value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)",
            "hybrid_type": "Float64",
        },
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "weighted_sum >= 1000.0", "right_predicate": "weighted_sum < 1000.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, value3, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT weighted_sum FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, value3, weighted_sum FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, value3, weighted_sum FROM {hybrid_table} WHERE weighted_sum >= 1000.0 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_ComplexExpression("1.0"))
@Name("weighted sum")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: weighted_sum ALIAS (value1 * 0.3) + (value2 * 0.5) + (value3 * 0.2)."""
    Scenario(run=weighted_sum)
    Scenario(run=weighted_sum_in_watermark)

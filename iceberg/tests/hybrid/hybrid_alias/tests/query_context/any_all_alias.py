from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def any_all_comparison_with_alias(self):
    """
    Test = ANY / > ALL style comparisons using alias columns
    in non-correlated subqueries.
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
        "SELECT id, computed FROM {hybrid_table} WHERE computed > ALL (SELECT computed FROM {hybrid_table} WHERE value < 10) ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed = ANY (SELECT computed FROM {hybrid_table} WHERE value > 100) ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed < ALL (SELECT computed FROM {hybrid_table} WHERE value > 9000) ORDER BY id",
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
@Name("any all alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test ANY and ALL comparisons with alias columns in non-correlated subqueries."""
    Scenario(run=any_all_comparison_with_alias)

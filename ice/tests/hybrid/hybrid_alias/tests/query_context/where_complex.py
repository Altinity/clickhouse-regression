from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def complex_where_with_aliases(self):
    """
    Test complex WHERE conditions involving alias columns with AND/OR/NOT.
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
        "SELECT id, computed FROM {hybrid_table} WHERE computed > 100 AND sum_alias < 10000 ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed > 5000 OR sum_alias > 5000 ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE NOT (computed < 50) ORDER BY id",
        "SELECT id, computed, sum_alias FROM {hybrid_table} WHERE (computed BETWEEN 100 AND 1000) AND (sum_alias > 50) ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed IN (SELECT computed FROM {hybrid_table} WHERE value > 100) AND sum_alias > 200 ORDER BY id",
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
@Name("where complex")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test complex WHERE conditions with AND/OR/NOT/BETWEEN/IN on alias columns."""
    Scenario(run=complex_where_with_aliases)

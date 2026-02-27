from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def join_on_alias_column(self):
    """
    Test JOIN where alias columns are selected from both sides.
    Uses a self-join on the hybrid table to verify alias accessibility in JOINs.
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
        "SELECT a.id, a.computed, b.computed FROM {hybrid_table} a JOIN {hybrid_table} b ON a.id = b.id ORDER BY a.id",
        "SELECT a.id, a.computed + b.computed AS double_computed FROM {hybrid_table} a JOIN {hybrid_table} b ON a.id = b.id ORDER BY a.id",
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
@Name("join alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test JOIN operations with alias columns in hybrid tables."""
    Scenario(run=join_on_alias_column)

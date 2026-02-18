from testflows.core import *
from ..outline import outline
from ..requirements import *


@TestScenario
def left_normal_right_alias(self):
    """
    Define parameters for test case and call main outline.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    left_base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
        {"name": "computed", "datatype": "Int64"},  # Normal column in left
    ]
    right_base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    left_alias_columns = []
    right_alias_columns = [
        {"name": "computed", "expression": "value * 2"},  # Alias in right
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
        left_base_columns=left_base_columns,
        right_base_columns=right_base_columns,
        left_alias_columns=left_alias_columns,
        right_alias_columns=right_alias_columns,
    )


@TestScenario
@Requirements(
    RQ_Ice_HybridAlias_Segments_LeftNormalRightAlias("1.0"),
)
@Name("left normal right alias")
def feature(self, minio_root_user, minio_root_password):
    """Test case where left segment has normal column but right table has alias column."""
    Scenario(run=left_normal_right_alias)

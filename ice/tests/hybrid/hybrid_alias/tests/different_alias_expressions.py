from testflows.core import *
from ..outline import outline
from ..requirements import *


@TestScenario
def different_alias_expressions(self):
    """
    Test where left and right segments define the same alias column name
    with different expressions.
    Left: computed ALIAS value * 2
    Right: computed ALIAS value * 3
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "hybrid_type": "Int64"},
    ]
    left_base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    right_base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    left_alias_columns = [
        {"name": "computed", "expression": "value * 2"},
    ]
    right_alias_columns = [
        {"name": "computed", "expression": "value * 3"},
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
    RQ_Ice_HybridAlias_DifferentAliasExpressions("1.0"),
)
@Name("different alias expressions")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test where left and right segments define the same alias column name
    with different expressions (value * 2 vs value * 3)."""
    Scenario(run=different_alias_expressions)

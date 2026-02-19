from testflows.core import *
from ..outline import outline
from ..requirements import *


@TestScenario
def alias_in_left_missing_in_right(self):
    """
    Left segment defines computed as ALIAS value * 2.
    Right segment has no computed column at all (neither alias nor regular).
    Hybrid table defines computed as Int64.
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
    ]
    right_base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    left_alias_columns = [
        {"name": "computed", "expression": "value * 2"},
    ]
    right_alias_columns = []
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 36, "error_message": "DB::Exception: Hybrid segment"}
    test_queries = []
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
def alias_in_right_missing_in_left(self):
    """
    Right segment defines computed as ALIAS value * 2.
    Left segment has no computed column at all (neither alias nor regular).
    Hybrid table defines computed as Int64.
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
    ]
    right_base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    left_alias_columns = []
    right_alias_columns = [
        {"name": "computed", "expression": "value * 2"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 36, "error_message": "DB::Exception: Hybrid segment"}
    test_queries = []
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
    RQ_Ice_HybridAlias_AliasMissingInSegment("1.0"),
)
@Name("alias missing in segment")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test where an alias column exists in one segment but is completely
    missing from the other segment (no alias, no regular column)."""
    Scenario(run=alias_in_left_missing_in_right)
    Scenario(run=alias_in_right_missing_in_left)

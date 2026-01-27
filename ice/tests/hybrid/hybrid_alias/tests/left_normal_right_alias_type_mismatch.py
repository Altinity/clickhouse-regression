from testflows.core import *
from ..outline import outline


@TestScenario
def left_normal_right_alias_type_mismatch(self):
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
        {"name": "computed", "datatype": "Int32"},  # Regular column in left with mismatced type
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
        {"query": "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id", "exitcode": 0, "message": None},
        {
            "query": "SELECT computed FROM {hybrid_table} ORDER BY id",
            "exitcode": 179,
            "message": "DB::Exception: Multiple expressions __aliasMarker",
        },
        {
            "query": "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
            "exitcode": 179,
            "message": "DB::Exception: Multiple expressions __aliasMarker",
        },
        {
            "query": "SELECT id, value, computed FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
            "exitcode": 179,
            "message": "DB::Exception: Multiple expressions __aliasMarker",
        },
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
@Name("left normal right alias type mismatch")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test case where left segment has normal column with mismatched type
    but right table has alias column."""
    Scenario(run=left_normal_right_alias_type_mismatch)

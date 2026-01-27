from testflows.core import *
from ...outline import outline


@TestScenario
def single_level_dependency(self):
    """
    Define parameters for test case and call main outline.
    Test alias: computed_2 ALIAS computed + 10
    Single-level dependency: alias depends on one other alias.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "computed_2", "expression": "computed + 10", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed, computed_2 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed, computed_2 FROM {hybrid_table} ORDER BY id",
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
def single_level_dependency_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: computed_2 ALIAS computed + 10
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "computed_2", "expression": "computed + 10", "hybrid_type": "Int64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "computed_2 >= 100", "right_predicate": "computed_2 < 100"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed, computed_2 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed, computed_2 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed_2 FROM {hybrid_table} WHERE computed_2 >= 100 ORDER BY id",
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
@Name("single level dependency")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: computed_2 ALIAS computed + 10 (single-level dependency)."""
    Scenario(run=single_level_dependency)
    Scenario(run=single_level_dependency_in_watermark)

from testflows.core import *
from ...outline import outline


@TestScenario
def two_level_dependency(self):
    """
    Define parameters for test case and call main outline.
    Test alias: quadrupled ALIAS doubled * 2
    Two-level dependency chain: value -> doubled -> quadrupled
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled FROM {hybrid_table} ORDER BY id",
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
def two_level_dependency_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: quadrupled ALIAS doubled * 2
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "quadrupled >= 100", "right_predicate": "quadrupled < 100"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, quadrupled FROM {hybrid_table} WHERE quadrupled >= 100 ORDER BY id",
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
@Name("two level dependency")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: quadrupled ALIAS doubled * 2 (two-level dependency chain)."""
    Scenario(run=two_level_dependency)
    Scenario(run=two_level_dependency_in_watermark)

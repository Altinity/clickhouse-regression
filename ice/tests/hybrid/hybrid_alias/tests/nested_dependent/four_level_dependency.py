from testflows.core import *
from ...outline import outline


@TestScenario
def four_level_dependency(self):
    """
    Define parameters for test case and call main outline.
    Test alias: hexadecupled ALIAS octupled * 2
    Four-level dependency chain: value -> doubled -> quadrupled -> octupled -> hexadecupled
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
        {"name": "octupled", "expression": "quadrupled * 2", "hybrid_type": "Int64"},
        {"name": "hexadecupled", "expression": "octupled * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-05-12'", "right_predicate": "date_col < '2013-05-12'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, octupled, hexadecupled FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, octupled, hexadecupled FROM {hybrid_table} ORDER BY id",
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
def four_level_dependency_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: hexadecupled ALIAS octupled * 2
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
        {"name": "octupled", "expression": "quadrupled * 2", "hybrid_type": "Int64"},
        {"name": "hexadecupled", "expression": "octupled * 2", "hybrid_type": "Int64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "hexadecupled >= 400", "right_predicate": "hexadecupled < 400"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, octupled, hexadecupled FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, octupled, hexadecupled FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, hexadecupled FROM {hybrid_table} WHERE hexadecupled >= 400 ORDER BY id",
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
@Name("four level dependency")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: hexadecupled ALIAS octupled * 2 (four-level dependency chain)."""
    Scenario(run=four_level_dependency)
    Scenario(run=four_level_dependency_in_watermark)

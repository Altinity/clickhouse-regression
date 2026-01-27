from testflows.core import *
from ...outline import outline


@TestScenario
def conditional_with_aliases(self):
    """
    Define parameters for test case and call main outline.
    Test alias: conditional_result ALIAS if(doubled > 100, quadrupled, doubled)
    Conditional expression with aliases.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
        {"name": "conditional_result", "expression": "if(doubled > 100, quadrupled, doubled)", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, conditional_result FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, conditional_result FROM {hybrid_table} ORDER BY id",
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
def conditional_with_aliases_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: conditional_result ALIAS if(doubled > 100, quadrupled, doubled)
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
        {"name": "conditional_result", "expression": "if(doubled > 100, quadrupled, doubled)", "hybrid_type": "Int64"},
    ]
    # Use final alias column in watermark predicates
    watermark = {"left_predicate": "conditional_result >= 200", "right_predicate": "conditional_result < 200"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, conditional_result FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, conditional_result FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, conditional_result FROM {hybrid_table} WHERE conditional_result >= 200 ORDER BY id",
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
@Name("conditional with aliases")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: conditional_result ALIAS if(doubled > 100, quadrupled, doubled) (conditional with aliases)."""
    Scenario(run=conditional_with_aliases)
    Scenario(run=conditional_with_aliases_in_watermark)

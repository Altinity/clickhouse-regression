from testflows.core import *
from ...outline import outline


@TestScenario
def string_operations_multiple_aliases(self):
    """
    Define parameters for test case and call main outline.
    Test alias: combined ALIAS concat(toString(doubled), '-', toString(quadrupled))
    String operations with multiple aliases.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "doubled", "expression": "value * 2", "hybrid_type": "Int64"},
        {"name": "quadrupled", "expression": "doubled * 2", "hybrid_type": "Int64"},
        {
            "name": "combined",
            "expression": "concat(toString(doubled), '-', toString(quadrupled))",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT doubled, quadrupled, combined FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, doubled, quadrupled, combined FROM {hybrid_table} ORDER BY id",
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
@Name("string operations multiple aliases")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: combined ALIAS concat(toString(doubled), '-', toString(quadrupled)) (string operations with multiple aliases)."""
    Scenario(run=string_operations_multiple_aliases)

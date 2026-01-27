from testflows.core import *
from ...outline import outline


@TestScenario
def case_expr_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: case_expr ALIAS CASE value WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'other' END
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "case_expr",
            "expression": "CASE value WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'other' END",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT case_expr FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, case_expr FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, case_expr FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("case expr alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: case_expr ALIAS CASE value WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'other' END."""
    Scenario(run=case_expr_alias)

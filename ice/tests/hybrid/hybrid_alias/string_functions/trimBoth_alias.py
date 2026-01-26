from testflows.core import *
from ..outline import outline


@TestScenario
def trimBoth_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: trimmed_name ALIAS trimBoth(name, 'a')
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "trimmed_name", "expression": "trimBoth(name, 'a')", "hybrid_type": "String"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT trimmed_name FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, trimmed_name FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, trimmed_name FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("trimBoth alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: trimmed_name ALIAS trimBoth(name, 'a')."""
    Scenario(run=trimBoth_alias)

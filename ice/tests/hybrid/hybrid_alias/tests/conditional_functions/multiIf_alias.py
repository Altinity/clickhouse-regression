from testflows.core import *
from ...outline import outline


@TestScenario
def multiIf_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "status",
            "expression": "multiIf(value < 10, 'low', value < 50, 'medium', 'high')",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT status FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, status FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, status FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def multiIf_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')
    Using alias column length in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "status",
            "expression": "multiIf(value < 10, 'low', value < 50, 'medium', 'high')",
            "hybrid_type": "String",
        },
    ]
    # Use alias column length in watermark predicates (can't compare strings directly)
    watermark = {"left_predicate": "length(status) >= 6", "right_predicate": "length(status) < 6"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT status FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, status FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, status FROM {hybrid_table} WHERE length(status) >= 6 ORDER BY id",
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
@Name("multiIf alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: status ALIAS multiIf(value < 10, 'low', value < 50, 'medium', 'high')."""
    Scenario(run=multiIf_alias)
    Scenario(run=multiIf_alias_in_watermark)

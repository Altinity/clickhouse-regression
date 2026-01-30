from testflows.core import *
from ...outline import outline


@TestScenario
def toTimeZone_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: to_timezone ALIAS toTimeZone(datetime_col, 'America/New_York')
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "datetime_col", "datatype": "DateTime"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "to_timezone",
            "expression": "toTimeZone(datetime_col, 'America/New_York')",
            "hybrid_type": "DateTime('America/New_York')",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT to_timezone FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, to_timezone FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, to_timezone FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("toTimeZone alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: to_timezone ALIAS toTimeZone(datetime_col, 'America/New_York')."""
    Scenario(run=toTimeZone_alias)

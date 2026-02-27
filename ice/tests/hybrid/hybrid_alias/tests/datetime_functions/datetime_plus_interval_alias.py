from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def datetime_plus_interval_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: datetime_plus_interval ALIAS datetime_col + INTERVAL 1 HOUR
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "datetime_col", "datatype": "DateTime"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "datetime_plus_interval", "expression": "datetime_col + INTERVAL 1 HOUR", "hybrid_type": "DateTime"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT datetime_plus_interval FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, datetime_plus_interval FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, datetime_plus_interval FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def datetime_plus_interval_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: datetime_plus_interval ALIAS datetime_col + INTERVAL 1 HOUR
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "datetime_col", "datatype": "DateTime"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "datetime_plus_interval", "expression": "datetime_col + INTERVAL 1 HOUR", "hybrid_type": "DateTime"},
    ]
    # Use alias column in watermark predicates
    watermark = {
        "left_predicate": "datetime_plus_interval >= '2010-01-01 00:00:00'",
        "right_predicate": "datetime_plus_interval < '2010-01-01 00:00:00'",
    }
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT datetime_plus_interval FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, datetime_plus_interval FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, datetime_plus_interval FROM {hybrid_table} WHERE datetime_plus_interval >= '2010-01-01 00:00:00' ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_DateTimeFunction("1.0"))
@Name("datetime plus interval alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: datetime_plus_interval ALIAS datetime_col + INTERVAL 1 HOUR."""
    Scenario(run=datetime_plus_interval_alias)
    Scenario(run=datetime_plus_interval_alias_in_watermark)

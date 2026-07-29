from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def toYYYYMMDD_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: year_month_day ALIAS toYYYYMMDD(date_col)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "year_month_day", "expression": "toYYYYMMDD(date_col)", "hybrid_type": "UInt32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT year_month_day FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year_month_day FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year_month_day FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toYYYYMMDD_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: year_month_day ALIAS toYYYYMMDD(date_col)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "year_month_day", "expression": "toYYYYMMDD(date_col)", "hybrid_type": "UInt32"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "year_month_day >= 20100101", "right_predicate": "year_month_day < 20100101"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT year_month_day FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year_month_day FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year_month_day FROM {hybrid_table} WHERE year_month_day >= 20100101 ORDER BY id",
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
@Name("toYYYYMMDD alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: year_month_day ALIAS toYYYYMMDD(date_col)."""
    Scenario(run=toYYYYMMDD_alias)
    Scenario(run=toYYYYMMDD_alias_in_watermark)

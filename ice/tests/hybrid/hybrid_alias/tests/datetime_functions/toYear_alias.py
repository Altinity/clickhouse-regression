from testflows.core import *
from ...outline import outline


@TestScenario
def toYear_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: year ALIAS toYear(date_col)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "year", "expression": "toYear(date_col)", "hybrid_type": "UInt16"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT year FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toYear_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: year ALIAS toYear(date_col)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "year", "expression": "toYear(date_col)", "hybrid_type": "UInt16"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "year >= 2010", "right_predicate": "year < 2010"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT year FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, year FROM {hybrid_table} WHERE year >= 2010 ORDER BY id",
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
@Name("toYear alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: year ALIAS toYear(date_col)."""
    Scenario(run=toYear_alias)
    Scenario(run=toYear_alias_in_watermark)

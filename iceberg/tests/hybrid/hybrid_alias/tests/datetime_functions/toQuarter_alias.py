from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def toQuarter_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: quarter ALIAS toQuarter(date_col)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "quarter", "expression": "toQuarter(date_col)", "hybrid_type": "UInt8"},
    ]
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT quarter FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, quarter FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, quarter FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toQuarter_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: quarter ALIAS toQuarter(date_col)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "quarter", "expression": "toQuarter(date_col)", "hybrid_type": "UInt8"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "quarter >= 3", "right_predicate": "quarter < 3"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT quarter FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, quarter FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, quarter FROM {hybrid_table} WHERE quarter >= 3 ORDER BY id",
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
@Name("toQuarter alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: quarter ALIAS toQuarter(date_col)."""
    Scenario(run=toQuarter_alias)
    Scenario(run=toQuarter_alias_in_watermark)

from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def intdiv_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: intdiv ALIAS intDiv(value, 2)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "intdiv", "expression": "intDiv(value, 2)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-11-06'", "right_predicate": "date_col < '2008-11-06'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT intdiv FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, intdiv FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, intdiv FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def intdiv_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: intdiv ALIAS intDiv(value, 2)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "intdiv", "expression": "intDiv(value, 2)", "hybrid_type": "Int32"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "intdiv >= 5000", "right_predicate": "intdiv < 5000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT intdiv FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, intdiv FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, intdiv FROM {hybrid_table} WHERE intdiv >= 5000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_Arithmetic("1.0"))
@Name("intdiv alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: intdiv ALIAS intDiv(value, 2)"""
    Scenario(run=intdiv_alias)
    Scenario(run=intdiv_alias_in_watermark)

from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def sum_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: sum_alias ALIAS id + value
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "sum_alias", "expression": "id + value", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2004-04-16'", "right_predicate": "date_col < '2004-04-16'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT sum_alias FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sum_alias FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sum_alias FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def sum_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: sum_alias ALIAS id + value
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "sum_alias", "expression": "id + value", "hybrid_type": "Int64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "sum_alias >= 10000", "right_predicate": "sum_alias < 10000"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT sum_alias FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sum_alias FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, sum_alias FROM {hybrid_table} WHERE sum_alias >= 10000 ORDER BY id",
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
@Name("sum alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: sum_alias ALIAS id + value"""
    Scenario(run=sum_alias)
    Scenario(run=sum_alias_in_watermark)

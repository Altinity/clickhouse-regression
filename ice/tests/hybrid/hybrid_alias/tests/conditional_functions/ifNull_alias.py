from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def ifNull_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: if_null_result ALIAS ifNull(value, 0)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "if_null_result", "expression": "ifNull(value, 0)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT if_null_result FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, if_null_result FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, if_null_result FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def ifNull_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: if_null_result ALIAS ifNull(value, 0)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "if_null_result", "expression": "ifNull(value, 0)", "hybrid_type": "Int32"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "if_null_result >= 100", "right_predicate": "if_null_result < 100"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT if_null_result FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, if_null_result FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, if_null_result FROM {hybrid_table} WHERE if_null_result >= 100 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_Conditional("1.0"))
@Name("ifNull alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: if_null_result ALIAS ifNull(value, 0)."""
    Scenario(run=ifNull_alias)
    Scenario(run=ifNull_alias_in_watermark)

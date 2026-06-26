from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def modulo_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: modulo ALIAS value % 3
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "modulo", "expression": "value % 3", "hybrid_type": "Int16"},
    ]
    watermark = {"left_predicate": "date_col >= '2012-04-28'", "right_predicate": "date_col < '2012-04-28'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT modulo FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, modulo FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, modulo FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def modulo_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: modulo ALIAS value % 3
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "modulo", "expression": "value % 3", "hybrid_type": "Int16"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "modulo >= 1", "right_predicate": "modulo < 1"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT modulo FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, modulo FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, modulo FROM {hybrid_table} WHERE modulo >= 1 ORDER BY id",
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
@Name("modulo alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: modulo ALIAS value % 3"""
    Scenario(run=modulo_alias)
    Scenario(run=modulo_alias_in_watermark)

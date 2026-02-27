from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def quotient_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: quotient ALIAS value1 / value2
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "quotient", "expression": "value1 / value2", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2004-04-16'", "right_predicate": "date_col < '2004-04-16'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT quotient FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, quotient FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, quotient FROM {hybrid_table} WHERE value1 > 5000 ORDER BY id",
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
def quotient_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: quotient ALIAS value1 / value2
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value1", "datatype": "Int32"},
        {"name": "value2", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "quotient", "expression": "value1 / value2", "hybrid_type": "Float64"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "quotient >= 10.0", "right_predicate": "quotient < 10.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value1, value2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT quotient FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, quotient FROM {hybrid_table} ORDER BY id",
        "SELECT id, value1, value2, quotient FROM {hybrid_table} WHERE quotient >= 10.0 ORDER BY id",
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
@Name("quotient alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: quotient ALIAS value1 / value2"""
    Scenario(run=quotient_alias)
    Scenario(run=quotient_alias_in_watermark)

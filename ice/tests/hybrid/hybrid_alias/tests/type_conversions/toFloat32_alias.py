from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def toFloat32_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_float32 ALIAS toFloat32(value)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_float32", "expression": "toFloat32(value)", "hybrid_type": "Float32"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-11-06'", "right_predicate": "date_col < '2008-11-06'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_float32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_float32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_float32 FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
def toFloat32_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: value_float32 ALIAS toFloat32(value)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "value_float32", "expression": "toFloat32(value)", "hybrid_type": "Float32"},
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "value_float32 >= 5000.0", "right_predicate": "value_float32 < 5000.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT value_float32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_float32 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, value_float32 FROM {hybrid_table} WHERE value_float32 >= 5000.0 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_TypeConversion("1.0"))
@Name("toFloat32 alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: value_float32 ALIAS toFloat32(value)."""
    Scenario(run=toFloat32_alias)
    Scenario(run=toFloat32_alias_in_watermark)

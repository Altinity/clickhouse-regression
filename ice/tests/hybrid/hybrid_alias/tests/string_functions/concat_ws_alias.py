from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def concat_ws_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: concatenated_ws ALIAS concatWithSeparator(' ', first_name, last_name)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "first_name", "datatype": "String"},
        {"name": "last_name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "concatenated_ws",
            "expression": "concatWithSeparator(' ', first_name, last_name)",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT concatenated_ws FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, concatenated_ws FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, concatenated_ws FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_StringFunction("1.0"))
@Name("concat ws alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: concatenated_ws ALIAS concatWithSeparator(' ', first_name, last_name)."""
    Scenario(run=concat_ws_alias)

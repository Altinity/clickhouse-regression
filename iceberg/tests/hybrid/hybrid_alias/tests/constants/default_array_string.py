from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def default_array_string(self):
    """
    Define parameters for test case and call main outline.
    Test alias: default_array_string ALIAS array('a', 'b', 'c')
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "default_array_string", "expression": "array('a', 'b', 'c')", "hybrid_type": "Array(String)"},
    ]
    watermark = {"left_predicate": "date_col >= '2007-05-01'", "right_predicate": "date_col < '2007-05-01'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT default_array_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_array_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_array_string FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_Constants("1.0"))
@Name("default array string")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: default_array_string ALIAS array('a', 'b', 'c')."""
    Scenario(run=default_array_string)

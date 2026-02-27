from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def length_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: name_length ALIAS length(name)
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "name_length", "expression": "length(name)", "hybrid_type": "UInt64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT name_length FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, name_length FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, name_length FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("length alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: name_length ALIAS length(name)."""
    Scenario(run=length_alias)

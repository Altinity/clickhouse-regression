from testflows.core import *
from ...outline import outline


@TestScenario
def tuple_second_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: tuple_second ALIAS tupleElement(tuple_col, 2)
    Second element of tuple.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "tuple_col", "datatype": "Tuple(Int32, String)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "tuple_second", "expression": "tupleElement(tuple_col, 2)", "hybrid_type": "String"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT tuple_second FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, tuple_second FROM {hybrid_table} ORDER BY id",
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
@Name("tuple second alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: tuple_second ALIAS tupleElement(tuple_col, 2)."""
    Scenario(run=tuple_second_alias)

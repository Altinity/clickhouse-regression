from testflows.core import *
from ...outline import outline


@TestScenario
def tuple_first_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: tuple_first ALIAS tupleElement(tuple_col, 1)
    First element of tuple.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "tuple_col", "datatype": "Tuple(Int32, String)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "tuple_first", "expression": "tupleElement(tuple_col, 1)", "hybrid_type": "Int32"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT tuple_first FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, tuple_first FROM {hybrid_table} ORDER BY id",
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
@Name("tuple first alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: tuple_first ALIAS tupleElement(tuple_col, 1)."""
    Scenario(run=tuple_first_alias)

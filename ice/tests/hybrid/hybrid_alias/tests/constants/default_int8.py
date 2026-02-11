from testflows.core import *
from ...outline import outline


@TestScenario
def default_int8(self):
    """
    Define parameters for test case and call main outline.
    Test alias: default_int8 ALIAS 50
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "default_int8", "expression": "-50", "hybrid_type": "Int8"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-11-06'", "right_predicate": "date_col < '2008-11-06'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT default_int8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_int8 FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_int8 FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("default int8")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: default_int8 ALIAS 50."""
    Scenario(run=default_int8)

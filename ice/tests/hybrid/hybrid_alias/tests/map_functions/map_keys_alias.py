from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def map_keys_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: map_keys ALIAS mapKeys(map_col)
    Keys of map.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "map_col", "datatype": "Map(String, Int32)"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "map_keys", "expression": "mapKeys(map_col)", "hybrid_type": "Array(String)"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT map_keys FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, map_keys FROM {hybrid_table} ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_MapFunction("1.0"))
@Name("map keys alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: map_keys ALIAS mapKeys(map_col)."""
    Scenario(run=map_keys_alias)

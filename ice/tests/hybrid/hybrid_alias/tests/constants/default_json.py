from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def default_json(self):
    """
    Define parameters for test case and call main outline.
    Test alias: default_json ALIAS $${"a" : {"b" : 42}, "c" : [1, 2, 3]}$$::JSON
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    json_str = '{"a" : {"b" : 42}, "c" : [1, 2, 3]}'
    # Escape double quotes for bash: " becomes \"
    json_str_escaped = json_str.replace('"', '\\"')
    alias_columns = [
        {"name": "default_json", "expression": f"\\$\\${json_str_escaped}\\$\\$::JSON", "hybrid_type": "JSON"},
    ]
    watermark = {"left_predicate": "date_col >= '2014-09-14'", "right_predicate": "date_col < '2014-09-14'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT default_json FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_json FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, default_json FROM {hybrid_table} WHERE value > 5000 ORDER BY id",
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
@Name("default json")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: default_json ALIAS $${"a" : {"b" : 42}, "c" : [1, 2, 3]}$$::JSON."""
    Scenario(run=default_json)

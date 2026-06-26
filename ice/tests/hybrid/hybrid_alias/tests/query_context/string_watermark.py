from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def string_equality_watermark(self):
    """
    Test string equality predicate in watermark.
    Watermark: name = 'test'.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "upper_name", "expression": "upper(name)", "hybrid_type": "String"},
    ]
    watermark = {"left_predicate": "name LIKE 'A%'", "right_predicate": "name NOT LIKE 'A%'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, name, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT upper_name FROM {hybrid_table} ORDER BY id",
        "SELECT id, name, upper_name FROM {hybrid_table} ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_QueryContext("1.0"))
@Name("string watermark")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test string LIKE predicate used in watermark with alias columns present."""
    Scenario(run=string_equality_watermark)

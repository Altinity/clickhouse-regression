from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def greatest_date_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: greatest_date ALIAS greatest(date1, date2)
    Greatest of date values.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "date1", "datatype": "Date"},
        {"name": "date2", "datatype": "Date"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "greatest_date", "expression": "greatest(date1, date2)", "hybrid_type": "Date"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, date1, date2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT greatest_date FROM {hybrid_table} ORDER BY id",
        "SELECT id, date1, date2, greatest_date FROM {hybrid_table} ORDER BY id",
        "SELECT id, date1, date2, greatest_date FROM {hybrid_table} WHERE date1 > '2025-01-10' ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_UtilityFunction("1.0"))
@Name("greatest date alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: greatest_date ALIAS greatest(date1, date2) (date values)."""
    Scenario(run=greatest_date_alias)

from testflows.core import *
from ..outline import outline


@TestScenario
def alias_column_in_predicate(self):
    """
    Define parameters for test case and call main outline.
    Test alias column used in watermark predicate: computed >= 20 and computed < 20
    This tests section 2.2: Alias Column Predicates
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "computed >= 20", "right_predicate": "computed < 20"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed >= 20 ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed < 20 ORDER BY id",
        "SELECT max(computed), min(computed), avg(computed) FROM {hybrid_table}",
        "SELECT date_col, sum(computed) as total FROM {hybrid_table} GROUP BY date_col ORDER BY date_col",
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
def alias_column_in_predicate_overlapping_segments(self):
    """
    Define parameters for test case and call main outline.
    Test alias column used in watermark predicate: computed >= 20 and computed < 20
    This tests section 2.2: Alias Column Predicates
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "date_col", "hybrid_type": "Date"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-08-05'", "right_predicate": "date_col < '2025-08-05'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, computed FROM {hybrid_table} ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed >= '2013-08-05' ORDER BY id",
        "SELECT id, computed FROM {hybrid_table} WHERE computed < '2025-08-05' ORDER BY id",
        "SELECT max(computed), min(computed), avg(computed) FROM {hybrid_table}",
        "SELECT date_col, sum(computed) as total FROM {hybrid_table} GROUP BY date_col ORDER BY date_col",
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
@Name("alias column in predicate")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column used in watermark predicate: computed >= 20 and computed < 20."""
    Scenario(run=alias_column_in_predicate)
    Scenario(run=alias_column_in_predicate_overlapping_segments)

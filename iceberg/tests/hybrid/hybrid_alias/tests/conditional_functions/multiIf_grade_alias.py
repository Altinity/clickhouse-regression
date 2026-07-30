from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def multiIf_grade_alias(self):
    """
    Define parameters for test case and call main outline.
    Test alias: grade ALIAS multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "score", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "grade",
            "expression": "multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2020-08-26'", "right_predicate": "date_col < '2020-08-26'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, score, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT grade FROM {hybrid_table} ORDER BY id",
        "SELECT id, score, grade FROM {hybrid_table} ORDER BY id",
        "SELECT id, score, grade FROM {hybrid_table} WHERE score > 5000 ORDER BY id",
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
def multiIf_grade_alias_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: grade ALIAS multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')
    Using alias column length in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "score", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "grade",
            "expression": "multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')",
            "hybrid_type": "String",
        },
    ]
    # Use alias column length in watermark predicates (can't compare strings directly)
    watermark = {"left_predicate": "length(grade) = 1", "right_predicate": "length(grade) != 1"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, score, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT grade FROM {hybrid_table} ORDER BY id",
        "SELECT id, score, grade FROM {hybrid_table} ORDER BY id",
        "SELECT id, score, grade FROM {hybrid_table} WHERE length(grade) = 1 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_Conditional("1.0"))
@Name("multiIf grade alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: grade ALIAS multiIf(score >= 90, 'A', score >= 80, 'B', score >= 70, 'C', 'F')."""
    Scenario(run=multiIf_grade_alias)
    Scenario(run=multiIf_grade_alias_in_watermark)

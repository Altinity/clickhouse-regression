from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def normalization_formula(self):
    """
    Define parameters for test case and call main outline.
    Test alias: normalized_value ALIAS (value - min_value) / (max_value - min_value)
    Normalization formula with multiple base columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "min_value", "datatype": "Int32"},
        {"name": "max_value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "normalized_value",
            "expression": "(value - min_value) / (max_value - min_value)",
            "hybrid_type": "Float64",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2014-08-18'", "right_predicate": "date_col < '2014-08-18'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, min_value, max_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT normalized_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, min_value, max_value, normalized_value FROM {hybrid_table} ORDER BY id",
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
def normalization_formula_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: normalized_value ALIAS (value - min_value) / (max_value - min_value)
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "min_value", "datatype": "Int32"},
        {"name": "max_value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "normalized_value",
            "expression": "(value - min_value) / (max_value - min_value)",
            "hybrid_type": "Float64",
        },
    ]
    # Use alias column in watermark predicates
    watermark = {"left_predicate": "normalized_value >= 0.5", "right_predicate": "normalized_value < 0.5"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, min_value, max_value, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT normalized_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, min_value, max_value, normalized_value FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, normalized_value FROM {hybrid_table} WHERE normalized_value >= 0.5 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_ComplexExpression("1.0"))
@Name("normalization formula")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: normalized_value ALIAS (value - min_value) / (max_value - min_value)."""
    Scenario(run=normalization_formula)
    Scenario(run=normalization_formula_in_watermark)

from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def float32_multiply(self):
    """
    Define parameters for test case and call main outline.
    Test alias: scaled ALIAS price * 1.5 on Float32 base columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "price", "datatype": "Float32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "scaled", "expression": "price * 1.5", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2012-04-28'", "right_predicate": "date_col < '2012-04-28'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, price, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT scaled FROM {hybrid_table} ORDER BY id",
        "SELECT id, price, scaled FROM {hybrid_table} ORDER BY id",
        "SELECT id, price, scaled FROM {hybrid_table} WHERE price > 100.0 ORDER BY id",
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
def float64_sum(self):
    """
    Define parameters for test case and call main outline.
    Test alias: total ALIAS amount1 + amount2 on Float64 base columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "amount1", "datatype": "Float64"},
        {"name": "amount2", "datatype": "Float64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "total", "expression": "amount1 + amount2", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2013-08-05'", "right_predicate": "date_col < '2013-08-05'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, amount1, amount2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT total FROM {hybrid_table} ORDER BY id",
        "SELECT id, amount1, amount2, total FROM {hybrid_table} ORDER BY id",
        "SELECT id, amount1, amount2, total FROM {hybrid_table} WHERE amount1 > 500.0 ORDER BY id",
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
def float64_division(self):
    """
    Define parameters for test case and call main outline.
    Test alias: ratio ALIAS amount1 / amount2 on Float64 base columns.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "amount1", "datatype": "Float64"},
        {"name": "amount2", "datatype": "Float64"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "ratio", "expression": "amount1 / amount2", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "date_col >= '2008-11-06'", "right_predicate": "date_col < '2008-11-06'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, amount1, amount2, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT ratio FROM {hybrid_table} ORDER BY id",
        "SELECT id, amount1, amount2, ratio FROM {hybrid_table} ORDER BY id",
        "SELECT id, amount1, amount2, ratio FROM {hybrid_table} WHERE amount1 > 500.0 ORDER BY id",
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
def float_arithmetic_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: scaled ALIAS price * 1.5 on Float32 base column.
    Using alias column in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "price", "datatype": "Float32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "scaled", "expression": "price * 1.5", "hybrid_type": "Float64"},
    ]
    watermark = {"left_predicate": "scaled >= 500.0", "right_predicate": "scaled < 500.0"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, price, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT scaled FROM {hybrid_table} ORDER BY id",
        "SELECT id, price, scaled FROM {hybrid_table} ORDER BY id",
        "SELECT id, price, scaled FROM {hybrid_table} WHERE scaled >= 500.0 ORDER BY id",
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
@Requirements(RQ_Ice_HybridAlias_Arithmetic("1.0"))
@Name("float arithmetic alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test arithmetic alias columns on Float32 and Float64 base columns."""
    Scenario(run=float32_multiply)
    Scenario(run=float64_sum)
    Scenario(run=float64_division)
    Scenario(run=float_arithmetic_in_watermark)

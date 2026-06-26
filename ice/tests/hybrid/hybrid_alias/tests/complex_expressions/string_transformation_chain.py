from testflows.core import *
from ...outline import outline
from ...requirements import *


@TestScenario
def string_transformation_chain(self):
    """
    Define parameters for test case and call main outline.
    Test alias: formatted_string ALIAS concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))
    String transformation chain with nested functions.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "formatted_string",
            "expression": "concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))",
            "hybrid_type": "String",
        },
    ]
    watermark = {"left_predicate": "date_col >= '2008-04-25'", "right_predicate": "date_col < '2008-04-25'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, name, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT formatted_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, name, formatted_string FROM {hybrid_table} ORDER BY id",
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
def string_transformation_chain_in_watermark(self):
    """
    Define parameters for test case and call main outline.
    Test alias: formatted_string ALIAS concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))
    Using alias column length in watermark predicate.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "name", "datatype": "String"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {
            "name": "formatted_string",
            "expression": "concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))",
            "hybrid_type": "String",
        },
    ]
    # Use alias column length in watermark predicates (can't compare strings directly)
    watermark = {"left_predicate": "length(formatted_string) >= 5", "right_predicate": "length(formatted_string) < 5"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, value, name, date_col FROM {hybrid_table} ORDER BY id",
        "SELECT formatted_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, name, formatted_string FROM {hybrid_table} ORDER BY id",
        "SELECT id, value, formatted_string FROM {hybrid_table} WHERE length(formatted_string) >= 5 ORDER BY id",
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
@Name("string transformation chain")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test alias column: formatted_string ALIAS concat(upper(substring(name, 1, 1)), lower(substring(name, 2)))."""
    Scenario(run=string_transformation_chain)
    Scenario(run=string_transformation_chain_in_watermark)

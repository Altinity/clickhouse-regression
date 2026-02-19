from testflows.core import *
from ...outline import outline
from ...requirements import *

from helpers.tables import *
from helpers.common import getuid


@TestScenario
def insert_select_from_hybrid_with_alias(self):
    """
    Test INSERT INTO ... SELECT from hybrid table including alias columns.
    The alias values should materialize into the target table as regular data.
    """
    base_columns = [
        {"name": "id", "datatype": "Int32"},
        {"name": "value", "datatype": "Int32"},
        {"name": "date_col", "datatype": "Date"},
    ]
    alias_columns = [
        {"name": "computed", "expression": "value * 2", "hybrid_type": "Int64"},
    ]
    watermark = {"left_predicate": "date_col >= '2025-01-15'", "right_predicate": "date_col < '2025-01-15'"}
    expected = {"exitcode": 0, "error_message": None}
    test_queries = [
        "SELECT id, computed FROM {hybrid_table} ORDER BY id",
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
@Name("insert select alias")
def feature(self, minio_root_user=None, minio_root_password=None):
    """Test INSERT INTO ... SELECT from hybrid table with alias columns."""
    Scenario(run=insert_select_from_hybrid_with_alias)

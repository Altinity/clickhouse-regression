from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import *
from helpers.datatypes import *

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Create,
    RQ_ClickHouse_Hybrid_FirstSegment,
    RQ_ClickHouse_Hybrid_ExperimentalGate,
)

import iceberg.tests.steps.hybrid as hybrid_steps


@TestScenario
@Name("create and select")
def create_and_select(self):
    """Smoke: Hybrid over two MergeTree segments via remote(), exclusive date watermark."""
    node = self.context.node

    with Given("enable hybrid table"):
        hybrid_steps.enable_hybrid_table()

    with And("create left and right MergeTree segment tables"):
        base_columns = [
            Column(name="id", datatype=Int32()),
            Column(name="value", datatype=Int32()),
            Column(name="date_col", datatype=Date()),
        ]
        left_table_name = f"left_{getuid()}"
        right_table_name = f"right_{getuid()}"

        left_table = create_table(
            name=left_table_name,
            engine="MergeTree",
            columns=base_columns,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        left_table.insert_test_data(cardinality=1, shuffle_values=False)

        right_table = create_table(
            name=right_table_name,
            engine="MergeTree",
            columns=base_columns,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        right_table.insert_test_data(cardinality=1, shuffle_values=False)

    with And("create Hybrid table with remote() first segment"):
        hybrid_table_name = f"hybrid_{getuid()}"
        left_tf = f"remote('localhost', currentDatabase(), '{left_table_name}')"
        right_tf = f"remote('localhost', currentDatabase(), '{right_table_name}')"
        left_predicate = "date_col >= '2025-01-15'"
        right_predicate = "date_col < '2025-01-15'"

        create_table(
            name=hybrid_table_name,
            engine=(
                f"Hybrid({left_tf}, {left_predicate}, {right_tf}, {right_predicate})"
            ),
            columns=base_columns,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with When("select from Hybrid table"):
        result = node.query(
            f"SELECT count() FROM {hybrid_table_name} SETTINGS enable_analyzer = 1"
        ).output.strip()

    with Then("query returns a numeric count"):
        assert result.isdigit(), error()

    with And("drop Hybrid table"):
        node.query(f"DROP TABLE IF EXISTS {hybrid_table_name}")


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Create("1.0"),
    RQ_ClickHouse_Hybrid_FirstSegment("1.0"),
    RQ_ClickHouse_Hybrid_ExperimentalGate("1.0"),
)
@Name("smoke")
def feature(self):
    """Minimal Hybrid create + SELECT."""
    Scenario(run=create_and_select)

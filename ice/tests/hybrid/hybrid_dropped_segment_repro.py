from testflows.core import *

from helpers.tables import *
from helpers.datatypes import *


@TestSuite
def hybrid_dropped_segment_repro(self):
    """
    Reproduce the issue where a hybrid table fails to load when a segment table
    is dropped before DETACH/ATTACH or server restart.
    """

    node = self.context.node

    with Given("create base columns"):
        base_columns = [
            Column(name="id", datatype=Int32()),
            Column(name="value", datatype=Int32()),
            Column(name="name", datatype=String()),
        ]

    with And("create left and right tables"):
        left_table_name = f"left_{getuid()}"
        right_table_name = f"right_{getuid()}"

        with By("create left table and populate it with test data"):
            left_table = create_table(
                name=left_table_name,
                engine="MergeTree",
                columns=base_columns,
                order_by="id",
            )
            left_table.insert_test_data(cardinality=1, shuffle_values=False)

        with And("create right table and populate it with test data"):
            right_table = create_table(
                name=right_table_name,
                engine="MergeTree",
                columns=base_columns,
                order_by="id",
            )
            right_table.insert_test_data(cardinality=1, shuffle_values=False)

    with And("create hybrid table"):
        hybrid_table_name = f"hybrid_{getuid()}"

        left_table_func = f"remote('localhost', currentDatabase(), '{left_table_name}')"
        left_predicate = "id < 10000"
        right_table_func = f"remote('localhost', currentDatabase(), '{right_table_name}')"
        right_predicate = "id >= 1000"
        hybrid_engine = f"Hybrid({left_table_func}, {left_predicate}, {right_table_func}, {right_predicate})"

        create_table(
            name=hybrid_table_name,
            engine=hybrid_engine,
            columns=base_columns,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with When("drop right table"):
        node.query(f"DROP TABLE {right_table_name}")

    with And("restart the server"):
        node.restart_clickhouse(safe=False)

    with Then("check that hybrid table can be dropped"):
        node.query(f"DROP TABLE {hybrid_table_name}")


@TestFeature
def feature(self):
    """
    Reproduce the issue where a hybrid table fails to load when a segment table
    is dropped before DETACH/ATTACH or server restart:
    https://github.com/Altinity/ClickHouse/issues/1347
    """
    Scenario(run=hybrid_dropped_segment_repro)

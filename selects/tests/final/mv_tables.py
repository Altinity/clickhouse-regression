from selects.requirements import *
from selects.tests.steps import *


@TestScenario
def table_with_materialized_view(self, table_engine):
    """ """
    node = self.context.cluster.node("clickhouse1")
    uid = getuid()

    core_table = f"table_A{uid}"
    mv_1 = f"table_A_d{uid}"
    mv_1_table = f"table_B{uid}"

    with Given("I create data table"):
        node.query(
            f"create table if not exists {core_table} (x String, sign Int8 DEFAULT 1, version Int8 DEFAULT 1)"
            f" engine={table_engine} ORDER BY x SETTINGS force_select_final=1;"
        )

    with And("I create mv dependent table"):
        node.query(
            f"CREATE table {mv_1_table}"
            "( x String, sign Int8 DEFAULT 1)"
            f" ENGINE = {table_engine} ORDER BY x;"
        )

    with And("I add materialized view"):
        node.query(
            f"CREATE MATERIALIZED VIEW {mv_1}"
            f" TO {mv_1_table}"
            " AS SELECT x AS y, sign "
            f"FROM {core_table} GROUP BY sign, y;"
        )
        pause()


@TestFeature
@Name("mv_tables")
@Requirements()
def feature(self, use_transaction_for_atomic_insert=True):
    """"""
    self.context.use_transaction_for_atomic_insert = use_transaction_for_atomic_insert

    if self.context.stress:
        self.context.engines = [
            "ReplacingMergeTree()",
            "CollapsingMergeTree(sign)",
            "SummingMergeTree()",
            "AggregatingMergeTree()",
        ]
    else:
        self.context.engines = ["ReplacingMergeTree()"]

    for table_engine in self.context.engines:
        with Feature(f"{table_engine}"):
            for scenario in loads(current_module(), Scenario):
                scenario(table_engine=table_engine)

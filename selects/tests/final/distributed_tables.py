from selects.requirements import *
from selects.tests.steps import *


@TestScenario
def distributed_tables(
    self,
    table_engine,
):
    """Check that 'force_select_final' works correctly with distributed tables. Test creates distributed table over
    core table and makes insert and checks data is selecting on all shards with `FINAL` modifier.
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")

    core_table = f"table_A{uid}"
    core_table_d = f"table_A_d{uid}"
    cluster = "replicated_cluster"

    with Given("I create data table"):
        create_table(
            core_table=core_table,
            core_table_engine=table_engine,
            distributed=True,
            cluster=cluster,
            distributed_table=core_table_d,
        )

    with And(f"I insert into distributed table"):
        insert_into_table(table_name=core_table_d, row_number=4, equal_rows=True)

    with Then(
        "I check data inserted into distributed table on all shards with `FINAL` modifier"
    ):
        select(table_name=core_table_d, output=4)


@TestFeature
@Name("distributed tables")
@Requirements(
    RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines(
        "1.0"
    )
)
def feature(self):
    """Check 'force_select_final' setting works correctly with distributed tables."""
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

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

    try:
        with Given("I create data table"):
            node.query(
                f"create table if not exists {core_table} (x String, sign Int8 DEFAULT 1, version Int8 DEFAULT 1)"
                f" engine={table_engine} ORDER BY x SETTINGS force_select_final=1;"
            )

        with And("I create distributed table over data table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {core_table_d}  ON CLUSTER '{cluster}'"
                f" as {core_table}"
                " ENGINE = Distributed"
                f"({cluster}, currentDatabase(), {core_table})",
                steps=False,
            )

        with And(f"I insert into distributed table"):
            pause()
            node.query(f"insert into {core_table_d} values ('abc',1, 1);")
            node.query(f"insert into {core_table_d} values ('abc',1, 1);")

        with Then(
            "I check data inserted into distributed table on all shards with `FINAL` modifier"
        ):
            with By(f"checking table {core_table_d}"):
                for node_name in self.context.cluster.nodes["clickhouse"]:
                    with When(f"on {node_name} "):
                        retry(
                            self.context.cluster.node(node_name).query,
                            timeout=100,
                            delay=1,
                        )(
                            f"select count() from {core_table_d}",
                            message="1",
                            exitcode=0,
                        )
                        pause()
    finally:
        with Finally("I drop tables"):
            node.query(f"DROP TABLE {core_table};")
            node.query(f"DROP TABLE {core_table_d} ON CLUSTER '{cluster}';")


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

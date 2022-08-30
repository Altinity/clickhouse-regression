from atomic_insert.requirements import *
from atomic_insert.tests.steps import *


@TestScenario
def user_rights(
    self,
    table_engine,
    failure_mode,
):
    """Check that atomic insert works correctly with nit enough user rights."""
    node = self.context.cluster.node("clickhouse1")
    uid = getuid()

    database = f"test_database{uid}"

    tables = [
        f"test_database{uid}.table_A{uid}",
        f"test_database{uid}.table_B{uid}",
        f"test_database{uid}.table_B_mv{uid}",
    ]

    if table_engine.startswith("Replicated"):
        with Given("I create database and core table on cluster in this database"):
            create_table_on_cluster(
                table_engine=table_engine,
                node=node,
                database=database,
                core_table=tables[0],
            )

        with And("I add materialized view"):
            materialized_view_on_cluster(
                table_engine=table_engine,
                node=node,
                core_table=tables[0],
                mv_1=tables[2],
                mv_1_table=tables[1],
                failure_mode=failure_mode,
            )

        with And("I make insert into core table from user with not enough permissions"):
            for i in range(1):
                When(f"I make insert #{i}", test=insert, parallel=True)(
                    core_table=tables[0], failure_mode=failure_mode
                )

        with And(
            "I check data is not inserted to core table"
            "and any of its dependent tables on any of the cluster nodes"
        ):
            for node_name in self.context.cluster.nodes["clickhouse"]:
                for table_name in tables:
                    with When(f"table {table_name}"):
                        self.context.cluster.node(node_name).query(
                            f"select count()+737 from {table_name}",
                            message="737",
                            exitcode=0,
                        )

    else:
        with Given("I create database and core table in this database"):
            create_table(
                table_engine=table_engine,
                node=node,
                database=database,
                core_table=tables[0],
            )

        with And("I add materialized view with one of failure modes"):
            materialized_view(
                table_engine=table_engine,
                node=node,
                core_table=tables[0],
                mv_1=tables[2],
                mv_1_table=tables[1],
                failure_mode=failure_mode,
            )

        with And("I add readonly user"):
            node.query("CREATE USER OR REPLACE ivan SETTINGS readonly = 1")

        with And("I make insert from user with not enough permissions", flags=XFAIL):
            node.query(
                f"INSERT INTO {tables[0]} SELECT now() + number/10, toString(number%9999),"
                " number % 999"
                " FROM numbers(1000001)",
                settings=[("user", "ivan")],
                timeout=3000,
                message="ivan: Not enough privileges.",
                exitcode=497,
            )

        with And("I drop created user"):
            node.query("DROP USER IF EXISTS ivan")

        with And(
            "I check data is not inserted to core and any of its dependent tables"
        ):
            for table_name in tables:
                with When(f"table {table_name}"):
                    node.query(
                        f"SELECT count()+737 FROM {table_name}",
                        message="737",
                        exitcode=0,
                    )


@TestFeature
@Name("user_rights")
@Requirements(RQ_SRS_028_ClickHouse_AtomicInserts_Failures_UserRights("1.0"))
def feature(self):
    """Check atomic insert in presence of a query issues by a user that does not have
    enough rights either on the target table or one of its dependent tables."""
    if self.context.stress:
        self.context.engines = [
            "MergeTree",
            "SummingMergeTree",
            "ReplacingMergeTree",
            "AggregatingMergeTree",
            "CollapsingMergeTree",
            "VersionedCollapsingMergeTree",
            "GraphiteMergeTree",
            "ReplicatedMergeTree",
            "ReplicatedSummingMergeTree",
            "ReplicatedReplacingMergeTree",
            "ReplicatedAggregatingMergeTree",
            "ReplicatedCollapsingMergeTree",
            "ReplicatedVersionedCollapsingMergeTree",
            "ReplicatedGraphiteMergeTree",
        ]
    else:
        self.context.engines = ["MergeTree", "ReplicatedMergeTree"]

    failure_mode = ["dummy"]

    falure_mode_1 = ["dummy", "throwIf"]

    for table_engine in self.context.engines:
        for fail in failure_mode:
            with Feature(f"{table_engine}"):
                for scenario in loads(current_module(), Scenario):
                    scenario(table_engine=table_engine, failure_mode=fail)

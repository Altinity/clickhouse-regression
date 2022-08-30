from atomic_insert.requirements import *
from atomic_insert.tests.steps import *


@TestScenario
def table_with_materialized_view(self, table_engine, failure_mode):
    """Check atomic insert by making simple insert with different failure mode in chain of core table
    (single and on cluster) with single materialized view table_B_mv with dependent table_B.
    """
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

        with And("I add materialized view with one of failure modes"):
            materialized_view_on_cluster(
                table_engine=table_engine,
                node=node,
                core_table=tables[0],
                mv_1=tables[2],
                mv_1_table=tables[1],
                failure_mode=failure_mode,
            )

        with And("I make insert into core table"):
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

        if self.context.use_transaction_for_atomic_insert:
            with And("I make insert with trowIf fail", flags=XFAIL):
                node.query(
                    f"BEGIN TRANSACTION;"
                    f"INSERT INTO {tables[0]}"
                    " SELECT now() + number/10, toString(number),"
                    " if(5,"
                    " throwIf(number=5,'block fail'), number)"
                    f" FROM numbers(10)"
                    " SETTINGS max_block_size=1,"
                    f" min_insert_block_size_bytes=1;",
                    exitcode=139,
                )
                node.query("ROLLBACK")

        else:
            with And("I make insert"):
                for i in range(1):
                    When(f"I make insert #{i}", test=simple_insert, parallel=True)(
                        core_table=tables[0], failure_mode=failure_mode
                    )

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


@TestScenario
def table_with_materialized_view_cascading(self, table_engine, failure_mode):
    """Check atomic insert by making simple insert with different failure mode in chain of core table
    (single and on cluster) with cascading materialized views and dependent table_B and table_C.
    """
    node = self.context.cluster.node("clickhouse1")
    uid = getuid()
    keeper_cluster_nodes = self.context.cluster.nodes["clickhouse"]

    database = f"test_database{uid}"

    tables = [
        f"test_database{uid}.table_A{uid}",
        f"test_database{uid}.table_B{uid}",
        f"test_database{uid}.table_B_mv{uid}",
        f"test_database{uid}.table_C{uid}",
        f"test_database{uid}.table_C_mv{uid}",
    ]

    if table_engine.startswith("Replicated"):
        with Given("I instrument logs on all keeper cluster nodes"):
            instrument_cluster_nodes(test=self, cluster_nodes=keeper_cluster_nodes)

        with And("I create database and core table on cluster in this database"):
            create_table_on_cluster(
                table_engine=table_engine,
                node=node,
                database=database,
                core_table=tables[0],
            )

        with And(
            "I add cascading materialized view on cluster with one of failure modes"
        ):
            materialized_view_on_cluster(
                table_engine=table_engine,
                node=node,
                core_table=tables[0],
                mv_1=tables[2],
                mv_1_table=tables[1],
                mv_2=tables[4],
                mv_2_table=tables[3],
                cascading=True,
                failure_mode=failure_mode,
            )

        with And("I make insert"):
            for i in range(1):
                When(f"I make insert #{i}", test=insert, parallel=True)(
                    core_table=tables[0], failure_mode=failure_mode
                )

        with And(
            "I check data is not inserted to core and any of its "
            "dependent tables on any of the cluster nodes"
        ):
            for node_name in self.context.cluster.nodes["clickhouse"]:
                for table_name in tables:
                    with When(f"on {node_name} table {table_name}"):
                        retry(
                            self.context.cluster.node(node_name).query,
                            timeout=100,
                            delay=1,
                        )(
                            f"SELECT count()+737 FROM {table_name}",
                            message="737",
                            exitcode=0,
                        )

    else:
        with Given("I create database and core table on cluster in this database"):
            create_table(
                table_engine=table_engine,
                node=node,
                database=database,
                core_table=tables[0],
            )

        with And("I add cascading materialized view with one of failure modes"):
            materialized_view(
                table_engine=table_engine,
                node=node,
                core_table=tables[0],
                mv_1=tables[2],
                mv_1_table=tables[1],
                mv_2=tables[4],
                mv_2_table=tables[3],
                cascading=True,
                failure_mode=failure_mode,
            )

        with And("I make insert"):
            for i in range(1):
                When(f"I make insert #{i}", test=simple_insert, parallel=True)(
                    core_table=tables[0], failure_mode=failure_mode
                )

        with And(
            "I check data is not inserted to core and any of its dependent tables"
        ):
            for table_name in tables:
                with When(f"table {table_name}"):
                    retry(node.query, timeout=100, delay=1)(
                        f"SELECT count()+737 FROM {table_name}",
                        message="737",
                        exitcode=0,
                    )


@TestOutline
def materialized_view_some_view(self, table_engine, view_type, failure_mode):
    """Check atomic insert by making simple insert with some failure mode in chain of core table with materialized view
    and some view.
    """
    node = self.context.cluster.node("clickhouse1")
    uid = getuid()

    database = f"test_database{uid}"

    tables = [
        f"test_database{uid}.table_A{uid}",
        f"test_database{uid}.table_B{uid}",
        f"test_database{uid}.table_B_mv{uid}",
        f"test_database{uid}.table_C_v{uid}",
    ]

    with Given("I create core table "):
        create_table(
            table_engine=table_engine,
            node=node,
            database=database,
            core_table=tables[0],
        )

    with And("I add some mv/view section"):
        materialized_some_view(
            table_engine=table_engine,
            node=node,
            core_table=tables[0],
            mv_1=tables[2],
            mv_1_table=tables[1],
            view_1=tables[3],
            view_type=view_type,
            failure_mode=failure_mode,
        )

    with And("I make insert"):
        for i in range(1):
            When(f"I make insert #{i}", test=simple_insert, parallel=True)(
                core_table=tables[0], failure_mode=failure_mode
            )

    with And("I check data is not inserted to core and any of its dependent tables"):
        for table_name in tables:
            with When(f"table {table_name}"):
                retry(node.query, timeout=100, delay=1)(
                    f"SELECT count()+737 FROM {table_name}", message="737", exitcode=0
                )


@TestScenario
def materialized_view_normal_view(self, table_engine, failure_mode):
    """Check atomic insert by making simple insert with some failure mode in chain of core table with materialized view
    and normal view.
    """
    if table_engine.startswith("Replicated"):
        pass
    else:
        with Given(
            f"I make atomic insert in core table with materialized view and normal view with"
            f" failure mode: {failure_mode}"
        ):
            materialized_view_some_view(
                table_engine=table_engine, view_type="normal", failure_mode=failure_mode
            )


@TestScenario
def materialized_view_live_view(self, table_engine, failure_mode):
    """Check atomic insert by making simple insert with some failure mode in chain of core table with materialized view
    and live view.
    """
    if table_engine.startswith("Replicated"):
        pass
    else:
        with Given(
            f"I make atomic insert in core table with materialized view and live view with"
            f" failure mode: {failure_mode}"
        ):
            materialized_view_some_view(
                table_engine=table_engine, view_type="live", failure_mode=failure_mode
            )


@TestScenario
@Requirements(
    RQ_SRS_028_ClickHouse_AtomicInserts_Failures_CircularDependentTables("1.0")
)
def table_with_circle_materialized_view(self, table_engine, failure_mode):
    """Test to check atomic insert for circular mv dependent tables."""
    node = self.context.cluster.node("clickhouse1")
    uid = getuid()

    database = f"test_database{uid}"

    tables = [f"test_database{uid}.table_A{uid}", f"test_database{uid}.table_B{uid}"]

    if table_engine.startswith("Replicated"):
        pass
    else:
        with Given("I create core table "):
            create_table(
                table_engine=table_engine,
                node=node,
                database=database,
                core_table=tables[0],
            )

        with And("I create circular mv dependent table to core table"):
            materialized_view_circle(node=node, core_table=tables[0], mv_1=tables[1])

        with And("I make insert into core table", flags=XFAIL):
            node.query(
                f"insert into {tables[0]}"
                f" select now() + number/10, toString(number), number"
                f" from numbers(10)"
            )

        with And(
            "I check data is not inserted to core and any of its dependent tables"
        ):
            for table_name in tables:
                with When(f"table {table_name}"):
                    retry(node.query, timeout=100, delay=1)(
                        f"SELECT count()+737 FROM {table_name}",
                        message="737",
                        exitcode=0,
                    )


# @TestScenario
# def materialized_view_window_view(self, table_engine, failure_mode):
#     """Materialized with live view atomic insert test.
#     """
#     materialized_view_some_view(table_engine=table_engine, view_type="window", failure_mode=failure_mode)


@TestFeature
@Name("dependent_tables")
@Requirements(
    RQ_SRS_028_ClickHouse_AtomicInserts_DependentTables("1.0"),
    RQ_SRS_028_ClickHouse_AtomicInserts_SupportedTableEngines_MergeTree("1.0"),
    RQ_SRS_028_ClickHouse_AtomicInserts_SupportedTableEngines_ReplicatedMergeTree(
        "1.0"
    ),
    RQ_SRS_028_ClickHouse_AtomicInserts_Failures_MismatchedTableStructure("1.0"),
    RQ_SRS_028_ClickHouse_AtomicInserts_Failures_OneOrMoreParts("1.0"),
)
def feature(self, use_transaction_for_atomic_insert=True):
    """Atomic insert check for a table which has different dependent tables."""
    self.context.use_transaction_for_atomic_insert = use_transaction_for_atomic_insert

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

    falure_mode_1 = ["dummy", "throwIf", "column type mismatch", "user_rights"]

    for table_engine in self.context.engines:
        for fail in failure_mode:
            with Feature(f"{table_engine}"):
                for scenario in loads(current_module(), Scenario):
                    scenario(table_engine=table_engine, failure_mode=fail)

from atomic_insert.requirements import *
from atomic_insert.tests.steps import *


@TestOutline
def insert_setting(self, table_engine, insert_setting="max_block_size=1"):
    """Check some atomic insert setting option
    :param insert_setting: testing setting
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")

    database = f"test_database{uid}"
    core_table = f"test_database{uid}.table_A{uid}"

    with Given("I create database and core table"):
        create_table(
            table_engine=table_engine,
            node=node,
            database=database,
            core_table=core_table,
        )

    with And(f"I use insert with testing setting {insert_setting}"):
        node.query(
            (
                f"BEGIN TRANSACTION;"
                if self.context.use_transaction_for_atomic_insert
                else ""
            )
            + (
                f"INSERT INTO {core_table}"
                f" SELECT now() + number/10, toString(number), number"
                f" FROM numbers(10)"
                f" SETTINGS {insert_setting};"
            )
            + (f"COMMIT;" if self.context.use_transaction_for_atomic_insert else ""),
            exitcode=0,
        )

    with And(
        "I check data is inserted to the core table and any of its dependent tables"
    ):
        with When(f"table {core_table}"):
            node.query(f"SELECT count() FROM {core_table}", message=f"10", exitcode=0)


@TestOutline
def insert_setting_in_replicated_table_on_cluster(
    self, table_engine, insert_setting="max_block_size=1"
):
    """Check some atomic insert setting option on cluster
    :param insert_setting: testing setting
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")

    database = f"test_database{uid}"
    core_table = f"test_database{uid}.table_A{uid}"

    with Given("I create replicated table on cluster"):
        create_table_on_cluster(
            table_engine=table_engine,
            node=node,
            database=database,
            core_table=core_table,
        )

    with And(f"I use insert with testing setting {insert_setting}"):
        node.query(
            f"insert into {core_table}"
            f" select now() + number/10, toString(number), number"
            f" from numbers(10)"
            f" settings {insert_setting}"
        )

    with And(
        "I check data is not inserted into core tables and any of their dependents on all nodes"
    ):
        for node_name in self.context.cluster.nodes["clickhouse"]:
            with When(f"on {node_name} table {core_table}"):
                node.query(
                    f"select count() from {core_table}", message=f"10", exitcode=0
                )


@TestScenario
def max_block_size_insert_setting(self, table_engine):
    """Check max_block_size setting."""
    if table_engine.startswith("Replicated"):
        insert_setting_in_replicated_table_on_cluster(
            table_engine=table_engine, insert_setting="max_block_size=1"
        )
    else:
        insert_setting(table_engine=table_engine, insert_setting="max_block_size=1")


@TestScenario
def min_insert_block_size_rows_setting(self, table_engine):
    """Check min_insert_block_size_rows setting."""
    if table_engine.startswith("Replicated"):
        insert_setting_in_replicated_table_on_cluster(
            table_engine=table_engine, insert_setting="min_insert_block_size_rows=1"
        )
    else:
        insert_setting(
            table_engine=table_engine, insert_setting="min_insert_block_size_rows=1"
        )


@TestScenario
def input_format_parallel_parsing_setting(self, table_engine):
    """Check input_format_parallel_parsing setting."""
    if table_engine.startswith("Replicated"):
        insert_setting_in_replicated_table_on_cluster(
            table_engine=table_engine, insert_setting="input_format_parallel_parsing=1"
        )
    else:
        insert_setting(
            table_engine=table_engine, insert_setting="input_format_parallel_parsing=1"
        )


@TestScenario
def max_insert_threads_setting(self, table_engine):
    """Check max_insert_threads setting."""
    if table_engine.startswith("Replicated"):
        insert_setting_in_replicated_table_on_cluster(
            table_engine=table_engine, insert_setting="max_insert_threads=1"
        )
    else:
        insert_setting(table_engine=table_engine, insert_setting="max_insert_threads=1")


@TestScenario
def min_insert_block_size_bytes_setting(self, table_engine):
    """Check min_insert_block_size_bytes setting."""
    if table_engine.startswith("Replicated"):
        insert_setting_in_replicated_table_on_cluster(
            table_engine=table_engine, insert_setting="min_insert_block_size_bytes=1"
        )
    else:
        insert_setting(
            table_engine=table_engine, insert_setting="min_insert_block_size_bytes=1"
        )


@TestFeature
@Name("insert settings")
@Requirements(RQ_SRS_028_ClickHouse_AtomicInserts_InsertSettings("1.0"))
def feature(self, use_transaction_for_atomic_insert=True):
    """Check atomic insert support all INSERT settings."""
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

    for table_engine in self.context.engines:
        with Feature(f"{table_engine}"):
            for scenario in loads(current_module(), Scenario):
                scenario(table_engine=table_engine)

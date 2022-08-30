from atomic_insert.requirements import *
from atomic_insert.tests.steps import *


@TestOutline
def block_data_fail(
    self, table_engine, failure_mode, number_of_blocks, fail_block_number=None
):
    """Check atomic insert when there is a failure on a particular data block
    using throwIf function.
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

    with And(
        f"I insert {number_of_blocks} blocks with throwIf fail on {fail_block_number}",
        flags=XFAIL,
    ):
        node.query(
            (
                f"BEGIN TRANSACTION;"
                if self.context.use_transaction_for_atomic_insert
                else ""
            )
            + (
                f"INSERT INTO {core_table}"
                f" SELECT now() + number/10, toString(number), if({fail_block_number},"
                f" throwIf(number={fail_block_number},'block fail'), number)"
                f" FROM numbers({number_of_blocks})"
                " SETTINGS max_block_size=1,"
                " min_insert_block_size_bytes=1;"
            )
            + (f"COMMIT;" if self.context.use_transaction_for_atomic_insert else ""),
            exitcode=139,
        )

        if self.context.use_transaction_for_atomic_insert:
            node.query("ROLLBACK")

    with And("I check data is not inserted to core and any of its dependent tables"):
        with When(f"table {core_table}"):
            node.query(
                f"SELECT count()+1 FROM {core_table}",
                message=f"1",
                exitcode=0,
            )


@TestOutline
def block_data_fail_in_replicated_table_on_cluster(
    self, table_engine, number_of_blocks, fail_block_number, failure_mode
):
    """Check atomic insert when there is a failure on a particular data block
    using throwIf function when inserting into a replicated table on cluster.
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

    with And(
        f"I insert {number_of_blocks} blocks with throwIf fail on {fail_block_number}",
        flags=XFAIL,
    ):
        node.query(
            f"INSERT INTO {core_table}"
            f" SELECT now() + number/10, toString(number), if({fail_block_number},"
            f" throwIf(number={fail_block_number},'block fail'), number)"
            f" FROM numbers({number_of_blocks})"
            " SETTINGS max_block_size=1,"
            " min_insert_block_size_bytes=1;",
            exitcode=139,
        )

        with And(
            "I check data is not inserted into core tables and any of their dependents on all nodes"
        ):
            for node_name in self.context.cluster.nodes["clickhouse"]:
                with When(f"on {node_name} table {core_table}"):
                    if failure_mode == "dummy":
                        node.query(
                            f"SELECT count() FROM {core_table}",
                            message=f"{fail_block_number}",
                            exitcode=0,
                        )
                    else:
                        node.query(
                            f"SELECT count()+1 FROM {core_table}",
                            message=f"1",
                            exitcode=0,
                        )


@TestScenario
def block_data_fail_first_part(self, table_engine, failure_mode):
    """Check failure on the first data block."""
    if table_engine.startswith("Replicated"):
        block_data_fail_in_replicated_table_on_cluster(
            table_engine=table_engine,
            number_of_blocks=10,
            fail_block_number=1,
            failure_mode=failure_mode,
        )
    else:
        block_data_fail(
            table_engine=table_engine,
            number_of_blocks=10,
            fail_block_number=1,
            failure_mode=failure_mode,
        )


@TestScenario
def block_data_fail_middle_part(self, table_engine, failure_mode):
    """Check failure in the middle data block."""
    if table_engine.startswith("Replicated"):
        block_data_fail_in_replicated_table_on_cluster(
            table_engine=table_engine,
            number_of_blocks=10,
            fail_block_number=5,
            failure_mode=failure_mode,
        )
    else:
        block_data_fail(
            table_engine=table_engine,
            number_of_blocks=10,
            fail_block_number=5,
            failure_mode=failure_mode,
        )


@TestScenario
def block_data_fail_last_part(self, table_engine, failure_mode):
    """Check failure on the last data block."""
    if table_engine.startswith("Replicated"):
        block_data_fail_in_replicated_table_on_cluster(
            table_engine=table_engine,
            number_of_blocks=10,
            fail_block_number=9,
            failure_mode=failure_mode,
        )
    else:
        block_data_fail(
            table_engine=table_engine,
            number_of_blocks=10,
            fail_block_number=9,
            failure_mode=failure_mode,
        )


@TestFeature
@Name("block fail")
@Requirements(
    RQ_SRS_028_ClickHouse_AtomicInserts_BlocksAndPartitions("1.0"),
    RQ_SRS_028_ClickHouse_AtomicInserts_Failures_EmulatedUsingThrowIf("1.0"),
)
def feature(self, use_transaction_for_atomic_insert=True):
    """Check atomic insert when block fail has been received during insert
    emulated using throwIf function on replicated and non replicated tables.
    """
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

    for table_engine in self.context.engines:
        for fail in failure_mode:
            with Feature(f"{table_engine}"):
                for scenario in loads(current_module(), Scenario):
                    scenario(table_engine=table_engine, failure_mode=fail)

from atomic_insert.requirements import *
from atomic_insert.tests.steps import *


@TestScenario
def distributed_tables(
    self,
    table_engine,
    failure_mode,
    insert_setting="insert_distributed_one_random_shard=1",
):
    """Check that atomic insert works correctly with distributed tables. Test creates distributed table over
    core table and makes insert with some failure mode and checks data is not inserted
    into distributed table on all shards.
    """
    uid = getuid()
    node = self.context.cluster.node("clickhouse1")

    core_table = f"table_A{uid}"
    core_table_d = f"table_A_d{uid}"
    cluster = "ShardedAndReplicated"

    try:
        with Given("I create data table"):
            node.query(
                f"CREATE TABLE {core_table} ON CLUSTER '{cluster}' "
                "( timestamp DateTime,"
                "host      String,"
                "repsonse_time      Int32"
                f") ENGINE {table_engine}() ORDER BY (host, timestamp)"
            )

        with And("I create distributed table over data table"):
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {core_table_d}  ON CLUSTER '{cluster}'"
                f" as {core_table}"
                " ENGINE = Distributed"
                f"({cluster}, currentDatabase(), {core_table})",
                steps=False,
            )

        if failure_mode == "dummy":
            with And(f"I insert into distributed table with setting {insert_setting}"):
                node.query(
                    f"INSERT INTO {core_table_d}"
                    " SELECT now() + number/10, toString(number), number"
                    f" FROM numbers(10)"
                    " SETTINGS max_block_size=1,"
                    f" min_insert_block_size_bytes=1,{insert_setting};",
                    exitcode=0,
                )
        elif failure_mode == "throwIf":
            with And(
                f"I insert into distributed table with setting {insert_setting}",
                description="""This insert uses to create with 'throwIf' option
                      and should not occur with the atomic insert.""",
                flags=XFAIL,
            ):
                node.query(
                    f"INSERT INTO {core_table_d}"
                    " SELECT now() + number/10, toString(number), if(5,"
                    " throwIf(number=5,'block fail'), number)"
                    f" FROM numbers(10)"
                    " SETTINGS max_block_size=1,"
                    f" min_insert_block_size_bytes=1,{insert_setting};",
                    exitcode=139,
                )

        elif failure_mode == "user_rights":
            node_name = "clickhouse1"
            with Given("I add readonly user"):
                self.context.cluster.node(node_name).query(
                    "CREATE USER OR REPLACE ivan SETTINGS readonly = 1"
                )

            with And(
                "I make insert from user with not enough permissions", flags=XFAIL
            ):
                self.context.cluster.node(node_name).query(
                    f"INSERT INTO {core_table} SELECT now() + number/10, toString(number%9999),"
                    " number % 999"
                    " FROM numbers(1000001)",
                    settings=[("user", "ivan")],
                    timeout=3000,
                    message="ivan: Not enough privileges.",
                    exitcode=497,
                )

            with And("I drop created user"):
                self.context.cluster.node(node_name).query("DROP USER IF EXISTS ivan")

        with Then("I check data is not inserted into distributed table on all shards"):
            with By(f"checking table {core_table_d}"):
                if failure_mode == "dummy":
                    for node_name in self.context.cluster.nodes["clickhouse"]:
                        with When(f"on {node_name} "):
                            retry(
                                self.context.cluster.node(node_name).query,
                                timeout=100,
                                delay=1,
                            )(
                                f"SELECT count() FROM {core_table_d}",
                                message=f"10",
                                exitcode=0,
                            )
                elif failure_mode == "throwIf":
                    for node_name in self.context.cluster.nodes["clickhouse"]:
                        with When(f"on {node_name} "):
                            retry(
                                self.context.cluster.node(node_name).query,
                                timeout=100,
                                delay=1,
                            )(
                                f"SELECT count() FROM {core_table_d}",
                                message=f"5",
                                exitcode=0,
                            )
                elif failure_mode == "user_rights":
                    for node_name in self.context.cluster.nodes["clickhouse"]:
                        with When(f"on {node_name} "):
                            retry(
                                self.context.cluster.node(node_name).query,
                                timeout=100,
                                delay=1,
                            )(
                                f"SELECT count()+1 FROM {core_table_d}",
                                message=f"1",
                                exitcode=0,
                            )

    finally:
        with Finally("I drop tables"):
            node.query(f"DROP TABLE {core_table} ON CLUSTER '{cluster}';")
            node.query(f"DROP TABLE {core_table_d} ON CLUSTER '{cluster}';")


@TestFeature
@Name("distributed table")
@Requirements(RQ_SRS_028_ClickHouse_AtomicInserts_DistributedTable("1.0"))
def feature(self):
    """Check atomic insert works correctly with distributed tables."""
    if self.context.stress:
        self.context.engines = [
            "ReplicatedMergeTree",
            "ReplicatedSummingMergeTree",
            "ReplicatedReplacingMergeTree",
            "ReplicatedAggregatingMergeTree",
            "ReplicatedCollapsingMergeTree",
            "ReplicatedVersionedCollapsingMergeTree",
            "ReplicatedGraphiteMergeTree",
        ]
    else:
        self.context.engines = ["ReplicatedMergeTree"]

    failure_mode = ["dummy"]

    falure_mode_1 = ["dummy", "throwIf", "user_rights"]

    for table_engine in self.context.engines:
        for fail in failure_mode:
            with Feature(f"{table_engine}"):
                for scenario in loads(current_module(), Scenario):
                    scenario(table_engine=table_engine, failure_mode=fail)

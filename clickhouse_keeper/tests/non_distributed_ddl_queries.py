from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl import *


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_NonDistributedDDLQuery_RenameReplicatedTable("1.0")
)
def rename(self):
    """Check that RENAME command works correctly in non-distributed mode when it is used
    towards replicated table.
    """
    with Given("Receive UID"):
        uid = getuid()
    try:
        with And("I create replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

    finally:
        with When("I rename created table on clickhouse1 node"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"RENAME TABLE {table_name} TO test_rename{uid}",
                exitcode=0,
                steps=False,
            )

        with And("I check that table renamed only on this node"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                "SHOW TABLES", message=f"test_rename{uid}", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                "SHOW TABLES", message=f"{table_name}", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse3").query, timeout=100, delay=1)(
                "SHOW TABLES", message=f"{table_name}", exitcode=0, steps=False
            )

        with And("I insert data into replica of renamed table"):
            table_insert(node_name="clickhouse2", table_name=f"{table_name}")

        with And("I check that data inserted into renamed table"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"select * from test_rename{uid} FORMAT CSV",
                message="1,111",
                exitcode=0,
                steps=False,
            )

        with And("I drop renamed table"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"DROP TABLE test_rename{uid} ", exitcode=0, steps=False
            )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_NonDistributedDDLQuery_DropReplicatedTable("1.0")
)
def drop(self):
    """Check that Drop command works correctly in non-distributed mode when it is used
    towards replicated table.
    """
    with Given("Receive UID"):
        uid = getuid()
    try:
        with And("I create replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

    finally:
        with And("I use 'drop table' towards table"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"DROP TABLE {table_name}", exitcode=0, steps=False
            )

        with And("I check that table dropped only on this node"):
            self.context.cluster.node("clickhouse1").query(
                f"insert into {table_name}(id, partition) values (1,1)",
                exitcode=60,
                message=f"DB::Exception: Table default.{table_name} doesn't exist.",
            )
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                "SHOW TABLES", message=f"{table_name}", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse3").query, timeout=100, delay=1)(
                "SHOW TABLES", message=f"{table_name}", exitcode=0, steps=False
            )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_NonDistributedDDLQuery_TruncateReplicatedTable("1.0")
)
def truncate(self):
    """Check that TRUNCATE command delete information from only 1 shard in non-distributed mode
    when it is used towards replicated table.
    """
    with Given("Receive UID"):
        uid = getuid()
    try:
        with And("I create replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I insert data into all shards of the table"):
            table_insert(node_name="clickhouse1", table_name=f"{table_name}")
            table_insert(node_name="clickhouse4", table_name=f"{table_name}")
            table_insert(node_name="clickhouse7", table_name=f"{table_name}")

    finally:
        with When("I use 'truncate' towards created table on clickhouse1 node"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"TRUNCATE TABLE {table_name}", exitcode=0, steps=False
            )

        with And("I check that data deleted only on 1 shard"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"select * from {table_name} FORMAT CSV", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse4").query, timeout=100, delay=1)(
                f"select * from {table_name} FORMAT CSV",
                message="1,111",
                exitcode=0,
                steps=False,
            )
            retry(self.context.cluster.node("clickhouse7").query, timeout=100, delay=1)(
                f"select * from {table_name} FORMAT CSV",
                message="1,111",
                exitcode=0,
                steps=False,
            )


@TestScenario
@Requirements(
    RQ_SRS_024_ClickHouse_Keeper_NonDistributedDDLQuery_CreateReplicatedTable("1.0")
)
def create(self):
    """Check that Create command works correctly in non-distributed mode when it is used
    without "ON CLUSTER" option.
    """
    node = self.context.cluster.node("clickhouse1")

    with Given("Receive UID"):
        uid = getuid()
    try:
        with And(
            "I create replicated table without 'ON CLUSTER' option on two replicas"
        ):
            table_name = f"test{uid}"
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name}"
                " (Id Int32, partition Int32 ) "
                "ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "ORDER BY Id PARTITION BY partition",
                steps=False,
            )
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name}"
                " (Id Int32, partition Int32 ) "
                "ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "ORDER BY Id PARTITION BY partition",
                steps=False,
            )
            retry(self.context.cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name}"
                " (Id Int32, partition Int32 ) "
                "ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "ORDER BY Id PARTITION BY partition",
                steps=False,
            )

        with And("I make insert in clickhouse1 table"):
            table_insert(table_name=table_name)

        with And("I select data on other replicas"):
            table_select(node_name="clickhouse2", table_name=table_name)
            table_select(node_name="clickhouse3", table_name=table_name)
    finally:
        with Finally(
            "I use 'drop table' towards table on clickhouse1 and clickhouse2 nodes"
        ):
            retry(node.query, timeout=100, delay=1)(
                f"DROP TABLE {table_name}", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse2").query, timeout=100, delay=1)(
                f"DROP TABLE {table_name}", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse3").query, timeout=100, delay=1)(
                f"DROP TABLE {table_name}", exitcode=0, steps=False
            )


@TestFeature
@Name("non_distributed_ddl_queries")
def feature(self):
    """
    Check that clickhouse-keeper controlled replicated tables
    works correctly with non-distributed DDL queries.
    """
    with Given("I start mixed ClickHouse cluster"):
        if self.context.ssl == "false":
            start_mixed_keeper()
        else:
            start_mixed_keeper_ssl()

    for scenario in loads(current_module(), Scenario):
        scenario()

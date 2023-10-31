from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_ClickHouseOperation_Insert("1.0"))
def insert(self):
    """Check that INSERT command is synchronized via keeper servers
    when one of the ClickHouse server nodes is temporary unavailable."""
    cluster = self.context.cluster
    with Given("Receive UID"):
        uid = getuid()

    with And("I create simple table"):
        table_name = f"test{uid}"
        create_simple_table(table_name=table_name)

    with And("I stop clickhouse server 1 node"):
        cluster.node("clickhouse1").stop_clickhouse()

    with When("I make simple insert ClickHouse server 2 node"):
        table_insert(node_name="clickhouse2", table_name=table_name)

    with Then("I start clickhouse server 1 node"):
        cluster.node("clickhouse1").start_clickhouse()

    with And("I check correctness of data on ClickHouse server 1 node"):
        table_select(node_name="clickhouse1", table_name=table_name)


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_DistributedDDLQuery_CreateQueries("1.0"))
def create(self):
    """Check that CREATE command is synchronized via keeper servers
    when one of the ClickHouse server nodes is temporary unavailable."""
    cluster = self.context.cluster
    with Given("Receive UID"):
        uid = getuid()

    with And("I stop clickhouse1 node"):
        cluster.node("clickhouse1").stop_clickhouse()

    with When("I create simple table and I start clickhouse1 node"):
        Step("I create simple table", test=create_simple_table, parallel=True)(
            node=self.context.cluster.node("clickhouse2"), table_name=f"test{uid}"
        )

        with Step("I start clickhouse1 node"):
            cluster.node("clickhouse1").start_clickhouse()

        join()

    with Then("I check the table is created"):
        retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
            "SHOW TABLES", message=f"test{uid}", exitcode=0, steps=False
        )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_DistributedDDLQuery_DROP("1.0"))
def drop(self):
    """Check that DROP command is synchronized via keeper servers
    when one of the ClickHouse server nodes is temporary unavailable.
    """
    cluster = self.context.cluster

    with Given("Receive UID"):
        uid = getuid()

    with And("I create simple table"):
        table_name = f"test{uid}"
        create_simple_table(table_name=table_name, manual_cleanup=True)

        with When("I stop clickhouse1 node"):
            cluster.node("clickhouse1").stop_clickhouse()

    with When("I try dropping table when clickhouse1 node is stopped"):
        Step(
            "I try dropping table",
            test=drop_table,
            parallel=True,
        )(table_name=table_name)

        with Step("I restart clickhouse1 stopped node"):
            cluster.node("clickhouse1").start_clickhouse()

        join()

    with Then("I check the table doesn't exist."):
        message = (
            "DB::Exception: Table default.{table_name} doesn't exist."
            if check_clickhouse_version("<23.8")(self)
            else "DB::Exception: Table default.{table_name} does not exist."
        )

        self.context.cluster.node("clickhouse2").query(
            f"insert into {table_name}(id, partition) values (1,1)",
            exitcode=60,
            message=message.format(table_name=table_name),
        )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_DistributedDDLQuery_TRUNCATE("1.0"))
def truncate(self):
    """Check that TRUNCATE command delete all data from replicated table
    when it is used in 'on cluster mode'.
    """
    with Given("Receive UID"):
        uid = getuid()

    try:
        with And("I create replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name, manual_cleanup=True)

        with And("I insert data into all shards of the table"):
            table_insert(node_name="clickhouse1", table_name=f"{table_name}")
            table_insert(node_name="clickhouse4", table_name=f"{table_name}")
            table_insert(node_name="clickhouse7", table_name=f"{table_name}")

        with When(
            "I use 'truncate on cluster' towards created table on clickhouse1 node"
        ):
            cluster_name = "'Cluster_3shards_with_3replicas'"
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"TRUNCATE TABLE {table_name} ON CLUSTER {cluster_name}",
                exitcode=0,
                steps=False,
            )

        with Then("I check that data deleted on all shards"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"select * from {table_name} FORMAT CSV", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse4").query, timeout=100, delay=1)(
                f"select * from {table_name} FORMAT CSV", exitcode=0, steps=False
            )
            retry(self.context.cluster.node("clickhouse7").query, timeout=100, delay=1)(
                f"select * from {table_name} FORMAT CSV", exitcode=0, steps=False
            )

    finally:
        with Finally("I drop table"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"DROP TABLE {table_name} ON CLUSTER {cluster_name}",
                exitcode=0,
                steps=False,
            )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_DistributedDDLQuery_RENAME("1.0"))
def rename(self):
    """Check that RENAME command works correctly in 'ON CLUSTER' mode when it is used
    towards replicated table.
    """
    with Given("Receive UID"):
        uid = getuid()

    try:
        with And("I create replicated table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with When("I rename created table on clickhouse1 node"):
            cluster_name = "'Cluster_3shards_with_3replicas'"
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"RENAME TABLE {table_name} TO test_rename{uid} ON CLUSTER {cluster_name}",
                exitcode=0,
                steps=False,
            )

        with Then("I check that table renamed on all shards"):
            for name in self.context.cluster.nodes["clickhouse"][:9]:
                retry(self.context.cluster.node(name).query, timeout=100, delay=1)(
                    "SHOW TABLES", message=f"test_rename{uid}", exitcode=0, steps=False
                )

        with And("I insert data into replica of renamed table"):
            table_insert(node_name="clickhouse2", table_name=f"test_rename{uid}")

        with And("I check that data inserted into renamed table"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"select * from test_rename{uid} FORMAT CSV",
                message="1,111",
                exitcode=0,
                steps=False,
            )

    finally:
        with Finally("I drop renamed table"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"DROP TABLE test_rename{uid}  ON CLUSTER {cluster_name}",
                exitcode=0,
                steps=False,
            )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_DistributedDDLQuery_ATTACH("1.0"))
def attach(self):
    """Check that ATTACH command works correctly in 'ON CLUSTER' mode when it is used
    towards replicated table.
    """
    with Given("Receive UID"):
        uid = getuid()

    try:
        with And("I create table function"):
            table_name = f"test{uid}"
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"INSERT INTO TABLE FUNCTION file('01188_attach/test/data.TSV', 'TSV', 's String, n UInt8')"
                f" VALUES ('test', 42)",
                exitcode=0,
                steps=False,
            )

        with When("I attach table on cluster"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"ATTACH TABLE test FROM '01188_attach/test' (s String, n UInt8) ENGINE = File(TSV);",
                exitcode=0,
                steps=False,
            )

        with Then("I check that table attached"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"select * from test", exitcode=0, message="test\t42", steps=False
            )
    finally:
        with Finally("I drop table"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                f"drop table test", exitcode=0, steps=False
            )


@TestScenario
@Requirements(RQ_SRS_024_ClickHouse_Keeper_DistributedDDLQuery_DETACH("1.0"))
def detach(self):
    """Check that DETACH command works correctly in 'ON CLUSTER' mode when it is used
    towards replicated table.
    """
    with Given("Receive UID"):
        uid = getuid()

    with And("I create replicated table"):
        table_name = f"test{uid}"
        create_simple_table(table_name=table_name)

    with When("I detach created table on clickhouse1 node"):
        cluster_name = "'Cluster_3shards_with_3replicas'"
        retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
            f"DETACH TABLE {table_name} ON CLUSTER {cluster_name}",
            exitcode=0,
            steps=False,
        )

    with Then("I check that table detached on all shards"):
        message = (
            "DB::Exception: Table default.{table_name} doesn't exist."
            if check_clickhouse_version("<23.8")(self)
            else "DB::Exception: Table default.{table_name} does not exist."
        )

        for name in self.context.cluster.nodes["clickhouse"][:9]:
            retry(self.context.cluster.node(name).query, timeout=100, delay=1)(
                f"select * from {table_name}",
                message=message.format(table_name=table_name),
                exitcode=60,
                steps=False,
            )


@TestFeature
@Name("synchronization")
def feature(self):
    """Check data synchronization between replicas for different DDL queries."""
    with Given("I create remote config"):
        if self.context.ssl == "false":
            entries = {
                "Cluster_3shards_with_3replicas": [
                    {
                        "shard": [
                            {"replica": {"host": "clickhouse1", "port": "9000"}},
                            {"replica": {"host": "clickhouse2", "port": "9000"}},
                            {"replica": {"host": "clickhouse3", "port": "9000"}},
                        ]
                    },
                    {
                        "shard": [
                            {"replica": {"host": "clickhouse4", "port": "9000"}},
                            {"replica": {"host": "clickhouse5", "port": "9000"}},
                            {"replica": {"host": "clickhouse6", "port": "9000"}},
                        ]
                    },
                    {
                        "shard": [
                            {"replica": {"host": "clickhouse7", "port": "9000"}},
                            {"replica": {"host": "clickhouse8", "port": "9000"}},
                            {"replica": {"host": "clickhouse9", "port": "9000"}},
                        ]
                    },
                ]
            }

            create_remote_configuration(entries=entries, modify=True)

            with Given("I start mixed ClickHouse cluster"):
                start_mixed_keeper()
        else:
            entries = {
                "Cluster_3shards_with_3replicas": [
                    {
                        "shard": [
                            {
                                "replica": {
                                    "host": "clickhouse1",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                            {
                                "replica": {
                                    "host": "clickhouse2",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                            {
                                "replica": {
                                    "host": "clickhouse3",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                        ]
                    },
                    {
                        "shard": [
                            {
                                "replica": {
                                    "host": "clickhouse4",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                            {
                                "replica": {
                                    "host": "clickhouse5",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                            {
                                "replica": {
                                    "host": "clickhouse6",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                        ]
                    },
                    {
                        "shard": [
                            {
                                "replica": {
                                    "host": "clickhouse7",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                            {
                                "replica": {
                                    "host": "clickhouse8",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                            {
                                "replica": {
                                    "host": "clickhouse9",
                                    "port": "9440",
                                    "secure": "1",
                                }
                            },
                        ]
                    },
                ]
            }

            create_configuration_ssl(entries=entries, modify=True)

            with Given("I start mixed ClickHouse cluster"):
                start_mixed_keeper_ssl()

    for scenario in loads(current_module(), Scenario):
        scenario()

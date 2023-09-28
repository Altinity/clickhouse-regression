import time

from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log

transactions = {
    "allow_experimental_transactions": "42",
    "merge_tree": {
        "old_parts_lifetime": "100500",
        "remove_rolled_back_parts_immediately": "0",
    },
    "transactions_info_log": {
        "database": "system",
        "table": "transactions_info_log",
        "flush_interval_milliseconds": "7500",
    },
}


@TestStep(Given)
def add_config_section(
    self,
    config,
    timeout=300,
    restart=False,
    modify=False,
    node=None,
    user=None,
    wait_healthy=True,
    check_preprocessed=True,
):
    """Add config on cluster nodes."""
    return add_config(
        config=config,
        restart=restart,
        modify=modify,
        user=user,
        node=node,
        wait_healthy=wait_healthy,
        check_preprocessed=check_preprocessed,
    )


@TestStep(Given)
def create_transactions_configuration(
    self,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="transactions.xml",
    nodes=None,
    entries=transactions,
):
    """Create ClickHouse SSL servers configuration.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param nodes: nodes which will use remote config section
    :param entries: inside config information
    """

    nodes = self.context.cluster.nodes["clickhouse"][0:3] if nodes is None else nodes

    for name in nodes:
        node = self.context.cluster.node(name)
        _entries = entries
        with Then("I converting config file content to xml"):
            config = create_xml_config_content(
                _entries,
                config_file=config_file,
                config_d_dir=config_d_dir,
                root="clickhouse",
            )

        with And(f"I add config to {name}"):
            add_config_section(
                config=config, restart=True, modify=True, user=None, node=node
            )


@TestStep(Given)
def instrument_cluster_nodes(self, test, cluster_nodes, always_dump=True):
    """Instrument logs on cluster nodes."""
    for name in cluster_nodes:
        instrument_clickhouse_server_log(
            node=self.context.cluster.node(name), test=test, always_dump=always_dump
        )


@TestStep(Given)
def create_table(self, table_engine, node, database, core_table):
    """Step to create database and basic data table in it."""
    try:
        with Given("I create database"):
            node.query(f"CREATE DATABASE {database}")

        with And("I create data table"):
            node.query(
                f"CREATE TABLE {core_table}"
                "( timestamp DateTime,"
                "host      String,"
                "repsonse_time      Int32"
                f") ENGINE {table_engine}() ORDER BY (host, timestamp)"
            )
        yield
    finally:
        with Finally("I drop database"):
            node.query(f"DROP DATABASE {database}")


@TestStep(Given)
def materialized_view(
    self,
    table_engine,
    failure_mode,
    node,
    core_table,
    mv_1,
    mv_1_table,
    mv_2=None,
    mv_2_table=None,
    cascading=False,
):
    """Step to create mv and it`s dependent table section for mv tests
    :param cascading: add additional mv section
    :param failure_mode: failure mode type
    """
    data_type = "String"

    if failure_mode == "column type mismatch":
        data_type = "DateTime"
    elif failure_mode == "dummy":
        data_type = "String"

    with Given("I create mv dependent table"):
        node.query(
            f"CREATE table {mv_1_table}"
            "( timestamp           DateTime,"
            f"  host      {data_type},"
            " quantiles_tdigest  AggregateFunction(quantilesTDigest(0.75, 0.9, 0.95, 0.99), Int32))"
            f" ENGINE = {table_engine} ORDER BY (host, timestamp) ;"
        )

    with And("I create mv"):
        node.query(
            f"CREATE MATERIALIZED VIEW {mv_1}"
            f" TO {mv_1_table}"
            " AS SELECT toStartOfFiveMinute(timestamp) AS timestamp,   host,"
            "  quantilesTDigestState(0.75, 0.9, 0.95, 0.99)(repsonse_time) AS quantiles_tdigest "
            f"FROM {core_table} GROUP BY host,timestamp;"
        )

    if cascading:
        with And("I create second table"):
            node.query(
                f"CREATE table {mv_2_table} "
                "(   timestamp           DateTime  ,"
                "    host      String,"
                "    quantiles_tdigest   "
                "AggregateFunction(quantilesTDigest(0.75, 0.9, 0.95, 0.99), Int32) CODEC (ZSTD(2))) "
                f"ENGINE = {table_engine}() Order by (host, timestamp);"
            )

        with And("I create mv from first dependent table to second"):
            node.query(
                f"CREATE MATERIALIZED VIEW {mv_2}"
                f" to {mv_2_table} "
                "AS SELECT"
                "    toStartOfFiveMinute(timestamp) AS timestamp,"
                "     host      ,"
                "    quantilesTDigestMergeState(0.75, 0.9, 0.95, 0.99)(quantiles_tdigest) AS quantiles_tdigest "
                f"  FROM {mv_1_table} GROUP BY host, timestamp;"
            )


@TestStep(Given)
def materialized_view_circle(self, node, core_table, mv_1):
    """Step to create mv and circle it."""
    with Given("I create circled mv"):
        node.query(
            f"CREATE MATERIALIZED VIEW {mv_1}"
            f" TO {core_table}"
            " AS SELECT toStartOfFiveMinute(timestamp) AS timestamp,   host,"
            "  quantilesTDigestState(0.75, 0.9, 0.95, 0.99)(repsonse_time) AS quantiles_tdigest "
            f"FROM {core_table} GROUP BY host,timestamp;"
        )


@TestStep(Given)
def create_table_on_cluster(self, table_engine, node, database, core_table):
    """Step to create database and basic data table in it on cluster."""
    try:
        with Given("I create database"):
            node.query(f"CREATE DATABASE {database} ON CLUSTER 'ShardedAndReplicated';")

        with And("I create data table"):
            node.query(
                f"CREATE TABLE {core_table} ON CLUSTER 'ShardedAndReplicated'"
                "( timestamp DateTime,"
                "host      String,"
                "repsonse_time      Int32"
                f") ENGINE {table_engine}() ORDER BY (host, timestamp)"
            )

        yield
    finally:
        with Finally("I drop database"):
            node.query(f"DROP DATABASE {database} ON CLUSTER 'ShardedAndReplicated';")


@TestStep(Given)
def materialized_view_on_cluster(
    self,
    table_engine,
    failure_mode,
    node,
    core_table,
    mv_1,
    mv_1_table,
    mv_2=None,
    mv_2_table=None,
    cascading=False,
):
    """Step to create mv and it`s dependent table on cluster section for mv tests on cluster
    :param cascading: add additional mv section
    :param failure_mode: failure mode type
    """
    data_type = "String"

    if failure_mode == "column type mismatch":
        data_type = "DateTime"
    elif failure_mode == "dummy":
        data_type = "String"

    with Given("I create mv dependent table on cluster"):
        node.query(
            f"CREATE table {mv_1_table} ON CLUSTER 'ShardedAndReplicated'"
            "( timestamp           DateTime,"
            "  host      String,"
            " quantiles_tdigest  AggregateFunction(quantilesTDigest(0.75, 0.9, 0.95, 0.99), Int32))"
            f" ENGINE = {table_engine} ORDER BY (host, timestamp) ;"
        )

    with And("I create mv on cluster"):
        node.query(
            f"CREATE MATERIALIZED VIEW {mv_1} ON CLUSTER 'ShardedAndReplicated'"
            f" to {mv_1_table}"
            " AS SELECT toStartOfFiveMinute(timestamp) AS timestamp,   host,"
            "  quantilesTDigestState(0.75, 0.9, 0.95, 0.99)(repsonse_time) AS quantiles_tdigest "
            f"FROM {core_table} GROUP BY host,timestamp;"
        )

    if cascading:
        with And("I create another table with wrong data type"):
            node.query(
                f"CREATE table {mv_2_table}  ON CLUSTER 'ShardedAndReplicated' "
                "(   timestamp           DateTime  ,"
                f"    host      {data_type},"
                "    quantiles_tdigest   "
                "AggregateFunction(quantilesTDigest(0.75, 0.9, 0.95, 0.99), Int32) CODEC (ZSTD(2))) "
                f"ENGINE = {table_engine}() ORDER BY (host, timestamp);"
            )

        with And("I create mv to the second dependent table"):
            node.query(
                f"CREATE MATERIALIZED VIEW {mv_2} ON CLUSTER 'ShardedAndReplicated'"
                f" to {mv_2_table} "
                "AS SELECT"
                "    toStartOfFiveMinute(timestamp) AS timestamp,"
                "     host      ,"
                "    quantilesTDigestMergeState(0.75, 0.9, 0.95, 0.99)(quantiles_tdigest) AS quantiles_tdigest "
                f"  FROM {mv_1_table} GROUP BY host, timestamp;"
            )


@TestStep(Given)
def materialized_some_view(
    self,
    table_engine,
    failure_mode,
    node,
    core_table,
    mv_1,
    mv_1_table,
    view_1=None,
    view_type=None,
):
    """Step to create mv and it`s dependent table section for mv tests
    :param view_type: type of mv dependent table
    :param failure_mode: failure mode type
    """
    data_type = "String"

    if failure_mode == "column type mismatch":
        data_type = "DateTime"
    elif failure_mode == "dummy":
        data_type = "String"

    with Given("I create mv dependent table"):
        node.query(
            f"CREATE table {mv_1_table}"
            "( timestamp           DateTime,"
            f"  host      {data_type},"
            " quantiles_tdigest  AggregateFunction(quantilesTDigest(0.75, 0.9, 0.95, 0.99), Int32))"
            f" ENGINE = {table_engine} ORDER BY (host, timestamp) ;"
        )

    with And("I create mv"):
        node.query(
            f"CREATE MATERIALIZED VIEW {mv_1}"
            f" TO {mv_1_table}"
            " AS SELECT toStartOfFiveMinute(timestamp) AS timestamp,   host,"
            "  quantilesTDigestState(0.75, 0.9, 0.95, 0.99)(repsonse_time) AS quantiles_tdigest "
            f"FROM {core_table} GROUP BY host,timestamp;"
        )

    if view_type == "normal":
        with And("I create normal view to mv view"):
            node.query(
                f"CREATE VIEW {view_1}"
                " AS SELECT"
                "    toStartOfFiveMinute(timestamp) AS timestamp,"
                "     host      ,"
                "    quantilesTDigestMergeState(0.75, 0.9, 0.95, 0.99)(quantiles_tdigest) AS quantiles_tdigest "
                f"  FROM {mv_1_table} GROUP BY host, timestamp"
            )

    elif view_type == "live":
        with And("I create live view to mv view"):
            node.query(
                f"CREATE LIVE VIEW {view_1}"
                " AS SELECT"
                "    toStartOfFiveMinute(timestamp) AS timestamp,"
                "     host      ,"
                "    quantilesTDigestMergeState(0.75, 0.9, 0.95, 0.99)(quantiles_tdigest) AS quantiles_tdigest "
                f"  FROM {mv_1_table} GROUP BY host, timestamp SETTINGS allow_experimental_live_view = 1;"
            )

    elif view_type == "window":
        with And("I create window view to mv view"):
            node.query(
                f"CREATE WINDOW VIEW {view_1}"
                " AS SELECT"
                "    tumbleStart(w_id) AS w_start,"
                "     count(host) "
                f"  FROM {mv_1_table} GROUP BY tumble(now(), INTERVAL '5' SECOND) as w_id"
                f" SETTINGS allow_experimental_window_view = 1;"
            )


@TestStep
def simple_insert(
    self,
    failure_mode,
    core_table,
    number_of_blocks=10,
    fail_block_number=7,
    node_name="clickhouse1",
):
    """Second variation of simple insert for base table"""
    if failure_mode == "throwIf":
        self.context.cluster.node(node_name).query(
            (
                f"BEGIN TRANSACTION;"
                if self.context.use_transaction_for_atomic_insert
                else ""
            )
            + (
                f"INSERT INTO {core_table}"
                f" SELECT now() + number/10, toString(number), if({fail_block_number}, throwIf(number={fail_block_number},"
                "'block fail'), number)"
                f" FROM numbers({number_of_blocks})"
                " SETTINGS max_block_size=1,"
                " min_insert_block_size_bytes=1;"
            )
            + (f"COMMIT;" if self.context.use_transaction_for_atomic_insert else ""),
            exitcode=139,
            steps=False,
            timeout=3000,
        )

    elif failure_mode == "user_rights":
        with Given("I add readonly user"):
            self.context.cluster.node(node_name).query(
                "CREATE USER OR REPLACE ivan SETTINGS readonly = 1"
            )

        with And("I make insert from user with not enough permissions", flags=XFAIL):
            self.context.cluster.node(node_name).query(
                (
                    f"BEGIN TRANSACTION;"
                    if self.context.use_transaction_for_atomic_insert
                    else ""
                )
                + (
                    f"INSERT INTO {core_table} SELECT now() + number/10, toString(number%9999),"
                    " number % 999"
                    " FROM numbers(1000001)"
                )
                + (
                    f"COMMIT;" if self.context.use_transaction_for_atomic_insert else ""
                ),
                settings=[("user", "ivan")],
                timeout=3000,
                message="ivan: Not enough privileges.",
                exitcode=497,
            )

        with And("I drop created user"):
            self.context.cluster.node(node_name).query("DROP USER IF EXISTS ivan")

    else:
        self.context.cluster.node(node_name).query(
            f"INSERT INTO {core_table} SELECT now() + number/10, toString(number%9999),"
            " number % 999"
            " FROM numbers(1000000)",
            timeout=3000,
        )


@TestStep
def insert(self, failure_mode, number_of_blocks=10, fail_block_number=7, core_table=""):
    """Loop step to make complex insert for all shards"""
    with Given(f"LOOP STEP"):
        for name in self.context.cluster.nodes["clickhouse"][:3]:
            When("I make insert", test=simple_insert, parallel=True)(
                node_name=name,
                number_of_blocks=number_of_blocks,
                fail_block_number=fail_block_number,
                core_table=core_table,
                failure_mode=failure_mode,
            )


@TestStep
def simple_transaction_insert(
    self, core_table, node_name="clickhouse1", numbers="10", no_checks=False
):
    with Given(f"I make transaction insert"):
        self.context.cluster.node(node_name).query(
            f"BEGIN TRANSACTION;"
            f"INSERT INTO {core_table}"
            " SELECT now() + number/10, toString(number),"
            " number"
            f" FROM numbers({numbers});"
            " COMMIT;",
            exitcode=0,
            no_checks=no_checks,
        )


@TestStep
def simple_transaction_insert_throwif(self, core_table, node_name="clickhouse1"):
    with Given(
        f"I make fail block transaction insert",
        flags=XFAIL,
    ):
        self.context.cluster.node(node_name).query(
            f"BEGIN TRANSACTION;"
            f"INSERT INTO {core_table}"
            " SELECT now() + number/10, toString(number),"
            " if(5,"
            " throwIf(number=5,'block fail'), number)"
            f" FROM numbers(10)"
            " SETTINGS max_block_size=1,"
            f" min_insert_block_size_bytes=1;",
            exitcode=139,
        )

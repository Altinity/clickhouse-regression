from testflows.core import *
from helpers.common import create_xml_config_content, add_config, add_invalid_config
import time
from helpers.common import getuid, instrument_clickhouse_server_log
from testflows.asserts import error
from testflows.connect import Shell

remote_entries = {
    "server": {"shard": {"replica": {"host": "clickhouse1", "port": "9000"}}}
}


@TestStep(Given)
def instrument_cluster_nodes(self, test, cluster_nodes, always_dump=True):
    """Instrument logs on cluster nodes."""
    for name in cluster_nodes:
        instrument_clickhouse_server_log(
            node=self.context.cluster.node(name), test=test, always_dump=always_dump
        )


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
def create_remote_configuration(
    self,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="remote.xml",
    nodes=None,
    entries=remote_entries,
):
    """Create ClickHouse remote servers configuration.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param nodes: nodes which will use remote config section
    :param entries: inside config information
    """

    nodes = self.context.cluster.nodes["clickhouse"][0:13] if nodes is None else nodes

    for name in nodes:
        node = self.context.cluster.node(name)
        _entries = {"remote_servers": entries}
        with Then("I converting config file content to xml"):
            config = create_xml_config_content(
                _entries, config_file=config_file, config_d_dir=config_d_dir
            )

        with And(f"I add config to {name}"):
            add_config_section(
                config=config, restart=True, modify=False, user=None, node=node
            )


@TestStep(When)
def create_config_section(
    self,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="keeper.xml",
    control_nodes=None,
    cluster_nodes=None,
    check_preprocessed=True,
    secure=0,
):
    """Create section for ClickHouse servers config file.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param control_nodes: nodes which are using for Zookeeper or Keeper
    :param cluster_nodes: nodes which will be controlled by control_nodes cluster
    """
    for name in cluster_nodes:
        node = self.context.cluster.node(name)
        node_part = []
        for name1 in control_nodes:
            node_element = {
                "node": {"host": f"{name1}", "port": "2181", "secure": f"{secure}"}
            }
            node_part.append(node_element)
        _entries = {"zookeeper": node_part}
        with When(f"I add config to {name}"):
            config = create_xml_config_content(
                _entries, config_file=config_file, config_d_dir=config_d_dir
            )

        with And(f"I add config to {name}"):
            add_config_section(
                config=config,
                restart=True,
                modify=False,
                user=None,
                node=node,
                check_preprocessed=check_preprocessed,
            )


@TestStep
def create_test_table(
    self,
    table_name="test_table",
    cluster_name="'cluster_1replica_3shard'",
    table_engine="ReplicatedSummingMergeTree",
    graphite=False,
    collapsing=False,
    vcollapsing=False,
):
    """Table creation step."""
    cluster = self.context.cluster
    node = self.context.cluster.node("clickhouse1")

    with Given("I create table"):
        if graphite == True:
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (d Date, a String, b UInt8, x String, y Int8, Path String, "
                f"Time DateTime, Value Float64, col UInt64, Timestamp Int64) "
                f"ENGINE = {table_engine}('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}', 'graphite_rollup_example') "
                " PARTITION BY y ORDER BY (b, d) PRIMARY KEY b "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=0;",
                steps=False,
            )

        elif collapsing == True:
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (v UInt64, sign Int8 DEFAULT 1) "
                f"ENGINE = {table_engine}('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}', sign) "
                "ORDER BY tuple() "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=0;",
                steps=False,
            )

        elif vcollapsing == True:
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (v UInt64, sign Int8 DEFAULT 1, version UInt64) "
                f"ENGINE = {table_engine}('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}', sign, version) "
                "ORDER BY tuple() "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=0;",
                steps=False,
            )

        else:
            retry(node.query, timeout=100, delay=1)(
                f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
                f" (v UInt64) "
                f"ENGINE = {table_engine}('/clickhouse/tables"
                "/replicated/{shard}"
                f"/{table_name}'"
                ", '{replica}') "
                "ORDER BY tuple() "
                "SETTINGS assign_part_uuids=1,"
                " part_moves_between_shards_enable=1,"
                " part_moves_between_shards_delay_seconds=3;",
                steps=False,
            )


@TestStep
def create_test_table_with_insert(
    self,
    table_name="test_table",
    cluster_name="'cluster_1replica_3shard'",
    table_engine="ReplicatedSummingMergeTree",
    graphite=False,
    collapsing=False,
    vcollapsing=False,
):
    """Table creation step with simple data insert."""

    with Given("I create table"):
        create_test_table(
            table_name=table_name,
            cluster_name=cluster_name,
            table_engine=table_engine,
            graphite=graphite,
            collapsing=collapsing,
            vcollapsing=vcollapsing,
        )

    with And("I stop merges"):
        for node_name in ["clickhouse1", "clickhouse2", "clickhouse3", "clickhouse4"]:
            self.context.cluster.node(node_name).query(
                f"SYSTEM STOP MERGES {table_name}"
            )

    with And("I make simple insert"):
        i = 0
        for name in ["clickhouse1", "clickhouse3"]:
            i = i + 1
            simple_insert(table_name=table_name, node_name=name, value=i)


@TestStep
def move_part(
    self, table_name, shard, part, node_name="clickhouse1", message="", exitcode=0
):
    cluster = self.context.cluster
    retry(cluster.node(node_name).query, timeout=100, delay=1)(
        f"ALTER TABLE {table_name} MOVE PART '{part}' TO SHARD '/clickhouse/tables/"
        f"replicated/{shard}/{table_name}'",
        message=message,
        exitcode=exitcode,
    )


@TestStep
def move_part_and_return(
    self,
    table_name,
    shard1,
    shard2,
    part,
    part_uuid,
    node_name1="clickhouse1",
    node_name2="clickhouse2",
    message="",
    exitcode=0,
):
    """One part of data moves from one shard to another and returns."""

    cluster = self.context.cluster

    retry(cluster.node(node_name1).query, timeout=100, delay=1)(
        f"ALTER TABLE {table_name} MOVE PART '{part}' TO SHARD '/clickhouse/tables/"
        f"replicated/{shard2}/{table_name}'",
        message=message,
        exitcode=exitcode,
    )

    # with Step("Stop step 2"):
    #     time.sleep(45)

    part = ""
    while part == "":
        part = (
            cluster.node(node_name2)
            .query(f"SELECT name FROM system.parts where uuid = '{part_uuid}'")
            .output.strip()
        )

    # with Step("Stop step 3"):
    #     time.sleep(45)

    retry(cluster.node(node_name2).query, timeout=100, delay=1)(
        f"ALTER TABLE {table_name} MOVE PART '{part}' TO SHARD '/clickhouse/tables/"
        f"replicated/{shard1}/{table_name}'",
        message=message,
        exitcode=exitcode,
    )
    #
    # for node_name in ["clickhouse1", "clickhouse2", "clickhouse3", "clickhouse4"]:
    #     retry(cluster.node(node_name).query, timeout=100, delay=1)(
    #         f"SYSTEM STOP MERGES {table_name}"
    #     )


@TestStep
def move_part_and_return_stopped_replica(
    self,
    table_name,
    shard1,
    shard2,
    part,
    part_uuid,
    node_name1="clickhouse1",
    node_name2="clickhouse2",
    message="",
    exitcode=0,
):
    """One part of data moves from one shard to another and returns when some and some
    replica stops and start when some replica stopped when `MOVE PART TO SHARD` goes.
    """
    with Given("I stop shard 2 replica"):
        self.context.cluster.node("clickhouse4").stop_clickhouse()

    retry(self.context.cluster.node(node_name1).query, timeout=100, delay=1)(
        f"ALTER TABLE {table_name} MOVE PART '{part}' TO SHARD '/clickhouse/tables/"
        f"replicated/{shard2}/{table_name}'",
        message=message,
        exitcode=exitcode,
    )

    with Given("I stop shard 2 replica"):
        self.context.cluster.node("clickhouse4").start_clickhouse()

    part = ""
    while part == "":
        part = (
            self.context.cluster.node(node_name2)
            .query(f"SELECT name FROM system.parts where uuid = '{part_uuid}'")
            .output.strip()
        )

    retry(self.context.cluster.node(node_name2).query, timeout=100, delay=1)(
        f"ALTER TABLE {table_name} MOVE PART '{part}' TO SHARD '/clickhouse/tables/"
        f"replicated/{shard1}/{table_name}'",
        message=message,
        exitcode=exitcode,
    )


@TestStep
def select_count_from_table(
    self, table_name, node_name="clickhouse1", message="", exitcode=0
):
    # self.context.cluster.node(node_name).query(
    #     f"select count() from {table_name}",
    # f" SETTINGS allow_experimental_query_deduplication = 1",
    # f"select count() from {table_name} SETTINGS allow_experimental_query_deduplication = 1,"
    # f" optimize_trivial_count_query = false",
    # message=message, exitcode=exitcode)
    retry(self.context.cluster.node(node_name).query, timeout=100, delay=1)(
        f"select count() from {table_name} SETTINGS allow_experimental_query_deduplication = 1",
        message=message,
        exitcode=exitcode,
    )


@TestStep
def select_all_from_table(
    self, table_name, node_name="clickhouse1", message="1\n2\n3", exitcode=0
):
    self.context.cluster.node(node_name).query(
        # f"select * from {table_name} ORDER BY v ASC SETTINGS allow_experimental_query_deduplication = 1 FORMAT TSV",
        # message=message, exitcode=exitcode)
        f"select * from {table_name} ORDER BY v ASC FORMAT TSV",
        message=message,
        exitcode=exitcode,
    )


@TestStep
def simple_insert(self, table_name, value="777", node_name="clickhouse1"):
    retry(self.context.cluster.node(node_name).query, timeout=100, delay=1)(
        f"INSERT INTO {table_name}" f" VALUES ({value})"
    )


@TestStep
def move_part_with_check(self, table_name, shard_b_number, shard_a_name, part_name='\'all_0_0_0\''):
    with Given("I move part from shard a to shard b"):
        self.context.cluster.node(shard_a_name).query(
            f"ALTER TABLE {table_name} MOVE PART {part_name} TO SHARD '/clickhouse/tables/"
            f"replicated/0{shard_b_number}/{table_name}'"
        )
        retry(self.context.cluster.node(shard_a_name).query, timeout=100, delay=1)(
            f"select count() from system.parts where name == {part_name}",
            message="0",
        )

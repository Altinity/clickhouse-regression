from testflows.core import *
from helpers.common import create_xml_config_content, add_config, add_invalid_config
import time
from helpers.common import getuid, instrument_clickhouse_server_log
from testflows.asserts import error
from testflows.connect import Shell


@TestStep(Given)
def create_3_3_cluster_config(self):
    with Given("I create remote config"):
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


remote_entries = {
    "server": {"shard": {"replica": {"host": "clickhouse1", "port": "9000"}}}
}

ssl_entries = {
    "server": {
        "certificateFile": "/etc/clickhouse-server/config.d/server.crt",
        "privateKeyFile": "/etc/clickhouse-server/config.d/server.key",
        "dhParamsFile": "/etc/clickhouse-server/config.d/dhparam.pem",
        "verificationMode": "none",
        "loadDefaultCAFile": "true",
        "cacheSessions": "true",
        "disableProtocols": "sslv2,sslv3",
        "preferServerCiphers": "true",
    },
    "client": {
        "certificateFile": "/etc/clickhouse-server/config.d/server.crt",
        "privateKeyFile": "/etc/clickhouse-server/config.d/server.key",
        "loadDefaultCAFile": "true",
        "cacheSessions": "true",
        "disableProtocols": "sslv2,sslv3",
        "preferServerCiphers": "true",
        "verificationMode": "none",
        "invalidCertificateHandler": {"name": "RejectCertificateHandler"},
    },
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
def add_invalid_config_section(
    self,
    config,
    message,
    recover_config=None,
    tail=30,
    timeout=300,
    restart=True,
    user=None,
    node=None,
):
    """Add invalid config on cluster nodes."""
    # todo add node section as in add config, add yield in common.py
    return add_invalid_config(
        config=config,
        message=message,
        recover_config=recover_config,
        tail=tail,
        timeout=timeout,
        restart=restart,
        user=user,
    )


@TestStep(Given)
def create_ssl_configuration(
    self,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="ssl_conf.xml",
    nodes=None,
    entries=ssl_entries,
    restart=True,
    check_preprocessed=True,
):
    """Create ClickHouse SSL servers configuration.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param nodes: nodes which will use remote config section
    :param entries: inside config information
    """

    nodes = self.context.cluster.nodes["clickhouse"][0:13] if nodes is None else nodes

    for name in nodes:
        node = self.context.cluster.node(name)
        _entries = {"openSSL": entries}
        with Then("I converting config file content to xml"):
            config = create_xml_config_content(
                _entries, config_file=config_file, config_d_dir=config_d_dir
            )

        with And(f"I add config to {name}"):
            add_config_section(
                config=config,
                restart=restart,
                modify=False,
                user=None,
                node=node,
                check_preprocessed=check_preprocessed,
            )


@TestStep(Given)
def create_remote_configuration(
    self,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="remote.xml",
    nodes=None,
    entries=remote_entries,
    restart=True,
    modify=False,
    check_preprocessed=True,
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
                config=config,
                restart=restart,
                modify=modify,
                user=None,
                node=node,
                check_preprocessed=check_preprocessed,
            )


@TestStep(When)
def create_keeper_cluster_configuration(
    self,
    invalid_config=False,
    config_d_dir="/etc/clickhouse-server/config.d/",
    config_file="serverkeeper.xml",
    nodes=None,
    test_setting_name="startup_timeout",
    test_setting_value="30000",
    check_preprocessed=True,
    tcp_port=2181,
    tcp_port_secure=False,
    restart=True,
    modify=False,
):
    """Create ClickHouse Keeper raft configuration file.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param nodes: nodes which are used as Keeper nodes (standalone or mixed)
    """
    tcp_port_secure = self.context.tcp_port_secure

    nodes = self.context.cluster.nodes["clickhouse"][0:3] if nodes is None else nodes
    id2 = 0
    if tcp_port_secure:
        port = "tcp_port_secure"
    else:
        port = "tcp_port"

    for name in nodes:
        id2 = id2 + 1
        node = self.context.cluster.node(name)
        server_part = []
        id = 0
        for name1 in nodes:
            id = id + 1
            server_element = {
                "server": {"id": f"{id}", "hostname": f"{name1}", "port": "44444"}
            }
            server_part.append(server_element)

        _entries = {
            "keeper_server": {
                port: f"{tcp_port}",
                "server_id": f"{id2}",
                "log_storage_path": "/var/lib/clickhouse/coordination/log",
                "snapshot_storage_path": "/var/lib/clickhouse/coordination/snapshots",
                "coordination_settings": {
                    "operation_timeout_ms": "10000",
                    "session_timeout_ms": "30000",
                    "raft_logs_level": "information",
                    # "election_timeout_upper_bound_ms": "10000",
                    "rotate_log_storage_interval": "10000",
                    # "startup_timeout": "22000",
                    "heart_beat_interval_ms": "5000",
                    f"{test_setting_name}": f"{test_setting_value}",
                },
                "raft_configuration": server_part,
            }
        }
        with When(f"I create xml config content to {name}"):
            config = create_xml_config_content(
                _entries, config_file=config_file, config_d_dir=config_d_dir
            )

        if invalid_config:
            _entries = {
                "keeper_server": {
                    port: "2181",
                    "server_id": f"{id2}",
                    "log_storage_path": "/var/lib/clickhouse/coordination/log",
                    "snapshot_storage_path": "/var/lib/clickhouse/coordination/snapshots",
                    "coordination_settings": {
                        "operation_timeout_ms": "10000",
                        "session_timeout_ms": "30000",
                        "raft_logs_level": "information",
                        # "election_timeout_upper_bound_ms": "10000",
                        "rotate_log_storage_interval": "10000",
                        # "startup_timeout": "22000",
                        "heart_beat_interval_ms": "5000",
                        f"{test_setting_name}": f"{test_setting_value}",
                    },
                    "raft_configuration": server_part,
                }
            }
            with When(f"I create xml config content to {name}"):
                recover_config = create_xml_config_content(
                    _entries, config_file=config_file, config_d_dir=config_d_dir
                )

            with And("adding invalid config file to the server"):
                add_invalid_config_section(
                    config=config,
                    recover_config=recover_config,
                    message="Exception",
                    tail=30,
                    timeout=300,
                    restart=False,
                )

        else:
            with And(f"I add config to {name}"):
                add_config_section(
                    config=config,
                    restart=restart,
                    modify=modify,
                    user=None,
                    node=node,
                    wait_healthy=False,
                    check_preprocessed=check_preprocessed,
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
    restart=True,
    modify=False,
):
    """Create section for ClickHouse servers config file.

    :param config_d_dir: path to CLickHouse config.d folder
    :param config_file: name of config file
    :param control_nodes: nodes which are using for Zookeeper or Keeper
    :param cluster_nodes: nodes which will be controlled by control_nodes cluster
    """
    secure = self.context.secure

    control_nodes = (
        self.context.cluster.nodes["clickhouse"][0:3]
        if control_nodes is None
        else control_nodes
    )
    cluster_nodes = (
        self.context.cluster.nodes["clickhouse"][0:12]
        if cluster_nodes is None
        else cluster_nodes
    )
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
                restart=restart,
                modify=modify,
                user=None,
                node=node,
                check_preprocessed=check_preprocessed,
            )


@TestStep(When)
def stop_all_zookeepers(self):
    """Stop all ZooKeeper services."""
    for name in self.context.cluster.nodes["zookeeper"]:
        node = self.context.cluster.node(name)
        with When(f"I stop {name}"):
            node.stop()

    # if simple:
    #     for name in self.context.cluster.nodes["zookeeper"]:
    #         node = self.context.cluster.node(name)
    #         with When(f"I stop {name}"):
    #             node.stop()
    # else:
    #     try:
    #         for name in self.context.cluster.nodes["zookeeper"]:
    #             node = self.context.cluster.node(name)
    #             with When(f"I stop {name}"):
    #                 node.stop()
    #         yield
    #     finally:
    #         with Finally("I restart ZooKeepers back up"):
    #             for name in self.context.cluster.nodes["zookeeper"]:
    #                 node = self.context.cluster.node(name)
    #                 with When(f"I restart {name}"):
    #                     node.restart()


@TestStep(Given)
def start_keepers(self, standalone_keeper_nodes=None, manual_cleanup=False):
    """Start Keeper services.

    :param standalone_keeper_nodes: nodes which will be used for standalone Keeper cluster
    """
    standalone_keeper_nodes = (
        self.context.cluster.nodes["clickhouse"][9:12]
        if standalone_keeper_nodes is None
        else standalone_keeper_nodes
    )
    try:
        for name in standalone_keeper_nodes:
            node = self.context.cluster.node(name)
            with When(f"I start {name}"):
                with By("starting keeper process"):
                    node.cmd("rm -rf /tmp/clickhouse-keeper.pid")
                    node.cmd(
                        "clickhouse keeper --config /etc/clickhouse-server/config.xml"
                        " --pidfile=/tmp/clickhouse-keeper.pid --daemon",
                        exitcode=0,
                    )

                with And("checking that keeper pid file was created"):
                    node.cmd(
                        "ls /tmp/clickhouse-keeper.pid",
                        exitcode=0,
                        message="/tmp/clickhouse-keeper.pid",
                    )
        yield
    finally:
        with Given("I stop all keepers"):
            if manual_cleanup is False:
                for name in standalone_keeper_nodes:
                    node = self.context.cluster.node(name)
                    with When(f"I stop {name}"):
                        with By("sending kill -TERM to keeper process"):
                            if node.cmd("ls /tmp/clickhouse-keeper.pid", exitcode=0):
                                pid = node.cmd(
                                    "cat /tmp/clickhouse-keeper.pid"
                                ).output.strip()
                                node.cmd(f"kill -TERM {pid}", exitcode=0)
                        with And("checking pid does not exist"):
                            retry(node.cmd, timeout=100, delay=1)(
                                f"ps {pid}", exitcode=1, steps=False
                            )


@TestStep(Given)
def stop_keepers(self, cluster_nodes=None):
    """Stop ClickHouses group.

    :param cluster_nodes: Clickhouse server nodes
    """
    cluster_nodes = (
        self.context.cluster.nodes["clickhouse"][:9]
        if cluster_nodes is None
        else cluster_nodes
    )
    for name in cluster_nodes:
        node = self.context.cluster.node(name)
        with When(f"I stop {name}"):
            with By("sending kill -TERM to keeper process"):
                if node.cmd("ls /tmp/clickhouse-keeper.pid", exitcode=0):
                    pid = node.cmd("cat /tmp/clickhouse-keeper.pid").output.strip()
                    node.cmd(f"kill -TERM {pid}", exitcode=0)
            with And("checking pid does not exist"):
                retry(node.cmd, timeout=100, delay=1)(
                    f"ps {pid}", exitcode=1, steps=False
                )


@TestStep(Given)
def stop_clickhouses(self, cluster_nodes=None, manual_cleanup=False):
    """ClickHouse cluster stop with restart option"""
    cluster_nodes = (
        self.context.cluster.nodes["clickhouse"][:3]
        if cluster_nodes is None
        else cluster_nodes
    )
    try:
        with Given("I stop ClickHouses"):
            for name in cluster_nodes:
                self.context.cluster.node(name).stop_clickhouse()

        yield
    finally:
        with Given("I restart ClickHouses"):
            if manual_cleanup is False:
                for name in cluster_nodes:
                    self.context.cluster.node(name).start_clickhouse()


@TestStep(Given)
def clean_coordination_on_all_nodes(self, cluster_nodes=None):
    """Clean coordination on ClickHouse server nodes.

    :param cluster_nodes: Clickhouse server nodes
    """
    cluster_nodes = (
        self.context.cluster.nodes["clickhouse"][:12]
        if cluster_nodes is None
        else cluster_nodes
    )
    for name in cluster_nodes:
        node = self.context.cluster.node(name)
        node.cmd(
            f"rm -rf /var/lib/clickhouse/coordination/snapshots "
            f"&& rm -rf /var/lib/clickhouse/coordination/log "
        )


@TestStep(When)
def create_simple_table(
    self,
    node=None,
    table_name="test",
    cluster_name="'simple_replication_cluster'",
    values="Id Int32, partition Int32",
    manual_cleanup=False,
):
    """Create simple table with timeout option.

    :param node: node for table
    :param table_name: table name
    :param cluster_name: name of cluster for replicated table
    :param manual_cleanup: manual cleanup
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")
    try:
        retry(node.query, timeout=100, delay=1)(
            f"CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name}"
            f" ({values}) "
            "ENGINE = ReplicatedMergeTree('/clickhouse/tables/replicated/{shard}"
            f"/{table_name}'"
            ", '{replica}') "
            "ORDER BY Id PARTITION BY Id",
            steps=False,
        )
        yield table_name
    finally:
        with Finally("I clean up"):
            if manual_cleanup is False:
                with By("dropping table if exists"):
                    node.query(
                        f"DROP TABLE IF EXISTS {table_name} ON CLUSTER {cluster_name} SYNC"
                    )


@TestStep(When)
def table_insert(
    self,
    node=None,
    exitcode=0,
    node_name="clickhouse1",
    table_name="test",
    values="1,111",
):
    """Table insert with timeout option.

    :param node_name: insert node name
    :param table_name: table name
    :param values: insert data
    """
    if node is None:
        node = self.context.cluster.node(node_name)
    retry(node.query, timeout=100, delay=1)(
        f"INSERT INTO {table_name}(Id, partition) values ({values})",
        exitcode=exitcode,
        steps=False,
    )


@TestStep(Given)
def table_select(
    self, node=None, node_name="clickhouse1", table_name="test", message="1,111"
):
    """Select from table with timeout option.

    :param node_name: insert node name
    :param table_name: table name
    :param message: data check message
    """
    if node is None:
        node = self.context.cluster.node(node_name)
    retry(node.query, timeout=100, delay=1)(
        f"SELECT * FROM {table_name} FORMAT CSV", message=message, steps=False
    )


@TestStep(Given)
def start_stand_alone_keeper(self):
    """Start 9 nodes ClickHouse server and standalone 3 nodes Keeper."""
    cluster = self.context.cluster
    try:
        with Given("I start standalone 3 nodes Keeper server"):
            time.sleep(10)
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][9:12])

        with Given("I start all standalone Keepers nodes"):
            time.sleep(10)
            for name in cluster.nodes["clickhouse"][9:12]:
                cluster.node(name).stop_clickhouse()
            start_keepers(standalone_keeper_nodes=cluster.nodes["clickhouse"][9:12])

        with And("I add Keeper server configuration file"):
            time.sleep(3)
            create_config_section(
                control_nodes=cluster.nodes["clickhouse"][9:12],
                cluster_nodes=cluster.nodes["clickhouse"][:12],
            )

        with And("I start ClickHouse server"):
            time.sleep(3)
            for name in cluster.nodes["clickhouse"][:9]:
                cluster.node(name).restart_clickhouse()
        yield
    finally:
        with Finally("I clean up"):
            with By("I start clickhouse servers", flags=TE):
                stop_keepers(cluster_nodes=cluster.nodes["clickhouse"][9:12])
                for name in cluster.nodes["clickhouse"][9:12]:
                    self.context.cluster.node(name).start_clickhouse(wait_healthy=False)
                    time.sleep(5)

            clean_coordination_on_all_nodes()


@TestStep(Given)
def start_mixed_keeper(
    self,
    control_nodes=None,
    cluster_nodes=None,
    rest_cluster_nodes=None,
    test_setting_name="startup_timeout",
    test_setting_value="30000",
):
    """Start 9 nodes ClickHouse server with one shared 3 nodes shard Keeper."""
    cluster = self.context.cluster
    control_nodes = (
        cluster.nodes["clickhouse"][6:9] if control_nodes is None else control_nodes
    )
    cluster_nodes = (
        cluster.nodes["clickhouse"][0:9] if cluster_nodes is None else cluster_nodes
    )
    rest_cluster_nodes = (
        cluster.nodes["clickhouse"][0:6]
        if rest_cluster_nodes is None
        else rest_cluster_nodes
    )
    try:
        with Given("I stop all ClickHouse server nodes"):
            for name in cluster_nodes:
                retry(cluster.node(name).stop_clickhouse, timeout=100, delay=1)(
                    safe=False
                )

        with And("I clean ClickHouse Keeper server nodes"):
            clean_coordination_on_all_nodes()

        with And("I create server Keeper config"):
            create_config_section(
                control_nodes=control_nodes,
                cluster_nodes=cluster_nodes,
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I create mixed 3 nodes Keeper server config file"):
            create_keeper_cluster_configuration(
                nodes=control_nodes,
                test_setting_name=test_setting_name,
                test_setting_value=test_setting_value,
                check_preprocessed=False,
                restart=False,
                modify=False,
            )

        with And("I start mixed ClickHouse server nodes"):
            for name in control_nodes:
                retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)(
                    wait_healthy=False
                )

        with And(f"I check that ruok returns imok"):
            for name in control_nodes:
                retry(cluster.node("bash-tools").cmd, timeout=100, delay=1)(
                    f"echo ruok | nc {name} 2181",
                    exitcode=0,
                    message="imok",
                )

        if rest_cluster_nodes != "no_rest_nodes":
            with And("I start rest ClickHouse server nodes"):
                for name in rest_cluster_nodes:
                    retry(cluster.node(name).start_clickhouse, timeout=100, delay=1)()

        yield
    finally:
        with Finally("I clean up"):
            with By("I clean ClickHouse Keeper server nodes"):
                clean_coordination_on_all_nodes()


@TestStep(Given)
def start_different_shared_keeper(self):
    """Check 9 ClickHouse server with different Keeper for each shard with one shared start up."""
    cluster = self.context.cluster
    try:
        with Given("I create 3 by 3 nodes Keeper server config section"):
            time.sleep(10)
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][:3])
            time.sleep(10)
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][3:6])
            time.sleep(10)
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][6:9])

        with And("I create 9 nodes ClickHouse Keeper server config section"):
            create_config_section(
                control_nodes=cluster.nodes["clickhouse"][6:9],
                cluster_nodes=cluster.nodes["clickhouse"][:9],
            )

        with And(
            "I start 9 nodes ClickHouse Keeper server with 3 different ClickHouse Keeper servers and 1 shared"
        ):
            for name in cluster.nodes["clickhouse"][:9]:
                cluster.node(name).restart_clickhouse(wait_healthy=False)

        yield
    finally:
        with Finally("I clean up"):
            with Given("I clean ClickHouse Keeper server and ClickHouse server nodes"):
                clean_coordination_on_all_nodes()


@TestStep(Given)
def start_different_keeper(self):
    """Start 9 nodes ClickHouse server with different 3 nodes Keeper for each shard."""
    cluster = self.context.cluster
    try:
        with Given("I create 3 nodes Keeper server config section"):
            time.sleep(10)
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][:3])

        with And("I create server Keeper config"):
            time.sleep(10)
            create_config_section(
                control_nodes=cluster.nodes["clickhouse"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:3],
            )

        with And("I restart all ClickHouse Keeper server nodes"):
            for name in cluster.nodes["clickhouse"][:3]:
                cluster.node(name).restart_clickhouse(wait_healthy=False)

        with Given("I create another 3 nodes Keeper server config section"):
            time.sleep(10)
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][3:6])

        with And("I create server Keeper config"):
            time.sleep(10)
            create_config_section(
                control_nodes=cluster.nodes["clickhouse"][3:6],
                cluster_nodes=cluster.nodes["clickhouse"][3:6],
            )

        with And("I restart all ClickHouse Keeper server nodes"):
            for name in cluster.nodes["clickhouse"][3:6]:
                cluster.node(name).restart_clickhouse(wait_healthy=False)

        with Given("I create 3 nodes Keeper server config section"):
            create_keeper_cluster_configuration(nodes=cluster.nodes["clickhouse"][6:9])

        with And("I create server Keeper config"):
            create_config_section(
                control_nodes=cluster.nodes["clickhouse"][6:9],
                cluster_nodes=cluster.nodes["clickhouse"][6:9],
            )

        with And("I restart all ClickHouse Keeper server nodes"):
            for name in cluster.nodes["clickhouse"][6:9]:
                cluster.node(name).restart_clickhouse(wait_healthy=False)

        yield
    finally:
        with Finally("I clean up"):
            with Given("I clean ClickHouse Keeper server and ClickHouse server nodes"):
                clean_coordination_on_all_nodes()


@TestStep(Given)
def connect_zookeeper(self):
    """Connect Zookeeper 3 nodes control cluster to ClickHouse server."""
    cluster = self.context.cluster
    try:
        with Given("I add ZooKeeper server configuration file to ClickHouse servers"):
            create_config_section(
                control_nodes=cluster.nodes["zookeeper"][:3],
                cluster_nodes=cluster.nodes["clickhouse"][:9],
            )

        with And("I start ClickHouse Server"):
            for name in cluster.nodes["clickhouse"][:9]:
                cluster.node(name).restart_clickhouse()
        yield
    finally:
        with Finally("I clean up"):
            with By("Clear Zookeeper meta information and keeper configs"):
                self.context.cluster.node("zookeeper1").cmd("rm -rf ../share/")


@TestStep(Given)
def simple_synchronization_check(self):
    """Simple synchronization check: stop 1 node,insert,restart and check synchronization."""
    cluster = self.context.cluster
    with Given("I stop ClickHouse server 1 node"):
        cluster.node("clickhouse1").stop_clickhouse()

    with And("I make simple insert clickhouse server 2 node"):
        table_insert(node_name="clickhouse2")

    with And("I start ClickHouse server 1 node"):
        cluster.node("clickhouse1").start_clickhouse()

    with And("I check correctness of data on ClickHouse server 1 node"):
        table_select(node_name="clickhouse1")


@TestStep(Given)
def insert_in_table_check(self):
    """Check that INSERT command is synchronized via keeper servers
    when one of the ClickHouse server nodes is temporary unavailable.
    """
    cluster = self.context.cluster
    try:
        with When("Receive UID"):
            uid = getuid()

        with And("I create simple table"):
            table_name = f"test{uid}"
            create_simple_table(table_name=table_name)

        with And("I stop clickhouse server 1 node"):
            cluster.node("clickhouse1").stop_clickhouse()
    finally:
        with And("I make simple insert ClickHouse server 2 node"):
            table_insert(node_name="clickhouse2", table_name=table_name)

        with And("I start clickhouse server 1 node"):
            cluster.node("clickhouse1").start_clickhouse()

        with And("I check correctness of data on ClickHouse server 1 node"):
            table_select(node_name="clickhouse1", table_name=table_name)


@TestStep(Given)
def create_table_check(self):
    """Check that CREATE command is synchronized via keeper servers
    when one of the ClickHouse server nodes is temporary unavailable.
    """
    cluster = self.context.cluster
    try:
        with When("Receive UID"):
            uid = getuid()

        with And("I stop clickhouse1 node"):
            cluster.node("clickhouse1").stop_clickhouse()
    finally:
        Step("I create simple table", test=create_simple_table, parallel=True)(
            node_name="clickhouse2", table_name=f"test{uid}"
        )

        with And("I start clickhouse1 node"):
            cluster.node("clickhouse1").start_clickhouse()

        with And("I check the table is created"):
            retry(self.context.cluster.node("clickhouse1").query, timeout=100, delay=1)(
                "SHOW TABLES", message=f"test{uid}", exitcode=0, steps=False
            )


@TestStep(Given)
def drop_table_check(self):
    """Check that DROP command is synchronized via keeper servers
    when one of the ClickHouse server nodes is temporary unavailable.
    """
    cluster = self.context.cluster
    with When("Receive UID"):
        uid = getuid()

    with And("I create simple table"):
        table_name = f"test{uid}"
        create_simple_table(table_name=table_name, manual_cleanup=True)

    try:
        with When("I stop clickhouse1 node"):
            cluster.node("clickhouse1").stop_clickhouse()

    finally:
        And(
            "I re-start clickhouse1 node while DROP command is executing",
            test=cluster.node("clickhouse1").start_clickhouse(),
            parallel=True,
        )(name="clickhouse1", sleep=10)

        with Then(
            "I try dropping table when clickhouse1 node is stopped", flags=MANDATORY
        ):
            self.context.cluster.node("clickhouse2").query(
                f"DROP TABLE IF EXISTS {table_name} ON CLUSTER "
                "'Cluster_3shards_with_3replicas' SYNC"
            )


@TestStep(Given)
def iops_check(self, sleep=0.5, check_points=20):
    """Simple iops check with iostat."""
    with When("I check IOPS"):
        for i in range(1, check_points):
            time.sleep(sleep)
            with Shell() as bash:
                metric(
                    name="iops",
                    value=bash(
                        "iostat -d nvme0n1 | grep nvme0n1 | awk '{ print $2 }'"
                    ).output.strip(),
                    units="tps",
                )

                metric(name="map insert time", value=current_time(), units="sec")


@TestStep(Given)
def rows_number(self, sleep=0.5, check_points=20, table_name="zookeeper_bench"):
    """Simple check rows number in table."""
    with When("I check rows number"):
        for i in range(1, check_points):
            time.sleep(sleep)
            metric(
                name="number_of_rows",
                value=self.context.cluster.node("clickhouse1")
                .query(f"select count() from {table_name}")
                .output.strip(),
                units="rows",
            )


@TestStep(Given)
def drop_table(self, table_name="test"):
    """Drop table step."""
    self.context.cluster.node("clickhouse2").query(
        f"DROP TABLE IF EXISTS {table_name} ON CLUSTER "
        "'Cluster_3shards_with_3replicas' SYNC"
    )


@TestStep(Given)
def system_zoo_check(
    self,
    sleep=0,
    check_points=2,
):
    """ZooKeeper rows check from system table."""
    with When("I check rows number"):
        for i in range(1, check_points):
            time.sleep(sleep)
            metric(
                name="",
                value=self.context.cluster.node("clickhouse1")
                .query("select * from system.events where event ilike '%ZooKeeper%';")
                .output.strip(),
                units="",
            )


@TestStep
def openssl_check_step(self, node=None, port="9440"):
    """Check ClickHouse connection to Clickhouse Keeper is ssl."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.cmd(
        f"openssl s_client -connect clickhouse1:{port}",
        no_checks=True,
    )


@TestStep(Then)
def openssl_client_connection(
    self,
    options="",
    port=None,
    node=None,
    hostname=None,
    success=True,
    message=None,
    messages=None,
    exitcode=None,
):
    """Check SSL connection using openssl s_client utility."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    if port is None:
        port = self.context.connection_port

    if hostname is None:
        hostname = node.name

    if exitcode is None:
        if success:
            exitcode = 0
        else:
            exitcode = "!= 0"

    node.command(
        f'openssl s_client -brief {options} -connect {hostname}:{port} <<< "Q"',
        message=message,
        messages=messages,
        exitcode=exitcode,
    )


@TestStep(Given)
def add_ssl_clickhouse_client_configuration_file(
    self,
    entries,
    config=None,
    config_d_dir="/etc/clickhouse-client/config.d/",
    config_file="fips.xml",
    timeout=300,
    restart=False,
    node=None,
):
    """Add clickhouse-client SSL configuration file.

    <config>
        <openSSL>
            <client> <!-- Used for connection to server's secure tcp port -->
                <loadDefaultCAFile>true</loadDefaultCAFile>
                <cacheSessions>true</cacheSessions>
                <disableProtocols>sslv2,sslv3</disableProtocols>
                <preferServerCiphers>true</preferServerCiphers>
                <!-- Use for self-signed: <verificationMode>none</verificationMode> -->
                <invalidCertificateHandler>
                    <!-- Use for self-signed: <name>AcceptCertificateHandler</name> -->
                    <name>RejectCertificateHandler</name>
                </invalidCertificateHandler>
            </client>
        </openSSL>
    </config>
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    entries = {"secure": "true", "openSSL": {"client": entries}}
    if config is None:
        config = create_xml_config_content(
            entries, config_file=config_file, config_d_dir=config_d_dir, root="config"
        )

    with When("I add the config", description=config.path):
        node.command(f"mkdir -p {config_d_dir}", exitcode=0)
        command = f"cat <<HEREDOC > {config.path}\n{config.content}\nHEREDOC"
        node.command(command, steps=False, exitcode=0)

    # try:
    #     with When("I add the config", description=config.path):
    #         node.command(f"mkdir -p {config_d_dir}", exitcode=0)
    #         command = f"cat <<HEREDOC > {config.path}\n{config.content}\nHEREDOC"
    #         node.command(command, steps=False, exitcode=0)
    #
    #     yield
    # finally:
    #     with Finally(f"I remove {config.name} on {node.name}"):
    #         with By("deleting the config file", description=config.path):
    #             node.command(f"rm -rf {config.path}", exitcode=0)


@TestStep(Then)
def clickhouse_client_connection(
    self,
    options=None,
    port=None,
    node=None,
    hostname=None,
    success=True,
    message=None,
    messages=None,
    exitcode=None,
    insecure=True,
    prefer_server_ciphers=False,
):
    """Check SSL TCP connection using clickhouse-client utility.

    supported configuration options:
        <verificationMode>none|relaxed|strict|once</verificationMode>
        <cipherList>ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH</cipherList>
        <preferServerCiphers>true|false</preferServerCiphers>
        <requireTLSv1>true|false</requireTLSv1>
        <requireTLSv1_1>true|false</requireTLSv1_1>
        <requireTLSv1_2>true|false</requireTLSv1_2>
        <requireTLSv1_3>true|false</requireTLSv1_3>
        <disableProtocols>sslv2,sslv3,tlsv1,tlsv1_1,tlsv1_2,tlsv1_3</disableProtocols>
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    if port is None:
        port = self.context.connection_port

    if hostname is None:
        hostname = node.name

    if options is None:
        options = {"loadDefaultCAFile": "false", "caConfig": "/etc/clickhouse-server/config.d/altinity_blog_ca.crt"}
    else:
        options["loadDefaultCAFile"] = "false"
        options["caConfig"] = "/etc/clickhouse-server/config.d/altinity_blog_ca.crt"

    if exitcode is None:
        if success:
            exitcode = 0
        else:
            exitcode = "!= 0"

    if insecure:
        options["verificationMode"] = "none"

    options["preferServerCiphers"] = "true" if prefer_server_ciphers else "false"

    with Given("custom clickhouse-client SSL configuration"):
        add_ssl_clickhouse_client_configuration_file(entries=options)

    output = node.command(
        f'clickhouse client -s --verbose --host {hostname} --port {port} -q "SELECT 1"',
        message=message,
        messages=messages,
        exitcode=exitcode,
    ).output

    return output
